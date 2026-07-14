#!/usr/bin/env python3
"""
Critic 진단 프로브 — 5-seed shuffle-null + bag-size 교란 + 필수 baseline (7-point #2).

  작성: braveji (Critic) · BIOP02-96 G2 · critic_status=reject 해소용
  대상: LUNG_NSCLC / GASTRIC_STAD / HEADNECK_HNSC / COLORECTAL

배경 (CRITIC_REVIEW_G2_ADDENDUM.md 참조)
--------------------------------------
kkkim이 COLORECTAL에 적용한 `full/run_openitems_robustness.py`가 5-seed shuffle-null에서
null SD 0.046~0.167을 보였다(cms1: 0.387~0.794). 즉 **단일시드 shuffle-null은 우연배제
근거로 쓸 수 없다.** 그런데 sealed-forward 3암종(폐/위/두경부)은 전부 단일시드(seed=42)
null만 갖고 있고, 그 위에서 법칙 판정이 내려졌다. 이 스크립트는 그 공백을 메운다.

또한 7-point #2가 요구하는 baseline 3종 중 pixel-mean/subtype-only가 전 암종에 없다.
`prevalence_baseline`은 `{"auc": 0.5}` 상수라 경험적 baseline이 아니다.

무엇을 산출하는가
-----------------
endpoint마다:

  [A] real (seed=42)                    — 저장본 재현 확인용
  [B] 5-seed shuffle-null               — null_mean / null_sd / 판정
        판정 기준 = kkkim 자체 기준 유지: real > null_mean + 2*null_sd
        (shuffle_null_robustness.json §criterion: "미달=우연배제 강건성 미확보로 '실패'")
  [C] n_tiles-only baseline  ★핵심★    — 슬라이드당 타일 수 **단 하나의 피처**로 LR.
        이게 높으면(예: 위암 lauren 0.8) AUROC가 형태가 아니라 **bag-size에서 나온다**는
        직접 증거다. shuffle-null이 >0.5로 뜨는 현상의 유력 용의자.
  [D] mean-embed baseline               — 슬라이드 임베딩 평균 → LR. MIL(attention)이
        단순 평균 대비 실제로 무엇을 더하는지. (#2의 pixel-mean 대응물)
  [E] bag-size 교란 진단
        - spearman(patient_proba, n_tiles) : 예측이 타일 수를 따라가는가
        - spearman(label,        n_tiles) : 라벨 자체가 타일 수와 엮여 있는가(원천 교란)
          → [E2]가 유의하면 [C]가 높은 건 당연하고, 그 endpoint의 AUROC는 전부 의심.

주의
----
- **학습 경로는 run_mil_cost.train_eval을 그대로 import**한다(재구현 금지 — RNG 소비까지
  동일해야 seed=42 real이 저장본을 재현). 이 프로브의 유일한 차이는 n_tiles 부수 산출.
- GPU 필요. 실행 전 #biop02-alerts에 GPU 인덱스 예약 (CLAUDE.md).
- 임베딩이 `/workspace/data/cache/biop02/`에 있어야 owner 아닌 사람도 돌릴 수 있다.
  현재 manifest는 `/home/kkkim/project/...`(개인 컨테이너 홈)를 가리켜 **owner 외에는
  재현 불가** → BLOCKER-5. 이 스크립트를 실행하려면 그 선행조건부터 풀어야 한다.

사용
----
  # 단일 암종 전 endpoint
  python critic_robustness_probe.py --cancer GASTRIC_STAD --device cuda:0

  # endpoint 지정 (긴 작업 분할)
  python critic_robustness_probe.py --cancer LUNG_NSCLC --device cuda:1 \
      --endpoints histology_lusc,egfr_activating

  # 산출: <cancer>/full/critic_robustness.json
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

# 학습 경로는 원본 그대로 재사용 (재구현 금지)
from run_mil_cost import bootstrap_auc, load_meta, patient_agg, train_eval  # noqa: E402

SHUFFLE_SEEDS = [42, 1, 2, 3, 4]


# ─────────────────────────────────────────────────────────────
# 슬라이드 메타 (타일 수 / 평균 임베딩) — mmap으로 싸게 읽는다
# ─────────────────────────────────────────────────────────────
def slide_stats(slides):
    """slide_id -> {n_tiles, mean_vec}. npy는 (n_tiles, 1024) 가정."""
    stats = {}
    for s in slides:
        arr = np.load(s["path"], mmap_mode="r")
        stats[s["slide_id"]] = {
            "n_tiles": int(arr.shape[0]),
            "mean_vec": np.asarray(arr).mean(axis=0).astype("float32"),
        }
    return stats


def labeled_rows(slides, labels, endpoint, split_name):
    out = []
    for s in slides:
        lv = labels.get(s["case_id"], {}).get(endpoint, "")
        if s["split"] == split_name and lv != "":
            out.append((s, int(lv)))
    return out


def patient_level(rows, stats, feat):
    """환자단위 집계. feat(slide_id)->vector(1-D). 반환 (X, y, case_ids)."""
    by = defaultdict(list)
    ylab = {}
    for s, y in rows:
        by[s["case_id"]].append(feat(s["slide_id"]))
        ylab[s["case_id"]] = y
    cids = sorted(by)
    X = np.stack([np.mean(np.stack(by[c]), axis=0) for c in cids])
    y = np.array([ylab[c] for c in cids])
    return X, y, cids


def fit_lr_auc(Xtr, ytr, Xho, yho, seed=42):
    """표준화 + 로지스틱회귀 → holdout AUROC + bootstrap CI. 학습 불가 시 None."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if len(set(ytr)) < 2 or len(set(yho)) < 2:
        return None
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed),
    )
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xho)[:, 1]
    auc, lo, hi = bootstrap_auc(list(yho), list(p), seed=seed)
    return {"auc": auc, "ci95": [lo, hi], "n_holdout": int(len(yho)), "n_pos": int(sum(yho))}


def spearman(a, b):
    from scipy.stats import spearmanr

    if len(a) < 3 or len(set(a)) < 2 or len(set(b)) < 2:
        return None, None
    r, p = spearmanr(a, b)
    return round(float(r), 4), round(float(p), 5)


# ─────────────────────────────────────────────────────────────
def probe_endpoint(cancer, slides, labels, stats, endpoint, device):
    res = {"endpoint": endpoint}
    tr_rows = labeled_rows(slides, labels, endpoint, "train")
    ho_rows = labeled_rows(slides, labels, endpoint, "val") + labeled_rows(
        slides, labels, endpoint, "test"
    )
    if not tr_rows or not ho_rows or len({y for _, y in tr_rows}) < 2:
        return {"endpoint": endpoint, "status": "skip(insufficient labels)"}

    # ── [A] real (seed=42) ────────────────────────────────────
    t = time.time()
    recs, dev_auc = train_eval(slides, labels, endpoint, device, shuffle=False, seed=42)
    if recs is None:
        return {"endpoint": endpoint, "status": "skip(train_eval returned None)"}
    pa = patient_agg(recs)
    y_real = [v[1] for v in pa.values()]
    p_real = [v[0] for v in pa.values()]
    auc, lo, hi = bootstrap_auc(y_real, p_real)
    res["real"] = {
        "auc": auc,
        "ci95": [lo, hi],
        "dev_auc": dev_auc,
        "n_holdout_patients": len(pa),
        "n_pos": int(sum(y_real)),
        "note": "seed=42, run_mil_cost.train_eval 그대로 — 저장본(mil_cost_results.json) 재현 확인용",
    }
    print(f"    [A] real       auc={auc}  n_pos={int(sum(y_real))}/{len(pa)}  ({time.time()-t:.0f}s)")

    # ── [B] 5-seed shuffle-null ───────────────────────────────
    nulls = []
    for sd in SHUFFLE_SEEDS:
        t = time.time()
        srecs, _ = train_eval(slides, labels, endpoint, device, shuffle=True, seed=sd)
        if not srecs:
            continue
        spa = patient_agg(srecs)
        sa, _, _ = bootstrap_auc([v[1] for v in spa.values()], [v[0] for v in spa.values()])
        if sa is not None:
            nulls.append(sa)
        print(f"    [B] null s={sd:<3} auc={sa}  ({time.time()-t:.0f}s)")
    if len(nulls) >= 2:
        nm = float(np.mean(nulls))
        nsd = float(np.std(nulls, ddof=1))
        thr = nm + 2 * nsd
        robust = bool(auc is not None and auc > thr)
        res["shuffle_null_5seed"] = {
            "seeds": SHUFFLE_SEEDS[: len(nulls)],
            "null_aucs": [round(x, 4) for x in nulls],
            "null_mean": round(nm, 4),
            "null_sd": round(nsd, 4),
            "threshold_mean_plus_2sd": round(thr, 4),
            "real_auc": auc,
            "chance_exclusion_robust": robust,
            "criterion": "real > null_mean + 2*null_sd (kkkim 자체 기준, shuffle_null_robustness.json §criterion 유지)",
            "verdict": "PASS" if robust else "FAIL(우연배제 강건성 미확보 — weak≠zero)",
        }
        print(
            f"    [B] → null_mean={nm:.4f} sd={nsd:.4f} thr={thr:.4f} "
            f"→ {'PASS' if robust else '**FAIL**'}"
        )

    # ── [C] n_tiles-only baseline ★핵심★ ─────────────────────
    f_tiles = lambda sid: np.array([stats[sid]["n_tiles"]], dtype="float32")  # noqa: E731
    Xtr, ytr, _ = patient_level(tr_rows, stats, f_tiles)
    Xho, yho, cids_ho = patient_level(ho_rows, stats, f_tiles)
    res["baseline_n_tiles_only"] = fit_lr_auc(Xtr, ytr, Xho, yho)
    if res["baseline_n_tiles_only"]:
        res["baseline_n_tiles_only"]["note"] = (
            "타일 수 단일 피처 LR. 높으면 AUROC가 형태가 아니라 bag-size에서 나온다는 직접 증거."
        )
        print(f"    [C] n_tiles-only  auc={res['baseline_n_tiles_only']['auc']}  ★")

    # ── [D] mean-embed baseline ───────────────────────────────
    f_mean = lambda sid: stats[sid]["mean_vec"]  # noqa: E731
    Xtr2, ytr2, _ = patient_level(tr_rows, stats, f_mean)
    Xho2, yho2, _ = patient_level(ho_rows, stats, f_mean)
    res["baseline_mean_embed"] = fit_lr_auc(Xtr2, ytr2, Xho2, yho2)
    if res["baseline_mean_embed"]:
        res["baseline_mean_embed"]["note"] = (
            "슬라이드 임베딩 평균 → LR. MIL(attention)이 단순 평균 대비 더하는 값 측정 (7-point #2)."
        )
        print(f"    [D] mean-embed    auc={res['baseline_mean_embed']['auc']}")

    # ── [E] bag-size 교란 진단 ────────────────────────────────
    tiles_ho = [float(Xho[i][0]) for i in range(len(cids_ho))]
    proba_ho = [pa[c][0] for c in cids_ho if c in pa]
    lab_ho = [int(yho[i]) for i in range(len(cids_ho))]
    conf = {}
    if len(proba_ho) == len(tiles_ho):
        r, p = spearman(proba_ho, tiles_ho)
        conf["spearman_proba_vs_ntiles"] = {"rho": r, "p": p}
    r2, p2 = spearman(lab_ho, tiles_ho)
    conf["spearman_label_vs_ntiles"] = {
        "rho": r2,
        "p": p2,
        "note": "유의하면 라벨 자체가 타일 수와 엮인 원천 교란 → 해당 endpoint의 AUROC 전부 의심.",
    }
    conf["n_tiles_holdout"] = {
        "min": int(min(tiles_ho)),
        "median": int(np.median(tiles_ho)),
        "max": int(max(tiles_ho)),
    }
    res["bagsize_confound"] = conf
    print(
        f"    [E] spearman(proba,n_tiles)={conf.get('spearman_proba_vs_ntiles',{}).get('rho')} "
        f"· spearman(label,n_tiles)={r2}"
    )
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True,
                    choices=["LUNG_NSCLC", "GASTRIC_STAD", "HEADNECK_HNSC", "COLORECTAL"])
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--endpoints", default="",
                    help="쉼표구분. 생략 시 기존 mil_cost_results.json의 endpoint 전부.")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    labels, split, slides = load_meta(a.cancer)
    print(f"{a.cancer}: 슬라이드 {len(slides)} (임베딩 존재) / 라벨환자 {len(labels)}")
    if not slides:
        sys.exit(f"임베딩 없음 — {a.cancer}/full/embeddings/ 확인. "
                 f"(manifest가 /home/kkkim/... 개인경로면 owner 외 재현 불가 = BLOCKER-5)")

    # endpoint 결정
    if a.endpoints:
        eps = [e.strip() for e in a.endpoints.split(",") if e.strip()]
    else:
        prev = HERE / a.cancer / "full" / "mil_cost_results.json"
        if not prev.exists():
            sys.exit(f"{prev} 없음 — --endpoints 로 직접 지정하세요.")
        eps = list(json.loads(prev.read_text())["endpoints"].keys())
    print(f"  endpoints: {eps}")

    print("  슬라이드 통계(n_tiles / mean_vec) 산출 중…")
    stats = slide_stats(slides)
    nt = [v["n_tiles"] for v in stats.values()]
    print(f"  n_tiles: min={min(nt)} median={int(np.median(nt))} max={max(nt)}")

    out = {
        "cancer": a.cancer,
        "probe": "critic_robustness_probe (braveji, BIOP02-96 G2)",
        "purpose": "5-seed shuffle-null + bag-size 교란 + 필수 baseline(7-point #2). "
                   "단일시드 null 무효화 대응 — CRITIC_REVIEW_G2_ADDENDUM.md 참조.",
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "shuffle_seeds": SHUFFLE_SEEDS,
        "criterion": "real_auroc > null_mean + 2*null_sd (kkkim 자체 기준 유지)",
        "n_slides": len(slides),
        "endpoints": {},
    }
    for ep in eps:
        print(f"\n  ── {ep} ──")
        out["endpoints"][ep] = probe_endpoint(a.cancer, slides, labels, stats, ep, a.device)

    dest = Path(a.out) if a.out else (HERE / a.cancer / "full" / "critic_robustness.json")
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n✅ wrote {dest}")

    # 요약
    print("\n═══ 요약 ═══")
    hdr = f"{'endpoint':<20}{'real':>8}{'null_m':>9}{'null_sd':>9}{'thr':>8}{'robust':>9}{'n_tiles_only':>14}{'mean_embed':>12}"
    print(hdr)
    print("-" * len(hdr))
    for ep, r in out["endpoints"].items():
        if "real" not in r:
            print(f"{ep:<20}  {r.get('status')}")
            continue
        sn = r.get("shuffle_null_5seed", {})
        nt_b = (r.get("baseline_n_tiles_only") or {}).get("auc")
        me_b = (r.get("baseline_mean_embed") or {}).get("auc")
        print(
            f"{ep:<20}{str(r['real']['auc']):>8}{str(sn.get('null_mean','-')):>9}"
            f"{str(sn.get('null_sd','-')):>9}{str(sn.get('threshold_mean_plus_2sd','-')):>8}"
            f"{('PASS' if sn.get('chance_exclusion_robust') else 'FAIL'):>9}"
            f"{str(nt_b):>14}{str(me_b):>12}"
        )
    print("\n★ n_tiles_only가 높으면(≳0.7) 해당 endpoint의 AUROC는 형태가 아니라 bag-size 산물일 수 있음.")
    print("★ robust=FAIL이면 우연배제 미확립 — 그 endpoint로는 법칙을 확증/반증할 수 없음.")


if __name__ == "__main__":
    main()

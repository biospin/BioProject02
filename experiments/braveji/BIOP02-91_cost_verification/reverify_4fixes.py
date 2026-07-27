"""BIOP02-91 caution 4건 수정본 독립 재계산 (braveji Critic, 2026-07-27).

목적: `patient_routing_cost_receptor.json`(owner=kkkim)의 4건 수정이 실제로 반영됐는지
**필드 존재 확인이 아니라 원자료 재계산**으로 검증한다(Owner≠Reviewer).

검증 대상 4건 (JIRA BIOP02-91 comment 11395):
  1. headline_contrast.ci95를 환자 클러스터 부트스트랩으로 교체 (슬라이드 단위는 pseudo-replication)
  2. pred_source를 개인 홈 절대경로 → repo-relative
  3. 라우팅 임계 0.5 명시
  4. CI 산출 메타(리샘플 단위·B·seed) 기재

`/workspace` 불필요: 예측은 커밋된 CSV(BIOP02-90 재생성분, case_id 포함), 라벨은
CPTAC manifest의 repo 내 사본을 쓴다. 따라서 GPU 머신 없이도 재현된다.

Run (repo 루트에서):
    python3 experiments/braveji/BIOP02-91_cost_verification/reverify_4fixes.py

기본은 워킹트리의 파일을 읽는다. 특정 리비전을 검증하려면 --rev 로 지정한다
(내부에서 `git show <rev>:<path>`를 쓴다):
    python3 .../reverify_4fixes.py --rev origin/feat/BIOP02-91-kkkim-multifm-virchow2
"""

import argparse
import csv
import io
import json
import subprocess
import sys

import numpy as np

# --- repo-relative 경로 (개인 홈·/tmp 경로 금지 — BIOP02-91 지적사항 #2와 같은 규율) ---
PRED = "experiments/sjpark/cptac_ext_predictions_indexed.csv"
MANIFEST = "experiments/kkkim/20260709_cptac_official_join/embedding_manifest_cptac_uni_v1.csv"
TARGET = "experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost_receptor.json"

# therapeutic_distance.json (axis_pair_distance) — 1 - Kendall tau on 170 discriminating drugs
DIST = {
    ("endocrine", "antiHER2"): 0.395,
    ("endocrine", "chemo"): 0.695,
    ("antiHER2", "chemo"): 0.765,
}
THRESHOLD = 0.5  # 라우팅 임계 (검증항목 3)
B = 5000
SEED = 42
AXES = ["endocrine", "antiHER2", "chemo"]


def read(path, rev=None):
    """rev가 주어지면 git show로, 아니면 워킹트리에서 읽는다."""
    if rev:
        return subprocess.check_output(["git", "show", f"{rev}:{path}"], text=True)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def dist(a, b):
    if a == b:
        return 0.0
    return DIST.get((a, b)) or DIST.get((b, a))


def route_true(er, her2):
    if her2 == "positive":
        return "antiHER2"
    return "endocrine" if er == "positive" else "chemo"


def route_pred(er_p, her2_p, thr=THRESHOLD):
    if her2_p > thr:
        return "antiHER2"
    return "endocrine" if er_p > thr else "chemo"


def load_rows(rev):
    """예측 × 라벨을 결합해 (case_id, true_axis, pred_axis, cost) 행을 만든다."""
    pred = {r["slide_id"]: r for r in csv.DictReader(io.StringIO(read(PRED, rev)))}
    rows = []
    for r in csv.DictReader(io.StringIO(read(MANIFEST, rev))):
        sid = r["slide_id"]
        if sid not in pred:
            continue
        er = (r.get("er") or "").strip().lower()
        her2 = (r.get("her2") or "").strip().lower()
        # equivocal·결측은 제외 (원 분석과 동일 — 라벨 보유 슬라이드만)
        if her2 not in ("positive", "negative") or er not in ("positive", "negative"):
            continue
        p = pred[sid]
        t = route_true(er, her2)
        q = route_pred(float(p["er_pred_prob"]), float(p["her2_pred_prob"]))
        rows.append((r["case_id"], t, q, dist(t, q)))
    if not rows:
        sys.exit("결합 결과가 0행 — 경로/컬럼을 확인하라")
    return rows


def patient_bootstrap(case, axis, cost):
    """환자 클러스터 부트스트랩. 같은 환자의 슬라이드는 라벨이 같고 예측이 상관되므로
    독립 표본이 아니다 → 슬라이드 단위 리샘플은 CI를 과소추정한다."""
    rng = np.random.default_rng(SEED)
    pats = sorted(set(case))
    idx_by = {p: np.where(case == p)[0] for p in pats}
    draws = []
    for _ in range(B):
        i = np.concatenate([idx_by[p] for p in rng.choice(pats, len(pats), replace=True)])
        a2, c2 = axis[i], cost[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0:
            continue
        d = {t: (c2[a2 == t].mean() if (a2 == t).sum() else np.nan) for t in AXES}
        d["headline"] = c2[a2 == "antiHER2"].mean() - c2[a2 == "endocrine"].mean()
        draws.append(d)
    return draws


def ci95(draws, key):
    v = np.array([d[key] for d in draws], dtype=float)
    v = v[~np.isnan(v)]
    return [round(float(x), 4) for x in np.percentile(v, [2.5, 97.5])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default=None,
                    help="검증할 git 리비전 (생략 시 워킹트리)")
    args = ap.parse_args()

    rows = load_rows(args.rev)
    case = np.array([r[0] for r in rows])
    axis = np.array([r[1] for r in rows])
    predr = np.array([r[2] for r in rows])
    cost = np.array([r[3] for r in rows])
    n_s, n_p = len(rows), len(set(case))
    print(f"n_slides={n_s}  n_patients={n_p}  (평균 {n_s / n_p:.2f}장/환자)")

    draws = patient_bootstrap(case, axis, cost)
    mine = {
        "n_slides": n_s,
        "n_patients": n_p,
        "confusion": {t: {q: int(((axis == t) & (predr == q)).sum())
                          for q in AXES if ((axis == t) & (predr == q)).sum()}
                      for t in AXES},
        "per_axis": {t: {"n": int((axis == t).sum()),
                         "mean_cost": round(float(cost[axis == t].mean()), 4),
                         "misroute_rate": round(float(1 - (predr[axis == t] == t).mean()), 3),
                         "mean_cost_ci95_patient": ci95(draws, t)}
                     for t in AXES},
        "headline_contrast": round(
            float(cost[axis == "antiHER2"].mean() - cost[axis == "endocrine"].mean()), 4),
        "headline_ci95_patient": ci95(draws, "headline"),
    }
    print(json.dumps(mine, ensure_ascii=False, indent=2))

    committed = json.loads(read(TARGET, args.rev))
    pa = committed["per_axis"]
    print("\n===== 커밋본 대조 =====")
    ok = True

    def chk(label, got, want, tol=0.0):
        nonlocal ok
        if isinstance(got, list) and isinstance(want, list):
            match = len(got) == len(want) and all(abs(x - y) <= tol for x, y in zip(got, want))
        elif isinstance(got, (int, float)) and isinstance(want, (int, float)):
            match = abs(got - want) <= tol
        else:
            match = got == want
        ok &= match
        print(f"{'✅' if match else '❌'} {label}: 재계산 {got} | 커밋 {want}")

    # 검증항목 2·3·4 — 메타 필드
    chk("[3] routing_threshold", THRESHOLD, committed["routing_threshold"])
    chk("[2] pred_source repo-relative", True, not committed["pred_source"].startswith("/"))
    chk("[4] ci_method.resample_unit", "patient",
        committed["ci_method"]["resample_unit"].split(" ")[0])
    chk("[4] ci_method.n_bootstrap", B, committed["ci_method"]["n_bootstrap"])
    chk("[4] ci_method.seed", SEED, committed["ci_method"]["seed"])
    chk("[4] ci_method.n_slides", n_s, committed["ci_method"]["n_slides"])
    chk("[4] ci_method.n_patients", n_p, committed["ci_method"]["n_patients"])

    # 검증항목 1 + 수치 무결성. CI는 부트스트랩 재현이라 소폭 허용(0.006).
    hc = pa["headline_contrast"]
    chk("headline_contrast", mine["headline_contrast"], hc["value"], 0.0002)
    chk("[1] headline CI95 (환자단위)", mine["headline_ci95_patient"], hc["ci95"], 0.006)
    for t in AXES:
        chk(f"{t}.mean_cost", mine["per_axis"][t]["mean_cost"], pa[t]["mean_cost"], 0.0002)
        chk(f"{t}.CI95_patient", mine["per_axis"][t]["mean_cost_ci95_patient"],
            pa[t]["mean_cost_ci95_patient"], 0.006)
        chk(f"{t}.misroute_rate", mine["per_axis"][t]["misroute_rate"],
            pa[t]["misroute_rate"], 0.002)
    chk("confusion", mine["confusion"], committed["confusion_true_to_pred"])

    print("\n>>> 전체 일치:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""BIOP02-141 #8 — 슬라이드·영역 강건성 (HPV·MSI 우선).

카드 지침: 종양 annotation·coords 없음 → tumor-only/necrosis 제외는 '안 됨'으로 적고,
"몇 개 타일/영역에 의존하나"는 대체 지표(타일 subsample·top-k 집중도)로 본다. 억지로 안 함.

(A) 다중슬라이드 일치도 — 한 환자 여러 슬라이드의 예측 score 일치도.
    ⚠️ 제약: 다중슬라이드 환자에 endpoint 양성이 거의 없다(HNSC HPV+ 1, GAST MSI+ 0).
    → 양성 클래스 일치도는 측정 불가. score/음성 기준으로만 보고하고 그 한계를 명시한다.

(B) 타일 subsample region-robustness (대체 지표, 양성 포함 전 환자).
    각 환자 첫 슬라이드에서 타일을 무작위 subsample→mean-pool→held-out LR로 재점수.
    subsample 간 score 변동(SD·call flip)이 작으면 신호가 슬라이드 전반에 퍼짐(강건),
    크면 소수 타일/영역 의존. OOF(StratifiedKFold) 모델로 leakage 차단.

(C) 타일 기여 집중도 — held-out LR 가중치로 per-tile 선형기여 s_i=w·z_i 계산,
    상위 5%/10% 타일이 슬라이드 신호에서 차지하는 비중. 높으면 소수 타일 의존.

CPU. 기존 UNI per-tile 임베딩 재사용(신규 데이터 없음).
"""
import argparse, csv, json
from pathlib import Path
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

META = "/workspace/data/cache/biop02_site_audit"
EMB = "/workspace/data/cache/biop02/crosscancer/{cohort}/uni_v1"


def load_cohort(cohort, endpoint):
    meta = Path(META) / cohort
    labels = {r["case_id"]: r for r in csv.DictReader(open(meta / "patient_labels.csv"))}
    emb = Path(EMB.format(cohort=cohort))
    bycase = defaultdict(list)
    for p in sorted(emb.glob("*_uni_embeddings.npy")):
        bycase[p.name[:12]].append(p)
    return labels, bycase


def multislide_concordance(labels, bycase, endpoint, seed=42):
    """(A) 다중슬라이드 환자에서 슬라이드 간 score 일치도.
    held-out LR(단일슬라이드 환자로 학습)로 각 슬라이드를 독립 점수."""
    single = {c: v[0] for c, v in bycase.items()
              if len(v) == 1 and c in labels and labels[c].get(endpoint) in ("0", "1")}
    multi = {c: v for c, v in bycase.items()
             if len(v) >= 2 and c in labels and labels[c].get(endpoint) in ("0", "1")}
    # 학습: 단일슬라이드 환자 mean-pool
    Xtr = np.stack([np.load(single[c]).mean(0) for c in single]).astype(np.float32)
    ytr = np.array([int(labels[c][endpoint]) for c in single])
    sc = StandardScaler().fit(Xtr)
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(sc.transform(Xtr), ytr)
    rows = []
    for c, paths in multi.items():
        scores = [float(clf.predict_proba(sc.transform(np.load(p).mean(0)[None]))[0, 1]) for p in paths]
        rows.append({"case": c, "label": int(labels[c][endpoint]), "n_slides": len(paths),
                     "slide_scores": [round(s, 4) for s in scores],
                     "score_sd": round(float(np.std(scores, ddof=1)), 4),
                     "score_range": round(float(max(scores) - min(scores)), 4),
                     "calls_agree@0.5": bool(len({s >= 0.5 for s in scores}) == 1)})
    npos = sum(r["label"] for r in rows)
    agree = [r for r in rows if r["calls_agree@0.5"]]
    return {
        "n_multislide_patients": len(rows), "n_pos": npos, "n_neg": len(rows) - npos,
        "median_score_sd": round(float(np.median([r["score_sd"] for r in rows])), 4) if rows else None,
        "median_score_range": round(float(np.median([r["score_range"] for r in rows])), 4) if rows else None,
        "call_agree_rate@0.5": round(len(agree) / len(rows), 4) if rows else None,
        "CONSTRAINT": f"양성 다중슬라이드 환자 {npos}명 — 양성 클래스 일치도는 사실상 측정 불가. "
                      f"아래 일치율은 대부분 음성(모델이 자신있게 낮게 주는)에 지배됨 → 정작 검증하려던 "
                      f"'HPV/MSI 양성 확증이 슬라이드 추첨에 의존하나'는 이 데이터로 답할 수 없다.",
        "per_patient": sorted(rows, key=lambda r: -r["label"]),
    }


def region_robustness(labels, bycase, endpoint, B=50, fracs=(0.5, 0.25), seed=42):
    """(B)+(C) OOF 모델로 타일 subsample 안정성 + 타일기여 집중도."""
    cases = [c for c, v in bycase.items() if c in labels and labels[c].get(endpoint) in ("0", "1")]
    paths = {c: bycase[c][0] for c in cases}  # 환자당 첫 슬라이드
    y = np.array([int(labels[c][endpoint]) for c in cases])
    Xmean = np.stack([np.load(paths[c]).mean(0) for c in cases]).astype(np.float32)

    rng = np.random.default_rng(seed)
    skf = StratifiedKFold(5, shuffle=True, random_state=seed)
    oof = np.zeros(len(cases))
    per = {c: {} for c in cases}
    idx = np.arange(len(cases))
    for tr, te in skf.split(Xmean, y):
        sc = StandardScaler().fit(Xmean[tr])
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(sc.transform(Xmean[tr]), y[tr])
        w = clf.coef_[0]; b = clf.intercept_[0]
        for i in te:
            c = cases[i]
            Z = sc.transform(np.load(paths[c]))          # (n_tiles, d) 표준화 타일
            full = float(clf.predict_proba(Z.mean(0)[None])[0, 1])
            oof[i] = full
            per[c]["label"] = int(y[i]); per[c]["n_tiles"] = int(Z.shape[0]); per[c]["full_score"] = round(full, 4)
            # (B) subsample 안정성
            for frac in fracs:
                k = max(20, int(frac * Z.shape[0]))
                ss = []
                for _ in range(B):
                    sub = rng.choice(Z.shape[0], k, replace=False)
                    ss.append(float(clf.predict_proba(Z[sub].mean(0)[None])[0, 1]))
                ss = np.array(ss)
                per[c][f"sd@{frac}"] = round(float(ss.std(ddof=1)), 4)
                per[c][f"flip@{frac}"] = round(float((( ss >= 0.5) != (full >= 0.5)).mean()), 4)
            # (C) 타일기여 집중도: s_i = w·z_i (슬라이드 logit ∝ mean s_i + b)
            s = Z @ w
            order = np.argsort(-s)  # 양의 기여 큰 순
            tot = s.sum()
            top5 = int(max(1, 0.05 * len(s)))
            per[c]["top5pct_tile_share"] = round(float(s[order[:top5]].sum() / tot), 4) if tot != 0 else None
    auc = roc_auc_score(y, oof)

    def agg(mask, key):
        vals = [per[c][key] for c in cases if per[c]["label"] == mask and key in per[c] and per[c][key] is not None]
        return round(float(np.median(vals)), 4) if vals else None

    summary = {"endpoint": endpoint, "n": len(cases), "n_pos": int(y.sum()),
               "oof_auroc_meanpool": round(float(auc), 4), "B_subsamples": B, "fracs": list(fracs)}
    for cls, nm in [(1, "pos"), (0, "neg")]:
        summary[nm] = {
            "median_sd@0.5": agg(cls, "sd@0.5"), "median_flip@0.5": agg(cls, "flip@0.5"),
            "median_sd@0.25": agg(cls, "sd@0.25"), "median_flip@0.25": agg(cls, "flip@0.25"),
            "median_top5pct_tile_share": agg(cls, "top5pct_tile_share"),
        }
    return summary, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--B", type=int, default=50)
    a = ap.parse_args()
    labels, bycase = load_cohort(a.cohort, a.endpoint)
    print(f"[{a.cohort}/{a.endpoint}] 환자 {len(bycase)}", flush=True)
    conc = multislide_concordance(labels, bycase, a.endpoint)
    print(f"  (A) 다중슬라이드 {conc['n_multislide_patients']}명(양성 {conc['n_pos']}) "
          f"일치율@0.5 {conc['call_agree_rate@0.5']} · median score_sd {conc['median_score_sd']}", flush=True)
    rob, per = region_robustness(labels, bycase, a.endpoint, B=a.B)
    print(f"  (B) region-robustness oof-AUROC {rob['oof_auroc_meanpool']} "
          f"pos: sd@0.5 {rob['pos']['median_sd@0.5']} flip@0.5 {rob['pos']['median_flip@0.5']} "
          f"top5%share {rob['pos']['median_top5pct_tile_share']} | "
          f"neg: sd@0.5 {rob['neg']['median_sd@0.5']} top5%share {rob['neg']['median_top5pct_tile_share']}", flush=True)
    out = {"cohort": a.cohort, "endpoint": a.endpoint,
           "A_multislide_concordance": conc, "B_region_robustness": rob,
           "NOT_FEASIBLE": {
               "tumor_only_vs_wsi": "종양영역 annotation 없음 → 측정 불가(카드 지침대로 '안 됨' 기록).",
               "necrosis_stroma_exclusion": "조직타입 annotation 없음 → 측정 불가.",
               "attention_FM_cross": "crosscancer 임베딩은 uni_v1 단일 FM만 존재 → FM 교차 attention 불가.",
               "attention_seed_cross": "학습된 CLAM 모델 없음 → seed 교차 attention은 CLAM 학습(GPU) 필요, heavier follow-up.",
           }}
    json.dump(out, open(a.out, "w"), indent=2, ensure_ascii=False)
    print(f"Saved {a.out}\nDONE_{a.cohort}")


if __name__ == "__main__":
    main()

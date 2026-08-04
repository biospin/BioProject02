#!/usr/bin/env python3
"""BIOP02-75/91 remediation — PAM50 라우팅 CI 환자단위 교체 + 리포 커밋용 인덱스 CSV.

배경: patient_routing_cost.json(PAM50 라우팅, headline 0.340)의 CI가 슬라이드 단위
부트스트랩이라 receptor와 동일한 pseudo-replication. 그러나 소스 predictions_ext.npz에
id 배열이 없어 환자 클러스터링이 막혀 있었다.

id 복원(증명): npz row i = embedding_manifest_cptac_uni.csv의 has_pam50 i번째 행.
label 배열이 395/395 행별 완전일치로 확인됨(추측 아님). → case_id 부여 가능.

산출:
  (1) pam50_ext_predictions_indexed.csv — braveji 독립 재계산용(리포 커밋). slide_id·case_id·true·pred·proba·cost.
  (2) patient_routing_cost.json 갱신 — headline+per_axis CI를 환자 클러스터 부트스트랩으로.
"""
import csv, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
NPZ = HERE.parent.parent / "sjpark/pam50_clam_mb_uni_v1/predictions_ext.npz"
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"
JSON = HERE / "patient_routing_cost.json"
OUT_CSV = Path("experiments/sjpark/pam50_clam_mb_uni_v1/predictions_ext_indexed.csv")
B, SEED = 5000, 42

PAM = {'LumA': 0, 'LumB': 1, 'Basal': 2, 'HER2': 3, 'Normal-like': 4}
CLASS_NAME = {0: 'LumA', 1: 'LumB', 2: 'Basal', 3: 'HER2', 4: 'Normal'}
PAM50_AXIS = {0: "endocrine", 1: "endocrine", 2: "chemo", 3: "antiHER2", 4: None}
DIST = {("endocrine", "antiHER2"): 0.395, ("endocrine", "chemo"): 0.695, ("antiHER2", "chemo"): 0.765}
MAXD = max(DIST.values())  # 0.765 = 예측 Normal(무치료) 최대 페널티

def tdist(a, b):
    if a == b: return 0.0
    return DIST.get((a, b)) or DIST.get((b, a))

def main():
    pz = np.load(NPZ, allow_pickle=True)
    lab, pred, proba = pz['label'], pz['pred'], pz['proba']
    mrows = [r for r in csv.DictReader(open(MANIFEST)) if r.get('pam50', '').strip() in PAM]
    mlab = np.array([PAM[r['pam50'].strip()] for r in mrows])
    assert len(mrows) == len(lab) and (mlab == lab).all(), "매핑 불일치 — id 복원 실패(추측 금지)"

    rows = []
    for i, r in enumerate(mrows):
        m, p = int(lab[i]), int(pred[i])
        ma, pa = PAM50_AXIS[m], PAM50_AXIS[p]
        if ma is None:   # measured Normal → 라우팅 대상 아님
            continue
        if pa is None:   # 예측 Normal → 무치료 최대 페널티
            cost = MAXD
        else:
            cost = tdist(ma, pa)
        rows.append({"slide_id": r['slide_id'], "case_id": r['case_id'],
                     "pam50_true": CLASS_NAME[m], "pam50_pred": CLASS_NAME[p],
                     **{f"proba_{CLASS_NAME[k]}": round(float(proba[i][k]), 6) for k in range(5)},
                     "true_axis": ma, "pred_axis": pa or "none_Normal", "cost": round(cost, 4)})

    # (1) 인덱스 CSV (리포 커밋)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    n_pat = len(set(r['case_id'] for r in rows))
    print(f"[CSV] {OUT_CSV}: {len(rows)}행 / 환자 {n_pat}명 ({len(rows)/n_pat:.2f} 슬라이드/환자)")

    # (2) 환자 클러스터 부트스트랩
    case = np.array([r['case_id'] for r in rows]); axis = np.array([r['true_axis'] for r in rows])
    cost = np.array([r['cost'] for r in rows])
    def mc(ax, i): return cost[i][axis[i] == ax].mean() if (axis[i] == ax).any() else np.nan
    pats = sorted(set(case)); idx_by = {p: np.where(case == p)[0] for p in pats}
    rng = np.random.default_rng(SEED)
    axes = ["endocrine", "antiHER2", "chemo"]
    bh, bax = [], {a: [] for a in axes}
    for _ in range(B):
        pick = rng.choice(pats, len(pats), replace=True)
        i = np.concatenate([idx_by[p] for p in pick]); a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0: continue
        bh.append(cost[i][a2 == "antiHER2"].mean() - cost[i][a2 == "endocrine"].mean())
        for a in axes:
            if (a2 == a).any(): bax[a].append(cost[i][a2 == a].mean())
    lo_p, hi_p = np.percentile(bh, [2.5, 97.5])
    # slide-level (기존 값 재현 대조)
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(rows), len(rows)); a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0: continue
        bs.append(cost[i][a2 == "antiHER2"].mean() - cost[i][a2 == "endocrine"].mean())
    lo_s, hi_s = np.percentile(bs, [2.5, 97.5])
    full = np.ones(len(rows), bool)
    ct = float(cost[axis == "antiHER2"].mean() - cost[axis == "endocrine"].mean())
    print(f"headline={ct:.4f}  patient-CI=[{lo_p:.4f},{hi_p:.4f}]  slide-CI=[{lo_s:.4f},{hi_s:.4f}]  0배제={lo_p>0}")

    j = json.load(open(JSON))
    for a in axes:
        lo, hi = np.percentile(bax[a], [2.5, 97.5])
        j["per_axis"][a]["mean_cost_ci95_patient"] = [round(float(lo), 4), round(float(hi), 4)]
    j["headline_contrast_antiHER2_minus_endocrine"] = {
        "value": round(ct, 4), "ci95": [round(float(lo_p), 4), round(float(hi_p), 4)],
        "ci95_method": "patient-cluster bootstrap", "excludes_zero": bool(lo_p > 0),
        "ci95_slide_level_deprecated": [round(float(lo_s), 4), round(float(hi_s), 4)]}
    j["ci_method"] = {"resample_unit": "patient (cluster bootstrap)", "n_bootstrap": B, "seed": SEED,
                      "n_slides": len(rows), "n_patients": n_pat,
                      "index_source": "predictions_ext_indexed.csv (npz↔manifest has_pam50 행별 label 완전일치로 case_id 복원)"}
    j["indexed_predictions"] = str(OUT_CSV)
    JSON.write_text(json.dumps(j, ensure_ascii=False, indent=2))
    print(f"[JSON] {JSON} 갱신")

if __name__ == "__main__":
    main()

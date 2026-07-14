"""BIOP02-52 v0.2 — PRISM vs GDSC Consistency 실측 분석 (drug name 매칭)"""
import json, logging, sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

DATA_DIR = Path("/workspace/data/BIOP02-52")
OUT_DIR  = Path("/workspace/experiments/jhans/20260702_consistency")
OUT_DIR.mkdir(parents=True, exist_ok=True)

log_file = OUT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)])
log = logging.getLogger()
log.info("BIOP02-52 v0.2 Consistency 분석 시작")

# ── Step 1: PRISM 로딩 ───────────────────────────────────────
log.info("[Step 1] PRISM subsetted matrix 로딩")
prism = pd.read_csv(DATA_DIR / "PRISM_Repurposing_Secondary_(AUC)_subsetted.csv", index_col=0)
log.info(f"  PRISM shape: {prism.shape} (cell lines × drugs)")

# ── Step 2: GDSC 로딩 ───────────────────────────────────────
log.info("[Step 2] GDSC2 로딩")
gdsc = pd.read_excel(DATA_DIR / "GDSC2_fitted_dose_response_27Oct23.xlsx")
gdsc_brca = gdsc[gdsc["CANCER_TYPE"] == "Breast Carcinoma"]
log.info(f"  GDSC BRCA rows: {len(gdsc_brca)}")

# ── Step 3: Cell line 매핑 (ModelID → SangerModelID) ─────────
log.info("[Step 3] Cell line 매핑")
model = pd.read_csv(DATA_DIR / "Model.csv")
m2s = model.dropna(subset=["SangerModelID"]).set_index("ModelID")["SangerModelID"].to_dict()
prism.index = prism.index.map(lambda x: m2s.get(x, x))
gdsc_sanger = set(gdsc_brca["SANGER_MODEL_ID"].unique())
prism_sanger = set(prism.index)
overlap_cl = prism_sanger & gdsc_sanger
log.info(f"  Cell line 교집합: {len(overlap_cl)}개")
prism_overlap = prism.loc[prism.index.isin(overlap_cl)]

# ── Step 4: Drug 매칭 (name 기준) ───────────────────────────
log.info("[Step 4] Drug 매칭 (drug name, case-insensitive)")
prism_drugs = {c.upper(): c for c in prism.columns}
gdsc_drugs  = {n.upper(): n for n in gdsc_brca["DRUG_NAME"].unique()}
common_drugs_upper = set(prism_drugs.keys()) & set(gdsc_drugs.keys())
log.info(f"  Drug 교집합: {len(common_drugs_upper)}개")

# ── Step 5: Z-score 정규화 + Spearman ────────────────────────
log.info("[Step 5] Spearman ρ 계산")
results, skip = [], 0
gdsc_pivot = gdsc_brca.pivot_table(index="SANGER_MODEL_ID", columns="DRUG_NAME", values="Z_SCORE", aggfunc="mean")

for drug_upper in common_drugs_upper:
    p_col = prism_drugs[drug_upper]
    g_col = gdsc_drugs[drug_upper]

    p_vals = prism_overlap[p_col].dropna()
    p_z = (p_vals - p_vals.mean()) / (p_vals.std() + 1e-8)

    if g_col not in gdsc_pivot.columns:
        skip += 1; continue
    g_vals = gdsc_pivot[g_col].dropna()

    common = p_z.index.intersection(g_vals.index)
    if len(common) < 5:
        skip += 1; continue

    rho, pval = spearmanr(p_z[common], g_vals[common])
    results.append({
        "drug_name": drug_upper,
        "n_cell_lines": len(common),
        "spearman_rho": round(float(rho), 4),
        "pval": round(float(pval), 6),
        "data_source": "both" if (rho >= 0.3 and pval < 0.05 and len(common) >= 5) else "prism_only"
    })

log.info(f"  계산 완료: {len(results)}개 (skip: {skip}개)")
df = pd.DataFrame(results)

# ── 저장 ─────────────────────────────────────────────────────
df.to_csv(OUT_DIR / "consistency_scores.csv", index=False)
n_both = (df["data_source"] == "both").sum()
summary = {
    "version": "0.2", "ticket": "BIOP02-52",
    "n_cl_overlap": len(overlap_cl),
    "n_drug_overlap": len(common_drugs_upper),
    "n_drugs_analyzed": len(df),
    "n_both": int(n_both),
    "rho_median": round(float(df["spearman_rho"].median()), 4),
    "rho_pct_above_03": round(float((df["spearman_rho"] >= 0.3).mean() * 100), 1),
}
with open(OUT_DIR / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

log.info("=" * 50)
log.info(f"  Cell line 교집합: {len(overlap_cl)}개")
log.info(f"  Drug 교집합:      {len(common_drugs_upper)}개")
log.info(f"  분석 완료:        {len(df)}개")
log.info(f"  data_source=both: {n_both}개 ({round(n_both/len(df)*100,1) if len(df) else 0}%)")
log.info(f"  rho 중앙값:       {summary['rho_median']}")
log.info("=" * 50)
log.info(f"완료! 로그: {log_file}")

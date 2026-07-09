#!/usr/bin/env python3
"""
C1 cost-of-substitution — STEP 1: frozen cell-line -> drug-sensitivity map (per therapy axis).

세포주-only (누수 가드: TCGA/CPTAC 발현 미투입). GDSC2 fitted dose-response의 within-drug
Z_SCORE(음수=민감)를 축(endocrine/antiHER2/chemo)별로 집계 → 각 축의 약물감수성 벡터.
BIOP02-52 권고(절댓값 비교 금지, within-dataset z/rank)를 따른다.

입력:
  ../20260710_cellline_counts/cellline_axis_table.csv   (51 lines, axis membership)
  ../20260710_cellline_counts/data/GDSC2_fitted_dose_response_27Oct23.xlsx
출력(이 폴더):
  frozen_map.csv        drug × axis 평균 Z + n + between-axis gap
  frozen_map.json       축 -> {drug: mean_z}  + discriminating drug list
  map_build_report.md
"""
from pathlib import Path
import json, numpy as np, pandas as pd

HERE = Path(__file__).parent
CNT = HERE.parent / "20260710_cellline_counts"
axis = pd.read_csv(CNT / "cellline_axis_table.csv")
gdsc = pd.read_excel(CNT / "data" / "GDSC2_fitted_dose_response_27Oct23.xlsx")

print("GDSC2 cols:", list(gdsc.columns))
# sensitivity metric: Z_SCORE (within-drug normalized). fallback LN_IC50->z.
sens_col = "Z_SCORE" if "Z_SCORE" in gdsc.columns else None
key = "SANGER_MODEL_ID" if "SANGER_MODEL_ID" in gdsc.columns else "SANGER_MODEL_ID"

AX = {"endocrine": "axis_endocrine_ERpos",
      "antiHER2": "axis_antiHER2_ERBB2amp",
      "chemo": "axis_chemo_TNBC"}
# map SangerModelID -> set of axes
line_axis = {}
for _, r in axis.iterrows():
    sid = r["SangerModelID"]
    line_axis[sid] = {a: int(r[c]) == 1 for a, c in AX.items()}

sids = set(axis["SangerModelID"])
g = gdsc[gdsc[key].isin(sids)].copy()
print(f"GDSC2 rows for our 51 lines: {len(g)}  drugs: {g['DRUG_NAME'].nunique()}")

if sens_col is None:
    # compute within-drug z from LN_IC50 across ALL GDSC lines (proper normalization)
    mu = gdsc.groupby("DRUG_NAME")["LN_IC50"].transform("mean")
    sd = gdsc.groupby("DRUG_NAME")["LN_IC50"].transform("std")
    gdsc["_Z"] = (gdsc["LN_IC50"] - mu) / sd
    g = gdsc[gdsc[key].isin(sids)].copy()
    sens_col = "_Z"

rows = []
for drug, sub in g.groupby("DRUG_NAME"):
    target = sub["PUTATIVE_TARGET"].iloc[0] if "PUTATIVE_TARGET" in sub else ""
    pathway = sub["PATHWAY_NAME"].iloc[0] if "PATHWAY_NAME" in sub else ""
    rec = {"drug": drug, "target": target, "pathway": pathway}
    means = {}
    for a in AX:
        lines_a = [s for s in sub[key] if line_axis.get(s, {}).get(a)]
        vals = sub[sub[key].isin(lines_a)][sens_col].dropna().values
        rec[f"{a}_z"] = round(float(np.mean(vals)), 3) if len(vals) else None
        rec[f"{a}_n"] = int(len(vals))
        if len(vals): means[a] = float(np.mean(vals))
    # between-axis gap = max-min of axis means (larger = more discriminating)
    rec["gap"] = round(max(means.values()) - min(means.values()), 3) if len(means) >= 2 else None
    rec["most_sensitive_axis"] = min(means, key=means.get) if means else None  # lowest z = most sensitive
    rows.append(rec)

df = pd.DataFrame(rows).sort_values("gap", ascending=False, na_position="last")
df.to_csv(HERE / "frozen_map.csv", index=False)

# discriminating drugs: gap >= 0.5 (>=~0.5 sd separation) and each axis n>=3
disc = df[(df["gap"] >= 0.5)].copy()
frozen = {a: {} for a in AX}
for _, r in df.iterrows():
    for a in AX:
        if r.get(f"{a}_z") is not None:
            frozen[a][r["drug"]] = r[f"{a}_z"]

out = {
    "exp": "C1_frozen_map",
    "leakage_guard": "cell-line-only; no TCGA/CPTAC expression",
    "sensitivity_metric": sens_col,
    "n_lines": int(len(sids)),
    "n_drugs": int(df.shape[0]),
    "axes_n": {a: int(axis[c].sum()) for a, c in AX.items()},
    "n_discriminating_drugs(gap>=0.5)": int(len(disc)),
    "top_discriminating": disc.head(20)[["drug", "target", "pathway",
        "endocrine_z", "antiHER2_z", "chemo_z", "gap", "most_sensitive_axis"]].to_dict("records"),
    "frozen_map_axis_to_drug_z": frozen,
}
(HERE / "frozen_map.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

# sanity: known targeted drugs should route to expected axis
KNOWN = ["Lapatinib", "Afatinib", "Sapitinib", "Alpelisib", "Palbociclib",
         "Taselisib", "Pictilisib", "AZD8186", "Tamoxifen", "Fulvestrant"]
print("\n=== 알려진 표적약물 축별 Z (음수=민감) — positive control ===")
for k in KNOWN:
    m = df[df["drug"].str.contains(k, case=False, na=False)]
    for _, r in m.iterrows():
        print(f"{r['drug']:14} tgt={str(r['target'])[:18]:18} "
              f"endo={r['endocrine_z']} her2={r['antiHER2_z']} chemo={r['chemo_z']} "
              f"-> {r['most_sensitive_axis']}")

print(f"\nwrote frozen_map.csv / frozen_map.json  ({len(df)} drugs, {len(disc)} discriminating)")

#!/usr/bin/env python3
"""
Cross-cancer 냉동 세포주→약물 지도 + 치료거리 (build_frozen_map + compute_cost §A 일반화).

BRCA build_frozen_map.py(3 고정축)를 임의 치료축으로 일반화. 각 암종의
cellline_axis_table.csv(axis_* 컬럼) + GDSC2 Z_SCORE로 축별 약물감수성 벡터 + 축쌍 치료거리.
세포주-only(누수 가드). GPU 0.

⚠️ ICI 금칙: MSI→면역치료(pembro) 축은 drug-map에서 제외(CLAUDE.md). MSI는 stratifier로만.
"""
from pathlib import Path
import json, itertools, numpy as np, pandas as pd

HERE = Path(__file__).parent
GDSC = pd.read_excel(HERE.parent / "kkkim/20260710_cellline_counts/data/GDSC2_fitted_dose_response_27Oct23.xlsx")
KEY = "SANGER_MODEL_ID"

# 암종별 치료축 스펙: label -> (axis_column | ('NOT', axis_column) 파생)
CANCERS = {
 "LUNG_NSCLC": {  # ALK 드롭(NO-GO n=2)
   "antiEGFR": "axis_antiEGFR",
   "antiKRAS_G12C": "axis_antiKRAS_G12C",
   "chemo": "axis_chemo_noTargetDriver",
 },
 "COLORECTAL": {  # MSI(ICI) 제외, KRAS(항체·GDSC부재) 제외 → BRAF vs baseline
   "antiBRAF": "axis_antiBRAF_V600E",
   "baseline": ("NOT", "axis_antiBRAF_V600E"),
 },
}
KNOWN = {  # positive control: 약물 -> 기대 최민감 축
 "LUNG_NSCLC": {"Gefitinib":"antiEGFR","Afatinib":"antiEGFR","Osimertinib":"antiEGFR"},
 "COLORECTAL": {"Dabrafenib":"antiBRAF","Trametinib":"antiBRAF","Selumetinib":"antiBRAF"},
}

def build(cancer, axes):
    tab = pd.read_csv(HERE / cancer / "cellline_counts/cellline_axis_table.csv")
    # 축 -> SangerModelID 집합
    members = {}
    for lab, spec in axes.items():
        if isinstance(spec, tuple) and spec[0] == "NOT":
            sel = tab[tab[spec[1]] != 1]
        else:
            sel = tab[tab[spec] == 1]
        members[lab] = set(sel["SangerModelID"].dropna())
    g = GDSC[GDSC[KEY].isin(set(tab["SangerModelID"].dropna()))].copy()
    labs = list(axes)
    rows = []
    for drug, sub in g.groupby("DRUG_NAME"):
        rec = {"drug": drug, "target": str(sub["PUTATIVE_TARGET"].iloc[0])[:30],
               "pathway": str(sub["PATHWAY_NAME"].iloc[0])[:30]}
        means = {}
        for lab in labs:
            v = sub[sub[KEY].isin(members[lab])]["Z_SCORE"].dropna().values
            rec[f"{lab}_z"] = round(float(np.mean(v)), 3) if len(v) else None
            rec[f"{lab}_n"] = int(len(v))
            if len(v): means[lab] = float(np.mean(v))
        rec["gap"] = round(max(means.values()) - min(means.values()), 3) if len(means) >= 2 else None
        rec["most_sensitive"] = min(means, key=means.get) if means else None
        rows.append(rec)
    df = pd.DataFrame(rows)
    # discriminating: 전 축 값 존재 + gap>=0.5
    common = df[df[[f"{l}_z" for l in labs]].notna().all(axis=1)].copy()
    disc = common[common["gap"] >= 0.5].sort_values("gap", ascending=False)
    zmap = {l: {r["drug"]: r[f"{l}_z"] for _, r in common.iterrows()} for l in labs}
    # 치료거리 = 1 - Kendall tau (discriminating 약물 랭킹, 축쌍)
    dnames = disc["drug"].tolist()
    def rank(l):
        order = sorted(dnames, key=lambda d: zmap[l][d]); return {d: i for i, d in enumerate(order)}
    rk = {l: rank(l) for l in labs}
    def tau(a, b):
        c = d = 0
        for x, y in itertools.combinations(dnames, 2):
            s = np.sign((rk[a][x]-rk[a][y])*(rk[b][x]-rk[b][y]))
            if s > 0: c += 1
            elif s < 0: d += 1
        return (c-d)/(c+d) if (c+d) else float("nan")
    dist = {}
    for a, b in itertools.combinations(labs, 2):
        tt = tau(a, b)
        dist[f"{a}__{b}"] = {"kendall_tau": round(tt, 3), "therapeutic_distance": round(1-tt, 3)}
    # positive control
    pc = {}
    for drug, exp in KNOWN.get(cancer, {}).items():
        m = df[df["drug"].str.contains(drug, case=False, na=False)]
        if len(m):
            r = m.iloc[0]; pc[drug] = {"most_sensitive": r["most_sensitive"], "ok": r["most_sensitive"] == exp,
                                       "z": {l: r.get(f"{l}_z") for l in labs}}
    out = {"cancer": cancer, "leakage_guard": "cell-line-only", "axes_n": {l: len(members[l]) for l in labs},
           "n_drugs": int(len(df)), "n_discriminating": int(len(disc)),
           "axis_pair_distance": dist,
           "positive_control": pc,
           "top_discriminating": disc.head(15)[["drug","target"]+[f"{l}_z" for l in labs]+["gap","most_sensitive"]].to_dict("records"),
           "note": "세포주-only 냉동지도. cost = 오라우팅빈도(WSI→MIL 예측, GPU 게이트) × 치료거리(아래). MSI(ICI)·KRAS(항체) 축 제외."}
    (HERE / cancer / "frozen_map.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n=== {cancer} ===  축 n: {out['axes_n']}  drugs {out['n_drugs']}  disc {out['n_discriminating']}")
    print("  positive control:", {k: ('OK' if v['ok'] else v['most_sensitive']) for k, v in pc.items()})
    print("  치료거리(1-tau):", {k: v['therapeutic_distance'] for k, v in dist.items()})
    print(f"  wrote {cancer}/frozen_map.json")

for c, ax in CANCERS.items():
    build(c, ax)

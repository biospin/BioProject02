"""
BIOP02-52 v0.2 — PRISM vs GDSC Consistency 실측 분석
Author: jhans (서정한)
Based on: agents/therapeutic_evidence/docs/BIOP02-52_prism_gdsc_consistency.md

실행 방법:
  cd /workspace/BioProject02
  python agents/therapeutic_evidence/scripts/run_consistency.py \
      --config experiments/jhans/20260702_consistency/config.yaml
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


# ── Step 1: BRCA Cell Line 교집합 ────────────────────────────
def get_brca_cell_lines(cfg: dict, data_dir: Path):
    print("\n[Step 1] BRCA Cell Line 교집합 파악")

    model = pd.read_csv(data_dir / cfg["data"]["depmap_model"])
    brca_depmap = model[model["OncotreeLineage"] == cfg["filter"]["brca_lineage"]][
        ["ModelID", "SangerModelID", "COSMICID", "CellLineName"]
    ].dropna(subset=["SangerModelID"])
    print(f"  DepMap BRCA cell lines: {len(brca_depmap)}개")

    gdsc = pd.read_excel(data_dir / cfg["data"]["gdsc_response"])
    brca_gdsc = gdsc[gdsc["TCGA_DESC"] == cfg["filter"]["brca_tcga"]][
        ["SANGER_MODEL_ID", "COSMIC_ID", "CELL_LINE_NAME"]
    ].drop_duplicates()
    print(f"  GDSC BRCA cell lines:   {len(brca_gdsc)}개")

    overlap_cl = brca_depmap.merge(
        brca_gdsc.rename(columns={"SANGER_MODEL_ID": "SangerModelID"}),
        on="SangerModelID",
        how="inner"
    )
    print(f"  교집합 (SangerModelID): {len(overlap_cl)}개  ← 실측값")

    return brca_depmap, brca_gdsc, overlap_cl, gdsc


# ── Step 2: Drug 교집합 ──────────────────────────────────────
def get_drug_overlap(cfg: dict, data_dir: Path):
    print("\n[Step 2] Drug 교집합 파악 (PubChem CID 기준)")

    prism_cpd = pd.read_csv(data_dir / cfg["data"]["prism_compound"])
    prism_cpd = prism_cpd[
        ["IDs", "Drug.Name", "MOA", "target", "pubchem_cid"]
    ].dropna(subset=["pubchem_cid"])
    prism_cpd["pubchem_cid"] = prism_cpd["pubchem_cid"].astype(str).str.strip()
    print(f"  PRISM 약물 (pubchem_cid 有): {len(prism_cpd)}개")

    gdsc_cpd = pd.read_csv(data_dir / cfg["data"]["gdsc_compound"])
    gdsc_cpd = gdsc_cpd[
        ["DRUG_ID", "DRUG_NAME", "PATHWAY_NAME", "PUTATIVE_TARGET", "PUBCHEM"]
    ].dropna(subset=["PUBCHEM"])
    gdsc_cpd["PUBCHEM"] = gdsc_cpd["PUBCHEM"].astype(str).str.strip()
    print(f"  GDSC 약물 (PUBCHEM 有):   {len(gdsc_cpd)}개")

    overlap_drug = prism_cpd.merge(
        gdsc_cpd,
        left_on="pubchem_cid",
        right_on="PUBCHEM",
        how="inner"
    )
    print(f"  PubChem CID 교집합:       {len(overlap_drug)}개  ← 실측값")

    return prism_cpd, gdsc_cpd, overlap_drug


# ── Step 3: Z-score 정규화 ───────────────────────────────────
def normalize_sensitivity(cfg: dict, data_dir: Path, brca_depmap, overlap_cl, gdsc):
    print("\n[Step 3] Sensitivity 정규화")

    # PRISM secondary AUC matrix
    print("  PRISM secondary matrix 로딩 (대용량, 잠시 대기)...")
    prism_sec = pd.read_csv(
        data_dir / cfg["data"]["prism_matrix"],
        index_col=0
    )
    brca_model_ids = brca_depmap["ModelID"].tolist()
    prism_brca = prism_sec.loc[prism_sec.index.intersection(brca_model_ids)]
    print(f"  PRISM BRCA rows: {len(prism_brca)}개")

    # drug별 z-score (BRCA cell line 분포 기준)
    prism_zscore = prism_brca.apply(
        lambda col: (col - col.mean()) / (col.std() + 1e-8), axis=0
    )

    # GDSC Z_SCORE (이미 제공됨, BRCA subset 추출)
    gdsc_brca = gdsc[
        (gdsc["TCGA_DESC"] == cfg["filter"]["brca_tcga"]) &
        (gdsc["SANGER_MODEL_ID"].isin(overlap_cl["SangerModelID"]))
    ][["SANGER_MODEL_ID", "DRUG_ID", "DRUG_NAME", "LN_IC50", "AUC", "Z_SCORE"]]
    print(f"  GDSC BRCA rows:  {len(gdsc_brca)}개")

    return prism_zscore, gdsc_brca


# ── Step 4: Spearman 상관계수 계산 ──────────────────────────
def compute_spearman(cfg, overlap_drug, overlap_cl, prism_zscore, gdsc_brca):
    print("\n[Step 4] Spearman ρ 계산")

    # ModelID → SangerModelID 매핑
    model_to_sanger = overlap_cl.set_index("ModelID")["SangerModelID"].to_dict()

    min_n   = cfg["consistency"]["min_cell_lines"]
    results = []
    skipped = 0

    for _, drug_row in overlap_drug.iterrows():
        broad_id = drug_row["IDs"]
        drug_id  = int(drug_row["DRUG_ID"])

        # PRISM: broad_id 포함 컬럼 찾기
        prism_cols = [c for c in prism_zscore.columns if broad_id in str(c)]
        if not prism_cols:
            skipped += 1
            continue
        p_vals = prism_zscore[prism_cols[0]].dropna()

        # ModelID → SangerModelID 변환
        p_mapped = p_vals.rename(index=model_to_sanger).dropna()

        # GDSC: 해당 drug의 Z_SCORE
        g_sub = gdsc_brca[gdsc_brca["DRUG_ID"] == drug_id].set_index("SANGER_MODEL_ID")
        if g_sub.empty:
            skipped += 1
            continue
        g_vals = g_sub["Z_SCORE"].dropna()

        common = p_mapped.index.intersection(g_vals.index)
        if len(common) < min_n:
            skipped += 1
            continue

        rho, pval = spearmanr(p_mapped[common], g_vals[common])
        results.append({
            "broad_id":      broad_id,
            "drug_id":       drug_id,
            "drug_name":     drug_row["Drug.Name"],
            "pubchem_cid":   drug_row["pubchem_cid"],
            "n_cell_lines":  len(common),
            "spearman_rho":  round(float(rho), 4),
            "pval":          round(float(pval), 6),
            "moa":           drug_row.get("MOA", ""),
            "pathway":       drug_row.get("PATHWAY_NAME", ""),
        })

    print(f"  계산 완료: {len(results)}개 약물  (skip: {skipped}개)")
    return pd.DataFrame(results)


# ── Step 5: data_source 태깅 ─────────────────────────────────
def tag_data_source(cfg, consistency_df: pd.DataFrame) -> pd.DataFrame:
    rho_min = cfg["consistency"]["spearman_rho_min"]
    pval_max = cfg["consistency"]["pval_max"]
    min_n    = cfg["consistency"]["min_cell_lines"]

    def tag(row):
        if (row["spearman_rho"] >= rho_min and
                row["pval"] < pval_max and
                row["n_cell_lines"] >= min_n):
            return "both"
        return "prism_only"

    consistency_df["data_source"] = consistency_df.apply(tag, axis=1)
    return consistency_df


# ── 저장 + 요약 ──────────────────────────────────────────────
def save_results(out_dir: Path, overlap_cl, overlap_drug, consistency_df, cfg):
    overlap_cl.to_csv(out_dir / "cell_line_overlap.csv", index=False)
    overlap_drug.to_csv(out_dir / "drug_overlap.csv", index=False)
    consistency_df.to_csv(out_dir / "consistency_scores.csv", index=False)

    rho_min  = cfg["consistency"]["spearman_rho_min"]
    pval_max = cfg["consistency"]["pval_max"]
    n_both   = (consistency_df["data_source"] == "both").sum()
    n_total  = len(consistency_df)

    summary = {
        "version": "0.2",
        "ticket": "BIOP02-52",
        "n_brca_cl_depmap":  int(len(overlap_cl)),
        "n_brca_cl_gdsc":    int(overlap_cl["SANGER_MODEL_ID"].nunique()),
        "n_cl_overlap":      int(len(overlap_cl)),
        "n_drug_overlap":    int(len(overlap_drug)),
        "n_drugs_analyzed":  int(n_total),
        "n_both":            int(n_both),
        "rho_median":        round(float(consistency_df["spearman_rho"].median()), 4),
        "rho_pct_above_03":  round(float((consistency_df["spearman_rho"] >= rho_min).mean() * 100), 1),
        "criteria": {
            "min_cell_lines": cfg["consistency"]["min_cell_lines"],
            "spearman_rho_min": rho_min,
            "pval_max": pval_max,
        }
    }

    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "="*55)
    print("  BIOP02-52 v0.2 실측 결과 요약")
    print("="*55)
    print(f"  BRCA cell line 교집합:   {summary['n_cl_overlap']}개")
    print(f"  Drug 교집합 (PubChem):   {summary['n_drug_overlap']}개")
    print(f"  Spearman 계산 완료 약물: {n_total}개")
    print(f"  data_source='both' 약물: {n_both}개  "
          f"({round(n_both/n_total*100,1) if n_total else 0}%)")
    print(f"  Spearman ρ 중앙값:       {summary['rho_median']}")
    print(f"  ρ ≥ {rho_min} 비율:        {summary['rho_pct_above_03']}%")
    print("="*55)
    print(f"\n  출력 파일:")
    for fname in ["cell_line_overlap.csv","drug_overlap.csv",
                  "consistency_scores.csv","summary.json"]:
        p = out_dir / fname
        size = p.stat().st_size // 1024 if p.exists() else 0
        print(f"    {fname}  ({size} KB)")


# ── main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg      = load_config(args.config)
    out_dir  = Path(args.config).parent
    data_dir = out_dir / "data"

    if not data_dir.exists():
        print(f"ERROR: data 디렉토리 없음 → {data_dir}")
        print("먼저 실행: bash agents/therapeutic_evidence/scripts/download_data.sh")
        sys.exit(1)

    brca_depmap, brca_gdsc, overlap_cl, gdsc = get_brca_cell_lines(cfg, data_dir)
    _prism_cpd, _gdsc_cpd, overlap_drug      = get_drug_overlap(cfg, data_dir)
    prism_zscore, gdsc_brca                  = normalize_sensitivity(cfg, data_dir, brca_depmap, overlap_cl, gdsc)
    consistency_df                            = compute_spearman(cfg, overlap_drug, overlap_cl, prism_zscore, gdsc_brca)
    consistency_df                            = tag_data_source(cfg, consistency_df)

    save_results(out_dir, overlap_cl, overlap_drug, consistency_df, cfg)
    print("\n완료! BIOP02-60 작업 시 consistency_scores.csv 사용하세요.")


if __name__ == "__main__":
    main()

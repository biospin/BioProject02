"""BIOP02-96 Critic #4/#5 sub-check (jhans, non-owner).

#5 Biological plausibility:
   frozen_map.json의 positive_control을 검증하고 표준 종양학 pathway-drug 일관성 확인.

#4 Cross-dataset (PRISM vs GDSC):
   PRISM Repurposing Secondary AUC와 GDSC2 AUC의 Spearman ρ를 암종별로 계산.
   PRISM 데이터가 없으면 #4를 skip하고 다운로드 지시 출력.

Usage:
    # #5만 (PRISM 없이):
    python agents/therapeutic_evidence/scripts/crosscancer_subcheck.py \\
        --frozen_maps experiments/crosscancer/COLORECTAL/frozen_map.json \\
                      experiments/crosscancer/LUNG_NSCLC/frozen_map.json \\
        --gdsc /workspace/data/BIOP02-52/GDSC2_fitted_dose_response_27Oct23.xlsx \\
        --model_csv Model.csv \\
        --out_dir /workspace/experiments/jhans/crosscancer_subcheck_v1

    # #4 포함 (PRISM 있을 때):
    python ... \\
        --prism_bowel  /workspace/data/BIOP02-96/PRISM_Repurposing_Secondary_Bowel.csv \\
        --prism_lung   /workspace/data/BIOP02-96/PRISM_Repurposing_Secondary_Lung.csv
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from scipy import stats

# ── 표준 종양학 기반 pathway→drug 방향성 사전 ─────────────────────────────
PATHWAY_DRUG_PRIOR = {
    # 대장암
    "COLORECTAL_antiBRAF": {
        "expected_sensitive_drugs": ["Dabrafenib", "Trametinib", "Selumetinib", "PLX-4720"],
        "rationale": "BRAF-V600E CRC: BRAF+MEK 병용이 표준(BEACON-CRC). Dabrafenib/Encorafenib(BRAF), Trametinib/Selumetinib(MEK) 세포주 감수성 문헌 확립.",
        "ref": "Kopetz et al. NEJM 2019 (BEACON-CRC)",
    },
    # 폐암
    "LUNG_NSCLC_antiEGFR": {
        "expected_sensitive_drugs": ["Gefitinib", "Afatinib", "Osimertinib", "Erlotinib", "AZD3759"],
        "rationale": "EGFR-activating(L858R/exon19del) NSCLC: EGFR TKI 감수성 세포주 데이터가 가장 견고한 positive control 중 하나.",
        "ref": "Mok et al. NEJM 2009; Soria et al. NEJM 2018 (FLAURA)",
    },
    "LUNG_NSCLC_antiKRAS_G12C": {
        "expected_sensitive_drugs": ["Sotorasib", "Adagrasib"],
        "gdsc_note": "Sotorasib/Adagrasib GDSC2 27Oct23 미수록 — MEK proxy(Selumetinib)로 간접 검증. G12C 직접 약물 PRISM 확인 필요.",
        "rationale": "KRAS-G12C: Sotorasib(CodeBreaK100) 승인. GDSC2 미수록이라 직접 양성대조 불가; MEK 하류 대리약물로 간접 확인.",
        "ref": "Skoulidis et al. NEJM 2021 (CodeBreaK100)",
    },
}


def check_positive_controls(frozen_map: dict) -> dict:
    """frozen_map positive_control의 most_sensitive 방향성을 검증."""
    cancer = frozen_map.get("cancer", "UNKNOWN")
    pc = frozen_map.get("positive_control", {})
    results = {}
    n_ok = n_fail = 0
    for drug, info in pc.items():
        ok = info.get("ok", False)
        results[drug] = {
            "most_sensitive": info.get("most_sensitive"),
            "ok": ok,
            "z_scores": info.get("z", {}),
        }
        if ok:
            n_ok += 1
        else:
            n_fail += 1
    return {
        "cancer": cancer,
        "n_positive_controls": len(pc),
        "n_pass": n_ok,
        "n_fail": n_fail,
        "all_pass": n_fail == 0,
        "details": results,
    }


def check_biological_priors(frozen_map: dict) -> dict:
    """pathway→drug 사전 지식과 frozen_map top_discriminating 방향성 일치 확인."""
    cancer = frozen_map.get("cancer", "UNKNOWN")
    top_drugs = {d["drug"]: d for d in frozen_map.get("top_discriminating", [])}
    issues = []
    checks = []

    for key, prior in PATHWAY_DRUG_PRIOR.items():
        if not key.startswith(cancer):
            continue
        expected = prior["expected_sensitive_drugs"]
        axis = key.replace(f"{cancer}_", "")
        found_in_top = [d for d in expected if d in top_drugs]
        for drug in found_in_top:
            entry = top_drugs[drug]
            correct_axis = entry.get("most_sensitive", "").lower().replace("-", "").replace("_", "")
            expected_axis = axis.lower().replace("-", "").replace("_", "")
            direction_ok = expected_axis in correct_axis or correct_axis in expected_axis
            checks.append({
                "drug": drug,
                "axis": axis,
                "most_sensitive_in_map": entry.get("most_sensitive"),
                "direction_ok": direction_ok,
                "rationale": prior["rationale"],
            })
            if not direction_ok:
                issues.append(f"{drug}: axis={axis}, map shows {entry.get('most_sensitive')}")
        if not found_in_top:
            note = prior.get("gdsc_note", f"{expected} not in top_discriminating (may be absent from GDSC2)")
            checks.append({
                "drug": f"[{expected[0]} et al.]",
                "axis": axis,
                "most_sensitive_in_map": "N/A",
                "direction_ok": None,
                "note": note,
                "rationale": prior["rationale"],
            })

    return {
        "cancer": cancer,
        "issues": issues,
        "checks": checks,
        "status": "fail" if issues else "pass",
    }


def run_prism_gdsc_consistency(
    frozen_map: dict,
    prism_csv: Path,
    gdsc_xlsx: Path,
    model_csv: Path,
    log: logging.Logger,
) -> Optional[dict]:
    """#4: PRISM vs GDSC Spearman ρ for key drugs in this cancer type."""
    cancer = frozen_map.get("cancer", "UNKNOWN")

    # OncotreeLineage 매핑
    lineage_map = {
        "COLORECTAL": "Bowel",
        "LUNG_NSCLC": "Lung",
        "GASTRIC_STAD": "Stomach",
        "HEADNECK_HNSC": "Head and Neck",
    }
    lineage = lineage_map.get(cancer)
    if lineage is None:
        log.warning(f"#4 skip: {cancer} lineage 매핑 없음")
        return None

    # Model.csv 로드 → cancer lineage cell lines
    try:
        model_df = pd.read_csv(model_csv)
    except Exception as e:
        log.error(f"Model.csv 로드 실패: {e}")
        return None

    cl_ids = model_df[model_df["OncotreeLineage"] == lineage]["ModelID"].tolist()
    sanger_ids = model_df[model_df["OncotreeLineage"] == lineage]["SangerModelID"].dropna().tolist()
    log.info(f"#4 {cancer}: {lineage} cell lines — DepMap {len(cl_ids)}개, Sanger {len(sanger_ids)}개")

    # PRISM 로드
    try:
        prism_df = pd.read_csv(prism_csv, index_col=0)
        prism_df.index = prism_df.index.str.strip()
        prism_cls = [c for c in cl_ids if c in prism_df.index]
        prism_sub = prism_df.loc[prism_cls]
        log.info(f"#4 {cancer}: PRISM 교집합 {len(prism_cls)}개 cell line")
    except Exception as e:
        log.error(f"#4 PRISM 로드 실패: {e}")
        return None

    # GDSC 로드
    try:
        gdsc_df = pd.read_excel(gdsc_xlsx)
        gdsc_df.columns = gdsc_df.columns.str.strip()
        drug_col = "DRUG_NAME" if "DRUG_NAME" in gdsc_df.columns else "Drug Name"
        auc_col = "AUC" if "AUC" in gdsc_df.columns else "AUC"
        model_col = "SANGER_MODEL_ID" if "SANGER_MODEL_ID" in gdsc_df.columns else "Sanger Model ID"
        gdsc_sub = gdsc_df[gdsc_df[model_col].isin(sanger_ids)]
        gdsc_wide = gdsc_sub.pivot_table(index=model_col, columns=drug_col, values=auc_col, aggfunc="mean")
        # SangerModelID → ModelID 매핑
        sid_to_mid = dict(zip(model_df["SangerModelID"].dropna(), model_df["ModelID"]))
        gdsc_wide.index = [sid_to_mid.get(s, s) for s in gdsc_wide.index]
        log.info(f"#4 {cancer}: GDSC 교집합 {len(gdsc_wide)}개 cell line")
    except Exception as e:
        log.error(f"#4 GDSC 로드 실패: {e}")
        return None

    # key drugs = top_discriminating + positive_control
    key_drugs_raw = (
        [d["drug"] for d in frozen_map.get("top_discriminating", [])]
        + list(frozen_map.get("positive_control", {}).keys())
    )
    key_drugs = list(dict.fromkeys(key_drugs_raw))

    rho_results = []
    common_cls = list(set(prism_sub.index) & set(gdsc_wide.index))
    log.info(f"#4 {cancer}: 최종 교집합 cell line {len(common_cls)}개")

    for drug in key_drugs:
        prism_drug = drug.upper()
        prism_drug_alt = drug
        gdsc_drug = drug

        prism_vec = None
        for d in (prism_drug, prism_drug_alt):
            if d in prism_sub.columns:
                prism_vec = prism_sub.loc[common_cls, d].dropna()
                break

        gdsc_vec = gdsc_wide.loc[common_cls, gdsc_drug].dropna() if gdsc_drug in gdsc_wide.columns else None

        if prism_vec is None or gdsc_vec is None or len(prism_vec) < 5:
            rho_results.append({
                "drug": drug,
                "status": "skip",
                "reason": "PRISM 미수록" if prism_vec is None else ("GDSC 미수록" if gdsc_vec is None else "n<5"),
            })
            continue

        common = list(set(prism_vec.index) & set(gdsc_vec.index))
        if len(common) < 5:
            rho_results.append({"drug": drug, "status": "skip", "reason": f"공통 CL {len(common)}<5"})
            continue

        r, p = stats.spearmanr(prism_vec.loc[common], gdsc_vec.loc[common])
        rho_results.append({
            "drug": drug,
            "spearman_rho": round(float(r), 4),
            "p_value": round(float(p), 4),
            "n": len(common),
            "status": "both" if (r >= 0.3 and p < 0.05) else ("rho_low" if r < 0.3 else "p_ns"),
        })
        log.info(f"  {drug}: ρ={r:.3f} p={p:.3f} n={len(common)}")

    valid = [x for x in rho_results if x.get("spearman_rho") is not None]
    median_rho = pd.Series([x["spearman_rho"] for x in valid]).median() if valid else None
    n_both = sum(1 for x in valid if x.get("status") == "both")

    return {
        "cancer": cancer,
        "n_drugs_checked": len(valid),
        "median_spearman_rho": round(float(median_rho), 4) if median_rho is not None else None,
        "n_both_consistent": n_both,
        "pct_consistent": round(n_both / len(valid) * 100, 1) if valid else None,
        "per_drug": rho_results,
        "status": "pass" if (median_rho is not None and median_rho >= 0.3) else "fail",
    }


def main():
    parser = argparse.ArgumentParser(description="BIOP02-96 Critic #4/#5 sub-check")
    parser.add_argument("--frozen_maps", nargs="+", required=True)
    parser.add_argument("--model_csv", default="Model.csv")
    parser.add_argument("--gdsc", default=None, help="GDSC2 xlsx (서버 경로)")
    parser.add_argument("--prism_bowel", default=None)
    parser.add_argument("--prism_lung", default=None)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = out_dir / f"crosscancer_subcheck_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    log = logging.getLogger(__name__)

    prism_map = {
        "COLORECTAL": args.prism_bowel,
        "LUNG_NSCLC": args.prism_lung,
    }

    report = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "reviewer": "jhans (non-owner, Critic 7-point #4/#5 sub-check)",
        "owner": "kkkim",
        "claim_level": "hypothesis_only",
        "check_5_biological_plausibility": [],
        "check_4_cross_dataset": [],
        "summary": {},
    }

    for fm_path in args.frozen_maps:
        with open(fm_path, encoding="utf-8") as f:
            fm = json.load(f)
        cancer = fm.get("cancer", "?")
        log.info(f"\n=== {cancer} ===")

        # #5 biological plausibility
        pc_result = check_positive_controls(fm)
        prior_result = check_biological_priors(fm)
        bio_status = "pass" if (pc_result["all_pass"] and prior_result["status"] == "pass") else "caution"
        report["check_5_biological_plausibility"].append({
            "cancer": cancer,
            "status": bio_status,
            "positive_controls": pc_result,
            "prior_consistency": prior_result,
        })
        log.info(f"#5 {cancer}: positive_control={pc_result['n_pass']}/{pc_result['n_positive_controls']} pass | prior={prior_result['status']} | overall={bio_status}")

        # #4 cross-dataset
        prism_path = prism_map.get(cancer)
        if prism_path and args.gdsc and Path(prism_path).exists() and Path(args.gdsc).exists():
            log.info(f"#4 {cancer}: PRISM={prism_path}")
            consistency = run_prism_gdsc_consistency(fm, Path(prism_path), Path(args.gdsc), Path(args.model_csv), log)
            report["check_4_cross_dataset"].append(consistency or {"cancer": cancer, "status": "error"})
        else:
            missing = []
            if not prism_path:
                missing.append(f"PRISM_{cancer}.csv (DepMap Custom Downloads > {cancer.split('_')[0]} context)")
            elif not Path(prism_path).exists():
                missing.append(f"{prism_path} 미존재")
            if not args.gdsc:
                missing.append("GDSC2 xlsx")
            log.warning(f"#4 {cancer}: skip — 미수 데이터: {', '.join(missing)}")
            report["check_4_cross_dataset"].append({
                "cancer": cancer,
                "status": "pending_data",
                "missing": missing,
                "download_note": "DepMap Custom Downloads -> Repurposing Secondary AUC -> Cancer Type 필터 적용 후 CSV 저장",
            })

    # 요약
    bio_all = all(x["status"] == "pass" for x in report["check_5_biological_plausibility"])
    cross_done = [x for x in report["check_4_cross_dataset"] if x.get("status") not in ("pending_data", "error")]
    cross_pass = all(x.get("status") == "pass" for x in cross_done) if cross_done else None

    report["summary"] = {
        "check_5_overall": "pass" if bio_all else "caution",
        "check_4_overall": "pass" if cross_pass else ("pending_data" if not cross_done else "fail"),
        "critic_upgrade_possible": bio_all and (cross_pass is True),
        "note": "jhans sub-check (BIOP02-96, non-owner). #5 완료. #4는 PRISM Bowel/Lung 데이터 확보 후 서버에서 재실행 필요." if not cross_done else "jhans sub-check 완료.",
    }

    out_path = out_dir / f"crosscancer_subcheck_{ts}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"\n결과: {out_path}")
    log.info(f"#5 biological plausibility: {report['summary']['check_5_overall']}")
    log.info(f"#4 cross-dataset: {report['summary']['check_4_overall']}")
    log.info(f"Critic pass 상신 가능: {report['summary']['critic_upgrade_possible']}")


if __name__ == "__main__":
    main()

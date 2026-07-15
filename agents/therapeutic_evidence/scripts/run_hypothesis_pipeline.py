"""BIOP02-89 — Therapeutic hypothesis batch pipeline.

sjpark 표현형 예측 CSV → endocrine_rule() → hypothesis.schema.json 형식 배치 출력.

입력 CSV 필수 컬럼:
    slide_id   : str   (예: TCGA-3C-AALI-01Z-00-DX1)
    patient_id : str   (예: TCGA-3C-AALI)  ← 없으면 slide_id 앞 16자
    er_pred    : str   "Positive" | "Negative"   (또는 er_status)
    pr_pred    : str   "Positive" | "Negative"   (또는 pr_status)
    her2_pred  : str   "Positive" | "Negative"   (또는 her2_status)

선택 컬럼:
    pam50_pred : str   LumA | LumB | HER2E | Basal | Normal  (또는 pam50)
    cohort     : str   (기본: TCGA-BRCA)
    er_prob / pr_prob / her2_prob : float  확률값(0~1) — pred 컬럼 없을 때 thr=0.5 적용

출력:
    <out_dir>/per_patient/<patient_id>_hypothesis.json  — 환자별 hypothesis.schema
    <out_dir>/hypothesis_summary.csv                    — 배치 요약
    <out_dir>/pipeline_<timestamp>.log

Usage:
    python agents/therapeutic_evidence/scripts/run_hypothesis_pipeline.py \\
        --predictions /workspace/experiments/sjpark/er_status_clam_uni_v2/predictions.csv \\
        --out_dir /workspace/experiments/jhans/hypothesis_pipeline_v1 \\
        [--consistency_csv /workspace/experiments/jhans/20260702_consistency/consistency_scores.csv] \\
        [--prob_threshold 0.5]
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[2]))
from therapeutic_evidence.rules import endocrine_rule, check_forbidden_phrases

SCHEMA_VERSION = "0.2"
PHENOTYPE_MODEL_TAG = "SlideMLP/CLAM-SB (BIOP02-39/46/53, uni_v2)"

_PROB_THRESHOLD = 0.5


def _get_git_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _resolve_label(row: pd.Series, base: str, threshold: float) -> str:
    """컬럼명 유연 처리: {base}_pred → {base}_status → {base}_prob."""
    for col in (f"{base}_pred", f"{base}_status", base):
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).strip()
            if val.lower() in ("positive", "negative"):
                return val.capitalize()
    prob_col = f"{base}_prob"
    if prob_col in row.index and pd.notna(row[prob_col]):
        return "Positive" if float(row[prob_col]) >= threshold else "Negative"
    return "Negative"


def _resolve_pam50(row: pd.Series) -> str | None:
    for col in ("pam50_pred", "pam50"):
        if col in row.index and pd.notna(row[col]):
            return str(row[col]).strip()
    return None


def _plausibility_check(er: str, pr: str, her2: str, hypotheses: list[dict]) -> list[str]:
    issues = []
    drug_classes = " ".join(h["drug_class"].lower() for h in hypotheses)
    if her2.lower() == "positive" and "anti-her2" not in drug_classes:
        issues.append("HER2 양성인데 anti-HER2 계열 없음")
    if her2.lower() == "negative" and "anti-her2" in drug_classes:
        issues.append("HER2 음성인데 anti-HER2 추천됨")
    if (er.lower() == "positive" or pr.lower() == "positive") and "endocrine" not in drug_classes:
        issues.append("ER/PR 양성인데 endocrine therapy 없음")
    if all(x.lower() == "negative" for x in (er, pr, her2)) and "chemotherapy" not in drug_classes:
        issues.append("Triple-negative인데 chemotherapy 없음")
    return issues


def process_patient(
    row: pd.Series,
    commit_hash: str,
    consistency_csv: Path | None,
    threshold: float,
    out_dir: Path,
) -> dict:
    slide_id = str(row.get("slide_id", "unknown"))
    patient_id = str(row.get("patient_id", slide_id.split("-01Z")[0]))
    cohort = str(row.get("cohort", "TCGA-BRCA"))

    er = _resolve_label(row, "er", threshold)
    pr = _resolve_label(row, "pr", threshold)
    her2 = _resolve_label(row, "her2", threshold)
    pam50 = _resolve_pam50(row)

    hypotheses = endocrine_rule(er, pr, her2, pam50=pam50, consistency_csv=consistency_csv)

    all_text = json.dumps(hypotheses, ensure_ascii=False)
    forbidden = check_forbidden_phrases(all_text)
    direction_issues = _plausibility_check(er, pr, her2, hypotheses)

    record = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "commit_hash": commit_hash,
        "slide": {"slide_id": slide_id, "patient_id": patient_id, "cohort": cohort},
        "phenotype": {
            "model": PHENOTYPE_MODEL_TAG,
            "predictions": {
                "er_status": er,
                "pr_status": pr,
                "her2_status": her2,
                "pam50": pam50,
            },
        },
        "hypothesis": hypotheses,
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "critic_5_biological_plausibility": {
            "status": "caution" if (forbidden or direction_issues) else "pass",
            "forbidden_phrase_violations": forbidden,
            "direction_consistency_issues": direction_issues,
            "note": "BIOP02-89 v1.0 (endocrine_rule v1.0, BIOP02-52 consistency_scores 기반)",
        },
    }

    out_path = out_dir / "per_patient" / f"{patient_id}_hypothesis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    top = hypotheses[0] if hypotheses else {}
    return {
        "patient_id": patient_id,
        "slide_id": slide_id,
        "er": er,
        "pr": pr,
        "her2": her2,
        "pam50": pam50 or "",
        "n_hypotheses": len(hypotheses),
        "top_drug_class": top.get("drug_class", ""),
        "top_confidence": top.get("confidence", ""),
        "top_data_source": top.get("data_source", ""),
        "plausibility_status": record["critic_5_biological_plausibility"]["status"],
        "direction_issues": "; ".join(direction_issues) if direction_issues else "",
        "forbidden_violations": "; ".join(forbidden) if forbidden else "",
    }


def main():
    parser = argparse.ArgumentParser(description="BIOP02-89 hypothesis pipeline")
    parser.add_argument("--predictions", required=True, help="sjpark 예측 CSV 경로")
    parser.add_argument("--out_dir", required=True, help="출력 디렉토리")
    parser.add_argument(
        "--consistency_csv",
        default=None,
        help="BIOP02-52 consistency_scores.csv (기본: 서버 경로)",
    )
    parser.add_argument(
        "--prob_threshold",
        type=float,
        default=_PROB_THRESHOLD,
        help="확률→이진 변환 임계값 (기본 0.5)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    consistency_csv = Path(args.consistency_csv) if args.consistency_csv else None

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = out_dir / f"pipeline_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    log = logging.getLogger(__name__)

    commit_hash = _get_git_hash()
    log.info(f"BIOP02-89 hypothesis pipeline | commit={commit_hash}")
    log.info(f"predictions={args.predictions}")
    log.info(f"out_dir={out_dir}")
    log.info(f"consistency_csv={consistency_csv or '(서버 기본 경로)'}")
    log.info(f"prob_threshold={args.prob_threshold}")

    df = pd.read_csv(args.predictions)
    log.info(f"입력 환자 수: {len(df)}")

    rows = []
    n_pass = n_caution = n_err = 0
    for _, row in df.iterrows():
        try:
            summary = process_patient(row, commit_hash, consistency_csv, args.prob_threshold, out_dir)
            rows.append(summary)
            if summary["plausibility_status"] == "pass":
                n_pass += 1
            else:
                n_caution += 1
                log.warning(f"[caution] {summary['patient_id']}: {summary['direction_issues']}")
        except Exception as e:
            log.error(f"[error] {row.get('patient_id', row.get('slide_id', '?'))}: {e}")
            n_err += 1

    summary_path = out_dir / "hypothesis_summary.csv"
    pd.DataFrame(rows).to_csv(summary_path, index=False)

    log.info("=" * 60)
    log.info(f"완료: {len(rows)}명 처리 | pass={n_pass} caution={n_caution} error={n_err}")
    log.info(f"요약 CSV: {summary_path}")
    log.info(f"로그: {log_path}")
    log.info("claim_level=hypothesis_only 고정 (DRP 프레이밍 아님)")


if __name__ == "__main__":
    main()

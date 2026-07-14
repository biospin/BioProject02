"""BIOP02-60 — Endocrine rule v1.0 (DepMap/GDSC transfer 초안)

endocrine_rule_draft.py(sjpark 임시 작성)의 정식 대체 구현.
BIOP02-52에서 생성한 consistency_scores.csv의 실측 Spearman ρ를 기반으로
drug_class별 confidence를 산출하고 hypothesis.schema.json 형식으로 반환.

CLAUDE.md 절대 금지 준수:
  - "patient-specific optimal treatment prediction" / "personalized therapy" 표현 금지
  - ICI / Pembrolizumab 추천 금지
  - claim_level: hypothesis_only 고정
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import pandas as pd

# ── 기본 consistency_scores.csv 경로 (서버 기준) ─────────────
_DEFAULT_CONSISTENCY_CSV = Path(
    "/workspace/experiments/jhans/20260702_consistency/consistency_scores.csv"
)

# ── Drug class → 후보 약물 (UPPERCASE, GDSC/PRISM drug_name 기준) ─
DRUG_CLASS_MAP: dict[str, list[str]] = {
    "Endocrine therapy (SERM/aromatase inhibitor)": [
        "TAMOXIFEN", "LETROZOLE", "ANASTROZOLE", "EXEMESTANE", "FULVESTRANT",
    ],
    "CDK4/6 inhibitor": [
        "PALBOCICLIB", "RIBOCICLIB", "ABEMACICLIB",
    ],
    "Anti-HER2 therapy (TKI)": [
        "LAPATINIB", "AFATINIB", "NERATINIB",
    ],
    "Cytotoxic chemotherapy (backbone)": [
        "PACLITAXEL", "DOCETAXEL", "DOXORUBICIN", "GEMCITABINE",
        "VINORELBINE", "ERIBULIN",
    ],
}

FORBIDDEN_PHRASES = [
    "patient-specific optimal treatment",
    "personalized therapy",
    "drug response prediction",
    "pembrolizumab",
    "ici therapy",
]


def check_forbidden_phrases(text: str) -> list[str]:
    """텍스트에 금지 표현이 있는지 검사. 위반 목록 반환 (없으면 빈 리스트)."""
    text_lower = text.lower()
    return [p for p in FORBIDDEN_PHRASES if p in text_lower]


def _load_consistency(csv_path: Path) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(csv_path)
        df["drug_name"] = df["drug_name"].str.upper()
        return df
    except FileNotFoundError:
        return None


def _class_evidence(
    drug_names: list[str],
    df: pd.DataFrame,
) -> dict:
    """약물 목록에 대해 consistency_scores에서 집계 evidence를 반환."""
    matched = df[df["drug_name"].isin(drug_names)]
    if matched.empty:
        return {
            "n_found": 0, "n_both": 0,
            "mean_rho": None, "data_source_tag": "DepMap-PRISM",
            "drug_details": [],
        }

    n_both = int((matched["data_source"] == "both").sum())
    # "both" 약물이 있으면 우선 반영, 없으면 전체 평균
    if n_both > 0:
        mean_rho = float(matched[matched["data_source"] == "both"]["spearman_rho"].mean())
        src_tag = "both"
    else:
        mean_rho = float(matched["spearman_rho"].mean())
        src_tag = "DepMap-PRISM"

    drug_details = (
        matched[["drug_name", "spearman_rho", "n_cell_lines", "data_source"]]
        .sort_values("spearman_rho", ascending=False)
        .to_dict(orient="records")
    )

    return {
        "n_found": len(matched),
        "n_both": n_both,
        "mean_rho": round(mean_rho, 4),
        "data_source_tag": src_tag,
        "drug_details": drug_details,
    }


def _confidence_from_rho(mean_rho: Optional[float], n_both: int) -> float:
    """Spearman ρ → confidence 변환. 데이터 없으면 fallback 0.3."""
    if mean_rho is None:
        return 0.3
    base = max(0.0, min(1.0, mean_rho))
    # "both" 약물 수에 따라 소폭 보정
    bonus = min(0.05 * n_both, 0.1)
    return round(min(0.95, base + bonus), 4)


def endocrine_rule(
    er: str,
    pr: str,
    her2: str,
    pam50: str = None,
    consistency_csv: Optional[Path | str] = None,
) -> list[dict]:
    """
    분자 아형 → 치료 클래스 가설 생성 (hypothesis_only).

    Args:
        er, pr, her2 : "Positive" | "Negative"
        pam50        : "LumA" | "LumB" | "Basal" | "HER2E" | "Normal" (optional)
        consistency_csv : BIOP02-52 consistency_scores.csv 경로.
                          None이면 기본 서버 경로 사용.

    Returns:
        hypothesis.schema.json의 "hypothesis" 배열 형식
    """
    csv_path = Path(consistency_csv) if consistency_csv else _DEFAULT_CONSISTENCY_CSV
    df = _load_consistency(csv_path)
    data_available = df is not None

    er_pos  = er.strip().lower()  == "positive"
    pr_pos  = pr.strip().lower()  == "positive"
    her2_pos = her2.strip().lower() == "positive"

    hypotheses: list[dict] = []
    rank = 1

    # ── HER2+ → Anti-HER2 TKI ────────────────────────────────
    if her2_pos:
        ev = _class_evidence(DRUG_CLASS_MAP["Anti-HER2 therapy (TKI)"], df) if data_available else {}
        conf = _confidence_from_rho(ev.get("mean_rho"), ev.get("n_both", 0)) if data_available else 0.5
        n_found = ev.get("n_found", 0)
        rho_str = f"Spearman ρ={ev['mean_rho']:.3f} ({ev['n_found']}개 약물 매칭, {ev['n_both']}개 both)" if data_available and n_found else "consistency 데이터 미매칭"
        hypotheses.append({
            "rank": rank,
            "drug_class": "Anti-HER2 therapy (TKI: lapatinib/afatinib class)",
            "rationale": (
                f"HER2 양성 표현형은 표준 종양학 가이드라인상 항HER2 표적 치료 대상군으로 알려져 있음. "
                f"BRCA 세포주 DepMap/GDSC 일관성 분석 결과: {rho_str}. "
                f"(hypothesis_only — 개별 환자 처방 근거 아님, BIOP02-60 v1.0)"
            ),
            "confidence": conf,
            "data_source": ev.get("data_source_tag", "DepMap-PRISM") if data_available else "DepMap-PRISM",
            "supporting_endpoints": ["her2_status"],
        })
        rank += 1

    # ── ER+/PR+ → Endocrine therapy ──────────────────────────
    if er_pos or pr_pos:
        ev_et  = _class_evidence(DRUG_CLASS_MAP["Endocrine therapy (SERM/aromatase inhibitor)"], df) if data_available else {}
        ev_cdk = _class_evidence(DRUG_CLASS_MAP["CDK4/6 inhibitor"], df) if data_available else {}

        # ET + CDK4/6i 합산 confidence (평균)
        rhos = [x for x in [ev_et.get("mean_rho"), ev_cdk.get("mean_rho")] if x is not None]
        n_both_total = ev_et.get("n_both", 0) + ev_cdk.get("n_both", 0)
        combined_rho = (sum(rhos) / len(rhos)) if rhos else None
        conf = _confidence_from_rho(combined_rho, n_both_total) if data_available else 0.5

        et_str  = f"ET: ρ={ev_et.get('mean_rho', 'N/A')} ({ev_et.get('n_found',0)}개)"  if data_available else "미매칭"
        cdk_str = f"CDK4/6i: ρ={ev_cdk.get('mean_rho', 'N/A')} ({ev_cdk.get('n_found',0)}개)" if data_available else "미매칭"

        src = "both" if (ev_et.get("data_source_tag") == "both" or ev_cdk.get("data_source_tag") == "both") else "DepMap-PRISM"

        active_markers = []
        if er_pos:  active_markers.append("ER+")
        if pr_pos:  active_markers.append("PR+")

        hypotheses.append({
            "rank": rank,
            "drug_class": "Endocrine therapy (SERM/aromatase inhibitor) ± CDK4/6 inhibitor",
            "rationale": (
                f"{'·'.join(active_markers)} 표현형은 호르몬 수용체 경로 의존성과 연관된 아형으로 내분비 치료 계열이 표준적으로 고려됨. "
                f"BRCA 세포주 일관성 분석(BIOP02-52): {et_str}, {cdk_str}. "
                f"(hypothesis_only — BIOP02-60 v1.0)"
            ),
            "confidence": conf,
            "data_source": src if data_available else "DepMap-PRISM",
            "supporting_endpoints": [s for s, pos in [("er_status", er_pos), ("pr_status", pr_pos)] if pos],
        })
        rank += 1

    # ── TNBC → Cytotoxic chemotherapy ────────────────────────
    if not er_pos and not pr_pos and not her2_pos:
        ev = _class_evidence(DRUG_CLASS_MAP["Cytotoxic chemotherapy (backbone)"], df) if data_available else {}
        conf = _confidence_from_rho(ev.get("mean_rho"), ev.get("n_both", 0)) if data_available else 0.3
        chemo_str = f"ρ={ev.get('mean_rho', 'N/A')} ({ev.get('n_found',0)}개 매칭)" if data_available else "미매칭"
        hypotheses.append({
            "rank": rank,
            "drug_class": "Cytotoxic chemotherapy (taxane/anthracycline backbone)",
            "rationale": (
                f"Triple-negative 표현형(ER-/PR-/HER2-)은 표적 호르몬/HER2 경로가 없어 세포독성 화학요법이 표준 backbone으로 고려됨. "
                f"BRCA 세포주 일관성 분석: {chemo_str}. "
                f"ICI 계열은 본 프로젝트 범위에서 명시적으로 제외. (hypothesis_only — BIOP02-60 v1.0)"
            ),
            "confidence": conf,
            "data_source": ev.get("data_source_tag", "DepMap-PRISM") if data_available else "DepMap-PRISM",
            "supporting_endpoints": ["er_status", "pr_status", "her2_status"],
        })
        rank += 1

    return hypotheses


if __name__ == "__main__":
    import json

    print("=== ER+/PR+/HER2- (LumA) ===")
    h = endocrine_rule("Positive", "Positive", "Negative", pam50="LumA")
    print(json.dumps(h, indent=2, ensure_ascii=False))
    print("금지 표현:", check_forbidden_phrases(json.dumps(h)) or "없음")

    print("\n=== HER2+ ===")
    h2 = endocrine_rule("Negative", "Negative", "Positive")
    print(json.dumps(h2, indent=2, ensure_ascii=False))

    print("\n=== TNBC ===")
    h3 = endocrine_rule("Negative", "Negative", "Negative")
    print(json.dumps(h3, indent=2, ensure_ascii=False))

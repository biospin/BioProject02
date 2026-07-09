"""
[DRAFT — sjpark 임시 작성, jhans(Therapeutic Evidence Agent) 검토 필요]

BIOP02-59(Biological plausibility check)를 언블록하기 위한 임시 규칙 기반
phenotype → drug_class 매핑. BIOP02-60(Endocrine rule sample, jhans owner)의
정식 구현을 대체하지 않음. DepMap/GDSC 실제 데이터 연결 전, 표준 종양학
가이드라인(교과서 수준 지식)에 기반한 최소 골격.

⚠️ 다음 항목은 jhans/braveji 검토 후 확정 필요:
  - drug_class 목록의 정확성/최신성
  - DepMap PRISM/GDSC 데이터 연결 (현재는 rationale만, confidence는 placeholder)
  - data_source 필드는 아직 실제 DepMap/GDSC 조회 결과가 아님

CLAUDE.md 절대 금지 준수:
  - "patient-specific optimal treatment prediction" / "personalized therapy" 표현 금지
  - ICI / Pembrolizumab 추천 금지
  - claim_level: hypothesis_only 고정
"""

from __future__ import annotations

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


def endocrine_rule(er: str, pr: str, her2: str, pam50: str = None) -> list[dict]:
    """
    표준 유방암 분자 아형 → 치료 클래스 매핑 (교과서 수준, hypothesis_only).
    실제 세포주 기반 DepMap/GDSC 검증은 jhans BIOP02-60에서 별도 수행 예정.

    Args:
        er, pr, her2: "Positive" | "Negative"
        pam50: "LumA" | "LumB" | "Basal" | "HER2" | "Normal" (optional)

    Returns:
        hypothesis.schema.json의 "hypothesis" 배열 형식 (rank/drug_class/rationale/
        confidence/data_source/supporting_endpoints)
    """
    er_pos = er.strip().lower() == "positive"
    pr_pos = pr.strip().lower() == "positive"
    her2_pos = her2.strip().lower() == "positive"

    hypotheses = []
    rank = 1

    if her2_pos:
        hypotheses.append({
            "rank": rank,
            "drug_class": "Anti-HER2 therapy (trastuzumab-class)",
            "rationale": "HER2 양성 표현형은 표준 종양학 가이드라인상 항HER2 표적 치료의 대상군으로 알려져 있음 (hypothesis_only — 개별 환자 처방 근거 아님).",
            "confidence": 0.5,  # placeholder — DepMap/GDSC 연결 전
            "data_source": "GDSC",  # placeholder, jhans 검증 필요
            "supporting_endpoints": ["her2_status"],
        })
        rank += 1

    if er_pos or pr_pos:
        hypotheses.append({
            "rank": rank,
            "drug_class": "Endocrine therapy (SERM/aromatase inhibitor) ± CDK4/6 inhibitor",
            "rationale": "ER/PR 양성 표현형은 호르몬 수용체 경로 의존성과 연관된 아형으로, 내분비 치료 계열이 표준적으로 고려되는 군으로 알려져 있음 (hypothesis_only).",
            "confidence": 0.5,  # placeholder
            "data_source": "DepMap-PRISM",  # placeholder, jhans 검증 필요
            "supporting_endpoints": ["er_status", "pr_status"],
        })
        rank += 1

    if not er_pos and not pr_pos and not her2_pos:
        hypotheses.append({
            "rank": rank,
            "drug_class": "Cytotoxic chemotherapy (standard-of-care backbone)",
            "rationale": "Triple-negative 표현형(ER-/PR-/HER2-)은 표적 호르몬/HER2 경로가 없어 세포독성 화학요법이 표준 backbone으로 고려되는 군으로 알려져 있음 (hypothesis_only). ICI 계열은 본 프로젝트 범위에서 명시적으로 제외.",
            "confidence": 0.3,  # placeholder, 근거 약함
            "data_source": "both",
            "supporting_endpoints": ["er_status", "pr_status", "her2_status"],
        })
        rank += 1

    if pam50:
        hypotheses.append({
            "rank": rank,
            "drug_class": f"[PAM50={pam50}] subtype 특이적 세부 근거는 BIOP02-60(jhans) 확정 후 추가 예정",
            "rationale": f"PAM50 {pam50} subtype에 대한 pathway-drug 연결은 아직 draft 수준. jhans 정식 검토 필요.",
            "confidence": 0.0,
            "data_source": "both",
            "supporting_endpoints": ["pam50"],
        })

    return hypotheses


if __name__ == "__main__":
    # smoke test
    example = endocrine_rule("Positive", "Positive", "Negative", pam50="LumA")
    import json
    print(json.dumps(example, indent=2, ensure_ascii=False))

    all_text = json.dumps(example)
    violations = check_forbidden_phrases(all_text)
    print("\n금지 표현 검사:", "위반 없음" if not violations else f"위반: {violations}")

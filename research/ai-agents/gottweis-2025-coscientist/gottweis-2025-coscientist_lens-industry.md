# gottweis-2025-coscientist — Industry / Reproducibility Lens

## 재현성: 닫혀 있다 (Closed system)
- **공개 코드·weight 없음.** Google는 **trusted-tester 프로그램**으로만 접근을 열었고, 시스템·프롬프트·에이전트 오케스트레이션을 공개 배포하지 않는다.
- 기반 모델은 **Gemini 2.0** (독점). 외부 연구자가 결과를 그대로 복제할 수 없다 → 논문은 **capability demonstration**이지 사용 가능한 artifact가 아니다.
- 함의: 우리는 그들의 구현을 가져다 쓸 수 없으므로, **자체 구현 + 공개 가능한 거버넌스 사양**이 오히려 기여가 된다. (재현 불가능한 거대 시스템 vs. 재현 가능한 governed pipeline.)

## 도구 접근 (Tool access) — 우리와 비교
- co-scientist 에이전트는 **web search + 특화 AI 모델 + 데이터베이스**를 호출. 즉 *외부 grounding이 있는 에이전트*.
- 우리 BIOP02 에이전트의 "도구 접근"은 훨씬 좁고 명시적이다: **DepMap PRISM / GDSC / cBioPortal 등 고정된 정적 소스**, foundation-model 임베딩(UNI 등), 고정 split. 임의 web-crawl이 아니라 **감사 가능한(auditable) 데이터 경로**.
- 이는 약점이 아니라 **거버넌스 자산**: 모든 hypothesis가 *추적 가능한 데이터 출처*를 갖는다 → npj Precision Oncology류 임상 인접 저널에서 신뢰 요건과 정합.

## 비용·운영 (Cost / ops)
- **test-time compute scaling** = 품질을 사려면 GPU/inference 비용이 든다. co-scientist는 사실상 무제한 Google 인프라 가정.
- 우리는 **A100 80GB ×1** 단일 서버. 따라서 우리의 multi-agent 루프는 *경량·결정적(deterministic)·배치형*이어야 하며, 무한 토너먼트가 아니라 **유한 Critic-gate 1패스**가 현실적. 이 제약을 설계에 솔직히 반영한다.

## 한 줄 산업 관점
co-scientist는 **닫힌·고비용·범용** 데모. 우리의 산업/학술적 틈새는 **열린 사양·저비용·도메인 한정·감사 가능**한 governed 변형.

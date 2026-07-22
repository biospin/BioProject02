# 06 — 설계 계보: 왜 "완전 자율"이 아니라 "거버넌스 중심"으로 설계했나

이 설계 방향은 즉흥이 아니라 **AI Scientist / multi-agent science 선행연구를 읽고 의도적으로 내린 포지셔닝 결정**이다. 근거 자료는 `research/ai-agents/`에 멀티렌즈 분석으로 정리돼 있다.

## 읽은 선행연구 (research/ai-agents/)

| 논문 | 무엇 | 이 프로젝트에 준 함의 |
|---|---|---|
| **lu-2024-aiscientist** (Sakana, *The AI Scientist*) | 아이디어→실험→논문→자동리뷰까지 **완전 자율** 파이프라인 | **대조군(autonomy contrast).** BIOP02는 그 반대 극단으로 자율성을 **의도적으로 제한**하고 hypothesis-only + 사람 거버넌스를 둔다는 포지셔닝 근거 |
| **gottweis-2025-coscientist** (Google, *AI co-scientist*) | 전문 에이전트(Generation·Reflection·Ranking·Evolution·Meta-review) + Elo 토너먼트 + **scientist-in-the-loop** | Reflection = "우리 Scientific Critic의 직접 대응물". 다중 전문 에이전트 + 사람 개입 구조의 선례 |
| **su-2024-virsci** (VirSci) | 역할 분화 다중 에이전트가 단일보다 나은 아이디어 생성 | "멀티에이전트=novelty"는 **이미 포화(crowded)** → BIOP02의 delta는 협업 자체가 아님을 확인 |
| **qi-2024-biohypo** | LLM 생의학 가설 생성기 평가 | "LLM 가설 생성 자체"도 crowded → 기여를 **거버넌스·검증**으로 재포지셔닝하라는 근거 |
| li-2024-judge-survey · zheng-2023-llmjudge · panickssery-2024-selfpreference | LLM-as-judge와 그 **자기선호(self-preference) 편향** | 자동 검수를 쓰되 **Critic 자기참조 금지·owner≠reviewer**를 못박는 근거 |
| hkust-2025-sciagent-survey | science-agent 서베이 | 전체 지형 지도 |

## 핵심 결론: 기여는 method가 아니라 system/governance

`research/_index/reading_list.md`(kkkim, 2026-06-09)의 novelty 판단이 설계 방향을 못박는다:

> **"형태(H&E)→분자표현형 예측은 이미 포화 상태(scoop 위험 큼).** 따라서 BIOP02의 형태→표현형 컴포넌트 자체는 novelty가 아니며, 단독 기여로 내세우면 리뷰를 못 넘긴다."*

직접 scoop 후보(`tafavvoghi-2024` 동일 코호트+공개코드, `dawood-2024` H&E→약물민감도)가 존재하므로, 정직한 포지셔닝은:

> **"정직한 포지셔닝: 기여 = 새 method가 아니라 system / evaluation / governance.** 경쟁자를 baseline으로 인용하고, 그 위에 **표현형-매개 framing + Critic 가드레일 + cross-DB(PRISM↔GDSC) 일관성**을 delta로."*

## 이것이 설계 전반을 어떻게 결정했나

선행연구의 두 교훈 — ① 완전 자율(Sakana)은 화려하지만 검증이 약하다, ② 다중 에이전트·가설 생성은 이미 붐빈다 — 이 곧바로 이 프로젝트의 설계 원칙이 됐다:

| 선행연구 교훈 | 이 프로젝트의 설계 선택 | 구현 위치 |
|---|---|---|
| 완전 자율은 검증이 약함 | **자율성 제한 + 사람 거버넌스 게이트** (검증 게이트·공개 게이트) | [01](01_two_layer_architecture.md), [04](04_automated_review_and_governance.md) |
| 멀티에이전트 자체는 novelty 아님 | delta를 **독립 Critic 게이트·재현성 산출물**에 둠 | [04](04_automated_review_and_governance.md), 5종 아티팩트 계약 |
| 가설 생성도 crowded | **hypothesis-only** 출력 + `claim_level` 강제, DRP 프레이밍 금지 | [03](03_routing_and_artifact_contract.md), 스키마 |
| LLM-judge는 자기선호 편향 있음 | **Critic 자기참조 금지, owner≠reviewer, 독립 다중패스** | [04](04_automated_review_and_governance.md), [05](05_human_collaboration.md) |
| 사람이 병목이면 몇 주 정체 | **티어 게이트로 사람 개입 최소화**(Tier B 진행 허용, C만 사람) | [04](04_automated_review_and_governance.md) |

## 한 줄로

> **Sakana의 AI Scientist가 "얼마나 자율적으로 갈 수 있나"를 물었다면, 이 프로젝트는 "얼마나 정직하고 검증 가능하게, 그리고 여러 사람이 함께 굴릴 수 있게 만들 수 있나"를 물었다.** 자동화의 목표는 사람을 빼는 것이 아니라, 사람이 판단해야 할 지점만 남기고 나머지 노동을 에이전트가 대신하는 것이다.

## 참고

- 선행연구 원본 분석: `research/ai-agents/*/`, 인덱스 `research/_index/reading_list.md`·`papers.csv`
- 포지셔닝 문서: `research/novelty_positioning.md`, `research/critique_and_revised_direction.md`
- ⚠️ 위 표의 arXiv 인용 다수는 `reading_list.md`에서 **DOI unverified**로 표기됨 — 논문 인용 전 `agents/critic/scripts/verify_citations.py` + CrossRef 재확인 필수(`CLAUDE.md` 인용 검증 규칙).

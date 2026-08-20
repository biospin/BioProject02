# Falsify(창과 방패) 스터디 ↔ AI Scientist 하네스 연계안

> 초안 2026-08-20 (kkkim). **논의용 draft** — 팀·스터디 킥오프 전 검토. 관련: SCRUM-6(가짜연구소 시즌13 빌더), `ai_scientist/output_v03`, `research/ai-scientist-positioning/2026-08-20_landscape-and-differentiation.md`.
> ⚠️ 미발표 과학(Paper C 5암종 결과·raw)은 이 스터디에 **넣지 않는다** — 공유 대상은 일반화된 검증 하네스뿐.

## 1. 왜 붙는가 (한 줄)

Falsify는 **Red(위조: 논문에 결함 주입/탐지) × Blue(반증: 게이트가 그 결함을 잡나)** 구도의 검증시스템 스터디다(SCRUM-6). 이건 우리 `ai_scientist` 하네스의 **핵심 차별점(b+d)** 과 정확히 같은 결이다 — 무결성 게이트를 mutation/공허통과로 검증하는 층. 즉 **스터디를 굴리면 하네스의 방어 가능한 부분이 저절로 증거로 축적된다.**

## 2. 두 트랙은 상보적이다 (혼동 금지)

| | **Registry-Replay** (내부) | **Falsify 코퍼스** (스터디/공개) |
|---|---|---|
| 대상 | 우리 사고 27건(PITFALLS_REGISTRY) | 공개 논문 10–20편(SCRUM-6 범위) |
| 질문 | 우리 CI 7종이 *우리가 실제 겪은* 결함을 잡나 (catch rate X/27) | 게이트가 *공개 논문의* 결함 3–5종을 잡나 |
| 비용 | 값쌈·비-GPU (에이전트 1차 ~30–60분 + 검토 반나절) | 스터디 16주 분량 |
| 역할 | 하네스 논문의 **내부 증거**(우리 게이트가 실전에서 작동) | 하네스의 **외부 일반화**(남의 논문에도 통함) + 오픈소스 코퍼스 |

→ **Registry-Replay가 먼저·값쌈**, Falsify가 그 위에 외부 검증을 쌓는다.

## 3. 커리큘럼 ↔ 하네스 조각 매핑 (스터디 주차 초안)

Falsify 운영원칙(SCRUM-6): "1주차에 제출 경로(저장소·제출양식·자동판정)부터, 게이트는 그 위에."

| 단계 | 스터디 활동 | 우리 하네스에서 재사용 |
|---|---|---|
| 제출 경로 | 저장소·제출양식·자동 판정 배선 | `evals/validation_harness/run_validation.py`·`.github/workflows/critic-validators.yml`(이미 `{{SLOT}}` 살균) |
| 결함 3–5종 | 숫자 불일치·없는 인용·근거↔결론 어긋남 | `check_number_drift`·`verify_citations`(medsci 버그 replica)·claim 규율 |
| Blue 게이트 검증 | 게이트가 공허하지 않은지 mutation | `evals/*/mutation_check.py`·`test_gate_vacuous_pass.py` |
| 라벨·리포트 | 결함 라벨 3개 + 리포트 1편 | 하네스 논문 related-work·방법 절 재료 |
| 메타학습 | 놓친 결함 → 새 가드 | incident→registry→가드 루프(우리 (d)) |

## 4. Registry-Replay — 스터디 킥오프의 값싼 씨앗

**바로 착수 가능**(비-GPU, 미발표 과학 무접촉):
- 입력: PITFALLS 27건 + CI 7종.
- 절차: 각 사고 → (어느 게이트가 잡아야 하나 판정) → 재현 케이스 구성 → 게이트 실행 → caught/missed 기록 → **catch rate X/27 표 + 놓친 건 Limitation**.
- ⚠️ **가드레일**: 점수 좋아지게 게이트 튜닝 금지(= A5/A2가 금지한 골대이동). 봉인 그대로 재생.
- 산출: `evals/registry_replay/` + 리포트. 스터디 1주차 데모 + 하네스 논문 Fig 소재로 이중 사용.

## 5. 경계 (외부 공유 전 필수)

1. **미발표 과학 격리** — 5암종 결과·raw·manifest는 스터디에 안 올린다. 공유는 일반화 하네스(template/evals/CI)만.
2. **살균** — 루트 `CLAUDE.md`에 서버 IP·포트·이메일 있어 공개 불가. `{{SLOT}}` 템플릿만.
3. **귀속 사전합의** — 스터디 집단 산출물 vs 팀 논문의 선을 처음부터. 하네스 논문 저자에 스터디원이 들어갈지 미리 정한다.
4. **순서** — Paper C 먼저. Registry-Replay·툴킷 일반화는 미발표 과학 무접촉이라 병행 가능.

## 6. 소요·의사결정

- **Registry-Replay 1차안**: 에이전트 ~30–60분 + 사람 검토 반나절. 비-GPU, 지금 병행 가능.
- **스터디 빌더 신청**: SCRUM-6 마감 8/19(경과) — 합격 발표 8/21, 온보딩 4주, 킥오프 9월 중순~말. Registry-Replay를 그 전에 해두면 킥오프 자료가 이미 손에 있다.
- **결정 필요**: (a) Registry-Replay 지금 착수? (b) 하네스 논문을 스터디 산출물로 공식 연결할지 팀 합의.

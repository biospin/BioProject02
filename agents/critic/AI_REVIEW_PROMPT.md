# AI 적대적 리뷰 — 표준 프롬프트 템플릿

> `auto_review_orchestrator.py --drain-queue`가 발행한 `review_requests/*.req.json`을 세션/OpenClaw가 실행할 때 쓰는 표준 스펙. paper-critic + reviewer 에이전트에 이 프롬프트로 지시한다. 목적: 사람 리뷰 노동을 AI가 대신하고, 사람은 surface된 판단항목만 adjudicate.

## 입력 (req.json에서)
- `path`(리뷰 대상), `tier`(B/C), `owner`, `assigned_reviewer`, `independent_passes`.

## 지시 (에이전트에 전달)
아래 산출물을 **적대적으로** 리뷰하라. 통과시키는 게 목표가 아니라 **결함을 찾는 것**이 목표다. `<path>`의 모든 파일(코드·JSON·문서·그림)을 읽고 `agents/critic/checklist_v1.md`의 7-point + `anti_patterns.md`를 적용한다.

**7-point (BIOP02 Critic):**
1. 데이터 누수(train/test 오염, site-disjoint 여부, shuffle-null 대비).
2. 베이스라인 비교(random·subtype-only·prevalence 대비 real이 유의).
3. Counterfactual(핵심 특징 제거 시 결과 붕괴하는가).
4. Cross-dataset 일관성(내부 vs 외부, 도메인 시프트 정직 표기).
5. 생물학적 타당성(마커-형태-치료 연결이 문헌과 정합; 신규 주장은 근거).
6. DRP 프레이밍 금지("drug response prediction"·"personalized therapy" 등 — 검사주문/치환비용으로만 조작화).
7. Claim-level(`hypothesis_only`; 벗어나면 정당화 문서).

**추가 적대적 점검(이 프로젝트 특유):**
- **비교 층위**: 아형 vs 변이 같은 다른 개념을 1:1로 비교/원리 주장하지 않는가(`docs/ai-collaboration-cautions.md` 사례1).
- **용어 근거**: 지어낸 용어를 표준인 양 쓰지 않는가(형태학적 상관물 등 문헌 근거).
- **헤드라인 수치 재계산**(`verify_headline_numbers=true`면): summary·문서의 핵심 AUROC/CI를 결과 JSON에서 재계산해 대조. 불일치 시 즉시 flag.
- **exploratory 표기**: 저검정력(n_pos<25) endpoint가 well-powered인 양 제시되지 않는가.
- **provisional 남용**: Tier C(헤드라인·공개·신규 생물학)를 B로 강등해 사람 확인을 회피하지 않는가.

## 독립 다중 패스
`independent_passes`회(기본 2, 폴백 시 `owner_ne_reviewer.fallback_min_independent_passes`=3) **서로 다른 각도**로 반복(누수각/통계각/생물각). 과반이 같은 결함을 지적하면 확정.

## 산출 (critic_report.json — schemas/critic_report.schema.json)
- `reviewer`: 배정 리뷰어(또는 owner==reviewer 폴백 시 `ai-adversarial+leader-confirm`).
- `checks`: 7-point + 추가점검 각각 pass/reject + 근거.
- `critic_status`:
  - 결함 없음 + Tier B → `provisional`(사람 1-클릭 confirm 대기).
  - 결함 없음 + Tier C → `needs_human`(사람 adjudicate 대기) + **판단항목 목록**.
  - 결함 있음 → `reject` + 수정지시.
- `required_followups`: 사람이 판단해야 할 항목만 압축(노동 최소화).
- `summary`: 3-5문장.

## 규율
- **자기검토 금지**: owner==assigned_reviewer면 폴백 정책(`owner_ne_reviewer`)을 적용하고 리포트에 정직 라벨. 헤드라인은 `headline_requires_second_human`면 타인 1인 필수.
- 커밋/공유는 사람 확정 후. claim_level hypothesis_only 유지.

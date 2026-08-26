# 01 — 2-레이어 아키텍처: 분석 파이프라인 + 논문 생산 하네스

## 핵심 설계 결정

AI Scientist를 **하나의 거대한 자율 에이전트로 만들지 않았다.** 대신 **책임이 다른 두 레이어를 분리**하고, 위 레이어가 아래 레이어의 산출물을 소비하도록 설계했다.

```
┌─────────────────────────────────────────────────────────────────┐
│  레이어 B — 논문 생산 하네스 (paper-production harness)           │
│  결과 → 논문·그림·검수·발표. .claude/agents/ + .claude/skills/    │
│  literature-scout · novelty-strategist · research-methodologist  │
│  manuscript-writer · paper-critic · venue-reviewer · presenter   │
│  입구 = paper-production-orchestrator (Skill, 메인 루프가 실행)   │
└───────────────────────────▲─────────────────────────────────────┘
                            │  result 파일 + consolidated summary 소비
                            │  (도메인 슬롯 spatialpatho-analyst 가 다리)
┌───────────────────────────┴─────────────────────────────────────┐
│  레이어 A — 도메인 분석 파이프라인 (analysis pipeline)           │
│  H&E WSI → 임베딩 → 분자 표현형 예측 → 치료 근거 랭킹            │
│  agents/data · agents/embedding · agents/modeling ·              │
│  agents/therapeutic_evidence · agents/critic                    │
│  결과물 = experiments/<user>/<date>/ 5종 아티팩트               │
└─────────────────────────────────────────────────────────────────┘
```

근거: `docs/HARNESS.md` 서두 경고 — *"이건 논문 **생산** 하네스다. 기존 **분석 파이프라인**(`agents/<role>/`)을 대체하지 않는다 — 그 위에 얹혀 결과를 논문으로 쓰는 레이어이고, 분석 레이어는 도메인 슬롯 `spatialpatho-analyst`가 대표한다."*

## 왜 두 레이어로 나눴나

1. **재사용성.** 레이어 B(문헌·집필·검수·발표)는 도메인과 무관한 **연결조직(connective tissue)** 이다. `docs/HARNESS.md`의 로스터에서 대부분 멤버가 "재사용"으로 표시된다. 다른 논문/프로젝트(BIOP01 등)에 그대로 복사 가능. 도메인 특수성은 **단 하나의 슬롯** `spatialpatho-analyst`에 격리된다.
2. **관심사 분리.** 분석 레이어는 "숫자가 맞나"(누수·baseline·재현성)를 책임지고, 생산 레이어는 "그 숫자를 정직하게 논문으로 쓰나"를 책임진다. 검증 게이트가 두 레이어 경계에 놓인다(아래).
3. **성숙도 차이 흡수.** 집필-단계 산출물이 없던 시기에도 생산 레이어를 `<FILL>` 플레이스홀더로 **미리 배선만 해둘 수 있었다** — 없는 것을 없다고 표시해두면 구조가 먼저 서고 값은 나중에 들어온다.

> 🔴 **정정(2026-08-04): "집필-단계 산출물이 아직 없다"는 더 이상 사실이 아니다.**
> 초판은 *"분석 진행 단계라 manuscript/figures가 아직 없다"* 고 적었으나, 현재 `manuscript/sections/`에 **5개 섹션이 존재**하고 Discussion 한계 절까지 실물로 작성돼 있다(`04_discussion.md` §한계, Critic 승인조건 1 충족 판정 완료).
> ⚠️ 다만 **`SKILL.md`는 아직 이 사실을 반영하지 못했다** — L10이 *"집필 이전 단계 산출물이 아직 없다"*, L18이 `<FILL: docs/manuscript/preprint.md (미존재)>`라고 말한다. 실제 원고 경로는 **`manuscript/sections/`** 다. 하네스 문서가 현실보다 뒤처진 상태이며, 이 설계서는 그것을 **감추지 않고 표시**한다([03](03_routing_and_artifact_contract.md) 참조).

## 레이어 A — 도메인 분석 파이프라인

역할별 워크스페이스(`agents/<role>/`)로 구성. 의존성 체인이 있다 (`CLAUDE.md` *Agent Dependency Chain*):

```
data (manifest + split_policy_v0)
  └→ embedding (어떤 슬라이드 tiling할지 결정)
        └→ modeling (dummy 임베딩 → 실제 임베딩 교체 후 학습)
              └→ therapeutic_evidence (DepMap/GDSC 전이)
                    └→ critic → critic_report.json
                          └→ orchestrator (등록·공유)
```

파이프라인의 과학적 목표: **H&E WSI → 형태학 임베딩 → 분자 표현형 예측(ER/PR/HER2·PAM50) → DepMap/GDSC 전이 → 순위화된 치료 가설.** 이것은 **약물반응예측(DRP)이 아니다** — 약물 구조 입력 없음, 가설 출력 전용 (`CLAUDE.md`, `README.md`).

**모든 실험은 5종 아티팩트로 봉인된다** (`AGENTS.md` §5): `config.yaml · model.pt · metrics.json · predictions.npy · critic_report.json` + `metrics.json` 안에 `commit_hash`. 이 강제 산출물 계약이 "실험을 실제로 수행했다"의 재현 가능한 증거가 된다.

## 레이어 B — 논문 생산 하네스

레이어 A가 만든 result 파일을 소비해 논문·그림·발표를 생산한다. 표준 경로 (`docs/HARNESS.md` §2):

```
research-methodologist / literature-scout / novelty-strategist   (기획·근거)
   └─▶ spatialpatho-analyst ──▶ result files + summary            (분석·검증)
   └─▶ manuscript-writer ──▶ manuscript (+ figure 스크립트 → figures)  (집필·그림)
   └─▶ paper-critic (+ agents/critic/ 체크리스트)                  (내부 적대검수)
            └─▶ (수정) manuscript-writer
   └─▶ 🔒 검증 게이트 ① 결과 검증 (커밋 전)                        (숫자 재계산)
   └─▶ venue-reviewer (선택, 격리)                                 (외부 referee 시뮬)
            └─▶ (수정) manuscript-writer  ⚠️ 게이트 ① 이후의 수정
   └─▶ 🔒 검증 게이트 ② 패키지 검증 (공개 직전) ──▶ presenter       (재대조→발표)
```

> ⚠️ **게이트 ① 뒤의 "수정"은 검증을 무효화할 수 있다.** `manuscript-writer`는 `Write`를 보유해(`Read, Write, Edit, Bash, Grep, Glob`) 리뷰 반영 과정에서 원고를 **통째로 다시 쓸 수 있고**, 그때 게이트 ①이 확인한 숫자·인용이 조용히 바뀌어도 **에러가 나지 않는다.** 게이트 ②가 공개 직전에 재대조하도록 설계된 이유가 이것이지만, ②는 **사후 탐지**이지 사전 차단이 아니다. 같은 성격의 방어가 CI에도 있다 — `check_number_drift.py` 역시 드리프트를 **발견**할 뿐 발생을 막지 않는다([04](04_automated_review_and_governance.md) CI 절).

> ⚠️ **2026-07-27 순서 스왑(BIOP02-103).** 이전 설계는 `리뷰 → 검증 게이트` 순이었으나 **`검증 게이트 → 리뷰`로 뒤집혔다.** 근거는 원본 하네스 규칙 *"paper-critic + gate **FIRST**, then reviewer — reviewer assumes pre-submission QA is done"*. 요지: **검증되지 않은 숫자를 리뷰에 보내지 않는다.** 동시에 게이트가 1개 → **2개**(① 커밋 전 결과 검증 / ② 공개 직전 패키지 재검증)로 늘었다 — 리뷰 반영으로 본문이 바뀌었을 수 있어 공개 전 한 번 더 돌린다.

## 레이어 경계의 게이트 (사람이 통과시킨다)

레이어 경계는 **자동화하지 않은 사람 게이트**로 지킨다 (`SKILL.md` 실행 흐름 7·8.5, `CLAUDE.md` 사람 승인 게이트):

1. **검증 게이트 ① — 결과 검증 (커밋 전).** headline 숫자를 결과 파일에서 **결정론적으로 재계산**해 대조. 캐시·이전 세션 출력을 그대로 믿지 않는다. 실패하면 멈추고 사람에게 보고, 커밋·발행 금지.
2. **검증 게이트 ② — 패키지 검증 (공개 직전).** 본문 숫자 ↔ 결과 파일 재대조 + 그림·표·supplementary 동봉 확인.
3. **공개 게이트 (publication gate).** 저자·소속·저자순서·corresponding email·IP·GPU 제공처(Modulabs) 확정 전까지 공개 보류. 팀 프로젝트라 저자-대면 내용은 팀 합의 필요.

> 🔴 **게이트 ①은 아직 실행 명령이 없다(리포 실측 2026-07-27, `SKILL.md` 7단계 경고).** BIOP01의 `p3_concordance.py`에 해당하는 **BIOP02용 결정론 재계산 스크립트가 리포에 존재하지 않는다.** `agents/critic/auto_review_gate.py`는 DRP 스코프·claim level·metrics 표기를 보는 **문서 규칙 검사이지 수치 재계산이 아니다.** 그 자리가 채워지기 전까지 게이트 ①은 **사람이 수동 대조**한다 — 이 설계서가 기록하는 하네스의 가장 큰 미완성 지점이다.

→ 다음: [02_agents_and_roster.md](02_agents_and_roster.md)

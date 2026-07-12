# 자동 리뷰 · provisional 진행 정책 (사람 의존 최소화)

> 2026-07-12, 리더(kkkim) 결정. 목적: 빠른 리더가 느린 팀 리뷰에 막히지 않게 하되, **무결성·공개 게이트는 사람에 남긴다.** "자동 **승인**"이 아니라 **자동 리뷰 + 조건부 진행**이다.
> 관련: `agents/critic/checklist_v1.md`(7-point), `anti_patterns.md`, `schemas/critic_report.schema.json`, `agents/critic/auto_review_gate.py`(집행 스크립트).

## 왜 전부 자동승인(A-only)은 안 되나
이 프로젝트 품질은 사람 리뷰가 빠른-단독-리더의 실수를 잡아온 것에 의존해 왔다(아형 vs 변이 층위 오류, 지어낸 용어, 이미 승인된 모델 재신청 등 — 전부 사람이 잡음). Critic owner≠reviewer는 자기검토 방지 장치라 자동승인 시 무력화된다. → 무결성·공개는 자동승인 대상 아님.

## 3층 정책
| 층위 | 대상 예 | 처리 | 사람 |
|---|---|---|---|
| **A. 기계적** | 문서·인프라·상태전환·의존성 확인·JIRA 진행·용어/스키마 | **완전 자동**(gate 통과 시 `auto_pass`) | 불필요 |
| **B. 루틴 결과** | 일반 MIL 결과·그림·라벨·원고 섹션 초안 | **AI 리뷰 → `provisional` 즉시 진행 → 사람 비동기 1-클릭 확인** | 확인만(비동기) |
| **C. 무결성·공개** | 헤드라인 주장·저자/공개·신규 생물학 주장·교차개념 비교 | **AI 적대적 리뷰(heavy lifting) → 사람 adjudicate만** | 필수(최소 노동) |

## Tier-C 인력난 해법 (사람이 적어도 돌아가게)
1. **AI가 리뷰 노동을 대신**: `paper-critic` + `reviewer` 에이전트가 **독립 다중 패스**로 적대적 리뷰 → 이슈를 다 surface. 사람은 처음부터 리뷰하지 않고 **surface된 판단항목만 adjudicate**(노동 1/5로).
2. **리더는 타인 산출물의 adjudicator 가능**. 단 **리더 자신의 산출물은 owner≠reviewer** — 이때는 (a) 다른 팀원 1인 확인, 또는 (b) **AI-적대적 다중리뷰 + 리더 확인** 조합을 쓰되 리포트에 `reviewer: "ai-adversarial+leader-confirm"`으로 **정직히 라벨**(사람 부재 시 폴백, 헤드라인엔 가급적 타인 1인).
3. **비-헤드라인 C 후보는 B로 강등** 가능(리더 판단) — 진짜 C(공개·저자·신규 생물학 주장)만 남긴다.

## critic_status 어휘 (schema 확장)
- `auto_pass` — Tier A, gate 기계검사 전부 통과. 사람 불필요.
- `provisional` — Tier B, AI 리뷰 통과·사람 확인 대기. **이 상태로 진행·커밋 허용**(공유는 확인 후).
- `needs_human` — Tier C, AI 적대적 리뷰 완료·사람 adjudication 대기.
- `pass` / `reject` — 사람(또는 위임된 adjudicator) 최종 판정.
- `blocked` — 하드룰 위반(아래). 티어 무관 즉시 정지.

## 하드룰 (티어 무관, 항상 `blocked`)
- DRP 표현(`drug response prediction`·`personalized therapy`·`patient-specific ... treatment`·`optimal treatment`) 검출.
- `claim_level != hypothesis_only`(정당화 문서 없이).
- 필수 산출물 누락(experiment 5종: config·model·metrics·predictions·critic_report + commit_hash) 또는 `metrics.json` 필수필드 결측.
- 헤드라인 수치 재계산 ↔ summary 불일치.
- 무결성 항목 자기검토(owner==reviewer, AI 폴백 라벨 없이).

## 흐름
```
산출물 생성(분석/원고 에이전트)
  → auto_review_gate.py: 티어분류 + 기계검사(하드룰)
      ├ 하드룰 위반 → blocked (정지, 리더에 알림)
      ├ Tier A 통과 → auto_pass (끝)
      ├ Tier B → provisional + AI 리뷰 큐 → (AI 리뷰) → 사람 비동기 확인
      └ Tier C → AI 적대적 리뷰 → needs_human(판단항목 목록) → 사람 adjudicate
```

## 구조 (구현됨 — 결정되면 config만 채워 활성화)
```
agents/critic/
  auto_review_config.json     # ★ 결정 항목 전부(스터디에서 <DECIDE...> 채움 + enabled=true)
  auto_review_gate.py         # 결정론 게이트(하드룰·티어). config 기반, 없으면 기본값
  auto_review_orchestrator.py # gate→큐→상태→알림. enabled=false면 DRY-RUN(안전 대기)
  AI_REVIEW_PROMPT.md         # AI 적대적 리뷰 표준 스펙(7-point+추가점검)
  cron_auto_review.sh         # 주기 스캔 스캐폴드(cron.enabled=true 시)
  ai_review_queue.jsonl       # (생성) AI리뷰 대기 큐
  review_status.json          # (생성) 경로별 상태
  review_requests/            # (생성) drain 시 에이전트 호출 스펙
```
데이터 흐름: `cron_auto_review.sh`(주기) → `orchestrator --scan`(gate+큐+알림) → `orchestrator --drain-queue`(에이전트 호출 스펙 발행) → **세션/OpenClaw가 스펙대로 paper-critic/7-point 실행** → `critic_report.json` → `orchestrator --confirm <path> --by <사람>`(1-클릭 확인).

## 활성화 절차 (스터디 결정 후)
1. `auto_review_config.json`의 `<DECIDE...>` 채움: adjudicators(C 담당)·owner_ne_reviewer 폴백·notify 채널·cron 주기·(원하면 tier 패턴 조정).
2. `"enabled": true` (+ 원하면 `cron.enabled: true`).
3. cron 등록: `crontab -e` → `*/30 * * * * /home/kkkim/project/BioProject02/agents/critic/cron_auto_review.sh`.
4. #biop02-general 공지(팀 리뷰 의무 변경).
   — 이전까지는 `enabled=false`라 실제 행동 없이 DRY-RUN(무엇을 할지만 로그).

## 이식성 (타 프로젝트 재사용, 예: BIOP01)
코드(gate·orchestrator·cron·prompt)는 **project-agnostic** — 프로젝트별 값은 전부 `auto_review_config.json`에 있다. 타 프로젝트는:
1. `agents/critic/` 5개 파일 복사.
2. 자기 `auto_review_config.json` 작성 — **hard_rules(자기 금지 프레이밍·필수 metrics 필드), tier 패턴(자기 파일명), cross_review_map(자기 팀), notify 채널, adjudicators**. (BIOP02의 DRP 금지어·#biop02-* 채널·팀원명을 자기 것으로 교체.)
3. `enabled=true`.
코드 수정 불필요. ROOT는 스크립트 위치 기준 자동 산출(`parents[2]`).

## 거버넌스
리더가 정책·티어 경계를 정한다. 팀원의 리뷰 의무를 바꾸므로 **팀 공지 대상**(#biop02-general). provisional로 진행한 것도 **공개·저자-대면은 사람 확정 게이트 유지**(CLAUDE.md).

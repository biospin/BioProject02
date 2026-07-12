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

## 거버넌스
리더가 정책·티어 경계를 정한다. 팀원의 리뷰 의무를 바꾸므로 **팀 공지 대상**(#biop02-general). provisional로 진행한 것도 **공개·저자-대면은 사람 확정 게이트 유지**(CLAUDE.md).

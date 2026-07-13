---
name: paper-production-orchestrator
description: 논문 생산 루프의 입구(진행표/팀장) — SpatialPathoAgent(BioProject02). "논문 풀 파이프라인 돌려줘", "프리프린트 업데이트해서 제출 준비", "분석→집필→그림→검수까지 한 번에", "그림만 다시", "리뷰만 다시", "critic 지적 반영해", "최신 결과로 본문 갱신" 같이 분석·집필·그림·검수·검증·발표를 엮는 요청에서 사용한다. 기존 멤버(spatialpatho-analyst, manuscript-writer, 그림 스크립트, paper-critic, reviewer, presenter)를 정해진 순서로 호출하고 부분 재실행을 처리한다. 새 agent는 만들지 않는다.
---

# paper-production-orchestrator (논문 생산 루프 진행표 / 팀장) — SpatialPathoAgent

이 Skill은 **메인 루프(PI)가 실행**한다. "계획만" 하는 `paper-orchestrator`(agent)와 달리 실제로 루프를 돌린다. 멤버는 전부 기존 정의를 재사용 — 신규 agent 0개. 전체 랩 지도·멤버 JD = `docs/HARNESS.md`, 라우팅·산출물 계약 = `CLAUDE.md`.

> ⚠️ **BioProject02는 팀 프로젝트이자 분석 진행 단계**다(sprint 0/1). 집필 이전 단계 산출물(consolidated FINDINGS·manuscript·figures)이 **아직 없다** → 그 부분 FILL은 팀 확정 대기. headline 숫자·주장을 지어내지 말 것.

## 언제 이 스킬을 쓰나
초기/전체("풀 파이프라인", "제출 준비") · 부분 재실행("그림만", "리뷰만", "분석만") · 보완("critic 지적 반영", "최신 결과로 갱신").

## 실행 모드 분기 (먼저 확인)
1. 산출물 존재·최신 여부:
   - result files: `<FILL: modeling eval outputs / therapeutic-evidence tables>` + `<FILL: consolidated results-summary — e.g. results/FINDINGS.md (미존재)>`
   - manuscript: `<FILL: docs/manuscript/preprint.md (미존재)>`, figures: `<FILL: docs/manuscript/figures/ (미존재)>`
2. 분기: 없음/"풀 파이프라인"/"제출 준비" → 전체 · 있음+부분요청 → 해당 단계만 · "지적 반영"/"최신 결과로 갱신" → 하류 단계만.
3. `spatialpatho-analyst`의 LLM 기반 sub-분석이 **offline mock**로 돌았는지 확인 → mock이면 "실 결과 아님/데모" 명시.

## 멤버 구성 (전원 기존 재사용)
`spatialpatho-analyst`(도메인 슬롯 = data/embedding/modeling/therapeutic_evidence/critic 파이프라인 대표), manuscript-writer(그림 포함), paper-critic, reviewer, presenter. (기획 선택: research-methodologist, literature-scout, novelty-strategist.)

> 그림 생성은 agent가 아니라 스크립트로 둔다. `manuscript-writer`가 `<FILL: figure-generation script>`를 실행해 결과 파일에서 만든다.

## 품질 기준선
- **Scope 규율: NOT drug-response prediction** (약물 구조 입력 없음, BRCA 단일, 가설 출력). 통계 뒷받침 없는 우월 주장 금지, weak ≠ zero.
- 숫자는 결과 파일에서만(메모리 재유도 금지). class imbalance → AUPRC + AUC. leakage-controlled(환자 단위) split 명시. GPU 제공처(Modulabs) Acknowledgments 명시.
- 그림은 결과 파일에서 생성(하드코딩 금지), 95% CI + paired test 표시, 번호는 첫 언급 순.

## 실행 흐름
1. 모드 분기 → 단계 집합 결정.
2. (선택) 기획·근거 — 새 방향일 때만.
3. **분석·eval** — `spatialpatho-analyst` → result 파일 + consolidated summary 갱신. mock 경고 확인. Scientific Critic 체크리스트 대조.
4. **집필 + 그림** — `manuscript-writer` → manuscript. 그림은 figure 스크립트 → figures/.
5. **검수 (자동 리뷰 오케스트레이터 경유)** — `agents/critic/auto_review_orchestrator.py`가 **결정론 게이트 → 큐 → AI 적대적 리뷰**(`AI_REVIEW_PROMPT.md` 스펙으로 `paper-critic`+`reviewer` 실행) → `critic_report.json`. 하드룰 위반=`blocked`, Tier B=`provisional`(진행·커밋 허용, **공유만** 사람 확인), Tier C=`needs_human`(사람 adjudicate). reject/blocked면 6으로. (config `enabled=false`면 dry-run 안전대기.)
6. **수정** — `manuscript-writer`가 반영.
7. (선택) 정식 리뷰 — `reviewer` → `<FILL: peer review note path>`.
8. **검증 게이트** — `<FILL: verify-gate — headline AUC/AUPRC를 모델 eval 출력에서 결정론적 재계산 → summary 대조>`. 실패하면 멈추고 사람에게 보고, 커밋·발행 금지.
9. (선택) 발표 — `presenter` → 덱·발제.

각 단계 산출물은 파일로 남긴다.

## 산출물 계약
| 단계 | 멤버 | 산출 파일 | 다음이 읽음 |
| --- | --- | --- | --- |
| 분석·eval | spatialpatho-analyst | `<FILL: eval outputs>`, `<FILL: results summary>` | 집필·검수 |
| 집필+그림 | manuscript-writer | `<FILL: manuscript>`, `<FILL: figures dir>` | 검수·리뷰·발표 |
| 검수 | paper-critic (+ agents/critic/) | 적대 노트 + 그림 QA | 집필(수정) |
| 검증 게이트 | (커밋/공개 전) | `<FILL: verify-gate command>` | 사람 |
| 발표 | presenter | 슬라이드/발제 | 사람 |
| 상태 핸드오프 | (전원) | `HANDOFF.md`, `TODO.md`, `SESSION_LOG.md` | 다음 세션 |

## 자동 리뷰 루프 — 사람이 병목 되지 않게 (loop-engineering)
> **critic이 몇 주간 돌고 도는데 중간에 사람이 병목**이 되는 실패를 막는 게 이 루프의 목적(2026-07 스터디 논의). 코드 = `agents/critic/{auto_review_gate,auto_review_orchestrator}.py` + `auto_review_config.json`(결정항목 전부) + `AI_REVIEW_PROMPT.md` + `cron_auto_review.sh`.

- **AI가 리뷰 노동을 대신**한다(7-point + 적대적 다중패스 + 헤드라인 수치 재계산). 사람은 **surface된 판단항목만 adjudicate**(`required_followups`) — 노동 최소화.
- **진행을 사람 리뷰에 볼모 잡지 않는다**: Tier B = `provisional`(진행·커밋 허용) → **공유/공개만** 사람 1-클릭 확인. 사람이 하드 블로킹하는 건 headline·publish(Tier C `needs_human`)뿐.
- **리뷰어 부재 폴백**(리더 단독): `owner_ne_reviewer` — AI 적대 독립 패스 ≥3 + 리더 확인(라벨 `ai-adversarial+leader-confirm`), headline은 타인 1인 필수. → 몇 주 정체 대신 계속 굴러감.
- **cron 주기 스캔**(`cron.enabled`)으로 사람 트리거 없이 자동 검수 → 큐 → drain(에이전트 실행 스펙 발행). 전부 `config.enabled=false`면 dry-run.
- **portable**: 코드는 project-agnostic. BIOP01 등은 스크립트 복사 + 자기 `auto_review_config.json`(하드룰·금지프레이밍 교체)만 넣으면 작동.

## 실패 처리 / 멈춤 조건
- verify 게이트 실패 → 멈춤, 무엇이 왜 실패했는지 보고. mock 경로 → 데모 명시. 산출 파일 미생성 → 재시도 1회 후 보고.

## 사람 승인 게이트 (자동화하지 않음)
- 공개(프리프린트/blog)는 **저자·소속·저자순서·corresponding email·IP·GPU 제공처 확정** 전까지 보류. 외부 발송은 사람 승인 뒤에만. 커밋/푸시는 사람이 한다. **팀 프로젝트라 저자-대면 내용은 팀 합의 필요.**

## 마무리
최종 보고에 무엇을 어떤 순서로 돌렸고, 어떤 파일이 갱신됐고, verify 통과 여부, 남은 일을 done/in-progress/blocked로 구분해 명시. 부분 재실행이면 안 건드린 단계도 명시.

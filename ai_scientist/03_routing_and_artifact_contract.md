# 03 — 자연어 라우팅 + 산출물 계약

에이전트를 여럿 두면 "어떤 요청을 누구에게 보내나"와 "에이전트끼리 무엇을 주고받나"를 정해야 한다. 이 설계는 그 둘을 각각 **자연어 라우팅표**와 **산출물 계약(artifact contract)** 으로 고정했다.

## (A) 자연어 라우팅 — 에이전트 이름을 몰라도 배정

요청에 에이전트 이름이 없어도 자연어로 배정한다. 근거: `CLAUDE.md` *자연어 라우팅* 표.

| 요청 (자연어) | 첫 에이전트 |
|---|---|
| "분석 돌려줘 / 재실행 / eval·통계 / 임베딩·모델 성능 / 오류 분석" | `spatialpatho-analyst` |
| "프리프린트/저널/블로그 초안·섹션 써줘" | `manuscript-writer` |
| "그림 만들어줘 / 그림 번호 정리" | `manuscript-writer` (figure 스크립트 실행) |
| "선행연구 / related work / 스쿱 확인" | `literature-scout` |
| "차별화 각도 / 뭘 새로 해야 하나" | `novelty-strategist` |
| "가설·실험설계·분석계획 점검·감사" | `research-methodologist` |
| "제출 전 적대적 자체검토 / 그림 QA" | `paper-critic` |
| "인용 검증 / 이 논문 진짜 있나" | `paper-critic` 또는 `literature-scout` — **둘 다 `agents/critic/scripts/verify_citations.py`를 실행**(눈으로 보지 않는다) |
| "정식 venue 리뷰 시뮬레이션" | `reviewer` |
| "발표자료/슬라이드/발제" | `presenter` |
| "로고·아이콘·브랜드·그림 미감" | `design` |
| "여러 단계를 어떤 순서로 엮을지 계획만" | `paper-orchestrator` (계획만) |
| **여러 단계를 엮는 요청** ("풀 파이프라인 / 제출 준비 / 분석→집필→그림→검수 / 그림만 다시 / critic 지적 반영") | **`paper-production-orchestrator` Skill** (메인 루프 실행) |

핵심: **단일 단계 요청은 해당 에이전트로 직행**하지만, **여러 단계를 엮는 요청은 오케스트레이터 스킬로 모여** 정해진 순서로 실행된다.

## (B) 산출물 계약 — 단계 간에 무엇을 넘기나

각 단계는 **다음 단계가 읽을 파일**을 산출물로 남긴다. 근거: `CLAUDE.md` *산출물 계약* 표, `docs/HARNESS.md` §2.

| 단계 | Writer | 산출물 | 다음이 읽음 |
|---|---|---|---|
| 분석·eval | `spatialpatho-analyst` | eval outputs + consolidated results summary | 집필·검수 |
| 집필+그림 | `manuscript-writer` | manuscript, figures dir | 검수·리뷰·발표 |
| 검증 게이트 | (커밋/공개 전) | headline AUC/AUPRC 재계산 → summary 대조 | 사람 |
| 리뷰 | `paper-critic` / `reviewer` | peer review note | 집필(수정) |
| 발표 | `presenter` | 슬라이드/발제 | 사람 |
| 상태 핸드오프 | (전원) | `HANDOFF.md`, `TODO.md`, `SESSION_LOG.md` | 다음 세션 |

이 계약 덕분에 **부분 재실행**이 가능하다 — "그림만 다시"는 figure 스크립트만, "critic 지적 반영"은 하류 집필 단계만 돌린다. 오케스트레이터의 실행 모드 분기가 이를 처리한다 (`SKILL.md` "실행 모드 분기").

## 스키마로 굳힌 계약

산출물 중 일부는 자연어가 아니라 **JSON 스키마**로 강제된다:

- `schemas/critic_report.schema.json` — Critic 리포트 구조
- `schemas/hypothesis.schema.json` — 가설 출력 구조. 모든 hypothesis 출력에 `claim_level`(반드시 `"hypothesis_only"`) + `critic_status`(`pass`/`caution`/`reject`) 필수 (`AGENTS.md` §4).
- 실험 `metrics.json` 필수필드: `auc·auprc·balanced_accuracy·n_train·n_val·model·embedding_model·commit_hash` (`AGENTS.md` §5).

## "지어내지 않기"를 계약에 박았다

산출물 계약 곳곳에 `<FILL>` 플레이스홀더가 있다(예: `<FILL: manuscript (미존재)>`). 이는 **아직 없는 것을 없다고 표시**하는 장치다. `CLAUDE.md`와 `SKILL.md` L10은 반복해서 **"headline 숫자·주장을 지어내지 말 것"** 을 명령한다. 즉 계약은 "무엇을 넘길지"뿐 아니라 **"없는 것을 있는 척 넘기지 마라"** 까지 규정한다. 이 원칙은 `CLAUDE.md` *완료의 정의* #6과 *Absolute Prohibitions*(발표자료 숫자를 기준값으로 쓰기 금지, 도구의 "못 찾겠다"를 통과로 처리 금지)로 강화된다.

→ 다음: [04_automated_review_and_governance.md](04_automated_review_and_governance.md)

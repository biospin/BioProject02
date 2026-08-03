# AI Scientist 설계 정리 — BioProject02 (SpatialPathoAgent)

이 디렉토리는 BioProject02가 **"AI를 연구 도구를 넘어 연구 과정 전반(문헌 검색·정리 → 가설 설정 → 실험 수행 → 논문 작성 → 검수)을 자동화하는 AI Scientist"** 로 어떻게 설계되었는지, 그리고 **여러 연구자가 그 위에서 협업할 수 있는 구조**를 어떻게 설계했는지를 사후 정리한 문서 모음이다.

> ⚠️ 이 디렉토리는 **설계 회고(retrospective)** 다. 새 시스템을 만드는 것이 아니라, 이미 리포지토리 곳곳(`CLAUDE.md`, `docs/HARNESS.md`, `.claude/agents/`, `.claude/skills/`, `agents/critic/`, `research/ai-agents/`)에 흩어져 구현·기록된 설계를 한 곳에서 지도로 읽을 수 있게 모았다. 모든 서술은 실제 파일을 근거로 하며, 근거 경로를 함께 적는다. 지어낸 숫자·주장은 없다.

---

## 한 줄 요약

이 프로젝트의 AI Scientist는 **완전 자율 발견 기계가 아니라, "역할이 나뉜 다중 에이전트 + 독립 Critic 게이트 + 사람 거버넌스"** 로 설계된 **거버넌스 중심(governance-centric) 연구 자동화 하네스**다. 자동화의 목표는 "사람을 빼는 것"이 아니라 **"사람이 판단해야 할 지점만 남기고 나머지 노동을 에이전트가 대신하게 하는 것"** 이다.

이 방향은 우연이 아니라 선행연구를 읽고 **의도적으로 선택된 포지셔닝**이다 (→ [06_design_lineage.md](06_design_lineage.md)).

---

## 설계의 4개 기둥

| # | 기둥 | 한 줄 | 상세 문서 |
|---|---|---|---|
| 1 | **2-레이어 아키텍처** | 도메인 **분석 파이프라인** 위에 **논문 생산 하네스**를 얹는다 | [01_two_layer_architecture.md](01_two_layer_architecture.md) |
| 2 | **다중 에이전트 명부** | 문헌·기획 / 분석 / 집필·그림 / 검수 / 발표를 역할별 에이전트로 분리 | [02_agents_and_roster.md](02_agents_and_roster.md) |
| 3 | **자연어 라우팅 + 산출물 계약** | "그림만 다시" 같은 자연어를 에이전트로 배정, 단계 간 산출물을 계약으로 고정 | [03_routing_and_artifact_contract.md](03_routing_and_artifact_contract.md) |
| 4 | **자동 검수 루프 + 거버넌스** | 사람이 병목 되지 않게 AI가 적대적 리뷰를 대신하고, 사람은 판단항목만 처리 | [04_automated_review_and_governance.md](04_automated_review_and_governance.md) |

그리고 이 자동화 하네스 **아래에서 사람 6명이 실제로 협업하는 구조**:

| 5 | **다연구자 협업 구조** | JIRA→OpenClaw→Slack→Claude Code, 1인1역할, owner≠reviewer 교차검수 | [05_human_collaboration.md](05_human_collaboration.md) |
| 6 | **설계 계보 (왜 이렇게 설계했나)** | AI Scientist·multi-agent science 선행연구를 읽고 governance-centric으로 포지셔닝 | [06_design_lineage.md](06_design_lineage.md) |

---

## AI Scientist가 수행하는 연구 과정 (요청하신 "연구 과정 전반")

요청서에 적힌 "문헌 검색/정리 → 가설 → 실험 → 논문 작성" 각 단계가 이 설계에서 어떤 에이전트/스크립트로 구현되어 있는지:

| 연구 단계 | 담당 (에이전트/스킬) | 근거 |
|---|---|---|
| 문헌 검색·정리·선행연구 | `literature-scout`, `novelty-strategist` | `.claude/agents/literature-scout.md`, `research/ai-agents/` |
| 가설 설정·실험 설계·통계 감사 | `research-methodologist` | `.claude/agents/research-methodologist.md` |
| 실험 수행·eval·통계 | `spatialpatho-analyst` (도메인 슬롯 = `agents/data\|embedding\|modeling\|therapeutic_evidence/`) | `.claude/agents/spatialpatho-analyst.md` |
| 논문 작성·그림 생성 | `manuscript-writer` (+ figure 스크립트) | `.claude/agents/manuscript-writer.md` |
| 자동 검수·인용 검증 | `paper-critic`, `agents/critic/` 7-point + 자동 리뷰 루프 + **CI 검증기** | `.claude/agents/paper-critic.md`, `agents/critic/auto_review_*.py`, `.github/workflows/critic-validators.yml` |
| 외부 리뷰 시뮬레이션 | `venue-reviewer` (검증 게이트 ① 통과 후, 격리) | `.claude/agents/venue-reviewer.md` |
| 발표자료 | `presenter` | `.claude/agents/presenter.md` |
| 전 과정 오케스트레이션 | `paper-production-orchestrator` (실행), `paper-orchestrator` (계획) | `.claude/skills/paper-production-orchestrator/SKILL.md` |

---

## 어디서부터 읽나

- **무엇이 최근 바뀌었나** → 바로 아래 "변경 이력".
- 이 설계를 **처음 보는 사람** → [01_two_layer_architecture.md](01_two_layer_architecture.md) 부터 순서대로.
- **"왜 완전 자율이 아니냐"** 가 궁금하면 → [06_design_lineage.md](06_design_lineage.md).
- **실제 운영 규칙·라우팅표 원본** → 리포 루트 `CLAUDE.md`의 *Agent routing & artifact contract* 절, `docs/HARNESS.md`.

---

## 변경 이력 (설계 자체가 바뀐 지점)

이 설계서는 **살아 있는 하네스**를 기술한다. 초판(`89848ed`, 2026-07-22) 이후 실제 설계가 바뀐 부분:

| 일자 | 변경 | 근거 | 반영 문서 |
|---|---|---|---|
| 2026-07-27 | **검증 게이트 ↔ 리뷰 순서 스왑** + 게이트 1개 → **2개**(① 커밋 전 결과검증 / ② 공개 전 패키지검증). *"검증 안 된 숫자를 리뷰에 보내지 않는다"* | BIOP02-103 · `374345f` · `SKILL.md` 7/8/8.5 | [01](01_two_layer_architecture.md), [03](03_routing_and_artifact_contract.md) |
| 2026-07-27 | **`reviewer`(전역) → `venue-reviewer`(프로젝트 로컬) 실체화.** 내부 검수(`paper-critic`)와 외부 referee 시뮬레이션을 **격리** | BIOP02-103 · `.claude/agents/venue-reviewer.md` | [01](01_two_layer_architecture.md), [02](02_agents_and_roster.md), [03](03_routing_and_artifact_contract.md) |
| 2026-07-27 | 바이오 sub-check 담당 = **"owner 아닌 사람" 케이스별**(구 "sjpark/jhans 고정 분담"은 폐기 — 문자대로 따르면 Owner≠Reviewer 위반) | BIOP02-59 · `bea26f6` | [05](05_human_collaboration.md) |
| 2026-07-27 | 금지 항목 신설 — **티켓·파일을 열지 않고 상태 단정 금지**(JIRA 조회 시 `comment` 필수) | `9963b08` | [04](04_automated_review_and_governance.md) |
| 2026-08-03 | **CI 검증 레이어 신설** — PR/push에서 결정론 검증기 3종 blocking 실행. 검수가 **3층**(CI 기계 → AI 적대 → 사람 게이트)이 됨 | BIOP02-106/107 · `.github/workflows/critic-validators.yml` | [04](04_automated_review_and_governance.md) |

**미해결로 남은 것 (설계서가 기록하는 미완성 지점):**
- 🔴 **검증 게이트 ①의 실행 명령이 없다** — BIOP02용 결정론 재계산 스크립트가 리포에 부재. `auto_review_gate.py`는 문서 규칙 검사이지 수치 재계산이 아니다. 채워질 때까지 사람이 수동 대조.
- 🔴 **`auto_review_config.json`의 `ai_review.agents`가 아직 `["paper-critic", "reviewer"]`** — `SKILL.md`는 5단계를 `paper-critic` 단독으로 고쳤는데 config가 따라오지 않았다. `enabled=false`(dry-run)라 실害는 없으나 **활성화 전 정리 필요**.
- 🔴 **게이트 ① 이후의 "수정"에 권한 제약이 없다** — `manuscript-writer`가 `Write`를 보유해 리뷰 반영 중 검증된 숫자를 다시 쓸 수 있고, 방어는 게이트 ②의 **사후 재대조**뿐이다. 같은 규율이 `paper-critic`에는 **도구 수준으로**(쓰기 권한 없음) 걸려 있어, 하네스 안에 *권한으로 막은 곳*과 *말로만 막은 곳*이 섞여 있다. 부수로 `venue-reviewer`는 `tools:` **미선언 → 전체 도구 상속**이라 격리가 프롬프트로만 강제된다. → [01](01_two_layer_architecture.md), [02](02_agents_and_roster.md), [03](03_routing_and_artifact_contract.md)
- 🔴 **판정 어휘에 "더 해도 pass가 안 되는 것"을 적을 칸이 없다** — `critic_status`(`pass·caution·reject`)에 *"현재 데이터로는 식별 불가"* 가 없어 그런 항목이 `caution`으로 뭉뚱그려진다. BIOP02-75가 이 빈칸 때문에 **티켓 성공 기준 자체를 재정의**해 우회했다. → [04](04_automated_review_and_governance.md)
- 🔴 **비판 자체를 검증하는 층이 없다** — 루프가 비판을 생산(③)한 뒤 곧바로 확인 주체 배정(④)으로 넘어가, **Critic의 산출물만은 Critic을 거치지 않는다.** 2026-07-27 하루에 Critic 코멘트 4건이 작성자 본인에게 사후 정정된 것이 그 비용이다. → [04](04_automated_review_and_governance.md)

> ⚠️ 위 3건은 **관찰된 갭이지 채택된 설계 변경이 아니다.** 따라서 위 "변경 이력"에는 넣지 않았다. 셋 다 고치려면 `.claude/agents/*`·`schemas/*`·`auto_review_config.json`을 건드려야 하고, 그것은 **Critic이 자기 검수 기준을 스스로 정하는 일**이라 `CLAUDE.md`의 `❌ anti-self-reference`에 걸린다 → **Leader 승인 사안.** 특히 판정 어휘는 기존 `critic_report.json`의 유효성에 영향을 주므로 **BIOP02-75 최종 서명 이후**가 맞다.

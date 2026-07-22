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
| 자동 검수·인용 검증 | `paper-critic`, `reviewer`, `agents/critic/` 7-point + 자동 리뷰 루프 | `.claude/agents/paper-critic.md`, `agents/critic/auto_review_*.py` |
| 발표자료 | `presenter` | `.claude/agents/presenter.md` |
| 전 과정 오케스트레이션 | `paper-production-orchestrator` (실행), `paper-orchestrator` (계획) | `.claude/skills/paper-production-orchestrator/SKILL.md` |

---

## 어디서부터 읽나

- 이 설계를 **처음 보는 사람** → [01_two_layer_architecture.md](01_two_layer_architecture.md) 부터 순서대로.
- **"왜 완전 자율이 아니냐"** 가 궁금하면 → [06_design_lineage.md](06_design_lineage.md).
- **실제 운영 규칙·라우팅표 원본** → 리포 루트 `CLAUDE.md`의 *Agent routing & artifact contract* 절, `docs/HARNESS.md`.

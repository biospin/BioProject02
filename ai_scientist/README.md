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

## 이 하네스의 계보 — 어디서 왔고 어디로 복제됐나

이 설계는 처음부터 **재사용 스캐폴드**로 만들어졌고, 실제로 분야가 다른 두 프로젝트에 얹혔다.

```
원본(upstream) paper-production-harness   ← Designed by Ka-Kyung Kim, CC BY 4.0
        ├─▶ BioProject01 (velocity/전사체)
        └─▶ BioProject02 (병리/H&E)        ← 이 설계서가 기술하는 인스턴스
```

3자 상세 대조는 `docs/HARNESS_COMPARISON.md`에 있다(공용 자산 — 특정 프로젝트 소유가 아님).

> **"복사"가 아니라 "벤치마킹 이식"이라는 구분이 중요하다.** 예컨대 검수 하네스(`evals/validation_harness/`)는 BIOP01의 `reproducibility_pilot` **골격만** 가져오고(러너·control↔mutated 델타), **mutation과 detector는 BIOP02 도메인으로 새로 썼다** — 남의 도메인 판정 기준을 그대로 베끼지 않는다.
> 같은 원칙이 자동 리뷰 루프에도 있다: **코드는 project-agnostic**, 프로젝트별 값은 **전부 config로**. 그래서 다른 프로젝트는 *스크립트 복사 + 자기 config*만으로 작동한다.

## 변경 이력 (설계 자체가 바뀐 지점)

이 설계서는 **살아 있는 하네스**를 기술한다. 초판(`89848ed`, 2026-07-22) 이후 실제 설계가 바뀐 부분:

| 일자 | 변경 | 근거 | 반영 문서 |
|---|---|---|---|
| 2026-07-27 | **검증 게이트 ↔ 리뷰 순서 스왑** + 게이트 1개 → **2개**(① 커밋 전 결과검증 / ② 공개 전 패키지검증). *"검증 안 된 숫자를 리뷰에 보내지 않는다"* | BIOP02-103 · `374345f` · `SKILL.md` 7/8/8.5 | [01](01_two_layer_architecture.md), [03](03_routing_and_artifact_contract.md) |
| 2026-07-27 | **`reviewer`(전역) → `venue-reviewer`(프로젝트 로컬) 실체화.** 내부 검수(`paper-critic`)와 외부 referee 시뮬레이션을 **격리** | BIOP02-103 · `.claude/agents/venue-reviewer.md` | [01](01_two_layer_architecture.md), [02](02_agents_and_roster.md), [03](03_routing_and_artifact_contract.md) |
| 2026-07-27 | 바이오 sub-check 담당 = **"owner 아닌 사람" 케이스별**(구 "sjpark/jhans 고정 분담"은 폐기 — 문자대로 따르면 Owner≠Reviewer 위반) | BIOP02-59 · `bea26f6` | [05](05_human_collaboration.md) |
| 2026-07-27 | 금지 항목 신설 — **티켓·파일을 열지 않고 상태 단정 금지**(JIRA 조회 시 `comment` 필수) | `9963b08` | [04](04_automated_review_and_governance.md) |
| 2026-08-03 | **CI 검증 레이어 신설** — PR/push에서 결정론 검증기 3종 blocking 실행. 검수가 **3층**(CI 기계 → AI 적대 → 사람 게이트)이 됨 | BIOP02-106/107 · `.github/workflows/critic-validators.yml` | [04](04_automated_review_and_governance.md) |

### 2026-08-04 — 스킬(`SKILL.md`) 대조 동기화

설계가 바뀐 게 아니라 **설계서가 스킬을 덜 기술하고 있었다.** 대조 결과 누락 8건을 보강하고 낡은 서술 1건을 정정했다(설계 변경이 아니므로 위 표에는 넣지 않는다).

| 보강 | 어디에 |
|---|---|
| 실행 모드 분기 3단계 + ⭐ **offline mock 확인 → "데모" 명시** | [03](03_routing_and_artifact_contract.md) |
| **품질 기준선** — 숫자는 결과 파일에서만(메모리 재유도 금지) · 그림 하드코딩 금지 · 95% CI + paired test · 번호는 첫 언급 순 · **weak ≠ zero** | [03](03_routing_and_artifact_contract.md) |
| **실행·보고 계약** — 멈춤 조건(재시도 1회 후 보고 등) · 마무리 보고 `done/in-progress/blocked` · **부분 재실행 시 안 건드린 단계도 명시** | [03](03_routing_and_artifact_contract.md) |
| `required_followups` — 사람에게 넘기는 것은 **노동이 아니라 판단** | [04](04_automated_review_and_governance.md) |
| 🔴 **정정**: "집필-단계 산출물이 아직 없다" → 원고는 **존재**(`manuscript/sections/` 5섹션 + Discussion 한계) | [01](01_two_layer_architecture.md) |

### 2026-08-20 — 하네스 기법 전수 대조

git으로 하네스 자산을 전수 조사해 **설계서에 반영 안 된 기법 11건**을 찾아 보강했다(설계 변경이 아니므로 위 표에 넣지 않는다).

| 보강 | 어디에 |
|---|---|
| **CI 검증기 3종 → 7종** (게이트 mutation · split 누수 · 공허통과 회귀 · 국영문 정합 추가) | [04](04_automated_review_and_governance.md) |
| ⭐ **검증기를 검증한다** — mutation 하네스(*"실수를 심으면 게이트가 잡는가"*, control↔mutated 델타) + **공허통과(vacuous pass) 회귀** | [04](04_automated_review_and_governance.md) |
| **검증기가 스스로 터지지 않게** — `$ref` 지연 해석이라 늦게 터지는 실패를 회귀로 고정 | [04](04_automated_review_and_governance.md) |
| **판정하지 않는 검증기** — 드리프트 체커는 옳고 그름을 고르지 않고 *어긋남만* 보고. v1이 **범위 밖을 스스로 명시**해 v2가 이어받음 | [04](04_automated_review_and_governance.md) |
| **픽스처 자기충족 회피** — 픽스처 작성자 = 채점기 작성자면 통과가 자기충족 → 실제 산출물로 돌리되 **판정은 사람**(Owner≠Reviewer) | [04](04_automated_review_and_governance.md) |
| ⭐ **메타-학습 루프** — 사고 → `PITFALLS_REGISTRY` 등재 → **재발방지 장치 필수**(규칙 ②) → 금지조항/스크립트/CI | [04](04_automated_review_and_governance.md) |
| **`memory/` 층** — 핸드오프(며칠~몇 주)와 수명이 다른 *"다시 배우지 않아야 할 사실"* + 로그 유실 사고 | [05](05_human_collaboration.md) |
| **하네스 계보** — 원본(CC BY 4.0) → BIOP01·BIOP02, *"복사가 아니라 벤치마킹 이식"* | 위 §계보 |
| ✅ **닫힘**: `auto_review_config.json` 정렬(Leader 승인) | [04](04_automated_review_and_governance.md) |

**미해결로 남은 것 (설계서가 기록하는 미완성 지점):**
- 🔴 **검증 게이트 ①의 실행 명령이 없다** — BIOP02용 결정론 재계산 스크립트가 리포에 부재. `auto_review_gate.py`는 문서 규칙 검사이지 수치 재계산이 아니다. 채워질 때까지 사람이 수동 대조.
- 🔴 **게이트 ① 이후의 "수정"에 권한 제약이 없다** — `manuscript-writer`가 `Write`를 보유해 리뷰 반영 중 검증된 숫자를 다시 쓸 수 있고, 방어는 게이트 ②의 **사후 재대조**뿐이다. 같은 규율이 `paper-critic`에는 **도구 수준으로**(쓰기 권한 없음) 걸려 있어, 하네스 안에 *권한으로 막은 곳*과 *말로만 막은 곳*이 섞여 있다. 부수로 `venue-reviewer`는 `tools:` **미선언 → 전체 도구 상속**이라 격리가 프롬프트로만 강제된다. → [01](01_two_layer_architecture.md), [02](02_agents_and_roster.md), [03](03_routing_and_artifact_contract.md)
- 🔴 **판정 어휘에 "더 해도 pass가 안 되는 것"을 적을 칸이 없다** — `critic_status`(`pass·caution·reject`)에 *"현재 데이터로는 식별 불가"* 가 없어 그런 항목이 `caution`으로 뭉뚱그려진다. BIOP02-75가 이 빈칸 때문에 **티켓 성공 기준 자체를 재정의**해 우회했다. → [04](04_automated_review_and_governance.md)
- 🔴 **비판 자체를 검증하는 층이 없다** — 루프가 비판을 생산(③)한 뒤 곧바로 확인 주체 배정(④)으로 넘어가, **Critic의 산출물만은 Critic을 거치지 않는다.** 2026-07-27 하루에 Critic 코멘트 4건이 작성자 본인에게 사후 정정된 것이 그 비용이다. → [04](04_automated_review_and_governance.md)
- 🔴 **`SKILL.md` 자체가 현실보다 뒤처져 있다** — L10 *"집필 이전 단계 산출물이 아직 없다"* · L18 `<FILL: docs/manuscript/preprint.md (미존재)>`. 실제로는 `manuscript/sections/`에 5개 섹션이 있고 Discussion 한계까지 작성됐다. **`<FILL`은 스스로 갱신되지 않는다** — 남긴 쪽이 지우는 책임도 진다. (이 설계서는 감추지 않고 표시만 했고, `SKILL.md` 수정은 하네스 소유자 몫으로 남긴다.)

> ⚠️ 위 항목들은 **관찰된 갭이지 채택된 설계 변경이 아니다.** 따라서 위 "변경 이력"에는 넣지 않았다. 셋 다 고치려면 `.claude/agents/*`·`schemas/*`·`auto_review_config.json`을 건드려야 하고, 그것은 **Critic이 자기 검수 기준을 스스로 정하는 일**이라 `CLAUDE.md`의 `❌ anti-self-reference`에 걸린다 → **Leader 승인 사안.** 특히 판정 어휘는 기존 `critic_report.json`의 유효성에 영향을 주므로 **BIOP02-75 최종 서명 이후**가 맞다.

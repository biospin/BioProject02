# 05 — 다연구자 협업 구조

요청의 두 번째 목적: **"여러 연구자들과 협업할 수 있는 구조."** AI Scientist 하네스는 진공에서 돌지 않는다 — 사람 6명이 각자의 컨테이너·역할·검수 짝을 갖고 그 위에서 협업하도록 설계됐다.

## (A) 1인 1역할 — 사람 역할과 에이전트 벤치의 대응

각 연구자는 파이프라인의 한 역할을 소유한다. 근거: `CLAUDE.md` *Team & Roles*, `AGENTS.md` §1.

| 연구자 | 역할 | 대응 에이전트 벤치 |
|---|---|---|
| kkkim (김가경) | **Project Leader** + Embedding Agent | `agents/embedding/` → `spatialpatho-analyst` |
| braveji (지용기) | Orchestrator + **Scientific Critic 총괄** | `agents/critic/` → `paper-critic`, 오케스트레이터 |
| jamie (류재면) | Data Agent (manifest·label·split) | `agents/data/` |
| sjpark (박세진) | Modeling Agent (MLP·attention MIL) + 바이오 sub-check | `agents/modeling/` |
| jhans (서정한) | Therapeutic Evidence Agent (DepMap/GDSC) | `agents/therapeutic_evidence/` |
| gglee (이건규) | 재편입(2026-07-07), 역할 재배정 협의 중 | — |

**분담 원칙:** Leader=kkkim, Critic 총괄=braveji. 바이오 판단(7-point #4/#5)은 sjpark/jhans에 분담.

## (B) 작업 흐름: JIRA → OpenClaw → Slack → Claude Code

사람과 AI를 잇는 실제 파이프라인 (`CLAUDE.md` *Workflow: OpenClaw → Slack → Claude Code/Codex*):

```
JIRA (BIOP02)  ── 담당자에게 이슈 할당
      │
      ▼
OpenClaw bot (담당자별, 자동 모니터링)
  - 본인 할당 이슈를 주기적으로 확인
  - 새 할당/기한 임박/상태 변경 감지 → Slack 알림
      │
      ▼  Slack DM 또는 #biop02-dev
연구자 (담당자)
  - 알림 확인 → Claude Code/Codex로 실제 작업 수행
  - 완료 후 git commit (BIOP02-번호 포함) → PR
      │
      ▼
JIRA Smart Commits 자동 연동 (이슈 상태 자동 업데이트)
```

역할 구분: **OpenClaw** = JIRA 모니터링 + Slack 알림 전용(코드 안 씀). **Claude Code/Codex** = 연구자가 직접 구동하는 코딩 도구(실제 구현). CLI 선택은 각자 자유이되 **출력 스키마는 통일**(`CLAUDE.md` Governance).

## (C) 교차검수: owner ≠ reviewer

협업 품질의 핵심 규칙. **자기 결과를 자기가 critic 하지 않는다** (`AGENTS.md` §4, `CLAUDE.md` *Critic Cross-Review Rules*).

| 작성자 | Critic 담당 |
|---|---|
| sjpark (모델링) | kkkim |
| kkkim (임베딩) | jamie |
| jamie (데이터/split) | braveji |
| jhans (TE) | braveji 총괄 + 바이오 sub-check는 **owner가 아닌 사람**(아래 선정규칙) |

이 매핑은 **자동 리뷰 루프에도 그대로 주입**된다 — `auto_review_config.json`의 `cross_review_map`(`sjpark→kkkim, kkkim→jamie, jamie→braveji, jhans→braveji`)이 큐 drain 시 리뷰어를 자동 배정한다([04](04_automated_review_and_governance.md) 참조). 즉 사람 협업 규칙과 AI 자동화가 같은 규칙을 공유한다.

### 바이오 sub-check(#4/#5) 선정규칙 — **"고정 배정"이 아니다** (2026-07-27 정정)

이 규칙은 실제 사고를 겪고 다시 쓰였다. 우선순위대로 적용하며 **1번이 2번을 이긴다**:

1. **해당 산출물·검증 대상 rule의 owner가 아닌 사람** (제약이지 권고가 아님)
2. 도메인 기본 후보 = **sjpark / jhans** — **후보 목록이고 고정 배정이 아니다**
3. 후보가 전부 owner면 → **Leader가 다른 멤버를 케이스별 지정**(예: jamie)

> ⚠️ **실사례 BIOP02-59:** sjpark = **산출물 owner**, jhans = **검증 대상 rule owner** → **기본 후보 둘 다 리뷰 불가**였다. 구 문구 *"sub-check는 sjpark/jhans에 분담"* 을 문자대로 따르면 **Owner≠Reviewer를 위반**한다. Leader가 jamie를 지정한 것이 규율상 정답이었고, **문서가 현실보다 뒤처져 있었다.**
>
> 교훈: 담당이 헷갈리면 역할표가 아니라 **"이 산출물을 누가 만들었나"** 를 먼저 본다.

## (D) 공유 인프라 규약 — 협업이 깨지지 않게

여러 연구자가 **별도 Docker 컨테이너**에서 일하기 때문에 생기는 함정을 규약으로 막았다 (`CLAUDE.md`·`AGENTS.md` 공유 데이터 경로 규칙):

- `/home/<user>/`는 컨테이너 로컬 → **다른 계정에서 안 보임**. 컨테이너 간 공유는 `/workspace`뿐.
- **공유 데이터(임베딩·manifest·split·label)는 반드시 `/workspace/data/cache/biop02/`에 실파일로.** manifest 경로는 `/workspace/...` 절대경로(개인 홈 경로 금지).
- 폴더 네이밍 규약(`<model>_<version>/`, `embedding_manifest_<model>.csv`, `split_policy_v<n>.csv`).
- 공유 폴더는 `chmod 2775`(setgid) + `chgrp project`로 그룹 상속.
- GPU 슬롯은 `#biop02-alerts`에 예약 후 사용(A6000 3장).

## (E) 상태 핸드오프 — 세션·사람 간 인수인계

모든 참여자가 매 세션 남기는 3종 상태 파일(`CLAUDE.md` *완료의 정의* #7):
- `HANDOFF.md` — "다음이 이어받을 상태"
- `SESSION_LOG.md` — "그날 한 일의 날짜별 기록"(매 세션 필수, HANDOFF와 같은 턴에 함께 기록)
- `TODO.md` — 남은 일

이 파일들은 git 미추적(개인 작업일지)이고, durability는 **공유 볼륨 백업**으로 확보한다. 팀 공유 영구 기록은 **JIRA·Confluence·PR 본문·`experiments/registry/`** 가 담당.

### 한 층 더 — 세션을 넘어 지속되는 사실 (`memory/`)

핸드오프 3종이 **"이 프로젝트의 지금 상태"** 를 넘긴다면, `memory/`는 **"세션이 바뀌어도 다시 배우지 않아야 할 사실"** 을 넘긴다. 둘은 수명이 다르다.

| | 수명 | 예 |
|---|---|---|
| `HANDOFF` / `SESSION_LOG` / `TODO` | 며칠~몇 주 | 지금 막힌 것, 어제 한 일 |
| `memory/` | 프로젝트 내내 | 사람의 작업 방식·선호, 반복 확인된 운영 사실, 외부 자원 위치 |

한 항목 = 한 파일 = 한 사실이고, 색인(`MEMORY.md`)이 있어 다음 세션이 **먼저 읽는다.**
실제로 이 프로젝트 메모리에는 *"상태 판단 전 반드시 fetch/pull"*, *"로컬에서 막힌 재계산은 GPU 머신 공유 경로에서 가능"* 처럼 **반복해서 대가를 치른 사실**이 들어 있다.

> ⚠️ **메모리도 낡는다.** 기록 시점의 사실이므로, 파일·명령·플래그를 지목하는 항목은 **쓰기 전에 아직 존재하는지 확인**한다 — 이 설계서가 반복하는 *"열어서 확인한다"* 가 여기에도 적용된다.

### 이 층의 실패는 조용하고 되돌릴 수 없다

핸드오프 3종은 **개인 작업일지라 git 미추적**이다. 그래서 로컬 디스크와 함께 사라진다 — 이 프로젝트는 실제로 **한 달치 세션 로그를 잃었고**, 그 구간은 **트래커 코멘트가 유일한 기록**으로 남았다.

그 사고가 규칙 둘을 낳았다:
1. **공유 볼륨에 백업**한다(개인 홈은 컨테이너와 함께 사라질 수 있다)
2. 상태를 인용할 땐 **기억이 아니라** `파일:줄`·커밋·코멘트 id

## 협업 채널

| 채널 | 용도 |
|---|---|
| `#biop02-general` | 공지·전체 공유 |
| `#biop02-dev` | OpenClaw 알림 + 작업 진행 공유 |
| `#biop02-experiments` | 실험 결과 공유 (**Critic pass 후만**) |
| `#biop02-alerts` | GPU 슬롯 예약·서버 장애 |

주간 동기화: 매주 금요일 60분(Leader kkkim, 회의록 braveji). 진행 공유는 Confluence(Space VC)·JIRA(BIOP02).

→ 다음: [06_design_lineage.md](06_design_lineage.md)

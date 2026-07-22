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
| jhans (TE) | braveji 총괄 (바이오 sub-check: sjpark) |

이 매핑은 **자동 리뷰 루프에도 그대로 주입**된다 — `auto_review_config.json`의 `cross_review_map`(`sjpark→kkkim, kkkim→jamie, jamie→braveji, jhans→braveji`)이 큐 drain 시 리뷰어를 자동 배정한다([04](04_automated_review_and_governance.md) 참조). 즉 사람 협업 규칙과 AI 자동화가 같은 규칙을 공유한다.

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

이 파일들은 git 미추적(개인 작업일지)이고, durability는 `/workspace/kkkim_private/session_logs/` 백업으로 확보한다. 팀 공유 영구 기록은 **JIRA·Confluence·PR 본문·`experiments/registry/`** 가 담당.

## 협업 채널

| 채널 | 용도 |
|---|---|
| `#biop02-general` | 공지·전체 공유 |
| `#biop02-dev` | OpenClaw 알림 + 작업 진행 공유 |
| `#biop02-experiments` | 실험 결과 공유 (**Critic pass 후만**) |
| `#biop02-alerts` | GPU 슬롯 예약·서버 장애 |

주간 동기화: 매주 금요일 60분(Leader kkkim, 회의록 braveji). 진행 공유는 Confluence(Space VC)·JIRA(BIOP02).

→ 다음: [06_design_lineage.md](06_design_lineage.md)

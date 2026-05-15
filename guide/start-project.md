# Git 클론 & 브랜치 생성 & Confluence-JIRA 연동 가이드

> 참고: [CLAUDE.md](../CLAUDE.md) — Remote: `git@github.com:biospin/BioProject02.git`

---

## 1. Git 프로젝트 클론

```bash
# SSH 방식 (권장 — 서버 SSH key와 동일하게 설정돼 있으면 그대로 동작)
git clone git@github.com:biospin/BioProject02.git

# HTTPS 방식 (SSH key 미설정 시)
git clone https://github.com/biospin/BioProject02.git

cd BioProject02
```

---

## 2. 브랜치 명명 규칙

JIRA project key가 `BIOP02`이므로, **JIRA 이슈 번호를 브랜치명에 포함**시키면 Smart Commits으로 자동 연동됩니다.

```
<type>/<BIOP02-이슈번호>-<username>-<짧은설명>
```

예시:
```bash
feat/BIOP02-1-kkkim-embedding-setup
feat/BIOP02-2-jamie-tcga-manifest
feat/BIOP02-3-sjpark-mlp-baseline
feat/BIOP02-4-gglee-critic-checklist
feat/BIOP02-5-braveji-agents-md
```

타입 prefix 규칙:

| prefix | 용도 |
|---|---|
| `feat/` | 새 기능 (코드/스크립트) |
| `docs/` | 문서, schema, checklist |
| `fix/` | 버그 수정 |
| `infra/` | setup.sh, Dockerfile, gpu.lock 등 |

---

## 3. 브랜치 생성 & Push

```bash
# 1. 최신 main 받기
git pull origin main

# 2. 본인 브랜치 생성
git checkout -b feat/BIOP02-<번호>-<username>-<설명>

# 3. 작업 후 push
git push -u origin feat/BIOP02-<번호>-<username>-<설명>
```

---

## 4. main 브랜치 보호 설정 (braveji 담당 — Sprint 0 closeout 5/22 이후)

GitHub → Repository Settings → Branches → Add rule:
- Branch name pattern: `main`
- **Require a pull request before merging** 체크
- **Require approvals: 1** 설정

CODEOWNERS 파일 (`/.github/CODEOWNERS`):

```
/agents/data/                 @biospin/JamieLyu
/agents/embedding/            @biospin/kakyungkim
/agents/modeling/             @biospin/sezinie000
/agents/therapeutic_evidence/ @biospin/JeonghanSeo
/agents/critic/               @biospin/Geongyu
/schemas/                     @biospin/braveji18
```

---

## 5. Confluence ↔ JIRA 연동

| | |
|---|---|
| Confluence Space key | **VC** |
| JIRA Project key | **BIOP02** |
| Confluence 작업 위치 | 프로젝트 진행-AI전용 > 프로젝트#02 |

### Step 1 — Confluence에서 JIRA 프로젝트 연결

1. Confluence → **Space Settings** (VC 스페이스)
2. 좌측 메뉴 → **Integrations** → **JIRA**
3. **Link a JIRA project** → `BIOP02` 선택 → Save

### Step 2 — Confluence 페이지에 JIRA 이슈 목록 삽입

페이지 편집 중 `/jira` 입력 → **JIRA Issues** 매크로:
- Project: `BIOP02`
- Sprint: 현재 sprint
- Assignee: 본인

Sprint review 페이지, 회의록에 이슈 목록이 자동 렌더링됩니다.

### Step 3 — Smart Commits (Git commit → JIRA 자동 업데이트)

commit message에 JIRA 이슈 번호를 포함하면 JIRA 이슈가 자동으로 업데이트됩니다:

```bash
# 이슈 상태 전환
git commit -m "BIOP02-1 #in-progress tile_wsi.py 256x256 tiling 구현"

# 이슈 완료 처리
git commit -m "BIOP02-1 #done tile_wsi.py Otsu mask + per-patient cap 5000 완성"

# 코멘트 추가
git commit -m "BIOP02-1 #comment 1 slide pilot: 8.3min, 4821 patches, 19MB"
```

Smart Commits 활성화: JIRA → **Project Settings** → **GitHub integration** (GitHub for Jira 앱 설치 필요).

---

## 6. Confluence 페이지 구조 권장안

```
프로젝트#02/
├── 회의록/
│   ├── 2026-05-22 Sprint 0 closeout
│   └── 2026-05-29 ...
├── Sprint Review/
│   ├── Sprint 0 Retro
│   └── ...
└── AGENTS.md (v0.2)
```

---

## 7. Atlassian MCP — Claude Code에서 Confluence·JIRA 직접 조작

Atlassian 공식 MCP 서버를 설정하면 Claude Code가 Confluence 페이지 작성·수정, JIRA 이슈 생성·조회를 대화 중에 직접 실행할 수 있습니다.

### Step 1 — Atlassian API Token 발급

1. https://id.atlassian.com/manage-profile/security/api-tokens 접속
2. **Create API token** → Label: `claude-mcp-biop02` → Create
3. 토큰 복사 후 password manager에 저장 (재조회 불가)

### Step 2 — MCP 서버 설정 (`~/.claude/settings.json`)

각자 본인 계정 정보로 **글로벌 설정**에 추가합니다 (프로젝트 repo에 커밋하지 말 것 — 토큰 유출 위험).

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@atlassian/mcp-atlassian", "--transport", "stdio"],
      "env": {
        "ATLASSIAN_URL": "https://biospin-ai.atlassian.net",
        "ATLASSIAN_EMAIL": "<본인 atlassian 이메일>",
        "ATLASSIAN_TOKEN": "<위에서 발급한 API token>"
      }
    }
  }
}
```

팀원별 `ATLASSIAN_EMAIL` (CLAUDE.md 기준):

| Username | ATLASSIAN_EMAIL |
|---|---|
| jamie | jamie.orangecounty@gmail.com |
| kkkim | kakyung.kim@gmail.com |
| gglee | rjsrb365@gmail.com |
| sjpark | sezinie000@gmail.com |
| braveji | biospinleader@gmail.com |
| jhans | phoenicx16@gmail.com |

### Step 3 — 동작 확인

Claude Code 재시작 후 대화에서 바로 사용:

```
# Confluence 페이지 조회
"VC 스페이스의 프로젝트#02 > 회의록 페이지 목록 보여줘"

# JIRA 이슈 생성
"BIOP02 프로젝트에 Sprint 0 이슈 만들어줘 — 제목: tile_wsi.py 구현, 담당자: kkkim"

# JIRA 이슈 조회
"BIOP02에서 현재 In Progress 이슈 목록 보여줘"
```

### 주의사항

- `~/.claude/settings.json`은 git으로 관리하지 않습니다. API token이 포함되어 있어 절대 커밋 금지.
- 프로젝트 레벨 `.claude/settings.json`에는 MCP env 토큰을 넣지 말 것 — 대신 환경변수로 주입:

```bash
# .env.local (gitignore에 포함)
ATLASSIAN_TOKEN=your_token_here
```

---

## 8. OpenClaw — JIRA 모니터링 & Slack 작업 알림

OpenClaw는 **JIRA를 자동 모니터링하여 담당자에게 할당된 작업을 Slack으로 알려주는 봇**입니다. 코드 작업 자체는 각 팀원이 Claude Code 또는 Codex로 직접 수행합니다.

### 전체 워크플로우

```
JIRA BIOP02 (이슈 할당)
        │
        ▼  주기적 폴링 또는 Webhook
  OpenClaw bot (담당자별)
  - 본인 할당 이슈 감지 (신규 / 기한 임박 / 상태 변경)
  - Claude API로 이슈 내용 요약 + 작업 안내 메시지 생성
        │
        ▼  Slack DM 또는 #biop02-dev
  팀원 (담당자)
  - 알림 확인 후 Claude Code / Codex로 실제 작업 수행
  - git commit (BIOP02-번호 포함) → push → PR
        │
        ▼
  JIRA Smart Commits (이슈 상태 자동 업데이트)
```

**역할 구분:**

| 도구 | 역할 |
|---|---|
| **OpenClaw bot** | JIRA 모니터링 + Slack 알림 전용. 코드 작성 안 함. |
| **Claude Code / Codex** | 팀원이 직접 구동하는 코딩 도구. 실제 구현 담당. |

### 팀원별 OpenClaw Slack App

| Username | Slack App |
|---|---|
| jamie | jamie-openclaw-bot |
| kkkim | kakyung.kim-openclaw-bot |
| gglee | ggyu-claw |
| sjpark | sezinie-openclaw-bot |
| braveji | yong-openclaw-bot |
| jhans | (미설정 — Sprint 1 전 braveji 생성 예정) |

---

### Step 1 — Slack App 생성 (braveji 담당, 1회만)

1. https://api.slack.com/apps → **Create New App** → From scratch
2. App Name: 팀원별 bot name (예: `kkkim-openclaw-bot`) → 워크스페이스 선택
3. **OAuth & Permissions** → Bot Token Scopes 추가:
   - `chat:write` — 메시지 전송
   - `im:write` — DM 전송
   - `channels:read` — 채널 목록 조회
4. **Install to Workspace** → Bot Token (`xoxb-...`) 복사
5. 팀원 각자에게 본인 봇의 `SLACK_BOT_TOKEN` 전달

### Step 2 — 환경변수 설정 (서버에서 담당자별)

서버(`/workspace/agents/<role>/`) 또는 로컬 머신에서:

```bash
# ~/.bashrc 또는 ~/.zshrc
export SLACK_BOT_TOKEN="xoxb-..."          # 본인 OpenClaw Slack Bot Token
export SLACK_SIGNING_SECRET="..."           # Slack App → Basic Information
export ANTHROPIC_API_KEY="sk-ant-..."      # Claude API key (알림 메시지 생성용)
export ATLASSIAN_URL="https://<domain>.atlassian.net"
export ATLASSIAN_EMAIL="<본인 atlassian 이메일>"
export ATLASSIAN_TOKEN="<Atlassian API token>"  # §7에서 발급
export JIRA_PROJECT_KEY="BIOP02"
export JIRA_ASSIGNEE="<본인 JIRA username>"
export SLACK_NOTIFY_CHANNEL="<본인 Slack user ID 또는 #biop02-dev>"
```

### Step 3 — OpenClaw 알림 예시

JIRA에서 이슈가 할당되거나 기한이 임박하면 OpenClaw가 Slack으로 자동 전송:

```
[kkkim-openclaw-bot] 📋 할당된 작업 알림 — 2026-05-18

• BIOP02-7 | tile_wsi.py 구현 | 기한: 2026-05-22 | 상태: To Do
  → agents/embedding/scripts/tile_wsi.py 작성
  → 256×256 @ 20×, Otsu mask, per-patient cap 5000 (tile_config.yaml 참고)

• BIOP02-8 | 1 slide UNI pilot | 기한: 2026-05-22 | 상태: To Do
  → HF 승인 후 extract_uni.py 실행, wall-clock + GPU memory 측정
  → 결과: outputs/pilot/PILOT_REPORT.md

💡 Claude Code로 작업 시작:
   cd /workspace/agents/embedding && claude
```

### Step 4 — 팀원의 실제 작업 흐름

OpenClaw 알림 수신 후:

```bash
# 1. 서버 접속
ssh -p 2202 kkkim@61.109.239.220

# 2. 브랜치 생성
git checkout -b feat/BIOP02-7-kkkim-tile-wsi

# 3. Claude Code 또는 Codex로 작업
claude        # Claude Code
# 또는
codex         # OpenAI Codex CLI

# 4. 작업 완료 후 commit (JIRA Smart Commits 연동)
git commit -m "BIOP02-7 #done tile_wsi.py Otsu mask + per-patient cap 5000 완성"
git push -u origin feat/BIOP02-7-kkkim-tile-wsi
```

### Step 5 — 채널 구조

```
#biop02-general     — 공지, 전체 공유
#biop02-dev         — OpenClaw 알림 수신 + 작업 진행 공유
#biop02-experiments — 실험 결과 공유 (Critic pass 후만)
#biop02-alerts      — GPU 슬롯 예약, 서버 장애 알림
```

> **Critic cross-review 원칙 유지:** OpenClaw가 실험 결과 알림을 보낼 때도 owner ≠ reviewer 룰 적용. 본인 봇이 본인 결과를 critic하는 프롬프트 금지.

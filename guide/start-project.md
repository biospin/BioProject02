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

## 7. Atlassian MCP — Claude Code / Codex에서 Confluence·JIRA 직접 조작

Atlassian 공식 MCP 서버를 설정하면 Claude Code 또는 Codex가 Confluence 페이지 작성·수정, JIRA 이슈 생성·조회를 대화 중에 직접 실행할 수 있습니다. MCP를 설정하지 않은 경우에는 `guide/confluence_drafts.md` 내용을 Confluence에 수동으로 붙여넣습니다.

### Step 1 — Atlassian API Token 발급

1. https://id.atlassian.com/manage-profile/security/api-tokens 접속
2. **Create API token** → Label: `atlassian-mcp-biop02` → Create
3. 만료일은 UI 기본값이 1주일처럼 짧게 잡혀 있을 수 있으므로, 팀 작업용이면 가능한 최장 기간인 1년(365일)로 설정
4. 토큰 복사 후 password manager에 저장 (재조회 불가)

처음 설정하거나, token이 만료·분실·노출됐거나, Confluence/JIRA 요청에서 401 인증 오류가 발생하면 새 token을 발급합니다. 기존 token이 만료됐거나 노출된 경우에는 API tokens 페이지에서 예전 token을 revoke합니다.

토큰은 생성 직후 한 번만 확인할 수 있습니다. 대화창, Slack, repo 파일에 붙여넣지 않습니다.

### Step 2A — Claude Code MCP 서버 설정 (OAuth)

Claude Code도 Atlassian 공식 remote MCP 서버를 OAuth로 등록합니다. 예전 `@atlassian/mcp-atlassian` npm 패키지 방식은 npm registry에 패키지가 없어(404) `✗ Failed to connect` 상태가 되므로 사용하지 않습니다. 이 방식은 **MCP용 API token이 필요 없습니다** (Step 1의 token은 OpenClaw·직접 curl 호출용으로만 사용).

```bash
# user 스코프로 1회 등록 (모든 프로젝트에서 사용 가능)
claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse -s user

# 이미 깨진 atlassian 서버가 있으면 먼저 제거
#   claude mcp remove atlassian -s local   # 또는 -s user
```

등록 후 Claude Code 대화에서 `/mcp` → `atlassian` 선택 → **Authenticate** → 브라우저에서 Atlassian(biospin-ai 워크스페이스) 로그인·승인. 상태 확인:

```bash
claude mcp get atlassian
#   Status: ! Needs authentication  → /mcp 인증 전
#   Status: ✓ Connected             → 인증 완료, 사용 가능
```

### Step 2B — Codex MCP 서버 설정

Codex는 Atlassian 공식 remote MCP 서버를 OAuth로 등록한다. 예전 `@atlassian/mcp-atlassian` npm 패키지 방식은 npm registry에서 패키지를 찾지 못해 실패할 수 있다.

```bash
codex mcp add atlassian --url https://mcp.atlassian.com/v1/mcp
codex mcp login atlassian
```

`codex mcp login atlassian`이 출력하는 URL을 브라우저에서 열어 승인한다. 서버 SSH 환경에서 실행 중이면 callback URL이 서버의 `127.0.0.1:<PORT>`로 열리므로, 브라우저가 있는 로컬 PC에서 같은 포트로 SSH tunnel을 먼저 열어야 한다.

```bash
# login URL의 redirect_uri 포트가 39907인 예시
ssh -N -L 39907:127.0.0.1:39907 -p <SSH_PORT> <username>@<server_host>
```

터널을 연 터미널은 닫지 않고 유지한 뒤 OAuth URL을 다시 연다. 완료 후 확인:

```bash
codex mcp list
# atlassian ... Auth OAuth
```

### Step 2C — Token 만료 시 Claude/Codex 재설정

Claude Code나 Codex를 새로 설정할 필요는 없습니다. 기존 Atlassian MCP 설정은 그대로 두고, 만료된 token 값만 새 token으로 교체합니다.

환경변수 방식으로 쓰는 경우 shell 설정 파일의 `ATLASSIAN_TOKEN`만 갱신합니다.

```bash
export ATLASSIAN_URL="https://biospin-ai.atlassian.net"
export ATLASSIAN_EMAIL="<본인 atlassian 이메일>"
export ATLASSIAN_TOKEN="<새로 발급한 Atlassian API token>"
```

- Claude Code: `~/.claude/settings.json`에 token을 직접 저장해둔 경우에만 해당 값을 새 token으로 교체합니다. 환경변수를 참조하도록 설정했다면 shell 환경변수만 갱신합니다.
- Codex: `~/.codex/config.toml`이 `env_vars = ["ATLASSIAN_URL", "ATLASSIAN_EMAIL", "ATLASSIAN_TOKEN"]`를 참조한다면 config 파일은 그대로 두고 shell 환경변수만 갱신합니다.

갱신 후 Claude Code 또는 Codex를 완전히 재시작하고 MCP 연결을 확인합니다. 계속 401 오류가 나면 `ATLASSIAN_EMAIL`이 token을 만든 계정과 같은지 먼저 확인합니다.

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

Claude Code 또는 Codex 재시작 후 대화에서 바로 사용:

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
- `~/.codex/config.toml` 또는 프로젝트 `.codex/config.toml`에도 토큰 값을 직접 넣지 말 것 — `env_vars`와 쉘 환경변수로 주입.
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
# 1. 서버 접속 (2026-07-11부터 직접접속, kkkim 포트=2205)
ssh -p 2205 kkkim@121.126.38.195

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


### Step 6 — OpenClaw에서 Confluence 게시까지 수행하려는 경우

기본 원칙은 OpenClaw가 알림만 보내고, 실제 코드·문서 작업은 팀원이 Claude Code 또는 Codex에서 수행하는 것입니다. OpenClaw가 Confluence 게시까지 자동 수행하게 하려면 봇 역할을 확장하는 것이므로 별도 권한과 승인 절차를 둡니다.

권장 흐름:

1. OpenClaw가 JIRA 이슈 완료 또는 PR merge 이벤트를 감지
2. `guide/confluence_drafts.md` 또는 PR 설명에서 게시할 초안 추출
3. Slack DM 또는 `#biop02-dev`에 게시 미리보기 전송
4. 담당자가 Slack에서 승인
5. OpenClaw가 Atlassian API 또는 Atlassian MCP 서버를 통해 Confluence에 페이지 생성·수정
6. 생성된 Confluence URL을 JIRA 코멘트와 Slack 스레드에 기록

OpenClaw 서버 환경변수에 아래 값을 추가합니다. 토큰은 repo에 커밋하지 않습니다.

```bash
export ATLASSIAN_URL="https://biospin-ai.atlassian.net"
export ATLASSIAN_EMAIL="<봇 또는 담당자 atlassian 이메일>"
export ATLASSIAN_TOKEN="<Atlassian API token>"
export CONFLUENCE_SPACE_KEY="VC"
export CONFLUENCE_PARENT_PAGE_TITLE="프로젝트#02"
export OPENCLAW_CONFLUENCE_DRY_RUN="true"
```

운영 전에는 `OPENCLAW_CONFLUENCE_DRY_RUN=true`로 Slack 미리보기만 보내고, 실제 게시가 검증된 뒤에만 `false`로 전환합니다.

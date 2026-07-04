# OpenClaw 에이전트 하니스 설정 런북 (BIOP02-85)

**담당:** braveji | **대상 서버:** 61.109.239.220 (port 2205) | **버전:** OpenClaw 2026.5.18 (50a2481)

이 런북은 OpenClaw gateway에서 에이전트 하니스 교체 → API 키 설정 → Atlassian MCP 등록 → cron 등록까지 순서대로 실행하는 절차를 기술한다.

---

## 현재 상태 (kkkim 확인, 2026-06-03 기준)

| 항목 | 상태 |
|---|---|
| Slack 봇 `kakyung.kim-openclaw-bot` | ✅ enabled, gateway reachable |
| Atlassian MCP OpenClaw 등록 | ✅ 등록됨 (OAuth 미완료) |
| 에이전트 main 모델 | ⚠️ `codex` — provider 인증 미설정으로 실행 실패 (모델은 codex 유지) |
| 모델 provider 키 | ❌ 미설정 |

---

## Step 0 — 서버 접속 및 환경 확인

```bash
ssh -p 2205 braveji@61.109.239.220
```

접속 후 OpenClaw 버전과 Node.js 환경 확인:

```bash
# Node.js v22.12+ 필요 (nvm으로 관리)
node -v       # v22.x.x 이어야 함
which openclaw
openclaw --version   # OpenClaw 2026.5.18 (50a2481)
openclaw doctor      # 환경 종합 점검
```

Node.js가 v22 미만이면:

```bash
nvm install 22
nvm use 22
nvm alias default 22
hash -r
```

OpenClaw가 없거나 버전이 낮으면:

```bash
npm install -g openclaw@latest
hash -r
openclaw --version
```

현재 에이전트 · cron · MCP 목록 확인:

```bash
openclaw agents list
openclaw cron list
openclaw mcp list
```

---

## Step 1 — 에이전트 main 재생성 (모델 codex로 설정)

OpenClaw gateway는 Claude 계열 모델(`claude-sonnet-4-6` 등)에 연결할 수 없으므로 `main` 에이전트를 **codex 모델**로 설정한다.
기존 실행 실패의 원인은 모델 선택이 아니라 provider 인증 미설정이므로, 아래 재생성 후 Step 2에서 codex 인증을 잡는다.

```bash
# 현재 에이전트 목록 확인
openclaw agents list

# 삭제 후 codex 모델로 재생성
openclaw agents delete main
openclaw agents add main --model codex

# 재등록 확인
openclaw agents list
# main 항목이 출력되면 정상
```

> **참고:** `openclaw agents add` 옵션: `--model <id>` / `--workspace <dir>` / `--agent-dir <dir>` / `--bind <channel>`. `--harness`는 없음.
> 모델 ID는 `codex`. OpenClaw gateway가 Claude 계열 모델에 연결 불가하여 codex를 사용한다.

---

## Step 2 — OPENAI_API_KEY 설정

OpenClaw gateway가 codex 모델을 호출할 수 있도록 OpenAI API 키를 등록한다.

```bash
# ~/.bashrc에 추가 (권장)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc

# 설정 확인 (키 값은 직접 출력하지 말 것)
echo ${OPENAI_API_KEY:0:7}...   # 앞 7자만 출력
```

반영 후 gateway 재시작:

```bash
openclaw gateway restart
openclaw gateway status   # running 확인
```

> ⚠️ API 키는 절대 git에 커밋하지 않는다. `~/.bashrc`는 `chmod 600 ~/.bashrc`로 보호.

---

## Step 3 — Atlassian MCP 등록

> ⚠️ OpenClaw `mcp` 명령에는 **`login` 서브커맨드가 없다** — 등록(`set`)만 한다.
> 실제 JIRA 호출 시점에 런타임 OAuth가 처리된다.

```bash
# Atlassian 공식 Remote MCP 서버 등록
openclaw mcp set atlassian '{"url":"https://mcp.atlassian.com/v1/mcp","transport":"streamable-http"}'

# 확인
openclaw mcp list          # - atlassian  이 나와야 정상
openclaw config validate   # Config valid
```

---

## Step 4 — kkkim 일일 다이제스트 cron 등록

매일 아침 9시(KST)에 kkkim의 Slack DM으로 BIOP02 할당 이슈 다이제스트를 전송하는 cron을 등록한다.

```bash
openclaw cron add \
  --name biop02-jira-digest \
  --cron "0 9 * * *" \
  --tz Asia/Seoul \
  --agent main \
  --message "BIOP02에서 나에게 할당된 미완료 이슈 중 새로 할당됐거나 기한 3일내 임박한 것 정리해줘." \
  --announce \
  --channel slack \
  --to U0AJZK9R4JE \
  --expect-final \
  --timeout-seconds 120
```

> `U0AJZK9R4JE` = kkkim의 Slack user ID

등록 확인:

```bash
openclaw cron list
# biop02-jira-digest  0 9 * * *  Asia/Seoul  main  ...

# 즉시 실행으로 동작 테스트
openclaw cron run biop02-jira-digest
```

---

## Step 5 — 전체 팀원 cron 확장 (kkkim 검증 후)

| 팀원 | Slack App | Slack User ID | SSH Port |
|---|---|---|---|
| jamie | jamie-openclaw-bot | (확인 필요) | 2201 |
| gglee | ggyu-claw | (확인 필요) | 2203 |
| sjpark | sezinie-openclaw-bot | (확인 필요) | 2204 |
| braveji | yong-openclaw-bot | (확인 필요) | 2205 |
| jhans | (미설정) | — | 2206 |

각 팀원 Slack User ID: Slack 프로필 → ⋮ → **Copy member ID**로 확인.

---

## DoD 검증

다음 날 아침 9시 이후 kkkim에게 확인:

```
✅ Slack DM으로 BIOP02 이슈 다이제스트 도착
✅ 다이제스트에 현재 할당된 To Do / In Progress 이슈 목록 포함
✅ 기한 3일 내 이슈 강조 표시
```

---

## 문제 해결

### gateway가 실행 안 될 때 (daemon 설치 불가 환경)

공유 서버에서 daemon 설치 실패 시 `tmux`로 백그라운드 실행:

```bash
tmux new -s openclaw
openclaw gateway --port 18789 --verbose
# Ctrl+b → d  (세션 분리)

# 재접속
tmux attach -t openclaw
```

### nvm: command not found

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
```

### NPM_CONFIG_PREFIX 충돌

```bash
unset NPM_CONFIG_PREFIX
nvm use 22
```

### MCP `Failed to connect`

SSE 엔드포인트(`/v1/sse`) 또는 `npx @atlassian/mcp-atlassian` 방식은 동작하지 않는다.
반드시 `streamable-http` + `/v1/mcp`를 사용해야 한다:

```bash
openclaw mcp list   # 기존 atlassian 항목 확인
openclaw mcp remove atlassian
openclaw mcp set atlassian '{"url":"https://mcp.atlassian.com/v1/mcp","transport":"streamable-http"}'
openclaw config validate
```

### DNS 오류 (Could not resolve host)

```bash
# Cloudflare DoH로 IP 확인 후 --resolve 우회 (CLAUDE.md 참조)
curl -sS -H "accept: application/dns-json" \
  "https://1.1.1.1/dns-query?name=mcp.atlassian.com&type=A"
```

### cron 미실행 시 로그 확인

```bash
openclaw cron run biop02-jira-digest   # 수동 실행
openclaw logs --cron biop02-jira-digest --tail 30
```

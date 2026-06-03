# OpenClaw 에이전트 하니스 설정 런북 (BIOP02-85)

**담당:** braveji | **대상 서버:** 61.109.239.220 (port 2205) | **작성일:** 2026-06-03

이 런북은 OpenClaw gateway에서 에이전트 하니스 교체 → 모델 키 설정 → Atlassian MCP OAuth → cron 등록까지 순서대로 실행하는 절차를 기술한다.

---

## 현재 상태 (kkkim 확인, 2026-06-03 기준)

| 항목 | 상태 |
|---|---|
| Slack 봇 `kakyung.kim-openclaw-bot` | ✅ enabled, gateway reachable |
| Atlassian MCP OpenClaw 등록 | ✅ 등록됨 (OAuth 미완료) |
| 에이전트 main 하니스 | ❌ `codex` 가리킴 → 실행 실패 |
| 모델 provider 키 | ❌ 미설정 |

---

## Step 0 — 서버 접속

```bash
ssh -p 2205 braveji@61.109.239.220
```

접속 후 kkkim의 OpenClaw gateway가 동작 중인 workspace로 이동:

```bash
# OpenClaw가 설치된 경로 확인
which openclaw
openclaw --version

# 현재 에이전트/cron 목록 확인
openclaw agent list
openclaw cron list
openclaw mcp list
```

---

## Step 1 — 에이전트 main 하니스 교체 (codex → claude)

현재 `main` 에이전트가 미등록 하니스 `codex`를 가리켜 실행 실패하는 상태다.
Claude Code CLI(`claude`)로 교체한다.

```bash
# 기존 main 에이전트 설정 확인
openclaw agent show main

# claude 하니스로 재등록
# (openclaw agent update 또는 set 명령 — 버전에 따라 다름)
openclaw agent set main --harness claude

# 또는 삭제 후 재생성 방식:
openclaw agent delete main
openclaw agent add main --harness claude --description "BIOP02 팀 AI 에이전트"

# 확인
openclaw agent show main
```

> **참고:** OpenClaw 버전에 따라 명령어가 다를 수 있다. `openclaw agent --help`로 확인.

---

## Step 2 — ANTHROPIC_API_KEY gateway 설정

OpenClaw가 Claude API를 호출할 수 있도록 모델 provider 키를 등록한다.

```bash
# 방법 A: openclaw 환경변수 직접 설정
openclaw config set ANTHROPIC_API_KEY "sk-ant-..."

# 방법 B: gateway 실행 환경의 ~/.bashrc에 추가
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc

# 설정 확인 (키 값은 마스킹됨)
openclaw config list | grep ANTHROPIC
```

> ⚠️ API 키는 절대 git에 커밋하지 않는다. 환경변수 또는 openclaw config 명령으로만 관리.

---

## Step 3 — Atlassian MCP OAuth 완료

Atlassian MCP는 이미 `openclaw mcp set atlassian`으로 등록되어 있으나 OAuth 인증이 미완료된 상태다.

```bash
# 현재 MCP 상태 확인
openclaw mcp list

# OAuth 로그인 시작
openclaw mcp login atlassian
```

`openclaw mcp login atlassian`이 출력하는 인증 URL을 브라우저에서 열어 승인한다.

서버(headless)에서 실행 중이라면 callback 포트가 로컬로 오지 않으므로 SSH 터널 필요:

```bash
# 로컬 PC에서: login URL의 redirect_uri 포트(예: 39907)를 터널
ssh -N -L 39907:127.0.0.1:39907 -p 2205 braveji@61.109.239.220
```

터널 유지 후 OAuth URL을 다시 브라우저에서 열어 승인.

완료 후 확인:

```bash
openclaw mcp list
# atlassian ... Auth: OAuth  Status: connected
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
```

---

## Step 5 — 전체 팀원 cron 확장 (선택)

kkkim 다이제스트 검증 후 나머지 팀원에게도 동일한 cron을 추가한다.

| 팀원 | Slack App | Slack User ID | SSH Port |
|---|---|---|---|
| jamie | jamie-openclaw-bot | (확인 필요) | 2201 |
| gglee | ggyu-claw | (확인 필요) | 2203 |
| sjpark | sezinie-openclaw-bot | (확인 필요) | 2204 |
| braveji | yong-openclaw-bot | (확인 필요) | 2205 |
| jhans | (미설정) | — | 2206 |

각 팀원 Slack User ID는 Slack 프로필 → ⋮ → Copy member ID로 확인.

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

### openclaw agent 실행 실패
```bash
# 로그 확인
openclaw logs --agent main --tail 50

# 하니스 재확인
openclaw agent show main
```

### Atlassian MCP OAuth 만료
```bash
openclaw mcp logout atlassian
openclaw mcp login atlassian  # 재인증
```

### cron 미실행
```bash
# 수동 실행으로 테스트
openclaw cron run biop02-jira-digest
openclaw logs --cron biop02-jira-digest --tail 30
```

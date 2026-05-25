# Confluence 페이지 수정안: write-confluence

대상 페이지: https://biospin-ai.atlassian.net/wiki/spaces/VC/pages/31457401/write-confluence

## 1. 자동 업로드 문구 교체

기존 문구가 아래처럼 Claude Code 전용으로 되어 있으면:

```md
이 파일의 내용을 Confluence에 붙여넣거나, Claude Code에서 "Confluence에 써줘"라고 요청하면 자동 업로드됩니다.
```

아래 문구로 교체합니다:

```md
이 파일의 내용은 Confluence에 직접 붙여넣을 수 있습니다. Claude 또는 Codex에서 Atlassian MCP 설정을 완료한 경우 "Confluence에 써줘"라고 요청하면 자동 업로드할 수 있고, MCP 미설정 시에는 수동으로 붙여넣습니다.
```

## 2. Codex MCP 설정 섹션 추가

Claude Code MCP 설정 섹션 뒤에 아래 내용을 추가합니다.

````md
### Codex MCP 서버 설정 (`~/.codex/config.toml`)

Codex는 MCP 설정을 `~/.codex/config.toml` 또는 신뢰한 프로젝트의 `.codex/config.toml`에서 읽습니다. 토큰 값은 파일에 직접 쓰지 말고 환경변수로 전달합니다.

```toml
[mcp_servers.atlassian]
command = "npx"
args = ["-y", "@atlassian/mcp-atlassian", "--transport", "stdio"]
env_vars = ["ATLASSIAN_URL", "ATLASSIAN_EMAIL", "ATLASSIAN_TOKEN"]
```

쉘 환경에는 본인 계정 값만 설정합니다.

```bash
export ATLASSIAN_URL="https://biospin-ai.atlassian.net"
export ATLASSIAN_EMAIL="<본인 atlassian 이메일>"
export ATLASSIAN_TOKEN="<Atlassian API token>"
```

Codex 재시작 후 TUI에서 `/mcp`로 `atlassian` 서버가 활성화됐는지 확인합니다.
````

## 3. Atlassian API token 발급 및 만료 시 재설정 섹션 추가

사전 조건 앞 또는 Atlassian MCP 설정 섹션 앞에 아래 내용을 추가합니다.

````md
### Atlassian API token 발급 및 만료 시 재설정

Confluence 자동 생성·수정에는 Atlassian 계정의 API token이 필요합니다. 토큰은 개인 계정에 귀속되므로 팀 공용으로 공유하지 않습니다.

처음 설정하거나, token이 만료·분실·노출됐거나, Confluence/JIRA 요청에서 401 인증 오류가 발생하면 새 token을 발급합니다.

1. [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) 페이지에 로그인합니다.
2. **Create API token**을 선택합니다.
3. Label에는 예: `BioProject02 Confluence MCP`처럼 용도를 알 수 있는 이름을 입력합니다.
4. 만료일은 UI 기본값이 1주일처럼 짧게 잡혀 있을 수 있으므로, 팀 작업용이면 가능한 최장 기간인 1년(365일)로 설정합니다.
5. 생성된 token을 한 번만 복사해서 개인 shell 환경변수 또는 개인 MCP 설정에 저장합니다.
6. 기존 token이 만료됐거나 노출된 경우에는 API tokens 페이지에서 예전 token을 revoke합니다.

토큰은 생성 직후 한 번만 확인할 수 있습니다. 대화창, Slack, repo 파일에 붙여넣지 않습니다.

공식 안내: [Manage API tokens for your Atlassian account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

### Token 만료 시 Claude/Codex 재설정

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
````

## 4. OpenClaw로 수행할 때의 운영 절차 추가

OpenClaw 설명이 있는 경우 아래 내용을 추가합니다.

````md
### OpenClaw에서 Confluence 게시까지 수행하려는 경우

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
````

## 5. Codex가 직접 원격 수정하려면 필요한 정보

아래 환경변수가 설정되면 Codex가 Confluence REST API로 페이지를 읽고 수정할 수 있습니다.

```bash
export ATLASSIAN_URL="https://biospin-ai.atlassian.net"
export ATLASSIAN_EMAIL="<본인 atlassian 이메일>"
export ATLASSIAN_TOKEN="<Atlassian API token>"
```

토큰은 대화창이나 repo 파일에 붙이지 말고, shell 환경변수로만 제공합니다.

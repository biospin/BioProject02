현재 완료한 작업 내용을 JIRA 이슈에 작성하고 상태를 완료로 전환합니다.

## 실행 절차

1. 현재 git 브랜치 이름에서 JIRA 이슈 번호를 추출합니다 (예: `docs/BIOP02-30-kkkim-pilot-report` → `BIOP02-30`).
2. `mcp__atlassian__jira_get_issue`로 이슈 현재 상태와 기존 description을 확인합니다.
3. 아래 소스에서 작업 내용을 파악합니다:
   - `git log main..HEAD --oneline` — 이번 브랜치의 커밋 목록
   - `git diff main..HEAD --stat` — 변경된 파일 목록
   - 변경된 주요 파일 직접 읽기 (스크립트, 리포트, 스키마 등)
4. 아래 description 형식에 맞춰 내용을 작성합니다.
5. `mcp__atlassian__jira_update_issue`로 description을 업데이트합니다.
6. `mcp__atlassian__jira_get_transitions`로 "완료" transition ID를 확인합니다.
7. `mcp__atlassian__jira_transition_issue`로 상태를 완료로 전환합니다.

## JIRA Description 형식

BIOP02-29 description이 기준 서식입니다. 아래 구조를 따릅니다:

```
완료 내용

<무엇을 했는지 1-2문장 요약. 과정에서 발견한 이슈나 추가 작업도 포함.>

- 파일: <변경/생성된 주요 파일>
- 커밋: <short hash> (브랜치: <브랜치명>)
- PR: <PR URL> (있는 경우)

<섹션 제목 1> (작업 성격에 따라 자유롭게)

- 구체적인 구현/측정 내용을 불릿으로

<섹션 제목 2>

- ...

다음 단계

- <이 작업 완료로 unblock되는 다음 담당자/이슈>
- <후속 작업이 있으면 기록>
```

## 참고

- description은 한국어로 작성합니다.
- 측정값(wall-clock, shape, 파일 크기 등)이 있으면 반드시 포함합니다.
- PR이 생성된 경우 PR URL을 포함합니다.
- 이슈가 이미 완료 상태면 description만 업데이트하고 transition은 건너뜁니다.
- atlassian MCP가 설정되어 있어야 합니다 (`~/.claude/mcp.json`).

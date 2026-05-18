현재 완료한 JIRA 작업 내용을 Confluence에 페이지로 작성합니다.

## 실행 절차

1. 현재 git 브랜치 이름에서 JIRA 이슈 번호를 추출합니다 (예: `feat/BIOP02-27-kkkim-tile-wsi` → `BIOP02-27`).
2. git log와 `guide/progress_kkkim.md`(또는 본인 progress 파일)에서 해당 이슈의 작업 내용을 파악합니다.
3. `guide/confluence_drafts.md`에 해당 이슈의 초안이 있으면 그것을 기준으로 합니다.
4. 아래 형식에 맞춰 Confluence 페이지를 작성합니다.
5. atlassian MCP를 사용해 VC 스페이스 > 프로젝트 진행-AI전용 > 프로젝트#02 > BIOP02-1 하위에 페이지를 생성합니다.

## Confluence 페이지 형식

**제목:** `[S<스프린트번호>] <작업 파일/내용> (한 줄 설명)`

**본문 구성:**
- 첫 문단: 무엇을 했고 왜 했는지 2-3문장으로 요약
- **진행 내역:** 불릿 리스트로 구체적인 구현 내용
- **사용 예시:** 코드 블록
- **(개념 설명):** 비기술 팀원도 이해할 수 있도록 비유로 설명 (선택)

## 참고

- BIOP02-28 페이지가 작성 형식의 기준입니다.
- 초안이 `guide/confluence_drafts.md`에 없으면 git log와 코드를 직접 읽어 작성합니다.
- atlassian MCP가 설정되어 있어야 합니다 (`~/.claude/mcp.json`). 설정 방법: `guide/start-project.md §7`.

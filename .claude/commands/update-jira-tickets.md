완료한 JIRA 티켓들의 본문을 작업 내용으로 업데이트합니다. kkkim 완료 티켓 서식을 기준으로 작성합니다.

## 사용법

```
/update-jira-tickets [티켓번호1 티켓번호2 ...]
```

- 티켓 번호를 명시하면 해당 티켓만 업데이트합니다. (예: `BIOP02-32 BIOP02-33`)
- 인자 없이 실행하면 최근 git 커밋에서 BIOP02-* 번호를 자동 감지합니다.

## 실행 절차

1. **티켓 번호 확인**
   - 인자로 전달된 티켓 번호를 사용합니다.
   - 없으면 `git log -20 --oneline`에서 `BIOP02-\d+` 패턴을 추출합니다.

2. **각 티켓별 정보 수집**
   - `curl` + Atlassian REST API로 현재 티켓 summary, status, description 확인
   - `git log --oneline --all | grep <티켓번호>` 로 관련 커밋 해시/메시지 수집
   - `git show <commit> --stat` 로 변경 파일 목록 확인
   - 변경된 핵심 파일(`.py`, `.yaml`, `.md`, `.json`) 직접 읽어 구현 내용 파악

3. **Description 작성** (아래 형식 준수)

4. **Atlassian REST API로 description 업데이트**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -u "$ATLASSIAN_EMAIL:$ATLASSIAN_TOKEN" \
     -H "Content-Type: application/json" \
     -X PUT \
     "https://biospin-ai.atlassian.net/rest/api/3/issue/<티켓번호>" \
     -d '{"fields": {"description": { ... }}}'
   ```
   - HTTP 204 응답 확인

5. **완료 상태로 transition (필수)**
   - 이미 완료 상태여도 description 업데이트는 수행합니다.
   - 완료 상태가 아닌 경우 transitions API로 "완료"(id: 41) transition 적용합니다.
   ```bash
   curl -s -o /dev/null -w "%{http_code}" \
     -u "$ATLASSIAN_EMAIL:$ATLASSIAN_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST \
     "https://biospin-ai.atlassian.net/rest/api/3/issue/<티켓번호>/transitions" \
     -d '{"transition": {"id": "41"}}'
   ```
   - HTTP 204 확인

6. **처리 결과 요약 출력**
   - 티켓별 description 업데이트 성공 여부, 완료 transition 여부를 표로 출력합니다.

## Description 서식

kkkim BIOP02-30 서식 기준. 반드시 아래 구조를 따릅니다.

```
완료 내용

<무엇을 했는지 1-2문장 요약. 발견한 이슈나 추가 작업도 포함.>

- 파일: <변경/생성된 주요 파일>
- 커밋: <short hash> (브랜치: <브랜치명 또는 main>)
- PR: <PR URL> (있는 경우만)

<섹션 제목> (구현 내용, 측정 결과, 설계 결정 등 작업 성격에 맞게)

- 구체적인 내용을 불릿으로 기술
- 측정값(wall-clock, shape, 파일 크기, 수치 결과 등)이 있으면 반드시 포함

다음 단계

- 이 작업 완료로 unblock되는 다음 담당자/이슈
- 후속 작업 또는 의존 조건
```

## Atlassian API description 포맷

description은 Atlassian Document Format(ADF) JSON으로 전달합니다.
텍스트 전체를 하나의 paragraph로 감싸는 단순 구조를 사용합니다.

```json
{
  "type": "doc",
  "version": 1,
  "content": [{
    "type": "paragraph",
    "content": [{
      "type": "text",
      "text": "완료 내용\n\n<내용 전체를 \n 로 구분하여 작성>"
    }]
  }]
}
```

## 참고

- description은 한국어로 작성합니다.
- 측정값(wall-clock, shape, 파일 크기 등)이 있으면 반드시 포함합니다.
- 이미 본문이 있는 티켓도 덮어씁니다 (PUT 방식).
- 이미 완료 상태면 transition은 건너뜁니다.
- `ATLASSIAN_EMAIL`, `ATLASSIAN_TOKEN` 환경변수가 설정되어 있어야 합니다 (`~/.claude/settings.json` env 섹션).

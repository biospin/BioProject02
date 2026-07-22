# output_v01 — AI Scientist 설계 시각화 문서

`ai_scientist/`의 6개 마크다운 설계 회고(01~06)를 **mermaid 다이어그램 + HTML** 단일 페이지로 시각화한 결과물.

## 파일

- **`index.html`** — 전체 문서. 브라우저로 열면 된다.

## 여는 법

```bash
# 로컬에서 바로 열기 (macOS)
open ai_scientist/output_v01/index.html
# Linux
xdg-open ai_scientist/output_v01/index.html
```

## 포함된 다이어그램 (mermaid, 8종)

| # | 다이어그램 | 대응 문서 |
|---|---|---|
| 0 | 전체 파이프라인 (요청→라우팅→기획→분석→집필→검수→발표) | README |
| 1 | 2-레이어 아키텍처 + 사람 게이트 2개 | 01 |
| 2 | 분석 파이프라인 의존성 체인 | 01 |
| 3 | 벤치별 다중 에이전트 명부 | 02 |
| 4 | 자연어 라우팅 (단일 직행 vs 다단계 오케스트레이터) | 03 |
| 5 | **자동 검수 루프** (결정론 게이트→AI 적대 리뷰→티어별 처리) | 04 |
| 6 | 협업 흐름 (JIRA→OpenClaw→Slack→Claude Code) | 05 |
| 7 | 교차검수 owner≠reviewer 매핑 | 05 |
| 8 | 설계 계보 (선행연구→설계 선택) | 06 |

## 특징

- **테마 대응** — 우상단 `◐ 테마` 버튼으로 라이트/다크 전환(mermaid 다이어그램도 함께 리렌더). 시스템 테마 자동 감지.
- **사이드바 네비게이션** — 스크롤에 따라 현재 섹션 하이라이트(scrollspy).
- **반응형** — 모바일 폭에서 사이드바가 상단으로 접힘.

## 의존성 주의

`index.html`은 mermaid를 CDN(`cdn.jsdelivr.net/npm/mermaid@10`)에서 불러온다 →
**다이어그램 렌더링에는 인터넷 연결이 필요**하다. 완전 오프라인/자체포함 버전이 필요하면 mermaid를 인라인으로 임베드한 `output_v02`를 별도로 만들 수 있다.

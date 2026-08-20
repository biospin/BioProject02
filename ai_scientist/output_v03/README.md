# output_v03 — AI Scientist 설계서 시각화 (2026-08-20 기준)

`ai_scientist/`의 설계서 7개(README + 01~06)를 **mermaid 10종 + HTML** 단일 페이지로 시각화한 결과물.

| 파일 | 내용 |
|---|---|
| `index.html` | 본문 (46 KB) |
| `mermaid.min.js` | 로컬 mermaid 런타임 (3.2 MB) — **오프라인 렌더용** |

```bash
xdg-open ai_scientist/output_v03/index.html   # Linux
open      ai_scientist/output_v03/index.html   # macOS
```

## v03의 이야기 — 검증기가 자기 자신을 검증하기 시작했다

v02 이후 이 하네스의 가장 큰 변화는 기능 추가가 아니라 **검수의 성격**이다.
CI 검증기가 **3종 → 7종**으로 늘었고, 그중 둘(`게이트 mutation 하네스`·`게이트 공허통과 회귀`)은
*"우리 게이트가 실제로 잡는가"* 를 **의도적 결함 주입으로 시험**한다.

설계서가 반복해 지적해온 *"문서에만 있는 보장은 보장이 아니다"* 가 **기계로 강제**되기 시작했다.

## v02 대비

| | v02 (08-03) | **v03 (08-20)** |
|---|---|---|
| CI 검증기 | 3종 | **7종** (게이트 mutation · 공허통과 회귀 · split 누수 · 국영문 정합 추가) |
| 검수의 성격 | 결과를 검증 | **검증기 자신을 검증** |
| 미해결 갭 | 5건 | **6건** + **1건 닫힘**(스키마) |
| 03 문서 반영 | 라우팅 + 계약 | + **품질 기준선** · **실행·보고 계약** · **mock 분기** |
| 04 문서 반영 | 티어 게이트 | + **`required_followups`**(노동 ≠ 판단) |
| 01 문서 | "원고 아직 없음" | 🔴 **정정** — 원고 존재 |
| 다이어그램 | 12종 | **10종**(재구성: 닫힌 루프·mock 분기·mutation 신규) |

## 다이어그램 10종

| # | 그림 | 대응 |
|---|---|---|
| 1 | 전체 흐름 + **실행 모드 분기**(mock 포함) | README·03 |
| **2** | **⭐ 닫힌 루프** — 발견→분리→결정→도구화→CI | 신규 |
| 3 | 2-레이어 + 사람 게이트 3개 | 01 |
| 4 | **권한 강제 지도** — 도구로 막힌 곳 vs 말로만 | 02 (GAP 3) |
| 5 | **mock 분기** — 데모를 실 결과처럼 넘기지 않는 장치 | 03 |
| 6 | **검수 3층 — CI 7종 상세** | 04 |
| **7** | **⭐ 검증기를 검증하는 층**(mutation / 공허통과) | 04 · 신규 |
| 8 | 협업 흐름 | 05 |
| 9 | 교차검수 owner≠reviewer | 05 |
| 10 | 설계 계보 | 06 |

## 갭 6건은 전부 실물 재검증했다

v03 작성 시점에 **문서를 믿지 않고 리포를 열어** 재확인했다. 그 결과 v02가 갭으로 적었던 **스키마 항목은 닫혀 있어** "닫힌 루프" 절로 옮겼다.

| 근거 | 확인한 것 |
|---|---|
| `SKILL.md` L10·L18·L40 | 게이트 ① 실행 명령 부재 · 원고 "미존재" 문구 잔존 |
| `auto_review_config.json` | `ai_review.agents` = `["paper-critic","reviewer"]`, `enabled=false` |
| `.claude/agents/*.md` frontmatter | `manuscript-writer`는 `Write` 보유 · `venue-reviewer`는 `tools:` 미선언 |
| `schemas/critic_report.schema.json` | `critic_status` enum 3값 — "식별 불가" 없음 |
| `schemas/hypothesis.schema.json` | 3필드 **정식 등재됨** → 갭 아님(닫힘) |
| `.github/workflows/critic-validators.yml` | blocking 스텝 **7개** |

## 특징

- **오프라인 렌더** — `mermaid.min.js`를 로컬에서 먼저 읽고, 없으면 CDN 폴백
- **테마 대응** — 우상단 `◐ 테마` 버튼(다이어그램 동시 리렌더) · 시스템 테마 감지 · 선택 기억
- **사이드바 + scrollspy**, 모바일 반응형, 표·다이어그램 가로 스크롤

## 주의

- **"열린 갭 6건"은 변경 이력에 없다.** 갭은 *관찰된 것*이지 *채택된 설계 변경*이 아니다.
- GAP 3·4·5 수정은 `.claude/agents/*`·`schemas/*`·config를 건드려야 하고, 그건 **Critic이 자기 검수 기준을 정하는 일**이라 `❌ anti-self-reference`에 걸린다 → **Leader 승인 사안.**
- `mermaid.min.js`(3.2 MB)는 vendored 파일이다. 커밋 여부는 팀 판단 — **커밋하지 않아도 CDN 폴백으로 동작**한다.
- `output_v01`(초판)·`output_v02`(08-03)는 **시점 스냅샷으로 보존**한다. 덮으면 "무엇이 바뀌었나"를 잃는다.

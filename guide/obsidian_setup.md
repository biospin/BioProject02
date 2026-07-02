# Obsidian 셋업 가이드 — 연구 노트 (범용)

> 작성: kkkim | 2026-05-23

## 1. 설치

1. [obsidian.md](https://obsidian.md) → Download → macOS `.dmg` 다운로드 후 설치
2. Obsidian 실행 → **Create new vault**
   - Name: `Research`  (또는 원하는 이름)
   - Location: `~/Obsidian/Research/`

---

## 2. Vault 폴더 구조

Obsidian 설치 후 아래 폴더를 수동으로 만든다 (Finder 또는 터미널).

```
~/Obsidian/Research/
├── 00-Inbox/           # 빠르게 던져놓는 임시 노트
├── 10-Projects/        # 프로젝트별 작업 노트
├── 20-Literature/      # 논문 리딩 노트 (1논문 = 1파일)
├── 30-Concepts/        # 개념 정리
├── 40-Experiments/     # 실험 기록 (날짜별)
├── 50-Blog/            # 블로그 초안
├── 90-Archive/         # 완료된 것들
└── _templates/         # 템플릿 파일
```

터미널에서 한번에 만들기:
```bash
mkdir -p ~/Obsidian/Research/{00-Inbox,10-Projects,20-Literature,30-Concepts,40-Experiments,50-Blog,90-Archive,_templates}
```

---

## 3. 필수 플러그인 설치

Obsidian 설정 → Community plugins → Browse

| 플러그인 | 용도 | 우선순위 |
|---|---|---|
| **Obsidian Git** | vault를 private GitHub repo에 자동 백업 | ⭐⭐⭐ |
| **Templater** | 논문/실험 노트 템플릿 자동 채우기 | ⭐⭐⭐ |
| **Zotero Integration** | Zotero 논문 메타데이터 자동 import | ⭐⭐⭐ |
| **Dataview** | 노트를 DB처럼 쿼리 (논문 목록, 실험 목록) | ⭐⭐ |
| **Calendar** | 일별 Daily Note 탐색 | ⭐⭐ |

---

## 4. Obsidian Git 셋업 (자동 백업)

### 4.1 GitHub에 private repo 만들기

`.gitignore` 먼저 생성:
```
.obsidian/workspace*
.obsidian/workspace-mobile*
.trash/
```

```bash
cd ~/Obsidian/Research
git init
git add .gitignore
git remote add origin git@github.com:<your-username>/research-notes.git
git branch -M main
git add -A && git commit -m "init: vault structure"
git push -u origin main
```

### 4.2 Obsidian Git 플러그인 설정

Settings → Obsidian Git:
- Vault backup interval (minutes): `10`
- Auto pull interval (minutes): `5`
- Commit message: `vault backup: {{date}}`

---

## 5. 템플릿

### 5.1 논문 노트 (`_templates/literature.md`)

```markdown
---
title: "{{title}}"
authors: 
year: 
journal: 
arxiv: 
tags: [literature]
status: reading  # reading / done / skimmed
---

## 한 줄 요약

## 읽은 이유 (왜 이게 중요한가)

## 핵심 주장

## 방법론

## 결과 / 수치

## 내 프로젝트와의 연결

## 인용할 문장

## 다음에 읽을 논문
```

### 5.2 실험 노트 (`_templates/experiment.md`)

```markdown
---
date: {{date}}
project: 
tags: [experiment]
status: running  # running / done / failed
---

## 목표

## 설정

## 결과

| 지표 | 값 |
|---|---|
| | |

## 관찰 사항

## 다음 스텝
```

### 5.3 개념 노트 (`_templates/concept.md`)

```markdown
---
tags: [concept]
---

## 한 줄 정의

## 비유로 설명하면

## 수식 / 알고리즘

## 언제 쓰나

## 관련 개념
```

---

## 6. Zotero Integration 셋업

### 6.1 Zotero란?

논문 레퍼런스 관리 앱 (무료). 브라우저에서 논문 페이지를 열고 버튼 하나로 제목/저자/연도/DOI/PDF를 자동 저장. Obsidian 플러그인과 연결하면 Zotero 라이브러리 → Obsidian 노트로 자동 import.

**흐름:** arXiv/PubMed 페이지 → Zotero Connector 클릭 → Zotero 저장 → Obsidian에서 import

### 6.2 설치 순서

**① Zotero 데스크탑 앱**

[zotero.org](https://www.zotero.org/download/) → Zotero 7 다운로드 후 설치

**② Zotero Connector (브라우저 확장)**

[zotero.org/download/connectors](https://www.zotero.org/download/connectors) → Chrome/Firefox용 설치

→ 논문 페이지에서 주소창 오른쪽 아이콘 클릭 → Zotero에 자동 저장

**③ Better BibTeX (Zotero 플러그인)**

Zotero에서 논문을 고유 키(`Chen2024`)로 관리해주는 플러그인.

1. [github.com/retorquere/zotero-better-bibtex](https://github.com/retorquere/zotero-better-bibtex/releases) → 최신 `.xpi` 다운로드
2. Zotero → Tools → Plugins → 톱니바퀴 → Install Plugin from File → `.xpi` 선택
3. Zotero 재시작

Better BibTeX 설정:
- Zotero → Edit → Settings → Better BibTeX
- Citation key formula: `auth.lower + year` → 예: `chen2024`

**④ Obsidian Zotero Integration 플러그인**

Obsidian → Settings → Community plugins → Browse → `Zotero Integration` 설치

Settings → Zotero Integration:
- Database: `Zotero`
- Note import location: `20-Literature/`
- Import template: `_templates/literature.md`

### 6.3 사용법

1. 브라우저에서 논문 페이지 열기 (arXiv, PubMed, Nature 등)
2. Zotero Connector 클릭 → Zotero에 저장 (PDF 자동 첨부)
3. Obsidian에서 `Cmd+P` → `Zotero Integration: Import` 실행
4. 논문 제목 검색 → 선택 → `20-Literature/` 에 노트 자동 생성

### 6.4 Zotero 권장 폴더 구조 (Zotero 앱 내)

```
My Library/
├── Reading/       # 읽는 중
├── Done/          # 완료
├── Key Papers/    # 핵심 논문 (별표)
└── Projects/
    └── 프로젝트명/
```

---

## 7. 모바일 동기화 (갤럭시 / Android)

### 7.1 방법 비교

| 방법 | 비용 | 난이도 |
|---|---|---|
| **Syncthing** | 무료 | 중간 |
| **Obsidian Sync** | $10/월 | 쉬움 |

→ **Syncthing 권장** (무료, 안정적)

### 7.2 Syncthing 셋업

**PC (Mac):**
```bash
brew install syncthing
brew services start syncthing
```
브라우저에서 `http://localhost:8384` 열기

**갤럭시:**
- Play Store → **Syncthing** 설치 및 실행

**연결:**
1. 갤럭시 Syncthing → 상단 ID 복사
2. Mac Syncthing (`localhost:8384`) → Add Remote Device → ID 붙여넣기
3. 양쪽에서 승인
4. Mac에서 Shared Folder 추가: `~/Obsidian/Research/` → 갤럭시와 공유

**갤럭시 Obsidian:**
- Play Store → Obsidian 설치
- Open folder as vault → Syncthing이 동기화한 폴더 선택

> Syncthing은 같은 Wi-Fi 또는 인터넷 경유로 실시간 동기화. 양쪽 모두 Obsidian 열려있을 때 충돌 주의 — 동시 편집은 피하기.

---

## 8. 추천 워크플로

```
논문 읽기
  → 브라우저에서 Zotero Connector 클릭
  → Obsidian: Zotero Integration으로 노트 import
  → [[링크]]로 관련 개념/프로젝트 노트에 연결

실험 진행
  → 40-Experiments/ 에 날짜_설명.md (experiment 템플릿)
  → 완료되면 결과 기록
  → 90-Archive/ 로 이동 (완료 후)

개념 정리
  → 30-Concepts/ 에 개념명.md (concept 템플릿)
  → 논문 노트에서 [[개념명]] 으로 링크

블로그/공유
  → 충분히 쌓이면 50-Blog/ 에서 정리
  → GitHub Pages 또는 Notion으로 export
```

---

## 9. Daily Note 설정

### 9.1 Daily Note 활성화

Settings → Core plugins → **Daily notes** 켜기

| 설정 | 값 |
|---|---|
| New file location | `00-Inbox/` |
| Template file location | `_templates/daily.md` |
| Date format | `YYYY-MM-DD` |

### 9.2 Daily Note 템플릿 (`_templates/daily.md`)

```markdown
---
date: {{date:YYYY-MM-DD}}
tags: [daily]
---

## 오늘 할 일

- [ ] 

## 오늘 읽은 것

## 실험 기록

## 막힌 것 / 질문

## 내일 이어서
```

Calendar 플러그인으로 사이드바에서 날짜 클릭 → Daily Note 자동 생성.

---

## 10. Dataview 쿼리 예시

### 10.1 읽는 중인 논문 목록

````markdown
```dataview
TABLE authors, year, journal
FROM "20-Literature"
WHERE status = "reading"
SORT year DESC
```
````

### 10.2 진행 중인 실험 목록

````markdown
```dataview
TABLE project, status
FROM "40-Experiments"
WHERE status != "done"
SORT file.mtime DESC
```
````

### 10.3 최근 수정 노트 전체

````markdown
```dataview
LIST
FROM ""
SORT file.mtime DESC
LIMIT 20
```
````

---

## 11. Templater 자동화 설정

### 11.1 플러그인 설정

Settings → Templater:
- Template folder location: `_templates`
- **Trigger Templater on new file creation**: 켜기
- Folder Templates 추가:

| Folder | Template |
|---|---|
| `20-Literature` | `_templates/literature.md` |
| `40-Experiments` | `_templates/experiment.md` |
| `30-Concepts` | `_templates/concept.md` |

→ 해당 폴더에서 새 파일 만들면 템플릿이 자동 적용됨.

### 11.2 파일명 규칙

```
20-Literature/  저자Year-키워드.md      예: Chen2024-UNI.md
40-Experiments/ YYYYMMDD_설명.md        예: 20260523_pilot-run.md
30-Concepts/    개념명.md               예: Attention-MIL.md
```

---

## 12. 자주 쓰는 단축키

| 단축키 | 기능 |
|---|---|
| `Cmd+N` | 새 노트 |
| `Cmd+O` | 빠른 파일 열기 |
| `Cmd+Shift+F` | 전체 검색 |
| `Cmd+E` | Edit / Preview 전환 |
| `[[` 입력 | 내부 링크 |
| `Cmd+P` | 명령 팔레트 |

Obsidian Git (명령 팔레트):
- `Obsidian Git: Commit all changes` — 수동 커밋
- `Obsidian Git: Pull` — 수동 풀

Zotero Integration (명령 팔레트):
- `Zotero Integration: Import notes` — 논문 import

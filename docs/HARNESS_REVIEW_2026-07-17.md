# 하네스·에이전트 점검 문서 검토 — BIOP02/BIOP01 적용 + 범용화 판단

**검토자:** kkkim(Leader) · **일자:** 2026-07-17
**대상:** `~/collab_workspace/Presentation/docs/AutoBioX_하네스_에이전트_점검_2026-07-17.md`
**목적:** 위 문서의 제안을 BIOP02·BIOP01에 **무엇을·어떤 순서로** 적용할지 확정하고, **무엇을 범용화하고 무엇을 프로젝트별로 둘지** 가른다.

---

## 0. 결론 요약

1. **착수 순서(확정):** ① BIOP02 Critic 3항목 Inspect 파일럿 + 2026-07-17 실패 6건을 회귀셋 씨앗으로 → ② 되면 BIOP01 재현성 회귀로 확장 → ③ GitHub Actions CI 게이팅.
2. **범용/전용 분할:** eval 하네스·실패 코퍼스·문헌 분석 하네스 = **범용**. Critic scorer 임계값·오케스트레이션·검증 게이트 설계 = **프로젝트별/자작 유지**(차별점).
3. **⚠️ 원문 갱신 필요:** §5.1의 BIOP02 타깃이 "Therapeutic 가설(서정한 Paper B) 인용 근거화"인데, **같은 날 Paper B 엔진 보류(결정 2-B)** 가 내려졌다 → 문헌 우선순위는 **Paper C flagship + Yale 앵커**로 이동.
4. **§5.6 차용 후보 3종(HIGH) 실존 확인 완료** + 원문에 없는 4건 추가 발견(§4).

---

## 1. BIOP02 적용

### 1.1 §5.2 Inspect eval (Critic 7항목) — **최적 대상, 즉시 가능**
- `agents/critic/checklist_v1.md`(223줄) + `schemas/critic_report.schema.json`에 **`checks` 구조가 이미 존재** → scorer 인코딩 기반 완비. 새로 설계할 게 아니라 **기존 스키마를 그대로 채점 대상으로** 쓰면 된다.
- **`.github/workflows` 부재 확인** → §5.5 CI는 개선이 아니라 **신규 구축**. 현재 우리 DoD의 "헤드라인 숫자 재계산 게이트"는 **수동**이다. 이걸 CI화하는 게 정확히 §5.5.

### 1.2 §6 실패 코퍼스 — **씨앗이 오늘 실제로 쌓였다**
문서는 "실패 사례를 축적해 회귀셋으로"를 제안하는데, 2026-07-17 하루에 **진짜 실패 6건**이 나왔다(가상 사례 아님):

| # | 실패 | 성질 |
|---|---|---|
| 1 | csv `\r` 파일명 → openslide "missing" | 파이프라인·**조용한 실패** |
| 2 | `local coh="$1" man="...${coh}..."` 같은 줄 자기참조 → `set -u` unbound → **다운로드 성공 후 임베딩 침묵 사망** | 파이프라인·**조용한 실패** |
| 3 | detached shell에 conda 없음 → 임베딩 실패 | 파이프라인 |
| 4 | n=187 vs n=85 혼동 | 문서·주장 |
| 5 | 인용 오류 5건(**존재하지 않는 "Williams 2022"** — 링크는 정반대 결론의 Koudijs 2023) | 문서·주장 |
| 6 | "523 slides" vs "523 cases" 단위 혼동 | 문서·주장 |

**분류가 중요하다:** 4~6은 Critic eval로 잡을 수 있고, 1~3은 **eval이 아니라 파이프라인 스모크 회귀**로 잡아야 한다. 이 둘을 한 바구니에 넣으면 scorer가 못 잡는 걸 잡는 척하게 된다.

> **오늘 추가된 7번째:** Virchow2 HF 캐시가 `.incomplete` 부분파일인데 `du` 크기(610M)만 보고 "캐시 완료"로 보고 → **1장 E2E 스모크가 잡음.** "대량 작업 전 1장 E2E"가 회귀 규칙이 될 자격이 있다.

### 1.3 §5.1 PaperQA2 — **오늘 실증 근거가 생겼다**
- 우리 문서에서 **실제 인용 오류 5건**을 적대적 검증으로 발견 → 문서의 "인용≥2 + 근거 span, 오류 0" 메트릭이 정확히 이 실패를 겨냥한다.
- **baseline이 이미 있다**: `research/REFERENCE_LIST.md`(77편) + `CITATION_AUDIT_2026-07-17.md`(33+ 정확, 미확인 0) → **diff 파일럿 비용이 최저**. PaperQA2를 붙여 우리 audit과 대조하면 "도구가 우리보다 나은가"를 싸게 답할 수 있다.

### 1.4 ⚠️ 원문과 오늘 결정의 충돌
§5.1이 BIOP02 타깃으로 **"Therapeutic 가설(서정한 Paper B)"** 를 지목하나, `research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md` **결정 2-B로 Paper B 무거운 엔진은 보류**됐다(같은 날짜라 원문 저자가 몰랐을 것). → **BIOP02 문헌 타깃 = Paper C flagship + Yale 앵커**로 정정.

---

## 2. BIOP01 적용

- **§5.2 Inspect** — 지용기님 **재현성 회귀**(ref/compact/reset diff)를 eval 스위트로. scorer = **4종 교차 재현 일치도**. 문서가 이를 "Flywheel 첫 발판"으로 지목한 건 타당하다.
- **§5.1 PaperQA2** — velocity 방법론 + Trevino 2021 코퍼스. BIOP01은 이미 `paper_analysis/`에 dual-lens 20편 이상 보유 → **BIOP02와 동일한 "baseline 대비 diff"** 방식이 그대로 적용된다.
- **§7 액션** — BIOP01 에이전트 구조 점검(데이터셋 기준 → 역할/단계 구조로 수렴 중)에 BIOP02 구조가 참조 모델.
- **§5.6 매핑** — GPTomics bioSkills(RNA-seq·single-cell) · BioMate(DESeq2/edgeR/limma 선택법) · Anthropic **scvi-tools** 번들이 BIOP01 쪽 직접 후보(§4 참조).

---

## 3. 범용화 판단 — 층을 갈라야 한다

| 층 | 범용? | 근거 |
|---|---|---|
| **eval 하네스(Inspect) + 실패 코퍼스 스키마** | ✅ **범용** | 프로젝트 무관 인프라. `run_id·agent·metric·verdict` 공통 |
| **문헌 분석 하네스**(kkkim-paper-agent) | ✅ **범용** | 두 프로젝트가 이미 같은 dual-lens 포맷 사용 |
| **paper-critic 반려 사례 풀** | ✅ **범용 — 레버리지 최대** | 문서 §6이 지목. 두 프로젝트를 한 풀로 모을 때 가치가 커짐 |
| **Critic scorer(항목·임계값)** | ❌ **프로젝트별** | BIOP02 = site 편향·DRP 프레이밍·7항목 / BIOP01 = 재현 일치도 α. 내용이 도메인 특화 |
| **오케스트레이션·검증 게이트 설계** | ❌ **자작 유지** | 문서 §5.4·§5.6 채택원칙과 일치 = **우리 차별점** |

**이미 만들어진 범용 자산**(2026-07-17, `~/.claude/projects/-home-kkkim/memory/`): ADF 멘션 curl 셋업 · TCIA PathDB headless 다운로드 · csv `\r` 함정 · **HF 캐시 `.incomplete` 함정 / Virchow2 register token / detached conda 절대경로**. 전부 프로젝트 무관.

---

## 4. §5.6 GitHub Agent Skills — **실존 검증 결과** (kkkim, 2026-07-17)

> 원문 스스로 **"Star 순위는 관심도이지 정확성·GxP 보장이 아님"** 이라 경고한다. 오늘 우리 문서에서 **존재하지 않는 논문("Williams 2022")을 인용한 사고**가 나온 직후이므로, 채택 논의 전에 **실존부터** 확인했다.

### 4.1 HIGH 3종 — 전부 실존 확인 ✅

| 후보 | 실존 | 확인된 내용 | 우리 적용 |
|---|---|---|---|
| **Anthropic Life Sciences** | ✅ [`anthropics/life-sciences`](https://github.com/anthropics/life-sciences) | Claude Code 마켓플레이스(`marketplace.json` 장기 호스팅). 스킬: **scvi-tools** · **nextflow-development** · single-cell-rna-qc · instrument-data-to-allotrope · scientific-problem-selection | **BIOP01** single-cell(scvi-tools·single-cell-rna-qc) 1순위. 공식이라 유지보수 유리 |
| **ClawBio** | ✅ [`ClawBio/ClawBio`](https://github.com/ClawBio/ClawBio) | "bioinformatics-native, local-first, reproducible". **spec-first**(도메인 지식이 모델 가중치가 아니라 **SKILL.md**에) · agent-agnostic · pip/conda/Claude Code 플러그인 | **§6 재현성 인프라 1순위**(아래 4.2) |
| **AIPOCH Medical Research Skills** | ✅ [`aipoch/medical-research-skills`](https://github.com/aipoch/medical-research-skills) | 550+ 스킬. Evidence Insights·Protocol Design·Data Analysis·Academic Writing. **MedSkillAudit** 감사 프레임워크로 사전 심사. **"literature authenticity constraints — hard rules"** 명시 | **논문 하네스 벤치마킹 1순위**(아래 4.3) |

*(star 수치 자체는 검증하지 않았다 — 실존·내용만 확인. 관심도는 채택 근거가 아니므로 굳이 확인할 가치가 낮다.)*

### 4.1.1 라이선스 게이트 확인 결과 (kkkim, 2026-07-17) — §4.4-4의 실행

우리는 학술 비상업(출판 전용)으로 운용 중이라 **채택 전 라이선스 확인이 필수**다. 확인 결과:

| 후보 | 라이선스 | 설치 | 비고 |
|---|---|---|---|
| **AIPOCH** medical-research-skills | ✅ **MIT** | — | 무료·유료계정 불요. 단 개별 스킬이 외부 서비스(PubMed·ChEMBL·DrugBank) 호출 시 각 자격증명 필요 |
| **ClawBio** | ✅ **MIT** | `pip install clawbio` · `conda install -c bioconda clawbio` · **`/plugin marketplace add ClawBio/ClawBio`** | local-first |
| **Aperivue** medsci-skills | ✅ **MIT** (README 명시) | — | citation check 특화 |
| **Anthropic** life-sciences | ⏳ **미확인** | `/plugin marketplace add` (marketplace.json) | 공식 |

**→ MIT 3종은 라이선스 게이트 통과.** 우리 FM 라이선스(CC-BY-NC-ND)보다 오히려 자유롭다.
**⚠️ 남은 게이트:** SKILL.md·스크립트 **내용 확인**(실행 코드를 읽지 않고 설치 금지) · 외부 전송 여부.

### 4.1.2 ★ ClawBio 재현성 계약 — 실측 확인

ClawBio 스킬은 `reproducibility/` 디렉토리를 emit한다:

| 파일 | 내용 | 우리에게 없는 것? |
|---|---|---|
| `commands.sh` | 재실행 명령 | ❌ **없음** |
| `environment.yml` | conda 환경 스냅샷 | ❌ **없음** |
| `checksums.sha256` | 산출물 SHA-256 | ❌ **없음** |
| `runtime-lock.json` | 추가 lock(선택) | ❌ 없음 |

우리 `experiments/<user>/<date>/` 5종 규약은 `commit_hash`만 있고 **환경·명령·체크섬이 전부 없다** → 재현이 사람 기억에 의존. **이 4파일 계약을 우리 규약에 추가하는 게 §5.6 전체에서 가장 값싸고 확실한 이득.** (문서 주의: "일부 replay는 원본 외부 입력·도구가 로컬에 있어야 함" — 우리 WSI raw 보관 정책과 연결됨.)

### 4.2 ★ ClawBio에서 **지금 바로 차용할 구체 계약**
ClawBio 스킬은 **replay 메타데이터**를 export한다: **`commands.sh` + `environment.yml` + `SHA-256` 체크섬** → **"원래 에이전트 세션 없이 재검증 가능"**.

이건 우리 DoD의 "헤드라인 숫자를 다시 계산해 대조"를 **파일 계약으로 굳힌 형태**이고, 우리 `experiments/<user>/<date>/` 5종 아티팩트 규약의 **빈 칸을 정확히 메운다**(현재 우리는 `commit_hash`만 있고 **환경·명령·체크섬이 없다** → 재현이 사람 기억에 의존). **아이디어 차용 우선순위 1위.**

### 4.3 ★ AIPOCH의 "literature authenticity hard rules" = 우리가 오늘 당한 그 문제
우리는 오늘 **존재하지 않는 논문을 인용**했다가 적대적 검증으로 잡았다. AIPOCH가 이걸 **hard rule**로 강제한다면 §5.1 파일럿의 **직접 비교 대상**이다. 검증 질문: *"AIPOCH의 authenticity rule이 우리 CITATION_AUDIT 5건을 잡아내는가?"* — 이게 곧 저비용·고정보 파일럿이다.

### 4.3.1 ★★ 파일럿 실행 결과 — `medsci-skills/verify-refs` vs **우리 인용오류 5건** (kkkim, 2026-07-17)

§4.5-(c)의 원칙("합격 기준 = 우리가 실제로 당한 실패셋")을 **실제로 집행한 첫 사례**.

**게이트 통과 확인:** LICENSE 실파일 = **MIT**(Aperivue). `verify_refs.py` 1,050줄 **순수 파이썬**,
`subprocess`/`os.system`/`eval`/`exec` **없음**, 외부통신 = CrossRef/NCBI/OpenAlex뿐(SKILL.md에 공개).
스킬 설계도 좋다: **"기억으로 검증하지 말고 번들 스크립트를 실행하라"** = 결정론적, audit-only(참고문헌 미수정).

**시험 구성:** 우리 오류 3건(서지성) + 실존 대조군 3건.

| 우리 오류 | 성격 | verify-refs 판정 | 결과 |
|---|---|---|---|
| **"Williams 2022" LINCS reversal** | **날조(실존 안 함)** | **`OK`** | ❌ **놓침** |
| Sharifi-Noghabi **2024**(→실제 2021) | 연도 오류 | `MISMATCH` | ✅ 잡음 |
| Path2Space **"Kaminski"**(→실제 Shulman) | 저자 오류 | `MISMATCH` | ✅ 잡음 |
| "cross-dataset Spearman 0.2–0.25" | 초록에 없는 **수치** | — | ⚪ **범위 밖**(서지 아님) |
| MAKO = "subtype 벤치마크"(→ROR-P) | **스코프** 오프레이밍 | — | ⚪ **범위 밖**(서지 아님) |

**→ 서지성 오류 3건 중 2건 적발. 그러나 가장 위험한 1건(날조)을 놓쳤다.**

#### 왜 놓쳤나 — 도구의 진짜 약점 (코드 확인)
`verify_refs.py` L557–560: PubMed `esearch`를 **제목으로 조회해 결과가 하나라도 있으면 무조건 `OK`**를 반환한다.
유사도 가드(`_title_similarity`)는 **OpenAlex 경로에만** 걸려 있고 **PubMed 경로엔 없다**.
→ 날조된 제목이 느슨하게 매칭된 아무 논문이나 물어오면 `OK`. 실제로 "Williams 2022"는
`PubMed title match; PMID candidates=41646932,35...`로 **OK** 판정됐다.

**★ 치명적인 이유: 날조 인용은 정의상 DOI가 없다.** 이 도구의 강한 경로(CrossRef DOI 대조)는
**DOI가 있을 때만** 작동하고, DOI가 없으면 약한 PubMed 제목 경로로 떨어져 `OK`가 된다.
**즉 "존재하지 않는 논문"이 정확히 이 도구가 가장 약한 지점이다** — 우리가 실제로 당한 그 유형.

#### 내 시험 설계 결함도 있었다 (정직 보고)
- 1차 시도에서 `.bib`의 DOI가 전부 파싱 안 됐다 → 원인은 도구 정규식 `doi\s*=\s*[{"](.+?)[}"]\s*,`이
  **끝 쉼표를 요구**하는데 내 DOI가 마지막 필드였던 것. (내 실수지만 **정규식도 취약** — 마지막 필드 DOI는
  적법한 BibTeX다.) 쉼표 추가 후 CrossRef 경로가 정상 작동.
- 대조군 3건의 **제목을 내가 축약**해 넣어서 전부 `MISMATCH`가 됐다 → **위양성률은 이 시험으로 판정 불가.**
  정확한 제목으로 재시험해야 한다(미완).

#### 판단
- **차용 가치 있음(조건부):** DOI가 있는 인용의 **연도·저자·제목 대조는 실제로 작동**했다(우리 오류 2건 적발).
  우리에게 없는 기능이고 MIT다.
- **그러나 이걸로 우리 검증을 대체하면 안 된다.** 우리 적대적 검증은 **"Williams 2022"를 잡았고**
  이 도구는 **놓쳤다.** 우리 방식이 이 지점에선 더 강하다 — §5.4/§5.6의 *"검증 게이트 설계는 자작 유지"*가
  실증된 셈.
- **차용한다면:** DOI 있는 인용의 기계적 대조 = 이 도구, **DOI 없는 인용 = 무조건 사람/적대적 검증**으로
  라우팅. `submission_safe` 플래그를 **그대로 믿으면 안 된다**(1차 시도에서 날조 인용이 있는데도 `True`였다).
- **업스트림 기여 후보:** PubMed 경로에도 `_title_similarity` 가드 적용 → MIT라 PR 가능.

### 4.4 원문에 없던 발견 4건

1. **⚠️ `OpenClaw` 이름 충돌 — 반드시 인지.** 원문 LOW의 "OpenClaw(★2,847) 종합 컬렉션"은 **오픈소스 에이전트 게이트웨이/플랫폼**이다(ClawBio가 "self-hosted OpenClaw gateway"를 지원, [`FreedomIntelligence/OpenClaw-Medical-Skills`]도 존재). **BIOP02 CLAUDE.md의 "OpenClaw bot"(팀원별 JIRA→Slack 알림 봇)과 같은 이름**이라 문서·대화에서 혼동이 확실히 생긴다. 둘의 관계를 확인하고 **명칭을 구분**해야 한다(예: "OpenClaw 플랫폼" vs "OpenClaw 알림봇").
2. **[`Aperivue/medsci-skills`](https://github.com/Aperivue/medsci-skills)** — 원문 미수록. "literature search, **reporting-guideline & citation checks**, statistics, publication figures, submission... 의사-연구자가 만들고 **실제 출판물로 테스트**. **MIT**." → **MIT 라이선스**라 차용 자유도가 AIPOCH보다 높을 수 있다. citation check가 우리 니즈와 정확히 일치 → **§5.1 파일럿 후보에 추가**.
3. **[`GoekeLab/awesome-genomic-skills`](https://github.com/GoekeLab/awesome-genomic-skills)** — 유전체 agentic skill·MCP·**벤치마크** 큐레이션. 후보 탐색의 상위 소스.
4. **라이선스 검토가 채택 원칙에서 빠져 있다.** 우리는 FM 라이선스가 전부 학술 비상업(CC-BY-NC-ND)이라 **출판 전용**으로 운용 중이다(CLAUDE.md). 스킬 라이브러리도 **채택 전 라이선스 확인을 원칙에 명시**해야 한다 — SKILL.md·스크립트 확인과 같은 급의 게이트.

### 4.5 채택 원칙 (원문 유지 + 보강)
> SKILL.md·스크립트 확인 후 공개 데이터로 파일럿 → **상용/표준부(문헌·통계·재현 인프라)만 차용**, **검증 게이트 설계·오케스트레이션은 자작 유지**(차별점).

**보강 3가지:**
- **(a) 라이선스 게이트** 추가(§4.4-4).
- **(b) star 수는 채택 근거로 쓰지 않는다** — 실존·SKILL.md·라이선스·우리 실패셋 통과 여부로만 판단(원문 경고의 실행 버전).
- **(c) 파일럿의 합격 기준 = 우리 실패 코퍼스**(§1.2의 6건 + 인용오류 5건). "우리가 실제로 당한 걸 잡는가"가 유일하게 의미 있는 벤치마크다.

---

## 5. 미검증 · 열린 질문

- Inspect 파일럿은 **작업 중**(`evals/critic_pilot/`) — 결과 나오기 전엔 ②③ 진행 불가.
- §5.6 후보들의 **라이선스·SKILL.md 내부**는 미확인(실존만 확인).
- `OpenClaw` 플랫폼과 우리 알림봇의 관계 **미확인**.
- AIPOCH/medsci-skills의 authenticity rule이 **우리 5건을 실제로 잡는지 미검증** — 파일럿 전엔 아무 주장도 하지 않는다.

## 6. 관련 문서
- 원문: `~/collab_workspace/Presentation/docs/AutoBioX_하네스_에이전트_점검_2026-07-17.md` (1차 출처: `feedback/1차출처_AI과학자_Agentic_트렌드_2026-07.md`, LinkedIn 2026-07-15)
- 논문 구조 정본: `research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md`
- 인용 감사: `research/CITATION_AUDIT_2026-07-17.md` · `research/CITATION_CORRECTIONS_2026-07-17.md`
- Critic: `agents/critic/checklist_v1.md` · `schemas/critic_report.schema.json`

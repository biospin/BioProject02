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

> ⚠️ **kkkim 정정 (2026-07-17, 실행 후):** 아래 원안 중 **"ref/compact/reset diff"는 실물이 없다.**
> 그 표현은 회의록(§5.2·§6)에만 있고 BIOP01엔 **자동화 코드·결과가 없다**(git log엔
> `/compact + /clear consistency tests` 커밋 2건이 있으나 이건 **문헌 재분석 일관성 확인**이지
> 재현성 회귀 자동화가 아니다). **원 제안이 미착수 계획 항목을 기존 자산으로 오인했다.**
> → 실제로 존재하는 **사전등록 채점 자산**(`pipeline/hspc-velocity-benchmark/`)을 대상으로 삼았다.
>
> ⚠️ **두 번째 정정 — 임계값:** 원 제안의 **"α 0.88 기준선"은 임계가 아니라 관측값**이다.
> 봉인된 사전등록(`manuscript/PREREGISTRATION_gse205117.md` L15)은 **"Spearman ρ ≥ 0.50"**이고
> "HSPC 0.88"은 **비고란의 관측치**다. **0.88을 게이트로 박으면 사전등록을 사후에 조이는 것**
> (= 그 문서 L26이 명시적으로 금지한 행위의 반대 방향 버전). → **0.50을 썼다.**

- **§5.2 Inspect** — ~~지용기님 재현성 회귀(ref/compact/reset diff)~~ → **사전등록 채점 재현**을 eval 스위트로.
  실물: `manuscript/PREREGISTRATION_gse205117.md`(fit 산출 **전에 봉인**된 6예측+임계+반증조건) ·
  `cross_dataset/p3_prereg_gse205117.py`(결정론적 채점기) · `results/prereg_gse205117_scorecard.{csv,md}`(6 PASS/0 FAIL).
  **산출: `BioProject01/evals/reproducibility_pilot/`** — 105/105, 실물 scorecard 6/6 정확 재현,
  Inspect 6 task accuracy 1.000, **뮤턴트 25/25 전멸**(`invert_threshold` 포함 — α는 ρ가 높아야 pass,
  lag는 낮아야 pass로 **방향이 반대**라 부호 뒤집기 뮤턴트가 살면 안 된다. BIOP01 고유 위험).
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

**시험 3회 반복.** 1·2차는 **내 .bib 결함**으로 오염됐고(아래 "시험 결함" 참조), **3차가 유일하게 유효**하다.
3차 설계: CrossRef에서 **실제 제목·전체 저자 명단·정확 연도**를 받아 대조군을 만들고, 오류는 **한 필드씩만 오염**시켜 무엇이 검출을 트리거하는지 격리.

#### ✅ 3차(유효) 결과 — **4/6**

| ref | 오염 | 기대 | 실제 | |
|---|---|---|---|---|
| ctrl_farahmand | 없음(전 저자 정확) | OK | **OK** | ✅ |
| ctrl_koudijs | 없음 | OK | **OK** | ✅ |
| ctrl_kaczmarzyk | 없음 | OK | **OK** | ✅ |
| err_author_only | 1저자만 `Kaminski`(실제 Shulman) | MISMATCH | **MISMATCH** | ✅ |
| err_year_only | 연도만 `2024`(실제 2021) | MISMATCH | **`OK`** | ❌ **놓침** |
| err_fabricated | 날조(DOI 없음) | FABRICATED | **`OK`** | ❌ **놓침** |

**위양성 0/3** — 서지가 정확하면 오탐하지 않는다. 발화하면 정확하다.
**저자 환각은 정밀하게 잡는다:** `#1 family: cited='Kaminski' vs source='Shulman'` → *"first-author hallucination suspected"*.

#### 우리 인용오류 5건 최종 성적 — **서지성 3건 중 1건만 적발**

| 우리 오류 | 성격 | 판정 | |
|---|---|---|---|
| Path2Space **"Kaminski"**(→Shulman) | 저자 환각 | `MISMATCH` | ✅ **잡음** |
| **"Williams 2022"** | **날조(실존 안 함)** | `OK` | ❌ **놓침** |
| Sharifi-Noghabi **2024**(→2021) | 연도 오류 | `OK` | ❌ **놓침** |
| "Spearman 0.2–0.25" | 초록에 없는 수치 | — | ⚪ 범위 밖 |
| MAKO = "subtype 벤치마크"(→ROR-P) | 스코프 오프레이밍 | — | ⚪ 범위 밖 |

> ⚠️ **kkkim 자기정정:** 나는 2차 시험 후 *"3건 중 2건 적발(연도 오류도 잡음)"* 이라고 보고했다. **틀렸다.**
> 2차의 연도 케이스 `MISMATCH`는 **연도 때문이 아니라 내가 저자를 1명만 적어서 생긴 author-count 불일치**였다.
> 연도만 격리한 3차에서 **`OK`** 가 나왔다. 도구를 우호적으로 오판할 뻔했다 — **격리 시험이 아니었으면 못 잡았다.**

#### 왜 놓치나 — **코드로 확정** (추정 아님)
1. **연도를 아예 비교하지 않는다.** `year_guess`는 파싱만 되고(L40·191·271) **비교하는 코드가 없다.**
2. **MISMATCH의 유일한 근거는 저자 불일치다.** L856: `record.status = "MISMATCH" if author_mismatch else "OK"`.
   L681 주석: *"This is the **sole** decision surface behind an AUTHOR MISMATCH status"*.
   → **이 도구는 사실상 "저자 환각 검출기" 하나다.** 이름(`verify-refs`)이 시사하는 것보다 훨씬 좁다.
3. **날조는 구조적으로 못 잡는다.** L557–560: PubMed `esearch` 결과가 **하나라도 있으면 무조건 `OK`**.
   유사도 가드(`_title_similarity`)는 **OpenAlex 경로에만** 있고 PubMed 경로엔 **없다**.
   **★ 날조 인용은 정의상 DOI가 없다** → 강한 CrossRef 경로를 못 타고 약한 PubMed 제목 경로로 떨어져 `OK`.
   실제로 "Williams 2022"는 `actual_authors=0`(소스 저자 0명!)인데도 `OK`가 됐다.
   **즉 "존재하지 않는 논문"이 정확히 이 도구의 최약점** — 우리가 실제로 당한 바로 그 유형.

#### 내 시험 설계 결함 (정직 보고 — 2건 다 내 잘못)
- **1차:** `.bib`의 DOI가 전부 파싱 안 됨 → 도구 정규식 `doi\s*=\s*[{"](.+?)[}"]\s*,`이 **끝 쉼표를 요구**하는데
  내 DOI가 마지막 필드였다. (내 실수. 다만 **정규식도 취약** — 마지막 필드 DOI는 적법한 BibTeX다.)
- **2차:** 저자를 **1명만** 적어 대조군 전부가 `AUTHOR COUNT: cited=1 vs source=7`로 오탐 → 위양성률 측정 불가.
  → **교훈: 도구를 시험할 땐 도구가 아니라 내 입력부터 의심하라.** 세 번 만에 유효한 시험이 나왔다.

#### 판단
- **좁지만 진짜인 가치:** **저자 환각 검출**은 정밀하고(위양성 0/3) 우리에게 **없는 기능**이며 MIT다.
  실제로 우리 Path2Space 오류를 잡았을 것이다. **그 용도로만 차용할 가치가 있다.**
- **이름을 믿지 마라.** `verify-refs`는 인용을 "검증"하지 않는다 — **저자만** 본다. 연도·저널은 안 본다.
- **우리 검증을 대체하면 안 된다.** 우리 적대적 검증은 **"Williams 2022"를 잡았고 이 도구는 놓쳤다.**
  §5.4/§5.6의 *"검증 게이트 설계는 자작 유지"*가 실증됐다.
- **차용한다면 라우팅:** 저자 대조 = 이 도구 / **DOI 없는 인용·연도·스코프 = 사람·적대적 검증 필수.**
- **`submission_safe` 플래그를 믿지 마라** — 1차에서 날조 인용이 있는데도 `True`였다.
- **업스트림 기여 후보(MIT라 PR 가능):** ① PubMed 경로에 `_title_similarity` 가드 ② 연도 대조 추가
  ③ DOI 정규식의 끝-쉼표 의존 제거 ④ `actual_authors=0`이면 `OK` 금지.

#### 부수 발견
CrossRef 실측이 **우리 정정 2건을 독립 확인**했다: Sharifi-Noghabi = **2021** ✅, Path2Space 1저자 = **Shulman, Eldad D.** ✅.
반면 우리가 "Koudijs **2023**"으로 쓴 건 CrossRef `issued` 기준 **2022**다(epub/issue 연도 차이로 추정) — 원고 확정 시 확인 필요.

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

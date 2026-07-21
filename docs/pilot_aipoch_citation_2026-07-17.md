# Pilot: AIPOCH medical-research-skills 인용검증 벤치마크 (2026-07-17)

> **목적:** AIPOCH `medical-research-skills`(605 SKILL.md)가 **우리가 실제로 당한 인용오류 5건**, 특히 **날조 인용("Williams 2022")**을 잡는지 검증.
> **비교군:** `medsci-skills/verify-refs`(이미 벤치마크 완료 — 날조를 `OK`로 통과시킴).
> **결론 선요약:** **AIPOCH는 날조 인용을 잡지 못한다.** 다만 medsci처럼 **틀린 `OK`를 내는 게 아니라, 애초에 판정을 내지 않는다.** 이 차이가 차용 판단의 핵심이다.

---

## 1. 게이트 확인 (실행 전 필수)

| 항목 | 결과 |
|---|---|
| 라이선스 | **MIT** (`LICENSE`, Copyright (c) 2026 AIpoch) — 차용 가능 |
| 위험 호출 (`subprocess`/`os.system`/`eval`/`exec`/`pickle`) | 후보 스크립트 3종에서 **0건** (grep 검증) |
| 네트워크 전송 대상 | 공개 API만 — `api.crossref.org`, `eutils.ncbi.nlm.nih.gov`, `openretractions.com`. **외부 유출·인증정보 전송 없음** |
| 판정 | ✅ **실행 안전** — 게이트 통과 |

검사 대상: `crossref-database/scripts/query_crossref.py`, `crossref-database/scripts/validate_skill.py`, `retraction-watcher/scripts/main.py`

---

## 2. 스킬 선정 근거

605개 중 인용검증 관련 후보를 grep으로 좁혔다. 주의: `grep -i "authentic|fabricat|hallucinat"`는 **~300개**가 걸리는데, 대부분 무관한 보일러플레이트다(예: `buffer-calculator/SKILL.md` → "Do not fabricate molecular weights"). 이걸 히트로 세면 안 된다.

실제 후보와 선정 결과:

| 스킬 | 스크립트 | 스코프 | 선정 |
|---|---|---|---|
| `awesome/Academic Writing/reference-integrity-checker` | **없음** (SKILL.md + references/ 7개 .md만) | 인용-주장 **정합성**(mismatch/overextension/drift) | ✅ 평가 — README "authenticity hard rules"의 실체 |
| `awesome/Evidence Insight/paper-to-claim-verifier` | **없음** (SKILL.md + references/ 9개 .md만) | 주장-근거 **지지 여부** | ✅ 평가 — 이름이 "verifier" |
| `scientific/Evidence Insight/crossref-database` | ✅ `query_crossref.py` | CrossRef **원시 질의** | ✅ 실행 — 유일한 결정론적 후보 |
| `scientific/Evidence Insight/retraction-watcher` | ✅ `main.py` | **알려진** DOI/PMID의 철회 여부 | ⚠️ 해당없음 — 날조는 DOI가 없어 입력 자체가 불가 |

### README 주장의 실체 추적

AIPOCH README L225가 표방하는 문구:

> `* **Literature authenticity constraints**: Implementing hard rules`

이 "hard rules"를 실제로 따라가면 `reference-integrity-checker/references/hard-rules.md`(821 B) 및 `paper-to-claim-verifier/references/literature-integrity-rules.md`가 나온다. 내용은 전부 **산문 지시문**이다:

```
7. Never fabricate references, PMIDs, DOIs, source conclusions, or consensus positions.
```
```
Never fabricate references, PMIDs, DOIs, trial identifiers, findings, bibliographic details...
When source access or certainty is incomplete, label the point as unverified...
```

**★ 핵심 발견:** 이 "authenticity hard rules"는 **에이전트 자신이 날조하지 말라**는 *출력 제약*이지, **사용자가 들고 온 인용의 날조를 탐지하는 메커니즘이 아니다.** 방향이 반대다. 우리가 필요한 건 후자인데 AIPOCH가 제공하는 건 전자다.

---

## 3. 케이스별 판정 표 (실제 실행)

실행: `python3 query_crossref.py --query "<질의>" --limit 5` (habanero 2.9.2, 8케이스 전건 실행)

**대조군 제목은 CrossRef DOI 조회로 정본을 받아 축약 없이 그대로 사용**(앞선 시험의 실패 원인 회피). 확인된 정본:

> 📌 **읽는 법 주의:** C2·C3·C5·CTRL1-3은 **틀린 인용 문자열이 아니라 CrossRef 정본 제목**으로 질의했다. 즉 **도구에 가장 유리한 조건**(올바른 메타데이터를 떠먹여 준 상태)에서 시험했고, **그런데도 판정이 나오지 않는다**는 것이 결과다. 이는 결론을 약화시키는 게 아니라 강화한다. C1(날조)만은 실존 정본이 없으므로 주장된 서지(Williams 2022 + 주제어)로 질의했다.

| DOI | 1저자 | 연도 | 제목(정본) |
|---|---|---|---|
| `10.1038/s41379-021-00911-w` | Farahmand | 2022 | Deep learning trained on hematoxylin and eosin tumor region of Interest predicts HER2 status... |
| `10.1093/bib/bbac490` | Koudijs | **2022**(CrossRef 기준) | Validation of transcriptome signature reversion for drug repurposing in oncology |
| `10.1038/s41746-025-02334-2` | Kaczmarzyk | 2026 | Towards interpretable prediction of recurrence risk in breast cancer using pathology foundation models |
| `10.1093/bib/bbab294` | Sharifi-Noghabi | 2021 | Drug sensitivity prediction from cell line-based pharmacogenomics data: guidelines... |
| `10.1016/j.cell.2026.04.023` | Shulman | 2026 | AI-predicted spatial transcriptomics unlocks breast cancer biomarkers from pathology |

### 판정 표

| # | 케이스 | 진실 | AIPOCH `query_crossref.py` 실행 결과 | AIPOCH 판정 | medsci `verify-refs` |
|---|---|---|---|---|---|
| **C1** | **"Williams 2022" LINCS reversal** ★ | **날조(NOT FOUND)** | exit=0, **5건 반환**, Williams 없음. top-5 = Hendrickx/de Souza/Doss/Bender | **❌ 판정 없음**(원시 JSON) | **❌ `OK` = 놓침(위험)** |
| C2 | Sharifi-Noghabi 2024→2021 | 실존, 연도 오류 | exit=0, 5건. top-1 = Sharifi-Noghabi **2021** | ❌ 판정 없음 | ✅ `MISMATCH` |
| C3 | Path2Space "Kaminski"→Shulman | 실존, 저자 오류 | exit=0, 5건. top-2 = **Shulman 2026**, Kaminski 없음 | ❌ 판정 없음 | ✅ `MISMATCH` |
| C4 | "Spearman ≈0.2–0.25" | 초록에 없는 수치 | exit=0, 5건(무관한 표·논문) | ⚪ 범위 밖(서지 아님) | ⚪ 범위 밖 |
| C5 | MAKO="subtype 벤치마크" | ROR-P 오프레이밍 | exit=0, 5건. top-1 = Kaczmarzyk 2026 | ⚪ 범위 밖(서지는 정확) | ⚪ 범위 밖 |
| **CTRL1** | Farahmand 2022 (실존) | genuine | exit=0, **5건**. top-1 = Farahmand 2022 ✔ | ❌ 판정 없음 | — |
| **CTRL2** | Koudijs (실존) | genuine | exit=0, **5건**. top-1 = Koudijs 2022 ✔ | ❌ 판정 없음 | — |
| **CTRL3** | Kaczmarzyk (실존) | genuine | exit=0, **5건**. top-1 = Kaczmarzyk 2026 ✔ | ❌ 판정 없음 | — |

### ★ 결정적 관찰

**8건 전부가 `exit=0`, 정확히 `5건 반환`, `판정 없음`이다.** 즉 **날조 인용(C1)과 진짜 논문 3건(CTRL1-3)의 도구 출력이 보고 수준에서 구별되지 않는다.**

- **"결과가 N건 나왔으니 OK"** 라는 휴리스틱(= medsci `verify_refs.py` L557-560의 로직)을 이 출력에 적용하면 **8건 전부, 날조 포함해서 통과**시킨다.
- C1의 top-5에는 `de Souza 2026 | Guarded LINCS/L1000 reversal of severe equine asthma...` 처럼 **주제가 정확히 맞아 보이는** 논문이 섞여 나온다. "결과도 나왔고 주제도 맞다"고 판단하는 순진한 LLM은 **날조를 승인**한다.

### 우리가 외부에서 덧댄 가드(= AIPOCH에 없는 것)

벤치마크 하네스에 **"주장된 1저자가 top-5에 있는가"** 한 줄을 넣어봤다. 이것만으로 갈린다:

| 케이스 | claimed author in top-5 |
|---|---|
| C1-FABRICATED | **False** ← 잡힘 |
| C3-AUTHOR | **False** ← 잡힘 |
| C2 / C5 / CTRL1 / CTRL2 / CTRL3 | True |

**이 가드는 AIPOCH 어디에도 없다.** 우리가 이 보고서를 위해 직접 짠 것이다(`scratchpad/bench_aipoch.py`).

---

## 4. 못 잡은 것의 코드 근거

### (a) `crossref-database` — 스크립트에도, SKILL.md에도 게이트가 없음

**스크립트 측.** `scientific-skills/Evidence Insight/crossref-database/scripts/query_crossref.py` **전체 45줄**. 핵심:

- **L32:** `results = cr.works(query=args.query, limit=args.limit)` — CrossRef에 질의
- **L34:** `print(json.dumps(results['message']['items'], indent=2, ensure_ascii=False))` — **받은 걸 그대로 출력**
- **L40-42:** `except` — 네트워크 오류만 처리

**유사도 비교·저자 대조·연도 대조·존재 판정이 한 줄도 없다.**

**SKILL.md 측(138줄)도 확인했다** — 스킬은 스크립트+지시문이므로, LLM에게 대조를 시키는 단계가 여기 있을 수 있어 정독했다. 결과: **없다.**
- L19-24 유스케이스는 전부 **retrieve / search / lookup** — DB 접근 도구다. L22 "verify or enrich citation records"는 유스케이스 문구일 뿐 **대조 절차가 아니다.**
- L94-99 "Validation and Safety Rules"는 일반 보일러플레이트다: `Validate required inputs before execution`(입력 **존재** 확인), `Do not fabricate ... references`(**에이전트 자신의** 날조 금지). **반환된 메타데이터를 인용된 서지와 대조하라는 지시가 없다.**
- 즉 **"반환 결과의 저자/연도/제목이 주장된 인용과 일치하는가"를 확인하라는 단계가 스크립트에도 지시문에도 존재하지 않는다.**

이 스크립트는 **DB 질의 도구**지 검증기가 아니다. CrossRef 서지 검색은 질의가 헛소리여도 **항상 순위 매긴 결과를 반환**하므로, 반환 자체는 실존의 증거가 **전혀 아니다**. medsci L557-560과 **같은 함정이며, 가드가 아예 없다는 점에서 더 노출돼 있다.**

> ⚖️ **공정성 단서:** `crossref-database`는 스스로를 "검증기"라고 표방한 적이 없다. 따라서 **"AIPOCH의 검증기가 실패했다"는 부정확한 서술**이다. 정확한 서술은 → **"AIPOCH에는 판정을 내는 결정론적 인용-진위 검증기가 아예 없다. 가장 근접한 결정론적 자산이 가드 없는 원시 CrossRef 질의다."**

### (b) `reference-integrity-checker` — 실행 코드 0줄, 스코프도 다름

- 디렉토리 전체 = `SKILL.md`(270줄) + `references/*.md` 7개(합계 **~4 KB**) + eval JSON. **`scripts/` 없음. 실행 가능한 코드 0줄.**
- **스코프 자체가 존재 검증이 아니다.** SKILL.md L14-19가 정의하는 대상은 mismatch / overextension / second-hand / quote drift — 전부 **"인용이 주장을 지지하는가"**이지 **"인용이 실존하는가"**가 아니다.
- 오히려 **날조를 잡지 못하도록 설계돼 있다.** `hard-rules.md` 4번:
  > `4. Never certify claim-reference alignment when the source text is unavailable and the evidence remains unclear.`

  날조 인용은 정의상 원문이 없다 → 이 규칙이 발동 → 스킬은 **"판정 보류, 원문을 업로드하라"**(SKILL.md L222-224 §H)로 빠진다. **날조라고 말하지 않는다.**

### (b-2) `paper-to-claim-verifier` — 이름은 "verifier"지만 존재 검증 단계가 없음

이름이 "verifier"라 **존재 검증 워크플로가 숨어 있을 수 있어 SKILL.md(326줄)를 직접 확인**했다. 결과: **DB 조회·존재 확인 단계가 없다.**
- `scripts/` **없음. 실행 코드 0줄.**
- **L54-58 Input Validation** — 입력은 `a scientific claim plus one or more cited papers`, `a title / PMID / DOI / citation string **attached to a claim**`. 즉 **DOI/PMID는 조회 대상이 아니라 "주장에 딸려온 꼬리표"**로 받는다.
- **L60-66 예시**가 스코프를 확정한다: *"Does this paper really support the claim...?"* / *"Did the original study show causation, or only association?"* / *"Check whether this figure caption statement is citation drift."* — **전부 "주어진 원문이 주장을 지지하는가"**다. **"이 인용이 실존하는가"를 묻는 예시가 하나도 없다.**
- L296은 `reference-integrity-checker`와 동일한 산문 하드룰(`Never fabricate references, PMIDs, DOIs...`) — **자기 출력 제약**.

**→ 두 LLM 스킬 모두 인용-주장 **정합성** 판정기이며, **존재 검증 메커니즘이 없다.** 이것이 본 벤치마크의 헤드라인 발견이다.** (README가 지목한 스킬을 직접 읽고 내린 판정이므로 "엉뚱한 스킬을 봤다"는 반박은 성립하지 않는다.)

### (c) `retraction-watcher` — 입력 불가

`main.py`는 **이미 알고 있는** DOI/PMID의 철회 여부를 조회한다(L276 CrossRef, L331 NCBI, L375 openretractions). **날조 인용은 DOI가 없으므로 입력 자체가 성립하지 않는다.** 우리 C1에 해당없음.

---

## 5. medsci-skills 대비 우열

**둘 다 날조를 못 잡는다. 그러나 실패 방식이 다르다 — 이게 중요하다.**

| | medsci-skills `verify-refs` | AIPOCH |
|---|---|---|
| C1 날조 | **`OK` 출력 = 적극적 오판(false clear)** | **판정 없음**(스크립트) / **"확인 불가, 원문 달라" 보류**(LLM 스킬) |
| C2 연도오류 | ✅ `MISMATCH` | ❌ 판정 없음 |
| C3 저자오류 | ✅ `MISMATCH` | ❌ 판정 없음 |
| 결정론적 판정 | ✅ 있음(단, 게이트 결함) | **❌ 없음** |
| 위험도 | **높음** — `OK`는 사람을 안심시켜 검증을 종료시킴 | 중간 — 아무 보장도 안 하지만, 틀린 안심도 안 줌 |

**판정:**
- **서지 검증 능력 자체는 medsci가 우위다.** medsci는 C2·C3를 결정론적으로 잡는다. AIPOCH는 어떤 케이스에도 판정을 내지 않는다.
- **AIPOCH가 나은 단 하나의 지점:** C1에서 **틀린 `OK`를 주지 않는다.** medsci의 `OK`는 "검증됨"으로 읽혀 사람이 확인을 멈추게 만든다 — 우리가 실제로 당한 사고 경로다. AIPOCH의 보류는 최소한 사람을 멈춰 세운다.
- 단, 이걸 AIPOCH의 **설계적 미덕으로 과대평가하면 안 된다.** AIPOCH는 **애초에 시도하지 않아서** 틀리지 않은 것에 가깝다. "판정을 안 하니 틀린 판정도 없다"는 안전이 아니라 **부재**다.

---

## 6. 차용 판단

### 결론: **인용검증 목적으로는 차용하지 않는다.** 단, 두 조각은 조건부로 가치가 있다.

**차용 안 함 (❌):**
- `reference-integrity-checker` / `paper-to-claim-verifier`를 **인용 진위 검증기로 도입 금지.** 우리 DoD("실제로 돌려봤는가", 결정론적 재계산)와 구조적으로 안 맞는다 — **실행할 코드가 없다.** LLM 판단만으로 하는 검증은 우리가 이미 겪은 실패의 원인이지 해법이 아니다.
- README의 "Literature authenticity constraints"를 **우리가 필요로 하는 기능으로 오독하지 말 것.** 이건 에이전트 출력 제약이지 탐지기가 아니다.

**조건부 차용 (⚠️):**
1. **`reference-integrity-checker`의 산문 체크리스트** — 인용 **진위**가 아니라 **오프레이밍/과확대**(우리 C4·C5 유형) 점검용 **사람용 리뷰 체크리스트**로는 쓸 만하다. C4(없는 수치)·C5(스코프 오프레이밍)는 서지 검증기가 원래 못 잡는 영역인데, 이 스킬의 "overextension / quote drift" 축이 정확히 그 영역이다. **단 반드시 "판정"이 아니라 "리뷰 프롬프트"로만.**
2. **`retraction-watcher/main.py`** — 별개 용도로 유용. 우리 인용 목록의 **DOI가 확정된 것들**에 대해 철회 여부를 결정론적으로 조회한다(3개 소스 교차). 이건 우리 파이프라인에 **없는 기능**이고 게이트도 통과했다. 인용검증과 분리해 별도 검토 권장.

**우리가 실제로 해야 할 일 (본 벤치마크의 실질적 산출):**
> AIPOCH도 medsci도 날조를 못 잡는다. **필요한 건 "질의 결과 존재 → OK"를 끊는 가드**다. 본 벤치마크에서 **"주장된 1저자/연도가 top-N에 있는가" 한 줄만으로 C1·C3가 갈렸다**(§3). medsci `verify_refs.py`의 유사도 가드가 OpenAlex 경로에만 있는 걸 **PubMed/CrossRef 경로에도 적용**(L557-560 수정)하는 게 AIPOCH 차용보다 비용 대비 효과가 크다.

---

## 7. 미검증 · 한계 (정직 보고)

- ⚠️ **LLM 스킬 2종(`reference-integrity-checker`, `paper-to-claim-verifier`)은 실제로 LLM에 물려 돌리지 않았다.** 본 보고서의 해당 판정은 **SKILL.md·references/ 정독에 근거한 구조 분석**이지 실행 결과가 아니다. "원문 없으면 보류로 빠진다"는 `hard-rules.md` 4번·SKILL.md §H의 **문서 근거에 따른 예측**이며, **실제 LLM 출력으로 검증되지 않았다.** 다만 **실행 코드가 0줄이라는 사실 자체는 검증됐고**(디렉토리 확인), 그것만으로 우리 DoD 부적합 판정은 성립한다.
- ⚠️ **C4·C5는 "범위 밖"으로 처리했다.** 두 케이스는 서지 검증이 아니라 초록 내용 대조(C4)·스코프 프레이밍(C5) 문제다. `query_crossref.py`를 돌리긴 했으나 그 결과는 판정 근거가 아니다.
- ⚠️ **`query_crossref.py`는 라이브러리 부재로 즉시 실패한다.** `habanero` 미설치 시 L7-8에서 exit(1). 본 벤치마크는 `pip install habanero`(2.9.2) 후 실행했다. AIPOCH에 `requirements.txt` 없음.
- ⚠️ **605개 중 4개만 심층 검토했다.** grep 기반 선정이라 다른 명명 규칙의 스킬을 놓쳤을 수 있다. 단 "authenticity/citation/verify" 축으로는 이 4개가 최유력이고, **후보 4종의 SKILL.md를 전부 정독**했으며(`reference-integrity-checker` 270줄 · `paper-to-claim-verifier` 326줄 · `crossref-database` 138줄 · `retraction-watcher` 스크립트), README가 지목하는 스킬을 직접 추적해 평가했으므로 **"엉뚱한 스킬을 벤치마크했다"는 반박은 성립하지 않는다.**
- ℹ️ **"게이트 없음" 판정의 근거 범위:** 스크립트(45줄) **및** SKILL.md 지시문(138줄)을 모두 읽고 내렸다. 다만 `crossref-database` SKILL.md에 일반적 "validation summary" 문구(L96)는 존재한다 — 이는 **저자/연도 대조 게이트가 아니라** "무엇을 확인했는지 요약하라"는 서술 지시다. 이 구분을 근거로 "게이트 없음"이라 판정했다.
- ⚠️ **CrossRef 결과는 2026-07-17 시점 스냅샷.** 랭킹은 시간에 따라 변한다. C1의 "5건 반환"은 재현되겠지만 개별 top-5 항목은 달라질 수 있다.
- ℹ️ Koudijs는 우리 정본이 2023인데 **CrossRef는 2022**로 반환한다(온라인 선공개 vs 지면 호). 오류가 아니라 날짜 필드 차이 — 다만 **연도 기반 자동 판정을 짤 때 이런 케이스가 오탐을 만든다**는 점은 설계 시 반영 필요.

---

## 부록: 재현

```bash
pip install habanero            # 2.9.2
python3 /tmp/.../scratchpad/bench_aipoch.py
```
- 벤치마크 하네스: `scratchpad/bench_aipoch.py` (8케이스, 우리가 작성 — AIPOCH 자산 아님)
- 대상 스크립트: `medical-research-skills/scientific-skills/Evidence Insight/crossref-database/scripts/query_crossref.py` (45줄)

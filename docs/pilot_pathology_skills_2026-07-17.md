# Pilot: 병리·이미지(본진) 공개 Agent Skill 차용 검토 (2026-07-17)

> **목적:** §5.6 스킬 검토가 **인용검증만** 보고 본진(병리 WSI/파운데이션 모델)을 안 봤다는 kkkim 지적에 따라, 공개 Agent Skill 중 **BIOP02 본진에 차용할 것이 있는지** 조사.
> **판정 기준:** `docs/HARNESS_REVIEW_2026-07-17.md` §4.5 — star 수 금지, **합격 기준 = 우리가 실제로 당한 실패셋**.
> **결론 선요약:** **본진(병리)에 차용할 스킬은 없다.** 후보 5종 전부 **실행코드 0줄**이고, 우리 실패 6건 중 **0건**을 잡는다.
> 부수적으로 **§5.6의 K-Dense LOW 판정은 근거가 틀렸다**(결론은 유지) — 아래 §5.

---

## 1. 조사 범위 (뭘 뒤졌나)

| 대상 | 규모 | 조사 방법 |
|---|---|---|
| AIPOCH `medical-research-skills` | **605** SKILL.md | 로컬 클론 grep + 파일트리 + SKILL.md 정독 |
| Aperivue `medsci-skills` | **57** SKILL.md | 로컬 클론 grep + 스크립트 정독 |
| K-Dense `scientific-agent-skills` | **149** SKILL.md | **신규 클론**(§5.6 판정 검증용) |
| `anthropics/life-sciences` | 5 skills | WebFetch |
| Harvard `ToolUniverse` | ~1000 tools / 68 workflows | WebFetch |
| ClawBio (스크래치패드에 있던 미상 저장소) | — | 신원 확인만 (§7) |

검색 패턴: `pathology|histolog|whole.slide|WSI|openslide|tile|foundation model|MIL|attention`
+ **우리 실패셋 직접 grep**: `incomplete` / `HF_HOME|hf_hub` / `nohup|detached|conda activate` / `carriage|\r|dos2unix` / `register token|CLS token` / `checksum|md5`.

---

## 2. 후보별 표 (본진 = 병리·이미지)

| 후보 | 실존 | 라이선스 | **실행코드** | 우리 실패셋 적용 | 판정 |
|---|---|---|---|---|---|
| AIPOCH `Data Analysis/histolab` | ✅ | 리포 MIT / **frontmatter `MIT`** ⚠️(§6) | **0줄** (SKILL.md + references/ 5개 .md) | **0/6** | ❌ 차용 불가 |
| AIPOCH `Data Analysis/pathml` | ✅ | MIT | **0줄** (SKILL.md만) | **0/6** | ❌ |
| AIPOCH `Data Analysis/pathology-roi-selector` | ✅ | MIT | **0줄 — 그런데 "있다"고 광고함** ★§4 | **0/6** | ❌ **역효과** |
| K-Dense `skills/histolab` | ✅ | 리포 MIT / frontmatter `Apache-2.0` ⚠️ | **0줄** | **0/6** | ❌ |
| K-Dense `skills/pathml` | ✅ | MIT | **0줄** | **0/6** | ❌ |
| `anthropics/life-sciences` | ✅ | 미확인(LICENSE 파일 미표기) | — | **해당없음** | ❌ 도메인 불일치 |
| Harvard `ToolUniverse` | ✅ | **Apache-2.0** | 라이브러리(있음) | **해당없음** | ❌ 도메인 불일치 |
| medsci `preprocess-imaging` / `uncertainty-imaging` / `radiomics-ml` | ✅ | MIT | 있음(각 3파일) | **0/6** — **방사선(CT/MRI) 스코프**, WSI 아님 | ❌ |

### 실패셋 대조 (§4.5-(c) 집행)

| # | 우리가 실제로 당한 실패 | 잡는 스킬 |
|---|---|---|
| ① | HF 캐시 `.incomplete`인데 완료로 착각 | **없음** — 두 리포 통틀어 `HF_HOME|hf_hub` grep **0건** |
| ② | detached shell conda 없어 임베딩 침묵 사망 | **없음** |
| ③ | csv `\r` → openslide "missing" | **없음** (`dos2unix|carriage` 히트는 전부 워드/PPT 문서 스킬) |
| ④ | Virchow2 register token 혼입 | **없음** — `register token|CLS token` grep **0건** |
| ⑤ | BRCA manifest coords 없어 재타일링 | **없음** |
| ⑥ | n=187/85 혼동 | **없음** (§6 참조 — 유일한 근접 후보가 구조적으로 불가) |

**0/6.** 이 6건은 전부 **운영·인프라 함정**인데, 공개 스킬은 **방법론 산문**과 **라이브러리 사용법**만 다룬다. 겹치는 층이 아니다.

---

## 3. 왜 "0줄"이 곧 결과인가 — histolab/pathml의 실체

AIPOCH·K-Dense의 `histolab`·`pathml`은 **스킬이 아니라 기존 pip 라이브러리 사용설명서**다. SKILL.md 본문은 이런 형태다:

```python
from histolab.slide import Slide
from histolab.tiler import RandomTiler
slide = Slide("slide.svs", processed_path="output/")
tiler = RandomTiler(tile_size=(512, 512), n_tiles=100, level=0, seed=42)
tiler.extract(slide)
```

- **우리는 이미 이 층을 지났다.** `agents/embedding/scripts/tile_wsi.py`(256×256 @20×, Otsu, per-patient cap 5000)는 histolab의 `RandomTiler`보다 **우리 요구에 특화**돼 있다 — histolab이 제공하는 건 랜덤/그리드 타일러이지 per-patient cap도, 우리 coords 계약도 없다.
- **차용해도 얻는 게 없고 잃는 게 있다.** histolab 도입은 openslide/pyvips 위에 **의존성 한 겹**을 더 얹는데, 우리 실패 ③(csv `\r`)·⑤(coords 부재)는 **바로 그 경계면**에서 났다. 추상화가 늘면 이 경계가 더 흐려진다.
- **DoD 불합치.** 우리 DoD는 **결정론적 재계산**인데, 산문 스킬은 재계산할 대상이 없다. (§철칙 — AIPOCH 인용검증에서 이미 확인된 패턴의 반복.)

---

## 4. ★ 핵심 발견 — `pathology-roi-selector`: 없는 스크립트를 광고하고, 자기 eval이 92/100을 줬다

`pathology-roi-selector/SKILL.md`는 실행 경로를 **명시적으로 광고**한다:

```
- Packaged executable path(s): `scripts/main.py`.
...
python -m py_compile scripts/main.py
python scripts/main.py --help
```

**그런데 `scripts/` 디렉토리 자체가 없다.** 실제 내용물은 3개뿐:

```
POLISH_CHANGELOG.md   611 B
SKILL.md            6,998 B
eval_report_pathology-roi-selector_result.json  10,839 B
```

그리고 **그 eval_report가 스스로에게 준 점수:**

| 항목 | 값 |
|---|---|
| `veto_gates.skill_veto.gate` | **PASS** |
| `veto_gates.research_veto.code_usability.result` | **PASS** |
| `veto_gates.research_veto.code_usability.detail` | **"Scripts parse without errors"** |
| `static_score.subtotal` | **92 / 100** |

**존재하지 않는 스크립트가 "에러 없이 파싱된다"고 PASS 판정을 받았다.**

**전수 확인 (추정 아님):** AIPOCH 605개 중 **"Packaged executable path"를 광고하는 SKILL.md = 201개**, 그중 **`.py`를 0개 배송하는 것 = 15개**.

> ⚠️ **이건 우리 CLAUDE.md가 이미 금지한 사고의 외부 사례다.**
> - *"계획을 자산으로 쓰지 않는다. 있다고 적혀 있으면 열어서 확인한다."* → SKILL.md의 "packaged executable"은 **계획이었지 자산이 아니었다.**
> - *"도구가 '못 찾겠다'고 한 것을 통과로 처리하는 것"* → 여기선 한술 더 떠 **도구가 존재하지 않는데 PASS**다.
>
> **교훈: 스킬 저장소의 self-eval 점수를 게이트로 쓰면 안 된다.** medsci `verify-refs`의 `submission_safe=True`와 정확히 같은 실패 유형(자기 보증).

---

## 5. §5.6 K-Dense LOW 판정 검증 — **결론은 맞고, 근거는 틀렸다**

§5.6 원문: *"신약 discovery/ADMET/docking 중심이라 우리와 겹침 적음"* → LOW.

**실측 결과 — 이 근거는 사실이 아니다.** K-Dense(149 skills, MIT)에는 **병리 스킬이 실제로 있다**:

| K-Dense 스킬 | 내용 |
|---|---|
| `skills/histolab` | WSI 타일 추출·조직 검출 — **우리 본진과 정면으로 겹친다** |
| `skills/pathml` | computational pathology 툴킷 |
| `optimize-for-gpu/references/cucim.md` | GPU WSI 읽기(RAPIDS cuCIM) 언급 |

즉 **"겹침이 적어서 LOW"는 틀렸다 — 겹치는 스킬이 있었다.**
**그럼에도 LOW 결론은 유지된다.** 이유가 다르다: **두 스킬 다 실행코드 0줄**이고(위 표), 우리 실패셋 **0/6**이다.

> **이게 §4.5-(b)가 왜 필요한지 보여준다.** 원문은 K-Dense를 **star 수 / 도메인 인상**만으로 훑고 "겹침 적음"이라 적었다. 실제로는 **열어보지 않아서** 병리 스킬의 존재 자체를 놓쳤다. 우연히 결론이 같았을 뿐이다.
>
> **AIPOCH `histolab`과 K-Dense `histolab`은 파일 구조·references 파일명 5종이 동일하지만 내용은 다르다**(md5 전건 불일치, SKILL.md 본문 diff 101줄) — 공통 조상에서 갈라진 병렬 산물로 보인다. **같은 장르(라이브러리 문서 래퍼)의 중복**이지 독립 검증 2건이 아니다.

---

## 6. 통계·그림 쪽 (sjpark 모델링 · Fig 작업)

**여기가 유일하게 실행코드가 있는 구역이다.** medsci-skills(MIT, Aperivue):

| 스킬 | 실행코드 | 내용 | 우리 적용 |
|---|---|---|---|
| `analyze-stats` | **25 파일** | `references/templates/` — survival_analysis.py, forest_plot.py, regression.py, diagnostic_accuracy.py, table1_demographics.py … + `check_separation.py`(완전분리 검출) | ⭕ **템플릿 참조 가치 있음** |
| `make-figures` | **16 파일** | `render_core_figures.py`, `critic_figure.py`, `derive_figure_legend_counts.py`, STROBE/PRISMA 템플릿 빌더 | ⭕ 제한적 |
| `model-validation/check_split_leakage.py` | 있음 | patient-ID 집합연산으로 split 교차 **증명** + seed 기록 강제 | ❌ **이미 있음** ↓ |
| `model-evaluation/check_metric_reporting.py` | 있음 | AUROC/AUPRC **명명 여부** 린터 | ❌ **구조적 불가** ↓ |

### `check_split_leakage.py` — 차용 불필요 (우리 게 더 강하다)

우리는 이미 `agents/modeling/scripts/verify_split_integrity.py`(85줄)를 갖고 있고, **더 엄격하다**:
- medsci: **patient-level** disjointness만.
- **우리: patient-level(`case_id`) + site-level(TCGA TSS 코드) 둘 다.** TSS 누출은 medsci가 보지 않는 축이다.

§4.5 *"검증 게이트 설계는 자작 유지"*가 여기서도 실증됐다 — **차용했다면 오히려 후퇴였다.**

### `check_metric_reporting.py` — 실패 ⑥(n=187/85)을 못 잡는다 (코드로 확정)

docstring이 스스로 밝힌다:

> *"A conservative **presence linter** … It checks **which metrics are named** (and whether confidence intervals are mentioned); **it does not recompute a number.**"*

→ **n이 일관되는지 대조하지 않는다.** 메트릭 **이름이 적혔는지**만 본다.
우리 ⑥은 *"n=187과 85가 뒤섞였다"* 는 **수치 정합성** 문제 → **범위 밖.** (읽어서 판정, 실행 불필요.)

### 게이트 (차용 후보 = analyze-stats / make-figures)

| 항목 | 결과 |
|---|---|
| LICENSE 실파일 | **MIT** (`medsci-skills/LICENSE`, Aperivue) ✅ |
| `eval(`/`exec(`/`os.system`/`pickle.load` | **0건** ✅ |
| `subprocess` | **1건** — `make-figures/generate_visual_abstract.py:269` |
| ↳ 실체 | `soffice --headless --convert-to png` (LibreOffice CLI). **고정 argv 리스트, `shell=True` 없음, timeout=30, 사용자 입력 미주입** → ✅ 안전 |
| 외부 전송 | 후보 스크립트에서 미발견 |

**⚠️ 라이선스 표기 불일치 (차용 전 확인 필요):** AIPOCH `histolab/SKILL.md` frontmatter는 `license: MIT`라 적었으나 **histolab 원 라이브러리는 Apache-2.0**이고 K-Dense는 `Apache-2.0`이라 적었다. **스킬 frontmatter의 license 필드는 신뢰할 수 없다** — 원 라이브러리 라이선스를 직접 확인해야 한다. (본 건은 차용 안 하므로 실무 영향 없음.)

---

## 7. ClawBio — 신원 확인 (차용 후보 아님)

스크래치패드에 있었으나 브리핑에 없던 저장소. 확인 결과:
- `https://github.com/ClawBio/ClawBio.git`, **MIT (Copyright 2026 Manuel Corpas)**, 최신 커밋 2026-07-17.
- **제3자 공개 저장소**(우리 자작 아님). 유전체/집단유전 중심(`scrna-embedding`, `rnaseq-de`, `pathway-enricher`, `ancestry-risk-profiler`, `fine-mapping` …).
- **병리·WSI 스킬 없음.** `cell-detection`이 이름상 근접하나 본진(WSI 타일→FM 임베딩)과 층이 다르다.
- 본 조사 범위 밖 — **미평가**로 남긴다.

---

## 8. 차용 판단

| 대상 | 판단 |
|---|---|
| **본진(병리 WSI/FM 임베딩)** | **차용할 것 없음.** 후보 5종 전부 실행코드 0줄, 실패셋 0/6. **이것이 결론이다 — 억지 후보를 만들지 않았다.** |
| ToolUniverse (Apache-2.0) | **본진엔 부적합**(병리/WSI 도구 없음, API·DB 지향). 단 **Paper B therapeutic evidence** 맥락에서 **별건 검토 여지** — 본 조사 범위 밖, 미평가. |
| `anthropics/life-sciences` | **부적합.** 5개 스킬 전부 single-cell/nextflow. 병리 없음. |
| K-Dense | **LOW 유지**(근거는 §5로 정정). |
| **medsci `analyze-stats`** | **유일한 실질 후보.** MIT·실행코드·위험호출 없음. **단 "차용"이 아니라 "템플릿 참조"** — sjpark 생존분석/forest plot 작성 시 참고. **우리 파이프라인에 끼워넣지 않는다.** |
| medsci `check_*.py` 검증기 | **차용 안 함.** 우리 Critic 7-point와 중복이고, split 건은 **우리 게 더 엄격**(site-level 추가). §4.5 "검증 게이트 자작 유지". |

**한 줄 요약:** **병리 이미지 도메인에 차용 가능한 공개 Agent Skill은 존재하지 않는다.** 공개 스킬 생태계는 (a) 방법론 산문, (b) 기존 라이브러리 사용설명서 두 층에 몰려 있고, **우리가 실제로 피 흘리는 층(운영·인프라 함정, 결정론적 재계산)은 아무도 다루지 않는다.**

---

## 9. 한계 (미검증 · 정직 보고)

- **실행 시험 안 함.** 본진 후보 5종은 **실행할 코드가 없어서** 실행 파일럿이 성립하지 않는다. 판정은 **파일트리 + SKILL.md·eval_report 정독** 기반이다. 인용검증 파일럿처럼 8케이스를 돌린 게 아니다.
- **`analyze-stats` 템플릿 25개를 실행해보지 않았다.** MIT·위험호출 0건까지만 확인. **"참조 가치 있음"은 코드를 읽은 인상이지 실측이 아니다** — 실제 채택 전 sjpark가 1건 파일럿 필요.
- **AIPOCH 605 / K-Dense 149를 전수 정독하지 않았다.** grep 패턴 기반 후보 선별 → 선별된 것만 정독. **패턴에 안 걸린 병리 스킬이 있을 가능성은 배제 못 한다.**
- **`life-sciences` LICENSE 미확인** (WebFetch에서 LICENSE 파일 미표기). 도메인 불일치로 차용 대상이 아니라 추적 안 함.
- **ToolUniverse 내부 미확인.** WebFetch 요약만 — 클론·코드 확인 안 했다. Paper B 맥락 검토는 **별건**.
- **ClawBio 미평가**(§7).
- **`check_metric_reporting.py`는 읽고 판정**했다(docstring 근거). 실행 안 함.

---

## 10. 관련 문서
- 판정 원칙: `docs/HARNESS_REVIEW_2026-07-17.md` §4.5
- 선행 파일럿(인용): `docs/pilot_aipoch_citation_2026-07-17.md`
- 우리 자작 split 검증: `agents/modeling/scripts/verify_split_integrity.py`
- 우리 자작 인용 검증: `agents/critic/scripts/verify_citations.py`
- 실패셋 출처: `experiments/kkkim/20260717_multifm_robustness/RESUME.md`, `~/.claude/projects/-home-kkkim/memory/infra_hf_fm_embedding.md`

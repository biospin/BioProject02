# Critic G2 — 부록: 블로커 2 원인 규명 · 블로커 4 신규 · 블로커 1 정정

> reviewer: **braveji** · 2026-07-14 · 본문: [`CRITIC_REVIEW_G2_braveji.md`](./CRITIC_REVIEW_G2_braveji.md) · 기계판독: [`critic_report.json`](./critic_report.json)
> `critic_status: reject` **유지** (블로커 1의 *메커니즘* 서술은 정정하되, *결론*은 변하지 않음)

---

## 1. 블로커 2 — 원인 규명 완료: **문서가 낡았다 (stale doc)**

폐 `mil_cost_results.json`은 **두 번 실행됐고, 문서는 1차 실행 기준으로 멈춰 있습니다.**

| 시점 | 커밋 | n_slides | histology_lusc | egfr_activating | kras_g12c |
|---|---|---|---|---|---|
| 07-12 15:35 | `994b187` | 1024 | **0.9247** (152/270) · shuffle 0.4665 | 0.8133 · shuffle **0.6641** | 0.6549 |
| 07-13 13:35 | `9b42d37` | 1026 | **0.939** (153/271) · shuffle 0.4343 | 0.8518 · shuffle **0.4589** | 0.6809 |

- `LUNG_NSCLC/full/LAW_TEST.md`는 `994b187`에서 **한 번만** 커밋됐습니다 → 1차 실행 기준.
- `mil_cost_results.json`은 `9b42d37`에서 **덮어써졌습니다** (785 insertions / 1715 deletions).
- `9b42d37`의 제목은 *"위암 전체-442 held-out MIL …"* 이고, 폐 재실행은 본문의 *"폐/대장 mil_cost_results·embedding manifest·라벨 갱신"* 한 줄에 묻혀 있습니다. **문서가 낡았다는 사실을 아무도 인지하지 못했습니다.**

### 과학적 귀결 — 정본으로 고치면 결과가 **좋아집니다**

| 항목 | 문서(낡음) | 정본 JSON |
|---|---|---|
| 봉인 예측 `histology ≥0.93` | 0.9247 → **점추정 미달**, CI 상한으로 구제 ("≈met") | 0.939 → **명확히 적중** |
| 봉인 예측 `KRAS ≤0.65` | 0.6549 → "라인 바로 위, 사실상 경계" | 0.6809 → **라인 위 (더 벗어남)** |
| EGFR shuffle-null | 0.6641 → 문서가 *"null이 높아 real과 마진 ~0.15로 작음, 신호 약하고 불안정"* 이라 자평 | 0.4589 → **마진 0.39로 훨씬 강함** |

**조치: 3개 문서(LAW_TEST · SCOREBOARD · 개념도)를 정본 JSON 기준으로 재생성하고, `commit_hash`+`split_hash`로 봉인.** 이건 결과를 깎는 수정이 아니라 **원래 결과를 되찾는 수정**입니다.

---

## 2. 블로커 4 (신규) — **완료·실패한 강건성 검정이 문서에서 사라졌습니다**

`COLORECTAL/full/shuffle_null_robustness.json` (커밋 `9b42d37`, 07-13 13:35) — 5-seed shuffle-null 재학습. **kkkim 자체 기준**: `real_auroc > null_mean + 2·null_sd`, 파일 자체가 *"미달 = 우연배제 강건성 미확보로 '실패'로 명시(weak≠zero)"* 라고 선언합니다.

자체 기준 적용 결과:

| endpoint | real | null_mean | null_sd | 임계(mean+2SD) | 판정 | null_seeds |
|---|---|---|---|---|---|---|
| cms1_vs_rest | 0.912 | 0.602 | 0.167 | 0.936 | **FAIL** | 0.714 / 0.387 / 0.794 / 0.633 / 0.479 |
| cms2_vs_rest | 0.871 | 0.461 | 0.054 | 0.569 | PASS | |
| cms3_vs_rest | 0.840 | 0.526 | 0.046 | 0.618 | PASS | |
| cms4_vs_rest | 0.661 | 0.526 | 0.124 | 0.773 | **FAIL** | 0.639 / 0.527 / 0.390 / 0.414 / 0.657 |
| msi_high | 0.918 | 0.525 | 0.107 | 0.739 | PASS | |
| anti_egfr_eligible | 0.705 | 0.537 | 0.065 | 0.667 | PASS | |
| braf_v600 | 0.882 | 0.534 | 0.084 | 0.703 | PASS | |

### 문제는 결과가 아니라 **결과가 사라진 것**입니다

| 시각 | 사건 |
|---|---|
| 07-13 **13:35** | `shuffle_null_robustness.json` 커밋 — 5-seed null **완료**, cms1·cms4 **FAIL** |
| 07-13 **23:28** | `COLORECTAL/full/LAW_TEST.md` 작성 — 각주¹: *"FOLLOW-UP(**non-blocking**): null ~5 seed 평균"* |
| 07-14 **00:19** | `LAW_HELDOUT_SCOREBOARD.md` 작성 — robustness 결과 인용 **0건** |

**10시간 전에 완료되어 2/7 endpoint가 실패한 검정이, 이후 문서에서 "아직 안 한 비차단 후속과제"로 기술됩니다.** 두 문서 어디에도 이 파일이 인용되지 않습니다 (`grep` 0건).

의도로 보지 않습니다 — robustness 파일이 "위암 442장" 제목의 대형 커밋(4026 insertions)에 묻혀 들어갔고, 이후 문서 작성자가 그 존재를 몰랐던 조율 실패로 보입니다. 그러나 **효과는 동일합니다: 실패한 검정이 보이지 않습니다.**

추가로, `afedc6a`의 커밋 메시지는 대장을 *"사전등록 3축 확증"* 으로 선언했습니다. cms1이 자체 강건성 기준에 미달한 지금, 그 "확증" 서술은 재검토 대상입니다.

---

## 3. 블로커 1 — **제 메커니즘 주장을 정정합니다** (결론은 유지)

### 제가 과했던 부분

본문에서 저는 위암 `lauren_diffuse`의 shuffle-null = 0.8232를 근거로 **"라벨무관 교란(bag-size·site·염색)이 AUROC를 구동한다 → 평가/파이프라인 결함 확정"** 이라고 단정했습니다.

**이 단정은 근거가 부족합니다.** 블로커 4에서 나온 5-seed 데이터가 보여주듯, **shuffle-null은 seed마다 크게 요동칩니다** — cms1에서 0.387 ~ 0.794 (SD 0.167). 이런 분산이라면 **단일시드 null 0.8232는 "교란 확정"이 아니라 넓은 null 분포의 높은 draw일 수 있습니다.** 저는 단일시드 수치로 메커니즘을 확정했고, 그건 제가 kkkim을 비판한 바로 그 오류(단일시드 null을 신뢰)입니다. 정정합니다.

### 그럼에도 결론은 바뀌지 않습니다 — 오히려 **더 나빠집니다**

정정된 올바른 서술:

> **단일시드 shuffle-null은 우연배제 근거로 쓸 수 없다.** 따라서 위암에서는 **어느 endpoint도 우연배제가 확립되지 않았다.**

이건 원래 결론보다 **넓은** 문제입니다:

1. **위암 `erbb2_amp` (real 0.6444)** — 관측된 null 분포(mean≈0.5, SD 0.05~0.17)에서 0.644는 **우연과 구별되지 않습니다.** 사전등록의 `blind ≤0.65 적중` 채점은 **여전히 무효**입니다 (신호 없음을 "blind 예측 적중"으로 셀 수 없음). ✅ 원 지적 유지
2. **위암 `lauren_diffuse` (real 0.5364, dev 0.963)** — null과 무관하게, **signet-ring/diffuse라는 H&E 최강 형태축에서 chance 수준**이고 dev↔holdout 격차가 0.43입니다. holdout n=58 (계획 132 대비 **56% 결손**). 양성대조 실패는 **null 없이도 성립**합니다. ✅ 원 지적 유지
3. **범위 확대:** 단일시드 null이 무효라면 이는 위암만의 문제가 아니라 **폐·두경부에도 동일 적용**됩니다. 두 암종 모두 5-seed null이 없습니다. → **두경부 HPV 0.9594(Paper C의 유일한 검정력 있는 CONFIRM)조차 우연배제가 5-seed로 확립되지 않았습니다.** ⚠️ **신규**

### 즉, 정정의 순효과는 지적의 **강화**입니다

- 원래: "위암 파이프라인이 깨졌다" (메커니즘 단정 — 근거 부족)
- 정정: "단일시드 null로는 **어느 암종도** 우연배제를 주장할 수 없다. 5-seed 도구는 이미 있고(`run_openitems_robustness.py`), 대장에만 적용됐으며, 적용된 곳에서 2/7이 실패했다."

**5-seed shuffle-null을 non-blocking → blocking으로 승격**하고, **sealed-forward 3개 암종(폐·위·두경부) 전 endpoint에 적용**해야 합니다. 도구는 이미 있습니다 — `COLORECTAL/full/run_openitems_robustness.py`를 이식하면 됩니다 (`n_tiles` 기록 기능이 있어 bag-size 교란 점검도 겸함).

---

## 3-bis. 블로커 5 (신규) — **owner 외에는 아무도 재현할 수 없습니다**

`critic_robustness_probe.py`를 돌리려다 발견했습니다. 4개 암종 `embedding_manifest`의 `embedding_path` **2,588건 전부**가 개인 컨테이너 홈을 가리킵니다.

| 암종 | 경로 접두사 | 건수 |
|---|---|---|
| LUNG_NSCLC | `/home/kkkim/project/...` | 1052 |
| COLORECTAL | `/home/kkkim/project/...` | 622 |
| HEADNECK_HNSC | `/home/kkkim/project/...` | 472 |
| GASTRIC_STAD | `/home/kkkim/project/...` | 442 |

`CLAUDE.md` §팀 공유 데이터 경로 규칙:

> 각 팀원 SSH 계정은 **별도 Docker 컨테이너**다. `/home/<user>/`는 해당 컨테이너 로컬 디스크라 **다른 계정에서는 보이지 않는다**(권한을 열어도 마운트 자체가 없음).
> manifest의 `embedding_path`는 **`/workspace/...` 절대경로**로 작성한다(**개인 홈 경로 금지**).

### 왜 이게 심각한가 — Owner≠Reviewer가 **구조적으로 불가능**합니다

- **Critic(braveji)이 재현할 수 없습니다.** 제가 이번 검토를 커밋된 JSON 정적 대조로만 한 것은 방법론 선택이 아니라 **강제**였습니다.
- **sub-reviewer(sjpark/jhans)도 재현할 수 없습니다.** #4·#5를 의뢰해도 두 분은 숫자를 확인할 방법이 없습니다.
- **남은 remediation도 owner만 실행 가능합니다.** 5-seed null, pixel-mean baseline — 전부 kkkim만 돌릴 수 있어 **동일한 단일 실패점을 재생산**합니다.
- **#1(누수) 판정을 `pass` → `caution`으로 내렸습니다.** `split_meta.json`의 `site_disjoint: true` / `patient_overlap: 0`을 **독립 재계산할 수 없어** owner 자기신고에 의존하기 때문입니다.

### 그리고 이것이 블로커 1·2·4가 살아남은 **구조적 이유**입니다

폐 문서가 낡은 것도, 대장 실패 결과가 사라진 것도, 위암 shuffle 열이 빠진 것도 — **아무도 검증할 수 없었기 때문에** 살아남았습니다. 검증 가능성이 없으면 Critic 게이트는 서류 절차가 됩니다.

**→ 블로커 5가 최우선 선행조건입니다.** 임베딩을 `/workspace/data/cache/biop02/`로 옮기고 manifest를 재작성하기 전까지, 나머지 remediation은 검증 불가능한 상태로 반복됩니다.

---

## 3-ter. Critic 제공 진단 도구

`experiments/crosscancer/critic_robustness_probe.py` (braveji 작성)

`run_mil_cost.train_eval`을 **그대로 import**합니다 (재구현 금지 — RNG 소비까지 동일해야 seed=42 real이 저장본을 재현). 유일한 차이는 `n_tiles` 부수 산출.

endpoint마다 산출:

| | 항목 | 목적 |
|---|---|---|
| **[A]** | real (seed=42) | 저장본 재현 확인 |
| **[B]** | **5-seed shuffle-null** | `null_mean` / `null_sd` / 판정 (`real > null_mean + 2·null_sd` — kkkim 자체 기준 유지) |
| **[C]** | **`n_tiles`-only baseline** ★ | **타일 수 단 하나의 피처로 LR.** 이게 높으면(≳0.7) AUROC가 형태가 아니라 **bag-size에서 나온다는 직접 증거** — shuffle-null이 >0.5로 뜨는 현상의 유력 용의자 |
| **[D]** | mean-embed baseline | 임베딩 평균 → LR. MIL(attention)이 단순 평균 대비 더하는 값 (#2 pixel-mean 대응물) |
| **[E]** | bag-size 교란 | `spearman(proba, n_tiles)` · **`spearman(label, n_tiles)`** — 후자가 유의하면 라벨 자체가 타일 수와 엮인 **원천 교란** → 그 endpoint의 AUROC는 전부 의심 |

**[C]가 위암 `lauren_diffuse` 진단의 핵심입니다.** `n_tiles` 하나로 0.8이 나오면 블로커 1이 확정되고, 0.5 근처면 lauren 실패는 라벨 품질/56% 결손 쪽입니다.

> ⚠️ **미실행입니다.** 구문·API 계약 정적 검증만 마쳤습니다 (`py_compile` 통과, `run_mil_cost`의 `train_eval(slides, labels, endpoint, device, shuffle, epochs, seed)` 시그니처와 계약 일치 확인). 로컬에 GPU·torch·데이터가 없고, **블로커 5 때문에 owner 외에는 실행 자체가 불가능**합니다. 실행 전 `#biop02-alerts`에 GPU 예약 필요.

```bash
python critic_robustness_probe.py --cancer GASTRIC_STAD --device cuda:0
python critic_robustness_probe.py --cancer LUNG_NSCLC   --device cuda:1
python critic_robustness_probe.py --cancer HEADNECK_HNSC --device cuda:2
# → <cancer>/full/critic_robustness.json
```

---

## 4. 갱신된 서명 조건

| # | 조건 | 상태 |
|---|---|---|
| **0** | **임베딩을 `/workspace/data/cache/biop02/`로 이전 + manifest 재작성** (`/home/kkkim/...` 2588건). CLAUDE.md 팀 공유 경로 규칙 위반이자, **모든 검증·remediation의 선행조건** | **신규 (블로커 5) · 최우선** |
| 1 | **폐 3개 문서를 정본 JSON(`9b42d37`) 기준으로 재생성** + commit/split hash 봉인 | 원인 규명 완료 → 기계적 수정만 남음. **결과가 좋아지는 방향** |
| 2 | **5-seed shuffle-null을 폐·위·두경부 전 endpoint에 적용** (`run_openitems_robustness.py` 이식). 판정 기준 = `real > null_mean + 2·null_sd` (kkkim 자체 기준 유지) | **blocking으로 승격** |
| 3 | **대장 robustness 결과를 스코어보드·LAW_TEST에 반영** — cms1·cms4 FAIL 명시, `afedc6a`의 "사전등록 3축 확증" 서술 재검토, LAW_TEST 각주¹의 "FOLLOW-UP(non-blocking)" 문구 정정 | **신규 (블로커 4)** |
| 4 | 위암 `erbb2_amp` `예측적중=적중` 표기 + 스코어보드 결론2 인용 철회 | 유지 |
| 5 | **pixel-mean · subtype-only baseline 추가** (전 암종, 7-point #2) | 유지 |
| 6 | 커버리지 비무작위 결손 분석 (두경부 86%, 위암 lauren 44%) | 유지 |
| 7 | 위 반영 후 **#4·#5 sub-check(sjpark/jhans)** → 재검토 → 최종 서명 | 유지 |

---

## 5. 총평 — 무엇이 진짜 문제인가

세 블로커의 **근본 원인은 하나**입니다: **결과 파일과 서술 문서 사이의 동기화 규율이 없습니다.**

- 폐: 결과가 재실행됐는데 문서가 안 따라감 (블로커 2)
- 대장: 강건성 결과가 나왔는데 문서가 안 따라감, 그것도 **실패한 결과** (블로커 4)
- 위암: 결정적 수치(shuffle 열)가 표에서 아예 누락 (블로커 1)

세 경우 모두 **문서가 결과보다 낙관적**입니다. 방향이 한쪽인 게 우연은 아닙니다 — **낙관적 서술은 눈에 띄지 않아 살아남고, 비관적 결과는 반영 안 되면 사라집니다.** 이건 개인의 정직성 문제가 아니라 **파이프라인 구조 문제**이고, 그래서 Critic 게이트가 존재합니다.

**권고: 결과 파일 → 문서 자동 생성(`sh_*_lawtest.py`가 이미 그렇게 설계됨)을 강제하고, 손으로 쓴 수치는 CI에서 JSON과 대조해 불일치 시 실패시킬 것.** 그러면 블로커 1·2·4가 구조적으로 재발하지 않습니다.

이 부록은 kkkim의 작업을 깎지 않습니다 — 오히려 **폐 결과는 정본으로 고치면 더 좋아지고**, 5-seed null 도구는 **kkkim이 이미 만들어 뒀습니다.** 남은 건 그걸 전부에 적용하고 문서를 결과에 맞추는 일입니다.

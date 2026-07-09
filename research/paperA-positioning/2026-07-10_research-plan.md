# Paper A — Pre-registerable Research Plan (Cost-of-Substitution + Critic-gated Hypotheses)

> 작성: research-methodologist 세션, 2026-07-10. Leader=kkkim.
> 입력: `research/paperA-positioning/2026-07-10_novelty-scoop-analysis.md`(확정 각), `agents/therapeutic_evidence/docs/BIOP02-52*`·`BIOP02-36*`(join keys), `research/morphology-drug/dawood-2024-hids/*`(직접회귀 경쟁자).
> 상태: **설계 확정, 사전등록 대상.** 이 문서는 실험 실행 전 동결(freeze)되어야 하는 pre-registration 초안이다.
> 제약: `hypothesis_only` · BRCA-only · **DRP 프레이밍 금지** · 약물구조 입력 금지 · personalized/optimal-therapy 금지 · ICI/pembro 세포주 전이 금지 · 냉동 지도는 **cell-line-only**(TCGA/CPTAC 발현 미투입 = leakage guard).

---

## ⚠️ Fixed facts (Leader/task handoff; registry는 현재 0 bytes → BIOP02에서 채워야 함)

TCGA-BRCA train → CPTAC-BRCA test, 공식 라벨, AUROC:

| 표현형 | 모델 | 내부 | 외부 | subtype_only 상한 | 판정 |
|---|---|---|---|---|---|
| ER | CLAM-SB | 0.901 | 0.894 | 0.918 (p=0.613 동등) | caution — **강** |
| PR | CLAM-SB | 0.777 | 0.778 | 0.808 | caution |
| HER2 | CLAM-SB | 0.599 | 0.530 (양쪽 random) | 0.724 | **reject** |
| PAM50 | CLAM-MB | 0.759 | 0.722 | N/A | caution |

> **행동 항목(비블로킹):** `experiments/registry/cross_validation_registry.jsonl`이 비어 있음. 이 수치의 provenance(config/commit/predictions)를 registry에 등재해야 pre-registration이 검증 가능. → kkkim/sjpark.

---

## 1. Sharp hypothesis + one-sentence contribution

**H1 (primary, falsifiable):** H&E-예측 분자상태를 측정 분자상태 대신 *냉동 세포주→약물 지도*에 넣을 때 발생하는 치료-랭킹 손실(cost-of-substitution)은 **치료축(therapy axis) 의존적**이며, **anti-HER2 축에 집중**되고 **endocrine/CDK4-6 축(luminal)에서는 near-zero**다. 정량 대비: `cost_antiHER2 − cost_endocrine`의 bootstrap 95% CI가 **0을 배제**한다.
- **반증조건:** (a) CI가 0을 포함하면 "축-의존적 붕괴" 기각 → 형태학은 어디서나 균일하게 안전(덜 흥미롭지만 정직) 또는 균일하게 위험. (b) `cost_endocrine`의 CI 상한이 사전등록 임계(τ 손실 > 0.10)를 넘으면 "luminal에서 값싼 triage 충분" 기각.

**H2 (secondary):** 투명한 H&E→상태→세포주-지도 체인이 확립된 상태-약물 관계(ER+→endocrine, HER2+→anti-HER2, basal→chemo/PI3Ki-resistance)를 positive control로 복원하며, **사전등록된 miss-rate**가 사전 임계 이하다. (파이프라인 검증이지 발견 아님.)

**One-sentence contribution:**
> 우리는 더 나은 예측기를 만들지 않는다 — **해석 가능한 표현형 병목이 있기에 측정 가능한**, 값싼 H&E 형태학이 치료적으로 충분한 곳(endocrine/luminal)과 분자검사가 non-negotiable한 곳(anti-HER2)의 정량·Critic-gated·`hypothesis_only` 지도를 제시한다 — end-to-end DRP(Dawood 2024)가 **구조상 낼 수 없는** 숫자다.

**기여 유형(정직):** novel *method*이 아니라 **novel measurement + governance system**. 표현형 병목을 자산으로 전환한 cost-of-substitution 지표(C1)와 anti-self-reference Critic 거버넌스(C2)가 기여의 본체. 예측 성능은 스쿱됨(Fernandez-Romero 2026) — 한 줄 인용 후 폐기.

---

## 2. C1 — Cost-of-substitution (FLAGSHIP), 전체 설계

### 2.0 핵심 프레이밍 landmine (반드시 명시, 논문 첫 문장급)
C1이 재는 것은 **측정-상태 라우팅으로부터의 divergence**이지 *참 약물반응으로부터의* divergence가 **아니다**. 환자 약물반응 ground truth는 없다. 주장은 항상 *"H&E-치환이 측정-상태 라우팅을 재현한다(anti-HER2 제외)"*이지 절대 *"H&E가 올바른 치료를 예측한다"*가 아니다. 이 한 문장을 애매하게 쓰면 리뷰어가 C1을 임상검증으로 오독하고 기각한다. (Critic #6/#7 직결.)

### 2.1 냉동 세포주→약물 지도 (cell-line-only, leakage guard)
- **재료:** DepMap PRISM(24Q2) ∩ GDSC2 유방 세포주, join key = `SangerModelID`(primary)/`COSMICID`(fallback), per BIOP02-36/45. 교집합 ~35–45 (jhans v0.2 실측 대기).
- **누수 가드(Critic #1):** 지도는 **세포주 발현·감수성만** 사용. TCGA/CPTAC 발현·라벨은 지도 구성에 **일절 미투입**. 지도는 환자 데이터를 보기 전에 동결.
- **감수성 지표(PRISM↔GDSC 비직접비교, BIOP02-52 준수):** 절댓값 IC50/AUC 직접 비교 금지(Haibe-Kains 2013). **각 데이터셋 내부에서 drug별 z-score(또는 rank)** 로 정규화 후, 두 소스 rank를 합산해 consensus 감수성 rank 산출. GDSC subset z-score는 BRCA subset 내 재계산(원 전체-cell-line z-score 사용 시 caveat 표기).
- **지도 구조 = 치료축별(therapy-axis-keyed), NOT PAM50-monolithic** ← 설계의 최대 레버:

| 치료축 (a) | keying 상태변수 | 세포주 그룹 | 우리 분류기 | 강건성 |
|---|---|---|---|---|
| **Endocrine / CDK4-6** | ER / luminal status | ER+ vs ER− 세포주 | ER (ext 0.894) | **강** (다수·잘 주석) |
| **Anti-HER2** | ERBB2-amplification / HER2 status | HER2-amp vs non (SKBR3·BT474·HCC1954·AU565·MDA-MB-361… ~10+) | HER2 (random) | **강한 지도, 약한 분류기** |
| **Chemo / platinum / PI3Ki-resistance** | TNBC / basal status | TNBC vs non | PAM50→basal | 중 |

  이유: 각 치료를 실제로 라우팅하는 **분자축**으로 keying하면 (a) anti-HER2 지도가 ERBB2-amp 세포주(풍부·GDSC lapatinib/afatinib 감수성 확립)로 **잘 powered**되어 얇은 PAM50-HER2E bin 문제를 우회하고, (b) HER2 붕괴가 **우리의 강건한 발견(HER2 분류기 random → HER2+ 환자 절반 오라우팅)** 에 얹힌다. 각 축의 지도 M_a(status) = 해당 축의 subtype-discriminating drug들에 대한 consensus 감수성 rank 벡터.
- **지도 검증(build 전 게이트):** anti-HER2 축이 ERBB2-status 그룹핑만으로 실제 구성 가능한지(GDSC에 lapatinib/afatinib × HER2-amp 세포주 충분한지) 커밋 전 확인.

### 2.2 Dual-ranking (측정 vs H&E-예측; 상태 라벨만 바뀜)
CPTAC 환자마다 **같은 냉동 지도**로 축별 두 랭킹:
- **Route A (측정):** 측정 분자상태 → M_a(measured)
- **Route B (H&E-예측):** CLAM 분류기 예측 상태 → M_a(predicted)
- 입력에서 **상태 라벨 하나만** 바뀌므로 divergence는 형태학에 clean하게 귀속(counterfactual, Critic #3).

### 2.3 COST metric + label↔therapy 해리 (핵심)
- **Discriminating-drug panel = 사전등록(established pharmacology 기반, 지도 기반 아님):** GDSC biomarker-drug 확립 연관에서 축별 패널을 **먼저 고정** — endocrine(tamoxifen/fulvestrant류), CDK4/6i(palbociclib/ribociclib), anti-HER2(lapatinib/afatinib), platinum/PARP(cisplatin/olaparib), PI3Ki. **지도로 판넬을 뽑으면 순환**(같은 지도로 채점) → 반드시 외부 약리학으로 사전 선정.
- **Per-patient cost(underlying data):** discriminating drug에 대해 Kendall-τ 및 top-k overlap(A,B). 정분류 환자는 divergence=0.
- **분해(설명 장치, per-therapy-axis):**

  cost_a(true=g) = Σ_{g'} P(predict g' | true g, axis a) · d_a(g, g')

  - `P(predict g'|true g)` = CPTAC에서 **우리 분류기의 confusion matrix**(CPTAC prevalence 내장).
  - `d_a(g,g')` = **therapeutic distance** = 1 − Kendall-τ(M_a(g), M_a(g')) on 사전등록 discriminating drugs.
  - 각 축이 자기 분류기 confusion을 쓰고 C2 positive control과 1:1 대응 → **C1·C2 통합**.
- **Baseline(Critic #2):** `subtype_only→therapy` = 다수클래스/base-rate 라우팅을 같은 지도에 통과 → 형태학이 base rate 이상 하는지(또는 base rate만으로 cost가 설명되는지) 대조.
- **Primary result:** 축별 cost 표 + **label↔therapy 해리 표**: 동일한 1-라벨 오차가 endocrine에서 τ손실≈0(LumA↔LumB·ER 오차는 같은 endocrine/CDK4-6로 수렴) vs anti-HER2에서 τ붕괴. **이 해리가 발견이며 AUC 표에서 복원 불가** — 순환성 방어의 핵심.

### 2.4 Headline은 절댓값이 아니라 **대비**로 보고
~40 세포주에서 절대 d_a(g,g') CI는 넓다. Headline = **`cost_antiHER2 − cost_endocrine`의 bootstrap 95% CI가 0 배제**. 비교 주장이 절대 크기보다 훨씬 강건. 절대 cost는 부표로.

### 2.5 Intra-luminal ≈0 의 "construction vs empirical" 정직 분리 (Trap A가 내부에서 재발하는 것 차단)
Receptor-status keying에서는 LumA·LumB가 둘 다 ER+ → 같은 bin → cost가 **구성상 정확히 0**(자명, 발견 아님). 진짜 경험적 주장("더 미세한 해상도에서도 LumA↔LumB는 치료적으로 값쌈")은 **PAM50-keyed 지도를 secondary resolution**으로 별도 실행해서 보여야 한다(+ C3 proliferation residual). 논문에서 "≈0"의 어느 부분이 construction이고 어느 부분이 empirical인지 **명시 분리**. 안 하면 Trap A가 flagship 내부에서 재발.

### 2.6 세포주 그룹핑: robust primary / caveated secondary
- **Primary(강건):** receptor-status(ER/HER2-amp/TNBC) 그룹핑 — cell line에 널리 주석, gate (ii) 통과 용이.
- **Secondary(caveat):** CCLE 발현 → Parker(2009) PAM50 centroid 재계산. **Caveat:** centroid는 종양-학습 → 세포주(stroma/immune 부재)에서 거리 불안정 → 근사. Sanity: MCF7=luminal, MDA-MB-231/BT549=basal 알려진 상태로 교차확인. `research/datasets-benchmarks/parker-2009-pam50` 활용.

### 2.7 Normal-like 정책 (cascade)
세포주에서 Normal-like는 artifact/contamination로 사실상 부재 → 지도에서 제외. **Cascade:** CPTAC에서 예측 또는 측정 Normal-like 환자는 C1에서 **제외**(fallback-route 아님) + **CPTAC Normal-like prevalence 보고**(제외 규모 투명화).

---

## 3. C2 — Critic-gated hypothesis pipeline + pre-registered miss-rate

- **Positive-control 복원 프로토콜:** 축별 확립 관계를 파이프라인이 복원하는지 — ER+→endocrine, HER2+→anti-HER2, basal→chemo/PI3Ki-resistance. **복원 실패 = 파이프라인 버그(생물학 아님)**, 디버그 후 재실행.
- **사전등록 top-k:** 파이프라인 동결 → 축별 top-k(예: k=5) 상태→drug 출력을 **먼저 등록**(이 문서 freeze 시점) → *그 다음* 고정 조회.
- **고정 문헌/clinicaltrials 조회:** 사전 정의된 쿼리 프로토콜(약물명 × 유방암 × 상태), 조회 날짜·DB 버전 pin. hits **와** misses **둘 다** 보고.
- **Miss-rate 사전등록:** positive-control recall의 사전 임계 명시(예: 3개 축 중 ≥2 복원). Cherry-pick 방지: "알려진 링크 복원 = 배관 검증이지 novelty 아님" 명문화.
- **DRP 가드 문장(per-output):** *"morphology가 환자를 세포주 감수성 시그니처 enriched 상태로 층화한다"*, 절대 *"약물반응 예측"* 아님. 모든 출력 `hypothesis_only` + `claim_level`.

---

## 4. Baselines / competitors

1. **`subtype_only→therapy`(필수, Critic #2):** base-rate/다수클래스 라우팅을 같은 지도 통과. 형태학이 base rate 이상인지, cost가 base rate만으로 설명되는지 판별.
2. **Random-label 라우팅(null):** §5 참조.
3. **Dawood-style direct-regression baseline(선택·secondary·critical path 밖):**
   - **왜:** 리뷰어 "왜 병목을 거치나, end-to-end가 더 강한데?"에 대한 실증 방어.
   - **최소 버전:** 우리 UNI 임베딩 + 기존 MIL로 ridge-imputed CTRP/PRISM 감수성을 end-to-end 회귀, 동일 TCGA subset, 5-fold(Dawood 프로토콜 근사). `research/morphology-drug/dawood-2024-hids/*` 브리프대로.
   - **목적(경쟁 아님):** (i) end-to-end는 **per-axis cost 지도를 구조상 못 낸다**(병목 부재)를 실증, (ii) HER2 약함을 **독립 재현**(Dawood median SCC 0.18–0.33). 이미 출판된 실패라 **이기지 않아도 됨** → optional, C1+C2 뒤 게이트.
   - **DRP 프레이밍 containment(중요):** 이 comparator 출력은 **hypothesis로 방출 금지**, `hypothesis.schema.json` 미경유, "black-box DRP comparator"로 명시 라벨. 금지는 프로젝트 *산출물/주장*을 규율하지, 반론을 위해 *돌려보는 것*을 막지 않는다. Critic이 이 containment를 확인.

---

## 5. Statistical plan

- **Null test 1 (label shuffle):** CPTAC 예측-상태 라벨을 permute → cost 귀무분포 생성 → 관측 cost의 위치로 p. "cost가 상태 정보에서 온다" 확인.
- **Null test 2 (map shuffle):** 세포주-drug 감수성 rank permute → therapeutic distance 귀무. 지도가 실제 약리 구조를 반영하는지.
- **CI:** 모든 headline에 **bootstrap 95% CI**. **Nested bootstrap**: 환자 resample(confusion) × 세포주 resample(therapeutic distance) — 두 불확실성 원천 모두 전파. Headline = `cost_antiHER2 − cost_endocrine` CI.
- **Paired test:** Route A vs B per-patient τ는 paired(같은 환자·같은 지도) → **Wilcoxon signed-rank**. 상태 오분류의 이산성 → **McNemar**(정라우팅 vs 오라우팅 축별).
- **Multiple comparison:** discriminating-drug별 consistency 검정에 **Benjamini-Hochberg FDR**. 축(3개)·해상도(receptor/PAM50) 다중성도 보고.
- **Power/support 정직:** ~40 세포주, 축별 n 얇음(특히 anti-HER2 감수성 세포주, PAM50-HER2E). n≥5(BIOP02-52 규칙) 미만 지도 column은 **"inconclusive"로 표기, negative로 주장 금지**. CPTAC n≈120 → 상태별 하위 n 작음 → 대부분의 축별 차이는 유의하지 않을 수 있음, 그대로 보고. **소규모 n에서 우월성 주장은 검정이 지지할 때만.**

---

## 6. Feasibility gates (go/no-go)

| # | 게이트 | 체크 | 임계 | 실패 시 fallback |
|---|---|---|---|---|
| **(i)** | 치료축별 세포주 support | jhans BIOP02-52 **v0.2 실측** 카운트: ER+/ER−, HER2-amp/non, TNBC/non | 각 축 그룹 **≥5** (양쪽) | HER2-amp<5면 anti-HER2 축을 GDSC lapatinib/afatinib 감수성 top-vs-bottom 세포주로 정의(status 무관). 어느 축도 <5면 그 축은 "inconclusive" 강등, headline 대비를 가능한 축쌍으로 |
| **(ii)** | 세포주 상태 라벨 소스 | receptor-status = DepMap/CCLE 주석 직접; PAM50 = CCLE 발현 Parker centroid 재계산 | receptor-status ≥90% 세포주 주석 확보 | **Primary는 receptor-status(강건)** → gate 사실상 자동 통과. PAM50 재계산 실패/불안정이면 PAM50-keyed를 아예 drop하고 §2.5 empirical 주장을 C3 proliferation residual로만 |
| **(iii)** | Normal-like 처리 | 세포주 Normal-like 수 | (부재 예상) | 지도에서 제외 + CPTAC Normal-like 환자 C1 제외, prevalence 보고(§2.7) |
| **(iv)** | anti-HER2 지도 구성 가능 | GDSC lapatinib/afatinib × HER2-amp 세포주 dose-response 존재 | ≥5 HER2-amp 세포주에 anti-HER2 감수성 값 | 없으면 anti-HER2 붕괴를 **분류기-random 사실 + 문헌**으로만 정성 주장, C1 정량에서 제외 |
| **(v)** | (선택) Dawood baseline | ridge-impute 라벨 재현 + MIL 학습 수렴 | 상위 약물 SCC>0.3 재현 | 미수렴이면 baseline drop, 정성 인용으로 대체 |

**Go 조건(최소):** (i) endocrine·최소 1개 추가 축 ≥5, (ii) receptor-status 확보, (iv) anti-HER2 지도 ≥5. → C1 headline 대비 성립.

---

## 7. 3 most damning reviewer objections + cheapest preemption

1. **"순환 — 상태 AUC 높으면 약물 랭킹 당연히 일치, drug 공간에서 AUC 재유도."**
   - **선제(가장 싼):** headline을 concordance가 아니라 **label↔therapy 해리**로 보고(§2.3): 동일 1-라벨 오차가 endocrine τ손실≈0 vs anti-HER2 τ붕괴 — AUC 표가 **낼 수 없는 대비**. + discriminating-drug 패널을 **지도 아닌 외부 약리학**으로 사전등록(§2.3) → tautology 차단. + `subtype_only→therapy` baseline.
2. **"냉동 지도가 작고 부정확 — ~40 세포주, off-label PAM50, HER2E/Normal-like 부재; therapeutic-distance는 노이즈."**
   - **선제:** (a) 지도를 **receptor-status로 keying**(§2.1) → anti-HER2가 풍부한 ERBB2-amp 세포주로 잘 powered, 얇은 PAM50-HER2E 회피. (b) headline을 **대비 CI**로(§2.4), 절대 크기 아님. (c) column별 세포주 카운트 + d_a CI 보고, n<5는 inconclusive. (d) PAM50은 caveated secondary.
3. **"왜 표현형 병목? Dawood end-to-end가 더 강하다."**
   - **선제:** (a) 병목이 **cost 지도·Critic 게이팅을 가능케 하는 계기** — Dawood는 구조상 못 냄. (b) Dawood도 **HER2 독립 실패**(median SCC 0.18–0.33) → 우리 붕괴점 corroborate. (c) 최소 Dawood-style baseline(§4)로 실증(선택, off critical path). (d) 우리 주장은 예측 성능이 아니라 measurement/governance — 예측 우월성 주장 안 함.

---

## 8. Critic 7-item mapping

| Critic 항목 | C1 | C2 | Dawood baseline |
|---|---|---|---|
| #1 Data leakage | 지도 cell-line-only, TCGA/CPTAC 발현 미투입(§2.1); train/test = TCGA→CPTAC 유지 | 동일 | ridge-impute 라벨 누수 점검 |
| #2 Baseline | `subtype_only→therapy` + random-label null(§4,5) | positive-control = 배관 baseline | end-to-end vs 병목 대조 |
| #3 Counterfactual | 상태 라벨 하나만 swap(A vs B) → divergence 귀속(§2.2) | 상태 제거 시 랭킹 변화 | — |
| #4 Cross-dataset(DepMap↔GDSC) | 지도 = PRISM·GDSC z-score consensus(BIOP02-52), 비직접비교 준수(§2.1) | consistency로 hypothesis `data_source` 태깅 | ridge route 간 수렴 |
| #5 Biological plausibility | therapeutic-distance = 확립 약리(endocrine/anti-HER2/platinum) | positive control이 곧 plausibility 검증 | HER2 약함 = 생물학적으로 예상됨 |
| #6 DRP framing | §2.0 reference 명시; per-output DRP 가드(§3) | "층화"만, "약물반응 예측" 금지 | **"black-box DRP comparator" 라벨·hypothesis 미방출**(§4) |
| #7 Claim-level | 모든 출력 `hypothesis_only`+`claim_level` | 사전등록 miss-rate, cherry-pick 금지(§3) | comparator 출력은 hypothesis 아님 |

**Owner≠Reviewer:** C1/C2 owner = kkkim/jhans → Critic 총괄 braveji, 바이오 sub-check(#4/#5) sjpark. 각 산출물 owner는 자기 결과 self-review 금지.

---

## 9. Minimal figure list

- **Fig 1 — Pipeline + governance schematic:** H&E→상태(병목)→냉동 세포주 지도→ranked `hypothesis_only`→Critic gate. 병목을 "계기"로 강조. (개념도)
- **Fig 2 (⭐ DECISIVE) — label↔therapy 해리 2-panel:** (좌) CPTAC H&E 상태-confusion matrix, (우) therapeutic-distance matrix d_a, 곱을 overlay. **anti-HER2가 켜지고 luminal은 안 켜짐.** 이 한 장이 논문.
- **Fig 3 — 축별 cost + headline 대비:** cost_a 막대 + `cost_antiHER2−cost_endocrine` CI(0 배제). receptor-status(primary) & PAM50(secondary) 나란히, construction vs empirical 분리(§2.5).
- **Fig 4 — C2 positive-control recall + miss-rate 표/그림:** hits·misses 정직 보고.
- **(선택) Fig 5 — Dawood baseline 대조:** end-to-end가 per-axis cost 못 냄 + HER2 약함 재현.

**단일 최결정 그림 = Fig 2.**

---

## 10. Scoped task breakdown + critical path

| ID | 작업 | Owner | 의존 | 산출물 |
|---|---|---|---|---|
| T0 | registry에 4개 CV 수치 provenance 등재(config/commit/predictions) | kkkim/sjpark | — | `cross_validation_registry.jsonl` |
| **T1** | **BIOP02-52 v0.2: 유방 세포주 교집합 + 치료축별(ER/HER2-amp/TNBC) 카운트 실측** | jhans | — | cell_line_overlap.csv, 축별 count → **gate (i)/(iv)** |
| T2 | 냉동 지도 구성: PRISM·GDSC z-score consensus, 축별 keying, discriminating-drug 사전등록 패널 | jhans | T1 | frozen_map.csv (동결) |
| T3 | 세포주 상태 라벨: receptor-status(primary) + PAM50 재계산(secondary, caveat) | jhans | T1 | cell_line_status.csv → gate (ii) |
| T4 | CPTAC 환자 축별 예측 상태 export(CLAM ER/HER2/PAM50 예측 + confusion) | sjpark | T0 | predictions + confusion matrix |
| **T5** | **Dual-ranking + cost 분해(confusion×distance), nested bootstrap, null tests** | sjpark(+kkkim) | T2,T3,T4 | cost 표, headline CI, Fig 2/3 |
| T6 | C2 파이프라인 동결 + 사전등록 top-k + 고정 조회 + miss-rate | jhans(+kkkim) | T2,T4 | hypotheses(hypothesis_only), miss-rate |
| T7 | (선택) Dawood-style baseline | sjpark | T4 | comparator(비-hypothesis) |
| T8 | Critic 7-item 리뷰(Owner≠Reviewer) | braveji 총괄, #4/#5 sjpark | T5,T6 | critic_report.json |

**Critical path:** T1 → T2/T3 → T5 (T4 병렬) → T8. **게이팅 리스크 1위 = T1**(축별 세포주 support). T1 결과 없이 T2/T5 착수 금지.

---

## Pre-registration freeze checklist (실행 전)
- [ ] Discriminating-drug 패널 확정·동결(외부 약리학 기반)
- [ ] 냉동 지도 동결(환자 데이터 접촉 전)
- [ ] C2 top-k 가설 등록 + 조회 프로토콜·DB 버전 pin
- [ ] Miss-rate·cost 임계 수치 명문화(§1 H1/H2)
- [ ] gate (i)–(iv) 통과 여부 기록(jhans T1)
- [ ] registry(T0) 등재로 fixed facts provenance 검증

---

*이 문서는 pre-registration 초안이다. gate 통과·패널 동결 후 커밋 해시와 함께 freeze한다. headline 숫자는 실행 전 미정 — 지어내지 않는다.*

# BIOP02 Experiment Plan — Exp1–Exp5 (v0.1)

작성 2026-06-10 (research-methodologist). Ground = research/novelty_positioning.md + 각 paper의 methodology-brief.
타겟 저널 = **npj Precision Oncology**. 이 문서는 Scientific Critic 검토 대상.

> **한 줄 thesis (정직):** 예측 숫자로는 못 이긴다. 우리가 이기는 축은 **(1) site-통제된 정직한 평가, (2) phenotype-bottleneck auditability, (3) 다중경로 수렴 + Critic gate**. 기여 = 더 나은 약물민감도 수치가 아니라 **재현·반증 프로토콜**.
> SOTA bar = **Tafavvoghi 2024 macro-F1 0.727** (약한 내부 baseline 아님). end-to-end 대조 = **Dawood 2024** (동일 저널, 최고 scoop 위험).

---

## 0. 공통 규약 (모든 Exp 적용)

**Cohorts/Scope.** Paper A scope = **TCGA-BRCA ~150–300 슬라이드 subset** (CLAUDE.md "Paper A scope = ~150 slide subset"; full ~1010 manifest 사용 금지). **권고: ~250 환자** — Exp2 site-probe와 Exp3 ranking에 최소한의 검정력을 주면서 GPU/시간 예산 안. CPTAC-BRCA(~120 paired)는 **외부 hold-out test only**.

**Split.** `agents/data/split_policy_v0.md` (patient-level + site-disjoint, PreservedSiteCV preferred). 모든 Exp는 동일 잠긴 split + `split_hash` 사용.

**Required metrics (CLAUDE.md).** `auc`, `auprc`, `balanced_accuracy` — phenotype task. PAM50(4-class)은 추가로 **macro-F1** (Tafavvoghi 비교용).

**Trivial baselines (Critic #2, 모든 phenotype Exp 의무).** Random / Majority(=subtype-only proxy) / MeanEmbed-LR(=pixel-mean proxy). 코드 = `agents/modeling/baselines/trivial.py`. 본 모델은 MeanEmbed를 통계적으로 상회해야 결과 인정.

**Statistical plan (공통).**
- 모든 headline 숫자 = **bootstrap 95% CI** (환자 단위 resample, 2000 reps).
- AUC 쌍 비교 = **DeLong test**; 분류 정확도 쌍 비교 = **McNemar** (paired).
- **Multiple-comparison: Benjamini–Hochberg FDR** across {4 targets × 비교 수}. 작은 n → 대부분 유의 아님 — "유의" 주장은 검정이 받칠 때만.

**Calibration + abstention (Exp2/3/5 연계).** temperature scaling (Guo 2017) → Mondrian conformal (Olsson 2022, `s=1−p̂`, class-conditional). gate: `|set|==1 → emit hypothesis_only`, else `abstain → Critic reject`. ε는 owner가 사전 고정 (anti-self-reference).

**Governance.** 출력 = hypothesis-only. "drug response prediction"/"personalized therapy" 표현 금지 (Critic #6). 결과는 Critic pass 후에만 `#biop02-experiments`. 모든 실험 디렉터리에 5 artifact + `commit_hash` + `split_hash`.

**Feasibility 공통.** GPU(A100×1)는 **일회성 임베딩 추출**에만 무겁게 사용 (UNI/CONCH tile feature 사전계산, ~250 슬라이드 → 수 시간). 이후 모델링(MLP/attention-MIL, 로지스틱 probe, conformal)은 CPU/경량 GPU. → 전체 계획이 단일 A100에서 현실적.

---

## Exp1 — 임베딩 substrate 정량화 (foundation vs ImageNet vs Tafavvoghi)

**Hypothesis.** phenotype 예측 성능의 이득 출처는 백본 임베딩이다: UNI/CONCH(FM) > ImageNet 백본 > Tafavvoghi tile-count+XGBoost — **동일 split** 하에서.

**Design / conditions.** 동일 site-disjoint split, 4 target(ER/PR/HER2/PAM50):
- (a) **UNI** (chen-2024-uni) + attention-MIL (CLAM, lu-2021-clam) head.
- (b) **CONCH** (lu-2024-conch) + 동일 head (FM ablation).
- (c) **ImageNet ResNet/ShuffleNet** + 동일 head (백본 통제).
- (d) **Tafavvoghi 공개 코드** (`uit-hdl/BC_MolSubtyping`, tile-count→XGBoost) — 격리 env.

**Baselines.** trivial 3종 + (d)가 published baseline.

**Metrics.** auc/auprc/balanced_accuracy (+ PAM50 macro-F1). bootstrap CI; (a) vs (c) = DeLong (FM 이득 격리); (a) vs (d) = 같은 split 재측정 head-to-head.

**Success criteria.** (a)/(b)가 (c)를 유의하게 상회 → 이득이 FM 임베딩에서 옴. (d) 대비는 Exp2의 *동일 harder split* 재측정치를 막대로 (그들 쉬운 0.727 아님).

**What it proves.** 두 scoop의 실제 방법 대비 개선 정량화. **단, "UNI가 최고" 과대선전 금지** — Exp1은 substrate 측정일 뿐, 기여는 파이프라인 설계 (novelty 리스크 #4).

**GPU/feasibility.** 임베딩 1회 추출 후 head 학습은 경량. 낮음.

**Risks.** Tafavvoghi 코드 재현 실패 → 그들 보고치를 상한으로만 인용하고 우리 재구현치를 막대로 명시.

---

## Exp2 ★ — Site-stratified vs random split + site-classifier probe (최강 reviewer shield)

> **crux:** 기존 문헌 숫자(0.727·Dawood 상관)가 **site로 교란**되어 부풀려졌고, 우리의 site-disjoint 숫자가 *정직한* 성능임을 선제 증명. 거의 무료 (임베딩 재사용). 이게 없으면 리뷰어 #5("site 교란이면 너희도 부풀려짐")에 무방비.

**Hypothesis.**
- H2-A: FM 임베딩은 submitting-site를 강하게 인코딩한다 (site-probe AUROC ≫ 0.5, Howard 0.964–0.998 영역에 근접).
- H2-B: random/patient-only split은 site-disjoint split 대비 phenotype 성능을 **유의하게 부풀린다** (ΔAUROC = random − site-disjoint > 0).

### Exp2-A — Site detectability probe (임베딩 위)

**Probe 정의.** 입력 = slide-level 집계 FM 임베딩 (UNI mean-pool 또는 attention-pool). 타깃 = `tss_code` (submitting site, K-class). 분류기 = **multinomial logistic regression** (단순·해석 가능, 과적합 위험 낮음). 평가 = **환자-disjoint 5-fold**, one-vs-rest **AUROC** 매크로 평균.

**해석.** AUROC가 1.0에 가까울수록 임베딩이 site를 강하게 인코딩 → site-aware split 필수성 입증. de Jong 2025(모든 FM이 medical-center 시그니처 인코딩, UNI 포함)와 정합 여부 리포트. 이 값을 split_policy의 leakage checklist에 floor로 기록.

**보조 (equity).** ancestry/race를 (i) random split, (ii) site-disjoint split 에서 각각 예측 시도 → site-disjoint에서 chance(≈0.5)로 떨어지는지 확인 (Howard BRCA 0.798→0.507 재현 여부). 떨어지면 site-disjoint가 demographic confound도 무력화함을 입증.

### Exp2-B — Random vs site-stratified 대조 (핵심)

**Design.** 동일 모델(예: UNI+attention-MIL, ER status 우선)을:
- (i) random/patient-only split (현 hash split 모사)
- (ii) site-disjoint(QP) split (split_policy_v0)
두 방식으로 학습/평가. 4 target 반복.

**Metric / interpretation.**
- **ΔAUROC = AUROC(random) − AUROC(site-disjoint)**, ΔmacroF1 동일.
- 각 Δ에 bootstrap 95% CI + DeLong (paired, 같은 test 환자에서 비교 가능한 경우) / 아니면 독립 split-level CI.
- **기대/해석:** Δ > 0 (CI가 0을 넘김) → random이 site leakage로 부풀려짐 → **site-disjoint 숫자가 우리의 primary 보고치**. 예상 규모: Howard류 confound에서 ΔAUROC ~0.02–0.10 (target·site 다양성 의존). Δ가 작아도(≈0) "우리 데이터엔 site 교란이 약함"을 *측정으로* 보인 것이므로 여전히 shield로 유효 — 어느 쪽이든 정직성 입증.

**Baselines.** trivial 3종을 두 split 모두에서 — trivial은 split에 둔감해야 정상 (sanity).

**Success criteria.** (1) Exp2-A site-AUROC를 숫자로 보고, (2) Exp2-B ΔAUROC + CI 보고, (3) **모든 후속 Exp의 primary 숫자를 site-disjoint split에서** 산출. 세 조건 = Critic #1 통과 전제.

**What it proves.** Tafavvoghi/Dawood가 통제 안 한 축(site/scanner confound)을 우리가 측정·통제 → 같은 split 재측정에서 0.727을 넘으면 **공정한 head-to-head 승리** (Exp1 (d)와 연결).

**GPU/feasibility.** 임베딩 재사용, probe·MLP만 재학습 → 매우 낮음. "거의 무료."

**Risks.** (1) site 수가 적어(K 작음) probe 검정력 부족 → site를 묶거나 작은 site는 'other'로. (2) random split이 우연히 site-balanced → Δ≈0; 이때 결론은 "교란 약함"으로 정직 보고 (over-claim 금지). (3) PreservedSiteCV QP가 class-balance를 못 맞춰 fold가 작아짐 → fallback greedy + class-balance표 동봉.

---

## Exp3 ★ — Phenotype-bottleneck vs end-to-end (Dawood 충실 재현) + failure-attributability

> **crux:** 병목(phenotype-intermediate)이 *수사(rhetoric)*가 아니라 실제로 **오류를 진단 가능(auditable)** 하게 만든다. 목표 = **동등 정확도에서 더 높은 감사성(auditability)**. 이게 benchmark 논문을 method 논문으로 격상시키는 단일 최고 레버리지.

**Hypothesis.** 두 시스템이 **유의차 없는 ranking 정확도**를 내되, bottleneck은 각 오류를 식별 가능한 중간단계(예측 phenotype)로 **귀속**시켜 attributability가 유의하게 높다.

**Design / conditions.** 동일 TCGA-BRCA subset·동일 CTRP 라벨(Dawood route)·동일 site-disjoint split:

- **Arm B (Bottleneck, 우리):** H&E → FM 임베딩 → **예측 phenotype**(ER/PR/HER2/PAM50, 해석 가능 중간단계) → phenotype-conditioned drug ranking (route 규칙은 Exp4 신호로). 중간 phenotype이 **명시적으로 노출·검사 가능**.
- **Arm E (End-to-end, Dawood 충실 재현):** TIAToolbox tissue seg → 512×512@0.25µm patch → **ImageNet ShuffleNet 1024-d** → Delaunay graph → **SlideGraph∞** EdgeConv → **pairwise ranking loss** → CTRP imputed sensitivity ranking. 중간단계 = saliency heatmap 뿐 (Dawood가 가진 유일한 해석).

라벨 route = CTRP ridge-imputation (geeleher 계보, dawood-2024-hids brief A) — **두 arm 공통**으로 두어 *라벨이 아니라 아키텍처* 차이를 격리.

**Metrics — 정확도 (동등성 검정).** drug-ranking 일치도 = **Spearman ρ** / top-k 정밀도 vs imputed sensitivity. 두 arm의 ρ 차이에 bootstrap CI. 핵심은 우월이 아니라 **동등성**: TOST(two one-sided tests)로 |Δρ| < margin(예: 0.05) 을 검정 → "정확도 동등" 주장의 근거.

**Metric — Failure-Attributability (FAS, 신규 정의).**
오분류된(혹은 top-k에서 빠진) 가설 각각에 대해, **단일 식별 가능한 중간 결함에 귀속될 수 있는가**를 점수화:

```
한 hypothesis-level 오류 e 에 대해:
  Arm B: 예측 phenotype 중간단계가 있으므로 →
    attributable(e) = 1  if 오류가 특정 phenotype head의 오예측으로 추적됨
                          (예: HER2 head가 HER2+를 HER2−로 → anti-HER2 약물 누락)
                          AND 그 head의 conformal set이 그 환자에서 비단일(uncertain)이었다
                       = 0  otherwise (오류가 어느 중간단계로도 국소화 안 됨)
  Arm E: 중간 phenotype 없음 → attributable(e)=1 은
         saliency heatmap이 단일 식별 가능 영역을 주는 경우만 (인간 rater 2인, Cohen's κ 보고)

FAS = (# attributable 오류) / (# 전체 오류)
```

**FAS 측정 프로토콜.** 두 rater(owner≠reviewer)가 오류 표본(예 50건)을 blind 라벨링; κ 보고. Arm B의 attributability는 **자동**(phenotype head 추적 + conformal set 기록)이므로 rater 부담이 Arm E보다 작다는 점 자체가 결과의 일부.

**Success criteria (equal-accuracy-higher-auditability).**
1. **동등 정확도:** TOST로 두 arm ranking ρ의 동등성 성립 (|Δρ| < 0.05, 양측 one-sided p<0.05). *또는* Arm B가 유의 열등이 아님 (DeLong/bootstrap CI가 큰 음수 배제).
2. **우위 감사성:** **FAS(Arm B) − FAS(Arm E) > 0** with bootstrap 95% CI 가 0을 넘김. (paired McNemar on per-error attributable 0/1.)
→ 둘 다 성립 = 논문 thesis 실증 ("같은 정확도, 더 진단 가능").

**What it proves (vs Dawood).** Dawood는 end-to-end + saliency만 → 오류 원인 불투명. 우리 병목은 동등 정확도에서 **각 오류를 예측 phenotype + conformal 불확실성으로 국소화** → reviewer #1("Dawood + extra steps")에 대한 실증 답.

**GPU/feasibility.** Arm E(SlideGraph∞ GNN 학습)가 이 계획에서 **가장 무거운 단일 항목** — 그래도 ~250 슬라이드·patch graph 규모면 A100 single에서 수일 내. Arm B는 사전계산 임베딩 + 경량 head. 중간.

**Risks.** (1) Arm E 재현이 어려움(공개 코드 의존도 높음) → 충실 재현 불가 시 "공식 구현 한계"를 명시하고 보고 파라미터 고정. (2) 정확도가 동등하지 않고 Arm B가 열등 → 그래도 FAS 우위면 "auditability–accuracy 트레이드오프"로 정직 보고 (over-claim 금지). (3) FAS rater 주관 → κ 낮으면 rubric 재정의, n 확대. (4) CTRP 라벨 자체가 cell-line imputed (Dawood도 인정한 약점) → Exp4 수렴이 그 약점의 존재 이유.

---

## Exp4 — Multi-route convergence (다중경로 수렴)

**Hypothesis.** 두(이상)의 **방법론적으로 독립**인 readout에서 모두 상위인 약물 가설은 단일 route hit보다 known BRCA-actionable로 더 강하게 enrich된다 (투표 장난이 아닌 실제 신호).

**Routes (비-순환).**
- **route1 — viability transfer:** phenotype → PRISM/GDSC/CTRP 민감도 전이 → rank R1. (3중 일관성 = Critic #4: corsello-2020-prism / iorio-2016-gdsc / seashore-2015-ctrp.)
- **route2 — signature reversal:** phenotype-연관 발현 signature → LINCS L1000 τ (subramanian-2017-lincs) → reversal rank R2. **viability label 미사용 → route1과 독립.**
- **actionability grounding:** OncoKB(Tx level, gated ceiling) · CIViC(A–E, open) · Open Targets · DGIdb (open floor).

**Design.** 약물별 route 신호 일치도 = **RBO / top-k rank-overlap (R1,R2)**. ≥k 합의 가설 집합 vs 단일-route 집합을 **known BRCA-actionable**(HER2+→anti-HER2, basal/BRCA-like→PARP/platinum) enrichment로 비교 (Fisher exact / hypergeometric, FDR).

**Metrics.** convergence count/가중합의; enrichment odds ratio + CI; open-floor vs OncoKB-ceiling **coverage gap을 명시 카운트** ("open route가 OncoKB level의 X% 커버, 나머지 = gated residual"). open floor를 ceiling으로 포장 금지.

**Success criteria.** 수렴(≥k) 가설이 단일-route보다 actionable enrichment 유의 상승. 후향 점검: HER2+ 수렴 가설이 anti-HER2 actionability를 회수하는지.

**What it proves.** 단일 cell-line route(Dawood)의 취약성 → 직교 경로 합의 요구가 우리 차별점. **GPU 불필요** (KB/순위 연산). 

**Risks.** OncoKB 토큰/라이선스 gated → open KB로 floor 도달범위 정량화 + residual gap 표기 (chakravarty brief). route2 signature 도출이 발현데이터 의존 → TCGA/CPTAC 발현 가용성 확인.

---

## Exp5 — Critic-gate operating characteristic

**Hypothesis.** Critic 7-point gate가 결과를 실제로 바꾼다 (rejection rate > 0). 통과 가설의 actionability precision이 raw(게이트 전)보다 높다.

**Design.** Critic gate를 **가설 분류기**로 취급. 입력 = Exp3/Exp4 후보 가설(+conformal set + route 합의). 출력 = pass/reject + reason. ground-truth = OncoKB level (ordinal: `actionable_L1_2 / investigational_L3_4 / resistance_R / open_only / unsupported`, chakravarty brief).

**Metrics (operating characteristic).**
- **rejection rate** (전체 / reason별: conformal-ambiguous, route-불일치, unsupported-KB, DRP-framing).
- **gate precision** = pass된 edge 중 (`actionable_L1_2`+`investigational_L3_4`) 비율.
- **Dawood식 raw 예측 기각률**: end-to-end raw ranking을 같은 gate에 통과시켜 기각 비율 비교 (gate가 raw를 더 많이 거르면 effective).
- ROC-유사 곡선: ε(conformal) / 합의 임계 k 를 스윕한 precision–coverage 곡선.

**Success criteria.** rejection rate > 0 **AND** gate-pass precision > pre-gate precision (bootstrap CI). 아니면 Critic은 장식.

**What it proves.** Critic을 측정 가능한 **falsifiability gate**(operating characteristic)로 보고 → method로 출판 가능 (novelty doc §멀티에이전트: "에이전트 있어요"가 아니라 기각률로). owner≠reviewer·anti-self-reference는 LLM-judge 편향(Zheng 2023, Panickssery 2024)의 구체적 완화책으로 포지셔닝.

**Risks.** OncoKB ground-truth gated + 희소 → CIViC/Open Targets로 보강, residual은 `open_only/unsupported`로 카운트. gate가 아무것도 안 거름(rejection≈0) → "현 후보가 이미 정제됨" 또는 "gate 무효" 둘 중 정직 판정.

---

## 최소 논문 세트 & 최고 레버리지

- **Minimum viable paper (Paper A) = Exp1 + Exp2 + Exp4.**
  - Exp1: substrate 정량화 (두 scoop 대비 개선 측정).
  - Exp2: site-통제 정직 평가 (reviewer shield, 거의 무료) — **없으면 desk-reject 위험**.
  - Exp4: 다중경로 수렴 (단일 novelty 축, GPU 불필요).
  - 이 세트만으로 "honest, externally-validated, convergence-grounded hypothesis protocol" 주장 성립.

- **Exp3 가 benchmark→method 논문으로 격상**시킴 (auditability thesis 실증). 여력 있으면 포함.

- **단일 최고 레버리지 수 = Exp2 평가체제 + Exp3 (bottleneck vs end-to-end).**
  - Exp2는 *모든 다른 숫자의 신뢰성*을 떠받치는 토대 (싸고 필수).
  - Exp3는 *thesis 자체*("auditable이 실제로 의미 있다")를 실증.
  - 자원 제약 시 우선순위: **Exp2 → Exp4 → Exp1 → Exp3 → Exp5.**

---

## Leader 결정 반영 (2026-06-10, kkkim)

1. **Paper A subset = 전체 1010 (full BRCA cohort).** Exp2 site-probe·Exp3 ranking 검정력 최대화 + 충분한 site 수 확보. 영향: GPU 임베딩 추출 ~34 GPU-h/모델(스트리밍, 디스크 부담 적음), 라벨 완전성 점검 부담↑. ⚠️ **CLAUDE.md 금지조항("TCGA WSI full download, Paper A scope ~150 subset", line 220/239)과 충돌 → Leader 결정으로 override, 거버넌스 갱신 필요.**
2. **Exp3 = 보류(나중 결정).** Paper A는 **Exp1+Exp2+Exp4**로 우선 진행. Exp3(병목 vs SlideGraph∞ end-to-end, 최대 GPU 항목)는 GPU 확보·중간 결과 보고 Paper A 포함 vs 별도 method paper 추후 결정. 설계는 본 문서에 유지.
3. **PAM50 소스 = cBioPortal TCGA-BRCA PAM50 (1순위)**, 분류기 정의는 **Parker 2009** 인용. 커버리지 부족분은 **TCGA RNA-seq + genefu(Parker centroids) 직접 산출** fallback. (TCGA-BRCA 2012 부속표는 표본 적어 1010 미커버 → 1순위 아님.) split_policy §4 라벨 정책에 반영.

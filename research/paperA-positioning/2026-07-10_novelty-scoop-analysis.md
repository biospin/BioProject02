# Paper A — Novelty / Scoop 분석 + 포지셔닝 (2026-07-10)

> 작성: kkkim (Leader) 세션. 근거: 외부 에이전트 2종(literature-scout, novelty-strategist) 병렬 조사 + 원문 검증.
> 목적: "H&E→분자표현형 예측" 레드오션을 피하고 **novelty·임상 의미로 승부**할 각을 확정.
> 상태: **결론 도출 완료 + 2개 🔴 검증 반영.** 다음 = research-methodologist로 정식 연구계획 전환.
> ⚠️ 이 문서는 조사 원본을 **생략 없이** 보존한다(사용자 지시). 수치·주장 인용 전 §4 검증/플래그 확인.

---

## 0. TL;DR — 결정

- **레드오션 확정 사망:** "H&E foundation-model + MIL로 ER/PR/HER2/PAM50 예측 + TCGA→CPTAC 외부검증 + multi-FM 비교"는 **이미 출판됨**(Fernandez-Romero 2026, Med Biol Eng Comput) — 우리 HER2 외부 실패까지 재현. 이걸 논문 본체로 삼으면 안 됨. 한 줄 인용("consistent with [2026]") 후 폐기.
- **치료 전이 파이프라인 자체도 스쿱됨:** Dawood 2024(npj Precision Oncology)가 H&E→세포주 약물감수성(유방)을 이미 냄. "H&E→약물"은 novelty 아님.
- **살아남는 유일한 헤드라인:** #3을 **agentic, Critic-governed, hypothesis_only 치료가설 생성 *시스템/거버넌스* 기여**로 재구성. 예측기도, 전이 파이프라인도 아님.
- **플래그십 실험:** **cost-of-substitution** — 분자검사 대신 H&E-예측 아형을 냉동 세포주→약물 지도에 넣었을 때 치료 랭킹을 얼마나 잃는가(아형별 층화). 이것이 (a) 표현형 병목을 정당화하고 (b) "천장 못 넘음"을 논점으로 뒤집는다.
- **2개 함정(반드시 해소):** (A) subtype 천장(PAM50→ER)이 near-tautological → 치료 공간에서 재정의로 de-circularize. (B) "형태학은 subtype 넘어 못 준다"(#1)와 "분자검사 없을 때 유용"(#2)은 다른 세계 → #2는 동기로만.
- **feasibility 리스크(신규 확인):** 유방 세포주 교집합(DepMap∩GDSC) ~35–45개뿐 → PAM50 아형별 support 얇음(**Normal-like 세포주 사실상 없음**, HER2E 소수). C1의 냉동 지도 신뢰 범위를 명시해야 함.

---

## 1. 배경 — 질문과 우리 결과(사실)

**파이프라인:** H&E WSI → foundation-model tile embedding(UNI 1024d / CONCH 512d / EXAONE Path 2.0 768d) → attention MIL(CLAM-SB/MB) → 분자표현형(ER/PR/HER2 status, PAM50). BRCA-only. `hypothesis_only`. **DRP 아님**(약물구조 입력 없음). 하류 의도: 예측 표현형 → DepMap PRISM/GDSC 세포주 약물감수성 → **랭크된 치료 가설**, 7항목 Scientific Critic 검증.

**외부검증(TCGA-BRCA train → CPTAC-BRCA test, 공식 라벨; `experiments/registry/cross_validation_registry.jsonl`):**

| 표현형 | 모델 | 내부 AUC | 외부 AUC | gap | subtype_only(상한) | 판정 |
|---|---|---|---|---|---|---|
| ER | CLAM-SB | 0.901 | 0.894 | -0.007 | 0.918 (p=0.613 **통계 동등**) | caution |
| PR | CLAM-SB | 0.777 | 0.778 | +0.001 (최고 일반화) | 0.808 | caution |
| HER2 | CLAM-SB | 0.599 | 0.530 (양쪽 random) | -0.070 | 0.724 | **reject** |
| PAM50 | CLAM-MB | 0.759 | 0.722 | -0.037 | N/A | caution |

- 부가: EXAONE slide_global ER 0.923(≈천장)이나 **내부 tiling+집계 혼재**라 clean한 model-quality 주장 불가 → 헤드라인 금지.
- 정직한 요지: 일반화는 잘 됨(gap 작음). 문제는 subtype_only 상한을 못 넘거나(ER 동등) HER2가 양쪽 random(reject).

**검토한 두 프레이밍:**
1. **Subtype ceiling / orthogonality** — "H&E가 분자 아형(PAM50) 너머 무엇을 더하나?"
2. **Cheap-input 임상 유용성** — 분자검사 없는 세팅(LMIC·소규모 랩·triage)에서 H&E 한 장 → Critic검증 치료 가설.
3. (하류) **Therapeutic 연결** — 표현형 → DepMap/GDSC → 랭크된 hypothesis_only.

---

## 2. literature-scout 리포트 — 선행연구 / 스쿱 (원문 보존)

**검증 상태(에이전트 자체):** 3개 핵심 논문(Springer 2026 domain-gen; Dawood npj Precis Oncol 2024; Kather/Arslan Commun Med 2024)을 EuropePMC 1차 색인으로 검증(제목·저자·저널·연도·DOI·abstract). WebFetch(nature/springer) DNS 차단 → *[snippet, unverified]* 표시 항목은 검색 요약만이므로 인용 전 확인 필요.

### 0) Red ocean (한 줄)
"H&E predicts ER/PR/HER2/PAM50"는 **포화**(Couture 2018 → Naik/ReceptorNet 2020 → Kather pan-cancer 2024 → Fernandez-Romero 2026). ER AUC ~0.86–0.92, PAM50 ~0.72–0.87, **TCGA→CPTAC 외부검증은 이미 표준·출판된 설계.** 서술적 결과는 스쿱됨 — 논문을 여기 세우지 말 것.

### 1) 형태학이 분자 아형과 ORTHOGONAL한 신호를 주는가?
**(a) Discordance의 의미 — 근접연구 존재, 갭 좁음.** Shamai et al., *Commun Med* 2024(검증)가 최근접: H&E로 ER/PR/ERBB2 예측 + 모델–IHC **불일치(discordance)** 를 임상가치로 재프레이밍(위양성 IHC/오진 QA 탐지). Naik(ReceptorNet, *Nat Commun* 2020)도 discordance 논의. **갭:** 둘 다 discordance를 *QA/오류탐지* 신호로 다룸, *orthogonal biology*("H&E가 assay가 못 보는 걸 본다")로는 아님. discordant 케이스를 별개 생물축으로 인과 규명한 사례 없음. 얇지만 실재.

**(b) 아형 내부 예후(같은 LumA, 다른 결과) — 활발히 추진 중, 스쿱 위험 높음.** LumA "subtype purity/admixture"(medRxiv 2023), 이미지 기반 고위험 ER+/HER2−(PMC11616316), *[snippet, unverified]* *Lancet Oncology* 2025(H&E로 재발위험 **및 항암화학 이득** 예측). 세 orthogonality 각 중 가장 crowded → **near-scooped**.

**(c) "subtype 천장"(형태학이 subtype-informed baseline 못 넘음)을 정식 기여로 — whitespace에 가장 근접, 단 standalone은 약함.** 분자아형-informed 천장 baseline을 돌려 형태학의 failure-to-exceed를 기여로 낸 논문 **못 찾음.** Kather/Arslan 2024(검증)가 최근접 "H&E가 뭘 예측 가능/불가"이나 **feasibility 총조사**(12,093 모델, 4,031 biomarker; "50% 모델 AUC≥0.644")로, subtype baseline과 대결 안 함. 그래서 `subtype_only`(p=0.613 동등) 프레이밍은 진짜 under-occupied.
**정직성 주의 2:** (i) 우리 천장은 `PAM50→ER`인데 PAM50/ER 분자적으로 얽힘(Luminal≈ER+) → "형태학이 PAM50-예측-ER 못 넘음"은 *부분적 tautology*, 리뷰어가 near-circular라 깜; (ii) well-powered 동등/음성 결과는 단독 출판 어려움.

**판정 1:** (a) 근접/좁은 갭 · (b) near-scooped · (c) 얇은 whitespace이나 standalone 약함. **종합: 단독 논문 불가, 더 큰 기여 안의 rigor 레이어로만 유효.**

### 2) Cheap-input 임상 유용성 (분자검사-free / LMIC / triage)
**동기로서 스쿱됨 — "비용/turnaround/assay 부재" 논거는 commoditized.** 여기 거의 모든 논문의 상투 정당화이며, **우리 최근접 스쿱의 첫 문장**: Fernandez-Romero 2026(검증 abstract) = *"PAM50과 IHC는 많은 세팅에서 비싸고 이용 불가."* Shamai 2024 제목 자체가 "**Clinical utility** of receptor status prediction." PANProfiler Breast는 이미 **UKCA 인증·blind-validated 배포 제품** *[snippet, unverified]*. 전용 **LMIC 비용-정량화**(정확도 vs assay 비용 tradeoff) 논문은 **못 찾음** — 얇은 whitespace이나 이건 동기이지 기여 아님, 단독 불가.

**구조적 긴장(반드시 해소):** #1은 "형태학이 분자 subtype 너머 못 준다", #2는 "분자 없을 때 형태학이 중요"인데, #1 천장(`subtype_only`)은 **PAM50=분자검사**를 요구 → assay-free 세계(#2)엔 그 baseline이 없음. 두 프레이밍이 다른 세계에 삶; 논문이 의도적으로 붙들어야 함.

**판정 2:** **프레이밍으로서 스쿱됨.** LMIC 비용-정량화는 진짜지만 얇음, 단독 불충분.

### 3) Agent/Critic 검증 치료가설 생성 (pathology → DepMap/GDSC → ranked hypothesis)
**최근접(파이프라인 기전 직접 스쿱):** Dawood, …, Rajpoot & Minhas, *npj Precision Oncology* 2024(**검증 abstract**). "*최초로* … DL이 유방암 H&E WSI의 조직패턴을 **세포주 유래 약물감수성**과 연결." gene-expression-mapped 세포주(GDSC류) 약물효과로 학습, 수백 개 승인·실험 약물 감수성 예측. 이미지→치료가설-via-세포주-전이, 유방, 이미 출판.
- **핵심 차이:** Dawood는 WSI에서 약물감수성 **직접 회귀** — **명시적 분자표현형 중간단계 없음, 에이전트 없음, Critic/거버넌스 레이어 없음.**

**Agentic/critic 레이어는 존재하나 pathology와 미결합:** Robin(arXiv 2505.13400), PharmaSwarm/BioScientist(bioRxiv 2025)가 actor-critic 약물가설 생성 — 단 knowledge graph/omics에서, **WSI-유래 표현형에서가 아님.**

**핵심(리뷰):** 리뷰어가 물음 *"왜 Dawood처럼 약물감수성 직접 회귀 안 하고 저차원 표현형 병목을 거치나?"* 유일한 방어 = **해석가능성 + `hypothesis_only` Critic 거버넌스** → 진짜 novelty는 **이미지-유래 치료가설을 검증하는 agentic Critic**이지 전이 파이프라인 자체가 아님. 명시할 것.

**판정 3:** "형태학 → 예측 표현형 → DepMap/GDSC 전이 → **multi-agent Critic 검증** 랭크 가설" 조합은 **통합 시스템으로서 진짜 whitespace** — 단 개별 부품은 다 스쿱, 표현형 병목은 Dawood 대비 *liability*, Critic/거버넌스가 헤드라인일 때만. **시스템/거버넌스 기여로만 방어 가능.**

### 4) 가장 위협적인 선행연구 (랭킹)
1. **Fernandez-Romero et al.** "Domain generalisation challenges in breast cancer molecular classification using foundation models", *Med Biol Eng Comput* 2026, vol 64. *검증.* → 우리와 동일 설계(13 FM+3 MIL, PAM50+IHC, TCGA-BRCA CV → CPTAC-BRCA 외부) **+** 동일 비용/assay-부재 동기. 서술적+외부검증 기여 스쿱. https://doi.org/10.1007/s11517-026-03590-4
2. **Dawood, Rajpoot, Minhas et al.** "Cancer drug sensitivity prediction from routine histology images", *npj Precision Oncology* 2024, vol 8. *검증.* → H&E→세포주 약물감수성(유방); #3 프레이밍 핵심. https://doi.org/10.1038/s41698-023-00491-9
3. **Shamai et al.** "Clinical utility of receptor status prediction … and misdiagnosis identification", *Commun Med* 2024, vol 4. *검증.* → "clinical utility"(#2)·discordance-as-QA(#1a) 소유. https://doi.org/10.1038/s43856-024-00695-5
4. **Arslan et al. (Kather group)** "A systematic pan-cancer study on DL-based prediction of multi-omic biomarkers", *Commun Med* 2024, vol 4. *검증.* → 최근접 "H&E 가능/불가" 총조사; 일반 feasibility 주장 선점. https://doi.org/10.1038/s43856-024-00471-5
5. **Naik et al.** ReceptorNet, "…hormonal receptor status from base-level H&E stains", *Nat Commun* 2020, vol 11. *메타데이터 재검증 안 함.* → ER AUC ~0.92 레드오션 anchor. https://doi.org/10.1038/s41467-020-19334-3
6. **"Deep learning on histopathology predicts recurrence risk and chemotherapy benefit"**, *Lancet Oncology* 2025. *[snippet, unverified]* → #1b(아형 내부 예후/치료이득) 위협. https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(25)00727-2/fulltext
7. **MAKO benchmark** 12+ FM/ABMIL for ROR-P from H&E, arXiv. *[snippet, unverified]* → FM+MIL 유방 벤치마크 중복. https://arxiv.org/html/2604.24679
8. **PANProfiler Breast — blind validation**, *Clinical Breast Cancer* 2025. *[snippet, unverified]* → 배포/규제승인 제품; "H&E predicts receptor" 임상유용성 주장 commoditize. https://www.clinical-breast-cancer.com/article/S1526-8209(25)00168-5/fulltext

### 5) 프레이밍별 정직한 판정
| 프레이밍 | 판정 | 출판되려면 |
|---|---|---|
| #1 Subtype ceiling / orthogonality | **Incremental, 부분 스쿱.** (b) near-scooped; (a) 좁은 갭; (c) under-occupied이나 천장 near-tautological(PAM50↔ER), 음성결과 배치 어려움 | 천장을 **비순환**으로: *비분자* baseline 사용, 또는 PAM50이 결정 못 하는 **진짜 orthogonal 엔드포인트**(아형 내부 outcome/내분비 저항)에서 형태학이 신호 추가함을 보일 것. 순수 "ties the baseline"은 통과 못 함 |
| #2 Cheap-input 임상 유용성 | **동기로서 스쿱.** | 단독 기여 아님. *정량화된* 증거(assay-free 정확도 vs assay 비용, prospective/triage 배포)로 실제 방법/시스템 기여에 붙을 때만 생존 |
| #3 Agentic Critic → 랭크 치료가설 | **방어가능 novel — 단 시스템/거버넌스 논문으로만.** 기전은 Dawood 스쿱; agentic-critic 레이어가 whitespace | 헤드라인 = **이미지-유래 치료가설을 검증하는 Critic/`hypothesis_only` 거버넌스**(falsification·baseline/leakage/counterfactual 게이팅·DepMap↔GDSC 일관성), *"H&E로 약물감수성 예측"이 아님*. 표현형 병목을 해석가능성으로 정당화 + Dawood 직접회귀 baseline을 이기거나 보완 |

**Bottom line:** #1·#2는 incremental-to-scooped, 리드 금지. 유일 방어 헤드라인 = **#3를 agentic, Critic-governed 가설생성 *시스템*으로 재구성**, #1 천장분석은 rigor/calibration 섹션으로 강등(baseline de-circularize 후), #2는 배포 동기로만. Fernandez-Romero 2026 외부 AUC는 post-cutoff·abstract에 숨어 있으니 "morphology ties the ceiling"을 기정사실로 쓰기 전 원문 대조.

---

## 3. novelty-strategist 리포트 — 차별화 + 값싼 실험 (원문 보존)

Adversarial. 우리 수치는 고정으로 취급. 레드오션 각은 명명 후 폐기(softening 없음).

### 1) 랜드스케이프 (뭘 하고 / 뭘 안 하나)
**Thread A — H&E → 분자 subtype + 외부검증 (우리 standalone; 이제 RED OCEAN)**
- **Fernandez-Romero, Med Biol Eng Comput 2026** — 13 FM × 3 MIL, PAM50+IHC, **TCGA-BRCA n=1079 → CPTAC n≈120.** HER2E·Normal-like 심각 외부 열화. *안 하는 것*: 치료 연결, morphology-vs-molecular 치환 비용 정량화, 표현형 하류 활용. **우리 논문의 절반이 이미 남에 의해 출판됨 — HER2 실패 포함.** [정확 AUC VERIFY 필요]
- **AI 분자 subtyping, population cohort, Cancers 2025** — subtyping 검증. *안 함*: 치료 연결, orthogonal 질문.
- **NSGA-II/MC-dropout PAM50, arXiv 2604.01798** [VERIFY id] — TCGA→CPTAC PAM50, patch-selection 최적화. *안 함*: 치료, 치환 비용.

**Thread B — H&E → 약물감수성 (치료 최근접)**
- **Dawood, npj Precision Oncology 2023/2024** — WSI graph GNN, **H&E→약물감수성 end-to-end**, 세포주 발현맵으로 환자 라벨 imputation; 유방 포함, multi-drug. *안 하는 것*: 표현형 병목 노출, 이미지 vs 분자검사 정보비용 정량화, 가설 게이팅 — 블랙박스 DRP. **1순위 must-cite-and-differentiate.**
- **Clin Cancer Res**(Lapatinib↑ HER2E, PI3Ki 저항 basal), **GDSC2 453-drug biomarker** — subtype→약물감수성 연관. *경쟁자 아닌 positive-control 문헌.*

**Thread C — 아형 내부 이질성/예후 (Angle-1 최근접)**
- **AACR Cancer Research Communications 2026** — DL로 **LumA purity/ITH from WSI → survival/임상.** *naive "intra-LumA prognosis"와 직접 중복.*
- **Breast Cancer Research 2020 (PMC6988279)** — 이미지 기반 intrinsic-subtype 분류가 생존 영향 ITH 드러냄.
- **npj Precision Oncology 2023 (s41698-023-00472-y)** — routine-H&E 조기 luminal 예후 마커.
- *종합*: intra-LumA 예후-from-H&E는 **이미 crowded**. "CNN 대신 UNI/CONCH 썼다"는 차별자 아님.

### 2) 스쿱/동시연구 판정
| 연구 | 라벨 | 겹치는 주장 | 우리 차별화 |
|---|---|---|---|
| Med&BiolEngComput 2026 (13 FM×MIL, TCGA→CPTAC) | **SCOOP(재프레이밍 필수)** | H&E FM+MIL이 PAM50/IHC 예측; HER2 포함 외부 열화 | 예측 재판매 금지. 형태학=subtype 충실한 그림자의 *증거*로 인용 후 기여를 치료공간으로 이동 |
| npj Prec Oncol 2023 (WSI→drug GNN) | **must-cite-and-differentiate** | 이미지→약물감수성, 세포주-imputed 라벨, 유방 | 우린 DRP 아님. 그들 설계가 구조상 노출 못 하는 *표현형-치환 비용* 측정; hypothesis_only + Critic gate |
| AACR CRC 2026 (LumA ITH→survival) | **must-cite-and-differentiate** | 형태학→intra-LumA 이질성→outcome | 또 하나의 survival 논문 아니라, 치료 관련 *연속 residual*(proliferation/ROR-P)로 접음 |

**Bottom line:** standalone 표현형예측+multi-FM+외부검증은 **레드오션으로 기각** — 독립 재현됨, HER2 실패까지. 한 줄("consistent with [2026]") 넘게 방어에 figure 쓰지 말 것.

### 3) 차별화 기여 (novelty × 임상의미 / 비용 랭킹)

**⭐ C1 — Cost-of-substitution: 분자검사 대신 H&E를 읽는 치료적 비용 정량화 (CENTERPIECE)**
- **주장:** morphology-예측 subtype을 측정 subtype 대신 쓰면 *냉동* 세포주→약물 랭킹이 **아형 의존적·정량 가능한 만큼** 열화 — luminal 축 내부는 ≈0(LumA↔B 혼동 둘 다 내분비/CDK4-6로 라우팅), HER2는 파국(오분류가 항HER2 랭킹 붕괴). 형태학은 분자검사가 필수인 곳 빼고 치료적으로 충분한 triage 레이어.
- **왜 방어가능 novel:** DRP crowd(npj 2023)는 end-to-end라 표현형 병목 노출 안 함 → **아무도 이 비용을 측정 안 함.** end-to-end 아키텍처가 *구조상 못 내는* 유일한 숫자. "ties the subtype ceiling"을 thesis로 전환: 치료공간에서 값싼 입력이 *더 적게* 잃음.
- **가장 싼 실험(가진 데이터):** GDSC/DepMap 유방 세포주를 PAM50 그룹핑해 `subtype → 약물감수성 벡터` **냉동 지도 하나** 구축(세포주-only; TCGA 발현 미투입 = 누수 가드). CPTAC 환자마다 *같은 지도*로 두 랭킹: **A**=측정 subtype, **B**=H&E-예측(CLAM-MB) subtype. divergence(Kendall-τ/top-k overlap)를 **subtype-구별 약물에서만**, 진짜 subtype별 층화, `subtype_only→therapy` 대비 벤치.
- **가장 치명적 반론:** *"순환 — subtype AUC 높으면 약물 랭킹 당연히 일치; drug 공간에서 AUC 재유도."* **선제:** concordance 아니라 *임상* 비용함수 보고 — LumA↔LumB 오차는 τ손실≈0, HER2 오차는 항HER2 거의 전멸; 이 *라벨오차↔치료오차 해리*가 발견이며 AUC 표에서 복원 불가.
- **2차 반론:** *"짧은 유방 약물 메뉴 → 전역 overlap 당연히 높음."* **선제:** subtype-구별 약물만 채점; 전역 top-k 아닌 subtype별 보고.

**⭐ C2 — Critic-gated 치료가설 파이프라인 + 사전등록 miss-rate (프로젝트 고유 자산)**
- **주장:** 투명한 H&E → 표현형 → DepMap/GDSC → **랭크, hypothesis_only** 체인이 확립된 subtype-약물 관계를 *positive control*로 복원(ER+→내분비; HER2+→항HER2; basal→화학/PI3Ki-저항), 비복원 랭킹은 miss-rate로 보고 — cherry-pick 아님.
- **왜 방어가능 novel:** 기존 H&E-치료 연구 중 *auditable* 파이프라인 + anti-self-reference Critic + 정직한 실패 회계 없음. 7항목 Critic + `hypothesis_only` 스키마는 진짜 방법 기여.
- **가장 싼 실험:** 랭킹 파이프라인 동결, top-k subtype→drug 출력 **사전등록**, 그다음 *고정* 문헌/clinicaltrials.gov 조회 프로토콜로 hits **와** misses 보고. positive control은 *파이프라인* 검증이지 발견 아님.
- **가장 치명적 반론:** *"post-hoc cherry-pick — 가설 본 뒤 논문 찾음"*(Critic #6/#7 실패). **선제:** 사전등록 + miss-rate + "알려진 링크 복원=배관 검증이지 novelty 아님" 명시. DRP 가드 문장: *"morphology가 환자를 세포주 감수성 시그니처 enriched 아형으로 층화"*, 절대 *"약물반응 예측"* 아님.

**C3 — Orthogonal 연속 residual, 치료 스토리 안으로 접음 (standalone 예후 논문에서 강등)**
- **주장:** 형태학이 이산 PAM50 라벨 너머 *아형 내부 연속* 치료관련 신호(예: TCGA RNA-seq proliferation/ROR-P) 보유, 이 residual이 치료 랭킹 이동(고증식 LumA → 화학이득 가설).
- **왜 Thread C 대비 novel:** 또 하나의 intra-LumA survival 아님(crowded, 그리고 — flag — TCGA-BRCA OS event 보통 <15%, intra-LumA HR엔 underpowered일 것; CPTAC는 survival 외부검증 불가). 대신 *분자-특성화* 주장으로 C1/C2 공급: molecular-LumA인데 H&E→LumB로 불린 케이스가 고증식 enriched인가?
- **가장 싼 실험:** TCGA에서 PAM50 클래스 내부 FM 임베딩 vs 연속 proliferation 회귀(교차검증), residual이 치료관련 축 예측하는지. **전제:** survival 엔드포인트 고집 시 먼저 subtype별 event-count 체크 — underpowered면 순수 분자로 유지.
- **가장 치명적 반론:** *"H&E 아형내부 이질성은 done(AACR CRC 2026)."* **선제:** 이질성 발견 주장 아니라, 연속 residual로 C1 비용지도 sharpening(sub-label 형태학이 치료 콜을 바꾸는 곳).

**기각 — 추진 금지:** standalone "H&E가 ER/PR/HER2/PAM50 예측 + 외부검증 + multi-FM." Med&BiolEngComput 2026에 HER2 실패까지 스쿱. EXAONE slide_global ER 0.923도 헤드라인 금지 — 내부 tiling/집계 혼재, 리뷰어가 apples-to-oranges라 깜.

### 4) 최소 rigorous 치료 체인 (C1+C2 결합) — 혼란변수 통제
1. **냉동 지도(세포주-only):** GDSC/DepMap 유방 세포주 → PAM50 그룹 → 약물감수성 벡터. *누수 가드:* TCGA/CPTAC 발현 미투입. *Flag&정량:* subtype별 세포주 수 세기 — **HER2E/Normal-like support 얇음**; 명명하고 어디까지 유효한지 진술(LumA 바닥을 천장으로 오도 금지).
2. **같은 지도로 환자당 두 랭킹:** A=측정 subtype, B=H&E-예측 subtype. subtype 입력만 바뀜 → divergence는 형태학에 깨끗이 귀속.
3. **비용 metric:** τ/top-k overlap on subtype-구별 약물, 진짜 subtype 층화; baseline=`subtype_only→therapy`.
4. **Positive control:** ER+→내분비, HER2+→항HER2, basal→화학/PI3Ki-저항 복원 필수. 실패=파이프라인 버그, 생물학 아님.
5. **정직 보고:** 사전등록 top-k; hits **및** miss-rate; 모든 출력 `hypothesis_only`; per-experiment DRP-가드.
- **핵심 혼란변수를 결과로:** *"H&E 대신 분자 쓰는 비용"* = divergence(A,B). 기여 = *비용이 ≈0인 곳(안전한 값싼 triage) vs 폭발하는 곳(HER2→분자 필수)의 지도.*

### 5) 정직한 판정 + thesis
**판정:** 현 프레이밍은 **재프레이밍 필요, 예측 실험 추가 아님.** 예측 절반은 스쿱; 치료 절반이 유일 방어지, DRP 필드가 표현형-치환 비용을 노출 안 했으므로 진짜 열려있음. 최고 레버리지 단일 수 = **냉동 세포주→약물 지도 구축 + dual-ranking cost-of-substitution 실험(C1)을 이번 스프린트에 CPTAC로 실행** — 싸고(이미 가진 임베딩+GDSC), 약한 숫자를 논점으로 재프레이밍, C2 de-risk.

**추천 thesis ("천장 비김 + HER2 실패" 생존):**
> *H&E 형태학은 분자 subtype의 충실하지만 값싼 그림자 — 라벨 예측에서 subtype 천장을 넘지 못하고 비긴다. 우린 이걸 실패로 두지 않고 임상적으로 결정적 질문을 한다: 값싼 그림자를 냉동 세포주 치료 지도에 넣으면 진짜 분자검사 대비 치료-랭킹 충실도를 얼마나 잃는가? 손실은 subtype 의존적이고 대개 작다 — luminal 혼동은 같은 내분비/CDK4-6로 라우팅되어 치료적으로 무해 — 그래서 H&E는 분자검사 없는 곳에서 가설생성에 충분한 triage 레이어다. 붕괴하는 유일한 곳은 HER2로, 형태학 오분류가 항HER2 랭킹을 파괴하므로 거기선 분자검사가 non-negotiable. 기여는 더 나은 예측기가 아니라, 값싼 형태학이 치료적으로 충분한 곳과 아닌 곳의 정량·Critic-gated·hypothesis-only 지도다.*

**[VERIFY 플래그(에이전트):** Med&BiolEngComput 2026 정확 외부 AUC, arXiv id 2604.01798 — 인용 전 원문 확인.**]**

---

## 4. 검증 (이 세션, 2026-07-10)

### 🔴① Fernandez-Romero 2026 — 스쿱 CONFIRMED (열린 메타 실측 확보; 표-단위 수치는 전문 호스트 네트워크 차단)
**식별자:** DOI 10.1007/s11517-026-03590-4 · **PMID 42113320 · PMCID PMC13269319 · OpenAlex W7160869106 · is_oa=true.** 게재 2026-05-11, Med Biol Eng Comput.

**Abstract 전문(OpenAlex/Semantic Scholar API로 verbatim 확보):**
> "Molecular classification guides breast cancer treatment, but PAM50 and IHC remain costly and unavailable in many settings. FMs combined with MIL show promise for predicting molecular subtypes from H&E slides, yet most studies report only internal validation. … We evaluate **13 FMs and 3 complementary MIL architectures** for PAM50 subtyping and IHC biomarker prediction using cross-validation on **TCGA-BRCA (n=1,079)** and external validation on **CPTAC-BRCA (n=120)**. **Virchow v2 achieves the best overall performance but exhibits severe degradation upon external validation**, consistent across all three MIL architectures **especially for HER2-enriched and Normal-like PAM50 subtypes and HER2-positive IHC prediction**. Four hypothesised domain shift factors are quantified … Staining variability, feature space divergence and morphological separability reach significance …; **staining variability and feature space divergence jointly account for 80.0% of RPD variance (R²=0.800, R²adj=0.750)**. … exploratory in nature …"

**추가 실측(WebSearch snippet extraction):**
- **지표(중요): ER/PR/HER2 = PR-AUC, PAM50 = macro-F1** 로 보고 — **AUROC 아님.** → 그들 숫자는 우리 AUROC와 *직접 비교 불가*. 우리가 "그들도 같은 AUROC"라 말할 수 없고, 그럴 필요도 없음.
- **모델 mean ranking:** Virchow v2 **2.00** > Prov-GigaPath 4.13 > H-optimus-0 4.25 ≈ UNI-2 4.25.
- **HER2-enriched: 외부 완전 붕괴(RPD = 1.000, 전 모델).**
- RPD 동인: staining variability + feature space divergence(공변량 shift)가 80% 설명; prevalence shift는 유의하지 않음.

**표-단위 per-model 정확 수치(내부 vs 외부 PR-AUC/F1):** OA 전문이 PMC(PMC13269319)에 존재하나 **ncbi.nlm.nih.gov·ebi.ac.uk 호스트가 이 실행환경에서 DNS 타임아웃**(paywall 아님, 네트워크 차단). springer·semanticscholar·openalex는 정상. → **사용자 PDF 업로드 시 즉시 표 추출 가능.** 단 지표가 PR-AUC/F1이라 우리 AUROC와 대조 목적엔 **불필요**할 수 있음.

**함의(확정):** 우리 서술적 결과(예측+외부검증+multi-FM)는 스쿱 확정, **우리 HER2 외부 실패도 그들이 RPD=1.00으로 재현.** 인용은 정성으로 충분("[Fernandez-Romero 2026]은 CPTAC 외부검증에서 HER2-enriched 완전 붕괴(RPD=1.00)를 보고 — 우리 HER2 reject와 일관"). "morphology ties the ceiling"은 *우리* registry 수치(ER 0.894 vs subtype_only 0.918, p=0.613)라 이미 확정 — 순환성(§2-1c)만 해소하면 됨.

### 🔴② 세포주 아형별 support — 얇음 CONFIRMED(directional), 정확 카운트 미측정
- **로컬 근거:** `agents/therapeutic_evidence/docs/BIOP02-52_prism_gdsc_consistency.md`(jhans) — **DepMap 유방 ~75, GDSC2 유방 ~50, 교집합 ~35–45(v0.2 실측 예정, 아직 추정).** PRISM 전체 4,518 약물 × 578 세포주.
- **PAM50 아형별 세포주 카운트는 로컬 문서에 없음** — 세포주는 통상 PAM50 typing 안 됨. 교집합 ~40개를 5 아형에 나누면 **HER2E 소수, Normal-like 사실상 없음**(Normal-like는 세포주에서 artifact/contamination로 간주되어 거의 부재). → literature-scout·novelty-strategist의 "HER2E/Normal-like support 얇음" **방향적으로 확정.**
- **함의(C1 feasibility 리스크, 신규):** 냉동 세포주→약물 지도의 신뢰 범위는 **luminal(LumA/B)·basal에 한정**될 공산. HER2E는 지도가 얇아 "HER2에서 붕괴" 주장을 세포주 지도로 세우기 전 support 카운트를 **실측(jhans v0.2)** 하고 명시해야 함. Normal-like는 지도에서 제외/별도 처리.
- **선행 자원 정리 위치:** `research/morphology-drug/`(Dawood 2024·PRISM·GDSC·CCLE·DepMap brief 이미 존재), `research/datasets-benchmarks/parker-2009-pam50`. 세포주 PAM50 라벨 소스는 별도 확보 필요(예: CCLE 발현 기반 PAM50 재계산 or 문헌 주석).

---

## 5. 종합 — 함정 · 재조정 · 최종 권고

### 두 함정(literature-scout가 포착, novelty-strategist가 흘림)
- **함정 A — subtype 천장 near-tautological:** `PAM50→ER`, PAM50↔ER 얽힘. "형태학이 PAM50 baseline 못 넘음"은 당연 → 리뷰어가 순환이라 깜.
- **함정 B — #1↔#2 세계 충돌:** #1 천장은 PAM50(분자검사)을 요구, #2 세계엔 부재.
- **함정 C — 병목이 Dawood 대비 약점:** 직접 회귀가 표현형 병목보다 강해 보임.

### 재조정(함정이 해답을 가리킴)
- **표현형 병목 = 예측엔 약점, 거버넌스엔 자산.** Dawood 블랙박스는 병목이 없어 **치환비용 측정·가설 게이팅 불가.** 우리 병목이 그걸 가능케 함 → 함정 C의 답 = "병목이 있어야 cost-of-substitution·Critic 게이팅이 됨." C1이 함정 C를 막음.
- **함정 A 해소:** cost-of-substitution을 **라벨 공간이 아닌 치료 공간**에서 정의 — "형태학 표현형 오분류가 치료 랭킹으로 전파되는 양"(라벨오차↔치료오차 해리). 순환적 천장 baseline 강등/폐기.
- **함정 B 해소:** #2는 기여 아닌 **배포 동기로만.** 본체=#3 시스템+C1, 천장분석은 de-circularize 후 calibration으로 강등.

### 최종 권고 (승부처)
> **헤드라인:** H&E-유래 치료가설을 검증하는 **agentic Critic 거버넌스 시스템**(falsification·baseline/leakage/counterfactual 게이팅·DepMap↔GDSC 일관성·`hypothesis_only` 스키마). 예측기·전이 파이프라인 아님.
>
> **플래그십 실험 = cost-of-substitution(C1):** 냉동 세포주→약물 지도에 (A)측정 아형 vs (B)H&E-예측 아형 → 치료 랭킹 divergence 아형별 층화. LumA↔B ≈0(내분비 수렴), HER2 붕괴(분자검사 필수). 병목 정당화 + "천장 못 넘음" 논점화.
>
> **C2:** positive control(알려진 관계 복원) + 사전등록 miss-rate로 hits·misses 정직 보고.
>
> **thesis:** §3-5 인용문.

### Owner≠Reviewer / 제약 준수
- `hypothesis_only`, BRCA-only, DRP 프레이밍 금지, ICI/pembro 세포주 전이 금지 — 전 실험에 per-experiment 가드 문장.
- Critic 7항목 중 #4(DepMap↔GDSC 일관성, jhans BIOP02-52)·#2(baseline)·#1(leakage: 냉동 지도 세포주-only)·#6(DRP)·#7(claim-level)이 C1/C2에 직접 걸림.

---

## 6. 열린 리스크 & 다음 스텝

**열린 리스크:**
1. **세포주 아형 support(C1 feasibility):** HER2E/Normal-like 얇음 → jhans v0.2 실측(BIOP02-52) 필요. Normal-like 제외 정책 확정.
2. **세포주 PAM50 라벨 소스:** 별도 확보(CCLE 발현 기반 PAM50 재계산 or 문헌). 누수 가드(TCGA/CPTAC 발현 미투입) 유지.
3. **Fernandez-Romero 정확 AUC:** paywall — 기관 접근 or 저자 문의로 표-단위 확보(정성 인용은 가능).
4. **near-scoop 감시:** Lancet Oncol 2025(#1b), MAKO/PANProfiler(unverified) — 인용 전 확인.
5. **Dawood 대비 baseline:** C2가 Dawood 직접회귀를 이기거나 보완함을 실증해야(해석가능성+거버넌스 논거만으론 부족할 수 있음).

**다음 스텝(권고 순):**
1. **research-methodologist로 전환** — 위 #3(시스템)+C1을 정식 가설·contribution statement·실험설계(냉동 지도 구성, 누수 가드, cost metric, positive control, 사전등록 miss-rate, Dawood baseline)로.
2. jhans에 **세포주 유방 subset 아형별 카운트 실측**(BIOP02-52 v0.2) 요청 — C1 feasibility 게이트.
3. 세포주 PAM50 라벨 소스 확정.
4. (선택) Fernandez-Romero 기관 접근으로 정확 AUC 확보.

---

## 7. Sources (전체)

**검증됨(EuropePMC/WebSearch):**
- Fernandez-Romero et al., Med Biol Eng Comput 2026 — https://doi.org/10.1007/s11517-026-03590-4
- Dawood et al., npj Precision Oncology 2024 — https://doi.org/10.1038/s41698-023-00491-9
- Shamai et al., Commun Med 2024 — https://doi.org/10.1038/s43856-024-00695-5
- Arslan/Kather et al., Commun Med 2024 — https://doi.org/10.1038/s43856-024-00471-5
- Naik et al., Nat Commun 2020 — https://doi.org/10.1038/s41467-020-19334-3
- Couture et al., npj Breast Cancer 2018 — https://www.nature.com/articles/s41523-018-0079-1

**snippet/unverified (인용 전 확인):**
- Lancet Oncol 2025 (recurrence/chemo benefit) — https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(25)00727-2/fulltext
- MAKO FM benchmark (arXiv) — https://arxiv.org/html/2604.24679
- PANProfiler Breast, Clinical Breast Cancer 2025 — https://www.clinical-breast-cancer.com/article/S1526-8209(25)00168-5/fulltext
- LumA subtype purity (medRxiv 2023) — https://www.medrxiv.org/content/10.1101/2023.02.27.23286511
- high-risk ER+/HER2− image analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC11616316/
- Robin multi-agent discovery — https://arxiv.org/pdf/2505.13400 · PharmaSwarm — https://arxiv.org/pdf/2504.17967
- NSGA-II PAM50 pipeline — https://arxiv.org/abs/2604.01798 (arXiv id VERIFY)

**로컬 근거:**
- `experiments/registry/cross_validation_registry.jsonl` (우리 외부검증 수치)
- `agents/therapeutic_evidence/docs/BIOP02-52_prism_gdsc_consistency.md` (세포주 교집합 ~35–45)
- `research/morphology-drug/` (Dawood 2024·PRISM·GDSC·CCLE·DepMap brief)

---

## 8. Tier B (endpoint 전환) 실현가능성 — literature-scout 2차 (2026-07-10)

**핵심 모순:** *임베딩 재사용(저비용) 가능한 endpoint는 이미 스쿱, 임상 의미 높은 endpoint(pCR)는 새 데이터 필요(임베딩 재사용 불가·고비용).* **주어진 제약(임베딩 재사용·GPU≈0)에서 Tier B 중 Tier A를 깨끗이 이기는 건 없음.**

| 순위 | Endpoint | novelty | 임상 | 재사용 | 진입비용 | 판정 |
|---|---|---|---|---|---|---|
| B1 | **pCR(전처치 H&E, HER2+/TNBC subgroup, FM 벤치+외부검증)** | 중(좁은 whitespace) | **높음** | **없음** | **높음**(새 슬라이드: IMPRESS n=126 + 2차 코호트, 새 tiling/추출) | 데이터 확보 의지 있으면 최선 |
| B2 | 형태–유전체 discordance as biology | 중–고 | 낮–중 | 부분(TCGA/CPTAC RNA) | 중 | 열려있으나 임상적으로 물렁 |
| B3 | TIL/공간 면역 | 낮 | 중(성숙) | **순환**(Saltz-2018 자동점수 예측=모델로 모델 예측) | 중(TIGER) | 레드오션 |
| B4 | 아형내 예후/ITH/stroma | 낮 | 중 | **완전** | ≈0 | **스쿱**(MAKO npj Dig Med 2026이 우리 정확한 재사용 실험=12 FM×MIL ROR-P, TCGA 외부검증 이미 냄; ITH 2023) — 진입 금지 |

**결정적:** 우리가 "공짜 재사용"으로 기대한 B4(예후/ITH)는 **MAKO(npj Digital Medicine 2026)가 우리 데이터로 우리 실험을 이미 출판.** 유일한 고임상 B는 **pCR**인데 새 데이터 필요 + 2025 attention-MIL TNBC 논문이 이미 "MIL+외부검증+subgroup+mIHC" 슬롯 점유.

**pCR 진입점(직접 실행 시):** 공개 **IMPRESS**(전처치 biopsy, n=126: HER2+ 62/TNBC 64, H&E+IHC; [npj PO 2023](https://www.nature.com/articles/s41698-023-00352-5), [GitHub](https://github.com/huangzhii/IMPRESS)) + 2차 코호트. 방어각 = *UNI/CONCH/EXAONE FM 벤치 for pCR in HER2+, 정직한 다중코호트 외부검증 + "FM이 임상변수 baseline 이기나?" 정직성 테스트*(우리 Critic 체크리스트 강점). ⚠️ TCGA/CPTAC엔 pCR 없음 확정 → 기존 임베딩 재사용 불가.

**권고:** (1) B4(공짜 재사용)는 진입 금지(MAKO·ITH-2023 스쿱). (2) **Tier A를 실용 디폴트로 유지**(제약 부합 유일). (3) pCR(B1)은 *의도적 데이터획득 프로젝트*로만, 저비용 재사용 아님.

**Sources(B):** IMPRESS npj PO 2023 · MAKO = Kaczmarzyk et al., *npj Digital Medicine* 9:149 (2026), DOI 10.1038/s41746-025-02334-2 [서지 확정 2026-07-17; ROR-P 재발위험 예측 — subtype 분류 아님] · attention-MIL TNBC pCR Cancers 2025 (arXiv 2505.14730) · TIGER challenge · Saltz TIL Cell Rep 2018 · ITH Eur J Cancer 2023 · POST-NAT-BRCA/BCNB(pCR 라벨 없음).

---

## 9. D2/D3 (H&E 없는 치료증거 트랙) 스쿱 — 2026-07-10

- **D3 (BRCA subtype CRISPR dependency → target): 🔴 RED OCEAN, 2025년에 두 번 스쿱.** Lin/Dai/Pusztai(Breast Cancer Res Treat 2025, 48 breast lines·DGIdb·subtype 66/53/29 targets) + Ding/Shao/Yu(Cancer Biol Med 2025, subtype dependency + **PRISM 교차검증까지**). Critic 거버넌스=packaging, 구제 불가. + Sannigrahi(Mol Oncol 2023)가 일반화 파이프라인 템플릿. **드롭.** (데이터도 CRISPRGeneEffect.csv 미보유 + ~48 라인 underpowered.)
- **D2 (PRISM TNBC repurposing): 🟠 얇은 whitespace.** 체계적 PRISM→GDSC breast repurposing이 의외로 미출판(리뷰 Jurj 2025가 PRISM 미인용)이나, Corsello 2020(PRISM 원자원, pan-cancer) 슬라이스 + ~50 라인 underpowered + wet 검증 0 → 약함. hypothesis_only Paper B sidecar로만.
- **결론: 둘 다 Tier A 못 이김.** D3 사망, D2는 A 공급용 내부 가설생성으로만. Critic 거버넌스는 방법 한 문단이지 primary novelty 아님(underpowering 못 고침).
- Sources: Corsello Nat Cancer 2020(32613204), Lin 2025(10.1007/s10549-025-07817-0), Ding/Shao/Yu 2025(Cancer Biol Med 22(12):1605-1626, DOI 10.20892/j.issn.2095-3941.2025.0290 — 서지확인 2026-07-17), Sannigrahi 2023(PMC10850805), Jurj 2025(PMC12471285).

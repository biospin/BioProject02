# Writing-Target Guide — npj Precision Oncology H&E→분자 논문 골격 분석

우리 원고(5개 암종에 걸친 "cost-of-substitution" 결정 지도, H&E가 언제 값비싼 분자검사를 싸게 대체할 수 있는가를 사전등록된 법칙으로 제시)를 npj Precision Oncology 수준 이상으로 쓰기 위해, 같은 저널에 실린 가장 가까운 H&E→분자 예시 논문 4편을 실제로 읽고 그 **논리·형식·표·그림**을 해부한 문서다. 각 관찰은 어느 논문에서 나온 것인지 명시했다. 지어낸 내용은 없으며, 논문에 실제로 있는 것만 옮겼다.

분석 대상은 다음 네 편이다.

- **Paper A** — 자궁내막암 분자아형을 H&E에서 예측하는 해석가능 딥러닝 (s41698-026-01280-w, 2026)
- **Paper B** — 자궁경부암 consensus molecular subtype(CMS)를 조직학에서 예측 (s41698-024-00778-5, 2025)
- **Paper C** — H&E에서 실행가능한 NSCLC 바이오마커를 검출하는 딥러닝의 검증 (s41698-025-01267-z, 2025)
- **Paper D** — Dawood et al., "Cancer drug sensitivity prediction from routine histology images" (s41698-023-00491-9, 2024) — 같은 저널의 가장 가까운 경쟁 논문

---

## Paper A — 자궁내막암 분자아형 예측 (interpretable DL)

### Structure
표준 IMRaD에 Results를 잘게 나눈 형태다. 순서는 Introduction → Results → Discussion → Methods. Results 아래 소제목은 "Model performance and cohort overview", "Patch-level visualization of morpho-molecular correlates", "Extraction and analysis of single-cell nuclear features"로 나뉜다. Methods도 "Data preparation and molecular classification", "Deep learning pipeline", "Patch-level visualization", "Correlations between single-cell nuclear features and molecular subtypes"로 구조화되어 있다. 본문 자체는 길게 읽히며(약 8,000단어급, 다수의 supplementary 표를 참조), 성능 수치는 본문·그림 캡션에 흩어져 있다.

### Abstract
구조화된 초록이다. 주장 → 방법 → 결과 → 결론 순으로 약 11문장. 리드 문장은 성능 숫자가 아니라 임상적 중요성("The molecular subtype of endometrial cancer is important for predicting prognosis and treatment effectiveness")으로 시작하고, 핵심 결과로 Fudan 코호트 5-fold CV에서 macro-average AUROC 0.867 (95% CI 0.823–0.911), 네 아형(MSI-H, NSMP, p53abn, POLEmut)에 걸쳐 class-wise AUROC 0.835–0.910을 제시한다.

### Figures (5개)
Figure 1이 파이프라인 도식이 **아니라** 성능 그림이라는 점이 특징이다.
- **Fig 1 = 성능**: (A) Fudan 5-fold CV의 macro + 아형별 ROC 곡선, (B) Suzhou 외부검증 ROC, (C) TCGA 외부검증 ROC, (D) 제안모델 vs 베이스라인(AB-MIL, CLAM, MIL) 비교(폴드 간 표준편차 포함).
- **Fig 2 = 해석가능성**: Grad-CAM 히트맵(빨강=고활성)과 대응하는 H&E 조직을 나란히 배치, 아형별 형태학적 상관물(MSI-H의 기질 림프구 밀도, POLEmut의 solid growth 등).
- **Fig 3 = 단일세포 핵 특징**: (A) 아형별 세포 수 막대그래프, (B) 84개 특징과 아형 간 Spearman 상관 히트맵, (C) 상관 분포 박스플롯.
- **Fig 4 = 데이터 준비 도식**: Fudan/TCGA/Suzhou 코호트 분할 흐름도.
- **Fig 5 = 딥러닝 파이프라인 도식**: WSI → tiling → tumor segmentation(DeepLabv3) → stain normalization(Vahadane) → EfficientNetV2 → soft voting.

즉 스키매틱 개요도가 Fig 4–5로 **뒤로 밀려나** 있고, 성능·해석가능성이 앞을 차지한다.

### Tables
본문 성능표는 없다. 13개 이상 표가 대부분 supplementary로, S1은 아형별 코호트 인구통계(n, 나이, 조직형, FIGO stage, grade, recurrence), S7–S13은 코호트별 class-wise AUROC·민감도·특이도·정확도·정밀도·recall·F1·NPV, S4는 베이스라인 대비 비교표다. **핵심 성능은 그림 캡션과 본문에 임베드**되어 있다.

### Performance reporting
주지표 AUROC, 모든 값에 95% CI. 내부는 5-fold stratified CV, 외부는 두 코호트(TCGA n=296, Suzhou n=36). 베이스라인은 동결 UNI foundation encoder 위에 얹은 6개 weakly-supervised 프레임워크(TransMIL, AB-MIL, CLAM-SB/MB, Max/Mean-Pooling)와 비교. 불확실성은 5-fold 표준편차로만 표현(Bayesian credible interval 없음). 저자는 POLEmut의 낮은 유병률·class imbalance 때문에 precision/recall/F1/민감도가 "relatively poor"함을 스스로 인정.

### Rigor
TRIPOD/CLAIM/STARD 명시 없음. "interpretable"·"proof-of-concept"로 스스로를 규정하고 임상검증 시험이 아님을 밝힘. 코드 공개(GitHub 2개 저장소 + Zenodo DOI 아카이브). Fudan/Suzhou는 요청 시 제공, TCGA는 공개. 5-fold stratified CV + 두 개 독립 외부 코호트(중복 없음), multi-center. 사전등록 없음. Fudan의 POLEmut 과대표집을 referral bias로 정직하게 언급.

### Framing
Introduction은 gap으로 연다: 현재 분자분류는 IHC(주관적·가변적)나 시퀀싱(비싸고 저자원 환경에서 접근 불가)에 의존하며, 자궁내막암에서 H&E 딥러닝 연구는 "only a few"뿐이고 선행연구는 해석가능성 부족·binary task·tumor-only filtering 미비의 한계가 있었다. Novelty는 end-to-end 학습(동결특징 MIL 대비 계산비용 절감), Grad-CAM 세밀 해석, tumor segmentation 전처리, 2.45억 세포·84특징의 세포수준 통찰. Discussion은 (1) POLEmut 성능, (2) 코호트 편향, (3) 짧은 추적으로 예후검증 불가를 한계로 명시하고, **"guideline molecular testing를 대체하는 게 아니라 H&E-first, human-in-the-loop triage 도구"**로 임상적 위치를 조심스럽게 잡는다.

---

## Paper B — 자궁경부암 CMS 예측 (histology→molecular subtype + 예후)

### Structure
IMRaD에 Results를 6개 소제목으로 확장. 순서 Introduction → Results → Discussion → Methods → Data/Code availability. Results 소제목: "Pipeline for CMS prediction and TME profiling", "Prediction of CMS from H&E-stained WSIs", "Digital-CMS score association with prognosis", "Histological features associated with CMS", "TME patterns associated with CMS", "Immunological patterns associated with CMS", "Higher lymphocytic infiltration in C1 tumours". 장문. **예측 정확도만이 아니라 예후 층화(survival)까지 밀어붙이는** 구성이 특징.

### Abstract
비구조화 산문 약 6문장. 리드는 역학적 무게("Cervical cancer remains the fourth most common cancer among women worldwide")로 시작. 핵심 수치는 AUC가 아니라 **예후 층화 p값**: 세 코호트 n=545, Digital-CMS가 TCGA(DSS p=0.0022, DFS p=0.0495)와 Oslo(DSS p=0.0495, DFS p=0.0282)에서 생존 층화. 즉 "분자검사를 조직학으로 대체해도 예후 신호가 산다"는 게 헤드라인.

### Figures (9개 — 가장 그림이 많음)
- **Fig 1 = 파이프라인 스키매틱**: patch 추출 → UNI feature encoding → TripletMIL → patch-level + slide-level score → TME 분석 흐름.
- **Fig 2 = 교차코호트 설계 + AUC**: (a) 세 개 train/test 분할 도식, (b) threefold CV ROC(AUC 0.78±0.03, 0.85±0.04, 0.85±0.02).
- **Fig 3 = Kaplan–Meier 생존곡선**: Digital-CMS vs molecular-CMS를 DSS/DFS로, TCGA·Oslo에서 log-rank p값.
- **Fig 4 = 다변량 Cox forest plot**: HPV type·stage·age·treatment 보정한 HR + 95% CI.
- **Fig 5 = 조직학 패턴 + WSI 히트맵**: (a) C1(파랑)/C2(빨강) 영역 히트맵, (b) 코호트별 exemplar patch.
- **Fig 6–9 = TME/면역 정량**: 세포밀도 박스플롯, 호중구·림프구 비(NLR), CD8+ IHC score vs Digital-CMS 산점도(rho=−0.22, p=0.0007, n=229), 종양침윤림프구(TIL) 분석.

### Tables
본문 표 없음(!). Supplementary Table 1은 Digital-CMS vs molecular-CMS의 C-Index 비교와 DeLong test p값(두 접근 간 유의차 없음, p>0.05). 즉 **"조직학 대체물이 분자 원본과 통계적으로 동등하다"를 표로 못박음** — 우리 cost-of-substitution 논지에 직접 대응하는 표 설계.

### Performance reporting
CMS 분류는 교차코호트 AUC(mean ± SD): 세 설정에서 0.78±0.03, 0.85±0.04, 0.85±0.02. 생존은 log-rank p값 표로, 다변량은 Cox HR + 95% CI forest plot. Digital-CMS vs molecular-CMS를 **DeLong test로 C-Index 동등성 검정**. 상관은 Spearman(Benjamini–Hochberg 보정). 컷오프는 discovery set ROC에서 Youden's J로 선택. 외부검증은 세 대륙 코호트(TCGA/미국, Uganda, Oslo/노르웨이) 교차, Uganda는 HIV+ 63%로 생존분석에서 제외.

### Rigor
TRIPOD/CLAIM/STARD 명시 없음(저자도 IMRaD가 부분적으로 TRIPOD와 정렬된다고만 언급). 코드 공개(GitHub). TCGA·Uganda 공개, Oslo 요청 시. 사전등록 없음. **Site-disjoint를 세 개 대륙 코호트로 강하게** 구현("three different continents, reflecting demographic differences"). 윤리 승인·동의 명시.

### Framing
Introduction gap: 선행연구(Chakravarthy 2022)가 multi-omics로 HPV+ CSCC의 두 CMS를 발견했지만 "the relationship between the CMS...and their histology has not been extensively studied"이고 "molecular analysis is typically expensive and slow." Novelty 4가지를 번호로 명시: (1) H&E에서 genomically-determined CMS를 처음 예측, (2) Digital-CMS의 생존 층화가 molecular-CMS와 comparable, (3) patch-level TME 프로파일링으로 "CMS-associated TME patterns are localised rather than uniformly distributed", (4) 조직학·면역 surrogate marker 식별. Discussion은 TCGA에서 AUC가 낮은 이유(CMS 결정법 차이), C2 과할당에 따른 overtreatment 위험, 고소득국 코호트 편중으로 저·중소득국 일반화 한계, 인과성 규명의 어려움을 한계로 든다.

---

## Paper C — NSCLC 실행가능 바이오마커 검증 (validation-focused, 산업체)

이 논문은 나머지 셋과 결이 다르다. **"발견"이 아니라 "검증"**이 목적이며, 임상 배포를 겨냥한 산업체(Imagene) 논문이다. 우리 원고의 검증 챕터·임상적 프레이밍에 가장 유용한 모델.

### Structure
IMRaD. Introduction(임상맥락·가이드라인·실무 gap) → Results(classifier 개발; 독립 test set 검증; 성능지표; subgroup 분석) → Discussion(임상효용·실세계 구현·한계) → Methods(study samples; test cohort; algorithm development; external validation; statistical analysis). 장문·방법 상세.

### Abstract
구조화, 단 **3문장**으로 매우 압축적. (1) 동기(NSCLC 분자분석 의존하나 challenge 존재), (2) 방법/결과("AI classifiers for EGFR, ALK, BRAF and MET...achieved AUCs of 0.87 for EGFR, 0.96 for ALK, 0.88 for BRAF and 0.83 for MET"), (3) 주장(임상 의사결정 지원 잠재력). **AUC 숫자를 초록 본문에 그대로** 박아 리드.

### Figures (6개)
- **Fig 1 = 워크플로 스키매틱**: embedding 추출 → MIL 학습 → Leave-One-Group-Out 검증 → 외부 test 적용 (A 개발, B 검증 2패널).
- **Fig 2 = 성능**: (A) confusion matrix(concordance 요약), (B) 네 유전자 ROC + AUC.
- **Fig 3–6 = 유전자별 성능**(EGFR/ALK/BRAF/MET 각 1그림, 4패널): (A) AI-negative군의 NPV, (B) AI 분류 tier별 양성률, (C) site별 AI score 분포 박스플롯, (D) predictiveness curve(위험 vs score, 95% CI band + threshold line).

**주목: attention overlay·히트맵·조직 이미지 예시가 전혀 없다.** 해석가능성보다 임상 성능·NPV 전달에 집중.

### Tables
**본문 표 딱 1개**. Table 1 = test set characteristics: 두 기관(Sheba n=510, Hoag n=458) 968 WSI의 인구통계·검체유형·기관별 바이오마커 유병률. 전형적인 "코호트 특성 표"를 test cohort에 대해 제시.

### Performance reporting
외부검증(n=968)에서 유전자별 AUC + **NPV·PPA(positive percent agreement) 각각 95% CI**:
- EGFR: AUC 0.87, NPV 98.6% (96.0–99.7), PPA 98.8% (96.4–99.7)
- ALK: AUC 0.96, NPV 99.7% (98.8–100.0), PPA 94.1% (80.3–99.3)
- BRAF: AUC 0.88, NPV 100.0% (99.1–100.0), PPA 100.0% (63.1–100.0)
- MET: AUC 0.83, NPV 99.6% (97.6–100.0), PPA 96.2% (80.4–99.9)

likely-positive class의 PPV도 별도 보고(EGFR 79.3%, ALK 68.8%, MET 50%, BRAF 20%). Subgroup(biopsy vs surgical, primary vs metastatic) 일관성 분석하되 양성 사례 부족을 명시. **Site-disjoint 외부검증**: 개발 8개 site + LOGO CV(3,997 WSI) → 두 개 새 기관(이스라엘·미국) test, pretraining·training에서 test site 배제.

### Rigor
TRIPOD/CLAIM/STARD 명시 없음, 후향적 설계 인정. **데이터·코드 비공개**("Imagene's intellectual property") — 산업체 논문의 전형. 사전등록 없음. Site-disjoint를 LOGO CV + 두 외부기관으로 엄격 구현. 분석가능 종양 부족 검체 제외(n=23, 2.3%) 명시.

### Framing
Intro gap이 **임상 실무 통계**로 매우 구체적: 가이드라인이 검사를 권고하는데도 "40–50% of patients not tested with comprehensive NGS", ">10% receive no testing", 검사 지연이 1차치료 선택 저해. Novelty는 4개 바이오마커로 확장 + foundation model(CanvOI 1.1) + 대규모 multicenter + 실세계 외부검증. Discussion 한계: BRAF/MET 양성 표본 극소, KRAS/RET/ROS1 미포함, intermediate group 큼(EGFR 66.5% 미분류), prospective 임상효용 연구 필요. 위치는 **"complementary tool...not replacement"** — 분자검사를 대체가 아니라 triage/보완으로.

---

## Paper D — Dawood, drug sensitivity from H&E (같은 저널 최근접 경쟁)

### Structure
IMRaD인데 Results를 **10개 안팎의 소제목**으로 가장 잘게 쪼갠다: imputed drug sensitivities from cell lines / analytical pipeline / prediction of drug sensitivity / spatially resolved 표현형 연관 / 약물별 조직패턴 / pathologist-assigned 표현형 연관 / receptor status 연관 / cellular composition 상관 / inflammatory-to-neoplastic 비 상관 / patch-level mitotic count 상관. Methods도 14개 소제목(윤리·데이터·전처리·graph modeling·GNN·학습·패턴식별·세포조성·유사분열·다변량회귀·ablation·batch effect·reporting). 장문 + supplementary 4개 데이터 파일.

### Abstract
비구조화 약 7문장. 동기 문장으로 시작해 **"we demonstrate for the first time that deep learning can link histological patterns...with drug sensitivities inferred from cell lines"**로 novelty를 리드. 성능 숫자를 초록에 넣지 않고 "가능하다"는 개념적 주장으로 감. (Paper C와 정반대 전략.)

### Figures (7개)
- **Fig 1 = 워크플로 스키매틱**(a–d): CCL 회귀학습 → 환자 sensitivity 임퓨테이션 → WSI graph의 GNN 예측 + patch-level score → Tamoxifen/Paclitaxel 예시 motif. **개념 개요도가 Fig 1**.
- **Fig 2 = predictability volcano plot**: 427개 약물의 mean Spearman correlation vs −log10(FDR p), top 10 강조 + 박스플롯.
- **Fig 3 = spatial heatmap + ROI 확대**: pseudo-color contribution map(파랑→빨강) + 확대 patch.
- **Fig 4 = representative patch gallery**: high/low sensitivity exemplar + 세포조성·유사분열·cellularity 막대.
- **Fig 5 = association heatmap**: 예측 약물감수성 vs pathologist 표현형·receptor status의 Kendall's tau 상관행렬(IDC/ILC 분리).
- **Fig 6 = radar plot**: high vs low 감수성 patch의 세포유형 상대수.
- **Fig 7 = 분포 플롯**: INCCR·유사분열수 vs 감수성 violin/box.

### Tables
본문 표 2개 + 광범위 supplementary. Supp Table 1 = 화합물별 high/low 조직패턴·표적유전자·활성class·FDA 승인여부. Supp Table 2 = 유사분열수·INCCR의 결합효과 다변량회귀(FDR 보정). Supp Data 1–3 = 427 화합물 리스트·predictability metric·CV 결과 전체.

### Performance reporting
주지표는 AUROC가 아니라 **Spearman correlation coefficient(SCC)** — 예측 vs 정답 약물감수성. 5-fold CV의 mean SCC + 박스플롯 분포. p값은 FDR 보정("twice the median p-value as conservative estimate"로 폴드 결합). 핵심 수치: "For 186 out of 427 drugs...significantly correlated (p≪0.001)", top 10 약물 mean SCC>0.5. **베이스라인 직접 비교는 없고 대신 다수 ablation**(tumor-only vs all, RetCCL vs ImageNet feature, LOSO batch effect, high-quality vs all WSI). **외부검증 없음** — Discussion에서 "needs a more stringent validation on a large multi-centric independent cohort from an RCT"라 명시.

### Rigor
TRIPOD/CLAIM/STARD 없음. WSI는 TCGA-BRCA(GDC 공개), 코드는 GitHub(engrodawood/HiDS) 공개. 사전등록 없음. 내부 5-fold CV(551 TCGA-BRCA) + **Leave-One-Site-Out CV로 batch effect 평가**(site-disjoint를 ablation으로). 품질필터로 936→551 환자. 외부 코호트 없음.

### Framing
Introduction gap: 정밀의료 동기 → "the applicability of genomics profiling for selecting appropriate drugs remains limited" → 디지털 슬라이드가 "spatial histological profiling"이라는 새 길. Novelty: **"To the best of our knowledge, this is the first study that proposes the prediction of patients' sensitivity to multiple drugs from routine H&E images by training...using drug sensitivity data imputed from CCLs."** Discussion 한계: (1) ground-truth가 gene expression 기반이라 추가검증 필요, (2) cell line은 microenvironment 결여, (3) HER2 inhibitor 예측 저조(SCC 0.18–0.33, H&E의 HER2 예측 한계 탓), (4) RCT 기반 multi-centric 검증 필요. 임상 위치: **routine H&E 스캔 위에 얹혀 "does not require any expensive or time-consuming assays"** — 비용 절감 프레임을 명시적으로 강조(우리 논지와 직결).

---

## 공통 패턴 — npj Precision Oncology 우수 논문의 골격

네 편을 겹쳐 보면, 이 저널의 H&E→분자 논문이 공유하는 modal 골격이 뚜렷하다. 아래는 우리 원고에 그대로 이식할 수 있는 형태로 정리한 것이다.

### 1. Modal section structure — "Results를 잘게 쪼갠 IMRaD"
네 편 모두 **Abstract → Introduction → Results → Discussion → Methods**의 IMRaD를 따르며, 예외 없이 **Results를 6~10개의 서술형 소제목으로 분할**한다(Paper A 3개는 예외적으로 적고, Paper D가 10개로 가장 많음). 소제목은 "Prediction of X from H&E-stained WSIs", "Histological/TME/immunological patterns associated with Y" 같은 **주장형 문장**으로 쓴다. Methods도 소제목으로 구조화(Paper A 4개, Paper D 14개). Introduction이 항상 먼저 오고 Results-first 편집형식(일부 Nature 본지 스타일)은 쓰지 않는다. 본문은 모두 장문(8,000단어급), 성능 상세는 supplementary로 밀어낸다.

### 2. Modal figure set — 5~9개, 4가지 그림 유형의 조합
반복되는 네 유형:
- **(i) 파이프라인/데이터 스키매틱** — 전처리→모델→예측 흐름도. 대개 Fig 1(Paper B, C, D)이지만 **반드시 Fig 1일 필요는 없다**: Paper A는 성능을 Fig 1에 놓고 스키매틱을 Fig 4–5로 뒤로 뺐다. 우리 논문도 "5개 암종 결정지도"의 개념도를 Fig 1으로 삼되, 성능이 헤드라인이면 A처럼 배치를 바꿔도 저널 관행 안이다.
- **(ii) 성능 패널** — 아형/유전자별 ROC 곡선 + AUC, 베이스라인 대비 막대. 네 편 모두 존재(Paper D만 SCC volcano/boxplot로 변형).
- **(iii) 해석가능성 overlay** — Grad-CAM/attention/contribution 히트맵을 H&E와 나란히(Paper A Fig 2, B Fig 5, D Fig 3). **단 Paper C(산업체 검증형)는 overlay를 전혀 넣지 않음** → 해석가능성 그림은 "발견형" 논문의 표지, "검증형"은 생략 가능.
- **(iv) 정량 연관 그림** — 세포조성·핵특징·TME·면역 지표의 박스플롯·히트맵·radar·forest plot(Paper A Fig 3, B Fig 6–9, D Fig 4–7). **surrogate marker를 정량화**해 "왜 되는가"를 보여주는 게 강한 논문의 공통 무기.

우리 원고는 cross-cancer이므로, 5개 암종을 한 패널에 겹치는 **비교 성능 그림**과 cost-substitution 결정경계를 담는 **결정지도 그림**이 (ii)+(i)의 자리를 차지해야 한다.

### 3. Modal table set — 본문 표는 최소, "코호트 특성 + 동등성 검정"이 핵심
네 편 중 셋(A, B, D)은 **본문에 성능표를 두지 않고** 그림 캡션·supplementary로 밀어낸다. 본문 표를 두는 건 검증형 Paper C뿐이고, 그것도 **Table 1 = test cohort 특성표 단 하나**다. 즉 modal은:
- **코호트 특성표**(n·나이·stage·grade·아형 유병률) — 거의 필수, 보통 본문 Table 1 또는 Supp S1.
- **per-endpoint 성능표**(class/유전자별 AUC·CI·민감도·특이도·NPV) — 대개 supplementary.
- **대체 동등성/베이스라인 비교표** — Paper B의 "Digital-CMS vs molecular-CMS C-Index를 DeLong test로 동등성 검정"이 **우리 cost-of-substitution 논지에 가장 직접적인 표 원형**. 우리는 이걸 5개 암종·엔드포인트마다 확장해 "H&E 대체물 vs 분자 원본"의 동등성/열위 여부를 한 표에 넣어야 한다.

### 4. Modal performance-reporting conventions
- **주지표는 AUROC + 95% CI**(A, C; B는 AUC±SD). 값마다 CI를 붙이는 게 규범. Paper D만 회귀문제라 SCC를 쓰지만, 그래도 5-fold 분포와 FDR p를 보고.
- **외부/교차코호트 검증이 강한 논문의 분기점**: A(TCGA+Suzhou 2개 외부), B(3대륙 교차코호트), C(2개 독립기관 + LOGO CV)는 모두 **site-disjoint 외부검증**을 갖췄다. D는 외부검증이 **없고**(LOSO ablation으로 대체) Discussion에서 이를 최대 한계로 자인한다 → **외부검증 유무가 "강한 논문 vs proof-of-concept"를 가르는 가장 큰 단일 요인**.
- **베이스라인**: A·C는 명시적 SOTA 비교(MIL 계열, foundation encoder). B·D는 직접 비교 대신 선행 molecular 표준과의 동등성 또는 ablation으로 대체. 우리 원고는 preregistered law가 핵심이므로 **사전등록된 예측 vs 관측**을 베이스라인처럼 대비시키는 게 차별점.
- **불확실성**: 모두 CV 폴드 표준편차/CI 수준. Bayesian credible interval·epistemic/aleatoric 분해는 아무도 하지 않음 → 우리가 하면 오히려 상향 차별화.
- **임상 지표 이중보고**: 검증형 Paper C는 AUC뿐 아니라 **NPV·PPA·PPV를 tier별로** 보고해 "실제 rule-out에 쓸 수 있는가"를 정량화. cost-of-substitution 논문이라면 이 임상효용 지표(특히 NPV, "H&E-negative면 분자검사 생략 가능한가")가 필수.

### 5. Modal rigor/reporting
- **TRIPOD/CLAIM/STARD를 본문에 명시한 논문은 네 편 중 0편** — 이 저널의 현재 관행이 체크리스트 명시가 아님을 뜻한다. **바로 여기가 우리의 상향 여지**: 우리 원고가 preregistration + TRIPOD/CLAIM 체크리스트를 명시하면 modal을 넘어선다.
- **코드 공개는 학술팀 논문의 규범**(A, B, D 모두 GitHub, A는 Zenodo DOI까지). 산업체 Paper C만 비공개.
- **데이터**: TCGA 등 공개분 + 기관코호트 "요청 시"의 혼합이 표준.
- **사전등록은 네 편 모두 없음** → 우리 원고의 preregistered law가 진짜 차별화 포인트.
- **split**: stratified CV(내부) + site-disjoint 외부(외부)가 modal. multi-center/multi-continent일수록 강함.

### 6. Modal framing/logic
- **Introduction은 항상 "gap"으로 연다**: 분자검사가 (a) 비싸고 느리다(B, D), (b) 저자원 환경에서 접근 불가(A), (c) 가이드라인 권고에도 실제로 40–50%가 검사받지 못한다(C — 실무 통계로 gap을 수치화한 게 가장 설득력 있음). 우리도 "분자검사의 비용/접근성 gap"을 **정량 통계로** 열어야 한다.
- **Novelty는 "first to..."로 못박되 번호로 나열**(B는 4개, D는 명시적 "to the best of our knowledge...first"). 우리는 "first cross-cancer preregistered cost-of-substitution law"로 잡을 수 있다.
- **Discussion 한계 처리 공식**: (1) 성능이 약한 하위군을 먼저 정직하게 인정(A의 POLEmut, C의 BRAF/MET 소표본, D의 HER2), (2) 코호트 편향, (3) 외부/전향 검증 필요, (4) 인과성 미확립. **회피가 아니라 선제적 자인**이 규범.
- **임상 위치를 항상 "대체가 아니라 triage/보완/human-in-the-loop"로 낮춰 잡는다**(A "not a replacement...triage tool", C "complementary tool...not replacement"). 우리 논문의 제목은 "언제 대체 가능한가"이므로, **"무조건 대체"가 아니라 "대체가 정당화되는 조건을 지도로 명시"**하는 이 톤을 반드시 지켜야 저널 정서와 충돌하지 않는다.

### 7. 강한 논문 vs 평범한 논문을 가르는 것 (종합)
1. **외부 site-disjoint 검증의 유무와 강도** — 가장 큰 단일 판별자(A/B/C 있음 = 강함, D 없음 = proof-of-concept 자인).
2. **"왜 되는가"의 정량화** — surrogate marker(세포조성·핵형태·TME·면역)를 그림 여러 개로 파고드는가(A, B, D). 성능표만 있는 논문은 약하다.
3. **대체 동등성의 명시적 통계검정** — Paper B의 DeLong C-Index 동등성이 우리 cost-of-substitution의 방법론적 원형.
4. **임상효용 지표의 이중보고**(NPV/PPA/PPV, Paper C) — "실제로 검사를 생략/triage할 수 있는가"에 답하는가.
5. **한계의 선제적·정직한 자인**과 **낮춰 잡은 임상 위치**(triage/보완).
6. 우리가 modal을 **넘어설** 지점: preregistration + TRIPOD/CLAIM 명시 + 5개 암종 cross-cancer 결정지도 + (선택) 불확실성 정량화 — 이 저널 관행에 아무도 갖추지 않은 것들이라, 갖추면 그대로 상향 차별화가 된다.

---

### 부록 — 4편 핵심 수치 대조 (구조 파악용 — 인용 전 원문 대조 필수)

> **경고 — 수치 검증 상태 (2026-07-18 저녁 원문 대조로 갱신)**: 아래 표와 본문의 정량 수치는 애초 WebFetch **소형 요약 모델**을 거쳐 추출됐고, 그 과정에서 한 곳이 훼손됐다 — Paper A의 p53abn **class-wise** AUROC CI 상한이 "1.003"으로 나왔는데, 이는 불가능한 값(요약모델 훼손)이고 **실제 원문 값은 1.000**이다.
>
> **초록 헤드라인 수치는 요약모델을 거치지 않은 경로(Europe PMC REST 원문 JSON)로 재검증 완료**했다: Paper A macro-AUROC **0.867 (95% CI 0.823–0.911)**, class-wise MSI-H 0.846(0.798–0.894)·NSMP 0.876(0.831–0.921)·p53abn 0.910(0.818–**1.000**) · Paper C AUC **0.87/0.96/0.88/0.83**(EGFR/ALK/BRAF/MET) · Paper B 생존 p값 DSS(TCGA 0.0022, Oslo 0.0495)·DFS(TCGA 0.0495, Oslo 0.0282), n=545 · Paper D는 초록에 성능수치 없음. **이 헤드라인들은 검증됨.**
>
> **아직 미검증 = 본문 전용 수치**(초록에 없는 것): Paper B의 교차코호트 AUC 0.78–0.85, 각 코호트 n, Paper D의 Spearman SCC·"186/427" 등. 이들을 우리 원고에 인용하려면 **원문 PDF 대조 필수**. 이 문서의 1차 용도는 **형식·논리·구조 파악**이다.

| | Paper A (자궁내막) | Paper B (자궁경부) | Paper C (NSCLC) | Paper D (drug sensitivity) |
|---|---|---|---|---|
| 주지표 | AUROC + 95% CI | AUC±SD + 생존 p | AUC + NPV/PPA + 95% CI | Spearman SCC + FDR p |
| 헤드라인 성능 | macro AUROC 0.867 (0.823–0.911) | AUC 0.78–0.85; DSS p=0.0022 | AUC 0.83–0.96 | 186/427 약물 p≪0.001, top10 SCC>0.5 |
| 외부검증 | TCGA n=296 + Suzhou n=36 | 3대륙 교차코호트 n=545 | 2개 독립기관 n=968 + LOGO | 없음 (LOSO ablation) |
| 그림 수 | 5 | 9 | 6 | 7 |
| 본문 표 | 0 (전부 supp) | 0 (전부 supp) | 1 (코호트 특성) | 2 |
| Fig 1 | 성능 ROC | 파이프라인 도식 | 워크플로 도식 | 개념 개요도 |
| 해석가능성 그림 | Grad-CAM | WSI 히트맵 | 없음 | contribution 히트맵 |
| 코드 공개 | O (GitHub+Zenodo) | O (GitHub) | X (독점) | O (GitHub) |
| 체크리스트 명시 | X | X | X | X |
| 사전등록 | X | X | X | X |
| 임상 위치 | H&E-first triage | 비용효과 대안 | complementary tool | assay 불요 저비용 |

위 수치는 4편의 본문/초록을 WebFetch 요약 모델로 추출한 것으로, 인용 전 원문 대조가 필요하다(위 경고 참조). 원문 DOI: A=10.1038/s41698-026-01280-w, B=10.1038/s41698-024-00778-5, C=10.1038/s41698-025-01267-z, D=10.1038/s41698-023-00491-9.

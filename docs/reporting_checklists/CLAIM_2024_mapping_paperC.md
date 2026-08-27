# CLAIM 2024 × Paper C 매핑표

**작성:** braveji (Critic 총괄) · 2026-08-20 · BIOP02-76 조건 4  
**대상 원고:** [`manuscript/DRAFT_paperC_full_ko.md`](../../manuscript/DRAFT_paperC_full_ko.md) (국문 완전 초안 v2, 203줄)  
**체크리스트 원문:** [`CLAIM_2024.md`](CLAIM_2024.md) (CLAIM 2024, 44항목)  
**선행 매핑:** [`TRIPOD_AI_mapping_paperC.md`](TRIPOD_AI_mapping_paperC.md) (TRIPOD+AI 48항목, 2026-08-19)

---

## 배경 & 판정 규칙

**CLAIM 2024 vs TRIPOD+AI의 차이:**
- **TRIPOD+AI**: 진단예측모델 일반(48항목) — 가설검정·회귀·단변량 분석 포함
- **CLAIM 2024**: 의료영상 AI 특화(44항목) — 이미지 획득프로토콜·reference standard 다중정의·annotation variability 강조

**이 매핑의 목적:**
1. TRIPOD 매핑 이후 **CLAIM 특화 항목**에 대한 추가 검증
2. **의료영상 용어 적용** (reference standard=분자검사 금표준, annotators=라벨 출처, acquisition protocol=WSI 수집 표준)
3. **Paper C 특수성** 인식 — 기존 라벨 사용이라 de novo annotation 없음 → 일부 항목(16-18) 해당없음 또는 부분

**판정 기준:**
- ✅ **충족** — 원고에 해당 정보 있음, 위치 지목 가능
- 🟡 **부분** — 있으나 항목이 요구하는 수준에 못 미침 (구체 명세 함께 기재)
- ❌ **미충족** — 원고에 없음
- ➖ **해당없음** — 연구 설계상 성립하지 않음 (사유 명기)

---

## 요약

| 판정 | 수 | 주요 사항 |
|---|---|---|
| ✅ 충족 | **19** | Methods 전처리·평가설계·기한선·검정력이 특히 강함 |
| 🟡 부분 | **11** | Title(확정 대기)·표본수 비율·라벨 정의·데이터 흐름 |
| ❌ 미충족 | **11** | Table 1 · 획득프로토콜 · annotation 문서 · 코드공개 · Funding |
| ➖ 해당없음 | **3** | Trial registration · de-id(공개 데이터) · 동적 재보정 |

**투고 전 반드시 닫아야 할 것 (우선순위)**  
1. **1, 1-AI** — 제목 정식 확정 (AI/ML·예측 대상 명시)
2. **13b** — Table 1 코호트 특성표 (제목·abstract에도 표본수 추가)
3. **14-18** — Reference standard 정의 보강 (금표준 프로토콜·라벨 출처 상세)
4. **23** — 소프트웨어 버전 (이미 CLAUDE.md에 있음, 옮겨 적기)
5. **43-44** — 코드공개 · Funding/Acknowledgments (Modulabs 명시 조건)

---

## 상세 매핑 (44항목)

### Title and Abstract (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 1 | **Title** | ❌ 미충족 | 미확정. 현재 "Paper C — 국문 완전 초안 v1" | 정식 제목 필요. 다음 요소 포함: (1) 예측 대상(분자 표현형), (2) AI/ML 명시, (3) 다암종 사전등록 연구, (4) cost-of-substitution 프레임. 예시: *"Histopathology-based molecular phenotype prediction across five cancer types: a pre-registered cost-of-substitution framework using deep learning"* |
| 1-AI | **Title (AI)** | ❌ 미충족 | 위와 동일 | CLAIM 추가항목. "AI" 또는 "deep learning" 용어 명시 필수 |
| 2 | **Abstract** | 🟡 부분 | L11-13 (목적·방법·결과·결론 완성도 높음) | 보완 필요: (1) 연구설계 명시(후향·다기관 공개코호트), (2) 표본수(5암종 총 ~3,500 슬라이드, ~2,000 환자), (3) 환자 단위 site-disjoint 분할, (4) 사전등록 언급. 현재 결과는 충실하나 방법 절이 간략함 |

### Introduction (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 3 | **Background** | ✅ 충족 | §1 L19-21 (선행연구·gap·임상 역할) | 선행연구(H&E 예측 성숙도)·현재 관행(성능만으로는 부족)·gap("예측된다" ≠ "대체 안전하다")·intended use(cost-of-substitution 프레임·치료 라우팅 오분류 비용) 모두 명확 |
| 4 | **Objectives** | ✅ 충족 | §1 L23-27 (프레임·법칙·기여도) | 주요 가설: "형태학적 상관물이 있는 축만 대체 가능", 다섯 암종 사전등록, 확증·미결·음성 축 구분. 개발/내부/외부 평가 구분(M1/M4/M7) 명확 |

### Methods — Study Design (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 5 | **Study design** | ✅ 충족 | M1·M4·R0 ("후향적") | 후향적 코호트 연구(결과 기존·공개 데이터). 주의: 폐·위·두경부는 sealed-forward(예측 결과 이전 봉인), 대장은 회고적(R47) — 이 구분을 abstract/methods에 명시하는 것이 CLAIM 요구 |
| 6 | **Study goal** | ✅ 충족 | §1 L25-27, §2 R0-R1 | 목표: 분자 축별로 H&E가 분자검사를 cost-of-substitution(오배정률)으로 대체 가능한지 판정. "개발"이 아니라 "기존 모델/라벨을 사용한 관찰 지도 작성" |

### Methods — Data (7항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 7 | **Data sources** | ✅ 충족 | M1 (TCGA 5암종 + Yale M7) | TCGA-BRCA ~1,010 진단슬라이드 · TCGA-LUAD/LUSC ~1,026 · TCGA-COAD ~523 · TCGA-STAD ~439 · TCGA-HNSCC ~468. Yale pCR 코호트 (외부 검증). 공개성: TCGA는 GDC open access, Yale은 cBioPortal 기반 |
| 8 | **Eligibility** | 🟡 부분 | M1 (암묘: "DX 진단 슬라이드·라벨 보유") | 포함: 조직 진단명(DX)·분자 라벨 완전. 제외: 명시 없음 (agents/data에 저장). CLAIM 요구: 명시적 포함/제외 문장 필요. 예: *"포함: 진단 슬라이드(DX) with complete IHC/PAM50/mutation labels. 제외: 결측 라벨, archived 슬라이드, 치료 후 샘플"* |
| 9 | **Preprocessing** | ✅ 충족 | M2 (타일화·마스킹·리사이즈·정규화) | 256×256 픽셀 @20× 배율 · Otsu 배경 분리 · 환자당 최대 5,000 타일 · 224×224 리사이즈 · ImageNet 채널 정규화. 염색정규화 미적용(한계로 명시) — modal 수준의 투명성 |
| 10 | **Subset selection** | ✅ 충족 | M2 (타일 상한) + M4 (site 분리) | 타일 수 제한(환자당 5,000) · site-disjoint holdout(같은 기관 슬라이드 분리). 인력 교육: 파운데이션 모델 전이학습이라 별도 annotator 교육 없음 |
| 11 | **De-identification** | ➖ 해당없음 | M1 (TCGA + Yale) | TCGA는 NIH de-identified (HIPAA 준수). Yale은 IRB 승인 협력 연구. 추가 de-id 불필요 — 공개 데이터 이용 |
| 12 | **Missing data** | ❌ 미충족 | M1 (암묘: agents/data 관리) | 라벨 결측 처리: has_* 필터(agents/data)로 제외되나 원고에 미기재. 보완 필요: *"라벨(IHC/PAM50/mutation) 결측 환자 제외. 암종별 제외 수 [Table 1에 포함]"* |
| 13 | **Acquisition protocol** | 🟡 부분 | M2 ("20× 배율") | 배율·타일 크기 명시. CLAIM 요구: WSI 스캔 표준(스캐너 제조사·모델·슬라이드 준비·염색 프로토콜). 보완: *"TCGA 표준 H&E 슬라이드, 다기관 Aperio/Leica 스캐너, 20×"* 또는 TCGA 획득프로토콜 링크 |

### Methods — Reference Standard (5항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 14 | **Reference standard definition** | 🟡 부분 | §2 R1 표 (축별 라벨), M1 (출처) | 라벨 출처 명시: IHC(금표준)·PAM50(subtypes)·MC3(mutation·cBioPortal) · 조직형(WHO). CLAIM 요구: WHO 진단기준·측정 프로토콜(절편 부위·depth·판독기준). 보완 필요: *"IHC: ER/PR/HER2는 ASCO/CAP 2020 가이드. PAM50: nanoString. Mutation: MC3(공개 annotation)"* |
| 15 | **Reference standard rationale** | ❌ 미충족 | 없음 | CLAIM 13번. 왜 IHC/PAM50/mutation을 선택했는가. 대체 기준(면역조직화학 vs 유전자발현 진단기)과의 비교. 보완 예: *"금표준은 임상적으로 검증된 분자검사다: (1) ER/PR/HER2 IHC는 선택적 치료 기준, (2) PAM50는 예후 아형, (3) EGFR/KRAS는 TKI 선택 기준"* |
| 16 | **Annotators** | ❌ 미충족 | M1 (라벨 출처 암시적) | CLAIM 12번. TCGA 병리학자·자격·교육: 공개 데이터라 원본 진단자 신원 추적 불가. 한계로 명시 필수: *"TCGA 진단은 다기관 공인 병리학자이나 개별 자격·교육 기록 미추적"* |
| 17 | **Annotation procedures** | ❌ 미충족 | 없음 | CLAIM 15번. 라벨 획득 절차(슬라이드 선택·부위·반복성). TCGA 원본 절차 링크 또는 요약 필요: *"TCGA 진단: 유리슬라이드 육안 검경, archived report"* |
| 18 | **Annotation variability** | ❌ 미충족 | M1·M9 (site confounding으로 대체) | CLAIM 18번. Inter-rater reliability(진단 일치도) 미측정. 대신 M9 site/batch 감사에서 site-label 구조화 측정(Cramér's V). 보완: *"이 연구는 기존 진단 라벨 사용(de novo annotation 없음)이므로 rater variability 새로 측정 불가. 대신 site 구조화를 Cramér's V로 감사*" — 이것이 CLAIM이 원래 요구하는 blinding/consistency의 대체 |

### Methods — Data Partitions (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 19 | **Partition assignment** | ✅ 충족 | M4 (site-disjoint holdout) | 분할: site(TSS)를 기준으로 train/test 분리(같은 기관 슬라이드 분산 방지). 비율: 각 암종·축별로 표 R2에 명시. 불균형 처리: shuffle-null 대조·class weight(암시) |
| 20 | **Partition disjointness** | ✅ 충족 | M4 ("같은 제출기관 슬라이드가 학습과 평가에 동시에") | 기관(site) 수준 분리. 환자 수준도 site와 동일하므로 자동 달성. 타일 수준: 같은 환자·같은 site라 leakage 없음(명시 권고) |

### Methods — Testing Data (1항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 21 | **Test set size** | ✅ 충족 | 표 R2 (축별 양성 표본 수) | 사전등록 규칙: 양성 표본 ≥25 필수. 표 R2에 모든 축의 실측값 명시 — 검정력 부족 판정의 객관적 근거. Modal 이상의 투명성 |

### Methods — Model (3항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 22 | **Model architecture** | ✅ 충족 | M3 (CLAM-SB attention MIL) | 입력: 1024-d UNI 임베딩 시퀀스 (타일당 벡터) · 입출력 수: 환자 단위 예측 (이진 분류). 구조: attention MIL(attention layer 256 차원, bag-level 출력). 참고: epoch/seed는 training parameters(M25에서) |
| 23 | **Software** | ❌ 미충족 | 원고 없음; CLAUDE.md 있음 | CLAIM 10-AI-c. 필수 버전: Python 3.13 · PyTorch 2.6.0+cu124 · CUDA 12.4 · Numpy · scikit-learn · CLAM framework version(미명기). 보완: M3에 한 줄 추가 → *"PyTorch 2.6.0, CUDA 12.4, RTX A6000 49GB×3"* |
| 24 | **Initialization** | ✅ 충족 | M2 (UNI v1 1024-d) + M3 (seed 42) | Transfer-learning: 사전학습 파운데이션 모델 UNI v1 사용. 난수 초기화: seed 42 고정. 재현성: M8에서 seed 42·1·2·3·4로 5회 실행·결정론 2회 재확인 |

### Methods — Training (3항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 25 | **Training procedures** | 🟡 부분 | M3 ("40-50 epoch, seed 42") | 제시: epoch 범위·seed. 누락: optimizer(Adam?), learning rate, batch size, gradient clipping, 조기종료 기준, 가중치 초기화. 데이터 증강: 없음(임베딩 입력이라 적용 불가). 보완 필요: CLAM 표준 하이퍼파라미터 명시 또는 github/paper 참조 |
| 26 | **Model selection** | ❌ 미충족 | M3 (CLAM-SB만 사용) | CLAIM 26번. 왜 CLAM-SB를 선택했는가. (1) 다른 MIL 아키텍처 대비 비교? (2) baseline(mean-pooling, max-pooling)과 대비? 현재는 선택 과정 없음. 보완: *"주모델은 CLAM-SB(attention MIL). 단순 baseline(pixel-mean, 조직형만)과 비교해 성능 우위 확인"* (이미 표 R1에 기준선 있음) |
| 27 | **Ensembling** | ➖ 해당없음 | 없음 | Ensemble 없음. R5의 다중 FM(UNI·Virchow2·UNI2-h)은 개별 모델 학습(output 앙상블 아님) — robustness check |

### Methods — Evaluation (7항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 28 | **Performance metrics** | ✅ 충족 | 표 R1 (AUROC·신뢰구간), M5 (오배정률) | 주요 지표: AUROC + 95% CI · confusion matrix (개념적 — Fig2) · misassignment cost(오배정률, 치료 거리 가중). 기준선 3-4종: shuffle-null(무신호), 0.5(무작위), pixel-mean, subtype-only. 기준선 비교 충실 |
| 29 | **Uncertainty** | ✅ 충족 | M4 (부트스트랩 CI), M8 (DeLong), M8-M9 (shuffle-null) | 신뢰구간: 1,000회 부트스트랩 95% CI · 통계 검정: DeLong (두 AUROC 비교). 유의성: CI가 0을 배제하는지로 판정 (formal p-value 없음 — 부트스트랩 대체) |
| 30 | **Robustness** | ✅ 충족 | M8 (다중 FM), M9 (site 감사), R4 (실패 사례), R5 (순서 보존) | 모델 견고성: 3개 FM × 5-seed 우연배제 · site/batch 혼동 감사(Cramér's V·순열검정) · 개발/홀드아웃 일반화 대비(0.963→0.536 사례). Modal 이상 |
| 31 | **Explainability** | ❌ 미충족 | 없음 | Attention weight 시각화·activation map 없음. cost-of-substitution 프레임 자체가 임상적 해석 제공. 보완 옵션: (1) attention weight(타일별 중요도) 예시 (2) SHAP/LIME(feature importance) 불필요 — embedding 해석 불가 |
| 32 | **Internal testing** | ✅ 충족 | M4·표 R1 (site-disjoint holdout) | 같은 데이터소스 내 평가(TCGA 내 train/test). 일반화: 개발셋 vs 홀드아웃 비교(R4 Lauren 0.43 저하 보고 — 정직한 음성) |
| 33 | **External testing** | ✅ 충족 | M7·R6 (Yale pCR 코호트) | 외부 코호트: Yale neoadjuvant trastuzumab 환자. 결과: 항HER2 축이 pCR 층화 실패(AUROC 0.533). 상태: 탐색적(hypothesis_only, 결과 이전 봉인 안 됨) |
| 34 | **Trial registration** | ➖ 해당없음 | 없음 | 임상시험 아님. 사전등록(봉인 문서)은 별도 존재하나 ICMJE 레지스트리 등록 불필요 |

### Results — Data (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 35 | **Inclusion/exclusion numbers** | 🟡 부분 | M1 (슬라이드 수), 예정 (L195 "Flowchart") | 슬라이드 수는 M1에 명시(각 암종 수). 부족: (1) 환자 단위 흐름도(적격→제외→분석), (2) 제외 사유별 수. CLAIM 요구. 보완 예: flow diagram — "TCGA 원본 1,500 진단슬라이드 → 라벨 결측 300 제외 → 1,010 대분석" |
| 36 | **Demographics** | ❌ 미충족 | L195 ("Table 1 예정") | TRIPOD·CLAIM 필수. 연령·성별·인종·TNM·조직형·치료정보를 train/test 분할별·암종별로 비교. 의료영상 공정성: 인구통계 층화 성능(subgroup AUROC, 현재 없음) |

### Results — Model Performance (3항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 37 | **Performance reporting** | ✅ 충족 | 표 R1 (축별 AUROC·신뢰구간·대조), R5 (다중 FM) | 분할별·암종별·변수별 성능 완성. 양성대조(폐 조직형 0.939)·음성 앵커(HER2 0.599)·미결 축(표 R2) 명시. site-disjoint 평가·multi-FM 순서 보존 보고 — modal |
| 38 | **Accuracy estimates** | ✅ 충족 | 표 R1 (AUROC [95% CI]), Fig2 (confusion matrix 개념) | AUROC + 95% 신뢰구간 · confusion matrix 개념(오배정률 비용) · 부트스트랩 95% CI · 불균형 처리(축별 양성 수 표시). ROC 곡선 그래프는 미포함(CLAIM 권고이나 지면 제약) |
| 39 | **Failure analysis** | ✅ 충족 | R3·R4·R6 (음성·실패 사례), R1 각주 (양성대조 한계) | 실패 분석: HER2 0.599(무작위), KRAS 신호 부재(조직형 편중), Lauren 기관 분리 효과, pCR 층화 실패. 혼동 행렬 해석(오배정 패턴). Modal 수준의 정직한 음성 보고 |

### Discussion (2항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 40 | **Limitations** | ✅ 충족 | §3 L147-150 (후향·code호트·site confounding·모델 한계) | 후향적·site-disjoint 단일분할·site/batch 혼동(필요조건만 보유)·염색정규화 미적용·모델 비의존성 부분(폐만 순서 보존)·site 구조화(V=0.378~1.000). Modal 이상의 투명성 |
| 41 | **Implications** | ✅ 충족 | §3 L151-152 (의사결정 틀·전향 검증·임상 권고 보류·자원제한 집중) | 함의 명확: H&E 선별이 모든 축에서 비용을 절감하지 않음 · 형태 특성에 따라 경계가 다름 · 대체 안전성 여부 판정 필수 · 전향 검증 대기. 과장 표현 없음 |

### Other Information (3항목)

| # | 항목 | 판정 | 원고 위치 / 필요 조치 | 비고 |
|---|---|---|---|---|
| 42 | **Full protocol** | 🟡 부분 | L200 ("봉인 사전등록 문서") | 봉인 문서 존재(폐·위·두경부) · 공개 여부(OSF/github)는 미정 → 투고 전 access 설정 필요. 보완: *"사전등록 프로토콜은 [URL] 공개 (또는 출판 후 공개)"* |
| 43 | **Availability** | ❌ 미충족 | 없음 | 코드 공개(github)·모델 가중치·처리 산출물 공개 여부 미기재. FM(UNI)이 비상업 학술 라이선스(CC-BY-NC-ND)이므로 가중치 재배포 가능 여부 확인 필요. 보완: *"코드와 모델은 [github] 공개 (조건: 학술용 only). 처리 코드는 Supplement 제공"* |
| 44 | **Funding** | ❌ 미충족 | 없음 | GPU 제공처 명시 의무(`CLAUDE.md` Infrastructure). 보완 필수: Acknowledgments 절에 *"Computational resources provided by Modulabs (모두의연구소)"* — 자원 제공 조건 |

---

## 요약표

### 섹션별 판정 분포

| 섹션 | 충족 | 부분 | 미충족 | 해당없음 | 합계 |
|---|---|---|---|---|---|
| Title & Abstract | 1 | 1 | 1 | 0 | 3 |
| Introduction | 2 | 0 | 0 | 0 | 2 |
| Methods - Design | 2 | 0 | 0 | 0 | 2 |
| Methods - Data | 4 | 2 | 1 | 1 | 8 |
| Methods - Ref. Std | 0 | 1 | 3 | 0 | 4 |
| Methods - Partitions | 2 | 0 | 0 | 0 | 2 |
| Methods - Test Set | 1 | 0 | 0 | 0 | 1 |
| Methods - Model | 2 | 1 | 1 | 0 | 4 |
| Methods - Training | 1 | 1 | 1 | 1 | 4 |
| Methods - Evaluation | 5 | 0 | 2 | 0 | 7 |
| Results - Data | 0 | 1 | 1 | 0 | 2 |
| Results - Performance | 2 | 1 | 0 | 0 | 3 |
| Discussion | 2 | 0 | 0 | 0 | 2 |
| Other Info | 0 | 1 | 2 | 0 | 3 |
| **합계** | **24** | **8** | **12** | **2** | **44** |

### 강점 (Modal 이상)

- **M2 Preprocessing**: 타일화·배경분리·상한·리사이즈·정규화·염색정규화 미적용 명시 (✅✅)
- **M4 Evaluation**: site-disjoint 분할·기준선 3-4종·부트스트랩·shuffle-null (✅✅)
- **M8-M9 Robustness**: 다중 FM·site 감사·결정론 재실행 (✅)
- **R2 Power analysis**: 축별 양성 표본 수 명시·미결 판정 명확 (✅)
- **R3-R4 Failure analysis**: 음성·실패 사례 상세 (✅)
- **Discussion Limitations**: 후향·site confounding·모델 한계 정직 (✅)

### 약점 & 필수 보완 (투고 전)

**그룹 A: 정식화 필요 (1건)**
- **1, 1-AI** — 제목 정식 확정

**그룹 B: 문서 작성 필요 (4건)**
- **13b (Table 1)** — 코호트 특성 (5암종, 연령·성별·인종·TNM·split)
- **35** — Inclusion/exclusion flow diagram
- **36** — Demographics per partition
- **37-39** — ROC 곡선 그래프 (선택)

**그룹 C: 텍스트 추가 필요 (7건)**
- **2** — Abstract: 표본수·site-disjoint 분할 명시
- **8** — Eligibility: 포함/제외 기준 명시적 문장
- **12** — Missing data: 라벨 결측 제외 규칙
- **13** — Acquisition protocol: WSI 수집 표준(스캐너·염색)
- **14-15** — Reference standard: 금표준 정의·선택 근거
- **16-18** — Annotators·procedures·variability: TCGA 진단 한계 명시 (대체: site 감사)
- **23** — Software: CUDA 12.4, PyTorch 2.6.0, 기타 버전
- **25** — Training: optimizer, LR, batch size (CLAM github 참조)
- **26** — Model selection: CLAM-SB 선택 근거

**그룹 D: 팀 결정 필요 (3건)**
- **42** — Preregistration access: OSF 또는 github 링크
- **43** — Code/model availability: github 공개 범위
- **44** — Funding: Modulabs GPU 제공처 명시 (Acknowledgments)

---

## TRIPOD+AI와의 차이 (이미 매핑됨, 참고용)

| 항목 | TRIPOD+AI (48) | CLAIM (44) | 주요 차이 |
|---|---|---|---|
| Reference Standard | 6a-6b (정의·blind) | 14-18 (정의·금표준·annotation detail) | CLAIM이 annotation 절차·variability 더 상세 |
| Preprocessing | 7a-AI (설명) | 9, 13 (preprocessing + acquisition) | CLAIM이 WSI 획득프로토콜 강조 |
| Data Partition | 8, 8-AI (표본수·effective size) | 19-21 (partition·disjointness·test size) | 용어 약간 다름(대체로 겹침) |
| Evaluation | 16, 16-AI (성능·fairness) | 28-34 (지표·uncertainty·robustness·explainability) | CLAIM이 robustness/explainability 별도 항목화 |
| Bias/Limitation | 19-AI (bias sources) | 40 (limitations) | 대체로 같음 |

**결론: TRIPOD 18~21항(충족)이 CLAIM 대부분을 커버. 추가 확인 필요한 것은 reference standard 정의(14-18)·acquisition protocol(13)·annotator detail(16-18).**

---

## 다음 체크리스트

투고 전 진행 순서:

1. **제목 정식화** (1일차) — 저자진회의
2. **Table 1 작성** (2-3일차) — 류재면
3. **Methods 보강** (2-3일차) — kkkim: 소프트웨어·하이퍼파라미터·WSI 프로토콜
4. **Reference standard 상세** (2일차) — braveji: 금표준 정의·라벨 출처·TCGA 한계
5. **심사자 응답** (last) — 코드공개·Funding·preregistration access

---

*CLAIM 2024 전문 참고: Tejani AS, Klontzas ME, Gatti AA, et al. Checklist for Artificial Intelligence in Medical Imaging (CLAIM): 2024 Update. Radiol Artif Intell. 2024;6(4):e240300. [https://pubs.rsna.org/doi/10.1148/ryai.240300]*

# kaczmarzyk-2026-mako — Abstract

## 서지
- **Title:** Towards interpretable prediction of recurrence risk in breast cancer using pathology foundation models
- **Framework name:** **MAKO** (Mammary Analysis for Knowledge of Outcomes)
- **Authors:** Jakub R. Kaczmarzyk, Sarah C. Van Alsten, Alyssa J. Cozzo, Rajarsi Gupta, Peter K. Koo, Melissa A. Troester, Katherine A. Hoadley, Joel H. Saltz
- **Venue:** npj Digital Medicine 9:149 (2026)
- **DOI:** [10.1038/s41746-025-02334-2](https://doi.org/10.1038/s41746-025-02334-2) · preprint arXiv:2508.12025

## 초록 요약
PAM50 기반 **ROR-P(risk-of-recurrence) 점수** 같은 전사체 assay는 비전이·ER+·HER2- 유방암의
재발 위험 층화를 안내하지만 보편적으로 이용 가능하지 않다. 조직병리는 일상적으로 확보되므로
확장 가능한 대안이 될 수 있다. MAKO는 **12개 pathology foundation model + 2개의 비-병리
baseline**을 attention-based MIL로 H&E WSI에서 ROR-P를 예측하도록 벤치마크했다.

- **데이터:** Carolina Breast Cancer Study(CBCS, ER+/HER2- 학습·검증) → **TCGA-BRCA 외부검증**.
- **핵심 결과:** 여러 FM이 분류·회귀·생존 태스크 전반에서 baseline을 능가.
  - **분류(Low/Med vs High ROR-P):** CONCH가 최고 ROC AUC — CBCS **0.809**, TCGA-BRCA **0.850**.
  - **연속 ROR-P 회귀(Pearson r):** H-optimus-0가 CBCS **r=0.638**; Virchow2도 상위 상관.
  - 교차코호트 일반화는 회귀 축에서 제한적(cross-cohort generalizability 한계 관찰).
- **강조점:** 성능뿐 아니라 **해석가능성(interpretable)** — 형태학적으로 재발 위험 신호를
  귀속하려는 방향.

## 우리 논문에서의 역할
- **BENCHMARK / SCOOP.** 우리가 "공짜 재사용"으로 기대했던 예후/ROR-P 재사용 슬롯을 **우리 데이터(TCGA-BRCA)로 우리 실험(FM × MIL 벤치마크)을 이미 출판** — 이 각도로는 진입 금지.
- **인용 방식:** H&E→marker/prognosis 예측이 이미 **포화된 벤치마크 영역**이라는 근거로 인용("standing FM benchmark[MAKO]"). 우리는 또 하나의 정확도 리더보드를 만들지 않는다.
- **포지셔닝 지지/위협:** 예측 정확도 헤드라인에는 위협이나, **결정-가치(substitutability) 프레임**은 다루지 않음 → 우리 전제("예측은 saturated, 기여는 substitution-cost 결정지도")를 강화.
- **Multi-FM 견고성 참조:** CONCH/H-optimus-0/Virchow2 간 성능 편차는 Paper C의 "치환가능성 법칙의 모델 비의존성" 검증 설계에 baseline 근거로 활용 가능.

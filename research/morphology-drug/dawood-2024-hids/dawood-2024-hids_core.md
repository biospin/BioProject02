# dawood-2024-hids — Core 요약

**Cancer drug sensitivity prediction from routine histology images**
Dawood M, Vu QD, Young LS, Branson K, Jones L, Rajpoot N, Minhas FAA.
*npj Precision Oncology* 8:5 (2024). DOI 10.1038/s41698-023-00491-9.

## 핵심 기여 (Core contribution)
H&E WSI만 입력으로 받아 **427개 CTRP 화합물의 약물 민감도를 end-to-end로 직접 예측**하는 HiDS 파이프라인 제시. 별도 분자 측정(발현, mutation) 없이 routine histology image에서 약물 민감도 신호를 회수할 수 있음을 보임.

## 방법 (Method)
- **입력·전처리:** FFPE H&E WSI → TIAToolbox U-Net으로 viable tissue 분할 → **512×512 patch @ 0.25 µm/px** 추출.
- **백본:** **ImageNet 사전학습 ShuffleNet** (pathology FM 아님) → patch당 1024-d feature.
- **라벨 생성:** cell line 발현 데이터 ↔ CTRP AUC-DRC 사이에 **linear ridge regression** 학습 → TCGA-BRCA 환자 발현에 적용해 환자별 imputed sensitivity 생성 (**단일 route = CTRP imputation**).
- **모델:** **SlideGraph∞** GNN — Delaunay triangulation(≤4000 px)으로 patch graph 구성, EdgeConv layer(L=1,2,3) 메시지 패싱, node score 집계로 WSI-level 예측, **pairwise ranking loss**.

## 데이터셋 (Dataset)
- 초기 1133 WSI / 1084 breast 환자 → 품질 필터 후 **TCGA-BRCA n=551** (427개 약물 imputed score 보유) 최종 분석. 발현 imputation은 936 환자 사용. **Breast-only.**

## 주요 결과 (검증된 수치)
- **427개 중 186개 약물**이 유의(p≪0.001, Spearman SCC 기반).
- 상위 10개 약물 평균 SCC > 0.5.
- HER2 억제제 계열은 약함 (median SCC 0.18–0.33) — H&E에서 HER2 상태 예측이 어려움이 원인.

## 한계 (Limitations)
- **5-fold CV만, 외부/임상 독립 코호트 검증 없음** (TCGA 단독).
- Ground-truth가 cell-line 발현 기반 → epigenetic/proteomic·종양미세환경(TME) 미반영.
- 모든 화합물 계열을 예측하지 못함; HER2 억제제 등 취약.

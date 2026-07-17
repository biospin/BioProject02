# kaczmarzyk-2026-mako — Core 요약

**Towards interpretable prediction of recurrence risk in breast cancer using pathology foundation models**
Kaczmarzyk JR, Van Alsten SC, Cozzo AJ, Gupta R, Koo PK, Troester MA, Hoadley KA, Saltz JH.
*npj Digital Medicine* 9:149 (2026). DOI 10.1038/s41746-025-02334-2. Framework = **MAKO** (Mammary Analysis for Knowledge of Outcomes). Preprint arXiv:2508.12025.

## 핵심 기여 (Core contribution)
H&E WSI만 입력으로 **PAM50 기반 ROR-P(risk-of-recurrence, 재발위험) 점수를 예측**하는 pathology foundation model 벤치마크. **12개 병리 FM + 2개 비-병리 baseline**을 attention-based MIL로 비교하고, CBCS 학습 → **TCGA-BRCA 외부검증**, 그리고 perturbation 기반 **해석가능성(HIPPO)**까지 붙였다. 예측 대상은 **재발위험 점수(연속·범주)이지 ER/PR/HER2/PAM50 아형 분류가 아니다** — 이 구분이 스코프의 핵심.

## 예측 대상 (무엇을 예측하나 — 정확히)
- **ROR-P = PAM50 상관계수 가중합 + 증식(proliferation) 성분**으로 구성된 **재발위험 점수**. 전사체 assay(예: Prosigna/PAM50)가 산출하는 값을 H&E로 대체 예측하려는 시도.
- 연속 ROR-P를 3구간으로 층화: **low <11.76 / intermediate 11.76–<52.94 / high ≥52.94** (컷포인트 [미확인 정밀도 — 단일 WebFetch 요약]).
- 동기: PAM50 기반 재발위험 assay는 비전이·ER+·HER2- 유방암 층화를 안내하나 보편적으로 이용 불가 → 일상적 H&E가 확장 가능한 대안.

## 방법 (Method)
- **백본(12 병리 FM):** CONCH, CTransPath, DiRLV2, Hibou-L, H-optimus-0, Kaiko-L/14, Phikon, Phikon-v2, Prov-GigaPath, UNI, Virchow, Virchow2.
- **baseline(2 비-병리):** ResNet50(ImageNet), ViT-DINOv2(142M 자연이미지 SSL).
- **집계:** **ABMIL** — gated attention, patch embedding → softmax-정규화 attention 가중 집계 → WSI-level 예측.
- **태스크 3종:** (a) 분류 Low/Med vs High ROR-P, (b) 연속 ROR-P 회귀, (c) 생존(재발) 층화 검증.
- **해석가능성:** attention map(저자 스스로 "unreliable"이라 명시) + **HIPPO**(patch 제거/추가로 necessity·sufficiency 검사).

## 데이터셋 (Dataset)
- **학습·내부검증:** Carolina Breast Cancer Study(CBCS) — n=1,339 참가자(1,384 WSI); **ER+/HER2- 서브셋 n=847(883 WSI)**. **10-fold CV.**
- **외부검증:** TCGA-BRCA n=1,050; **ER+/HER2- 서브셋 n=613(613 WSI)** — CBCS 학습모델을 직접 적용.
- 주 분석은 **ER+/HER2- 서브셋**(재발위험 assay의 임상 적용 대상군).

## 주요 결과 (검증된 수치 — PMC12895011)
- **분류(Low/Med vs High), ROC AUC:**
  - CBCS 내부: **CONCH 0.809**(최고); 6개 모델이 ResNet50 대비 유의 개선.
  - TCGA 외부: **CONCH 0.850**(ResNet50 대비 +10.4% 상대개선), H-optimus-0·Virchow2 각 0.840(+9%), CTransPath 0.829.
- **연속 ROR-P 회귀(Pearson r):**
  - CBCS: **H-optimus-0 r=0.638**(최고), ResNet50 0.541; 12개 중 11개 FM이 baseline 유의 초과.
  - TCGA 외부: **다중검정 보정 후 유의 도달 모델 없음** — Virchow2·CTransPath 수치적 개선, H-optimus-0는 오히려 저조. **연속 회귀 축의 교차코호트 일반화는 제한적**.
- **생존:** ABMIL 범주형 모델들이 CBCS 참가자를 전사체 ROR-P와 유사하게 재발 층화; C-index가 transcriptomic assay와 **동등**(p>0.05). CBCS ER+/HER2-에서 847명 중 107명이 10년 내 재발. TCGA는 추적 짧아 전사체 ROR-P 자체도 유의 층화 못 함.
- **해석가능성:** HIPPO로 "종양 영역이 high ROR-P 예측에 necessary하며 대부분 모델에서 sufficient"; 고위험 patch 120개(~2.0 mm²)에서 핵 다형성·유사분열·괴사·침윤성 성장 특징 관찰 [세부 수치 미확인 정밀도].

## 한계 (Limitations)
- **연속 ROR-P 회귀의 외부 일반화 실패**(TCGA에서 유의 모델 0) — 분류·생존은 유지되나 회귀 축은 취약.
- 코호트 특성·슬라이드 준비 차이로 성능 변동; prospective/임상 배포 검증 없음.
- attention map은 신뢰 낮음(저자 인정) → HIPPO로 보완.

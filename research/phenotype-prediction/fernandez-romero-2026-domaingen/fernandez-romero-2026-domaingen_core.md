# fernandez-romero-2026-domaingen — Core 요약

**Domain generalisation challenges in breast cancer molecular classification using foundation models: a cross-cohort exploratory study**
Fernandez-Romero J, Ramos-Berciano P, Perez-Perez M, Benavides D, Robles-Frias A, Garcia-Gutierrez J, Macias-Garcia L.
*Med Biol Eng Comput* 64 (2026). DOI 10.1007/s11517-026-03590-4. **OA**(PMC13269319, PMID 42113320). 소속: Hospital Universitario Virgen de Valme · Universidad de Sevilla.

## 핵심 기여 (Core contribution)
H&E → 유방암 분자분류(PAM50 아형 + ER/PR/HER2 IHC)를 pathology **foundation model(FM) × multiple instance learning(MIL)** 조합으로 예측하되, 선행연구 대부분이 internal validation만 보고한 공백을 지적하고 **외부검증에서의 도메인 일반화 실패(degradation)를 정면으로 계량화**한 exploratory 벤치마크. 신규 예측기가 아니라 **"in-domain 강세 → cross-domain 붕괴"의 진단**이 기여.

## 방법 (Method)
- **설계:** **13개 FM × 3개 MIL 아키텍처** 전조합 벤치마크.
  - MIL 3종(verbatim): **CLAM**(attention-based, multi-branch), **TransMIL**(transformer-based), **DSMIL**(dual-stream).
  - FM 13종: ResNet-50(baseline), CTransPath, RetCCL, CONCH, UNI, Prov-GigaPath, Hibou-B, Hibou-L, H-optimus-0, **Virchow v2**, Phikon v2, Musk, UNI-2. *(PMC 단일 fetch — 목록 자체는 재확인 미실시)*
- **전처리:** tile 크기 **128 µm / ~20×**로 고정("optimal for most FMs"; ≈256×256 px, 픽셀값은 원문 inline graphic). 40× 512×512 추출 후 적응했다는 서술도 있음(FoV 등가).
- **지표(중요):** **ER/PR/HER2 = PR-AUC, PAM50 = macro-F1** — **AUROC 아님**(우리 registry AUROC와 직접 비교 불가).
- **열화 계량:** **RPD(Relative Performance Drop) = (Q_CV − Q_HO) / Q_CV** (CV=내부 교차검증, HO=외부 hold-out).
- **도메인 시프트 요인분석:** 4개 가설 요인(staining variability, class prevalence shift, feature space divergence, morphological separability)을 RPD 회귀 → **staining variability + feature space divergence가 RPD 분산의 80.0% 설명(R²=0.800, R²adj=0.750)**; prevalence shift는 유의하지 않음.

## 데이터셋 (Dataset)
- **내부(CV):** TCGA-BRCA — **1,522 슬라이드 / 1,079 환자**(FFPE).
- **외부(HO):** CPTAC-BRCA — **387 flash-frozen 슬라이드 / 120 환자**(PAM50+IHC 완비). **flash-frozen vs FFPE**가 핵심 도메인 시프트 축의 하나.

## 주요 결과 (검증된 수치)
- **Virchow v2가 전체 최고**(모델 mean ranking **2.00** > Prov-GigaPath 4.13 > H-optimus-0 4.25 ≈ UNI-2 4.25).
- **Virchow v2 내부→외부**(Table 1): ER **0.972→0.916**, PR **0.874→0.862**(견고), **HER2 0.399→0.219**, PAM50 macro-F1 **0.542→0.358**(붕괴).
- **HER2-enriched 아형: 외부 완전 붕괴(RPD=1.000, 전 모델)**. Normal-like·HER2-positive IHC도 심각 열화, 3개 MIL 전반에서 일관.
- 요지: **in-domain 예측은 강하나 코호트·염색·특징공간 시프트에서 무너진다** — 특히 HER2 축.

## 한계 (Limitations)
- **저자 스스로 "exploratory"**로 규정. 외부검증 단일 코호트(CPTAC), flash-frozen이라 조직 준비 축과 코호트 축이 교락.
- 예측 정확도만 보고 — **치료 결정에서의 대체 가치(substitutability)는 다루지 않음**(우리 whitespace).
- ER/PR/HER2 PR-AUC·PAM50 F1 지표라 타 논문 AUROC와 직접 비교 곤란.

## 검증 플래그 (provenance)
- **이중 확인(OpenAlex abstract verbatim + PMC fetch):** 13 FM × 3 MIL, n=1,079/120, Virchow v2 best, HER2-enriched/Normal-like/HER2+ 열화, PR-AUC/macro-F1, R²=0.800, prevalence n.s., mean ranking(2.00 등).
- **PMC 좁은 재확인(quote-demand):** MIL 3종 명칭(CLAM/TransMIL/DSMIL), Virchow HER2 0.399→0.219 · PAM50 0.542→0.358, CPTAC 387 flash-frozen/120, tile 128µm/20×.
- **PMC 단일 fetch(미재확인):** 13-FM 전체 목록, RPD 공식 문자열, ER/PR 내부→외부 소수점(0.972→0.916, 0.874→0.862 — RPD 정합성으로 신뢰).
- **[미확인]** per-model 전체 표(Virchow 외 12모델 내부/외부 값). Data availability 문장 없음(NOT FOUND).

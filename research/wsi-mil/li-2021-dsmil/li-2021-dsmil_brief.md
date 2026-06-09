# DSMIL (Li et al., 2021, CVPR)

DSMIL(Dual-Stream MIL)은 두 개의 스트림을 결합한 WSI 분류 집계자로, 한 스트림은 가장 중요한 인스턴스를 max-pooling으로 식별(critical instance)하고 다른 스트림은 그 critical instance를 기준으로 나머지 타일에 attention을 부여한다. 또한 SSL 대비학습(contrastive)으로 학습한 타일 특징을 활용하는 점이 특징이다. BIOP02 관점에서 DSMIL은 **추가 MIL 비교군**이다. H&E WSI 타일 임베딩 → 슬라이드-레벨 BRCA 표현형(ER/PR/HER2/PAM50) 집계에서 ABMIL(1차 baseline)·CLAM·TransMIL과 나란히 비교해 집계 전략의 robustness를 점검하는 보조 비교자로 쓴다. **DOI는 unverified**(CVPR proceedings — DOI 없음)이므로 CVF proceedings URL로 인용하며 가짜 DOI 날조를 금한다. 우리는 hypothesis-only 시스템이므로 이 집계자는 표현형 예측 중간단계에만 활용한다.

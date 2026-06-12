# Phikon-v2 (Filiot et al., 2024, arXiv)

Phikon-v2는 **공개 데이터만으로** 학습한 ViT-L(1024차원) 병리 foundation model로, biomarker 예측에 특화된 feature extractor다. 핵심 가치는 학습 데이터·코드의 투명성과 재현 가능성으로, 폐쇄 데이터로 학습된 다른 FM과 달리 공개 baseline 역할을 한다. BIOP02 관점에서 Phikon-v2는 **임베딩 백본 후보이자 투명·재현 가능한 개방 baseline**이다. H&E WSI → 임베딩 → BRCA 분자 표현형(ER/PR/HER2/PAM50) 예측 파이프라인의 feature extractor로 쓸 수 있으며, 1024차원이라 UNI와 차원이 같아 교체 비교에 편리하다. biomarker 예측 특화라는 점에서 우리의 표현형 예측 과제와 정렬이 좋다. **DOI는 unverified**(arXiv preprint)이므로 인용 전 CrossRef 재확인이 필요하다. 우리는 약물 구조 입력 없는 hypothesis-only 시스템이므로 이 모델은 형태→표현형 중간단계의 임베딩 추출에만 사용한다.

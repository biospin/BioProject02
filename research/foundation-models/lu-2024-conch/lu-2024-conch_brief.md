# CONCH (Lu et al., 2024, Nature Medicine)

CONCH는 약 117만 개의 image-caption 쌍으로 학습한 **vision-language** 병리 foundation model(512차원)로, 이미지와 텍스트를 공동 임베딩 공간에 정렬해 zero-shot 분류와 텍스트 기반 검색이 가능한 점이 특징이다. BIOP02 관점에서 CONCH는 **임베딩 백본의 대안 후보**다. H&E WSI → 임베딩 → BRCA 분자 표현형(ER/PR/HER2/PAM50) 예측 파이프라인에서 쓸 수 있으나, 리스트에 정리된 대로 순수 feature extractor로는 UNI보다 약한 것으로 평가된다. 대신 vision-language 정렬 덕에 zero-shot·텍스트 검색 같은 보조 기능을 제공한다. CLAUDE.md에서도 CONCH는 2순위 백본(512d)으로 등재돼 있다. 우리는 약물 구조 입력 없는 hypothesis-only 시스템이므로 이 모델은 형태→표현형 중간단계의 임베딩 또는 보조 검색 용도로만 활용하며, DRP 프레이밍과는 무관하다. DOI는 검증됨(10.1038/s41591-024-02856-4).

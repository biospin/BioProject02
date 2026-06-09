# murchan-2024-combat — brief

핵심 기여(core contribution): 전산병리(computational pathology)에서 추출된 deep feature 임베딩에 ComBat 배치보정(batch correction)을 적용하여 제출 기관·스캐너 등 비생물학적 batch effect를 줄이는 방법을 제시한다. The paper adapts **ComBat**, a method originally developed for genomic batch correction, to patch/feature embeddings so that site-driven variance is attenuated while biological signal is preserved.

방법 요지(method): patch 임베딩을 입력으로 받아 ComBat 모델을 **train fold에서만 fit**하고 test에 적용하는 누수-안전 절차를 강조한다(train-only fit). 이로써 임베딩 공간의 medical-center 시그니처를 줄여 다운스트림 분류기의 site bias를 완화한다. DOI는 csv 기준 unverified.

BIOP02 관련성(RIGOR — split/leakage 엄밀성): howard-2021이 보인 site 시그니처는 site-disjoint split만으로 완전히 제거되지 않으므로, ComBat 배치보정은 SpatialPathoAgent의 UNI 임베딩에 적용 가능한 **보완책(complement, not replacement)**이다. 반드시 train fold에서만 fit하여 누수를 피하는 점이 핵심이며, site-stratified split·patient-level split과 함께 엄밀성 스택을 구성한다.

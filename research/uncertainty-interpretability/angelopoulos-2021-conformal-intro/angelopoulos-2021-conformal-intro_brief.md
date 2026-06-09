# angelopoulos-2021-conformal-intro — brief

핵심 기여(core contribution): conformal prediction과 distribution-free 불확실성 정량화(UQ)에 대한 실무 중심 입문서로, 모델·분포 가정 없이 유한표본 coverage를 보장하는 예측 집합을 만드는 방법을 단계별로 설명한다. The tutorial provides accessible recipes for split/conformal prediction, conformalized quantile regression, and risk control, giving distribution-free, finite-sample coverage guarantees that wrap around any black-box predictor.

방법 요지(method): held-out calibration set에서 nonconformity score의 분위수를 정해 원하는 coverage(1−α)를 만족하는 예측 집합을 구성하는 split-conformal 절차와 변형들을 코드 수준으로 안내한다. arXiv preprint(2107.07511) — DOI **unverified**.

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent의 uncertainty-gated hypothesis-only 출력에서 conformal coverage(olsson-2022·wang-2025)를 실제로 구현할 때의 **실무 레퍼런스**다. 저신뢰 표현형 가설을 기각하는 게이트를 모델 재학습 없이 분포-자유 보장과 함께 붙이는 방법을 제공한다.

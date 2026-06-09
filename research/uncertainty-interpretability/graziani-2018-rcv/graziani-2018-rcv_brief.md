# graziani-2018-rcv — brief

핵심 기여(core contribution): 연속형 임상·형태 측정값(예: 핵 크기, 대조도)을 잠재 공간의 방향으로 회귀해 만든 **Regression Concept Vectors(RCV)**로, 병리 분류기의 예측을 사람이 이해 가능한 연속 개념과 양방향으로 연결해 설명한다. The paper extends concept-based explanation (TCAV-style) to continuous-valued histopathology concepts, measuring how human-interpretable morphological measures influence a network's predictions in both directions.

방법 요지(method): activation 공간에서 개념 측정값에 대한 선형 회귀 방향(RCV)을 학습하고, 그 방향에 대한 예측 민감도(Br score)로 개념 기여도를 정량화한다. 유방 병리 등에서 핵 형태 개념의 영향을 해석한다. MICCAI 2018 iMIMIC workshop — DOI **unverified**(arXiv URL로 인용).

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent가 형태→분자상태(ER/PR/HER2/PAM50) 예측의 근거를 제시하려 할 때, RCV는 attention map을 넘어선 **개념 수준 해석**을 제공한다. 단 reading_list 경고대로 이런 해석은 필요조건일 뿐 인과 증명이 아니므로, **탐색적(exploratory) flag**로만 제시해야 한다.

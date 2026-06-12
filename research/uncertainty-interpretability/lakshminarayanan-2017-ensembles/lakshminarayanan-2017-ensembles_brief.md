# lakshminarayanan-2017-ensembles — brief

핵심 기여(core contribution): 베이지안 신경망 없이도 여러 개의 독립적으로 학습한 네트워크(서로 다른 초기화)를 앙상블하여 예측 불확실성을 추정하는 **deep ensembles**를 제안한다. The paper presents a simple, scalable, non-Bayesian baseline whose ensemble disagreement yields well-calibrated uncertainty and strong out-of-distribution detection, often matching or beating Bayesian approximations.

방법 요지(method): proper scoring rule(예: NLL)과 adversarial training을 결합해 각 멤버를 학습하고, 멤버 예측의 평균·분산으로 불확실성을 산출한다. 분류·회귀와 OOD 입력 전반에서 신뢰도 보정 품질을 평가한다. NeurIPS proceedings(DOI unverified — arXiv URL로 인용).

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent의 hypothesis 게이팅은 어떤 불확실성 신호를 cutoff에 쓸지 선택해야 한다. deep ensembles는 MC-dropout(gal-2016)·conformal(olsson-2022)과 나란히 비교되는 **비-Bayesian 불확실성 baseline**으로, 게이팅 신호 ablation의 대조군 역할을 한다.

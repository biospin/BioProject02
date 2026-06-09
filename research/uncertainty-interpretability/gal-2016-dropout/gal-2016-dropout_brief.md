# gal-2016-dropout — brief

핵심 기여(core contribution): 추론 시에도 dropout을 켜고 여러 번 forward pass하는 것이 deep Gaussian process의 근사 베이지안 추론과 동등함을 이론적으로 보이고, 이를 **MC-dropout**으로 명명해 추가 학습 비용 없이 모델 불확실성을 얻는 방법을 제시한다. The paper proves that dropout training approximates Bayesian inference, so test-time dropout sampling (MC-dropout) provides principled, cheap epistemic uncertainty without architectural changes.

방법 요지(method): 학습된 네트워크에서 dropout을 유지한 채 T회 stochastic forward pass를 수행하고, 예측 분포의 평균·분산으로 불확실성을 추정한다. 회귀·분류에서 예측 불확실성 품질을 검증한다. ICML proceedings(DOI unverified — proceedings URL로 인용).

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent가 채택하는 신뢰도 게이팅(dolezal-2022)이 바로 MC-dropout에 기반하므로, 본 논문은 그 **게이팅 신호의 방법론적·이론적 토대**다. 저신뢰 표현형 예측을 보류하는 hypothesis-only 출력의 불확실성 정의를 제공한다.

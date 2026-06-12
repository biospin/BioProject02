# guo-2017-calibration — brief

핵심 기여(core contribution): 현대 심층 신경망이 정확도는 높아도 예측 신뢰도(softmax 확률)가 실제 정답률보다 과대평가되어 **miscalibrated**임을 보이고, 단일 스칼라 파라미터만 학습하는 **temperature scaling**이 가장 단순하면서 효과적인 보정법임을 입증한다. The paper shows modern networks are overconfident and that post-hoc temperature scaling, fit on a held-out validation set, restores calibration without changing predictions.

방법 요지(method): logit을 학습된 온도 T로 나눈 뒤 softmax를 취해 validation NLL을 최소화하는 단일 파라미터 보정. Platt scaling·isotonic regression 등과 비교해 reliability diagram·ECE로 평가하며 temperature scaling이 우수함을 보인다. ICML proceedings(DOI unverified — proceedings URL로 인용).

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent의 불확실성 게이팅은 신뢰도 thresholding에 의존하므로, 보정되지 않은 확률에 cutoff를 적용하면 게이트가 왜곡된다. 본 논문은 **confidence threshold·conformal 적용 전 최소 recalibration 단계**로서 temperature scaling을 정당화한다.

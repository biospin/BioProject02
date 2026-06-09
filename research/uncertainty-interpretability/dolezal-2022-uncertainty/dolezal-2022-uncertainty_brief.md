# dolezal-2022-uncertainty — brief

핵심 기여(core contribution): MC-dropout 기반 불확실성 추정으로 디지털 병리 예측의 신뢰도를 정량화하고, 신뢰도 threshold를 넘는 **high-confidence subset만 보고**함으로써 그 부분집합에서 더 높은 정확도와 외부 일반화를 달성함을 보인다. The paper shows that uncertainty-informed deep learning, with a confidence threshold **calibrated only on training data**, lets the model abstain on low-confidence cases and yields high-confidence predictions that hold up under multi-site external validation.

방법 요지(method): dropout을 추론 시 활성화해 다수 forward pass의 분산으로 불확실성을 추정하고, train에서만 정한 cutoff로 저신뢰 예측을 보류(abstain)한다. 다기관 외부 코호트에서 high-confidence subset의 성능 유지를 검증한다.

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent는 uncertainty-gated hypothesis-only 출력을 표방한다. 본 논문은 (1) 저신뢰 표현형 예측을 보류하는 **게이팅 메커니즘**과 (2) 신뢰도 cutoff를 train에서만 설정하는 누수-안전 절차, (3) **TCGA train → CPTAC test 외부검증 템플릿**을 모두 제공한다. papers.csv에서 RIGOR·UQ 양쪽에 등재되나 폴더는 UQ에만 1회 생성.

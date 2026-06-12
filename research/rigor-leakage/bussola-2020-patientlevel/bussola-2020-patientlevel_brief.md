# bussola-2020-patientlevel — brief

핵심 기여(core contribution): 임상 머신러닝에서 같은 환자에서 유래한 슬라이드/타일을 train과 test에 섞어 넣는 random pooling이 정보 누수(data leakage)를 일으켜 성능 지표를 부풀린다는 점을 체계적으로 보인 연구다. The paper demonstrates that **patient-level data segregation** — assigning all samples from one patient to a single fold — is the minimal requirement for honest evaluation, and that slide/tile-level random splits inflate accuracy by allowing the model to memorize patient-specific signal rather than generalizable morphology.

방법 요지(method): 동일 코호트에서 (a) 환자 단위 분할과 (b) 단순 random 분할을 비교하여, 후자에서 과대평가된 성능이 환자 단위로 엄격히 분리하면 사라짐을 정량적으로 대조한다(medRxiv preprint, DOI는 csv 기준 unverified 아님 — 10.1101 preprint).

BIOP02 관련성(RIGOR — split/leakage 엄밀성): SpatialPathoAgent는 ~150 TCGA-BRCA 슬라이드에서 ER/PR/HER2/PAM50 표현형을 예측하므로 환자당 다수 타일·슬라이드를 사용한다. 본 논문은 patient-level split을 `split_policy_v0`의 잠금 요건으로 정당화하는 1차 근거이며, site-stratified split(howard-2021)과 함께 누수 방어축의 토대를 이룬다.

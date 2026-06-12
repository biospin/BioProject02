# Lens: Academic — Olsson 2022 Conformal Prediction

## 학문적 기여 / Contribution
**KR.** 핵심 신규성은 알고리즘이 아니라 **임상 병리에 conformal prediction을 처음으로 진지하게 실증**한 점이다. CP 이론(Vovk)·Mondrian ICP는 기존 도구지만, 디지털 병리의 다단계(타일→슬라이드) 파이프라인에 6개 외부/전향 테스트셋으로 *coverage 보장이 실제로 유지되는지*를 보였다.
**EN.** The novelty is empirical, not algorithmic: a rigorous demonstration that distribution-free, finite-sample CP guarantees hold across a real multi-stage digital-pathology pipeline and *degrade gracefully* (more abstentions) under domain shift. CP/Mondrian-ICP themselves are prior art (Vovk; Shafer & Vovk).

## 강점 / Strengths
- **분포-무관 보장.** softmax temperature(Guo 2017)나 MC-dropout(Gal 2016)과 달리, CP는 *유한표본*에서 사전 지정한 오류율 ε를 분포 가정 없이 보장. 검증 가능한 약속(verifiable promise).
- **모델-불가지론.** 베이스 분류기를 재학습하지 않고 calibration set만으로 사후 부착 — 우리의 frozen FM(UNI) + phenotype head에 그대로 적용 가능.
- **분포 이동 감지가 부수적으로 따라옴.** 외부 scanner에서 빈/큰 prediction set이 늘어 OOD 경보 역할(Test set 6: 80% flagged).

## 한계·비판 / Limitations & critique
- **Marginal vs conditional coverage.** 보장은 평균적(marginal). HER2-E 같은 소수 subgroup에서의 class-conditional validity는 Mondrian이 부분적으로만 해결 — calibration 표본이 작은 희귀 클래스에서 보장이 흔들릴 수 있음. 우리 프로젝트의 직접적 위험.
- **Exchangeability 가정.** train↔test가 교환 가능해야 보장 성립. TCGA→CPTAC 같은 cross-dataset에서는 깨지며, 이때 CP는 *틀린 보장*이 아니라 *기권 폭증*으로 나타남(완화책: Mondrian/weighted CP, conformal under covariate shift).
- **단순 nonconformity measure.** 저자도 인정: `1−p`는 단순하며 더 정교한 measure가 더 좁은 prediction set을 낼 수 있음.
- **전향 임상 검증 부재.** 실제 워크플로우 의사결정 영향은 미평가.

## 인접 문헌 / Adjacent literature
- **dolezal-2022-uncertainty** — H&E FM 불확실성(thresholded confidence)으로 abstention; CP의 보장이 없는 대안. 비교축.
- **guo-2017-calibration** — temperature scaling. CP 전처리로 결합하면 calibrated prob이 더 나은 nonconformity score 제공.
- **wang-2025-truecam (preprint)** — FM + conformal의 최신 청사진; Olsson은 그 임상-병리 선조. 우리 npj 제출의 직접 lineage.

**판정.** 인용 시 "병리-네이티브, 외부 검증된 conformal abstention의 1차 근거"로 자리매김 — 방법 자체의 신규성보다 *보장의 실증*을 강조해야 과대주장(DRP-framing) 회피.

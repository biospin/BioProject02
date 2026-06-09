# dawood-2024-hids — Lens: Academic

## Novelty 평가
H&E WSI에서 **약물 민감도를 직접** 예측한 초기 end-to-end 연구 중 하나. 진짜 신규성은 "약물 라벨을 cell-line CTRP imputation으로 만들어 image 모델 학습에 투입"한 라벨링 트릭이며, 모델(SlideGraph∞)·백본(ShuffleNet)은 기존 자산 재사용. 따라서 방법론적 신규성은 **중간**, 응용·규모 측면 기여가 큼.

## Rigor 평가
- 강점: 427 약물 전수 스크리닝, ranking-loss 약지도 학습, LOSO·tumor-only ablation, 수용체 상태(ER/PR/HER2) 연관 분석.
- 약점: **5-fold CV만 수행, 외부·임상 독립 코호트 검증 전무**(저자 본인도 RCT급 multi-centric 검증 필요 인정). 라벨 ground-truth가 cell-line 발현 imputation이라 순환적 신뢰도 한계.

## BIOP02와의 중복 (굵게 = 직접 충돌)
- **같은 저널 (npj Precision Oncology)**
- **같은 task family: H&E WSI → 약물 민감도**
- **같은 코호트: TCGA-BRCA, breast-only**
- **같은 transfer 컨셉: cell-line(CTRP) → 환자 약물 민감도**

## 차별점 (우리의 방어선)
- 우리는 **해석 가능한 phenotype 중간층**(ER/PR/HER2/PAM50)을 거치는 vs 이들의 **end-to-end 블랙박스**.
- **multi-route 수렴**(DepMap PRISM + GDSC + CTRP) vs **단일 route(CTRP imputation only)**.
- **외부 CPTAC 검증** vs **TCGA 단독·외부검증 없음**.
- **Pathology FM 백본(UNI/CONCH 등)** vs **ImageNet ShuffleNet**.
- **anti-DRP·hypothesis-only governance + Scientific Critic** vs 직접 sensitivity 점수 산출.

## 인용 포인트
- 본 논문을 "H&E→drug sensitivity end-to-end baseline"으로 인용하고, 우리가 Exp3에서 재현·비교.
- 외부검증 부재·단일 route·블랙box를 우리 설계 동기(motivation)로 인용.

## 검증 플래그
- 모든 수치 WebFetch(PMC10771481)로 확인: n=551, 427 화합물, 186 유의, 512px@0.25µm, ShuffleNet, SlideGraph∞, 5-fold CV. **외부/임상 독립 코호트 = 없음(확인됨)**. 분자 구조/SMILES 입력 = 없음(확인됨, end-to-end).

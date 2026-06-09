# tafavvoghi-2024-jpi — Lens: Academic

## Novelty 평가
H&E→4-class 분자 아형 분류를 WSI 스케일·다중 코호트에서 수행한 견고한 응용 연구. 진짜 신규성은 "tumor-tile segmentation → OvR CNN의 **threshold-초과 tile count**를 feature로 XGBoost 집계"라는 2단계 엔지니어링이며, 모델(Inception_V3/ResNet-18/XGBoost)은 모두 기성 자산. 따라서 방법론적 신규성은 **중간**, 과제·코호트 정합성과 재현 가능한 public code가 임팩트의 핵심.

## Rigor 평가
- 강점: 1,433 WSI 대규모, tumor segmentation F1 0.954, per-class F1 보고, **public PyTorch code(GPLv3)**로 재현성 확보.
- 약점: **site/scanner confound 통제 없음**, **외부 독립 test split 없음**(코호트를 섞어 평가) → generalization 과대평가 위험. HER2-E F1 0.545로 한 클래스가 명백히 취약.

## BIOP02와의 중복 (굵게 = 직접 충돌 = scoop overlap)
- **같은 task: H&E WSI → 4-class 분자 아형 (LumA/LumB/HER2-E/Basal)**
- **같은 코호트: TCGA-BRCA + CPTAC-BRCA, breast-only**
- **public runnable code 존재 (uit-hdl/BC_MolSubtyping)**
- **published macro-F1 0.727이 곧 우리가 넘어야 할 SOTA 막대**

## 차별점 (우리의 방어선)
- **Foundation-model 임베딩(UNI/CONCH) + attention-MIL** vs 그들의 **per-tile CNN + tile-count XGBoost**.
- **Site-stratified(harder) split**로 confound 통제 vs **통제 없는 cohort-mix**.
- **CPTAC를 진짜 외부 test로 hold-out** vs **외부 test split 없음**.
- **Uncertainty-aware 거부**: HER2-E F1=0.545 ceiling을 인정하고, 저신뢰 HER2-E hypothesis는 reject (그들은 그대로 출력).
- **하류 therapeutic hypothesis (DepMap/GDSC)** vs **진단 분류에서 종료**.

## 0.727 = the bar (positioning)
이 논문의 0.727은 **약한 내부 baseline이 아니라 published SOTA 기준선**이다. 우리는 (1) 그들의 public code를 그대로 돌려 baseline 재현하고, (2) UNI+attention-MIL이 **더 어려운 site-stratified split**에서 0.727을 넘으면 그것이 *공정한 승리(fair win)*임을 명시한다.

## 검증 플래그
모든 수치 WebFetch(PMC11667687) 확인: macro-F1 0.727, per-class F1(LumA 0.922/LumB 0.742/HER2 0.545/BL 0.698), 1,433 WSI(980+382+71), 512px@20×, Inception_V3 seg F1 0.954, ResNet-18 OvR + XGBoost tile-count. **site confound 통제 없음 / 외부 test split 없음 / therapeutics 없음 = 모두 확인됨.**

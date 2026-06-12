# tafavvoghi-2024-jpi — Methodology Brief (baseline 재현·비교 가이드)

우리가 **Exp1(baseline 재현)**과 **Exp2(site-stratified 공정 비교)**에서 직접 돌릴 방법. 목표: published **macro-F1 0.727**을 *우리 조건*에서 넘는다.

## A. 원 파이프라인 (재현 대상)
```
WSI ─tile 512×512 @20×─▶ [Step1] Inception_V3 tumor seg (F1 0.954)
                                  │ (tumor tiles only)
                                  ▼
        4× One-vs-Rest ResNet-18 이진 CNN (LumA/LumB/HER2-E/Basal)
                                  │  per-subtype threshold 초과 tile COUNT = feature
                                  ▼
                          XGBoost meta-classifier ─▶ WSI-level 4-class
```
- 입력: 512×512 tile @20× (HER2 클래스만 64px overlap).
- feature: OvR CNN의 **threshold-초과 tile count** (분자 측정 아님, 형태학 count).
- 집계: **XGBoost** (foundation model 아님).
- 원논문 검증: **외부 test split 없음, site/scanner confound 통제 없음** (cohort mix).

## B. BIOP02 Exp 연계

### Exp1 — Baseline 재현 (their condition)
- `uit-hdl/BC_MolSubtyping` public code를 격리 env에서 실행, TCGA-BRCA(980)+CPTAC-BRCA(382)로 그들의 cohort-mix 설정 재현 → **0.727이 재현되는지** 확인 (sanity check). 결과는 낙관적 상한으로 간주.

### Exp2 — Site-stratified 공정 비교 (our condition)
- **동일 코드 + 동일 라벨**을 **patient-level + site-stratified split**(TCGA site/scanner를 train↔test 분리, `split_policy_v0`)에서 재측정 → baseline의 *공정* macro-F1 산출.
- 같은 hard split에서 **우리 UNI(또는 CONCH) 임베딩 + attention-MIL**을 학습/평가.
- **Fair win 정의:** 우리 모델이 *동일 harder split*에서 baseline macro-F1을 통계적으로 상회하면 승리로 인정. (그들의 쉬운 0.727이 아니라, 동일 조건 재측정치를 막대로 사용.)

### HER2-E ceiling 대응
- 원논문 HER2-E F1 = **0.545**가 형태학 상한. 우리는 per-class **uncertainty(예: MC-dropout/entropy)** 를 산출해, 저신뢰 HER2-E 예측은 **hypothesis 단계에서 reject** → 하류 therapeutic hypothesis 오염 차단 (Critic checklist #7 claim-level, #5 plausibility).

### 외부검증 확장
- 두 Exp 모두 **CPTAC-BRCA를 진짜 hold-out 외부 test**로 사용 — 원논문이 결여한 generalization 증거 확보 (cross-dataset = Critic #4).

## C. 거버넌스
산출은 진단 아형 → 이후 **hypothesis-only** therapeutic 단계로만 연결. "drug response prediction"/"personalized therapy" 표현 금지, baseline·우리 결과 모두 **Critic pass 후** `#biop02-experiments` 공유, `metrics.json`에 `commit_hash` 기록.

## 검증 플래그
512px@20×, Inception_V3 seg F1 0.954, ResNet-18 OvR, tile-count→XGBoost, macro-F1 0.727(LumA 0.922/LumB 0.742/HER2 0.545/BL 0.698), 1,433 WSI(980+382+71) = PMC11667687 확인. **외부 test split·site confound 통제 없음 = 확인됨** (우리 Exp2의 차별 근거).

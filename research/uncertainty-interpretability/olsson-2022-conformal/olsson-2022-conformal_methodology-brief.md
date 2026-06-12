# Methodology Brief — Conformal Abstention for Phenotype→Hypothesis Gating

목적: Olsson 2022의 Mondrian ICP 레시피를 BIOP02의 **H&E→BRCA phenotype→therapeutic hypothesis** 게이트에 이식. "확신할 때만 hypothesis 발화", 특히 HER2-E F1 천장 회피.

## 레시피 / Recipe (5단계)
1. **Calibration split.** 환자-수준으로 분리(leakage 금지). Olsson은 train의 10%(837 biopsies)를 calibration으로 떼어냄. 우리: ER/PR/HER2/PAM50 각 클래스가 calibration에 충분히 포함되도록 **class-balanced** 추출.
2. **Calibrate base probs.** Phenotype head softmax에 **temperature scaling**(Guo 2017)을 calibration set에서 적합 → over/under-confidence 보정. (선택) MC-dropout(Gal 2016)으로 epistemic 신호 추가.
3. **Nonconformity score.** Olsson과 동일하게 `s = 1 − p̂(class)`. (개선 여지: APS/RAPS가 더 좁은 set 산출.)
4. **Mondrian(class-conditional) p-value.** 각 클래스 c의 calibration score 분포에서 새 샘플 score의 순위 → p-value. 클래스별로 따로 계산해야 소수 클래스(HER2-E)에서 conditional validity 근접.
5. **Prediction set @ ε.** p-value > ε인 라벨만 set에 포함. **|set|==1 → emit hypothesis; |set|≠1(0 또는 다중) → abstain → Critic rejection.**

## 게이트 결정 규칙 / Gating rule
```
if len(pred_set) == 1:   claim_level = "hypothesis_only"; critic_status = "candidate"  # 발화
elif len(pred_set) == 0:  critic_status = "reject:OOD"          # 분포 밖 → 기권
else:                     critic_status = "reject:ambiguous"    # 다중 라벨 → 기권
```
ε는 운영 임계: Olsson 암 검출은 ε=0.001(99.9%), ISUP은 0.33/0.20(67/80%). 우리: phenotype별 ε를 검증셋의 flagged-rate 대비 오류율 곡선으로 튜닝.

## 기대 거동 / Expected behavior (Olsson 근거)
- 보장: 동일-분포에서 오류율 ≤ ε가 **유한표본·분포-무관**으로 성립(exchangeability 가정).
- 트레이드오프: Olsson 암 검출 — 오류 2%→0.1% 대가로 22% abstain. HER2-E도 *틀린 hypothesis 감소 ↔ 기권 증가*로 전환될 것.
- 분포 이동(TCGA→CPTAC): exchangeability 붕괴 → empty/multi set 급증이 **자동 OOD 경보**. weighted/Mondrian CP로 covariate shift 부분 완화.

## Critic 연동 / Critic hooks
- checklist #7 (claim-level): conformal set이 단일일 때만 `hypothesis_only` 허용 — 자동 게이트.
- checklist #2 (baseline): random·subtype-only 대비 *coverage 보장이 있는* abstention의 효용 비교.
- checklist #4 (cross-dataset): flagged-rate가 PRISM/GDSC, TCGA/CPTAC 간 일관되게 상승하는지로 drift 정량화.
- anti-self-reference: ε·calibration은 owner가 사전 고정, Critic은 임계를 *스스로 설정 금지* — Olsson의 사전 지정 ε 관행과 정합.

## 기록 / Logging
`metrics.json`에 `conformal: {epsilon, calibration_set_hash, n_calibration, flagged_rate, empty_rate, multi_rate, per_class_coverage}` 추가 권장. calibration 재보정 시점(scanner/cohort 변경)을 commit에 명시.

## 주의 / Caveats
- Marginal 보장 ≠ subgroup 보장. HER2-E conditional validity는 Mondrian + 충분한 class 표본으로만 근접.
- Calibration이 stale하면 보장 무효 → CPTAC 전환 시 재보정 필수.
- `1−p` 단순 score는 baseline; APS/RAPS 업그레이드는 추후 실험으로.

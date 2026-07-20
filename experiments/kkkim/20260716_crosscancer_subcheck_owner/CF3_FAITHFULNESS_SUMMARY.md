# Critic #3 — cross-cancer sealed-forward attention-faithfulness (kkkim, owner)

> braveji 재판정 open item(폐/위/두경부 특징제거 counterfactual 부재) 대응. 2026-07-16.
> claim_level=hypothesis_only, critic_status=pending. owner 실행 = braveji #3 증거(Critic 서명 아님).
> 방법: `counterfactual_attention_crosscancer.py` — train_eval 재현 → top-attention k% 타일 제거 vs 무작위 k% 제거 → held-out 환자 AUC 낙폭 비교. cuda:1, seed=42.

## 재현 게이트 (advisor 요구: counterfactual 전 저장 AUC 재현 확인)
**10/10 endpoint 모두 재현 Δ=0.0000** (재학습 모델 = 봉인 모델, 결정론적). counterfactual이 방어 대상 그 모델에 정확히 부착됨.

## Faithfulness 결과 (top-att 제거 낙폭 > 무작위 제거 낙폭 = faithful)

| 암종 | endpoint | AUC | 10% 제거 | 20% 제거 | 판정 |
|---|---|---|---|---|---|
| LUNG | histology_lusc | 0.939 | faithful (top −0.032 / rnd ~0) | faithful (−0.084 / ~0) | ✅ |
| LUNG | egfr_activating | 0.852 | faithful (−0.036 / ~0) | faithful (−0.022 / ~0) | ✅ |
| LUNG | kras_g12c | 0.681 | — | — | N/A (低AUC=H&E-blind) |
| GASTRIC | msi_h | 0.860 | faithful (−0.010 / 0) | faithful (−0.036 / −0.006) | ✅ |
| GASTRIC | ebv | 0.948 | faithful (−0.061 / −0.007) | faithful (−0.082 / −0.002) | ✅ |
| GASTRIC | lauren_diffuse | 0.536 | — | — | N/A |
| GASTRIC | erbb2_amp | 0.644 | — | — | N/A |
| HEADNECK | **hpv_pos** | 0.959 | faithful (−0.042 / −0.001) | **faithful (−0.107 / −0.001)** | ✅ (핵심 CONFIRM) |
| HEADNECK | grade_high | 0.815 | 노이즈수준 (−0.004 / 0) | faithful (−0.017 / −0.0004) | ✅(20%) |
| HEADNECK | egfr_amp | 0.604 | — | — | N/A |

## 해석
- **모든 高-AUC/CONFIRM endpoint(histology 양성대조·egfr_activating·msi_h·ebv·hpv_pos)가 attention-faithful**: 상위 attention 타일 제거 시 AUC가 무작위 제거보다 훨씬 크게 하락 → 예측이 **모델이 주목한 형태(morphology)에 실제로 의존**.
- **低-AUC H&E-blind endpoint는 N/A**: 신호가 없어 faithfulness 검정 대상 아님(fail 아님). BRCA HER2 패턴과 정합.
- 핵심 주장: **"H&E가 진짜 예측하는 곳에선, 예측이 attended morphology에 의존한다."** shuffle-null(라벨순열)이 못 보이던 '특징 제거' 축을 채움.

## 산출
- 원본 JSON `counterfactual_faithfulness.json` · 스크립트 `../../crosscancer/counterfactual_attention_crosscancer.py` · 로그 `../../crosscancer/CF3_HEARTBEAT.log`.
- Owner≠Reviewer: braveji가 #3 caution→(보완 인정 시) 상향 판단. jhans/sjpark sub-check 무관(이건 형태-신호 faithfulness).

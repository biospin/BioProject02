# BIOP02-124 #3 operating-point — 1차 해석 (threshold 0.5)

> MUST/게재 blocker. AUROC만으론 '대체 가능/불가'를 못 정한다 → 실제 결정 지표(sens/spec/PPV/NPV + 유병률 민감도)로 재계산. 전부 기존 실측 예측(신규 데이터 0). claim_level: hypothesis_only. 산출=`operating_point_results.json`, 코드=`compute_operating_point.py`.

## 왜 이 분석이 필요한가
AUROC는 순위 지표라 "임상에서 대체가 안전한가"를 답하지 못한다. 같은 AUROC라도 임계에서의 PPV/NPV·rule-in/rule-out 능력은 축마다 다르다. 아래는 **threshold 0.5 고정** 관측점(rule-in/rule-out 임계 재조정·calibration·decision-curve는 후속).

## 핵심 결과 (전부 실측)

**음성 결론이 operating-point로 방어된다 (핵심):**
- **BRCA HER2**: sens **0.000** / spec 1.000 — 임계 0.5에서 HER2+ 환자를 **한 명도 못 짚는다**. NPV 0.863은 신호가 아니라 음성 기저율(86% HER2−)일 뿐. → "HER2 대체 불가"가 AUROC 0.599를 넘어 결정 지표에서도 성립.
- **위 ERBB2**(sens 0.000)·**두경부 grade_high**(0.000)·**폐 KRAS-G12C**(0.000) — 동일. 임계 0.5에서 양성 축을 rule-in 못 함 = 정직한 음성.

**대체 가능 축도 뉘앙스가 드러난다:**
- **두경부 HPV**: PPV **0.929**·spec 0.991(rule-**in** 강 — HPV+ 예측은 신뢰)이나 sens **0.500**(rule-out 약 — 음성 예측이 HPV를 배제 못 함). AUROC 0.959가 가리던 임상 구분.
- **폐 조직형 LUSC**: sens 0.882·spec 0.873·PPV 0.900·NPV 0.851 — 양방향 균형(형태 그 자체라 예상).
- **폐 EGFR**: NPV **0.986**(H&E 음성이 EGFR 거의 배제, rule-out 강)이나 PPV 0.226(rule-in 약). **위 EBV**: NPV 0.974.
- **위 MSI-H**: PPV 0.667·NPV 0.884.

## 판정·규율
- **rare-positive 축(HER2·ERBB2·KRAS·grade)**은 임계 0.5에서 sens 0 → rule-in 하려면 **임계를 낮춰야**(사전정의 또는 nested 선택). 이건 #3의 rule-in/rule-out threshold 재조정에서 다룬다(다음). 0.5 결과를 "무능"으로 과대해석하지 않는다 — 관측점 하나다.
- PPV/NPV는 관측 유병률 기준이며, `prevalence_sensitivity`(Bayes 재투영, 유병률 5/10/20/30%)를 JSON에 병기했다 — 자원제한·저유병 세팅에서 rule-out NPV가 유지되는지 판단용.
- claim_level: hypothesis_only. cost-of-substitution 프레임(BIOP02-91)과 정합: 음성 축의 낮은 sens = 오라우팅 비용의 결정-지표 근거.

## 남은 #3 (후속)
- rule-in/rule-out threshold 사전정의(또는 nested CV 선택) 후 재산출.
- calibration(reliability curve·ECE), decision-curve/net-benefit.
- missed-positive cost × prevalence 민감도 서술(표는 JSON에 산출됨).
- 리뷰: braveji(operating-point↔cost 정합·게이트). 서사 반영: 주저자(이건규).

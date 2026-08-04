# BIOP02-124 #3 — operating-point 해석 노트 (게재 blocker 대응)

> 담당 kkkim · 리뷰 braveji. 자동생성 수치는 [OPERATING_POINT_RESULTS.md](OPERATING_POINT_RESULTS.md)(스크립트 재실행으로 재현), 이 파일은 그 위의 임상 해석이다.
> claim_level: **hypothesis_only** · 후향적. operating-point는 임상 사용가능성의 *상한 탐색*이지 검증이 아니다.

## 왜 이 분석이 게재 blocker였나

리뷰어 지적(#3): AUROC만으로는 "H&E가 분자검사를 임상적으로 대체해도 되는가"에 답할 수 없다.
같은 AUROC라도 **어느 임계에서 얼마나 놓치고(FN) 얼마나 헛짚는가(FP)**, 그리고 **유병률이 바뀌면 PPV/NPV가 어떻게 무너지는가**가 대체 안전성을 가른다. 이 분석은 cost-of-substitution 프레임을 환자단위 지표(민감도·특이도·PPV·NPV·net benefit·유병률 민감도)로 조작화한다.

## 검정력 경계(먼저)

powered(n_pos≥25)만 확증적으로 읽는다: **brca_er·brca_pr·brca_her2·brca_pam50_HER2아형·lauren_diffuse·hpv_pos·grade_high·histology_lusc**. 나머지(braf_v600e·msi_h·erbb2_amp·ebv·egfr_amp·egfr_activating·kras_g12c)는 exploratory — 지점 추정이 5~15 양성에 얹혀 있어 임계 하나로 크게 흔들린다. 표에 ⚠️로 남기고 본문 승격하지 않는다.

## 핵심 판독 (powered)

1. **두경부 HPV — 유일한 검정력 있는 봉인 확증, operating-point에서도 rule-in 우수.** AUROC 0.959. threshold=0.5에서 특이도 0.991·PPV 0.929로 **헛짚음이 거의 없다**(rule-in). 특이도≥0.90을 지키는 임계(0.04)에서 민감도 0.885까지 확보돼, net benefit이 treat-all/none을 모두 상회. → HPV는 형태에 또렷이 보이는 저비용 축이라는 결정지도 판정을 임상 지표가 뒷받침한다.

2. **폐 LUSC 조직형(양성대조) — 균형 잡힌 operating-point.** AUROC 0.939, 민감도 0.882·특이도 0.873·PPV 0.900. decision curve에서 모델 우위. 양성대조가 지표 수준에서도 건강함을 재확인.

3. **위 Lauren diffuse — operating-point에서 음성이 더 분명해진다(정직한 음성).** AUROC 0.536에 더해 **ECE 0.356(최악의 보정)**, 그리고 pt=0.2 net benefit이 treat-all보다 **낮다**(0.254 < 0.418). 즉 이 축은 "예측이 약하다"를 넘어 **의사결정에 쓰면 손해**다 — 분자검사 필수 영역을 비용으로 증명하는 핵심 사례.

4. **유방 HER2(대체 불가 앵커) — 임계 0.5에서 아무도 양성으로 부르지 못한다.** 이진 HER2 AUROC 0.530, PAM50 HER2 아형 0.684이지만 둘 다 threshold=0.5 민감도 0.000(양성 확률이 임계를 넘지 못함). Youden/rule-in 임계를 낮춰도 특이도를 얻는 대가로 민감도가 무너진다. → H&E-예측 HER2로 항HER2 라우팅을 정하면 실제 HER2+ 환자를 놓친다는 결정지도·Yale pCR(0.533) 음성과 일관.

5. **유방 ER/PR — 대체가 아니라 분류(triage) 후보.** ER AUROC 0.894, rule-out 임계(0.63)에서 민감도≥0.90 유지 시 특이도 0.640 — **ER-음성 배제(rule-out)** 용도로는 신호가 있으나 PPV가 유병률에 민감(½유병률에서 0.374로 급락). "대체"가 아니라 "검사 전 우선순위"로 프레이밍해야 안전.

## operating-point 자체가 준 교훈 (방법 기여)

- **threshold=0.5는 임상적으로 틀린 기본값이다.** 희귀 양성 축(HER2 아형·grade_high·kras)은 softmax/sigmoid 출력이 낮은 확률로 쏠려 0.5에서 민감도 0.000이 나온다. 대체 안전성 판정은 **endpoint별 rule-in/rule-out 임계**로 해야 하며, 이 점을 Methods/Discussion에 명시한다.
- **유병률 민감도가 PPV를 지배한다.** ½유병률↔2×유병률 사이에서 PPV가 크게 흔들린다(예 ER 0.374↔0.963). 코호트 유병률에서 좋아 보여도 저유병 임상세팅에서 무너질 수 있어, PPV는 항상 목표 유병률과 함께 보고한다.

## 원고 반영

- Results: hpv_pos rule-in·histology_lusc 균형점을 "저비용 축"의 임상 근거로, Lauren net-benefit<treat-all과 HER2 민감도 0.000을 "고비용(대체 불가)"의 비용 증거로 추가.
- Methods(M4/M5): operating-point 정의(rule-in/out 임계 규칙·ECE·net benefit·유병률 Bayes 재계산) 한 문단.
- Discussion/Limitations: threshold=0.5 부적절성 + 유병률 민감도 + exploratory 축은 지점 추정 불안정.

## claim 규율

모든 수치는 후향적·hypothesis_only. operating-point는 전향 검증을 대신하지 않는다. exploratory(⚠️) 축은 방향만, 확증 아님.

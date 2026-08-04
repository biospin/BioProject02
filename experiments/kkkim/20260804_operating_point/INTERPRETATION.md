# BIOP02-124 #3 — operating-point 해석 노트 (게재 blocker 대응)

> 담당 kkkim · 리뷰 braveji. 자동생성 수치는 [OPERATING_POINT_RESULTS.md](OPERATING_POINT_RESULTS.md)(스크립트 재실행으로 재현), 이 파일은 그 위의 임상 해석이다.
> claim_level: **hypothesis_only** · 후향적. operating-point는 임상 사용가능성의 *상한 탐색*이지 검증이 아니다.

## 왜 이 분석이 게재 blocker였나

리뷰어 지적(#3): AUROC만으로는 "H&E가 분자검사를 임상적으로 대체해도 되는가"에 답할 수 없다.
같은 AUROC라도 **어느 임계에서 얼마나 놓치고(FN) 얼마나 헛짚는가(FP)**, 그리고 **유병률이 바뀌면 PPV/NPV가 어떻게 무너지는가**가 대체 안전성을 가른다. 이 분석은 cost-of-substitution 프레임을 환자단위 지표(민감도·특이도·PPV·NPV·net benefit·유병률 민감도)로 조작화한다.

## 단위·검정력 규율(먼저 — 지표 해석의 전제)

- **단위**: BRCA ER·PAM50 예측은 CPTAC-external·slide 단위라 **환자(case) 단위로 집계**해 재계산했다(ER 118환자, PAM50 115환자). BRCA PR·HER2는 npy만 있어 case_id가 없다 → **slide 단위 그대로**이며, 같은 환자 슬라이드가 상관돼 CI가 실제보다 좁을 수 있음(anticonservative)을 명시한다. 교차암종은 이미 환자 단위(cost JSON).
- **검정력**: powered(n_pos≥25)만 확증적으로 읽는다 = **brca_er·brca_pr·brca_her2·lauren_diffuse·hpv_pos·grade_high·histology_lusc**. 환자단위 집계 후 **PAM50 HER2 아형은 n_pos=14로 exploratory로 내려갔다**(집계 전 39는 슬라이드 중복). 나머지 변이·증폭 축(braf·msi·erbb2·ebv·egfr_amp·egfr_activating·kras)도 exploratory — 5~24 양성에 얹혀 지점 추정이 임계 하나로 크게 흔들린다. 표에 ⚠️로 남기고 본문 승격하지 않는다.

## 핵심 판독 (powered만)

1. **두경부 HPV — 유일한 검정력 있는 봉인 확증, operating-point에서도 rule-in 우수.** AUROC 0.959. threshold=0.5에서 특이도 0.991·PPV 0.929[0.76–1.00]로 **헛짚음이 거의 없다**(rule-in). 특이도≥0.90을 지키는 임계(0.04)에서 민감도 0.885까지 확보돼, pt=0.2 net benefit이 treat-all/none을 모두 상회(0.124 > −0.009). → HPV는 형태에 또렷이 보이는 저비용 축이라는 결정지도 판정을 임상 지표가 뒷받침한다.

2. **폐 LUSC 조직형(양성대조) — 균형 잡힌 operating-point.** AUROC 0.939, 민감도 0.882[0.83–0.93]·특이도 0.873[0.81–0.93]·PPV 0.900. decision curve에서 모델 우위. 양성대조가 지표 수준에서도 건강함을 재확인.

3. **위 Lauren diffuse — operating-point에서도 신호가 없다(정직한 음성).** AUROC 0.536[판별력 사실상 없음]. 여기에 더해 ECE 0.356(최악의 보정)이고 pt=0.2 net benefit이 treat-all보다 낮다(0.254 < 0.418). **주의(over-claim 회피): 판별력이 없으므로 "쓸 신호가 없다"가 안전한 진술이고, 음의 net benefit은 판별 실패에 더해 보정 실패가 얹힌 결과다** — 재보정하면 net benefit은 이동할 수 있다. "의사결정에 쓰면 손해"라는 인과 주장까지는 하지 않는다. 결론은 분자검사 필수 영역이라는 것.

4. **유방 HER2(대체 불가 앵커) — 임계 0.5에서 아무도 양성으로 부르지 못한다.** 이진 HER2 AUROC 0.530(slide 단위), 민감도 0.000·net benefit 음수. 임계를 낮춰도 특이도를 얻는 대가로 민감도가 무너진다. → H&E-예측 HER2로 항HER2 라우팅을 정하면 실제 HER2+ 환자를 놓친다는 결정지도·Yale pCR(0.533) 음성과 일관. (PAM50 HER2 아형은 환자단위 집계 후 exploratory라 앵커 근거로는 이진 HER2를 쓴다.)

5. **유방 ER — 대체가 아니라 분류(triage) 후보.** 환자단위 AUROC 0.913. rule-in 임계(0.70)에서 특이도≥0.90을 지키며 민감도 0.889 확보 — ER-양성 확정용으로 신호가 있으나 threshold=0.5의 특이도가 0.270으로 낮아 그대로는 헛짚음이 많다. PPV가 유병률에 민감(½유병률에서 0.851, 이 코호트 유병률 0.686이 높은 탓)하므로 저유병 세팅 이식은 주의. "대체"가 아니라 "검사 전 우선순위"로 프레이밍해야 안전. **PR은 slide 단위 AUROC 0.778로 균형점(0.5에서 sens 0.738/spec 0.711)** 이나 단위 caveat 유지.

## operating-point 자체가 준 교훈 (방법 기여)

- **threshold=0.5는 임상적으로 틀린 기본값이다.** 희귀 양성 축(HER2·grade_high·erbb2·kras)은 sigmoid/softmax 출력이 낮은 확률로 쏠려 0.5에서 민감도 0.000이 나온다(proba 분포로 컬럼 오독은 배제 확인: 전 endpoint에서 mean(p|y=1)>mean(p|y=0), grade_high는 max proba 0.498<0.5). 대체 안전성 판정은 **endpoint별 rule-in/rule-out 임계**로 해야 하며 이 점을 Methods/Discussion에 명시한다.
- **유병률 민감도가 PPV를 지배한다.** ½유병률↔2×유병률 사이에서 PPV가 크게 흔들린다. 코호트 유병률에서 좋아 보여도 저유병 임상세팅에서 무너질 수 있어, PPV는 항상 목표 유병률과 함께 보고한다.
- **저유병 exploratory 축의 net-benefit "우위"는 유병률 인공물이다.** pt=0.2에서 treat-all이 강한 음수라 거의 모든 모델이 형식상 우위로 보인다 — 그래서 표 2에서 exploratory 행의 ✅를 억제했다(braveji가 이미 egfr_amp를 허위 PASS로 판정한 것과 동류의 함정).

## 원고 반영

- Results: hpv_pos rule-in·histology_lusc 균형점을 "저비용 축"의 임상 근거로, Lauren 판별력 부재+음의 net-benefit과 HER2 민감도 0.000을 "고비용(대체 불가)"의 비용 증거로 추가.
- Methods(M4/M5): operating-point 정의(단위 집계·rule-in/out 임계 규칙·1000-bootstrap CI·ECE·net benefit·유병률 Bayes 재계산) 한 문단.
- Discussion/Limitations: threshold=0.5 부적절성 + 유병률 민감도 + PR/HER2 slide 단위 caveat + exploratory 축 지점 추정 불안정.

## claim 규율

모든 수치는 후향적·hypothesis_only. operating-point는 전향 검증을 대신하지 않는다. exploratory(⚠️) 축은 방향만, 확증 아님. PR/HER2는 slide 단위라 CI가 anticonservative.

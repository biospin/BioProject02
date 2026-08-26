# Discussion (집필 골격)

> 정직한 한계를 정면에 두는 것이 이 논문의 신뢰도. exemplar 정독(TARGET_JOURNAL_GUIDE.md)의 Discussion 관행 반영 후 확정.

## 문단 순서

1. **핵심 주장 재진술.** 결정지도는 "예측 가능성"이 아니라 "대체 안전성"을 기준으로 삼는다. 축마다 경계가 다르며, 그 경계가 임상 비용으로 정량화된다.
2. **정직한 음성의 의미.** 위 Lauren diffuse가 형태학에 안 보이는 것은 실패가 아니라 지도의 정보 — H&E 대체가 위험한 축을 식별하는 것이 이 프레임의 가치.
3. **유방 HER2 대체불가.** 예측 아형 라우팅이 HER2축을 항상 실패시킴 = 분자검사가 필수인 영역을 비용으로 증명. ⚠️ per-axis cost의 스킴 의존성(endocrine·chemo 반전)은 정직하게 서술, robust 주장은 antiHER2 misroute 1.00 + contrast CI로 한정.
4. **실증 이빨(Yale).** <FILL: A3/A4 후> — 후향적 지도에 실제 치료결과 층화를 달아 격상. HER2 blind면 정직한 음성도 C 논지와 일관.
5. **한계.** 전부 후향적·코호트 수준·hypothesis_only. 개인 benefit 아님. 전향 검증 필요. site-disjoint로 leakage는 통제했으나 다기관 일반화는 추가 검증 대상.
6. **모델 비의존성 (Supplement, hypothesis_only).** 헤드라인 UNI(1024-d) 외에 UNI2-h(1536-d)·Virchow2(2560-d)로 동일 파이프라인을 재학습하였고, 법칙의 방향은 특정 FM에 기대지 않는다. 검정력을 갖춘 확증은 세 FM에서 일관하게 재현된다 — 두경부 HPV는 20-seed 우연배제에서 3/3 FM PASS(UNI 0.959·UNI2-h 0.956·Virchow2 0.920), 폐 조직형(LUSC) 양성대조는 0.939·0.961·0.947, 위 MSI-H는 0.860·0.867·0.880이다. 정직한 음성 또한 모델 비의존적이다 — 위 Lauren diffuse는 세 FM 전부 우연배제에 실패(0.536·0.603·0.640)하여 site-교란이 UNI 고유의 산물이 아님을 보이고, 위 ERBB2 증폭도 세 FM 전부 신호가 없어(0.644·0.585·0.668) G2에서 철회한 인용이 모델과 무관하게 재현된다. 검정력이 부족한 경계 축(두경부 EGFR 증폭, 대장 BRAF 등)에서는 FM 간 소폭의 불일치가 남으나, 이는 본문이 이미 한계로 명시한 n_null=5 임계 불안정(M8)과 정합하며 해당 축을 INCONCLUSIVE로 유지하는 근거를 오히려 강화한다. 근거: `experiments/crosscancer/*/full/{mil_cost_results,shuffle_null_robustness}_{uni2h,virchow2}.json`, 20-seed = `experiments/kkkim/20260820_shuffle_null_20seed/`.
7. **임상·연구 함의.** 어디서 H&E 선별 후 표적 분자검사만 시행하면 비용을 아끼는지, 어디서 대체가 위험한지의 실무 지침.

## 한계 (Limitations) — 표현형 예측의 신뢰도 (Critic 7-point 게이트 반영, BIOP02-75)

앵커 코호트(TCGA-BRCA)의 표현형 예측 신뢰도에는 아래 한계를 정면에 둔다. 판정은 모두 완료됐으나(7항목 × 4엔드포인트, 미판정 0), 다음 네 가지는 caution 또는 정직한 음성으로 남으며 감추지 않는다. 근거는 봉인 게이트 트래커(`experiments/braveji/BIOP02-75_critic_gate/GATE_STATUS.md`)와 그 원자료다.

1. **형태-예측의 부가가치는 endpoint-특이적이며 사소한 기준선 위에서 가산적이지 않다(baseline).** ER·PR 예측은 슬라이드 평균 임베딩(mean-embed) 기준선을 외부 코호트에서 유의하게 넘으나(+0.128·+0.223), 아형-only(subtype-only) 기준선에서는 외부에서 역전되어 부가가치가 가산적이지 않다. HER2는 mean-embed 기준선조차 넘지 못한다. 네 엔드포인트 중 **PAM50 4-class만** 유효 기준선(mean-embed)을 내부·외부 모두 신뢰구간 비중첩으로 상회한다(+0.089·+0.165). 따라서 MIL이 사소한 기준선 위에 얹는 이득을 헤드라인으로 삼지 않는다.

2. **충실도 주장은 확률 수준(proba-level)에 한정한다(counterfactual).** attention 반사실 검정에서 예측은 상위-주목 타일에 확률 수준으로 충실하다(무작위 제거 대비 10~23배). 그러나 상위 타일을 제거해도 슬라이드 순위 AUROC는 유의하게 움직이지 않는다(ER 하락 0.0009, PAM50 p=0.061). 이는 결함이 아니라 MIL 신호의 **중복성** — 상위 타일을 지워도 다른 타일이 같은 신호를 담아 순위가 보존됨 — 에서 온다. 충실도는 확률 수준에서만 주장하고 슬라이드 순위(AUROC) 수준의 인과는 주장하지 않는다.

3. **HER2는 실패가 아니라 정직한 음성이다(baseline·cross-dataset reject).** HER2는 기준선 비교와 외부검증 모두에서 reject이며 H&E 형태로 대체 불가(near-random)다. 이는 파이프라인 결함이 아니라 결정지도의 **앵커** — 증폭축은 분자검사가 필수임을 비용으로 증명하는 자리 — 이며, pass인 것처럼 서술하지 않는다.

4. **치료 가설의 생물학적 타당성은 세포주 전이에 기댄 가설이다(bio-plausibility).** pathway-drug 연결은 DepMap/GDSC 일관성(Spearman ρ)에 근거한 가설이며(hypothesis_only), 세포주→환자 전이의 한계를 상속한다. PAM50 라벨은 Parker 2009 계산본(manifest 1009/1009 추적)이나 발현행렬 출처와 계산 스크립트 일부가 미커밋 상태로 재현성 잔여가 있다.

이 모든 산출은 후향적·코호트 수준이며 개인 수준 benefit 주장이 아니라 `hypothesis_only`다. site-disjoint 분할로 leakage(#1 pass)는 통제했으나 다기관 일반화는 추가 전향 검증 대상이다.

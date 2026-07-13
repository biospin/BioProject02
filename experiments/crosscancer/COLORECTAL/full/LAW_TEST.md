# 법칙 검정 — COLORECTAL (대장) ⚠️ **RETROSPECTIVE / post-hoc (봉인 held-out 아님)**

> **이 파일은 폐·위·두경부 LAW_TEST와 표 구조는 같으나 인식론적 지위가 다르다.**
> 대장 MIL 결과는 **2026-07-12 04:45 (commit afedc6a)** 에 먼저 산출·커밋됐고, 대장 사전등록 예측 행은 **2026-07-12 05:06 (commit 77c0633)**, 즉 **결과 21분 뒤**에 추가됐다. 사전등록 표가 대장만 "**이미 관측(0.918) ✓부합**"으로 적은 것이 그 증거다(폐/위/두경부는 "held-out → 예측 ≥X"). 따라서 **대장은 결과-먼저(observed-first) 회고적 특성화이며, 봉인 후 held-out 검정이 아니다.**
> 대조: 폐(예측 05:06 < 결과 15:35)·위·두경부(오늘 HNSC)는 진짜 sealed-forward. **대장은 "held-out 확증"으로 승격 금지 — '가설과 부합하는 회고적 특성화'까지만.**
> claim_level: hypothesis_only · critic_status: pending · 정본 수치 출처 = `routing_cost.json`(holdout=val+test pooled, site-disjoint, n_holdout=161). 2026-07-13.

## 관측 (retrospective, 사전 cost-class 대조)

| endpoint | 사전 cost-class | 관측 AUROC (CI95) | n_pos/n_hold | shuffle-null¹ | misroute | 검정력 | 회고적 판정 |
|---|---|---|---|---|---|---|---|
| msi_high → anti-PD-1 | 대체가능(low; TIL·점액·수질형) | 0.9184 ([0.850, 0.969]) | 21/161 | 0.636 | 0.112 | exploratory(n_pos<25) | 가설과 consistent(회고·저검정력) |
| anti_egfr_eligible → anti-EGFR | 필수(high; 형태 상관물 없음, 하류 프록시만) | 0.7053 ([0.620, 0.783]) | 84/161 | 0.539 | **0.416** | well-powered | 방향 consistent(회고) — held-out 확증 아님 |
| braf_v600 → BRAF+EGFR | 등급적/partial(serrated/MSI 동반 부분가시) | 0.8817 ([0.817, 0.938]) | 15/161 | 0.641 | 0.099 | exploratory(n_pos<25) | 가설과 consistent(회고·저검정력) |

¹ **shuffle-null 단일추정 주의(routing_cost.json §caveat):** seed=42 1회 순열, 소표본에서 분산 큼. braf null이 split 변경만으로 0.44(holdout151)→0.64(holdout161)로 흔들렸고 real은 거의 불변(0.868→0.882). 상승한(>0.5) null은 누수 신호가 **아니다**(누수는 null을 0.5로 낮춘다) — 라벨무관 CLAM bag-size 교란 가능성. 우연배제는 bootstrap CI + real-vs-null 마진으로 판단. patient_overlap=0·site-disjoint 검증됨. FOLLOW-UP(non-blocking): null ~5 seed 평균.

> **수치 정합(3-문서 드리프트 방지):** 정본 = `routing_cost.json`(holdout161, 세 축 동일 split). `mil_cost_results.json`의 braf 0.8676은 **옛 holdout151** 실행이라 이 표와 다름(같은 마커, 다른 split; CI 내 일치). DECISION_MAP Table 2와는 0.918/0.705/0.882로 일치.

## 별도 검정 — 대장 증분(D13, `CONCLUSION_CRC_INCREMENTAL.md`)
위 라우팅 검정과 **다른 질문**: "H&E가 통상 병리(점액성 조직형+편측성)를 **넘는가**"(중첩 LR). 요지: anti-EGFR은 통상병리 위로 작고 경계적 증분(+0.049, BH 통과·Bonferroni 미통과, +CMS 넣으면 소멸=아형 매개), MSI는 탐색적. **법칙 이분법은 이 데이터로 뒷받침 안 됨.** 이 파일(라우팅 cost-class 대조)과 혼동 금지.

## 이 파일이 법칙 스코어보드에 기여하는 것
- **held-out 확증 아님** — 대장은 회고적이라 5암종 "검정력 있는 봉인 확증" 집계에서 **제외**. 방향(대체가능축 高 AUROC / 필수축 最低 AUROC·最高 misroute)은 가설과 부합하나, 이는 sealed-forward 증거가 아니라 회고적 일관성.
- 검정력 있는 봉인 확증은 여전히 **양성대조(폐 histology 0.925·위 Lauren·두경부 grade) + 두경부 HPV(0.959, n_pos=26)** 뿐. 변이/증폭축은 전 암종에서 exploratory. **법칙 = 방향적 일관, 이분법 미확립.**

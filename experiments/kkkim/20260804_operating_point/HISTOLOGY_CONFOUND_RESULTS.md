# BIOP02-124 #7 — 조직형(histology) 보정: 폐 EGFR/KRAS 교란 검정

> 폐 EGFR/KRAS 변이는 LUAD에 몰려 있고 조직형은 형태로 쉽게 갈린다(LUSC AUROC 0.939).
> 조직형으로 층화해 within-stratum AUROC를 재계산 — 마진 신호가 조직형 인공물인지 검정.
> seed 42, 1000-bootstrap CI. **둘 다 n_pos<25 exploratory — 방향만, 확증 아님.**

| endpoint | 전체 AUROC (CI) | within-LUAD AUROC (CI) | within-LUSC | LUAD 유병률 | LUSC 유병률 | pred↔조직형확률 corr | 판정 |
|---|--|--|--|--:|--:|--:|---|
| egfr_activating | 0.851 [0.722–0.953] | 0.787 [0.628–0.922] (pos 14) | 0.668 (pos 1) | 0.119 | 0.006 | -0.621 | 부분 잔존(조직형이 대부분 설명) |
| kras_g12c | 0.681 [0.577–0.782] | 0.361 [0.207–0.52] (pos 14) | pos 0 부족 | 0.119 | 0.000 | -0.547 | **전적 교란**(LUAD한정 우연 이하 붕괴) |

## 판독

- **KRAS G12C: 마진 AUROC 0.681은 조직형 인공물이다.** LUAD 한정 시 0.361로 우연 이하로 붕괴 — 변이 형태 신호가 아니라 "LUAD를 맞히니 KRAS도 맞은 것처럼" 보인 것. 결정지도에서 KRAS는 형태 상관물 축으로 승격 불가.
- **EGFR activating: 마진 0.851 중 상당 부분이 조직형.** LUAD 한정 0.787로 잔존 신호는 있으나(변이 형태 신호가 조직형과 완전 독립은 아님) 마진값은 과대평가다. n_pos=14로 exploratory라 잔존 신호도 방향 수준.
- pred↔조직형확률 상관이 음(−0.62/−0.55)인 것은 예측기가 "LUSC 확률↓ → 변이 확률↑" 경로로 조직형을 타고 있음을 보인다.

## 원고 반영 (정직성 직결)

- 폐 EGFR/KRAS의 마진 AUROC를 "형태 상관물"로 읽으면 안 되며, **조직형 보정이 필수**임을 Methods/Results/Limitations에 명시. KRAS는 조직형 인공물로 강등, EGFR은 조직형 보정값(0.787, exploratory) 병기.
- 이는 결정지도의 신뢰성을 오히려 높인다: 교란을 스스로 찾아 보정했다는 것.

## 미완 (데이터 대기)

- **tumor purity 보정**: TCGA ABSOLUTE/CPE consensus purity 테이블이 리포에 없다 → 별도 데이터 풀 필요(후속). 폐는 조직형이 지배적 교란이라 우선 처리했고, purity는 보조 공변량. 타 암종(위 Lauren 등)의 stromal 교란 검정도 purity 확보 후.

> claim_level: hypothesis_only · 둘 다 exploratory(n_pos<25). 리뷰: braveji.
# Results (집필 골격 — 이 논문의 중심)

> 이 논문은 결정지도가 중심이라 Results가 서면 나머지가 딸려온다. 아래 숫자는 전부 실측(출처 파일 명시)이며 `hypothesis_only`·`critic_status: pending`. 헤드라인 승격 전 결정론 재계산 + Critic 서명 필요(README "검증 게이트").

## R1. 다섯 암종 치환가능성 결정지도 (헤드라인)

- **메시지:** 분자 축마다 H&E로 값싸게 대신할 수 있는 정도가 다르고, 그 경계를 비용으로 지도화한다.
- **Fig2**(confusion×distance + cost overlay) = "이 한 장이 논문". 근거 [../../experiments/kkkim/20260710_cost_of_substitution/fig2_confusion_distance.json](../../experiments/kkkim/20260710_cost_of_substitution/fig2_confusion_distance.json).
- **Fig3**(축별 cost + headline contrast CI). 근거 [.../fig3_axis_cost.json](../../experiments/kkkim/20260710_cost_of_substitution/fig3_axis_cost.json).
- 실측 표(holdout AUC, site-disjoint):
  - 폐 LUSC 조직형 0.939 [0.905–0.967] — 강하게 보임
  - 두경부 HPV 0.959 [0.921–0.986] — 강하게 보임
  - 대장 BRAF V600E 0.868 [0.780–0.938] — 보임
  - 위 Lauren diffuse 0.536 [0.379–0.694] — **안 보임(정직한 음성, R3에서 정면)**
- 대조군: shuffle-null, prevalence baseline(0.5) 각 파일에 포함. baseline 대비를 반드시 함께 서술.

## R2. 유방 anchor — 수용체축과 HER2 대체불가

- 前 Paper A가 흡수된 챕터. 예측된 아형으로 치료를 라우팅하면 **HER2축은 스킴 불문 항상 실패**(misroute 1.00) = 분자검사 대체불가를 비용으로 증명.
- 근거: [../../experiments/kkkim/20260710_cost_of_substitution/](../../experiments/kkkim/20260710_cost_of_substitution/) (patient_routing_cost.json, therapeutic_distance.json).
- ⚠️ 정직성: per-axis cost는 라우팅 스킴에 따라 endocrine·chemo가 반전(0.378↔0.035, 0.105↔0.510). robust한 주장은 **antiHER2 misroute 1.00 + contrast CI가 0을 배제**한다는 것뿐. 안전주장으로 과장 금지.

## R3. 정직한 음성 — 위 Lauren diffuse는 형태학에 안 보인다

- shuffle-null(0.82)이 real(0.54)보다 높고 CI가 0.5를 크게 물음 → H&E가 값싸게 대신할 수 **없는** 축의 실재 증거.
- 이걸 실패가 아니라 지도의 핵심 메시지로 세운다. "예측된다≠대체가능하다"의 가장 강한 사례.

## R4. Yale 실제-결과 앵커 — <FILL: A3/A4 대기>

- 항HER2 축 점수(A3, sjpark) → pCR 층화 AUROC + bootstrap CI, DeLong vs HER2-확률 baseline(A4, jhans).
- 성공 기준: frozen-transfer가 Farahmand **CV AUC 0.80 [0.69–0.88]**에 근접/겹침(이긴다 아님). 재료 완비(276 임베딩), 결과 미착수.
- **두 사람 산출물이 오기 전까지 placeholder.**

## R5. 모델-비의존성 (robustness supplement) — <FILL: 다중 FM 재학습 대기>

- Virchow2·UNI2-h 공간에서 CLAM 재학습 후 결정지도 순서가 유지되는지. 백그라운드 진행 중.
- **본문 아니라 Supplement.** sjpark/braveji 크로스체크(Owner≠Reviewer) 후 채움.

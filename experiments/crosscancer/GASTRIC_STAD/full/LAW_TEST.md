# 법칙 held-out 검정 — GASTRIC_STAD

> 사전등록: SUBSTITUTABILITY_LAW_PREREGISTRATION.md (봉인). claim_level: hypothesis_only · critic_status: pending.
> 자동생성(sh_chain.py) — mil_cost_results.json에서 파생. **커밋 전 사람 검토.**

| endpoint | 사전분류 | 예측(tight) | 반증선 | 관측 AUROC (CI95) | n_pos/n | 예측적중 | 법칙판정 | exploratory |
|---|---|---|---|---|---|---|---|---|
| erbb2_amp | 필수(형태 조용) | blind ≤0.65 | ≥0.80 | 0.6444 (shuffle-null **0.6406**, [0.523, 0.7713]) | 14/107 | **무효(real≈null, 신호 0)** | 미결(INCONCLUSIVE, n_pos<25) | 예 |
| msi_h | 대체가능(TIL/수질형) | 가시 ≥0.82 | ≤0.60 | 0.8599 ([0.7592, 0.9408]) | 24/107 | 적중 | 미결(INCONCLUSIVE, n_pos<25) | 예 |
| lauren_diffuse | 양성대조(강한 형태) | 가시 ≥0.85 | ≤0.60 | 0.5364 ([0.3785, 0.6936]) | 31/58 | 빗나감 | 부분/미결(예측 miss·반증 아님) | 아니오 |
| ebv | exploratory(lymphoepithelioma) | — | — | 0.9477 ([0.8614, 1.0]) | 7/89 | — | exploratory(탐색) | 예 |

**양성대조**: lauren_diffuse AUROC=0.5364 pass=False (soft=False)

- 내부순서 예측 lauren_diffuse≥msi_h≥erbb2_amp: 관측 lauren_diffuse=0.5364 , msi_h=0.8599 , erbb2_amp=0.6444 → 불일치 (점추정만, 유의성 미검정)

## 하이라이트 — 위 HER2/ERBB2-amp vs 유방 HER2(0.599)
- 관측 AUROC=0.6444 (n_pos=14), **shuffle-null 0.6406 → real↔null 마진 0.004 = 자기 순열 위로 신호 0.** 예측=blind≤0.65지만 **"예측적중" 채점은 무효(braveji G2 BLOCKER-1):** 아무것도 학습 못 하는 파이프라인은 모든 endpoint에 ≤0.65를 산출하므로, 신호 없는 낮은 AUROC를 "blind 예측 적중"으로 셀 수 없다. 법칙판정=미결(INCONCLUSIVE, n_pos<25).
- **exploratory(n_pos<25) + real≈null**: 신호 자체가 확립되지 않으므로 유방 HER2-blind(0.599)와의 "consistent" 인용도 **철회한다**(신호 없는 endpoint에서 증거 가치를 끌어올 수 없음). 위 ERBB2-amp는 "증폭 마커 H&E-blindness 부합"의 근거로 사용하지 않는다.

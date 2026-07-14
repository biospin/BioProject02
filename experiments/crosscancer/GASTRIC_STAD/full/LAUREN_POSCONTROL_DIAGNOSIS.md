# 위암 양성대조(Lauren-diffuse) FAIL 원인 진단 — braveji G2

> 질문(braveji G2 잔여): 위암 양성대조 lauren_diffuse가 사전예측 ≥0.85 대비 holdout **0.5364(near-random)**로 FAIL한 것이 **파이프라인 고장인가, 데이터 희소인가, 다른 원인인가.** 이에 따라 "위암 endpoint 전체 저신뢰" 판정을 유지/정정.
> claim_level: hypothesis_only · critic_status: pending(braveji 검토용) · 2026-07-14. 정본 수치 = `mil_cost_results.json`·`baseline_pixelmean.json`·`shuffle_null_robustness.json`·`split.csv`.

## 결론 (요지)
**파이프라인 전역 고장 아님 · 단순 데이터 희소 아님 · Lauren 특이적 site-교란(site confound)이 site-disjoint holdout에서 정당하게 노출된 것.** 따라서 "위암 endpoint **전체** 저신뢰"는 과도 → **Lauren에 국한**되며, 잘 일반화되는 위암 MSI(dev→holdout gap 작음)는 유효로 유지 가능.

## 증거 3종

### [1] dev_auc → holdout_auc 파국적 gap (Lauren에만)
dev_auc는 train에서 분리한 early-stop dev(=train과 **동일 site**), holdout은 **site-disjoint**.

| endpoint | dev_auc | holdout_auc | gap | 해석 |
|---|---|---|---|---|
| **lauren_diffuse** | **0.963** | **0.5364** | **−0.43** | 동일 site 거의 완벽 → site-disjoint 붕괴 = **site shortcut 학습·미전이** |
| msi_h | 0.899 | 0.860 | −0.04 | 건강한 일반화 |
| erbb2_amp | 0.811 | 0.644 | −0.17 | 중간 gap(부분 site 의존) |
| ebv | 0.762 | 0.948 | +0.19 | 소표본(n_pos 7) |

Lauren의 0.43 gap은 위암 4 endpoint 중 유일한 파국. MSI가 멀쩡히 일반화하므로 **임베딩/파이프라인 전역 고장이 아님**.

### [2] pixel-mean이 MIL을 상회 (Lauren에만)
| endpoint | MIL holdout | pixel-mean | MIL − pixel |
|---|---|---|---|
| **lauren_diffuse** | 0.5364 | **0.631** | **−0.09 (MIL이 trivial baseline보다 낮음)** |
| msi_h | 0.860 | 0.777 | +0.08 (MIL 이득, 정상) |
| erbb2_amp | 0.644 | 0.561 | +0.08 |

Lauren에서만 저용량 trivial baseline(slide mean-pool→LogReg)이 CLAM MIL을 이김 → **약하지만 존재하는 형태 신호(0.63)를 MIL이 오히려 못 잡음.** 신호가 아예 없으면(순수 데이터 문제) pixel-mean도 0.5여야 하나 0.63 → **데이터 희소 단독이 아님.** MIL이 site-상관 고용량 특징에 과적합해 일반화를 잃은 패턴과 일치.

### [3] Lauren 양성률의 강한 site 종속 → split이 shortcut을 노출
fold별 lauren 양성률: **train 0.457 · val 0.341 · test 0.875** (극심한 cross-fold 이동).
site별(n≥5): HU 1.00 · FP 0.86 · D7 0.71 · RD 0.69 · CD 0.64 ↔ BR 0.38 · VQ 0.31 · CG 0.18.

Lauren-diffuse 유병률이 site(제출기관/지역)에 강하게 종속. site-disjoint split이 고유병 site(HU 100% 등)를 test로 배치 → train(46%)과 test(88%) 분포가 크게 달라, **모델이 학습한 site-상관 shortcut이 held-out에서 무너짐.** 이는 site-disjoint 평가(Howard 2021)가 **정상 작동**해 site-누수 지름길을 거부한 결과다(덜 엄격한 site-leaky 평가였다면 dev급 0.96로 보였을 것 — 가짜).

## 판정 및 함의
1. **원인 = Lauren 특이적 site-교란.** 파이프라인 고장(X, MSI 정상)·데이터 희소 단독(X, pixel-mean 0.63) 아님. site-disjoint holdout이 교란을 정당하게 노출.
2. **"위암 endpoint 전체 저신뢰" → "Lauren 국한"으로 정정 권고.** 위암 MSI(dev→holdout gap 0.04, MIL>pixel)는 site-과적합 징후 없음 → **유효 유지 가능**(단 여전히 n_pos=24 exploratory). ERBB2는 중간 gap(0.17)이라 부분 의존 — 이미 "신호 0(무효)"로 별도 철회됨.
3. **Lauren은 이 split에서 깨끗한 양성대조로 부적합**(유병률이 site-구조적). 구조: 양성대조 실패는 **파이프라인 sanity 실패가 아니라 평가 엄격성의 증거.** 정직하게 그대로 보고, Lauren을 구조(rescue)하지 않음.
4. **후속(선택, non-blocking):** 더 site-중립적인 강형태 마커(예: signet-ring 세포 존재)로 양성대조 보강, 또는 Lauren을 site-stratified로 재평가(단 site-disjoint 원칙과 상충 주의).

## 스코어보드 반영 제안(braveji 승인 시)
- 위 lauren 행 각주: "양성대조 FAIL = **Lauren 특이 site-교란**(dev 0.96→holdout 0.54, 유병률 site 종속 HU100%~CG18%), 파이프라인 전역 고장 아님. 위암 MSI는 일반화 정상."
- 결론 §3 "위암 endpoint 전체 저신뢰" → "**Lauren 국한**; MSI 일반화 정상, ERBB2는 신호 0으로 별도 철회"로 정정.

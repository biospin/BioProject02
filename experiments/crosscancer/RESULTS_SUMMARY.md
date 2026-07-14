# Cross-cancer MIL + cost 결과 요약 (자동 생성)

생성 시각(UTC): 2026-07-12T06:33:01Z

> 이 문서는 watcher가 MIL 결과에서 자동 생성한 것이다. 판정은 기계적 규칙(real vs shuffle-null)이며, 최종 해석·시사점 갱신·JIRA 반영은 사람이 확인해야 한다.

## 핵심 가설과 읽는 법
유방암에서 얻은 가설은, H&E-예측 아형이 표적에 형태학적 상관물이 있을 때만 분자검사를 대신할 수 있다는 것이다. 따라서 형태학적 상관물이 있는 표적(예: BRAF-대장은 serrated/MSI를 동반)은 H&E가 예측하고, 상관물이 약한 표적(HER2 증폭, EGFR 등)은 H&E-blind일 것으로 본다. 두 결과 모두 원리와 일치할 수 있으며, real vs shuffle-null 비교는 각 표적이 어느 범주인지 알려준다. 양성대조인 histology(LUAD/LUSC)는 형태학 그 자체이므로 real이 shuffle을 크게 상회해야 파이프라인이 정상임을 뜻한다.

## COLORECTAL

임베딩 슬라이드 수는 523장이다. claim_level은 hypothesis_only, critic_status는 pending이다.

### endpoint별 판정 (real vs shuffle-null)
- **braf_v600e**: real AUROC 0.8676 (CI [0.7798, 0.9384], 양성 15명), shuffle-null 0.4426. → H&E가 예측 가능(real 0.8676 ≫ shuffle 0.4426) — 이 표적에 형태학적 상관물이 있다는 뜻이며 원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인..

### 치환비용(cost-of-substitution, 측정 vs 예측 축 라우팅)
- baseline: mis-route 0.015, mean_cost 0.013 (n=136)
- antiBRAF: mis-route 0.733, mean_cost 0.637 (n=15)

### endpoint별 오분류율(histology 포함 — H&E-blind vs triage 대비)
- braf_v600e: mis-route 0.086 (AUROC 0.8676, targeted-mutation(H&E-blind 예상))

## LUNG_NSCLC

임베딩 슬라이드 수는 1024장이다. claim_level은 hypothesis_only, critic_status는 pending이다.
- **양성대조(histology_lusc)**: real AUROC 0.9247, 통과. 양성대조가 실패하면 아래 변이 결과도 신뢰하기 어렵다.

### endpoint별 판정 (real vs shuffle-null)
- **histology_lusc**: real AUROC 0.9247 (CI [0.8894, 0.9573], 양성 152명), shuffle-null 0.4665. → H&E가 예측 가능(real 0.9247 ≫ shuffle 0.4665) — 이 표적에 형태학적 상관물이 있다는 뜻이며 원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인..
- **egfr_activating**: real AUROC 0.8133 (CI [0.6695, 0.9344], 양성 15명), shuffle-null 0.6641. → 경계(real 0.8133 vs shuffle 0.6641) — 사람 검토 필요..
- **kras_g12c**: real AUROC 0.6549 (CI [0.5634, 0.7434], 양성 14명), shuffle-null 0.3842. → 경계(real 0.6549 vs shuffle 0.3842) — 사람 검토 필요..
- **luad_TRU_vs_rest**: real AUROC 0.8325 (CI [0.7249, 0.9343], 양성 25명), shuffle-null 0.5713. → H&E가 예측 가능(real 0.8325 ≫ shuffle 0.5713) — 이 표적에 형태학적 상관물이 있다는 뜻이며 원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인..
- **luad_PI_vs_rest**: real AUROC 0.7863 (CI [0.6462, 0.9034], 양성 18명), shuffle-null 0.5299. → H&E가 예측 가능(real 0.7863 ≫ shuffle 0.5299) — 이 표적에 형태학적 상관물이 있다는 뜻이며 원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인..
- **luad_PP_vs_rest**: real AUROC 0.887 (CI [0.7574, 0.9842], 양성 14명), shuffle-null 0.3272. → H&E가 예측 가능(real 0.887 ≫ shuffle 0.3272) — 이 표적에 형태학적 상관물이 있다는 뜻이며 원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인..
- **lusc_basal_vs_rest**: real AUROC 0.7225 (CI [0.5586, 0.8667], 양성 15명), shuffle-null 0.3351. → 경계(real 0.7225 vs shuffle 0.3351) — 사람 검토 필요..
- **lusc_classical_vs_rest**: real AUROC 0.4719 (CI [0.3156, 0.6297], 양성 20명), shuffle-null 0.4. → H&E-blind(real 0.4719 ≈ shuffle 0.4) — 이 표적에 형태학적 상관물이 없어 분자검사가 대체 불가하다는 뜻이며 유방암 HER2 패턴과 일치한다..
- **lusc_secretory_vs_rest**: real AUROC 0.6408 (CI [0.4887, 0.7856], 양성 11명), shuffle-null 0.4191. → 경계(real 0.6408 vs shuffle 0.4191) — 사람 검토 필요..
- **lusc_primitive_vs_rest**: real AUROC 0.6159 (CI [0.3191, 0.8909], 양성 6명), shuffle-null 0.4565. → 경계(real 0.6159 vs shuffle 0.4565) — 사람 검토 필요..

### 치환비용(cost-of-substitution, 측정 vs 예측 축 라우팅)
- chemo: mis-route 0.008, mean_cost 0.006 (n=241)
- antiEGFR: mis-route 0.867, mean_cost 0.578 (n=15)
- antiKRAS_G12C: mis-route 1.0, mean_cost 0.914 (n=14)

### endpoint별 오분류율(histology 포함 — H&E-blind vs triage 대비)
- histology_lusc: mis-route 0.159 (AUROC 0.9247, morphology(triage 예상))
- egfr_activating: mis-route 0.056 (AUROC 0.8133, targeted-mutation(H&E-blind 예상))
- kras_g12c: mis-route 0.052 (AUROC 0.6549, targeted-mutation(H&E-blind 예상))

# 법칙 held-out 검정 — HEADNECK_HNSC (두경부)

> 사전등록: SUBSTITUTABILITY_LAW_PREREGISTRATION.md (봉인, 28행 표 + 원칙 #7). claim_level: hypothesis_only · critic_status: pending.
> 채점 = `sh_hnsc_lawtest.py` (mil_cost_results.json 파생). **커밋 전 사람 검토 완료(kkkim, 2026-07-13). Owner≠Reviewer → Critic 서명은 별도(kkkim이 owner라 self-sign 금지).**

**커버리지:** 임베딩 존재 슬라이드 468장(고유 환자 450) / 라벨 환자 523명 → **커버리지 450/523(86%)**. 평가는 val+test pooled holdout(site-disjoint). 라벨-임베딩 격차(73환자)는 raw WSI 미다운로드/타일 실패분(전량 검정 아님, STAD와 동일 방식으로 명시).

| endpoint | 사전분류 | 예측(tight) | 반증선 | 관측 AUROC (CI95) | n_pos/n_hold | shuffle | 예측적중 | 법칙판정 | exploratory |
|---|---|---|---|---|---|---|---|---|---|
| hpv_pos | **대체가능**(바이러스축 형태 가시: 비각화·basaloid) | ≥0.80 | ≤0.60 | **0.9594 ([0.921, 0.9863])** | **26/135** | 0.680 | 적중 | **부합(CONFIRM)** | **아니오(검정력 有)** |
| egfr_amp | 등급적/필수(형태 상관물 대체로 없음) | ≤0.70 | ≥0.80 | 0.6039 ([0.4428, 0.7595]) | 17/152 | 0.319 | 점추정 적중 | 미결(INCONCLUSIVE, n_pos<25) | 예 |
| grade_high | 양성대조(분화도=H&E; SCC soft) | ≥0.75(soft) | — | 0.8152 ([0.7423, 0.8815]) | 41/147 | 0.446 | 적중 | 양성대조 PASS | 아니오 |

**양성대조**: grade_high AUROC=0.8152 → PASS(≥0.75, 0.85엔 미달 — SCC 분화도라 강한 대역 아님이 예측대로). 파이프라인 sanity 확립.

## 하이라이트 — 교차암종 법칙 최초의 **검정력 있는** held-out 확증
- **HPV 상태 = n_pos=26 ≥ 25(사전등록 임계)** → exploratory 아님. 폐·위암·유방의 held-out은 대부분 n_pos<25로 INCONCLUSIVE였던 반면, **두경부 HPV가 법칙 "형태 상관물 있음 → 대체가능(≥0.80)" 축의 첫 검정력 확보 CONFIRM**.
- AUROC 0.9594 (CI 하한 0.921) ≫ 사전등록 0.80. shuffle-null 0.680 대비 뚜렷. 이는 변이축이 아니라 **바이러스축**(HPV 감염이 비각화·basaloid 형태를 유도) — 법칙의 "형태 상관물" 조항을 새 종류(감염)로 확장 검정한 것.
- **임상 의미(hypothesis_only):** HPV 상태는 de-escalation/예후 결정을 가르는데, H&E로 강하게 예측 가능 → 이 결정축에서 분자검사(p16 IHC / HPV ISH)를 형태학이 값싸게 보완할 여지. 단 확증 서술은 Critic 서명·복제 전까지 provisional.

## EGFR — 필수/등급적 축, 검정력 부족
- 관측 0.6039, n_pos=17(<25) → **INCONCLUSIVE**. 점추정은 사전등록 ≤0.70 대역 내(형태 상관물 약함과 consistent)이나, 검정력 부족으로 확증·반증 모두 불가. shuffle 0.319(양성률 낮아 불안정).
- 반증신호(≥0.80) 없음 → 법칙과 배치되진 않음.

## 내부순서 — HPV > EGFR
- 점추정 HPV 0.9594 > EGFR 0.6039, 그리고 **두 CI가 완전 분리**(HPV [0.921, 0.9863] vs EGFR [0.4428, 0.7595], 겹침 없음). 순서 자체는 견고.
- 단 EGFR endpoint의 **절대 대역(≤0.70) 판정은 exploratory**라 INCONCLUSIVE로 표기(과소검정력이 나쁜 결과를 가리지 않도록 대칭 verdict 유지). 순서(HPV≫EGFR)는 확립, EGFR의 법칙 대역 적합은 미결.

## 법칙 스코어보드 반영(provisional)
- 대체가능축(형태 상관물 有 → 높은 AUROC): 두경부 HPV **첫 검정력 확증**(0.96) · 유방 PAM50(0.76, 내부) · 위암 MSI(0.86, exploratory).
- 필수/변이축(형태 상관물 無 → 낮은 AUROC): 유방 HER2-blind(0.599) · 위암 ERBB2-amp(0.64, expl) · 두경부 EGFR(0.60, expl) — 방향 일관, 대부분 검정력 부족.
- **결론(hypothesis_only, critic pending):** 두경부 HPV가 "형태 상관물 있는 결정축은 H&E로 대체가능"을 처음으로 검정력 있게 뒷받침. 필수/변이축의 H&E-blindness는 방향은 일관하나 개별 암종에선 여전히 대부분 exploratory → 법칙의 완전 이분법 확립은 검정력 있는 필수축 반례/확증 축적 대기.


## 5-seed 우연배제 + pixel-mean baseline (2026-07-14, BLOCKER-1·3)
- **★ hpv_pos 0.9594 5-seed PASS(thr 0.790)** = Paper C 유일 검정력 있는 CONFIRM의 우연배제 확립(braveji BLOCKER-1 해소). pixel-mean 0.922로도 견고.
- grade_high(양성대조) PASS(thr 0.550). egfr_amp FAIL(real 0.604 < thr 0.631, 원 INCONCLUSIVE 일관).
- pixel-mean: hpv 0.922·grade 0.590(MIL 0.815, attention 이득)·egfr_amp 0.540. 통합 = 스코어보드 §5-seed.

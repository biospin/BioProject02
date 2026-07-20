# 다중 FM 재학습 비교 — 대장(첫 결과) · 모델 비의존성 검정

> 목적: 치환가능성 결정지도가 **특정 파운데이션 모델(UNI)의 산물이 아닌지** 검정. 각 FM 임베딩 공간에서 CLAM을 **재학습**해야 성립하는 주장이라(HANDOFF §1 "주장 한계"), 임베딩만으로는 말할 수 없다.
> claim_level: **hypothesis_only** · critic_status: **pending** · 2026-07-20. 산출 = `COLORECTAL/full/mil_cost_results_{virchow2,uni2h}.json`(재학습 러너 `multifm_retrain_watcher.py` 자동 실행, 07-20 01:36/01:39).
> **Owner=kkkim(대행) → Reviewer=sjpark/braveji 크로스체크 필요**(Owner≠Reviewer).

## 비교 조건 (apples-to-apples 확인)
세 FM 모두 **동일 슬라이드 523장 · 동일 site-disjoint holdout(n=151) · 동일 endpoint(braf_v600e) · n_pos=15**. 차이는 임베딩 공간뿐.

| FM | 차원 | real AUROC | 95% CI | shuffle-null | real−null 마진 | dev_auc |
|---|---|---|---|---|---|---|
| UNI v1 (정본) | 1024 | 0.8676 | [0.780, 0.938] | 0.4426 | +0.425 | 0.918 |
| Virchow2 | 2560 | **0.9328** | [0.865, 0.981] | 0.4819 | +0.451 | 0.990 |
| UNI2-h | 1536 | **0.9377** | [0.881, 0.980] | 0.6456 | +0.292 | 0.995 |

## 읽는 법 (과대주장 차단)

1. **방향 일치 = 모델 비의존성의 첫 근거.** 세 FM 모두 BRAF를 자기 shuffle-null보다 뚜렷이 높게 예측한다. 즉 "H&E가 대장 BRAF를 어느 정도 본다"는 관측이 UNI 특유의 인공물이 아니다. 결정지도의 이 칸은 FM을 바꿔도 유지된다.
2. **FM 우열은 주장할 수 없다.** UNI의 CI [0.780, 0.938]가 Virchow2·UNI2-h의 CI와 **크게 겹친다.** 점추정이 신형 FM에서 높지만 통계적으로 구분되지 않는다. "신형 FM이 더 낫다"는 서술 금지.
3. **exploratory(n_pos=15 < 사전등록 25).** 세 결과 모두 확증이 아니라 방향 근거다. 대칭 규칙상 확증·반증 어느 쪽도 못 한다.
4. **UNI2-h의 shuffle-null이 높다(0.6456).** real−null 마진이 0.292로 셋 중 가장 얇다. 이는 소표본 단일시드 null 불안정(기존 caveat, `routing_cost.json` §shuffle_null_caveat)과 같은 양상 — **UNI에 적용했던 5-seed 우연배제를 신형 FM에도 돌려야** 같은 수준의 근거가 된다(현재 미실시).
5. **범위 한계.** 대장의 **braf 한 endpoint**만 재학습됐다(MSI·anti-EGFR 미실시). 다른 암종(위·폐·두경부)·다른 축은 아직 없다. "법칙이 모델 비의존적"이라는 일반 주장은 이 한 칸으로 성립하지 않는다.

## 현재 말할 수 있는 것 / 없는 것
- ✅ 말할 수 있음: "대장 BRAF 축에서 H&E 신호는 UNI·Virchow2·UNI2-h 세 공간에서 방향이 일치했다(전부 exploratory)."
- ❌ 말할 수 없음: "법칙이 모델 비의존적이다"(1암종·1endpoint) · "신형 FM이 더 낫다"(CI 겹침) · "확증됐다"(n_pos<25).

## 남은 일
- [ ] 신형 FM에도 **5-seed 우연배제**(특히 UNI2-h) — UNI과 동일 기준(real > null_mean+2·null_sd).
- [ ] 대장 나머지 endpoint(MSI·anti-EGFR) 및 두경부·위·폐 재학습(임베딩 완료 순).
- [ ] **sjpark/braveji 크로스체크**: ① 결정론 재계산이 저장값과 일치하는지 ② UNI 결정지도의 **순서**가 다른 FM에서도 유지되는지(절대값이 아니라 순서가 논지).

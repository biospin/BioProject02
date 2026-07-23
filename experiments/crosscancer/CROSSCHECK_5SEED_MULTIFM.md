# 크로스체크 — 다중 FM 5-seed 우연배제 (2026-07-23, kkkim 자동 1차)

> 자동 크로스체크(결정론·순서보존) 결과. **사람 Owner≠Reviewer 사인오프는 별도**(sjpark/braveji, BIOP02-101).
> 데이터: 신형 FM(virchow2·uni2h) 5-seed shuffle-null. 기준 `real_auroc > null_mean + 2·null_sd`(ddof=1).

## 1. 결정론 재계산 대조
- UNI 정본 재현: 대장 braf real-only 스모크 = **0.8676** = `MULTIFM_COMPARISON.md` UNI값 정확 일치. 코드경로 안전.
- 신형 FM 재현: 대장 virchow2 braf seed42를 **두 번** 독립 실행 → 둘 다 **0.8798**(slides=526, n_pos=15/152). 결정론 성립.

### ⚠️ 발견: mil_cost 다중 FM real 값이 stale
| | mil_cost_results(재학습, 저장값) | 5-seed real(seed42, 현재 재현) | 원인 |
|---|---|---|---|
| 대장 virchow2 braf | 0.9328 (n_hold=151) | **0.8798** (n_hold=152) | 임베딩 커버리지 증가 |
| 대장 uni2h braf | 0.9377 (n_hold=151) | **0.8978** (n_hold=152) | 〃 |

- 신형 FM 임베딩이 재학습 시점 이후 늘어(UNI 523장 vs 신형 526장) site-disjoint 홀드아웃이 151→152명으로 바뀌었고, 그만큼 real이 이동했다. **UNI(523장)는 불변**이라 정본 헤드라인은 영향 없음.
- 조치: `MULTIFM_COMPARISON.md` 대장 표의 신형 FM real을 5-seed 재현값으로 정정(아래 §4). mil_cost 저장값은 참고로 남기되 "stale(구 커버리지)" 표기.

## 2. 결정지도 순서 보존 (논지 = 절대값 아닌 순서)
**폐(3 endpoint)**: 세 FM 모두 real AUROC 내림차순이 **histology_lusc > egfr_activating > kras_g12c**로 동일.
- Spearman(UNI real vs virchow2) = **1.000**, Spearman(UNI vs uni2h) = **1.000**.
- → "H&E가 폐에서 조직형>EGFR>KRAS 순으로 보인다"는 결정지도 순서가 **FM을 바꿔도 보존**된다. 모델 비의존성의 직접 근거.
- 대장은 endpoint 1개(braf)라 순서 검정 불가(단일 칸 방향만).

## 3. 5-seed 우연배제 PASS/FAIL (현재 정본)
| 코호트 | FM | endpoint | real | thr(null_mean+2sd) | 판정 |
|---|---|---|---|---|---|
| 폐 | virchow2 | histology_lusc | 0.9469 | 0.7981 | ✅ PASS |
| 폐 | virchow2 | egfr_activating | 0.8833 | 0.7886 | ✅ PASS |
| 폐 | virchow2 | kras_g12c | 0.7404 | 0.7128 | ✅ PASS |
| 폐 | uni2h | histology_lusc | 0.9607 | 0.8606 | ✅ PASS |
| 폐 | uni2h | egfr_activating | 0.8818 | 0.7790 | ✅ PASS |
| 폐 | uni2h | kras_g12c | 0.7607 | 0.6113 | ✅ PASS |
| 대장 | virchow2 | braf_v600e | 0.8798 | 0.8688 | ✅ PASS(빠듯, 마진 0.011) |
| 대장 | uni2h | braf_v600e | 0.8978 | **0.9272** | ❌ **FAIL** |

## 4. 판정 (과대주장 차단)
1. **폐 = 강한 모델 비의존성.** 6/6 PASS + 순서 Spearman 1.000. "H&E 신호의 폐 결정지도 순서는 UNI·Virchow2·UNI2-h에서 일치한다"고 말할 수 있다(단 endpoint별 exploratory 지위는 유지 — egfr/kras n_pos=14~15).
2. **대장 braf = 부분적 모델 비의존성(2/3 FM).** UNI PASS·virchow2 PASS(빠듯)이나 **uni2h는 5-seed에서 FAIL**. 이는 MULTIFM_COMPARISON §4가 예고한 "uni2h shuffle-null 0.646, 얇은 마진"이 **실제로 우연배제를 통과 못 한 것**. → "대장 BRAF가 모델 비의존적으로 확인됐다"는 서술 **금지**. 정직하게 "3 FM 중 2개에서 우연배제, uni2h는 단일-cohort 소표본(n_pos=15) 소음으로 미확보"로 쓴다.
3. **여전히 exploratory.** braf n_pos=15 < 사전등록 25. 5-seed PASS도 확증이 아니라 방향 근거. claim_level=hypothesis_only, critic_status=pending 유지.
4. **FM 우열 주장 금지**(CI 겹침, 기존 가드 유지). 5-seed는 "법칙 성립"이 아니라 "모델 비의존성" 근거이며, 대장 1축·폐 3축이라 법칙 일반화엔 불충분.

## 5. 남은 것 — 사람 Owner≠Reviewer 사인오프
kkkim은 결과 owner라 최종 판정 불가. **sjpark/braveji 크로스체크 요청**(BIOP02-101):
- (1) 결정론 재계산이 저장값과 일치하는지 독립 확인(특히 대장 uni2h FAIL 재현).
- (2) 순서보존 Spearman 1.000 독립 재계산.
- (3) 대장 uni2h FAIL의 서술 수위(§4-2) 동의 여부.

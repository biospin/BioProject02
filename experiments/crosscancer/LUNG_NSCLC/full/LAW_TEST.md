# 폐(LUNG_NSCLC) — 형태학적 상관물 치환가능성 법칙 held-out 검정

> **5개 암종 중 첫 held-out 검정.** 사전등록 `../../SUBSTITUTABILITY_LAW_PREREGISTRATION.md`(폐 봉인 예측 4개, 결과 보기 전 커밋으로 봉인)의 예측을 1047→1048 임베딩 기반 MIL 관측과 대조.
> claim_level: **hypothesis_only** · critic_status: pending · 2026-07-12
> **⚠️ 정본 재동기화 2026-07-14 (braveji G2 BLOCKER-2 반영):** 폐 MIL은 2회 실행됐고(994b187 → 9b42d37, n_slides 1024→1026) 본 문서는 1차 기준에 멈춰 있었다. 재실행이 "위암 442장" 커밋 본문에 묻혀 인지되지 못함. 아래 **base 3 endpoint(histology/egfr/kras)**를 정본 `mil_cost_results.json`(9b42d37) 기준으로 정정한다. 정정 방향은 결과 개선(histology 0.9247→0.939, egfr shuffle 0.66→0.46). subtype endpoint는 `mil_subtype_results.json` 소관으로 본 정정 범위 밖.
> 산출: `mil_cost_results.json`(base 3 endpoint + subtype 7 endpoint 병합), `mil_subtype_results.json`.
> 모델: CLAM-SB(UNI 1024-d), val+test **pooled site-disjoint holdout**, 환자단위 평균, AUROC + 1000-boot 95% CI. 각 endpoint {real, shuffle-null, prevalence}.

## 검정력 (해석의 지배 변수)
| endpoint | holdout n_pos | 검정력 판정 |
|---|---|---|
| histology_lusc | **153 / 271** | **충분 — 유일하게 확증/반증 가능한 진짜 검정** |
| egfr_activating | 15 / 271 | exploratory (n_pos<25) → INCONCLUSIVE |
| kras_g12c | 14 / 271 | exploratory → INCONCLUSIVE |
| luad_TRU_vs_rest | 25 / 57 | 경계(자체 AUROC는 보고 가능) |
| luad_PI / PP_vs_rest | 18 / 14 | exploratory → 순위 비교 불가 |

**대칭 적용 원칙(advisor):** exploratory→INCONCLUSIVE는 확증뿐 아니라 **반증에도 동일 적용**. n_pos 14–15에서는 점추정이 예측대역에 들어도 "consistent with"까지만, 예측을 벗어나도 "반증 확정" 금지. 양성대조가 통과해도 그것이 KRAS/EGFR의 검정력을 만들어주지 않는다(파이프라인 정상성 ≠ 마커 검정력).

## 관측 요약
| endpoint | real AUROC | 95% CI | shuffle-null | n_pos |
|---|---|---|---|---|
| histology_lusc | **0.939** | [0.9046, 0.9666] | 0.4343 | 153 |
| egfr_activating | 0.8518 | [0.7247, 0.953] | 0.4589 | 15 |
| kras_g12c | 0.6809 | [0.577, 0.7825] | 0.5081 | 14 |
| luad_TRU_vs_rest | 0.8325 | [0.7249, 0.9343] | 0.5713 | 25 |
| luad_PI_vs_rest | 0.7863 | [0.6462, 0.9034] | 0.5299 | 18 |
| luad_PP_vs_rest | 0.8870 | [0.7574, 0.9842] | 0.3272 | 14 |
| lusc_basal | 0.7225 | [0.5586, 0.8667] | 0.3351 | 15 |
| lusc_classical | 0.4719 | [0.3156, 0.6297] | 0.4000 | 20 |
| lusc_secretory | 0.6408 | [0.4887, 0.7856] | 0.4191 | 11 |
| lusc_primitive | 0.6159 | [0.3191, 0.8909] | 0.4565 | 6 |

## 봉인 예측 vs 관측

### [1] 조직형 LUAD/LUSC ≥ 0.93 (양성대조) — **유일한 검정력 충분 검정**
- 관측 **0.939**, CI [0.9046, **0.9666**], shuffle 0.4343, n_pos=153.
- **Verdict: PASS(양성대조 성립) / 임계 예측 ≥0.93 점추정 명확 적중.**
  - 파이프라인 정상성: 형태 자체 축을 0.94로 예측, shuffle 0.43 → H&E/MIL 정상 작동 확정.
  - 사전 0.93 라인: 점추정 **0.939 ≥ 0.93 명확 적중.** 1차(stale) 문서의 "0.9247·CI 상한으로 구제(≈met)"는 정본에서 불필요 — 깔끔한 적중이다.
  - 결론: **양성대조 통과. 파이프라인 sound.**

### [2] EGFR 활성변이 등급적 0.75–0.89, near-random(≤0.6) 아님
- 관측 0.8518, CI [0.7247, 0.953], shuffle-null 0.4589, n_pos=15.
- 점추정은 예측 대역 **안(0.75–0.89), near-random 아님** → 예측과 방향 일치. real↔shuffle 마진 **0.39**(1차 문서의 shuffle 0.664·마진 0.15는 stale — 정본 shuffle 0.4589로 신호가 훨씬 깨끗).
- 그러나 **exploratory(n_pos=15) → INCONCLUSIVE.** CI 하한 0.72로 여전히 광범위 → 점추정·마진은 강해졌으나 검정력 부족은 불변.
- **Verdict: consistent with graded(확증 아님).**

### [3] KRAS-G12C ≤ 0.65 **및 EGFR > KRAS 순서**
- KRAS 관측 0.6809(≤0.65 라인 **위** — 정본 기준 경계 이탈), CI [0.577, 0.7825], shuffle 0.5081, n_pos=14.
- EGFR(0.8518) > KRAS(0.6809) → **점추정 순서는 예측과 일치(EGFR>KRAS).**
- 그러나 EGFR·KRAS 모두 exploratory, **CI가 광범위하게 겹침**(EGFR [0.72,0.95] ∩ KRAS [0.58,0.78]) → **순서 어느 방향도 통계적으로 확립 불가.**
- **Verdict: INCONCLUSIVE.** 점추정 순서는 consistent with이나 n_pos 14로 확증 불가. KRAS 0.6809는 사전 ≤0.65 라인을 미세 초과(1차 0.6549 "경계"보다 정본은 오히려 예측서 벗어남) — 단 n_pos 14·CI 광범위로 "필수 마커 예측 실패" 반증으로도 셀 수 없음.

### [4] 전사체 아형 중 **TRU 최고 AUROC**
- LUAD 발현아형 one-vs-rest(LUAD 내 제한; LUSC를 rest에 넣지 않아 histology 재검출 차단):
  **PP 0.887 > TRU 0.833 > PI 0.786.**
- **TRU는 최고가 아님(PP가 더 높음)** → 점추정은 예측 #4를 **지지하지 않음.**
- 단, PP(n_pos=14)·PI(n_pos=18) 모두 exploratory → **순위 비교 자체가 검정력 부족 → INCONCLUSIVE.**
- **Verdict: 점추정 미스(TRU 비최고), 순위 검정 INCONCLUSIVE.** TRU 자체는 0.833로 높아 "TRU가 형태 상관물을 가진다"와는 consistent이나, "아형 중 최고"라는 특정 주장은 뒷받침되지 않음. (LUSC classical 0.47은 blind에 가까움 — 별개 관찰.)

## 종합 verdict
- **positive control(histology) 통과 → 파이프라인 sound.** 이것이 이 검정에서 유일하게 견고한 결론.
- **EGFR·KRAS·TRU-순위는 전부 검정력 부족으로 INCONCLUSIVE.** 점추정은 대체로 법칙과 같은 방향(EGFR 대역내·near-random 아님, KRAS 경계·EGFR>KRAS)이나 확증 불가. **유일한 점추정 미스는 예측 #4(TRU 최고)** — PP가 더 높음.
- **반증 트리거 없음:** (a) '필수' 마커 KRAS가 ≥0.8로 잘 예측되지 않음, (b) '대체가능' 축(histology)이 blind가 아님, (c) EGFR≤KRAS 뒤집힘 없음. 따라서 **법칙 반증은 아니나 확증도 아님** — 폐 코호트는 변이-순서 주장을 판정할 검정력이 없다(첫 held-out 검정의 정직한 결론).
- **함의:** 이 결과로 "법칙 복제/확증"을 주장하지 않는다. histology 양성대조만 확증되고 나머지는 "consistent with". 변이 endpoint의 확증에는 **양성 사례 증대**(다기관 통합/CPTAC 외부, EGFR·KRAS n_pos≥25)가 필요.

## 주의
- claim_level: hypothesis_only. 어떤 우월성/치료 최적화 주장 없음. DRP 아님(형태→가설 라우팅만).
- 임베딩 1048/1053(스트래글러 4장 다운로드중 + 1장 fail_dl; `../STRAGGLERS.md`). 완료 시 EGFR/KRAS n_pos는 사실상 불변(누락은 환자 4명)이라 결론 안정.
- shuffle-null은 holdout n_pos 소수에서 순열/부트스트랩 잡음이 커 endpoint마다 편차가 있다(subtype PP 0.33 등) — exploratory 판정을 강화한다. **단 base 3 endpoint는 정본(9b42d37) shuffle 0.43/0.46/0.51로 재동기화됨.** 단일시드 shuffle의 우연배제 한계는 별도 blocker(≥5-seed)로 다룬다.

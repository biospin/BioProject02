# 크로스체크 — 다중 FM 5-seed 우연배제 (2026-07-23, kkkim 자동 1차)

> 자동 크로스체크(결정론·순서보존) 결과. **sjpark 독립 크로스체크 PASS(2026-07-26, #11462)** — 3포인트 원자료 재계산 확인, 범위=파생통계·순서·서술규율(real 재학습 미포함, kkkim 결정론 근거 채택). **braveji 다중 FM Critic 판정 = caution(2026-07-27, PR#74 독립 재계산): '폐 6/6 재현·과대주장 없음' 인정 + findings 3건(egfr_amp 허위 PASS·모델비의존성 폐 한정·n_null=5 불안정) 원고 Results 반영 조건. → findings 원고 반영 완료(02_results R5·04_discussion, 커밋 926fdc4). 남은 것은 braveji 7-point 최종 서명(BIOP02-75, 원고 Limitation 반영으로 2단 조건 충족).**
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

## 5. 방법 한계 — n_null=5 임계 불안정 (허위 PASS/FAIL 위험)

**기준 `real > null_mean + 2·null_sd`는 null 표본이 5개뿐이라 임계값이 불안정하다.** null_sd가 우연히 작으면 임계가 real 바로 아래로 내려와 **신호가 없어도 기계적으로 PASS**하고(허위 PASS), 반대로 null_sd가 크면 real이 충분히 높아도 FAIL한다. 즉 경계 근처 판정은 신호의 유무가 아니라 **5-seed null의 산포 추정 오차**에 좌우된다. n_null=5는 sd 추정 자유도 4로, 이 산포 자체가 노이즈다.

**경계 판정 3건(이 영역에 실제로 걸림):**
| 사례 | real | thr | 마진 | null_sd | 문제 |
|---|---|---|---|---|---|
| 두경부 HPV / virchow2 | 0.9199 | 0.9234 | **−0.0035** | 0.2408(큼) | 큰 null 산포로 FAIL — 신호 부재 아님(real 0.92) |
| 대장 BRAF / virchow2 | 0.8798 | 0.8688 | **+0.011** | — | 빠듯한 PASS, sd 요동에 취약 |
| 두경부 egfr_amp / uni2h | 0.5046 | 0.4815 | +0.023 | 0.052(작음) | **허위 PASS** — real≈0.5(우연)인데 좁은 null_sd로 통과 |

**대응(과대주장 차단):**
- 경계 마진(|real−thr| 작음) 판정은 **단독 결론 근거로 쓰지 않는다.** HPV·대장 BRAF의 모델 비의존성은 "2/3 FM 통과"로만 서술하고, 경계 FAIL/PASS를 확증·반증으로 승격하지 않는다(§4).
- **egfr_amp uni2h "PASS"는 허위다** — real 0.5046은 우연 수준이고 좁은 null_sd의 산물이다. **어떤 축의 통과 근거로도 쓰지 않는다.** 원고 Results는 egfr_amp를 "미결"로 처리한다(통과축 아님). 산출 JSON(`HEADNECK_HNSC/full/shuffle_null_robustness_uni2h.json`)의 `egfr_amp`에도 caveat를 명기해 자동 재생성 시 오독을 방지한다.
- 무게중심은 경계 사례가 아니라 **마진이 큰 폐 3축(6/6, Spearman 1.000)**에 둔다.

## 6. Owner≠Reviewer 사인오프 (완료)
- (1) 결정론 재계산 저장값 일치 — kkkim 2회 독립 재현(대장 virchow2 0.8798).
- (2) 순서보존 Spearman 1.000 — sjpark 독립 재계산 확인.
- (3) 대장 uni2h FAIL 재현 + 서술 수위 동의 — **sjpark PASS(2026-07-26, BIOP02-101 #11462)**.
- braveji 다중 FM 판정 = **R5 사인오프 통과(2026-07-29, #11466)** — findings 3건(egfr_amp 허위 PASS·모델비의존 폐 한정·n_null=5 불안정) 반영 확인. 본 §5가 그 n_null=5 한계 절이다. claim_level=hypothesis_only·Supplement 유지 조건.
- 잔여: BIOP02-75 7-point 최종 서명(별개 게이트, Discussion caution·저자정보 대기).

# Cross-cancer (Paper C) — 진행·결정·결과 로그

> 살아있는 문서. 주요 진행/결정/결과를 시간순으로 계속 append. follow-up·검증·활용용.
> 관련: 재개=`RESUME_CROSSCANCER.md` · JIRA 에픽 **BIOP02-93**(하위 94 임베딩/95 라벨·split/96 MIL·cost).

## 스코프·전제
- **사용자 (B) 지시(2026-07-11):** GPU 서버 sunset **8/15** 전 논문용으로 cross-cancer 전량 실행. 발표(일 18시 마감/21시 회의)엔 BRCA 결과 위주, cross-cancer는 후속.
- 리더 사인오프하 별도 트랙. A/B(BRCA)는 BRCA-only 유지. hypothesis_only·비-DRP.
- 대상: 폐 NSCLC(LUAD 541 + LUSC 512 = 1053장) → 대장(COAD 459 + READ 166 = 625장), UNI 임베딩.

## 결정 기록 (with 근거)
| # | 결정 | 근거 | 날짜 |
|---|---|---|---|
| D1 | **ALK 드롭** | 세포주 게이트 NO-GO(n=2)·fusion(MAF 아님)·frozen_map에 anti-ALK 축 없음 | 07-11 |
| D2 | **UNI만**(EXAONE/CONCH 스킵) | BRCA 헤드라인=UNI·EXAONE=coords 비호환 셋업 블로커·3배 GPU | 07-11 |
| D3 | 임베딩 raw=**SSD**, 워커당 **OMP=4**, **10워커** | HDD 18워커=thrash(load133)·무제한스레드=thrash(load73) 실측 → 스윗스팟 | 07-11 |
| D4 | 각 endpoint **{real, shuffle-null, prevalence-baseline}** | AUROC≈0.5가 'H&E-blind(가설확증)'인지 'MIL고장'인지 shuffle로 구분(advisor) | 07-11 |
| D5 | **histology(LUAD/LUSC)=양성대조** (≥0.75 게이트) | H&E가 형태 보는지 확인 → 파이프라인 정상성 검증. 실패 시 전체 의심 | 07-11 |
| D6 | 평가=**val+test hold-out 합침**(site-disjoint 유지) | 변이 endpoint test 양성 7-9명 얇음 → CI 넓음. 합쳐 ~15-17명 검정력↑. **사용자 결정** | 07-11 |
| D7 | **EGFR 라벨 보정**(S768I·exon20 dup·E709 추가, T790M·passenger 제외) | strict 9.4%가 놓친 진짜 activating 포섭 → 10.2%(문헌 11-13% 정합). anchor-chasing 아님. **사용자 질의 후** | 07-11 |
| D8 | 폐 cost **버전 A(targeted 3축) + 버전 B(histology 포함 mis-route) 둘 다 산출**, 프레이밍 보류 | LUAD/LUSC가 chemo 레짐 바꿔 치료축 될 수 있음 vs BRCA 평행 단순성. **사용자 결정(보류)** | 07-11 |
| D9 | **ST(공간전사체) 트랙 지금 개설 X** — 방어각 A는 banked, 진짜 ST논문 C는 Paper B 후 | scout+strategist 수렴: H&E→ST 예측 포화·유방 페어ST 소규모/치료라벨無/HER2경계 미포괄. cost-of-sub는 ST 불필요. 상세=`research/paperA-positioning/2026-07-11_HE-ST-scoop-and-angles.md` | 07-11 |
| D9-확인 | **tie-breaker 2건 모두 해소(PDF/웹 직접 확인):** ①Path2Space는 cost-of-substitution 아님(바이오마커 advocacy·반대방향)→우리 **인접·미스쿱 확정** ②Xenium 유방패널 ERBB2 포함→Angle A 실행가능 | bioRxiv 전문(kkkim 업로드) 정독 + 10x 패널 확인. Path2Space는 최근접 선행으로 인용, 방향 반대 명시 | 07-11 |
| D10 | **Angle A 지금 착수**(공간 ERBB2=치환비용 floor, Paper A 강화 방어그림), **C는 bank**(Paper B 후; ⚠️ **필요시 Paper A+B 병합 가능**→C 착수 앞당겨질 수 있음) | 사용자 지시. 스쿱 아님 확정+데이터 확보(ERBB2 포함)→A는 값싸고 HER2 헤드라인 강화. 산출=`experiments/*/angle_A_spatial_erbb2/` | 07-11 |

## 변경 효과 이력 (before → after, 덮어쓰지 말고 누적)

> 개선/변경의 효과를 남긴다. 새 변경 시 아래에 append.

| 변경 | Before | After | 효과 |
|---|---|---|---|
| **D7 EGFR 라벨 분류기 보정** (S768I·exon20 dup·E709 추가) | 9.4% of LUAD (strict, ⚠️WARN 앵커 미달), 53환자 | **10.2%** (✅OK), 58환자 | 놓친 진짜 activating +5명 포섭 → 문헌 앵커(11-13%) 진입, anchor-chasing 아님 |
| **D6 평가 test-only → val+test 합침** (histology 스모크, 부분 데이터) | real 0.806, CI **[0.538, 1.0]**, shuffle-null **0.736** | real 0.954, CI **[0.896, 0.994]**, shuffle-null **0.473** | hold-out 17→60명 → CI 폭 0.46→0.10 축소, shuffle-null이 노이즈(0.74)→깨끗한 null(0.47). real vs shuffle 분리 명확화 |
| **D3 임베딩 자원 튜닝** | HDD 18워커 무제한스레드: load **133**, 폐 15분 **정체** | SSD 10워커 OMP=4: load **~8**, ~3 slides/min 안정 | HDD seek + torch 스레드 thrash 제거. 처리율 회복 |
| **Angle A 역치 v1→v2 하드닝** (methodologist spec) | 임의 percentile: 배경 median 12%~90th 63%~95th 78% (역치 의존 심함) | **threshold-free Θ=P(tumor≤ref)=1−AUC**: 중앙 0.158·범위 0.023-0.424, **CI 0배제 8/8** | 정규화 불변·rank기반. kill 통과: interior-only 7/8·depth-cond(high-ρ) 3/3 생존. mixture 대신 분포중첩 확정. commit 대기 |

## 진행 상황
- 07-11 ~11:40 임베딩 자율 착수(스모크 PASS 후 detached). 튜닝 수렴(D3).
- 07-11 12:xx 라벨·split·MIL 스크립트 작성+검증, supervised 자동 체인 detached(임베딩 완료 감지).
- **임베딩 진척:** 07-11 12:56 = 폐 235/1053 · 대장 168/625 → 16:06 = 폐 425 · 대장 356(순조). ETA 오늘밤~일 새벽.
- **Angle A 착수·1차 결과(07-11 16:xx, commit 6c73620):** Andersson HER2+ ST(Zenodo 4751624, 8명) 다운로드(AES 암호 README에서 획득)→분석. **확진 HER2+ 8명 전원 종양 면적 일부가 HER2-음성 배경 ERBB2 수준**(strict median 12%·range 7-30%). floor 논지 성립. 그림 `experiments/kkkim/angle_A_spatial_erbb2/fig_erbb2_floor.png`. ⚠️ ST=메커니즘 시연·Path2Space 반대해석 관리.
- **Angle A v2 하드닝(07-11 22:xx, methodologist spec):** 임의 percentile → **threshold-free Θ=P(tumor spot ERBB2 ≤ ref spot ERBB2)=1−AUC**(정규화 불변·rank기반). **Θ 중앙 0.158·범위 0.023-0.424, CI 0배제 8/8.** kill 통과: interior-only(확산통제) 7/8(B만 margin)·depth-conditioning(high-ρ C/E/G) 3/3 생존. 사전확인 tumor ERBB2 zero-frac≈0(graded-low). 환자=복제단위(pooling 금지). 산출 `analyze_v2_overlap.py`·`fig_erbb2_floor_v2.png`·`spatial_erbb2_floor_v2.json`. **floor 주장 하드닝 후에도 방어 성립.** claim 재규정=label 정보손실/target coverage('치료 실패' 아님). Path2Space 화해 프레이밍 확정.

## 검증된 사전결과 (임베딩 완료 전, 부분/GPU-free)
- **세포주 냉동지도·치료거리(완료):** 폐 antiKRAS-G12C↔chemo **0.914**·antiEGFR↔chemo 0.667 / 대장 antiBRAF↔baseline **0.868** (BRCA HER2↔chemo 0.765 재현). positive control 통과.
- **라벨 prevalence(게이트 통과):** EGFR-activating 10.2%·KRAS-G12C 12.4%·BRAF-V600E 9.0% (문헌 앵커 내). histology LUSC 484명.
- **split(site-disjoint 검증):** 폐 1050환자/69site(hash 9100041e)·대장 534/37site. patient/site-overlap 0.
- **MIL 스모크(양성대조, 부분 215장):** histology real AUROC **0.954** [0.90,0.99] vs shuffle-null **0.473** → 파이프라인 정상, H&E 형태 인식 확인.
- endpoint별 hold-out 양성수: histology 176(train308) / EGFR ~17 / KRAS ~15 / BRAF ~15 (val+test 합).

## 대기 중 (임베딩 완료 후 자동 산출 → **사람 검토 필요**)
- 폐/대장 `mil_cost_results.json`: endpoint별 real vs shuffle-null AUROC + cost 버전A/B.
- **가설:** 표적변이(EGFR/KRAS/BRAF) real≈shuffle(H&E-blind) vs histology real≫shuffle(H&E-triage) → BRCA "HER2 blind/basal triage" 패턴의 cross-cancer 재현.
- 검토 포인트: 양성대조 통과? 변이 CI? cost 프레이밍(A vs B)? EGFR 10.2% caveat.

---

## 중간 시사점 (계속 갱신 — 발표/논문 도입부 재활용용)

> 갱신 로그: **v1 2026-07-11** (임베딩 진행 중, MIL 전). 결과 나올 때마다 append.

### 수렴하는 핵심 원리
**H&E 형태학은 조직 수준 표현형(형태·아형)은 담지만, 국소 유전체 드라이버(점돌연변이·증폭)엔 체계적으로 눈이 멀며 — 바로 그 지점이 분자검사가 대체 불가한 곳이다.** BRCA에서 도출, cross-cancer에서 재현 시험 중.

### 확정 결과
1. **BRCA HER2축: 라우팅 무관 100% mis-route**(PAM50·receptor 둘 다) → H&E-예측 아형은 항HER2 결정을 대체 못 함(분자검사 필수).
2. **cost 렌즈가 외부 배치 아티팩트를 폭로:** CPTAC서 예측이 다수클래스로 붕괴(antiHER2 예측 0%·ER over-call). endocrine 5%/chemo 73% "반전"은 스킬 아닌 붕괴 산물. → raw AUROC(0.9)가 숨긴 miscalibration을 cost가 축별로 드러냄(방법론 기여).
3. **헤드라인 contrast robust:** cost(antiHER2)−cost(endocrine) = PAM50 0.340[0.276,0.402]·receptor 0.381[0.348,0.420], 둘 다 0 배제.
4. **표적축↔chemo 치료거리 암종 무관하게 큼**(세포주, GPU-free): BRCA HER2↔chemo 0.765·폐 KRAS-G12C↔chemo 0.914·대장 BRAF↔baseline 0.868. → 표적변이축의 치료적 고립은 치료 지형의 일반 성질.
5. **양성대조(부분):** H&E가 폐 LUAD/LUSC를 0.954[0.90,0.99]로 구분(shuffle 0.473과 명확 분리) → 형태는 확실히 읽음.

### 전략적 시사점
- **레드오션 탈출:** "H&E가 X를 예측"(포화)이 아니라 **"H&E triage 안전 vs 분자검사 필수의 결정 지도"**(미출판 각).
- **음성 결과가 자산:** H&E가 변이 못 맞힘 = "분자검사 필수 경계선"의 증거.
- **단일암종→원리:** 축별 결정 규칙 정식화한 선행 없음(advisor 확인).

### 정직한 한계
- 외부 miscalibration(CPTAC 붕괴)은 실재 위협 — 결과이자 caveat.
- 변이 endpoint 양성 얇음(hold-out 15-17), EGFR 라벨 10.2%(strict).
- 전부 hypothesis_only·Critic 미통과. 클리니컬 주장 아님.

### v2 부분 갱신 (2026-07-12, 대장 MIL 완료 — 폐 대기 중)

**대장 BRAF-V600E 결과가 가설을 뒤집었고, 이는 원리를 오히려 정교하게 만든다.**

- 대장 MIL이 완료되었다(임베딩 622/625, 3장은 다운로드 실패로 누락, 라벨·split 조인 후 n=523). **BRAF-V600E의 real AUROC는 0.868**(CI [0.780, 0.938], 양성 15명)이고 **shuffle-null은 0.443**이다. 즉 H&E가 대장암 BRAF 변이를 잘 예측한다.
- 이는 "표적 유전자 변이는 형태학에 눈멀다"는 단순 가설과 반대다. 그러나 생물학적으로 설명된다. BRAF 변이 대장암은 톱니형(serrated) 경로·MSI-high·점액성 등 뚜렷한 형태학적 특징을 동반하며(문헌에 확립), EGFR·HER2와 달리 형태학적 상관물이 있는 변이다.
- **정교화된 원리:** "모든 표적 변이가 H&E-blind"가 아니라, **형태학적 상관물이 없는 변이(EGFR·HER2)는 H&E가 눈멀지만, 상관물이 있는 변이(BRAF-대장)는 예측 가능하다.** 치환비용은 표적에 형태학 프록시가 있는지에 달린다.
- 한계: 양성 15명으로 얇아 CI가 넓다(하한 0.780은 0.5보다 확실히 높다). cost의 antiBRAF mis-route 0.733은 예측확률 임계값(0.5) 캘리브레이션 문제일 수 있어 별도 확인이 필요하다.
- **폐(EGFR·KRAS) 결과가 대비를 완성한다.** 폐 표적 변이가 H&E-blind(real ≈ shuffle)로 나오면 "형태학 상관물 유무가 가른다"는 원리가 확정된다. 폐는 진행 중(778/1053, 대장 완료로 가속).
- 산출: `experiments/crosscancer/COLORECTAL/full/mil_cost_results.json`, 자동 요약 `experiments/crosscancer/RESULTS_SUMMARY.md`.

### 다음 갱신 트리거
- [x] 대장 MIL 완료 → 위 부분 갱신(BRAF 예상 밖 예측 가능).
- [ ] **폐 MIL 완료 → EGFR/KRAS가 H&E-blind인지 확인 → 원리 확정(v2 최종).**
- [ ] cost 버전 A/B·임계값 캘리브레이션 확인.
- [ ] 양성대조(histology) 전량 재확인.

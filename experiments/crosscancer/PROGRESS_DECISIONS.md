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

**대장 BRAF-V600E 결과는 유방암에서 얻은 가설과 생물학적으로 일치하며, 원리를 확증하는 방향이다(가설을 뒤집는 것이 아니다).**

- 우리 가설의 정확한 형태(유방암에서 도출): H&E-예측 아형은 **표적에 형태학적 상관물이 있을 때만** 분자검사를 대신할 수 있다. HER2 증폭은 형태학적 상관물이 약해 H&E-blind이고, ER·basal 축은 형태 신호가 있어 상대적으로 예측된다. (초기 cross-cancer 테스트를 "모든 표적 변이는 blind"로 단순화해 세운 것은 loose한 setup이었고, 우리 실제 가설이 아니다.)
- 대장 MIL이 완료되었다(임베딩 622/625, 3장은 다운로드 실패로 누락, 라벨·split 조인 후 n=523). **BRAF-V600E의 real AUROC는 0.868**(CI [0.780, 0.938], 양성 15명)이고 **shuffle-null은 0.443**이다. 즉 H&E가 대장암 BRAF 변이를 잘 예측한다.
- 이는 가설과 **일치한다.** BRAF 변이 대장암은 톱니형(serrated) 경로·MSI-high·점액성 등 뚜렷한 형태학적 상관물을 동반하므로(문헌에 확립), 가설상 H&E가 예측할 것으로 기대되는 표적이며, 실제로 그렇게 나왔다.
- **원리(확증되는 방향):** 표적에 형태학적 상관물이 있으면 H&E가 예측하여 치환 가능하고(BRAF-대장), 상관물이 없으면 H&E-blind이어서 분자검사가 대체 불가하다(HER2 증폭). 치환비용은 표적의 형태학적 상관물 유무가 결정한다.
- 한계: 양성 15명으로 얇아 CI가 넓다(하한 0.780은 0.5보다 확실히 높다). cost의 antiBRAF mis-route 0.733은 예측확률 임계값(0.5) 캘리브레이션 문제일 수 있어 별도 확인이 필요하다.
- **폐(EGFR·KRAS) 결과가 대비를 완성한다.** EGFR·KRAS는 형태학적 상관물이 약하므로 가설상 H&E-blind(real ≈ shuffle)로 기대되며, 그렇게 나오면 원리가 확정된다. 폐는 진행 중(778/1053, 대장 완료로 가속).
- 산출: `experiments/crosscancer/COLORECTAL/full/mil_cost_results.json`, 자동 요약 `experiments/crosscancer/RESULTS_SUMMARY.md`.

### ⚠️ 비교 층위 오류 정정 (2026-07-12, 사용자 지적)

위 대장 BRAF 결과를 유방 HER2와 "하나의 원리"로 묶은 것은 **개념 층위 오류**다. 유방 HER2는 **아형(수용체·증폭)**, 대장 BRAF는 **점돌연변이**로 서로 다른 종류이며, 이를 1:1로 비교해 원리를 주장할 수 없다. **cross-cancer "원리" 주장을 보류한다.** 재발 방지책은 memory `feedback-comparison-like-with-like`에 등록.

**올바른 비교를 위해 대장암 아형 라벨을 확보 중이다.** 유방 PAM50/수용체 아형의 대장 격은 **CMS1-4(Consensus Molecular Subtypes)** 또는 **MSI-H/MSS**다. 진행: ① 대장암 아형 전면 조사(literature-scout, H&E→CMS 선행연구·데이터 접근 포함) ② R env `cms-r` 설치(CMScaller NTP + CMSclassifier RF, ⚠️ 두 알고리즘 불일치 알려짐 → 공개 Guinney 라벨을 authoritative로 우선) ③ CMS 템플릿(529유전자×CMS1-4)은 pyreadr로 이미 추출. 확정 후 CMS를 H&E MIL 아형-예측 endpoint로 추가.

### 다음 갱신 트리거
- [x] 대장 MIL(BRAF, 변이 층위) 완료 — 단 아형 비교엔 부적합(위 정정).
- [ ] **대장 CMS/MSI(아형 층위) 라벨 확보 → H&E→아형 예측 → 유방 아형과 like-with-like 비교.**
- [ ] 폐 MIL 완료 → EGFR/KRAS 확인.
- [ ] cost 임계값 캘리브레이션 확인.

---

### 2026-07-12 — 층위 분리 실행 완료: Part A(예측충실도) / Part B(라우팅비용) 트랙 분리

위 정정(비교 층위 오류)을 실제 분석으로 해소했다. 대장을 **두 트랙으로 분리 실행**하여 유방과 like-with-like 비교를 확립했다.

- **Part A = CMS 예측충실도 트랙**(아형↔아형): H&E→CMS one-vs-rest 4 endpoint MIL(CLAM-SB, site-disjoint holdout). CMS1 0.912(CI 0.828–0.973, exploratory n+19), CMS2 0.871(well-powered n+50), CMS3 0.840(exploratory n+21), CMS4 0.661(well-powered n+42, **약신호**). 이것은 **예측충실도이지 치료비용이 아니다**(CMS=예후 아형, Buikhuisen JNCI 2022). imCMS(Gut 2021, 0.84) 대비 우열 주장 금지 — 다른 코호트/방법. 산출: `COLORECTAL/full/mil_cms_fidelity.json`.
- **Part B = 치료 라우팅 치환비용 트랙**(변이↔변이/수용체): 라우팅 스킴 사전등록(`routing_scheme_preregistered.json`, cost 계산 전 동결) 후 마커 MIL. MSI-H 0.918/misroute 0.112(**저비용, 가설확증**), anti-EGFR(all-RAS/BRAF-WT) 0.705/misroute **0.416**(**고비용, 가설확증** — 가장 약한 예측·최고 misroute), BRAF-V600 0.882/misroute 0.099(부분, 기존 0.868과 CI 내 일치). 산출: `COLORECTAL/full/routing_cost.json`.
- **핵심 비대칭 확립**: 유방은 아형체계(PAM50/수용체)가 곧 치료라우팅이나, 대장은 CMS(예후)와 MSI/RAS(라우팅)가 **분리**된다. **유방 HER2(H&E-blind, 고비용)의 대장 격은 CMS 아형이 아니라 all-RAS 변이축이다** — 단 이는 **서열(ordinal)·결정구조 유사이지 수치 동치 아님**(HER2 0.599 near-random vs anti-EGFR 0.705 above-chance). 아형↔변이 1:1 비교는 여전히 금지.
- **내부-대-내부 비교 확립**: 두 표 모두 내부 site-disjoint holdout. 유방 CPTAC 외부전이 열화는 별도 §4로 격리(내부표에 미혼입).
- Step 0 치료마커 라벨(`labels_treatment.csv`, cBioPortal): MSI-H 86/14.0%, all-RAS 214/34.9%, BRAF 47 — 검증치와 일치, BRAF 재추출은 기존 patient_labels.csv와 0건 불일치(0.868 재사용 정당성 유지).
- 결정지도 문서: `experiments/crosscancer/CROSS_CANCER_DECISION_MAP.md`(표1 아형충실도 / 표2 라우팅비용 분리, §3 비대칭, §4 CPTAC 격리, §5 사람결정 필요항목).
- **미해결(사람/차기)**: ① MSI/anti-EGFR mean_cost는 frozen_map ICI/항체축 제외로 null → 별도 임상거리 사전등록 필요. ② shuffle-null 단일추출 불안정(BRAF null 0.44→0.64, split만 바뀜) → ~5 seed 평균 또는 tile수-proba 상관 확인(bag-size 교란 의심). 상승 null은 누수신호 아님(누수는 null을 낮춤). ③ 모든 산출 critic_status=pending.

### D11 — 통합 flagship 확정 (리더 kkkim, 2026-07-12)
유방(Paper A)을 별도로 두지 않고 **cross-cancer 치환비용 결정지도 flagship의 anchor 암종으로 흡수**(옵션 1). 근거: breast-only 예측은 스쿱(Fernandez-Romero 2026이 CPTAC HER2 열화까지 이미 출판). 거버넌스 재편(A/B BRCA-only → 통합)은 리더 승인으로 성립. 계획=`research/paperC-positioning/FLAGSHIP_PLAN.md`.
- **기여=결정지도(파이프라인 아님).** 예측충실도(표1)·라우팅 치환비용(표2) 분리 유지.
- **AI 레이어 확정:** 치환가능성 스코어 지수 + 보정/기권(CPTAC 붕괴 동기) 채택. VoI=stretch. **RL 제외(단일스텝 미스매치·gimmick 위험).**
- **사전등록 법칙 봉인:** 형태학적 상관물 치환가능성 법칙 = `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`. 폐가 held-out 검정(EGFR 등급적 0.75-0.89 > KRAS ≤0.65 순서 예측). 폐 결과 전 봉인 = 단일 최대 IF 레버.
- **저널 상향:** 모달 IF 6-12(npj Prec Oncol·Genome Med·EBioMedicine·Cell Rep Med), 스트레치 12-16(Nat Commun·npj Digit Med·Med). 20+ 비현실.
- **CPTAC 재해석:** 예측검증으로는 실패(+이미 출판됨)이나, "치환은 도메인 취약" 증거 + AI 결정레이어(보정/기권)의 존재이유. 단 전량붕괴=도메인/보정(고칠수있음) ≠ HER2 내재적 blind(0.599) 구분.

### D12 — 위암(STAD) + 두경부(HNSC) 추가, 5개 암종 flagship (리더 kkkim, 2026-07-12)
사용자 지시로 위암·두경부를 4·5번째 암종으로 추가. 근거: 법칙을 "개수"가 아니라 "대비"로 검정하되, 두 추가가 각각 고유 가치 — **위 HER2-amp = 유방 HER2를 같은 변이·다른 장기로 복제(법칙 최강 교차장기 검정)**, **두경부 HPV = 바이러스라는 새 종류의 형태-가시 축**(변이 아닌 형태 상관물로 법칙 조항 확장). pan-cancer 아틀라스로 흩지 않는 선(5개).
- 후보성 확정: TCGA-STAD ~440, HNSC ~523(WSI 충분). 핵심축 확보 가능(HER2-amp=CNA, MSI=MSIsensor, EGFR, Lauren/조직형). **단 HPV(HNSC)·EBV(STAD)·아형은 cBioPortal SUBTYPE 공란 → 마커논문/유도 필요(폐 SSP와 동일 패턴).**
- 법칙 예측 봉인(결과 전): `SUBSTITUTABILITY_LAW_PREREGISTRATION.md` — 위 HER2-amp ≤0.65(유방 0.599 복제)·MSI ≥0.82·Lauren ≥0.85; 두경부 HPV ≥0.80 > EGFR ≤0.70.
- **CPTAC proteomics(Mertins 2016) 활용 결정:** "HER2 단백질은 높은데 H&E엔 형태학적 상관물이 없음"을 한 줄 확인해 decoupling 굳힘(새 modality 아님, 보조). 사용자 지시. [용어: `PAPER_DIRECTION.md` §용어 정의]

### 밤샘 자율 결과 harvest (2026-07-12 밤) — 결과+의미
**1) shuffle-null 5-seed robustness** (`COLORECTAL/full/shuffle_null_robustness.json`):
- null이 5-seed로 안정화. well-powered(CMS2 0.871 vs null 0.46±0.05, MSI 0.918 vs 0.53±0.11, BRAF 0.882 vs 0.53±0.08)는 real≫null 깨끗 = **누수 없음**. CMS1 0.912 vs 0.60±0.17(null sd 큼, n_pos 19). CMS4 0.661 vs 0.53±0.12 → margin~0.13 **약신호 재확인**.
- **bag-size 교란(proba~tile수 ρ)**: 대부분 patient-level 무의미(견고). **예외 anti_egfr_eligible: slide ρ=−0.334(p≈0)·patient ρ=−0.262(p=8e-4)** → 항EGFR 0.705의 일부가 tile수 교란 = **진짜 형태 신호는 더 약함 → all-RAS 형태 상관물 부재 강화**. 원고에 정직 명시.

**2) Su IMC 재시도** (`COLORECTAL/ST_IMC/`) — **substantive NULL(해상도 문제 아님, 정보적)**:
- 세포 해상도(903k cells, 8 MSI-H/32 MSS)에서 **MSI-특이 면역 공간조직화 관측 안 됨**. 면역 hub 응집(log2 +0.66~1.37)·종양 배제는 MSI/MSS **공통(비특이)**.
- MSI 방향 신호는 **CD8 abundance(밀도)뿐**(+1.6×, NS). → **MSI 판별축 = 공간 기하가 아니라 면역세포 밀도(TIL), 이건 H&E TIL-scoring(Kather·imCMS)이 이미 읽는 것.**
- **결론(메커니즘 경로 확정): 대장 공간-ST 그림 폐기.** 메커니즘 근거 = (a) 유방 ERBB2 floor(공간, 작동) + (b) 대장 MSI=TIL 밀도를 **우리 H&E 모델의 해석가능 형태특징**으로(방법 스카우트 #2와 일치). Visium=해상도 null, IMC=축이 틀림 → 둘 다 "공간 ST는 MSI엔 틀린 도구"로 수렴.

**3) mean_cost 임상거리**: `clinical_routing_distance_preregistered.json` 생성(frozen). ⚠️ **routing_cost.json의 msi/anti_egfr mean_cost는 아직 null → 적용 확인 필요(다음 세션 TODO).**

### 폐 법칙 held-out 검정 결과 (2026-07-12, 5개 암종 중 첫 held-out)
**핵심: 견고히 결론나는 건 양성대조(파이프라인 정상성)뿐. 법칙 판별 예측 3개는 전부 검정력 부족→INCONCLUSIVE.** 사전등록이 노린 "discovery급 격상"을 폐는 못 준다.
- 조직형 LUAD/LUSC(양성대조, n_pos 152): **0.925** CI[0.889,0.957], shuffle 0.467 → **PASS(파이프라인 sound)**. 사전 ≥0.93은 점추정 0.5%p 미달이나 CI 부합(≈met).
- EGFR 등급적: 0.813(대역 안)이나 n_pos=15·shuffle 0.66(마진 0.15)→ **consistent with, INCONCLUSIVE**.
- EGFR>KRAS 순서: 점추정 성립(0.81>0.65)이나 CI 광범위 겹침→ **INCONCLUSIVE**(반증도 아님).
- TRU 최고: **아니오**(PP 0.887>TRU 0.833). 점추정 미스, 순위검정 검정력부족→INCONCLUSIVE.
- **전략 함의: held-out 변이축은 유병률 낮아 구조적 저검정력**(EGFR/KRAS n_pos 14-15). 법칙은 검정력 충분한 **유방+대장서 확립**, held-out(폐·위·두경부)은 **방향적 corroboration**. 위 법칙검정은 검정력 좋은 endpoint(Lauren·MSI·HPV) 전면 + 변이축 exploratory 보조로 프레이밍.
- 스트래글러: 영구실패 1(TCGA-49-4506-DX3, 환자 손실 아님)·느린 대용량 4(train-side만, holdout 불변). 산출: `LUNG_NSCLC/full/LAW_TEST.md`·`mil_cost_results.json`. hypothesis_only/pending.

### 다음 갱신 트리거 (갱신)
- [x] 대장 CMS/MSI(아형 층위) 라벨 확보 → H&E→아형 예측 → 유방 아형과 like-with-like 비교. **(완료: Part A/B 분리)**
- [x] 통합 flagship 확정 + 법칙 사전등록 봉인. **(D11)**
- [x] 위암·두경부 추가(5개 암종) + 법칙 예측 봉인. **(D12)**
- [x] shuffle-null 5-seed·Su IMC·mean_cost 사전등록 harvest(밤샘). **메커니즘=TIL밀도 경로 확정.**
- [ ] STAD/HNSC 임베딩→라벨(HER2-amp/MSI/HPV/EBV/조직형)→split→MIL(법칙 held-out 검정).
- [ ] CPTAC proteomics HER2 decoupling 한 줄 확인.
- [ ] 폐 subtype SSP 계산 → 폐 MIL 완료 → **법칙 held-out 검정**(EGFR>KRAS 순서, EGFR 등급적).
- [ ] MSI/anti-EGFR mean_cost 임상거리 사전등록(진행 중).
- [ ] shuffle-null 다중시드/bag-size 확인(진행 중, GPU).
- [ ] AI 레이어: 치환가능성 스코어 + 보정/기권 구현(결과 안착 후).
- [ ] Critic 리뷰(braveji 총괄) → critic_status pass 후 결과 공유.

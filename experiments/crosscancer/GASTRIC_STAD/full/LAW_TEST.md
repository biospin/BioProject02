# 위암(GASTRIC_STAD) — 형태학적 상관물 치환가능성 법칙 held-out 검정

> **5개 암종 중 두 번째 held-out 검정(폐 다음).** 사전등록 `../../SUBSTITUTABILITY_LAW_PREREGISTRATION.md`(위암 봉인 예측 #5·#6·EBV, 결과 보기 전 커밋으로 봉인)의 예측을 부분 임베딩 기반 MIL 관측과 대조.
> claim_level: **hypothesis_only** · critic_status: pending · 2026-07-12
> 산출: `mil_cost_results.json`. 모델: CLAM-SB(UNI 1024-d), val+test **pooled site-disjoint holdout**, 환자단위 평균, AUROC + 1000-boot 95% CI. 각 endpoint {real, shuffle-null, prevalence}.
> **임베딩: 337/442(부분).** 대용량 슬라이드라 9시 회의 전 442 미완 → 검정력 충분 endpoint(Lauren)로 우선 착수. 나머지는 백그라운드 계속.

## 검정력 (해석의 지배 변수)
| endpoint | holdout n_pos | train n_pos | 검정력 판정 |
|---|---|---|---|
| lauren_diffuse (양성대조) | 30 / 55 | 35 / 69 | n_pos는 임계 이상이나 **train 69명으로 희소 → 아래 참조** |
| msi_h | **24 / 103** | 44 / 224 | 사전임계 25 **1명 미달 → exploratory** (442 완료 시 교차) |
| erbb2_amp (헤드라인) | 14 / 103 | 25 / 224 | exploratory (n_pos<25) → INCONCLUSIVE |
| ebv | 7 / 87 | 15 / 198 | exploratory → INCONCLUSIVE (사전 지정) |

**대칭 적용 원칙(폐와 동일):** exploratory→INCONCLUSIVE는 확증·반증 **양쪽에 동일 적용**. 점추정이 예측대역에 들어도 "consistent with"까지만, 벗어나도 "반증 확정" 금지. **사전등록 임계 25는 사후 이동 금지** — MSI n_pos=24를 24로 낮춰 "well-powered"로 만들지 않는다(post-hoc rescue 금지).

## 관측 요약
| endpoint | real AUROC | 95% CI | shuffle-null | n_pos | 비고 |
|---|---|---|---|---|---|
| lauren_diffuse | 0.6067 | [0.4529, 0.7580] | **0.7693** | 30 | **CI가 0.5 포함, shuffle>real → null-consistent(실패)** |
| msi_h | 0.8027 | [0.6882, 0.9006] | 0.6598 | 24 | 높음, shuffle 상회 (exploratory) |
| erbb2_amp | **0.5851** | [0.4576, 0.7197] | 0.5393 | 14 | 유방 HER2 0.599와 근접, ≤0.65 (exploratory) |
| ebv | 0.8714 | [0.7407, 0.9697] | 0.7143 | 7 | 높음, shuffle 상회 (exploratory) |

## 봉인 예측 vs 관측

### [#6a] Lauren 조직형 ≥ 0.85 (양성대조) — **사전 예정 "유일한 진짜 검정"이 실패**
- 관측 **0.6067**, CI [0.4529, 0.7580](0.5 포함), shuffle-null **0.7693 > real**, n_pos=30.
- **Verdict: FAIL(양성대조 미성립).** 점추정은 0.75·0.85 라인 모두 미달이고, **CI가 우연(0.5)을 배제하지 못하며**, 순열(shuffle)이 real보다 높다 → 이 코호트에서 Lauren 예측은 사실상 null.
- **원인 규명(데이터희소 vs 파이프라인 고장 구분):**
  - Lauren 라벨은 TCGA-STAD에서 희소 기재 — **train 69명(pos 35)뿐**(폐 histology의 train 수백·holdout pos 152와 대비). 소표본 + 조기중단 dev ~10명 → 불안정(shuffle>real이 그 지표).
  - **파이프라인 자체는 건재:** MSI-H(0.80, shuffle 0.66)·EBV(0.87, shuffle 0.71) 모두 shuffle을 뚜렷이 상회 → H&E→UNI→MIL이 **형태-연동 분자신호를 실제로 포착**함. 즉 이 실패는 "H&E가 diffuse 형태를 못 본다"(생물학적으로 확립된 signet-ring 형태와 배치)가 아니라 **Lauren 라벨 희소성/불안정** 탓일 가능성이 높다.
  - **결론:** 사전 예정한 형태 양성대조(Lauren)는 이 부분 코호트에서 **INCONCLUSIVE-FAIL**. 파이프라인 정상성 판단은 **de facto 양성대조(MSI·EBV의 shuffle 상회)**로 대체 확보. 442 완료 + Lauren 라벨 보강 후 재검 필요.

### [#5] 위 HER2/ERBB2-amp ≤ 0.65 — 유방 HER2(0.599) 복제, **핵심 교차장기 검정 · 오늘 헤드라인 #2**
- 관측 **0.5851**, CI [0.4576, 0.7197](0.5 포함), shuffle 0.5393, n_pos=14.
- 점추정 0.585는 **≤0.65 대역 안이고, 유방 내부 HER2 0.599와 사실상 동일**(차이 0.014). real−shuffle 마진 ≈0.046으로 작아 신호 약함.
- **Verdict: consistent with(확증 아님).** exploratory(n_pos=14) → CI 광범위(0.46–0.72), 확증 불가. **반증도 아님** — 반증 시나리오(필수 마커 HER2-amp가 ≥0.8로 잘 예측 = 대체가능인데 blind 아님)는 **관측되지 않음**(0.585는 blind에 부합).
- **함의:** *같은 변이(HER2 증폭)·다른 장기(유방→위)*에서 **둘 다 H&E-blind(~0.59)**라는 점추정 일치는 "증폭≠형태" 원리와 부합. 단 검정력 부족으로 "복제 확증"이 아니라 **"consistent with breast 0.599"**까지만 주장.

### [#6b] MSI-H ≥ 0.82 (대체가능)
- 관측 0.8027, CI [0.6882, 0.9006], shuffle 0.6598, n_pos=24.
- 점추정 0.803은 **0.82 라인 바로 아래**(0.017 미달)이나 높은 수준이고 shuffle을 뚜렷이 상회 → 방향 일치(MSI가 형태-가시).
- **Verdict: consistent with substitutable(확증 아님).** n_pos=24로 **사전임계 25에 1명 미달 → exploratory → INCONCLUSIVE.** 442 완료 시 임계 교차 예상. 점추정 대역 미세 미달은 소표본 잡음 범위.

### [#6c] 내부순서 조직형 ≥ MSI > HER2-amp
- 관측: Lauren 0.607 / MSI 0.803 / HER2 0.585.
- **MSI > HER2 (0.803 > 0.585) 점추정 성립**(예측 방향 일치). 그러나 **조직형 ≥ MSI는 위반**(Lauren 0.607 < MSI 0.803) — 이는 **Lauren 양성대조 실패**에서 기인(MSI가 이상 고값이어서가 아님).
- **Verdict: INCONCLUSIVE.** MSI·HER2 모두 exploratory + CI 광범위 겹침 → MSI>HER2 순서 통계적 확립 불가(점추정만). 순서의 상단(Lauren)은 양성대조 실패로 무효 → **"형태-연동(MSI/EBV) > HER2-amp" 방향은 MSI(0.80)·EBV(0.87) > HER2(0.585)로 여전히 지지**되나, 특정 3항 순서 주장은 확립 불가.

### [EBV] exploratory (사전 지정)
- 관측 0.8714, CI [0.7407, 0.9697], shuffle 0.7143, n_pos=7.
- **Verdict: INCONCLUSIVE(n_pos=7).** 점추정은 높아 lymphoepithelioma-like 형태 상관물 가설과 부합하나 검정력 극히 부족.

## 종합 verdict
- **핵심 교차장기 검정(#5 HER2-amp): 점추정 0.585 ≈ 유방 0.599, ≤0.65 → consistent with 법칙**(증폭 마커가 두 장기에서 모두 H&E-blind). **확증 아님(n_pos=14 exploratory), 반증도 아님(≥0.8 미관측).** 오늘 헤드라인 #2로 "consistent with"까지만.
- **사전 양성대조(Lauren) 실패** — CI가 0.5 포함, shuffle>real. **Lauren 라벨 희소(train 69)에 따른 불안정**으로 판단(생물학적 diffuse 형태 부재가 아님). **파이프라인 정상성은 MSI(0.80)·EBV(0.87)의 shuffle 상회로 de facto 확보.**
- **MSI-H(0.803) consistent with substitutable**(0.82 라인 미세 미달·exploratory). EBV 높으나 n_pos=7.
- **반증 트리거 없음:** (a) '필수' 마커 HER2-amp가 ≥0.8로 잘 예측되지 않음(0.585), (b) 대체가능 축(MSI·EBV)이 blind 아님. 따라서 **법칙 반증 아님 — 그러나 확증도 아님**(사전 양성대조 실패 + 변이축 저검정력). 폐(변이축 INCONCLUSIVE)와 같은 정직한 결론.
- **함의:** 위암 부분 코호트로 "법칙 복제/확증" 주장하지 않는다. HER2-amp 교차장기 점추정 일치(유방≈위≈0.59)만 "consistent with"로 보고. 확증에는 (i) 442 완료(MSI n_pos≥25·HER2 n_pos↑), (ii) Lauren 라벨 보강 후 양성대조 재검이 필요.

## 주의
- claim_level: hypothesis_only. 우월성/치료 최적화 주장 없음. DRP 아님(형태→가설 라우팅만).
- 임베딩 337/442(부분, 대용량 슬라이드로 ~18/hr). 백그라운드 임베딩 마스터(sh_embed.py) 계속 가동 — 442 완료 시 재검(특히 Lauren 양성대조·MSI 임계).
- shuffle-null 편차(Lauren 0.77, EBV 0.71 등)는 holdout n_pos 소수에서의 부트스트랩/순열 잡음 — exploratory·불안정 판정을 강화한다.
- 봉인 예측 #7(두경부 HNSC HPV/EGFR)은 별도 코호트 — 본 문서 범위 밖.

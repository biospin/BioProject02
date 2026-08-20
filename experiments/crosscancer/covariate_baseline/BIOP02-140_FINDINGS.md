# BIOP02-140 v1 — 폐 공변량 기준선 · 증분가치 (KRAS/EGFR/histology)

`claim_level: hypothesis_only` · `critic_status: pending` · jamie, 2026-08-20
방법론 = `COVARIATE_BASELINE_PREREGISTRATION.md`(결과 전 고정, 실행 중 발견한 정정 1건 포함).
스크립트: `fetch_covariates_lung.py`(공변량 조회) → `audit_covariate_incremental_value.py`(분석).
전량 CPU, 재학습 없음(기존 임베딩·`mil_cost_results.json` H&E 예측값 재사용).

## v1 범위

티켓 본문의 완화 옵션대로 **폐(LUNG_NSCLC) 한 암종, KRAS·EGFR·histology_lusc 세 엔드포인트**만.
대장·위·두경부는 후속 카드(BIOP02-139가 HPV/grade_high/ERBB2_amp를 스킵한 것과 같은 판단).

## 공변량

purity(ABSOLUTE, Aran 2015 — 매칭 961/1050) · stage(cBioPortal AJCC, I/II/III/IV, 매칭
993/1050) · 해부학적 부위(ICD_O_3_SITE lobe, 매칭 996/1050) · cohort(LUAD/LUSC, 기존 라벨,
histology_lusc 엔드포인트에는 순환논리 방지로 제외). **grade는 실측 커버리지 0/1050으로 확인 후
제외**(TCGA 폐 임상데이터셋 자체에 없음 — 체리피킹 아님, `fetch_covariates_lung.py` 실행 로그가
근거). 결측은 전부 own category(대체·보간 없음).

## 방법 정정 1건 (실행 중 발견, 결과 계산 전)

원안은 공변량 모델을 `split.csv` train으로 학습→holdout 평가였는데, H&E 예측값
(`mil_cost_results.json`의 `patient_proba`)이 **holdout에만 존재**해 결합모델을 이 방식으로
학습할 수 없음을 `KeyError`로 발견했다(이 시점까지 AUROC 미계산). **holdout 271명 안에서
5-fold StratifiedKFold(seed=42) out-of-fold**로 방법을 바꿔 재등록 후 실행 — 전체 n·n_pos는
원안과 동일해 검정력 손실 없음. 상세 = 사전등록 문서 "정정" 절.

## 결과

| 엔드포인트 | n_pos | H&E-only(인용) | 공변량-only | 결합(공변량+H&E) | ΔAUROC (95% CI) | 판정 |
|---|---|---|---|---|---|---|
| histology_lusc (양성대조) | 153 | 0.939 | **0.586** (0.516–0.654) | 0.931 (0.895–0.962) | **+0.345** (0.278–0.415) | 🟢 유지 |
| egfr_activating | 15 | 0.852 | **0.816** (0.700–0.906) | 0.881 (0.766–0.952) | +0.065 (0.006–0.127) | **판정 불가**(n_pos<25) |
| kras_g12c | 14 | 0.681 | **0.802** (0.738–0.854) | 0.801 (0.739–0.855) | **−0.0004** (−0.009–0.007) | **판정 불가**(n_pos<25) **+ 🔴 공변량-only가 H&E 이상** |

**cohort(LUAD/LUSC) 단일공변량 검증** (티켓 본문 인용 "조직형만으로 예측하면 0.793" 확인):
kras_g12c 단독 cohort 모델 AUROC **0.7795**(5-fold OOF) — 티켓이 인용한 0.793과 방향·크기가
일치(정확히 같은 방법으로 낸 숫자가 아니라 소수점은 다르지만, **결론은 재현됨**). egfr_activating
cohort 단독 = 0.7173.

## 읽기

1. **양성대조 통과** — histology_lusc는 공변량-only가 거의 무작위(0.586)인데 H&E를 더하면
   즉시 0.931로 뛴다(ΔCI가 0을 크게 벗어남). 파이프라인이 정상 작동하고, 결합모델·부트스트랩
   설계 자체가 신뢰할 만하다는 증거.
2. **KRAS는 티켓의 우려보다 더 나쁘다.** 티켓은 "조직형만으로 0.793 vs H&E 0.681"을 반증으로
   들었는데, **purity·stage·site·cohort를 전부 합친 공변량-only 모델이 0.802**로 H&E(0.681)를
   더 크게 앞선다. 게다가 H&E를 공변량 위에 얹어도(결합모델 0.801) **사실상 아무것도 더하지
   않는다**(Δ=-0.0004, CI가 0을 딱 걸치고 거의 대칭). **H&E가 KRAS 상태에 대해 공변량(주로
   조직형)이 이미 아는 것 이상을 읽는다는 증거가 없다.**
3. **EGFR은 방향은 비슷하지만 덜 극단적이다.** 공변량-only(0.816)가 H&E-only(0.852)에
   근접하고, ΔAUROC CI([0.006, 0.127])는 형식상 0을 배제하지만 **n_pos=15로 프로젝트 자체
   기준(`LAW_HELDOUT_SCOREBOARD.md`, n_pos<25→exploratory)에 못 미쳐 사전등록 규칙대로
   "판정 불가"로 보고한다.** CI 하한이 0.006으로 0에 거의 붙어 있다는 것 자체가 표본이
   작다는 신호이지, 신뢰할 만한 양의 증분이라는 신호가 아니다.
4. **순도 층화(둘 다 층당 n_pos 5~10, 참고용):** egfr는 고순도(0.862)·저순도(0.842) 거의
   차이 없음. kras는 고순도(0.756)·저순도(0.595, 거의 무작위)로 갈리는데 — **표본이 너무
   작아 확증할 수 없지만**, 만약 실재한다면 "KRAS의 약한 H&E 신호가 있다면 고순도 샘플에
   집중돼 있다"는 가설과 방향이 맞는다. 판정에는 쓰지 않음(사전등록 n_pos<5 하한은 안
   걸렸지만 여전히 매우 작은 표본).

## 결정지도 제안 (독립 리뷰 대기, jamie 임의 반영 아님)

- **kras_g12c: 🔴로 본문 명시 권장.** "H&E가 KRAS 상태를 예측한다"가 아니라 "공변량(조직형
  주도)이 예측하고 H&E는 그 위에 추가 정보가 없다"로 서술을 바꿔야 함 — 데이터가 이걸
  지지한다(위 3번).
- **egfr_activating: 판정 보류, 결정지도 변경 안 함.** 방향은 kras와 같지만(공변량이 대부분
  설명) 표본이 너무 작아 🟡 강등을 단정할 근거는 아니다. Paper C 본문에 "탐색적, 표본 부족"
  각주는 필요.
- **histology_lusc: 변경 없음(원래 양성대조).**

## DoD 체크

- [x] 공변량 기준선 모델 정의·문서화 (결과 보기 전) — `COVARIATE_BASELINE_PREREGISTRATION.md`
- [x] 엔드포인트별 기준선/H&E/결합 AUROC 표 — 위
- [x] ΔAUROC + CI (bootstrap) — 위
- [x] 순도 층화 결과 — 위(표본 작음, 참고용)
- [x] 결정지도에서 강등할 칸 목록 — kras_g12c(🔴 권고), egfr_activating(보류)
- [ ] **독립 리뷰: 지용기(braveji)** — 아직

## 스킵/후속

- 폐 이외 4개 암종(대장·위·두경부 + 유방 anchor)은 v1 범위 밖 — 별도 카드로 분리 제안.
- LUAD-only 부분집합(조직형 혼합효과 배제) 정밀해부는 v1에서 안 함 — egfr/kras 표본이 이미
  n_pos 14~15인데 LUAD로만 좁히면 더 줄어 무의미할 가능성 높음. 필요하면 후속 요청.

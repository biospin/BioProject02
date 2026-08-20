# BIOP02-140 공변량 기준선 — 방법론 사전등록 (v1, 폐 한정)

`claim_level: hypothesis_only` · 작성 2026-08-20, jamie · **결과를 보기 전에 고정**(DoD 1번 항목).

## 범위 (v1)

티켓 본문이 명시한 부담 완화 옵션을 사용: **폐(LUNG_NSCLC) 한 개 암종만, KRAS·EGFR·histology 세
엔드포인트.** 이유는 티켓이 이미 준 것과 같다 — 반증(KRAS 0.681 vs 조직형-only 0.793)이 이미 여기
있고, 티켓 본문 4번 항목("폐 KRAS/EGFR 정밀 해부")도 폐부터 시작하라고 명시한다. 대장·위·두경부는
후속 카드로 분리(BIOP02-139가 HPV/grade_high/ERBB2_amp를 스킵한 것과 같은 판단).

## 공변량 정의 (신규 데이터 fetch 필요분만)

| 공변량 | 출처 | 커버리지(폐, n=1051 중) | 처리 |
|---|---|---|---|
| 종양순도 | ABSOLUTE purity (Aran et al. 2015, *Nat Commun* 6:8971) — `TCGA_mastercalls.abs_tables_JHU_UCSC.txt`, GDC file id `4f277128-f793-4354-a13d-30cc7fe9f6b5` | 확인 예정(fetch 스크립트가 join 후 보고) | 연속값, StandardScaler. 환자당 첫 매칭 tumor(`-01`) 샘플. 결측 환자는 "missing" 이진 플래그 + 값은 0으로 대체(모델이 결측을 별도로 학습하도록 — 값 추정/보간 안 함) |
| 조직형(cohort, LUAD/LUSC) | 기존 `patient_labels.csv`의 `cohort` 컬럼(이미 있음, 신규 fetch 아님) | 100% | **egfr_activating·kras_g12c에는 포함.** **histology_lusc에는 제외**(그 자체가 라벨이라 포함하면 순환논리) |
| stage | cBioPortal `AJCC_PATHOLOGIC_TUMOR_STAGE` (luad/lusc_tcga_pan_can_atlas_2018, PATIENT-level) | 실측: LUAD 512/1026, LUSC 484/969 (약 절반) | `STAGE IA/IB→I`, `IIA/IIB→II`, `IIIA/IIIB→III`, `IV→IV`(하위구분 접미사 제거, 표준 관행). 결측은 own category `"missing"`(대체 없음) — one-hot, `missing` 포함 |
| 해부학적 부위 | cBioPortal `ICD_O_3_SITE` | 실측: LUAD 514/1026, LUSC 485/969 | ICD-O-3 lobe 코드 그대로 category화(C34.0 주기관지/C34.1 상엽/C34.2 중엽/C34.3 하엽/C34.8 중복/C34.9 NOS). 결측은 own category `"missing"` |
| grade | cBioPortal `GRADE` | **실측 0/1026, 0/969 — 폐 코호트에 전혀 없음**(TCGA 폐 임상 데이터셋 자체가 등급을 안 매김, 유방과 다른 관행) | **v1에서 제외.** 체리피킹 아님 — 사전 실측으로 커버리지 0% 확인 후 배제(코드로 확인, 근거 = fetch 스크립트 출력 로그). 남는 4종(폐 이외 암종 포함) 카드 후속에서 필요 시 재확인 |

## 기준선 모델

- `sklearn.linear_model.LogisticRegression(max_iter=2000, C=1.0)`, 범주형은 one-hot(결측 포함),
  연속값(purity)은 `StandardScaler`.
- **학습**: 기존 `split.csv`의 `train` 환자만. **평가**: 기존 `mil_cost_results.json`의
  `patient_proba` 키 집합(= site-disjoint holdout, val+test pooled, n=271) — H&E 모델과 정확히
  같은 평가 대상이라야 비교가 성립한다.
- 결측으로 인한 환자 제외 없음(missing category가 흡수) — 안 그래도 n_pos 14~15인 표본을 더
  줄이지 않기 위해서다.

## 증분가치(핵심 지표)

- **결합모델** = 공변량 + H&E 예측확률(`mil_cost_results.json`의 `patient_proba`, 단일 실수
  피처로 추가) → 같은 LogisticRegression, 같은 train/holdout.
- **ΔAUROC = AUROC(결합모델, holdout) − AUROC(공변량-only, holdout)**.
- **CI**: paired bootstrap, n=1000·seed=42(`run_mil_cost.py`의 `bootstrap_auc` 컨벤션과 동일
  n/seed) — 매 반복에서 **같은 재표집 인덱스**로 두 AUROC를 계산해 차이를 내는 방식(두 모델의
  공유 표본변동을 상쇄하기 위해 독립 bootstrap이 아니라 paired로 함). `기존 run_mil_cost.py`의
  `bootstrap_auc()`를 단일 AUROC 계산에 그대로 재사용.

## 순도 층화

- 층화 기준은 **holdout 집합(n=271) 안에서** 계산한 purity 중앙값(**train이 아니라 holdout** —
  층화의 목적이 holdout 안에서 성능이 갈리는지를 보는 것이므로). 동점은 저순도 쪽으로.
- 층별로 H&E-only bootstrap AUROC(`run_mil_cost.py` 컨벤션 재사용) 계산.
- **사전에 박아두는 검정력 하한**: 층별 `n_pos < 5`면 AUROC 점추정을 계산하되 **"검정력 부족,
  판정 불가"로만 보고**하고 🟢/🟡/🔴 판정에 쓰지 않는다. egfr_activating(n_pos=15)·kras_g12c
  (n_pos=14)는 전체가 이미 프로젝트 자체 기준(`LAW_HELDOUT_SCOREBOARD.md`, n_pos<25→exploratory)
  에 못 미치므로, 층화하면 층당 7명 안팎 — **결과가 어떻게 나오든 이 두 엔드포인트의 층화는
  "판정 불가"로 보고될 가능성이 높다는 걸 미리 밝혀둔다**(사후 정당화 방지, 결과를 보고 이
  하한을 바꾸지 않는다).

## 판정 규칙 (티켓 본문 그대로, 결과를 보기 전에 재확인)

| 결과 | 결정지도 영향 |
|---|---|
| ΔAUROC의 95% CI가 0을 배제 | 🟢 유지 |
| ΔAUROC의 95% CI가 0을 포함 | 🟡 강등 — "H&E가 예측"이 아니라 "공변량이 예측" |
| 공변량-only AUROC 점추정이 H&E-only(mil_cost의 `real.auc`) 점추정보다 높음 | 🔴 본문 명시 |

**검정력 부족(층 n_pos<5, 또는 전체 n_pos<25)이면 위 표를 적용하지 않고 "판정 불가"로만 보고**
— 이건 결과를 보기 전에 정하는 규칙이지, 약한 신호를 가리려는 사후 조치가 아니다.

## 히스토리 검증 대상 (사전등록)

티켓 본문이 인용한 "조직형만으로 예측하면 0.793"은 **아직 코드로 확인된 수치가 아니다**
(CLAUDE.md 금지사항 — 발표/티켓 텍스트의 숫자를 그대로 근거로 쓰지 않는다). 이 사전등록이 끝난
직후 첫 번째로 계산할 값 = "cohort(LUAD/LUSC) 단일 공변량 → kras_g12c 예측 AUROC, 위와 동일한
train/holdout". 이 값이 0.793과 다르게 나와도(더 높든 낮든) **있는 그대로 보고**하고, 티켓 본문
수정은 별도로 제안한다.

## ⚠️ 정정 (2026-08-20, 실행 중 발견 — 결과를 보기 전) — train/holdout 분리 방법 변경

원안(공변량 모델을 `split.csv`의 train으로 학습, holdout으로 평가)을 실행하다 `mil_cost_results.json`
의 `patient_proba`가 **holdout(val+test)에 대해서만 저장돼 있고 train 환자에 대한 H&E 예측값은
존재하지 않는다**(재학습 없이는 만들 수 없음, GPU 필요 — v1 CPU-only 스코프 밖)는 걸
`KeyError`로 확인했다. **이 시점까지 AUROC·ΔAUROC 어떤 수치도 계산되지 않은 상태**였다 — 약한
결과를 보고 방법을 바꾼 게 아니라, 방법 자체가 데이터 가용성 때문에 애초에 불가능했다는 걸
첫 실행에서 잡은 것이다.

**수정된 방법**: 공변량-only 모델과 (공변량+H&E) 결합모델 둘 다 **holdout 271명 안에서
5-fold StratifiedKFold(seed=42)** 교차검증으로 학습·평가한다(폴드 안에서 공변량 모델을 4/5로
학습 → 나머지 1/5 예측, 5개 폴드 풀링해 out-of-fold AUROC). H&E 예측값은 이미 고정된 값(재학습
없이 피처로만 사용)이라 이 설계는 "고정된 블랙박스 점수 위에 공변량이 얼마나 더하는가"를 측정하는
표준적 방법이고, 전체 n(271)·n_pos(14~15)는 원안과 동일해 검정력 손실이 없다. `train_ids`(원래
`split.csv`의 train)는 이 비교에서 더 이상 쓰지 않는다. 판정 규칙·순도 층화·검정력 하한은
변경 없음.

## 재사용

- `run_mil_cost.py`의 `bootstrap_auc()` — 그대로 import.
- `mil_cost_results.json`의 `patient_proba` — H&E 예측확률 원천, 재계산 안 함.
- `patient_labels.csv`/`split.csv` — 기존 라벨·split, 변경 없음.
- 신규: purity/stage/site fetch만 (grade는 위에서 실측 후 배제).

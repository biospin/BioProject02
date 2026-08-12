# BIOP02-139 — 라벨 품질 민감도 분석 (v1)

> [Paper C] #6 라벨 품질 민감도 분석. "모델이 못 맞히는 것"과 "라벨이 틀린 것"을 분리하는 카드.
> **v1 범위**: 제2의 assay 소스가 실제로 존재하는 두 축(MSI, 변이 VAF)만 다룬다.
> 방법·기준은 결과를 보기 전에 [`EXCLUSION_CRITERIA_PREREGISTRATION.md`](./EXCLUSION_CRITERIA_PREREGISTRATION.md)에 사전등록했다.
> 기존 임베딩·라벨·예측점수 재사용, 신규 데이터·재학습 없음. GPU 불요.

## 1. 엔드포인트별 assay source 분포표

| 엔드포인트 | 정본 소스 | 제2 소스 | 둘 다 있는 환자 |
|---|---|---|---|
| GASTRIC_STAD `msi_h` | MSI_SENSOR_SCORE ≥3.5 | MSI_SCORE_MANTIS ≥0.4 (Kautto 2017/Bever 2018) | 437 |
| LUNG_NSCLC `kras_g12c` | WES 콜(p.G12C) | 콜의 VAF | 양성 70건 전부 |
| LUNG_NSCLC `egfr_activating` | WES 콜(activating 패턴) | 콜의 VAF | 양성 61건 전부 |
| COLORECTAL `braf_v600e` | WES 콜(p.V600x) | 콜의 VAF | 양성 48건 전부 |

HPV(HNSC)·grade_high(HNSC)·ERBB2_amp(GASTRIC)는 cBioPortal에 제2 소스가 없어(단일 curated SUBTYPE/GISTIC 콜) 이번 라운드에서 스킵했다. 후속 카드에서 TCGA 원본 clinical biotab까지 내려가 p16 IHC 등 별도 필드 존재 여부를 확인해야 한다.

## 2. MSI 라벨 원천 간 일치도

| 지표 | 값 |
|---|---|
| 둘 다 있는 환자 | 437 |
| 일치 | 436 |
| 불일치 | 1 |
| 일치율 | 0.9977 |
| Cohen's κ | 0.9925 |

**두 알고리즘이 사실상 완벽하게 일치한다.** MSIsensor와 MANTIS는 서로 다른 통계 기법으로 같은 microsatellite 불안정성을 재는데, 이 코호트에서는 임계값(각각 3.5·0.4) 근방에서 거의 갈라지지 않았다.

## 3. 변이 콜 VAF 분포

| 엔드포인트 | 양성 n | VAF<0.05 | VAF<0.10 | VAF<0.15 | 중앙값 |
|---|---|---|---|---|---|
| kras_g12c | 70 | 0 | 1 | 3 | 0.351 |
| egfr_activating | 61 | 0 | 2 | 11 | 0.289 |
| braf_v600e | 48 | 0 | 0 | 2 | 0.333 |

**저-VAF(<0.05) 콜이 세 endpoint 모두 0건이다.** TCGA MC3 파이프라인이 공개 이전에 이미 품질 필터를 거친 콜만 내놓기 때문으로 보인다 — 이 데이터에는 "명백히 신뢰도 낮은 변이 콜"이 애초에 거의 남아있지 않다.

## 4. 제외 전/후 AUROC 대조 (부트스트랩 95% CI, n=1000, seed=42)

| 엔드포인트 | 제외 수 (홀드아웃 기준) | AUROC 전 | AUROC 후 |
|---|---|---|---|
| `msi_h` | 0 / 107 | 0.8602 [0.768, 0.936] | 0.8602 [0.768, 0.936] (변화 없음, 제외 대상이 홀드아웃에 없었음) |
| `kras_g12c` | 1 / 271 | 0.6809 [0.569, 0.784] | 0.6983 [0.602, 0.797] |
| `egfr_activating` | 1 / 271 | 0.8514 [0.731, 0.955] | 0.8408 [0.710, 0.947] |
| `braf_v600e` | 0 / 151 | 0.8676 [0.786, 0.940] | 0.8676 [0.786, 0.940] (변화 없음) |

## 5. 해석

**이 두 축에서는 "판정"이 서지 않는다 — 제외 대상 자체가 거의 없기 때문이다.** 사전등록한 판정 기준(§ EXCLUSION_CRITERIA_PREREGISTRATION.md)이 미리 밝혔듯, 이런 경우 과잉 해석하지 않는다:

- MSI·BRAF는 홀드아웃 안에 제외 대상이 **0명**이라 전/후가 정의상 동일하다.
- KRAS·EGFR도 홀드아웃 안 제외 대상이 **1명**뿐이라, AUROC가 0.02 안팎 움직인 것은 방향조차 의미를 부여할 표본 크기가 아니다(KRAS는 오르고 EGFR은 내렸다 — 부호가 엇갈리는 것 자체가 표본 1명의 잡음이라는 뜻).

**그런데 이 "제외할 게 없다"는 사실 자체가 정보다.** 티켓이 예시로 든 폐 KRAS(AUROC 0.681, INCONCLUSIVE)의 근접-0에 가까운 성능이, 적어도 **MSI 원천 불일치**나 **저-VAF 저신뢰 콜** 때문은 아니라는 뜻이다 — 그런 라벨 잡음이 이 코호트에 거의 없다. 티켓이 제시한 두 갈래 해석("모델이 못 맞히는가" vs "라벨이 틀렸는가") 중, 적어도 이 두 축에 한해서는 후자를 뒷받침하는 증거가 나오지 않았다.

**한계**: 이건 라벨 품질의 전부를 본 게 아니라 두 개의 좁은 축(MSI 알고리즘 간 불일치, 변이 콜 VAF)만 본 것이다. 폐 KRAS의 근접-0이 이미지 한계인지 다른 종류의 라벨 문제(예: WES 자체의 커버리지 결손, 병리 슬라이드-유전형 매칭 오류)인지는 여전히 열려 있다. HPV·grade_high·ERBB2_amp는 제2 소스가 아예 없어 이번에 손도 못 댔다.

## 6. 결정지도 재분류 판정

이번 v1 범위(MSI, 변이 VAF)에서는 **"라벨 품질 제약"으로 재분류할 칸이 없다** — 라벨 잡음의 증거 자체가 나오지 않았기 때문이다(위 §5). 근접-0 칸(폐 KRAS 등)은 여전히 "예측 불가"로 남는다.

## 7. 완료조건(DoD) 대조

- [x] 엔드포인트별 assay source 분포표 (§1)
- [x] 불확실 라벨 정의·제외 기준 문서화, 결과 보기 전 확정 (`EXCLUSION_CRITERIA_PREREGISTRATION.md`)
- [x] 제외 전/후 AUROC 대조표, 부트스트랩 CI 동반 (§4)
- [x] 두 assay 병존 환자에서 일치율·κ (§2, MSI만 — 변이는 "일치도" 개념이 아니라 VAF 신뢰도 축이라 성격이 다름)
- [x] 결정지도 칸 재분류 판정 (§6 — 이번 범위에서는 없음)
- [ ] 독립 리뷰: 박세진(sezinie000) — 재계산 라인 (**미착수, 요청 필요**)
- [ ] HPV·grade_high·ERBB2_amp (제2 소스 부재로 v1 범위 밖, 후속 카드)

## 산출물

`experiments/crosscancer/label_quality/`: `fetch_assay_sources.py`(원값 fetch, 판정 없음) · `EXCLUSION_CRITERIA_PREREGISTRATION.md`(사전등록) · `audit_label_quality_sensitivity.py`(제외 전/후 대조) · `msi_dual_score.csv` · `mutation_vaf.csv` · `label_quality_sensitivity_results.json`.

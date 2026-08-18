# BIOP02-139 라벨 품질 민감도 분석 — 제외 기준 사전등록

> 이 문서는 AUROC 재계산(전/후 대조) **이전에** 작성한다(DoD 요구사항: "불확실 라벨 정의·제외 기준 문서화 — 결과 보기 전에 확정"). `fetch_assay_sources.py`가 받아온 원값(`msi_dual_score.csv`, `mutation_vaf.csv`)의 **분포·존재 여부**는 확인했지만, 그 값을 라벨 제외에 반영했을 때 AUROC가 어떻게 바뀌는지는 이 문서를 커밋하기 전까지 계산하지 않았다.

## 범위 (BIOP02-139 v1)

Jira 티켓 원문이 예시로 든 HER2/MSI/HPV/변이 네 갈래 중, 이번 라운드는 **제2의 assay 소스가 실제로 존재하는 두 갈래만** 다룬다(사전 조사 근거는 코멘트 참조).

| 엔드포인트 | 제2 소스 | 제외 대상 |
|---|---|---|
| GASTRIC_STAD `msi_h` | MSI_SCORE_MANTIS (기존 라벨은 MSI_SENSOR_SCORE) | 두 알고리즘 판정이 불일치하는 환자 |
| LUNG_NSCLC `kras_g12c`, `egfr_activating` | 변이 콜의 VAF (tumorAltCount/(Alt+Ref)) | VAF가 낮아 콜 신뢰도가 낮은 양성 |
| COLORECTAL `braf_v600e` | 〃 | 〃 |

HPV(HNSC)·grade_high·ERBB2_amp는 cBioPortal API에 제2의 assay 소스 자체가 없어(단일 curated 소스) 이번 라운드에서 제외했다 — 결측 처리 정책만 문서화하고 후속 카드로 넘긴다(아래 "스킵한 것" 참조).

## 제외 기준

### MSI (GASTRIC_STAD)

- 기존 라벨: `MSI_SENSOR_SCORE >= 3.5` → `msi_h` (스크립트 `sh_fetch_labels.py`가 이미 사용 중인 정의).
- 제2 소스: `MSI_SCORE_MANTIS >= 0.4` — MANTIS 원 논문(Kautto et al. 2017, *Oncotarget*)과 후속 검증(Bever et al. 2018, *J Mol Diagn*)이 제시한 표준 MSI-H 컷오프.
- **제외 대상**: 두 판정이 불일치하는 환자(`msi_sensor 판정 ≠ mantis 판정`). 둘 다 값이 없는 환자는 기존과 동일하게 `has_msi=0`으로 애초에 라벨 없음 처리(제외 대상 아님, 애초에 포함 안 됨).
- 사전 확인한 분포(판정에는 미반영): 437명 중 436명 일치, 불일치 1명 — 원값 확인 결과 표로만 기록.

### 변이 (LUNG kras_g12c/egfr_activating, COLORECTAL braf_v600e)

- 기존 라벨: cBioPortal DETAILED mutation projection에서 `fetch_labels.py`의 분류기(`kras_g12c`/`egfr_activating`/`braf_v600e`)로 판정된 단백질 변화 패턴 양성.
- 제2 소스: 같은 콜의 VAF = `tumorAltCount / (tumorAltCount + tumorRefCount)`.
- **제외 대상**: 양성 콜 중 **VAF < 0.10**. 벌크 WES에서 subclonal/저신뢰 콜을 가르는 데 흔히 쓰이는 관행적 임계값(예: TCGA MC3 하류 분석에서 반복적으로 쓰이는 5~10% 구간의 보수적 끝)이며, 특정 임상 가이드라인이 정한 절대 기준은 아니라는 점을 명시한다. 음성(콜 없음)에는 VAF 개념이 없으므로 제외 대상에서 제외 — 이 축의 민감도 분석은 "양성 콜의 신뢰도"만 다룬다.
- 사전 확인한 분포(판정에는 미반영): egfr_activating 61건 중 VAF<0.10은 2건, kras_g12c 70건 중 1건, braf_v600e 48건 중 0건. VAF<0.05는 세 endpoint 모두 0건.

## AUROC 재계산 방법 (제외 전/후 대조)

- 정본 예측 점수: `experiments/crosscancer/<COHORT>/full/mil_cost_results.json`의 `endpoints.<ep>.real.patient_proba` (환자별 확률, 기존 holdout 평가와 동일 소스).
- 부트스트랩: `run_mil_cost.py`의 `bootstrap_auc(y, p, n=1000, seed=42)`와 동일한 컨벤션(퍼센타일법, n=1000, seed=42)을 그대로 재사용한다 — 새 컨벤션을 만들지 않는다.
- "전"은 holdout 전체, "후"는 위 제외 대상을 holdout에서 뺀 부분집합. 둘 다 같은 `patient_proba`에서 조회하므로 모델 재학습은 없다.

## 스킵한 것 (후속 카드로 이관)

- HPV(HNSC), grade_high(HNSC), ERBB2_amp(GASTRIC): cBioPortal clinical-attributes에 제2의 assay 소스가 없음(단일 curated SUBTYPE/GISTIC 콜). TCGA 원본 clinical XML/biotab까지 내려가야 p16 IHC 등 별도 필드를 찾을 수 있는지 확인 가능하나, 이번 라운드 범위 밖.

## 판정 기준 (결과 보기 전 확정)

- 제외 후 AUROC 신뢰구간이 제외 전과 실질적으로 겹치면(즉 유의한 변화 없으면) → "라벨 잡음으로 설명되지 않는다"로 읽는다. 이 축에서는 근접-0 결과가 이미지 한계 쪽에 더 가깝다는 정황.
- 제외 후 AUROC가 유의하게 오르면 → 라벨 잡음이 근접-0 결과에 일부 기여했다는 뜻으로 읽는다.
- 제외 표본 수가 극히 작을 경우(위 사전 분포 확인 결과 MSI 1건, 변이 최대 2건), 애초에 검정력이 없어 "판정 불가"로 정직하게 보고하고 과잉 해석하지 않는다.

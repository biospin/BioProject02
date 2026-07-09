# her2_pam50_label_qc_v0.1

Owner: jmryu
Issue: BIOP02-49 — [S2] HER2/PAM50 레이블 추출 + QC
Status: 완료 — split 재배정 없음 (split_hash 불변 확인, split_policy_v0 lock 준수)

## 배경

HER2/PAM50 라벨 자체의 추출·조인 로직은 BIOP02-38(kkkim, `build_manifest.py`)에서
이미 구현·커밋되어 `agents/data/manifests/tcga_brca_manifest.csv`에 반영되어 있었다.
본 작업(BIOP02-49)은 그 결과를 QC하고, `split_policy_v0.md` §라벨 정의가 요구하는
fold별 class 비율표를 생성하는 것이 목적이다.

## 발견한 버그

`build_manifest.py`의 `MISSING` 값 집합에 TCGA biotab의 표준 sentinel 값
`"[Not Evaluated]"`(IHC 검사 자체가 수행되지 않음)가 빠져 있었다. `is_label()`이
이 값을 "유효 라벨"로 오판해, 검사를 안 한 슬라이드가 `has_*=1`로 잘못 집계됐다.

| 컬럼 | 버그 영향 | 비고 |
|---|---|---|
| `has_her2` | 118/1010 슬라이드(11.7%) 오분류 (698이 맞는데 816으로 집계) | 가장 큰 영향 |
| `has_pr` | 1/1010 슬라이드 오분류 | |
| `has_er` | 이번 1010-슬라이드 서브셋엔 `[Not Evaluated]` 케이스가 없어 실제 영향 0 | 잠재 버그였으나 미발현 |
| `has_pam50` | 영향 없음 | 별도 로직(`PAM50_MISSING`)이며 Normal-like 제외(§4)는 이미 정확히 동작 |

다행히 실제 다운스트림 분석 스크립트(`compare_uni_conch.py`, `compare_models.py`)는
`has_her2` 플래그가 아니라 `her2_status` 원본 문자열을 직접 Positive/Negative로
필터링하고 있어(각 스크립트에 "Equivocal/Indeterminate/NotEval dropped" 주석 존재),
이미 병합된 BIOP02-53 등 모델링 결과가 이 버그의 영향을 받았을 가능성은 낮다.
버그는 manifest의 QC용 파생 컬럼과 split 메타 통계에 국한된다.

## 조치

1. `agents/data/scripts/build_manifest.py`: `MISSING`에 `"[not evaluated]"` 추가.
2. `write_split_meta()`에 `pr_balance_per_split` / `her2_balance_per_split` /
   `pam50_balance_per_split`을 추가 (기존엔 `er_balance_per_split`만 있었음 —
   `split_policy_v0.md` 118행이 요구하는 ER/PR/HER2/PAM50 4종 비율표를 충족).
3. 이미 커밋된 `tcga_brca_manifest.csv`의 `has_er/has_pr/has_her2/has_pam50/has_labels`
   파생 컬럼만 원본 `er_status/pr_status/her2_status/pam50` 문자열로부터 재계산해
   patch했다. **`case_id`/`slide_id`/`source_path`/`split` 컬럼은 손대지 않았다** —
   재계산 후 `split_hash`가 기존과 동일한 `5995f29d3978b831`임을 확인했으므로
   patient-level split 배정에는 영향이 없다 (split lock 정책 준수).
4. `split_manifest_meta.json`을 재생성해 새 fold별 balance 표를 반영했다.

## 교차검증 (독립 소스 대조)

- **HER2 vs raw TCGA biotab** (`clinical_patient_brca.txt`, cBioPortal 캐시):
  1010/1010 완전 일치 (mismatch 0) — manifest의 HER2 추출이 원본 소스에 충실함을 확인.
- **PAM50 vs cBioPortal `brca_tcga_pan_can_atlas_2018` (SUBTYPE)**: 겹치는 902명 중
  concordance 57.0% (514/902) — 상당한 불일치. TCGA PAM50 재산정 배치 간 불일치는
  문헌상 알려진 현상이지만, 이 수치는 manifest의 PAM50이 pan-can atlas 2018과는
  **다른** cBioPortal study(예: 원 TCGA-BRCA 2012 study, Parker 2009 classifier
  초기 버전)에서 왔을 가능성을 시사한다. **현재 리포에는 kkkim이 BIOP02-38에서
  사용한 원본 `--pam50` CSV가 커밋되어 있지 않아(로컬 파일) 정확한 source study_id를
  재확인할 수 없었다.**

## 남은 리스크 / 후속 조치 제안

1. **PAM50 소스 재확인 필요** — kkkim에게 원본 `--pam50` CSV의 cBioPortal study_id를
   확인 요청하고, 그 파일을 `agents/data/manifests/`에 커밋할 것을 제안한다.
   `split_policy_v0.md`의 "라벨 정의 단일 소스 고정(train/test 간 정의 드리프트 차단)"
   요구사항을 만족하려면 소스가 문서화·버전관리되어야 한다.
2. **모델링 코드 정합성 확인 필요** — `agents/modeling/scripts/train.py`,
   `train_mil.py`의 `PAM50_MAP`/`PAM50_CLASSES`가 Normal을 포함한 5-class로 정의되어
   있다. Data/manifest 레이어는 정책대로 Normal-like를 정확히 제외 중이지만(§4 준수),
   모델링 코드가 여전히 Normal 클래스를 학습 대상에 포함한다면 정책과 어긋난다.
   BIOP02-49 범위(데이터/manifest) 밖이라 직접 수정하지 않았고, sjpark 확인이 필요하다.
3. **data-owner sign-off** — 새로 추가된 fold별 ER/PR/HER2/PAM50 balance 표
   (`split_manifest_meta.json`)를 `split_policy_v0.md` 118행에 따라 kkkim이 검토할 것.

## 변경 파일

- `agents/data/scripts/build_manifest.py`
- `agents/data/manifests/tcga_brca_manifest.csv` (파생 컬럼만 patch, split 불변)
- `agents/data/manifests/split_manifest_meta.json` (재생성)
- `agents/data/docs/her2_pam50_label_qc_v0.1.md` (본 문서)

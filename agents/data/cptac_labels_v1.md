# cptac_labels_v1 — CPTAC-BRCA 임상 라벨 매핑 + split 검증 (BIOP02-55)

담당: jamie (Data Agent) | 상태: 공식본 — BIOP02-53에서 만들어진 임시본을 대체함 (아래 "대체 관계" 참고)

## 목적

CPTAC-BRCA 외부검증 코호트에 ER/PR/HER2/PAM50 임상 라벨을 매핑하고, 환자(`case_id`)
단위에서 잠긴 TCGA-BRCA `split_policy_v0` 코호트와 겹치지 않는지 검증한다.
`split_policy_v0.md` §7 체크리스트에서 CPTAC 결과를 out-of-domain 평가로 신뢰하기 전에
요구하는 두 항목이다:

- **CPTAC 격리**: CPTAC 케이스가 TCGA train/val에 0건.
- **라벨 결측 처리 정책 일치**: `split_policy_v0.md` §4와 동일한 규칙을 적용해서,
  `has_er/has_pr/has_her2/has_pam50`가 두 코호트에서 같은 의미를 갖도록 함.

## 대체 관계

2026-07-03, kkkim(임베딩 담당 겸 리더)이 임시 CPTAC 라벨 파일
(`experiments/kkkim/20260703_cptac_labels/`, commit `039b93a`)을 만들었다.
Sprint 3(6/19~7/03) 마감 시점까지 이 Data Agent 산출물이 도착하지 않아 sjpark의
외부검증 평가(BIOP02-53)와 교차검증 registry(BIOP02-57)가 막혔기 때문이다. 그 파일의
결정 문서 자체에 "jamie의 공식 라벨 도착 시 대체"라고 명시돼 있고, 이 파일이 그 대체본이다.

**독립 교차검증**: kkkim도 동일한 공개 소스(`brca_cptac_2020`)와 동일한 ID 매핑 방식
(`01BR001` ↔ cBioPortal의 `X01BR001`)을 썼고, 결과도 같은 숫자(122명 중 120명 라벨 확보)로
나왔다. 이번 파일은 세 가지 지점에서 다르다:

1. **전체 IDC 이미징 코호트를 기준(anchor)으로 함** (`cptac_brca_idc_inventory.csv`,
   198명) — cBioPortal 122명 코호트만 보는 게 아니라, 이미징은 있지만 라벨이 없는
   78명도 명시적으로 함께 보고한다.
2. **결측 처리를 `split_policy_v0.md` §4 정책대로 함** (`has_er/has_pr/has_her2/
   has_pam50` boolean 플래그) — HER2 `Equivocal`이나 PAM50 `Normal-like` 값을 아예
   빈칸으로 지우지 않는다. 원본 값은 컬럼에 그대로 남기고, `has_*`로 해당 task에서
   쓸 수 있는지만 표시한다 — `tcga_brca_manifest.csv` / `build_manifest.py`와 동일한
   컨벤션이다.
3. **환자 단위 leakage 검증을 실제로 수행** — 잠긴 1010명 TCGA manifest
   (`tcga_brca_manifest.csv`, `split_hash=5995f29d3978b831`) 전체를 대상으로 확인했다
   (cBioPortal 122명 코호트만이 아니라).

kkkim의 파일과 그로부터 파생된 `/workspace/data/cache/biop02/
embedding_manifest_cptac_uni.csv`(395/653 슬라이드 라벨 채움)는 이 파일 기준으로
재생성이 필요하다. 임시 라벨로 이미 만들어진 `cross_validation_registry.jsonl`의
`critic_status: caution` 엔트리들도 재생성 후 재검토가 필요할 것 같다 (braveji / Critic 판단).

## 출처

- cBioPortal study `brca_cptac_2020` (Krug et al., Proteogenomic landscape of breast
  cancer, Cell 2020; PMID 33212010), 122 samples, 환자당 1 sample.
- 공개 REST API로 받음 (`GET .../clinical-data?clinicalDataType=PATIENT|SAMPLE`),
  캐시 위치: `agents/data/manifests/cptac_brca_clinical_raw_{patient,sample}.json`.
- 이미징 코호트 기준: `agents/data/manifests/cptac_brca_idc_inventory.csv`
  (198명, 653개 slide series — 이미 레포에 있는 파일, 다시 받지 않고 그대로 사용).

## Join key

cBioPortal은 숫자로 시작하는 환자 ID에 `X`를 붙인다(예: `X01BR001`). 이 접두어를
제거하면 레포에서 쓰는 `case_id`(`01BR001`)와 일치하고, `cptac_brca_idc_inventory.csv`와도
바로 맞는다. `CPT000814`, `CPT001846` 두 건은 다른 ID 체계를 쓰고 있어서 이 방식으로는
이미징과 매칭이 안 된다 — 그냥 버리지 않고 `join_key_resolved=no`, `has_imaging=no`로
표시해서 결과 파일에 남겨뒀다.

## 라벨 정규화

- **ER/PR/HER2 status**: 원본 값의 대소문자가 일관되지 않아서(`positive`/`Positive` 등)
  `.strip().capitalize()`로 정규화했다. 값 자체는 그대로 유지한다
  (`Positive`/`Negative`/`Equivocal`) — 아무것도 빈칸으로 지우지 않는다.
- **PAM50**: cBioPortal의 CPTAC 스터디는 HER2-enriched 클래스를 `Her2`로 표기하는데,
  TCGA 쪽 PAM50 소스(`split_policy_v0.md` §10)는 `HER2`로 표기한다. 두 코호트가 같은
  클래스 라벨을 쓰도록 `Her2` → `HER2`로 정규화했다 (kkkim의 임시 파일도 동일하게 처리함).
- **결측 처리** (`has_er/has_pr/has_her2/has_pam50`): `build_manifest.py`와 동일한
  `MISSING` / `PAM50_MISSING` 집합을 사용했다 — HER2 `Equivocal`과 PAM50 `Normal-like`는
  컬럼에 값은 남아있지만 `has_*=0`으로 표시된다.

## 코호트 구성

| 그룹 | case_id 수 |
|---|---:|
| IDC 이미징 코호트 (`cptac_brca_idc_inventory.csv`) | 198 |
| cBioPortal 임상 코호트 (`brca_cptac_2020`) | 122 |
| 합집합 (이 파일) | 200 |
| 이미징 + 사용 가능한 라벨 최소 1개 | 120 |
| 이미징만 있고 사용 가능한 라벨 없음 (`unlabeled_imaging_pool`) | 78 |
| 라벨은 있으나 이미징 매칭 안 됨 (`CPT0xxxxx` 체계) | 2 |

198명 이미징 코호트 기준, 엔드포인트별 라벨 보유 수 (`schemas/cv_registry.schema.json`
엔트리의 `n_test` 후보값으로 바로 쓸 수 있음):

| Endpoint | has_* == 1 (이미징 대상 중) |
|---|---:|
| er_status | 118 |
| pr_status | 113 |
| her2_status | 95 |
| pam50 | 115 |

이 수치가 BIOP02-57(braveji, 2026-07-08 댓글)의 `n_test` 블로커에 대한 답이다: CPTAC
외부검증 `n`은 653 슬라이드나 198명 같은 단일 숫자가 아니라 엔드포인트마다 다르다 —
TCGA 쪽에서도 `has_er/has_pr/has_her2/has_pam50`가 엔드포인트마다 다른 것과 마찬가지다.

## Split 검증 (§7 체크리스트)

- [x] **CPTAC 격리**: `set(cptac.case_id) & set(tcga_train_val_test.case_id) == {}`.
      잠긴 전체 manifest(`tcga_brca_manifest.csv`, 1010명,
      `split_hash=5995f29d3978b831`) 기준으로 확인 — **충돌 0건**.
      구조적으로 당연한 결과이긴 하다(서로 다른 코호트, 서로 다른 ID 네임스페이스:
      `TCGA-XX-XXXX` vs `01BRxxx`/`CPT0xxxxx`)이지만, 가정하지 않고 실제로 검증했다.
- [x] **Split 배정**: `split_policy_v0.md` §3에 따르면 "external test = CPTAC-BRCA
      전량" — CPTAC은 train/val/test로 나누지 않는다. 198명 이미징 코호트 전체가
      학습/튜닝에 노출되지 않는 외부 hold-out이다. 이 파일에 `split` 컬럼을 따로
      추가하지 않은 이유도 이것이다 (`has_imaging=yes`인 행은 항상 `external_test`가
      될 것이므로 의미가 없음).
- [ ] Site-disjoint 여부: CPTAC에는 해당 없음 — 단일 외부 코호트이므로 TCGA와의
      격리가 leakage gate이지, site 분할이 아니다.

## 남은 갭: 이미징은 있지만 라벨 없는 78명 (구조적 한계, 버그 아님)

이 갭을 메울 수 있는지 다른 공개 소스 2곳을 추가로 확인했으나, 둘 다 메우지 못했다:

- `breast_cptac_gdc` (cBioPortal, 2025, 154 samples, GDC/CDA 기반): ER/PR/HER2/PAM50
  필드 자체가 없음.
- GDC 프로젝트 `CPTAC-2` (Breast/Colon/Ovary, 134 breast cases): 198명 이미징 코호트와
  123명 겹치지만, 라벨 없는 78명 중 3명만 걸리고, GDC의 harmonized `diagnoses` 스키마에는
  수용체 상태/분자아형 필드가 아예 없음.

kkkim의 임시 파일 메모에 참고할 만한 단서가 있다: 78명 중 일부는 IDC
`series_description`(`cptac_brca_idc_inventory.csv`)이 `tumor_tissue`가 아니다 —
즉 일부는 정상조직(adjacent-normal) 슬라이드일 가능성이 있고, 그렇다면 애초에 종양
ER/PR/HER2/PAM50 라벨이 존재할 수 없는 케이스다. 이번 작업에서 환자별로 직접 검증하진
않았고, 갭을 더 좁히고 싶다면 후속 확인 항목으로 남겨둔다.

이 이상 갭을 메우려면 cBioPortal이나 GDC의 harmonized API로는 노출되지 않는 CPTAC
전용 임상/병리 파일(CPTAC 데이터 포털 / PDC 직접, 또는 dbGaP controlled access)이
필요할 것 같다 — 이번 작업 범위 밖이며, PDC GraphQL API는 이 작업 환경에서 접근이
안 됐다(타임아웃).

## 산출물

- `agents/data/manifests/cptac_brca_clinical_labels_v1.csv` — 이번 매핑 결과.
- `agents/data/manifests/cptac_brca_clinical_raw_{patient,sample}.json` —
  cBioPortal API 원본 캐시 (용량 작아서 `agents/data/README.md` 원칙대로 git에 포함).
- `agents/data/scripts/build_cptac_labels.py` — 재생성 스크립트 (`--refresh`로
  cBioPortal에서 다시 받을 수 있음).

## 다음 단계

1. kkkim/sjpark: `embedding_manifest_cptac_uni.csv` 재생성 + 이 파일 기준으로
   영향받은 `cross_validation_registry.jsonl` 엔트리 재실행.
2. braveji: 위 엔드포인트별 `n_test` 수치로 BIOP02-57 블로커 해소.
3. 78명 갭을 더 좁히는 게 우선순위가 되면, PDC 임상 데이터를 직접 받아보거나
   (접근 가능한 환경에서) 환자별 `series_description`을 확인해서 "애초에 종양
   슬라이드가 없는 경우"와 "정말 라벨만 없는 경우"를 구분해볼 수 있다.

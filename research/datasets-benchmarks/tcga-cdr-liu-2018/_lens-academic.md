# Academic Lens — Why TCGA-CDR over raw clinical files

## 문제 / The problem with raw clinical files
TCGA의 원본 임상 데이터(`clinical_patient_brca.txt`, follow-up XML 등)는 **암종마다
스키마가 다르고**, 동일 환자에 대해 enrollment 파일과 여러 follow-up 파일이 **상충**
하며, vital status·new-tumor-event·날짜 필드가 **불완전하거나 모순**된다. 여기서 직접
생존 라벨을 만들면 (a) 엔드포인트 정의가 분석자마다 달라지고 (b) censoring을 잘못 잡아
**event leakage / immortal-time bias**가 들어가기 쉽다.
Raw TCGA clinical files are schema-inconsistent across tumor types and internally
contradictory per patient; hand-deriving survival from them invites inconsistent
endpoint definitions and censoring errors.

## TCGA-CDR가 해결하는 것 / What TCGA-CDR fixes
Liu et al.는 33 enrollment + 97 follow-up 파일을 통합하며 **1,000건 이상의 품질 문제**를
명시적으로 해소하고, OS/PFI/DFI/DSS를 **단일하고 검증된 정의**로 못 박았다. 더 중요하게,
각 엔드포인트를 Cox PH·통계 검정으로 평가해 **"이 암종에서 이 엔드포인트는 쓰지 말라"**는
사용성 등급을 부여했다 — 이는 원본 파일에는 없는, 이 논문만의 기여다.
The decisive academic contribution is not just curation but **per-endpoint
usability guidance**: each (cancer type × endpoint) is graded as recommended,
use-with-caution, or not-recommended, backed by event counts and follow-up
adequacy. Raw files give numbers; TCGA-CDR gives **whether those numbers are
analyzable**.

## 왜 reviewer 방어에 중요한가 / Why it is a reviewer shield
npj Precision Oncology 같은 저널의 리뷰어는 "왜 BRCA에서 OS를 썼나? 이벤트가 부족하지
않나?"를 묻는다. TCGA-CDR을 인용하면 **PFI/DFI 선택이 임의가 아니라 정본 가이드라인을
따른 것**임을 입증할 수 있다. 또한 우리 코호트 라벨이 다른 TCGA 논문들과 **동일 정의**를
쓴다는 비교가능성(comparability)을 보장한다.
Citing TCGA-CDR converts an arbitrary endpoint choice into a **guideline-backed,
comparable, reproducible** one — directly answering the reviewer's "why this
endpoint / why this censoring" and aligning our labels with the wider TCGA
literature.

## BIOP02 적용 / Applied here
우리는 ER/PR/HER2(IHC)·PAM50(분자 아형) **phenotype** 라벨과 별개로 **outcome** 라벨이
필요하다. TCGA-CDR은 그 outcome 축의 **정본 ground truth**이며, BRCA에 대해 **PFI/DFI를
1차 생존 타깃**으로 고정하게 해준다 — 라벨 정의 단계에서의 leakage를 원천 차단한다.

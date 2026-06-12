# TCGA-CDR (Liu et al., 2018, *Cell*) — Core

**DOI** 10.1016/j.cell.2018.02.052 · **PMC** PMC6066282 · grounded via PMC (cell.com fulltext returns HTTP 403).

## 한줄 요약 / One-liner
The TCGA Pan-Cancer Clinical Data Resource (**TCGA-CDR**) harmonizes raw, messy
per-tumor clinical files into one curated table of **four survival endpoints** for
**11,160 patients across 33 cancer types**, and — uniquely — publishes
**per-endpoint, per-cancer usability guidance** so analysts pick a *statistically
valid* outcome rather than a convenient one.
TCGA-CDR는 흩어진 원본 임상 파일을 정리해 **11,160명 / 33개 암종**에 대한 **4개
생존 엔드포인트**를 표준화하고, **암종별로 어떤 엔드포인트가 통계적으로 타당한지**
가이드를 함께 제공하는 큐레이션 자원이다.

## What it is / 무엇인가
- 33개 enrollment 파일 + 97개 follow-up 파일을 통합하고 **1,000건 이상의 데이터
  품질 문제**를 해결한 curated resource. 결과물은 **Table S1 (tab `TCGA-CDR`)**.
- Single harmonized table keyed by `bcr_patient_barcode`, joinable to molecular,
  imaging, and WSI data. 원본 `clinical_patient_brca.txt`의 **상위(upstream) 정본**.

## Four endpoints / 4개 엔드포인트 (정의는 논문 인용)
| Endpoint | Definition (Liu 2018) |
|---|---|
| **OS** Overall Survival | diagnosis → death from **any** cause |
| **PFI** Progression-Free Interval | diagnosis → **first new tumor event** (new primary, locoregional recurrence, distant metastasis) |
| **DFI** Disease-Free Interval | diagnosis → first new tumor progression **after** the patient was determined disease-free |
| **DSS** Disease-Specific Survival | death **attributed to the cancer** (approximated; cause-of-death documentation incomplete) |

## Key numbers / 핵심 수치 (verified)
- **n = 11,160** patients; **33** cancer types.
- Median follow-up **~22.1 months** (range ~12 mo for GBM/LAML to ~48 mo for KICH).
- BRCA: **1,097 cases**, only **151 OS events** → OS/DSS are **event-poor**.

## BRCA verdict / BRCA 결론
For breast cancer the paper **recommends PFI and DFI**, and **cautions on OS/DSS**
(too few events; "need a longer follow-up for OS and DSS").
유방암은 **PFI·DFI 사용 권장**, **OS·DSS는 주의**(이벤트 수 부족, 추적기간 부족).

## Why it matters to BIOP02 / 본 프로젝트 의의
We already touched raw `clinical_patient_brca.txt`; TCGA-CDR is its **curated,
peer-reviewed replacement** for outcome labels. It (1) fixes label definitions and
censoring, (2) tells us **PFI/DFI are the valid BRCA survival targets**, and (3)
complements the IHC (ER/PR/HER2) + PAM50 **phenotype** labels with **outcome**
labels — and it is exactly the table our `agents/data/` manifest joins against the
NAS WSI inventory (by patient barcode).

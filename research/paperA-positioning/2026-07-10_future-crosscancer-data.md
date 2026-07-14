# Future-work: 타암종 cost-of-substitution 일반화 — 후보 암종 + 데이터 소스·다운로드 (2026-07-10)

> **계획만(미실행).** BRCA-only 룰(Paper B까지) → 스코프 확장은 리더 사인오프 필요. 스쿱=defensible whitespace(`2026-07-10_subtype-decision-map.md` §6).
> 목적: 우리 원리 *표적 유전체 변이 축은 형태학에 near-invisible(분자검사 필수) / 형태 특징 뚜렷한 축은 H&E triage 가능* 을 stress-test할 암종 선정.
> 좋은 후보 = **표적 축(H&E-blind 예상)** 과 **형태학 축(H&E-triageable 예상)** 을 둘 다 가진 암종.
> ⚠️ TCGA 슬라이드 수·DepMap lineage 수는 릴리스/필터로 변동 → *approx* 표기, 착수 전 GDC 포털·DepMap Model.csv 실측.

## 후보 요약 (랭킹순)

| 순위 | 암종 | TCGA 코호트 | 표적 축(H&E-BLIND) | 형태학 축(H&E-TRIAGEABLE) | 데이터 판정 |
|---|---|---|---|---|---|
| **1** | 폐 NSCLC | LUAD, LUSC | EGFR/ALK/ROS1/KRAS-G12C | LUAD vs LUSC 조직형 | **Excellent** |
| **2** | 대장 CRC | COAD, READ | BRAF-V600E·KRAS·(HER2-amp) | **MSI-H**(부분 형태학적) | Excellent |
| 3 | 위 STAD | STAD | **HER2-amp**(BRCA 직접 평행)·MSI | Lauren diffuse/intestinal·EBV | Strong(소규모) |
| 4 | Glioma | LGG, GBM | 1p/19q codel·MGMT-methyl·EGFRvIII | IDH-mut/wt·grade·oligo/astro | Strong |
| 5 | 자궁내막 UCEC | UCEC | POLE·CN-high(serous)·HER2 | serous vs endometrioid | Good |
| (경계) | 흑색종 SKCM | SKCM | BRAF-V600 | (형태학 분자아형 약함) | Marginal |

## 후보별 요지

**1. 폐 NSCLC — 1순위 파일럿.** 교과서적 이중 축: EGFR/ALK/KRAS(표적, H&E 무신호 → 붕괴 예상, BRCA HER2 직접 analog) vs **LUAD/LUSC**(병리 gold-standard H&E 콜, FM 임베딩 고정확 → triage). TCGA-LUAD ~507–534 + LUSC ~486–512 = **NSCLC ~1,000슬라이드** *approx*. 외부검증 **CPTAC-LUAD ~244 + LSCC ~212**(IDC). 라벨=cBioPortal(PanCancer LUAD/LUSC)·GDC MAF. 세포주=**DepMap 최대 lineage(~200+ NSCLC/SCLC)** *approx*, EGFR-i/ALK-i/KRAS-G12C-i 풍부.

**2. 대장 CRC — 2순위(뉘앙스 케이스).** BRAF/KRAS(표적, H&E-blind → 붕괴) + **MSI-H(actionable + 형태학적 상관: mucinous·저분화·TIL, H&E 예측 AUROC ~0.8–0.9, Kather Nat Med 2019)**. → MSI=중간 비용, BRAF=고비용으로 **metric calibration 검증** 가능. TCGA-COAD ~419 + READ ~150–165 *approx*. 외부 **CPTAC-COAD ~178**. 세포주 ~60–85 *approx*(CCLE 고사망 lineage ~60 cap), BRAF-i/anti-EGFR/MEK-i.

**3. 위 STAD — 서사 최강.** **HER2/ERBB2-amp → trastuzumab = BRCA HER2 문자 그대로 복제**(다른 장기). + MSI·CLDN18.2. 형태학=Lauren·signet-ring·EBV lymphoepithelioma. TCGA-STAD ~440 *approx*. ⚠️ **CPTAC-STAD IDC ~20슬라이드(빈약)** → TCGA 내부 split 또는 아시아 위암 보조코호트 필요. 세포주 ~35–45 *approx*(얇음, HER2 집중 복제엔 OK).

**4. Glioma — 형태학 축 showcase.** WHO-CNS5로 분자정의. 1p/19q·MGMT·EGFRvIII(H&E 무신호 → 붕괴; 단 drug-target보다 진단/예후성 → 프레이밍 주의) vs IDH-mut/wt·grade·oligo/astro(H&E 콜). TCGA-LGG ~783 + GBM ~513(대규모). 외부 CPTAC-GBM ~178. 세포주 ~60–85 *approx*, **약리 얇고 targeted-shaped 아님(TMZ·EGFR-i)** → 냉동지도 최약. 형태학 축 예시용.

**5. 자궁내막 UCEC — 검증용.** 4군 분자분류(POLE/MSI/CN-high/CN-low) + HER2(serous). 형태학=serous/endometrioid·grade. TCGA-UCEC ~560 *approx*. 외부 **CPTAC-UCEC ~254(CPTAC 최대급)** — 외부검증 우수. 세포주 ~30–40 *approx*(얇음) → 리드 아닌 검증.

**(경계) 흑색종 SKCM:** BRAF-V600 깨끗(표적 붕괴 데모엔 good)이나 **형태학 분자아형 축 약함** + TCGA-SKCM WSI ~107(소규모)·매칭 CPTAC 없음. 단일축 데모용만.

## 랭킹 + 추천 파일럿
1. **폐 NSCLC(1순위)** — 가장 깨끗한 이중축, ~1,000슬라이드, CPTAC 페어, DepMap 최대. BRCA 파이프라인 그대로 스케일.
2. **대장 CRC(2순위)** — MSI 뉘앙스로 metric calibration, COAD+READ+CPTAC-COAD, 세포주 적정.
3. 위(서사 최강, CPTAC 빈약) · 4. Glioma(형태학 축, 냉동지도 약) · 5. 자궁내막(CPTAC 우수, 세포주 얇음).
> **추천 파일럿 쌍 = 폐 + 대장.** 순수 H&E-blind 표적축(EGFR/ALK) + 순수 triage 형태학축(LUAD/LUSC) + 중간 뉘앙스(MSI) → cost-of-substitution 값의 전 범위를 커버.

## 접근 제약
- **TCGA 진단 WSI = open**(dbGaP 불필요). GDC 또는 GCS 미러 `gs://gdc-tcga-phs000178-open/`.
- 일부 raw somatic MAF는 controlled(dbGaP/PI) — 그러나 **cBioPortal/TCGA-CDR/published 콜(open)이면 충분**, controlled tier 회피.
- **CPTAC WSI = public**(IDC/TCIA, 무자격). CPTAC 분자=PDC/GDC.
- **DepMap(figshare)·GDSC(Sanger) = open.** 장벽 없음.
- 착수 전 **GDC 포털 facet(Data Type=Slide Image, Diagnostic Slide)로 정확 N 실측**.

## 다운로드 HOW-TO

| 필요 | 포털 | 도구/명령 |
|---|---|---|
| TCGA H&E WSI | GDC — portal.gdc.cancer.gov (facet: Slide Image·Diagnostic Slide) | cart→Manifest→`gdc-client download -m gdc_manifest.txt`. GCS 미러 `gs://gdc-tcga-phs000178-open/` |
| CPTAC H&E WSI(외부) | IDC — portal.imaging.datacommons.cancer.gov (collection_id 예: `cptac_luad`) | `pip install idc-index` → `IDCClient.client().download_from_selection(collection_id="cptac_luad", downloadDir="./")` (내장 s5cmd) |
| 분자 라벨(아형/변이/MSI/HER2) | cBioPortal — cbioportal.org (TCGA PanCancer Atlas) | 웹 다운로드 또는 REST(bravado); GDC MAF/CNV·TCGA-CDR |
| 세포주 약물감수성(냉동지도) | DepMap — depmap.org/portal/download (figshare); PRISM ~4,518cpd×~578line | figshare bulk, `Model.csv` lineage로 조인 |
| 〃 GDSC | cancerrxgene.org / ftp `cog.sanger.ac.uk/` | GDSC1/2 IC50 + 세포주 주석 |

## 재사용 자산 (우리 인프라)
타일링(tile_wsi.py)·임베딩(extract_uni/conch/exaone)·MIL·Critic·registry·cost_of_substitution 스크립트(frozen_map·compute_cost·freeze_panel) 전부 재사용. **암종당 신규 = WSI 다운로드+임베딩 추출 + 세포주 lineage 지도 + 아형-치료축 매핑.**

---
**Sources:** GeorgeBatch/TCGA-lung-histology-download · ISB-CGC TCGA images · ScienceDirect S2589004223022526(LGG/GBM/SKCM N) · IDC portal · idc-index · GDC DTT docs · DepMap portal/24Q2 figshare · CCLE datasets · Registry of Open Data DepMap/CCLE. (상세 URL = 조사 원본; *approx* 수치는 착수 전 실측)

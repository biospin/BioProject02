# BIOP02-36: DepMap PRISM + GDSC 데이터 소스 조사 (v0.1)

**Ticket**: BIOP02-36 | **Author**: 서정한 (@jhans) | **Status**: Draft v0.1 | **Last updated**: 2026-05-28

**Scope**: 모델링/치료 근거(therapeutic evidence) 연결을 위한 in vitro 약물 감수성 데이터 소스 1차 정리. BRCA(유방암) 필터링 가능 여부 확인 포함.

---

## 0. 요약 (TL;DR)

| 항목 | DepMap PRISM | GDSC (Sanger) |
|---|---|---|
| 호스트 | Broad Institute | Wellcome Sanger Institute |
| 최신 릴리스 | PRISM Repurposing Public 24Q2 (스크리닝), DepMap 26Q1 (omics) | Release 8.5 (GDSC1 + GDSC2) |
| 주요 response 지표 | log2(fold change), AUC, IC50 (EC50) | ln(IC50), AUC, Z-score |
| 화합물 수 | ~6,000+ (repurposing focus, 비온콜로지 포함) | ~620 (GDSC1 ~345 + GDSC2 ~295, 항암제 중심) |
| 세포주 수 | ~900+ | ~1,000 (GDSC1) / ~970 (GDSC2) |
| Cell line ID | `ModelID` (ACH-XXXXXX, DepMap ID) | `SANGER_MODEL_ID` (SIDMXXXXX), COSMIC_ID |
| BRCA 필터링 | ✅ `OncotreeLineage = "Breast"` 또는 `OncotreePrimaryDisease` | ✅ `Cancer Type (matching TCGA label) = "BRCA"` 또는 `GDSC Tissue` |
| 라이선스 | CC BY 4.0 (대부분) | 비상업적 학술 사용 (자세한 라이선스는 §4 참조) |

**권장**: 두 소스 모두 BRCA subset 추출 가능. 약물 cross-reference는 InChIKey / PubChem CID / DrugBank ID로 매핑.

---

## 1. DepMap PRISM

### 1.1 개요

PRISM(Profiling Relative Inhibition Simultaneously in Mixtures)은 Broad Institute가 개발한 분자 바코딩 기반 다중 세포주 약물 스크리닝 플랫폼이다. 비온콜로지 약물의 항암 효과 발굴(repurposing)에 강점이 있다.

대표 논문: Corsello et al., *Nat Cancer* 2020 — 4,518 drugs × 578 cell lines (primary screen).
이후 PRISM은 DepMap Portal에 분기별 릴리스로 통합되어 확장되고 있다.

### 1.2 다운로드 경로

| 자원 | URL |
|---|---|
| DepMap Portal 메인 | https://depmap.org/portal/ |
| 전체 다운로드 페이지 | https://depmap.org/portal/data_page/?tab=allData |
| PRISM Repurposing 소개 | https://depmap.org/repurposing/ |
| 25Q2 이전: Figshare 미러 | https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248 |
| 릴리스 노트 (포럼) | https://forum.depmap.org/c/announcements |

> ⚠️ **중요 변경**: 25Q2 릴리스부터는 Figshare 일괄 다운로드가 제공되지 않는다. Portal의 Downloads 탭에서 파일별 다운로드 또는 Custom Downloads 사용 필요. 24Q4까지는 Figshare에서 zip 일괄 받기 가능.

### 1.3 핵심 파일

#### (A) PRISM 약물 감수성 — `PRISM Repurposing Public 24Q2`

| 파일명 | 내용 |
|---|---|
| `Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv` | Primary screen log2 fold-change matrix (cell line × drug at single dose, 보통 2.5 µM) |
| `Repurposing_Public_24Q2_Extended_Secondary_Data_Matrix.csv` | Secondary screen, 8-point dose-response 기반 매트릭스 |
| `Repurposing_Public_24Q2_Extended_Primary_Compound_List.csv` | 화합물 메타데이터 (primary) |
| `Repurposing_Public_24Q2_Extended_Secondary_Compound_List.csv` | 화합물 메타데이터 (secondary) |
| `Repurposing_Public_24Q2_Cell_Line_Meta_Data.csv` | 세포주 메타데이터 (PRISM 컨텍스트) |

> 파일명은 릴리스에 따라 prefix가 바뀌므로(`primary-screen-*`, `secondary-screen-*` 등 구버전 명명도 존재) v0.2에서 정확한 매핑 표 추가 예정.

#### (B) 세포주 메타데이터 (DepMap omics 릴리스, BRCA 필터링 필수)

| 파일명 | 내용 |
|---|---|
| `Model.csv` | 세포주 마스터 메타 — ModelID, CellLineName, StrippedCellLineName, OncotreeCode, OncotreeLineage, OncotreePrimaryDisease, OncotreeSubtype, Sex, Age, GrowthPattern, …  |
| `OmicsProfiles.csv` | 세포주별 omics 프로파일 매핑 |

### 1.4 주요 컬럼

#### Primary/Secondary Data Matrix

| 컬럼 | 설명 | 비고 |
|---|---|---|
| `row_id` (또는 첫 컬럼) | DepMap ModelID (ACH-XXXXXX) | cell line 조인 키 |
| 각 컬럼명 | `<BroadID>::<dose>::<screen_id>` 형식의 drug-condition | secondary는 dose 컬럼 별도 존재 |
| 값 | log2 fold-change vs DMSO (primary) / fitted AUC, EC50 (secondary) | 음수일수록 감수성 |

#### Compound List

| 컬럼 | 설명 |
|---|---|
| `IDs` / `BroadID` (BRD-XXXXXX) | PRISM 내부 화합물 ID |
| `Drug.Name` / `name` | 화합물 이름 |
| `MOA` | mechanism of action |
| `target` | 알려진 단백질 표적 |
| `disease.area` | 임상 적응증 영역 |
| `indication` | 승인 적응증 |
| `phase` | 임상 단계 (Launched / Phase 3 등) |
| `smiles` | SMILES |
| `InChIKey` | InChIKey (drug 교차 매핑용) |
| `pubchem_cid` | PubChem CID |
| `repurposing_hub` | Drug Repurposing Hub 등록 여부 |

#### Model.csv (세포주 메타)

| 컬럼 | 설명 |
|---|---|
| `ModelID` | ACH-XXXXXX (조인 키) |
| `CellLineName` | 표시명 (예: MCF7) |
| `StrippedCellLineName` | 정규화된 이름 |
| `DepmapModelType` | 모델 분류 |
| `OncotreeLineage` | 상위 조직 (예: `Breast`) ← **BRCA 1차 필터** |
| `OncotreePrimaryDisease` | 주 질환 (예: `Invasive Breast Carcinoma`) |
| `OncotreeSubtype` | 세부 아형 (예: `Breast Invasive Ductal Carcinoma`) |
| `OncotreeCode` | Oncotree code |
| `Sex`, `Age`, `Source`, `Patient_ID` 등 | 보조 메타 |
| `SangerModelID` | GDSC 조인 키 (SIDMXXXXX) ← **GDSC와 cross-link 핵심** |
| `COSMICID` | COSMIC ID (또 다른 cross-link 키) |

### 1.5 BRCA 필터링

```python
# 예시 (pandas)
model = pd.read_csv("Model.csv")
brca_models = model[model["OncotreeLineage"] == "Breast"]["ModelID"].tolist()
# 또는 더 엄격하게:
brca_models = model[
    model["OncotreePrimaryDisease"].str.contains("Breast", na=False)
]["ModelID"].tolist()

# PRISM matrix 필터링
prism = pd.read_csv("Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv", index_col=0)
prism_brca = prism.loc[prism.index.intersection(brca_models)]
```

**가용 BRCA 세포주 수 (확인 필요, v0.2)**: DepMap 26Q1 기준 약 70~80개 추정. PRISM screening이 된 BRCA 세포주는 일부 subset.

### 1.6 라이선스

- 데이터 라이선스: **CC BY 4.0** (DepMap Portal 명시).
- 인용 요건: 릴리스 노트의 reference + 원 논문 (Corsello et al. 2020 for PRISM).
- 상업적 사용도 attribution 조건 하에 허용.

---

## 2. GDSC (Genomics of Drug Sensitivity in Cancer)

### 2.1 개요

Wellcome Sanger Institute(영국) + Massachusetts General Hospital(미국)이 공동 시작한 약물 감수성 스크리닝 자원. GDSC1과 GDSC2 두 데이터셋이 있으며, 동일 cell line × drug 조합이 중복될 경우 **GDSC2를 사용하도록 권장**된다 (실험 프로토콜 개선).

대표 논문: Yang et al., *NAR* 2013; Iorio et al., *Cell* 2016; Garnett et al., *Nature* 2012.

### 2.2 다운로드 경로

| 자원 | URL |
|---|---|
| 메인 포털 | https://www.cancerrxgene.org/ |
| Bulk download | https://www.cancerrxgene.org/downloads/bulk_download |
| ANOVA 결과 다운로드 | https://www.cancerrxgene.org/downloads/anova |
| 도움말 | https://www.cancerrxgene.org/help |
| Cell Model Passports (세포주 메타) | https://cellmodelpassports.sanger.ac.uk/downloads |
| 곡선 fitting R 패키지 | https://github.com/CancerRxGene/gdscIC50 |

### 2.3 핵심 파일 (Release 8.5 기준; 파일명에 날짜 suffix가 붙음)

| 파일명 (예시) | 내용 |
|---|---|
| `GDSC1_fitted_dose_response_27Oct23.xlsx` | GDSC1 fitted IC50/AUC/RMSE |
| `GDSC2_fitted_dose_response_27Oct23.xlsx` | GDSC2 fitted IC50/AUC/RMSE (권장) |
| `GDSC1_raw_data_27Oct23.csv` | GDSC1 plate-level raw viability |
| `GDSC2_raw_data_27Oct23.csv` | GDSC2 plate-level raw viability |
| `screened_compounds_rel_8.5.csv` | 화합물 메타데이터 |
| `Cell_Lines_Details.xlsx` | 세포주 상세 (조직, TCGA 라벨 포함) |
| `model_list_YYYYMMDD.csv` (cellmodelpassports) | 세포주 마스터 메타 |
| `mutations_all_YYYYMMDD.csv` | somatic mutation calls |
| `cnv_gistic_YYYYMMDD.csv` | copy number |
| `rnaseq_tpm_YYYYMMDD.csv` | RNA-seq 발현 (TPM) |

> ⚠️ 파일 날짜 suffix(예: `27Oct23`)는 마지막 갱신 시점에 따라 달라진다. v0.2에서 다운로드 직전 현재 파일명을 확정한다.

### 2.4 주요 컬럼

#### `GDSC2_fitted_dose_response_*.xlsx` (또는 csv)

| 컬럼 | 설명 |
|---|---|
| `DATASET` | "GDSC1" 또는 "GDSC2" |
| `NLME_RESULT_ID` | curve fitting 결과 ID |
| `NLME_CURVE_ID` | curve ID |
| `COSMIC_ID` | COSMIC cell line ID ← **DepMap의 `COSMICID`로 cross-link** |
| `CELL_LINE_NAME` | 세포주 이름 (예: `MCF7`) |
| `SANGER_MODEL_ID` | SIDMXXXXX ← **DepMap의 `SangerModelID`로 cross-link** |
| `TCGA_DESC` | TCGA 종양 코드 (예: `BRCA`) ← **BRCA 필터 핵심** |
| `DRUG_ID` | GDSC 내부 약물 ID (정수) |
| `DRUG_NAME` | 약물 이름 |
| `PUTATIVE_TARGET` | 표적 |
| `PATHWAY_NAME` | 표적 경로 |
| `COMPANY_ID` | 공급원 |
| `WEBRELEASE` | 공개 여부 (Y/N) |
| `MIN_CONC` / `MAX_CONC` | dose range (µM) |
| `LN_IC50` | **자연로그 IC50 (µM)** ← **주 감수성 지표** |
| `AUC` | normalized AUC (0~1, 낮을수록 감수성 높음) |
| `RMSE` | curve fit error |
| `Z_SCORE` | 약물별 IC50 z-score |

#### `screened_compounds_rel_8.5.csv`

| 컬럼 | 설명 |
|---|---|
| `DRUG_ID` | GDSC drug ID |
| `SCREENING_SITE` | MGH / Sanger |
| `DRUG_NAME` | 표시명 |
| `SYNONYMS` | 별칭 (세미콜론 구분) |
| `TARGET` | 표적 |
| `TARGET_PATHWAY` | 표적 경로 |
| `PUBCHEM` | PubChem CID ← **PRISM과 cross-link 키** |
| `SMILES` | SMILES (cellmodelpassports에서 보충 가능) |

#### `Cell_Lines_Details.xlsx`

| 컬럼 | 설명 |
|---|---|
| `Sample Name` | 세포주 이름 |
| `COSMIC identifier` | COSMIC ID |
| `Cancer Type (matching TCGA label)` | TCGA 라벨 (`BRCA` 등) ← **BRCA 필터** |
| `Microsatellite instability Status (MSI)` | MSI 상태 |
| `Cancer Type` | GDSC 상위 분류 |
| `GDSC Tissue descriptor 1`, `descriptor 2` | 조직 계층 (예: `breast`, `breast_carcinoma`) |

### 2.5 BRCA 필터링

```python
# 예시 (pandas)
fit = pd.read_excel("GDSC2_fitted_dose_response_27Oct23.xlsx")
brca = fit[fit["TCGA_DESC"] == "BRCA"]

# 또는 cell line details에서 추출 후 조인
cld = pd.read_excel("Cell_Lines_Details.xlsx")
brca_cosmic = cld[cld["Cancer Type (matching TCGA label)"] == "BRCA"]["COSMIC identifier"].tolist()
brca = fit[fit["COSMIC_ID"].isin(brca_cosmic)]
```

**가용 BRCA 세포주 수 (확인 필요, v0.2)**: GDSC 전체 약 50~55개 (GDSC2 기준 약 45개).

### 2.6 라이선스

- GDSC 데이터는 **학술/비상업적 사용에 무료**.
- 상업적 사용은 별도 라이선스 협의 필요 (Sanger Institute 정책).
- 인용 필수: 사용 시 GDSC 웹사이트의 권장 인용 (Yang 2013 + Iorio 2016) 명시.
- COSMIC mutation data는 별도 라이선스 (학술 사용 등록 필요할 수 있음 — v0.2에서 확인).

---

## 3. 두 데이터셋 통합 전략

### 3.1 Cell line cross-link 키

| Key | DepMap | GDSC |
|---|---|---|
| Sanger model ID | `Model.csv → SangerModelID` | `SANGER_MODEL_ID` (SIDM*) |
| COSMIC ID | `Model.csv → COSMICID` | `COSMIC_ID` |
| 이름 매칭 | `StrippedCellLineName` | `CELL_LINE_NAME` 정규화 후 비교 (less robust) |

**권장**: `SangerModelID` 우선 사용, fallback으로 `COSMICID`.

### 3.2 Drug cross-link 키

| Key | DepMap PRISM | GDSC |
|---|---|---|
| PubChem CID | `pubchem_cid` | `PUBCHEM` |
| InChIKey | `InChIKey` | (compound list 외부 보충 필요) |
| DrugBank ID | `drugbank_id` (일부) | (별도 매핑 필요) |
| 이름 매칭 | `Drug.Name` | `DRUG_NAME` + `SYNONYMS` |

**권장**: PubChem CID 우선. 이름 기반 매칭은 동의어/이성질체 문제 때문에 주의.

### 3.3 Response 지표 매핑

| 지표 | PRISM | GDSC | 비교 가능성 |
|---|---|---|---|
| Primary single-dose | log2(FC) (2.5 µM) | — | GDSC에는 없음 |
| IC50 | secondary (`EC50` 기반 fitted) | `LN_IC50` (자연로그) | 변환 필요 (PRISM의 IC50도 자연로그 또는 µM 단위 확인 필요) |
| AUC | secondary AUC | `AUC` (0~1 normalized) | 정의 다름 — 직접 비교 부적절, **rank 또는 z-score로 정규화 후 비교 권장** |
| Z-score | per-compound z-score 가공 | `Z_SCORE` 제공 | 비교 시 사용 권장 |

> 두 데이터셋의 IC50/AUC를 직접 비교하지 말 것 — 실험 프로토콜(농도 범위, dose point 수, viability assay 종류)이 다르다. **z-score 또는 rank-based 비교**가 안전하다 (Haibe-Kains et al. 2013 참고).

---

## 4. 라이선스 & 접근 제한 요약

| 자원 | 라이선스 | 접근 제한 | 비고 |
|---|---|---|---|
| DepMap PRISM 데이터 | CC BY 4.0 | 없음 | attribution만 |
| DepMap omics (Model.csv 등) | CC BY 4.0 | 없음 | |
| GDSC drug response | 학술 무료, 상업 별도 | 없음 (다운로드는 무료) | 인용 필수 |
| Cell Model Passports omics | CC BY-NC 일부 (확인 필요) | 일부 dbGaP 경유 raw seq 가능 | v0.2에서 확인 |
| COSMIC mutation | 학술 등록 필요 (https://cancer.sanger.ac.uk/cosmic/license) | 상업적 사용 별도 라이선스 | mutation 사용 시 주의 |

---

## 5. Open questions / 다음 단계 (v0.2에서 확정)

1. PRISM 24Q2 Extended Matrix의 정확한 컬럼 헤더 포맷 (특히 secondary screen의 dose 인코딩) — 실제 파일 헤더 확인 필요.
2. PRISM 파일에서 `secondary` AUC/EC50 값의 단위 (µM vs log2 등).
3. DepMap 25Q2/26Q1 릴리스에서 PRISM 통합 여부 (현재 PRISM은 24Q2가 별도 릴리스).
4. BRCA 세포주의 **PRISM ∩ GDSC** 교집합 실측 (작업: 각각 다운로드 → SangerModelID 조인 → count).
5. GDSC2 release 8.5 파일의 정확한 날짜 suffix (`27Oct23` 외 후속 release 있는지).
6. COSMIC mutation을 모델링에 쓸지 (라이선스 부담 → cellmodelpassports의 `mutations_all_*` 사용이 더 깔끔할 수 있음).
7. Drug ID 매핑 테이블의 출처 — Drug Repurposing Hub(`https://www.broadinstitute.org/repurposing`) vs ChEMBL 비교.
8. 두 데이터셋 모두 음성 대조군(DMSO) 처리·normalization이 다름 → 통합 시 standardize 절차 정의 필요.

---

## 6. 참고 문헌

- Corsello SM, et al. *Discovering the anti-cancer potential of non-oncology drugs by systematic viability profiling.* **Nat Cancer** 1, 235-248 (2020).
- Yang W, et al. *Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells.* **Nucleic Acids Res** 41, D955-D961 (2013).
- Iorio F, et al. *A Landscape of Pharmacogenomic Interactions in Cancer.* **Cell** 166, 740-754 (2016).
- Garnett MJ, et al. *Systematic identification of genomic markers of drug sensitivity in cancer cells.* **Nature** 483, 570-575 (2012).
- Haibe-Kains B, et al. *Inconsistency in large pharmacogenomic studies.* **Nature** 504, 389-393 (2013). ← 두 데이터셋 비교 시 필독.

---

*v0.1 — 1차 데이터 소스 인벤토리. 실측·세포주 교집합·정확한 파일 헤더는 v0.2에서 확정.*

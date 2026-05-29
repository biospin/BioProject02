# BIOP02-52: DepMap PRISM vs GDSC Consistency 검증 방법 (v0.1)

**Ticket**: BIOP02-52 | **Author**: 서정한 (@jhans) | **Status**: Draft v0.1 | **Last updated**: 2026-05-29

**Scope**: BIOP02-45에서 확정한 컬럼을 기반으로, DepMap PRISM과 GDSC2 데이터를 통합할 때 두 소스 간 drug sensitivity 일관성을 검증하는 방법을 정의한다. 결과물은 BIOP02-60 (Endocrine rule sample) 구현의 방법론적 근거가 된다.

---

## 0. 배경 및 문제 정의

Haibe-Kains et al. (Nature 2013)은 CCLE(현 DepMap)와 GDSC의 IC50/AUC 값이 직접 비교 시 낮은 상관관계(Pearson r ≈ 0.1~0.6)를 보인다는 것을 보였다. 주요 원인:

| 요인 | PRISM | GDSC |
|---|---|---|
| 스크리닝 방식 | 분자 바코딩 다중화 | 단일 well 플레이트 |
| dose 범위 | 단일 농도 (2.5 µM, primary) / 8-point (secondary) | 9-point dose-response |
| viability assay | LUMINEX bead (형광) | CellTiter-Glo (ATP 발광) |
| IC50 정의 | EC50 fitted (secondary) | ln(IC50) fitted |
| AUC 정규화 | 자체 정규화 방식 | 0~1 normalized |

**결론**: IC50/AUC 절댓값을 직접 비교하면 안 된다. **동일 데이터셋 내 상대적 순위(rank) 또는 z-score 기반 비교**가 필요하다.

---

## 1. 일관성 검증 절차

### Step 1 — Cell line 교집합 파악

BIOP02-45에서 확정한 조인 키 사용:

```python
import pandas as pd

# DepMap BRCA cell lines
model = pd.read_csv("Model.csv")
brca_depmap = model[model["OncotreeLineage"] == "Breast"][
    ["ModelID", "SangerModelID", "COSMICID", "CellLineName"]
].dropna(subset=["SangerModelID"])

# GDSC2 BRCA cell lines
gdsc = pd.read_excel("GDSC2_fitted_dose_response_*.xlsx")
brca_gdsc = gdsc[gdsc["TCGA_DESC"] == "BRCA"][
    ["SANGER_MODEL_ID", "COSMIC_ID", "CELL_LINE_NAME"]
].drop_duplicates()

# 교집합 (SangerModelID 기준)
overlap_cl = brca_depmap.merge(
    brca_gdsc,
    left_on="SangerModelID",
    right_on="SANGER_MODEL_ID",
    how="inner"
)
print(f"BRCA cell line 교집합: {len(overlap_cl)}개")
```

**예상 결과** (v0.2에서 실측 확정):
- DepMap BRCA: ~75개
- GDSC2 BRCA: ~50개
- 교집합: ~35~45개 추정

---

### Step 2 — Drug 교집합 파악

```python
# PRISM compound list
prism_cpd = pd.read_csv("Repurposing_Public_24Q2_Extended_Secondary_Compound_List.csv")
prism_cpd = prism_cpd[["IDs", "Drug.Name", "MOA", "target", "pubchem_cid"]].dropna(subset=["pubchem_cid"])
prism_cpd["pubchem_cid"] = prism_cpd["pubchem_cid"].astype(str).str.strip()

# GDSC screened compounds
gdsc_cpd = pd.read_csv("screened_compounds_rel_8.5.csv")
gdsc_cpd = gdsc_cpd[["DRUG_ID", "DRUG_NAME", "PATHWAY_NAME", "PUTATIVE_TARGET", "PUBCHEM"]].dropna(subset=["PUBCHEM"])
gdsc_cpd["PUBCHEM"] = gdsc_cpd["PUBCHEM"].astype(str).str.strip()

# PubChem CID 기준 교집합
overlap_drug = prism_cpd.merge(
    gdsc_cpd,
    left_on="pubchem_cid",
    right_on="PUBCHEM",
    how="inner"
)
print(f"Drug 교집합: {len(overlap_drug)}개")
```

**예상 결과** (v0.2에서 실측 확정):
- PRISM 약물: ~6,000+
- GDSC2 약물: ~620
- PubChem CID 매핑 교집합: ~100~200개 추정 (GDSC가 항암제 중심이므로 제한적)

---

### Step 3 — Sensitivity 지표 정규화

직접 비교 불가 → **각 데이터셋 내에서 z-score 변환 후 비교**.

#### 3A. PRISM secondary AUC z-score

```python
# PRISM secondary matrix: 행=ModelID, 열=BroadID::dose::screen
# AUC 컬럼만 추출 (secondary screen의 경우 별도 AUC 파일 존재 가능 — v0.2 확인)

prism_sec = pd.read_csv("Repurposing_Public_24Q2_Extended_Secondary_Data_Matrix.csv", index_col=0)
# BRCA cell line 필터
prism_brca = prism_sec.loc[prism_sec.index.intersection(brca_depmap["ModelID"])]

# drug별 z-score (각 drug에 대해 BRCA cell line 분포 기준)
prism_zscore = prism_brca.apply(
    lambda col: (col - col.mean()) / (col.std() + 1e-8), axis=0
)
```

#### 3B. GDSC2 Z_SCORE 활용

GDSC2는 `Z_SCORE` 컬럼이 이미 제공됨 (drug별 전체 cell line 기준 정규화).

```python
gdsc_brca = gdsc[
    (gdsc["TCGA_DESC"] == "BRCA") &
    (gdsc["SANGER_MODEL_ID"].isin(overlap_cl["SANGER_MODEL_ID"]))
][["SANGER_MODEL_ID", "DRUG_ID", "DRUG_NAME", "LN_IC50", "AUC", "Z_SCORE"]]
```

> ⚠️ GDSC `Z_SCORE`는 전체 cell line (~1,000개) 기준 정규화. BRCA만 추출하면 분포가 달라질 수 있음 → BRCA subset 내에서 재계산 여부는 §4에서 논의.

---

### Step 4 — 일관성 지표 계산

교집합 cell line × 교집합 drug 쌍에 대해 두 소스의 sensitivity 상관관계를 측정.

```python
from scipy.stats import spearmanr
import numpy as np

results = []
for _, drug_row in overlap_drug.iterrows():
    broad_id = drug_row["IDs"]
    drug_id = drug_row["DRUG_ID"]

    # PRISM: 해당 drug의 BRCA cell line z-score
    # (컬럼명에 broad_id 포함 여부 확인 필요)
    prism_col = [c for c in prism_zscore.columns if broad_id in c]
    if not prism_col:
        continue
    p_vals = prism_zscore[prism_col[0]].dropna()

    # GDSC: 해당 drug의 BRCA cell line Z_SCORE
    g_vals = gdsc_brca[gdsc_brca["DRUG_ID"] == drug_id].set_index("SANGER_MODEL_ID")["Z_SCORE"]

    # SangerModelID로 cell line 매핑
    common_cl = overlap_cl.set_index("ModelID")["SANGER_MODEL_ID"]
    p_mapped = p_vals.rename(index=common_cl).dropna()

    # 공통 cell line
    common = p_mapped.index.intersection(g_vals.index)
    if len(common) < 5:
        continue

    rho, pval = spearmanr(p_mapped[common], g_vals[common])
    results.append({
        "broad_id": broad_id,
        "drug_id": drug_id,
        "drug_name": drug_row["Drug.Name"],
        "n_cell_lines": len(common),
        "spearman_rho": rho,
        "pval": pval,
        "moa": drug_row["MOA"],
        "pathway": drug_row["PATHWAY_NAME"]
    })

consistency_df = pd.DataFrame(results)
```

---

### Step 5 — 일관성 기준 정의

| 기준 | 값 | 근거 |
|---|---|---|
| **최소 cell line 수** | ≥ 5개 | 통계적 유의성 확보 |
| **Spearman ρ 기준** | ≥ 0.3 | 두 소스 consensus로 사용 |
| **p-value** | < 0.05 | 유의미한 상관 |
| **data_source 결정** | ρ ≥ 0.3이면 `"both"`, 아니면 각 소스만 사용 | `hypothesis.schema.json` `data_source` 필드 |

```python
# 일관성 높은 drug 선별
high_consistency = consistency_df[
    (consistency_df["spearman_rho"] >= 0.3) &
    (consistency_df["pval"] < 0.05) &
    (consistency_df["n_cell_lines"] >= 5)
]
print(f"양 소스 일관성 있는 drug: {len(high_consistency)}개")

# data_source 태깅
consistency_df["data_source"] = consistency_df["spearman_rho"].apply(
    lambda r: "both" if r >= 0.3 else "single"
)
```

---

## 2. 예상 결과 및 한계

### 예상 패턴

선행 연구(Haibe-Kains 2013, GDSC2 논문) 기반 예측:

- **일관성 높은 약물군**: PARP 억제제(Olaparib), CDK4/6 억제제(Palbociclib), PI3K 억제제 — 항암제 중심 GDSC와 PRISM 모두 커버
- **일관성 낮은 약물군**: PRISM 전용 non-oncology repurposing drug (항생제, 정신과 약물 등) — GDSC에 없거나 농도 범위 불일치
- **BRCA 교집합 drug 수 제한**: GDSC가 항암제 위주이므로 양쪽 모두에 있는 drug은 전체의 일부

### 한계 및 주의사항

1. **GDSC Z_SCORE 재계산 여부**: GDSC 제공 Z_SCORE는 전체 ~1,000 cell line 기준. BRCA subset(~50개)으로 재계산하면 값이 달라짐. 재계산 시 statistical power 감소 — **BIOP02-60 구현 전에 결정 필요.**

2. **PRISM AUC 컬럼명 파싱**: secondary matrix 컬럼이 `BroadID::dose::screen` 형식으로 되어 있어 파싱 로직이 필요. 실제 파일 로드 전까지 불확실.

3. **Cell line n이 적음**: BRCA 교집합 ~35~45개 → drug별 상관 계산 시 power 부족 가능. n < 5인 drug은 분석 제외.

4. **repurposing drug의 비항암 효과**: PRISM의 log2FC는 세포 증식 전반에 영향 주는 독성 약물도 포함. GDSC는 항암 효과만 측정 → 비항암 약물의 일관성은 의미 없음.

---

## 3. 출력물 형식

일관성 검증 결과를 CSV로 저장:

```
experiments/jhans/YYYYMMDD_consistency/
├── config.yaml                     # 파라미터 (기준값, 데이터 버전)
├── cell_line_overlap.csv           # BRCA cell line 교집합 (ModelID ↔ SANGER_MODEL_ID)
├── drug_overlap.csv                # drug 교집합 (BroadID ↔ DRUG_ID, PubChemCID)
├── consistency_scores.csv          # drug별 Spearman ρ, n, pval, data_source
└── summary.md                      # 결과 요약 (n 통계, 고일관성 drug 목록)
```

`consistency_scores.csv` 필수 컬럼:

| 컬럼 | 설명 |
|---|---|
| `broad_id` | PRISM BroadID |
| `drug_id` | GDSC DRUG_ID |
| `drug_name` | 표시명 |
| `pubchem_cid` | 공통 ID |
| `n_cell_lines` | 비교에 사용된 BRCA cell line 수 |
| `spearman_rho` | Spearman 상관계수 |
| `pval` | p-value |
| `data_source` | `"both"` / `"prism_only"` / `"gdsc_only"` |
| `moa` | PRISM MOA |
| `pathway` | GDSC PATHWAY_NAME |

→ BIOP02-60에서 `data_source` 컬럼을 직접 `hypothesis[].data_source`에 매핑.

---

## 4. Open questions (v0.2에서 결정)

1. **GDSC Z_SCORE 재계산 여부** — 전체 vs BRCA subset 기준 중 선택.
2. **PRISM primary vs secondary** — primary(단일 농도 log2FC)만으로도 일관성 검증 가능한지, secondary AUC만 사용할지.
3. **Spearman ρ 기준 0.3의 적절성** — 실제 교집합 분포 확인 후 조정 필요.
4. **비항암 PRISM drug 처리** — `disease.area != "Oncology"`인 약물을 분석에 포함할지.

---

## 5. 참고 문헌

- Haibe-Kains B, et al. *Inconsistency in large pharmacogenomic studies.* **Nature** 504, 389-393 (2013). ← **핵심 근거**
- Corsello SM, et al. *Discovering the anti-cancer potential of non-oncology drugs by systematic viability profiling.* **Nat Cancer** 1, 235-248 (2020).
- Iorio F, et al. *A Landscape of Pharmacogenomic Interactions in Cancer.* **Cell** 166, 740-754 (2016).
- Aben N, et al. *TANDEM: a two-stage approach to maximize interpretability of drug response models based on multiple molecular data types.* **Bioinformatics** 32, i413-i420 (2016).

---

*v0.1 — 방법론 초안. 실측(cell line/drug 교집합 count, Spearman ρ 분포)은 PRISM·GDSC 데이터 다운로드 후 v0.2에서 확정.*

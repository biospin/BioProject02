# Colorectal (CRC) — cell-line therapeutic-axis feasibility gate (Phase 1)

**Date:** 2026-07-10 · **Owner:** kkkim · **Analog:** BRCA GO gate (experiments/kkkim/20260710_cellline_counts/, 51 lines -> GO)
**Data:** DepMap 24Q4 Public (figshare 27993248) x GDSC2 fitted_dose_response_27Oct23. Molecular data primary; no literature backfill used.

## Cohort
- DepMap Bowel (OncotreeLineage=Bowel; colon/rectal adenocarcinoma): **n = 99**
- INNER JOIN GDSC2-screened on SangerModelID: **n = 49** (TCGA_DESC: COREAD 46, UNCLASSIFIED 1, OV 1)

## IMPORTANT: CRC axes are NOT partitioned
Unlike BRCA (single-assignment ER/HER2/TNBC) and Lung (mutually-exclusive drivers), CRC axes **co-occur** (BRAF-V600E CRC is often MSI-high; MSI lines carry KRAS too). Each axis is counted **independently** over the same 49-line cohort; overlaps are reported below.

## Axis counts (threshold >= 5)

| Axis | Definition (molecular) | n | GO/NO-GO |
|---|---|---|---|
| **anti-BRAF** | BRAF p.V600E/V600x | **7** | **GO** |
| **MSI-high** | OmicsSignatures MSIScore >= 20 (calibrated) | **16** | **GO** |
| **KRAS-mut** | KRAS hotspot mut (anti-EGFR-resistant / MEK context) | **22** | **GO** |
| **KRAS-WT** | KRAS wild-type (anti-EGFR-eligible context) | **27** | **GO** |
| **chemo baseline** | whole cohort (5-FU/oxaliplatin/irinotecan) | **49** | **GO** |

- **Overlaps:** BRAF∩MSI = 3 · KRAS-mut∩MSI = 7 · BRAF∩KRAS-mut = 0 (BRAF and KRAS mutually exclusive, as expected).
- **BRAF-V600E lines (7):** SW1417, HT29, MDST8, RKO, SNUC5, LS411N, COLO205.
- **KRAS-mut + KRAS-WT = 22 + 27 = 49** (whole cohort partitioned).

## MSI threshold calibration (defensible, not arbitrary)
Clean bimodal separation: canonical **MSI-high** lines all score >= 65 (HCT116 89.1, DLD1/LoVo 88.6, RKO 90.5, SW48 84.6, HCT15 65.0, LS180 88.4); canonical **MSS** lines all <= 4 (SW480/SW620 3.2, HT29 1.3, COLO205 1.1). **No CRC line falls in the 4-65 gap**, so any threshold in [5,65] yields the same 16 MSI-high lines. Threshold set at 20.

## Drug validation (GDSC2 Z_SCORE; Z < 0 = more sensitive)

| Drug | target+ median Z (n) | target- median Z (n) |
|---|---|---|
| Dabrafenib (BRAF) | **-1.52** (7) | +0.45 (41) |
| Trametinib (MEK) | **-1.65** (7) | -0.91 (42) |
| Selumetinib (MEK) | **-1.17** (7) | -0.70 (42) |

BRAF-V600E lines are clearly more sensitive to BRAF/MEK inhibitors than BRAF-WT lines.

## Verdict: **GO** (all axes >= 5)
anti-BRAF (7), MSI-high (16), KRAS-mut (22), KRAS-WT (27), chemo (49) all pass.

## Caveats / label sources
- MSI/BRAF/KRAS co-occur; independent counts, not a single-assignment table.
- **anti-EGFR (cetuximab) NOT drug-validatable in GDSC2** (antibody, absent). KRAS-WT axis is a mutation-status feasibility proxy only.
- BRAF validation uses Dabrafenib/Trametinib; Vemurafenib/Encorafenib absent from GDSC2 27Oct23.
- All axes DepMap-molecular-derived (OmicsSomaticMutations, OmicsSignatures MSIScore). High confidence.

## vs BRCA
BRCA = GO (51 lines, 3 axes). CRC = **GO** and structurally richer: 4 molecular axes all pass on a smaller cohort (49 lines), with the strongest MSI signal (16) and clean drug validation for the BRAF axis. Note CRC axes overlap (co-occurring biology) whereas BRCA/Lung axes partition.

## Files
counts.json | cellline_axis_table.csv (per-line MSIScore + axis flags + variants) | _zscore_<drug>.csv (validation)

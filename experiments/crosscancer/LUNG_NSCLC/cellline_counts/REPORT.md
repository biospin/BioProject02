# Lung NSCLC — cell-line therapeutic-axis feasibility gate (Phase 1)

**Date:** 2026-07-10 · **Owner:** kkkim · **Analog:** BRCA GO gate (experiments/kkkim/20260710_cellline_counts/, 51 lines -> GO)
**Data:** DepMap 24Q4 Public (figshare 27993248) x GDSC2 fitted_dose_response_27Oct23. Molecular data primary; **no literature backfill used** (all axes fully DepMap-derived).

## Cohort
- DepMap NSCLC (OncotreeLineage=Lung AND OncotreeSubtype in {LUAD, LUSC, NSCLC, Large Cell, Adenosquamous, Poorly-Diff NSCLC}; **SCLC / carcinoid / NUT / mesothelioma / SMARCA4-undiff / immortalized excluded**): **n = 157**
- INNER JOIN GDSC2-screened on SangerModelID: **n = 104**
- TCGA_DESC of cohort: LUAD 63, UNCLASSIFIED 26, LUSC 13, SCLC 1, MESO 1
- **SCLC contamination guard:** 58 SCLC lines are GDSC-screened under OncotreeLineage=Lung; excluding them prevents inflating the chemo axis with non-NSCLC lines.

## Axis counts (threshold >= 5)

| Axis | Definition (molecular) | n | GO/NO-GO |
|---|---|---|---|
| **anti-EGFR** | EGFR activating mut: L858R / exon19del / G719X / L861Q (T790M-alone excluded) | **6** | **GO** (borderline) |
| **anti-ALK** | ALK fusion (EML4-ALK etc.), NSCLC-restricted | **2** | **NO-GO** |
| **anti-KRAS (G12C)** | KRAS p.G12C (sotorasib-druggable subset) | **9** | **GO** |
| KRAS any-mut (context) | KRAS any hotspot missense/indel | 28 | (context) |
| **chemo** | no EGFR-activating / ALK-fusion / KRAS mut | **68** | **GO** |

- **Driver co-occurrence:** 0 (EGFR / ALK / KRAS mutually exclusive here, as expected biologically).
- **EGFR-activating lines (6):** HCC827, PC14, NCIH1650 (exon19del), NCIH3255, NCIH1975 (L858R), LOUNH91 (L747_P753delinsS).
- **ALK-fusion lines (2):** NCIH3122 (EML4-ALK), NCIH2228 (EML4-ALK). A GALK2--FAM214A fusion in NCIH358 was correctly rejected (substring, not the ALK gene).

## Drug validation (GDSC2 Z_SCORE; Z < 0 = more sensitive; Z is within-drug)

| Drug | target+ median Z (n) | target- median Z (n) |
|---|---|---|
| Gefitinib | **-2.20** (6) | +0.12 (98) |
| Afatinib | **-2.57** (6) | +0.17 (98) |
| Osimertinib | **-3.56** (6) | +0.17 (98) |
| Crizotinib (ALK) | **-1.47** (2) | +0.31 (102) |

EGFR-activating lines sit deep in the sensitive tail of all three EGFR-TKIs (strong biological validation). ALK+ lines are sensitive to crizotinib but n=2.

## Verdict: **PARTIAL GO**
- **GO** on anti-EGFR (6), anti-KRAS-G12C (9), chemo (68).
- **NO-GO** on anti-ALK (2 < 5): a genuine feasibility limit (NSCLC ALK-fusion cell lines are rare in DepMap∩GDSC2). Not padded.

## Caveats / label sources
- All targeted axes DepMap-molecular-derived (OmicsSomaticMutations ProteinChange, OmicsFusionFiltered). High confidence.
- **KRAS-G12C cannot be drug-validated in GDSC2:** Sotorasib absent from 27Oct23 (MEKi Selumetinib is only downstream proxy).
- Ceritinib/Alectinib also absent; Crizotinib is the only ALK-TKI in GDSC2.
- anti-EGFR n=6 is exactly at threshold: a thin GO.

## vs BRCA
BRCA gate = GO with all three axes comfortably >=5 (ER+ 15 / HER2-amp 14 / TNBC 23; n=51). Lung = PARTIAL: two axes strong (KRAS-G12C 9, chemo 68) but anti-ALK fails and anti-EGFR borderline. Larger cohort (104 vs 51) but sparser actionable-driver lines per axis.

## Files
counts.json | cellline_axis_table.csv (per-line axis flags + variants) | _zscore_<drug>.csv (validation)

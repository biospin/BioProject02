# CPTAC-BRCA HER2 protein vs H&E — decoupling support (auxiliary)

**claim_level: hypothesis_only. Confirms known biology, NOT a new finding.**

In CPTAC-BRCA (cBioPortal `brca_cptac_2020`, mass-spec proteomics), HER2+ tumors show
strongly elevated ERBB2 protein relative to HER2− tumors: mean log2 ratio +3.07 vs −4.59
(clinical IHC/FISH grouping, n=13 vs 82; Cohen's d ≈ 4.0, Mann-Whitney p ≈ 1.6e-7), with the
same direction under DNA-amplification grouping (n=17 vs 105; d ≈ 3.4, p ≈ 1.1e-8). This simply
re-confirms established biology (ERBB2 amplification → protein overexpression); it is not a discovery.

Separately, on the H&E side, the attention-MIL model scores HER2 at AUROC 0.599 (internal holdout)
and 0.53 (external CPTAC) — near chance (source: sjpark modeling eval, `agents/modeling`; quoted, not
recomputed here).

**Decoupling (one line):** In the same CPTAC-BRCA cohort, HER2 is molecularly real and loud at the
protein level (d ≈ 4), yet morphologically near-silent to an H&E foundation-model MIL (AUROC ≈ 0.60).
The low H&E performance therefore reflects genuine morphological silence, not a label or DNA-copy
artifact. This is a cohort-level juxtaposition of two facts about CPTAC-BRCA — the proteomics subset
is **not** patient-paired to the H&E-evaluated slides, and no such pairing is claimed.

## Scope / caveats
- Auxiliary support for an existing decoupling narrative — not a new modality or new result.
- Protein values are log2 ratios vs a reference (negatives = below reference), so compare groups, not absolute signs.
- HER2 labels are cBioPortal native (`ERBB2_UPDATED_CLINICAL_STATUS`, case-normalized; `ERBB2_GENE_AMPLIFIED`),
  matched to protein by native `patientId` — no cross-ID join to our internal `X01BR`/`01BR` labels.
- Literature concordance (not our computation): Mertins et al. 2016 (Nature, doi:10.1038/nature18003)
  and Krug et al. 2020 (Cell) report ERBB2 amplification–protein correlation in this cohort.

## Files
- `her2_protein_decoupling.json` — locked numbers, source, attribution.
- `_raw_both.json` — pre-normalization run (exact-case labels), kept for trace.

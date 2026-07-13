# CRC "MSI-visible half" — cell-resolution re-attempt on Su et al. 2025 IMC

**Status:** `claim_level: hypothesis_only` · `critic_status: pending` · `evidence_strength: exploratory`
**Not a prediction model.** Mechanism-evidence for the cost-of-substitution argument (can H&E morphology partly stand in for an MSI assay?), re-run at the resolution the earlier Visium attempt lacked.

## Why re-attempt (context)
The earlier CRC Angle A on Visium (`../ST/README.md`) was **NULL** and diagnosed as a **substrate/resolution limit**: a 55 µm spot (~14 px in the hires image) is below nuclear resolution, so the lymphocyte-specific texture where the MSI-from-H&E signal lives was inaccessible. Per user instruction we retried on a **cell/protein-resolution substrate (IMC)** and — either way — diagnose *why*.

## Data (feasibility = LIGHT path, confirmed)
- **Su et al. 2025**, npj Precision Oncology, PMC11973205 — *single-cell spatial landscape of stage III CRC*. **Zenodo 13901180** (CC-BY).
- Used file: **`single_cell_phenotypes_and_coordinates.csv`** (104 MB) — **already segmented + phenotyped**: per-cell `AreaShape_Center_X/Y`, `AreaShape_Area`, marker-defined `cell_type`, patient (`alt_identifier`), ROI (`Metadata`). **903,125 cells, 52 patients, 170 ROIs (~1000×1000 px, IMC ~1 µm/px)**. No OME-TIFF segmentation and no H&E registration were needed → the heavy IMC burden was avoided.
- **MSI labels:** paper Suppl. Table 2 (`MSI_WES` True/False) → **8 MSI-H / 32 MSS** with cell data (record's "9/33" includes NA/version diff).
- `cell_type` is marker-based (panel incl. **CD8a, CD3, GranzB/GZMB, CD4, FoxP3, CD68, CD20, CD45RO**) — so the "immune protein" axis is captured by the phenotype labels; per-cell marker *intensities* live only in the 818 MB h5ad (not needed for this test).
- **H&E:** exists only in v2 (**Zenodo 14602539, `H&E_annotations.zip`, 3.8 MB**) as **unregistered pathologist-markup JPGs for 4 patients** (CR014, CR020, CR034, CR048; "inflammatory and stromal" regions). No IMC↔H&E transform is provided → qualitative only.

## Estimand (abundance-controlled, threshold-free, patient = unit)
Density colocalization alone would only rediscover *"MSI-H is immune-hot"* — the exact trap the Visium README flagged (**expression/abundance immune-hot ≠ H&E-visible spatial pattern**). So abundance and pattern are separated:
- **(A) Abundance — positive control, NOT the spatial result:** immune-cell fraction per patient, MSI vs MSS (pooled lymphocytes and CD8-specific).
- **(B) Spatial pattern — PRIMARY:** within-ROI **label permutation** (positions + counts fixed, 500 perms) → **log2(obs/null)** enrichment, a scale-free abundance-controlled effect:
  - `LL` = immune–immune adjacency → **aggregation beyond abundance** (TIL-hub geometry)
  - `LT` = immune–tumor adjacency → **infiltration/mixing** (>0) vs **exclusion** (<0)
  - z = (obs−null)/std reported as secondary (inflates with n). Neighbor radius 30 px (µm); robustness at 20/50 px. Aggregate ROI→patient; MSI vs MSS = Mann-Whitney + rank-biserial.
- **Two pre-declared immune definitions** (no post-hoc subset picking): broad `lymphocyte` {CD8/CD4 T, NK, B, Prolif. Immune} and cytotoxic `CD8` (the hypothesis-named compartment).

## Headline (honest) — a **substantive** null, not a resolution artifact
At cell resolution the hypothesized **MSI-specific immune spatial co-organization was NOT observed**. Crucially, unlike Visium this is **not** a substrate limit — the resolution is adequate — so the null is informative.

| Axis | MSI-H (n=8) | MSS (n=32) | p (MW) | rbc | read |
|---|---|---|---|---|---|
| **CD8 abundance** (frac/patient) | 0.086 | 0.053 | 0.209 | +0.30 | 1.6× higher in MSI-H, hypothesis-direction, **NS** |
| lymphocyte abundance | 0.228 | 0.196 | 0.561 | +0.14 | flat |
| **Lymphocyte aggregation** log2(obs/null) | **+0.66** | **+0.77** | 0.060 | −0.44 | strong hubs in **BOTH**; not MSI-specific (if anything ↓) |
| **CD8 aggregation** log2 | +1.14 | +1.37 | 0.126 | −0.36 | idem, CD8 hubs ~2.2–2.6× in both |
| Immune–tumor mixing log2 | −0.43 | −0.67 | 0.174 | +0.32 | immune **excluded** in both; MSI-H weakly less-excluded, NS |

Radius sensitivity (LL log2 p): lymphocyte {20:0.088, 30:0.060, 50:0.070}; CD8 {20:0.209, 30:0.126, 50:0.263} — **stable**, no radius rescues a positive.

**The lymphocyte-aggregation p=0.06 is an abundance-saturation artifact, not a real reverse effect.** log2(obs/null) mechanically *shrinks* as immune abundance rises (fold-enrichment compresses when the random expectation is already high): across patients `spearman(log2_LL, immune_frac) = −0.53 (p=0.0005)`. Since MSI-H is (weakly) more immune-abundant, the raw MSS>MSI-H gap is largely this confound. **After regressing immune fraction out, the residual MSI-vs-MSS comparison is null: p=0.117 (rbc −0.37)** — i.e. no abundance-clean spatial difference in *either* direction. Read the raw rbc −0.44 as confounded, not as "MSS more organized."

**Interpretation.** Immune cells form strong spatial hubs (log2>0, ~1.6–2.6×) and are excluded from tumor — but **these architectural features are generic to both MSI-H and MSS in this cohort**, so they do **not** discriminate MSI on the spatial-geometry axis. This is a robust no-spatial-signal finding; it is distinct from the **abundance** axis, where CD8 leans hypothesis-direction (+1.6×, rbc +0.30) but is **underpowered (n=8), not absent**. The only MSI-directional signals (CD8 abundance +1.6×; slightly reduced tumor–immune exclusion) are **weak and non-significant**. So the discriminating axis for MSI here is **abundance (CD8 density)**, *not* distinctive spatial geometry — and CD8/lymphocyte density is exactly what H&E TIL-scoring (Kather, imCMS) already reads. The "spatial asymmetry" framing appears to be the **wrong axis** for MSI; the earlier breast ERBB2 **floor** remains the clean positive.

## Precise diagnosis — why it is weak (the task's core requirement)
Feasibility was **not** the blocker (segmented single-cell table + labels were ready). Ranked bottleneck candidates, judged on data:
1. **Not resolution** — cell-level is adequate; this is the genuine lift over the Visium null.
2. **Statistical power** — n=8 MSI-H. The one real-direction effect (CD8 +1.6×) lands at p=0.21. This cohort caps MSI-H at 8; no reanalysis fixes it.
3. **Cohort selection** — all **stage III with recurrence/metastasis**. MSS here is aggressive *and* immune-infiltrated (lymphocyte frac 0.196), compressing the MSI-vs-MSS immune contrast seen in unselected series.
4. **ROI sampling** — IMC uses ~3 pathologist-chosen ~1 mm² fields/patient, not whole-slide; a whole-tumor spatial-architecture estimand is thin and non-randomly sampled.
5. **Metric/biology** — immune **aggregation is a generic lymphoid property** (both groups), so spatial organization per se is not the MSI signal; abundance is. The estimand that *would* separate (CD8 density / Immunoscore-like infiltration) is abundance-driven, and is precisely the H&E-countable feature — no spatial-geometry advantage.
6. **No co-registered H&E** in the light path → cannot test H&E-readability directly (only 4 unregistered annotation JPGs).

## Contrast vs breast ERBB2 floor (do not hide)
| Axis | Breast Angle A (ERBB2 floor) | CRC MSI (this IMC test) |
|---|---|---|
| Molecular event | **amplification** → direct mRNA up | MSI → **immune program** (indirect) |
| Clean readout | Θ = overlap(tumor vs ref) on a direct gene | abundance + spatial architecture of a cell population |
| Result | positive floor, n=8 patients | **null**; weak underpowered CD8-abundance trend |
| Why differ | direct dosage signal | immune organization generic to both MSI/MSS; discriminant is density, not geometry |

Consistent with the structural-difference table already in `../ST/README.md`: amplification↔direct-readout is H&E-legible in a way a subtype-associated immune program (organized similarly regardless of MSI) is not.

## Next possible paths (flagged, not run)
1. **Qualitative H&E overlay** (Zenodo 14602539): 4 patients incl. 2 MSI-H (CR014, CR048). No transform provided → feature-based registration, illustrative only (n too small for a quantitative claim).
2. **Functional cytotoxicity** from h5ad (818 MB): per-cell GZMB/PD1 *intensity* (function, not identity) — test whether functional-effector focus (not lymphocyte location) differs. Heavier, still feasible.
3. **Abundance/Immunoscore axis with adequate power** — needs a larger MSI-H n than this cohort provides; the spatial-geometry axis is not the lever.
4. **Accept the boundary:** at cell resolution, immune spatial architecture does not separate MSI/MSS beyond a weak underpowered CD8-abundance trend; keep the breast ERBB2 floor as the positive and document CRC MSI as a different (abundance-driven, immune-program) axis.

## Files
- `analyze_su_imc.py` → `su_imc_msi_colocation.json` (all metrics), `per_roi_metrics.csv`
- `make_fig.py` → `fig_su_imc_msi.png` (A CD8 abundance · B/C aggregation · D mixing)
- Inputs (not committed; scratchpad): `single_cell_phenotypes_and_coordinates.csv` (Zenodo 13901180), MSI map from Suppl. Table 2.

## Prior art / anchors
imCMS (Sirinukunwattana et al., *Gut* 2021); Kather et al. 2019 (MSI-from-H&E); Pelka et al., *Cell* 2021 (MMRd immune hubs); Su et al. 2025 (this IMC atlas).

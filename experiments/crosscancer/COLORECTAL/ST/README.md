# CRC "Angle A" (ST) — cost-of-substitution asymmetry, spatial test

**Status:** `claim_level: hypothesis_only` · `critic_status: pending` · `evidence_strength: exploratory`
**Not a prediction model.** This is *mechanism evidence* for the cost-of-substitution argument (why H&E can partly substitute one molecular test and not another), ported from the breast Angle A (`experiments/kkkim/angle_A_spatial_erbb2/`).

## Headline (honest)
The hypothesized **visible/silent spatial asymmetry was NOT observed** at Visium-spot / hires resolution.
- MSI half: immune signature does **not** colocalize with H&E nuclei density in the MSI/CMS1 sample (ρ = −0.007; CI includes 0); if anything it is stronger in MSS/CMS2 (ρ = 0.173) — opposite of the hypothesis.
- RAS half: MAPK activity proxy is **weakly *positive*** with density (ρ = 0.075–0.172, all 4 samples) — "not silent."
- Contrast Δρ = ρ_immune − ρ_MAPK: |Δρ| < 0.09, **sign-inconsistent** across samples (CMS1 −0.083, CMS2 +0.032, CMS4 −0.063/−0.037), and **flips sign between morphology proxies** (CMS1: hematoxylin −0.083 vs darkness +0.064). An effect smaller than proxy-choice noise is not a real spatial asymmetry.

This is a **substrate/resolution limit, NOT a biological refutation** of MSI-from-H&E. A 55 µm Visium spot ≈ 14 px in the 2000-px hires image — below nuclear resolution — so the lymphocyte-specific texture where the imCMS / Kather MSI-from-H&E signal lives is not accessible here. Generic nuclei density also conflates tumor and lymphocyte nuclei.

## The one robust positive — labeled precisely
**EXPRESSION-level** immune-hot vs cold: CMS1/MSI IFN-γ genes are far more detected (IRF1 0.85, STAT1 0.57, GBP1 0.61) than CMS2/MSS (0.23, 0.11, 0.03). This supports *"an immune program exists in MSI"* — it does **NOT** show *"it is H&E-visible."* Do not let it stand in for the spatial claim.

**Depth-controlled (not an artifact):** housekeeping ACTB/B2M detection is near-identical across CMS1/CMS2 (0.99/0.99 vs 0.99/0.93) and median UMI/spot comparable (4687 vs 3502), and the **CP10k-normalized** IFN means survive (CMS1 IRF1 1.58 / STAT1 0.75 / GBP1 0.81 vs CMS2 0.27 / 0.11 / 0.03; 5.8×–24×). So the immune contrast is real, not a sequencing-depth confound.

**Null is airtight (two substrate limits, not biology):**
1. A **lymphocyte-specific** CD8A+GZMB-only score is *also* null in CMS1/MSI (ρ = 0.04) — the null is not an artifact of the IFN-heavy signature composition.
2. **Signature composition:** the 7-gene score is dominated by broadly-expressed IFN-response genes (well detected) while lymphocyte-specific CD8A/GZMB are sparse under FFPE probe capture (0.09/0.11). IFN genes are induced in tumor *and* stroma, so the signature reads IFN-pathway *activity*, not lymphocyte *location* — a second substrate limit on top of the 14 px/spot image-resolution wall.

## Structural differences vs breast Angle A (do not hide these)
| Axis | Breast Angle A (ERBB2 floor) | CRC MSI half | CRC RAS half |
|---|---|---|---|
| Molecular event | **amplification** → direct mRNA up | subtype-associated immune program | **point mutation** (KRAS/NRAS) → expression unchanged |
| Readout | direct gene (ERBB2) | multi-gene IFN-γ signature | **downstream ACTIVITY proxy** (indirect, less clean) |
| Mutation status | HER2+ confirmed | CMS1 = MSI-*associated* transcriptomic subtype, not an MSI assay | **no KRAS status** for these samples |
| Estimand | Θ overlap (tumor vs ref) | ρ(score, H&E density) colocalization (re-pointed) | same |
| Replication n | 8 patients | **MSI n=1** (CMS1) vs MSS n=1 (CMS2) — descriptive only | n=4 sections |

The breast Θ ("floor") and the CRC ρ ("colocalization") **share the rank machinery, not the meaning** — Θ was re-pointed to an association metric. Amplification↔point-mutation and direct↔proxy readability differences are stated explicitly (per `docs/ai-collaboration-cautions.md` case 1).

## Method (ported from `analyze_v2_overlap.py`)
Threshold-free rank statistic (Spearman ρ of signature vs **continuous** H&E density — no arbitrary cut); spot-stratified bootstrap CI B=2000; hex 6-neighbor interior edge control; patient=unit, **no pooling**. Signature = mean per-gene z of CP10k+log1p over detected genes. Morphology proxy = **hematoxylin optical density** (Ruifrok–Johnston; nuclei-specific), validated by positive control ρ(totalUMI, hem)=0.36–0.52; mean-darkness kept as a sensitivity proxy.

**CI caveat:** bootstrap resamples spots *within one section* → within-sample spatial evidence only, **optimistic under spatial autocorrelation**. Read effect size + cross-sample sign-consistency, not CI stars. MSI-vs-MSS is descriptive/exploratory, not a tested difference.

## Data
- **GSE285505** (Iwane / Kyoto Univ.), Visium FFPE probe panel, 17,943 targeted genes, spaceranger-1.3.1. 4 samples: GSM8703565 sample24 **CMS1 (MSI target)**, GSM8703566 sample26 **CMS2 (MSS ctrl)**, GSM8703563/GSM8703564 CMS4 (mesenchymal). All 15 signature/proxy genes present in all samples (DUSP4 near-undetected, detect ≈ 0.02–0.06 — noted).
- **RAS mut/WT external — available but unused:** Valdeolivas et al. Zenodo **7760264** is reachable (per-sample zips 50–150 MB, `.ndpi` H&E). Not used here: `.ndpi` needs openslide + a separate heavy pipeline; the within-sample activity-proxy on GSE285505 (identical processing for both halves) is the cleaner apples-to-apples design. Mutation-stratified test = future step.

## Next substrate (resolution-appropriate, flagged not run)
**Su et al. 2025 IMC** (Zenodo **13901180**, CC-BY, MSI-H 9 / MSS 33, H&E confirmed): protein/cell-resolution CD8/GZMB co-mapping is the correct-resolution test of immune–morphology coexistence. Different modality + cell segmentation → a genuine lift, not run here.

## Files
- `analyze_crc_st.py` → `_per_sample.json` (raw per-sample metrics)
- `build_json.py` → `msi_immune_colocation.json`, `ras_silent_proxy.json` (deliverable results)
- `make_figs.py` → `fig_crc_st_msi_visible.png`, `fig_crc_st_ras_silent.png`
- `data/` GSE285505 supplementary (h5 + positions + scalefactors + hires PNG)

## Prior art / anchors
imCMS (Sirinukunwattana et al., *Gut* 2021); Kather et al. 2019 (MSI-from-H&E); Pelka et al., *Cell* 2021 (MMRd immune hubs); Path2Space (*Cell* 2026 — opposite direction, morphology→expression).

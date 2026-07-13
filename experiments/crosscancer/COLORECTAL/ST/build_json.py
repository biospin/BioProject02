#!/usr/bin/env python3
"""Emit the two deliverable JSONs from _per_sample.json — honest exploratory result."""
import json
from pathlib import Path
HERE = Path(__file__).parent
per = json.load(open(HERE / "_per_sample.json"))
by = {r["cms"]: r for r in per}

COMMON = {
    "dataset": "GSE285505 (Iwane/Kyoto Univ., Visium FFPE probe panel, 17,943 targeted genes, spaceranger-1.3.1)",
    "samples": {r["sample"]: {"gsm": r["gsm"], "cms": r["cms"], "role": r["role"],
                              "n_spots": r["n_spots"]} for r in per},
    "method": ("threshold-free Spearman ρ(molecular signature score, per-spot H&E hematoxylin-OD "
               "density) across all in-tissue spots; spot bootstrap CI B=2000; hex 6-neighbor "
               "interior edge control; patient=unit, NO pooling. Ported from breast Angle A "
               "(analyze_v2_overlap.py, Andersson HER2+ ST)."),
    "morphology_proxy": ("hematoxylin optical density (Ruifrok–Johnston deconvolution) = nuclei "
                         "cellularity. Positive control ρ(totalUMI, hem) = 0.36–0.52 across the 4 "
                         "samples (proxy validated). Mean-darkness proxy kept as sensitivity check."),
    "normalization": "CP10k + log1p; signature = mean of per-gene z-scores over detected genes.",
    "unit_of_replication_caveat": ("bootstrap resamples spots WITHIN one section → within-sample "
        "spatial evidence only; CI is OPTIMISTIC under spatial autocorrelation. Read effect size + "
        "cross-sample sign-consistency, NOT CI significance. MSI n=1 (CMS1) — MSI-vs-MSS is "
        "descriptive/exploratory, NOT a tested difference. CMS1 is a transcriptomic subtype strongly "
        "associated with (not an assay of) MSI-H."),
    "claim_level": "hypothesis_only",
    "critic_status": "pending",
    "evidence_strength": "exploratory",
    "prior_art": ["imCMS (Sirinukunwattana et al., Gut 2021)", "Kather et al. 2019 (MSI-from-H&E)",
                  "Pelka et al., Cell 2021 (MMRd immune hubs — biological anchor)",
                  "Path2Space (Cell 2026 — opposite direction: morphology→expression)"],
}

# ---- (1) MSI-visible ----
c1 = by["CMS1"]; c2 = by["CMS2"]
msi = {
    "analysis": "CRC Angle A — MSI-visible half (immune signature ↔ H&E morphology colocalization)",
    "hypothesis": ("MSI-H/CMS1 tumors: IFN-γ / cytotoxic immune signature (CD8A, GZMB, STAT1, GBP1, "
                   "IRF1, CXCL9, CXCL10) spatially coexists with H&E-visible lymphocyte-dense areas → "
                   "morphology correlate exists → H&E can partly substitute MSI testing (low cost)."),
    "signature_genes": ["CD8A", "GZMB", "STAT1", "GBP1", "IRF1", "CXCL9", "CXCL10"],
    "genes_missing_from_panel": "none (all 7 present in all samples)",
    "PRIMARY_result": {
        "rho_immune_vs_hem_density": {r["cms"]: r["rho_immune_vs_hem"] for r in per},
        "rho_immune_vs_hem_ci95": {r["cms"]: r["rho_immune_vs_hem_ci95"] for r in per},
        "rho_immune_interior": {r["cms"]: r["rho_immune_interior"] for r in per},
        "rho_lymphocyte_specific_CD8A_GZMB_only_vs_hem": {r["cms"]: r["rho_lymph_CD8A_GZMB_only_vs_hem"] for r in per},
        "finding": ("NULL / not demonstrable. In CMS1/MSI the immune signature does NOT colocalize "
                    "with H&E nuclei density (ρ = -0.007, CI includes 0). Colocalization is if "
                    "anything STRONGER in CMS2/MSS (ρ = 0.173) — opposite of the hypothesis. No "
                    "MSI-specific spatial morphology correlate at this substrate."),
        "lymphocyte_specific_crosscheck": ("Repeating with a CD8A+GZMB-only score (lymphocyte-specific, "
            "not IFN-dominated) is ALSO null in CMS1/MSI (ρ = 0.04) — the null is not an artifact of the "
            "IFN-heavy signature composition. Airtight: neither the pathway signature nor direct "
            "lymphocyte markers colocalize with H&E cellularity here."),
    },
    "signature_composition_caveat": ("The 7-gene immune score is dominated by broadly-expressed IFN-response "
        "genes (IRF1 0.85, STAT1 0.57, GBP1 0.61 detection) while lymphocyte-SPECIFIC CD8A/GZMB are sparse "
        "(0.09/0.11) under FFPE probe capture. IFN genes are induced in tumor AND stroma, so the signature "
        "reads IFN-pathway activity, not lymphocyte LOCATION — a SECOND substrate limitation (on top of the "
        "14px/spot image-resolution wall) explaining why the correlate is invisible."),
    "compartment_theta_stroma_vs_tumor": {r["cms"]: r["compartment_theta_immune_stroma_vs_tumor"] for r in per},
    "compartment_theta_note": ("template-port Θ (immune enrichment in epithelial-low vs epithelial-high "
        "compartment). ~0.40–0.48 (weak). Measures COMPARTMENTALIZATION, not H&E-visibility — does not "
        "rescue the headline."),
    "ORTHOGONAL_positive_EXPRESSION_LEVEL": {
        "note": ("This is EXPRESSION-level, NOT spatial-morphology. Supports 'an immune program exists "
                 "in MSI', NOT 'it is H&E-visible'. Do not substitute for the spatial claim."),
        "ifn_gamma_gene_detection_frac": {
            "CMS1_MSI": {g: c1["gene_detection"]["immune"][g]["detect_frac"] for g in ["STAT1", "GBP1", "IRF1", "CXCL9"]},
            "CMS2_MSS": {g: c2["gene_detection"]["immune"][g]["detect_frac"] for g in ["STAT1", "GBP1", "IRF1", "CXCL9"]},
        },
        "depth_control_NOT_an_artifact": {
            "median_umi_per_spot": {r["cms"]: r["depth_control"]["median_umi"] for r in per},
            "housekeeping_detect_ACTB_B2M": {r["cms"]: r["depth_control"]["housekeeping_detect"] for r in per},
            "ifn_cp10k_mean_depth_normalized": {r["cms"]: r["depth_control"]["ifn_cp10k_mean"] for r in per},
            "reading": ("Housekeeping ACTB/B2M detection is near-identical across CMS1/CMS2 (0.99/0.99 vs "
                        "0.99/0.93) and median UMI comparable (4687 vs 3502), so the immune contrast is NOT "
                        "a sequencing-depth artifact. CP10k-normalized (depth-controlled) IFN means SURVIVE: "
                        "CMS1 IRF1 1.58 / STAT1 0.75 / GBP1 0.81 vs CMS2 0.27 / 0.11 / 0.03 (5.8×–24×)."),
        },
        "reading": "CMS1 immune-hot (IRF1 0.85, STAT1 0.57, GBP1 0.61) vs CMS2 immune-cold (0.23, 0.11, 0.03).",
    },
    "interpretation": ("The predicted spatial morphology correlate is NOT demonstrable at Visium-spot / "
        "hires resolution. A 55µm spot ≈ 14 px in the 2000-px hires image — below nuclear resolution — "
        "so lymphocyte-specific texture (where the imCMS/Kather MSI-from-H&E signal lives) is not "
        "accessible. Additionally, generic nuclei density conflates tumor and lymphocyte nuclei; the "
        "CP10k-normalized immune fraction need not track total cellularity. This is a SUBSTRATE/"
        "RESOLUTION limit, NOT a biological refutation of MSI-from-H&E."),
    "next_substrate": ("Su et al. 2025 IMC (Zenodo 13901180, CC-BY, MSI-H 9 / MSS 33, H&E confirmed): "
        "protein/cell-resolution CD8/GZMB co-mapping is the resolution-appropriate test of immune–"
        "morphology coexistence. Flagged as next step, not run here (different modality + cell "
        "segmentation)."),
}
msi.update(COMMON)

# ---- (2) RAS-silent ----
ras = {
    "analysis": "CRC Angle A — RAS-silent half (MAPK activity proxy ↔ H&E morphology)",
    "hypothesis": ("RAS/EGFR-MAPK pathway activity is present in tumor but H&E-morphology-silent → no "
                   "morphology correlate → H&E cannot substitute → high substitution cost."),
    "CRITICAL_constraint": ("KRAS/NRAS are POINT mutations → expression unchanged → a RAS-expression "
        "floor is meaningless. We therefore map a DOWNSTREAM MAPK ACTIVITY proxy (DUSP4, DUSP6, SPRY2, "
        "ETV4, ETV5, PHLDA1 + EGFR ligands AREG, EREG). This is ACTIVITY-based, NOT mutation-based: we "
        "have NO KRAS status for these samples. Proxy route makes this half less clean than the breast "
        "ERBB2 (amplification→direct-expression) analog — asymmetry amplification↔point-mutation, "
        "direct↔proxy is explicit and NOT hidden."),
    "signature_genes": ["DUSP4", "DUSP6", "SPRY2", "ETV4", "ETV5", "PHLDA1", "AREG", "EREG"],
    "genes_missing_from_panel": "none (all 8 present in all samples; DUSP4 near-undetected, detect≈0.02–0.06)",
    "PRIMARY_result": {
        "rho_mapk_vs_hem_density": {r["cms"]: r["rho_mapk_vs_hem"] for r in per},
        "rho_mapk_vs_hem_ci95": {r["cms"]: r["rho_mapk_vs_hem_ci95"] for r in per},
        "rho_mapk_interior": {r["cms"]: r["rho_mapk_interior"] for r in per},
        "finding": ("MAPK proxy is WEAKLY POSITIVELY correlated with H&E nuclei density (ρ = 0.075–0.172, "
                    "all 4 samples). It is 'NOT silent' — a finding in itself, and one that UNDERCUTS the "
                    "clean visible/silent asymmetry (the proxy tracks generic cellularity, likely because "
                    "denser epithelium carries more MAPK-active tumor)."),
    },
    "CONTRAST_delta_rho": {
        "delta_rho_immune_minus_mapk_HEM": {r["cms"]: r["delta_rho_immune_minus_mapk_HEM"] for r in per},
        "delta_rho_HEM_ci95": {r["cms"]: r["delta_rho_HEM_ci95"] for r in per},
        "delta_rho_DARK_sensitivity": {r["cms"]: r["delta_rho_immune_minus_mapk_DARK"] for r in per},
        "finding": ("Predicted asymmetry NOT observed. |Δρ| < 0.09, sign-INCONSISTENT across samples "
                    "(CMS1 -0.083, CMS2 +0.032, CMS4 -0.063/-0.037), and Δρ FLIPS SIGN between the two "
                    "morphology proxies (CMS1: hematoxylin -0.083 vs darkness +0.064). An effect that is "
                    "smaller than proxy-choice noise is not a real spatial asymmetry."),
    },
    "interpretation": ("Neither a clean RAS-silence nor an immune-visible/RAS-silent asymmetry is "
        "demonstrable at this substrate. Same resolution + shared-cellularity-confound reasons as the MSI "
        "half. The Δρ differencing removes the shared confound and leaves only tiny, sign-unstable effects."),
    "data_availability_note": ("Paired KRAS-mut/WT Visium+H&E (Valdeolivas et al., Zenodo 7760264; "
        "Yang 2025 / GSA HRA011642) — Zenodo 7760264 IS reachable (per-sample zips 50–150 MB, .ndpi H&E). "
        "NOT used: .ndpi needs openslide + a separate heavy pipeline; within-sample activity-proxy on "
        "GSE285505 (same processing for both halves) is the cleaner apples-to-apples design. Recorded as "
        "available-but-unused; mutation-stratified test is a future step."),
}
ras.update(COMMON)

(HERE / "msi_immune_colocation.json").write_text(json.dumps(msi, indent=2, ensure_ascii=False))
(HERE / "ras_silent_proxy.json").write_text(json.dumps(ras, indent=2, ensure_ascii=False))
print("wrote msi_immune_colocation.json, ras_silent_proxy.json")

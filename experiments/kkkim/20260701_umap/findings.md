# BIOP02-63 — Embedding UMAP sanity (UNI, TCGA-BRCA)

**Date:** 2026-07-01 · **Owner:** kkkim (Embedding) · claim_level: sanity (non-modeling, no Critic gate)

## Setup
- Input: UNI v1 per-slide tile embeddings (5000×1024), mean-pooled → slide vector (1024).
- n = **1010 / 1010** slides (manifest rows missing embeddings: 0).
- StandardScaler → UMAP (n_neighbors=15, min_dist=0.1, metric=cosine, seed=42).
- Script: `agents/embedding/scripts/embed_umap.py`
- Artifacts: `slide_features.npz` (reusable by `site_classifier_probe.py --features`), `umap_coords.csv`, `umap_*.png`.

## Findings
1. **PAM50 subtype is NOT the dominant axis.** Basal/HER2/LumA/LumB/Normal are intermixed across the
   manifold — no clean subtype separation in mean-pooled UNI space. (`umap_pam50.png`)
2. **Submitting site (TSS) clusters strongly.** Sites form tight islands — e.g. A8 (n=83) is a fully
   detached left-hand island; A2/BH/D8/AR/E2 each clump. (`umap_tss_code.png`) This is the
   **Howard 2021 site-confound**: embeddings encode submitting-site batch signal more strongly than biology.
3. ER/PR/HER2 follow the same diffuse pattern as PAM50 (no clean IHC separation).

## Implication
- Empirically **justifies the site-disjoint `split_policy_v0`** — random splits would leak site → inflate
  phenotype AUC. Directly motivates **Exp2-A site-classifier probe** (quantify residual site AUROC; chance≈0.5).
- Caveat for modeling (sjpark): slide-level mean-pool washes out spatial structure → attention MIL
  (Sprint 3) should recover more subtype signal than mean-pool baseline.

## Exp2-A site-classifier probe (quantified)
- `site_probe_report.json` — logistic-regression site probe on `slide_features.npz`, patient-grouped 5-fold CV.
- **macro OvR AUROC = 0.9977** (95% CI 0.9958–0.9989) · shuffle baseline = 0.4999 · n=971 slides, 19 sites, 971 patients.
- Sits squarely in the **Howard 2021** site-AUROC range (0.964–0.998); chance ≈ 0.5.
- ⇒ UNI slide embeddings are **near-perfectly site-identifiable** → site-disjoint `split_policy_v0` is mandatory;
  any random-split phenotype AUC must be treated as site-inflated. Binds **Critic #1 (data leakage)**.

## Next
- Feed site-AUROC 0.9977 into Critic #1 for sjpark's MLP results.
- Regenerate same panels + probe for CONCH once 1010/1010 done → UNI vs CONCH site-confound comparison.

# BIOP02-48 — foundation-model embedding comparison (TCGA-BRCA, slide-level)

- UNI **1024d** · CONCH **512d** · EXAONE_pm **768d** · EXAONE_sg **768d** · probe: LogReg + StratifiedGroupKFold(5) by patient
- claim_level: **sanity** (embedding QC / model selection — not a Critic-gated claim)
- per label: identical intersection slide set across all models

## Phenotype linear-probe AUROC (higher = better)

| Label | n | UNI | CONCH | EXAONE_pm | EXAONE_sg | winner |
|---|---|---|---|---|---|---|
| er_status | 1007 | 0.8723 [0.8457, 0.8965] | 0.8577 [0.8291, 0.8858] | 0.8466 [0.8171, 0.8775] | 0.9249 [0.9021, 0.9464] | **EXAONE_sg** |
| pr_status | 1002 | 0.7694 [0.7375, 0.797] | 0.7615 [0.7286, 0.7951] | 0.7657 [0.7302, 0.7979] | 0.8527 [0.8242, 0.8784] | **EXAONE_sg** |
| her2_status | 698 | 0.5983 [0.5494, 0.6465] | 0.5903 [0.5355, 0.6416] | 0.6593 [0.6123, 0.7079] | 0.6967 [0.6485, 0.7435] | **EXAONE_sg** |
| pam50 | 1006 | 0.7241 [0.7057, 0.7448] | 0.7277 [0.7072, 0.7489] | 0.7267 [0.706, 0.748] | 0.7085 [0.6865, 0.7322] | **CONCH** |

## Site-confound (Howard 2021; lower = less batch signal)

| Model | site macro-AUROC |
|---|---|
| UNI | 0.9977 |
| CONCH | 0.9782 |
| EXAONE_pm | n/a |
| EXAONE_sg | n/a |

## Interpretation

Phenotype AUROC: higher = more linearly-decodable molecular signal (model-selection signal, not a prediction claim). Site AUROC: lower = less submitting-site batch confound. Probe is patient-grouped so no patient leaks across folds.

> Caveat: Per label all models scored on the identical intersection slide set. UNI/CONCH = mean-pooled tile embeddings (256^2@20x, Otsu, cap 5000). EXAONE = internal tiling+Macenko@0.5mpp; representation noted in model name (patch_mean = apples-to-apples pooling, slide_global = EXAONE's own aggregation). So deltas conflate model + tiling pipeline, not model alone.

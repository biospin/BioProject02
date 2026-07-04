# BIOP02-48 — foundation-model embedding comparison (TCGA-BRCA, slide-level)

- UNI **1024d** · CONCH **512d** · EXAONE_pm **768d** · EXAONE_sg **768d** · probe: LogReg + StratifiedGroupKFold(5) by patient
- claim_level: **sanity** (embedding QC / model selection — not a Critic-gated claim)
- per label: identical intersection slide set across all models

## Phenotype linear-probe AUROC (higher = better)

| Label | n | UNI | CONCH | EXAONE_pm | EXAONE_sg | winner |
|---|---|---|---|---|---|---|
| er_status | 1010 | 0.8551 [0.8279, 0.8824] | 0.8419 [0.8113, 0.8718] | 0.8517 [0.8209, 0.8816] | 0.9232 [0.8994, 0.9437] | **EXAONE_sg** |
| pr_status | 1005 | 0.7695 [0.7386, 0.7981] | 0.7611 [0.7275, 0.7929] | 0.7621 [0.7279, 0.7947] | 0.8450 [0.8157, 0.8732] | **EXAONE_sg** |
| her2_status | 698 | 0.5983 [0.5494, 0.6465] | 0.5903 [0.5355, 0.6416] | 0.6593 [0.6123, 0.7079] | 0.6967 [0.6485, 0.7435] | **EXAONE_sg** |
| pam50 | 1009 | 0.7358 [0.7164, 0.7568] | 0.7341 [0.7144, 0.7543] | 0.7319 [0.7119, 0.7518] | 0.7040 [0.6836, 0.7261] | **UNI** |

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

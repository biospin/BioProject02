# BIOP02-48 — UNI vs CONCH embedding comparison (TCGA-BRCA, slide-level)

- UNI dim **1024** · CONCH dim **512** · probe: LogReg + StratifiedGroupKFold(5) by patient
- claim_level: **sanity** (embedding QC / model selection — not a Critic-gated prediction claim)

## Phenotype linear-probe AUROC (higher = better)

| Label | n | UNI | CONCH | Δ(UNI−CONCH) | winner |
|---|---|---|---|---|---|
| er_status | 1010 | 0.8551 [0.8279, 0.8824] | 0.8419 [0.8113, 0.8718] | +0.0132 | **UNI** |
| pr_status | 1005 | 0.7695 [0.7386, 0.7981] | 0.7611 [0.7275, 0.7929] | +0.0084 | **UNI** |
| her2_status | 698 | 0.5983 [0.5494, 0.6465] | 0.5903 [0.5355, 0.6416] | +0.0080 | **UNI** |
| pam50 | 1009 | 0.7358 [0.7164, 0.7568] | 0.7341 [0.7144, 0.7543] | +0.0017 | **UNI** |

## Site-confound (Howard 2021; lower = less batch signal)

| Model | site macro-AUROC |
|---|---|
| UNI | 0.9977 |
| CONCH | 0.9782 |

## Interpretation

Phenotype AUROC: higher = more linearly-decodable molecular signal in the slide embedding (model-selection signal, not a prediction claim). Site AUROC: lower = less submitting-site batch confound. Probe is patient-grouped so no patient leaks across folds.

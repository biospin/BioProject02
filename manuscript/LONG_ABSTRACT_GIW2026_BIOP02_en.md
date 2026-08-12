# When is it safe to replace a molecular test with H&E? A cost-of-substitution frame across five cancers

*GIW/ISCB-Asia 2026 two-page long abstract. Blinded — no authors, affiliations or funding. All values are measured and traceable to the source manuscript.*

## Introduction

Predicting molecular status from H&E histology is a well-developed field. Microsatellite instability, mutations and expression subtypes have been predicted repeatedly by deep learning. The performance that gets reported, however, does not answer the question the clinic actually faces: when the prediction is wrong, which treatment does the patient receive instead? At the same AUROC, the clinical consequence differs by where the errors fall. Predictability and substitutability are different claims, and only the second licenses replacing a test.

We define cost of substitution as the confusion matrix weighted by treatment distance. Each prediction error is then converted into a departure from treatment assignment under a routing fixed in advance, with a distance-free misassignment rate as the headline measure. The definition does not predict drug response; it measures only the cost incurred at the point of assignment when a marker call is wrong. Applied endpoint by endpoint, it separates axes that can be substituted cheaply from those that cannot, and — most importantly — isolates the axes that cannot be decided with the data at hand.

## Methods

One pre-registered protocol was applied identically across five cancers. Breast (TCGA-BRCA, approximately 1,010 diagnostic slides) served as the anchor, analysed together with lung, colorectal, gastric and head and neck. Slides were tiled at 256×256 under 20× magnification with Otsu tissue segmentation, capped at 5,000 tiles per patient. Embeddings came from UNI v1 (1024-dimensional) and patient-level scores from CLAM-SB attention MIL. Evaluation was performed only on a site-disjoint holdout, so that slides from the same institution never appeared in both training and evaluation.

Three controls were applied to every endpoint: a five-seed label-shuffled null (the observed AUROC must exceed the null mean plus two standard deviations), a prevalence baseline, and baselines using subtype alone or pixel mean alone. Confidence intervals are 1,000-fold bootstrap. Decision thresholds are quoted only from the sealed pre-registration document, which also contains the power rule that leaves any endpoint with fewer than 25 holdout positives undecided.

## Results

Of roughly fifteen endpoints, exactly **one** non-control confirmation was adequately powered.

| Endpoint | AUROC | Holdout positives | Verdict |
|---|---|---|---|
| Head and neck HPV | 0.959 [0.921–0.986] | 26 | **Confirmed** (single FM family) |
| Lung LUSC histology | 0.939 [0.905–0.967] | 153 | Positive control, disqualified by audit |
| Gastric MSI-H | 0.860 | 24 | Undecided (one short of threshold) |
| Lung KRAS-G12C | 0.681 | 14 | Undecided |
| Gastric ERBB2 amplification | 0.644 | 14 | No signal (null 0.641) |
| Breast HER2 | 0.599 | 88 | **Negative anchor** |

Head and neck HPV is the only endpoint where substitution can be discussed at all. It is an axis created by viral infection rather than mutation, with real morphological correlates (non-keratinising, basaloid), showing that the frame's "morphological correlate" clause extends to a new class of alteration. The confirmation still carries limits: chance exclusion passed under UNI and UNI2-h but failed under Virchow2 (0.9199 against a threshold of 0.9234), and the site audit found structure between label and institution (Cramér's V = 0.378).

**Site-confounding audit.** The frame disqualifies our own best-looking result. Lung histology scored 0.939, the highest positive control in this study. The audit returned V(site, label) = 1.000: TCGA institution codes coincide exactly with LUAD/LUSC status. Morphological signal and site signature cannot be separated, so a result that conventional evaluation would report as a success is classified here as undecidable. Lung KRAS-G12C shows the same problem from the other side. It scored 0.681, but a baseline using histology alone and no image at all reaches 0.793. With 14 holdout positives this endpoint is undecided under our rule, so the contrast is recorded as an observation and no mechanistic conclusion is attached.

**Negative control.** In the breast anchor, anti-HER2 routing based on H&E-predicted subtype misassigned every candidate (misassignment rate 1.00). Endpoint-level costs invert between endocrine therapy and chemotherapy depending on the routing scheme (0.378 versus 0.035; 0.105 versus 0.510). What survives a change of scheme is only the anti-HER2 misassignment rate and the fact that the headline contrast's confidence interval excludes zero. The operating-point analysis that would fix these thresholds in advance is not yet complete, so the misassignment rate is reported but not extended into a safety verdict. Linking actual treatment outcome gave the same direction: in an exploratory check on an external pCR cohort the anti-HER2 axis did not stratify pathological complete response (0.533 [0.411–0.653]), short of the 0.80 [0.69–0.88] reported by a model based on measured HER2. This is outcome confirmation, not independent validation.

**Power.** Most clinically important endpoints did not meet the pre-registered decision criterion: lung EGFR 15, lung KRAS 14, gastric ERBB2 14, gastric MSI-H 24, gastric EBV 7 and head and neck EGFR amplification 17, against a threshold of 25. Gastric MSI fell one patient short and the threshold was not lowered.

## Discussion

All results are retrospective, cohort-level and hypothesis-level. A site-disjoint split blocks leakage but does not block confounding; the coupling between label and institution remains and was quantified in five endpoints. Across three foundation models the ordering of the lung endpoints and the principal negative results were preserved, but whether an individual endpoint cleared chance exclusion varied by model, and **no endpoint cleared it under all three.** This is ordering stability, not model independence.

## Conclusion

The contribution of this study is not a better predictor. It is a procedure for asking, endpoint by endpoint, whether substitution is safe, and for reporting the axes that cannot be decided with current data as undecided. Applied here, one endpoint survived; for the rest, the molecular test itself is required rather than an AI prediction. The same procedure makes negative results reportable and requires further scrutiny even of high performance. It transfers directly to any study proposing an H&E surrogate.

---

**Figure 1.** Observed cost-of-substitution map. Misassignment loss overlaid on the treatment-distance-weighted confusion matrix, by cancer and endpoint.

**Figure 2.** The power ceiling. Holdout positive counts per endpoint against the pre-registered decision threshold of 25.

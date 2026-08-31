# Predictability Is Not Substitutability: A Cost-of-Substitution Framework for H&E-Based Molecular Prediction Across 5 Cancers

*GIW/ISCB-Asia 2026 2-page long abstract. Blinded — no authors, affiliations or funding. All values are measured and traceable to the source manuscript.*

## Introduction

Predicting molecular subtypes from H&E histology with deep learning is a well-developed field. Microsatellite instability, driver mutations and expression-based subtypes have all been predicted repeatedly, often at high reported accuracy. The metrics that get reported, however, do not answer the question the clinic actually asks, because they say nothing about what happens to the patient when the prediction is wrong: which treatment is given instead. At the same AUROC, the clinical consequence differs sharply depending on which cell of the confusion matrix the errors fall into. Predictability and substitutability are therefore distinct claims, and only the latter licenses replacing a molecular test.

We define the cost of substitution as the confusion matrix weighted by treatment distance. Each prediction error is thereby converted into a departure from treatment assignment under a routing fixed in advance, with a distance-free misassignment rate as the headline measure. The definition does not predict drug response; it measures only the cost incurred at the moment of assignment when a marker call is wrong. Applied endpoint by endpoint, it separates endpoints that could plausibly substitute for a molecular test from those that cannot — and, critically, isolates those that cannot be decided with the data at hand.

## Methods

A single pre-registered protocol was applied identically across 5 cancers. Breast (TCGA-BRCA, approximately 1,010 diagnostic slides) served as the anchor cohort, analysed together with lung, colorectal, gastric and head and neck. Slides were tiled at 256×256 under 20× magnification with Otsu tissue segmentation and capped at 5,000 tiles per patient. Tile embeddings were extracted with UNI v1 (1,024-dimensional) and patient-level scores obtained by CLAM-SB attention-based multiple-instance learning. Evaluation was performed only on a site-disjoint hold-out, so that slides from one institution never appeared in both training and evaluation.

Three controls were applied to every endpoint. The first is a 5-seed label-shuffled null, which an endpoint passes only if the observed AUROC exceeds the null mean plus 2 standard deviations. The second is a prevalence baseline. The third is a baseline using histological subtype alone, or pixel mean alone. Confidence intervals are 1,000-fold bootstrap.

**Verdict scheme.** Each endpoint was assigned one of five verdicts; the assignment rules are quoted from the pre-registration document sealed before any result was seen.

| Verdict | Definition |
|---|---|
| Confirmed | Meets the pre-registered primary confirmation rule — clears the null **and** ≥ 25 hold-out positives |
| Audit-excluded | High accuracy, but morphological signal cannot be separated from site signature |
| No signal | Not meaningfully distinguishable from the shuffled null |
| Undecided | Fewer than 25 hold-out positives |
| Not counted | Anchor, retrospective or exploratory cohort — excluded from the confirmation tally by evidence class |

The criterion of 25 hold-out positives is not a statistical floor for excluding chance. It is a **pre-registered confirmation criterion chosen to narrow the confidence interval on the cost of substitution to a clinically interpretable width.** An endpoint below it is therefore not counted as confirmed even when it clears the null.

## Results

Of roughly 15 endpoints, **exactly one non-control endpoint met the pre-registered primary confirmation rule: head and neck HPV.**

**Table 1. Sealed-forward hold-out — lung, gastric, head and neck.** Cohorts in which predictions were sealed by commit before any result was produced.

| Endpoint | AUROC | 95% CI | Hold-out positives | Verdict |
|---|---|---|---|---|
| Head and neck HPV | 0.959 | [0.921–0.986] | 26 | **Confirmed** † |
| Lung LUSC histology | 0.939 | [0.905–0.967] | 153 | Audit-excluded |
| Gastric MSI-H | 0.860 | [0.759–0.941] | 24 | Undecided |
| Lung EGFR activating | 0.852 | [0.725–0.953] | 15 | Undecided |
| Lung KRAS-G12C | 0.681 | [0.577–0.783] | 14 | Undecided |
| Gastric ERBB2 amplification | 0.644 | [0.523–0.771] | 14 | No signal |

† The head and neck HPV confirmation holds under the primary model (UNI). Of 3 foundation models, UNI and UNI2-h cleared the null but Virchow2 did not (0.9199 against a threshold of 0.9234). The site audit also found an association between label and tissue source site (Cramér's V = 0.397).

**Table 2. Anchor and retrospective cohorts — breast and colorectal (not counted).**

| Endpoint | AUROC | Hold-out positives | Status |
|---|---|---|---|
| Breast HER2 | 0.599 | — | Internal anchor |
| Colorectal anti-EGFR | 0.705 | 84 | Retrospective |
| Colorectal MSI-high | 0.918 | 21 | Retrospective |
| Colorectal BRAF V600E | 0.882 | 15 | Retrospective |

Breast used an internal hold-out predating the pre-registered cross-cancer protocol, so no hold-out positive count is separately reported for it. Colorectal results were produced before the predictions were sealed and are therefore retrospective; direction consistent with the framework does not make them confirmatory. Colorectal anti-EGFR has 84 positives and is adequately powered, but is excluded on status grounds.

**Head and neck HPV.** This axis arises from viral infection rather than mutation, and real histological correlates are observed (non-keratinising, basaloid morphology). It suggests that the morphological correlate our framework requires need not be restricted to genomic alterations.

**Site-confounding audit.** The framework disqualified the highest-accuracy result in the study. Lung histological subtype scored AUROC 0.939, the best result we obtained, but the audit returned V(site, label) = 1.000: TCGA institution codes coincide exactly with LUAD/LUSC status. Morphological signal cannot be separated from site signature, so a result that conventional evaluation would report as a success is classified here as audit-excluded. Lung KRAS-G12C shows the same problem from the other direction. It scored 0.681, but a baseline using histological subtype alone and no image at all reaches 0.793. With 14 positives this endpoint is undecided under our rule, so the contrast is recorded as an observation only.

**Negative reference point.** In the breast anchor, anti-HER2 routing based on H&E-predicted subtype misassigned every candidate (misassignment rate 1.00). Changing the routing scheme reverses the direction of relative cost between endpoints, but the anti-HER2 misassignment rate of 1.00 is invariant to it. Because the operating-point analysis that would fix these thresholds in advance is not complete, we report the misassignment rate without extending it into a safety verdict. Linking actual treatment outcome pointed the same way: in an exploratory analysis on an external pCR cohort, the anti-HER2 prediction did not stratify pathological complete response (AUROC 0.533 [0.411–0.653]). This is outcome confirmation, not independent validation.

**Power.** Most clinically important endpoints did not meet the confirmation criterion. Hold-out positive counts were 15 for lung EGFR, 14 for lung KRAS, 14 for gastric ERBB2, 24 for gastric MSI-H, 7 for gastric EBV and 17 for head and neck EGFR amplification. Gastric MSI-H fell 1 patient short and the criterion was not adjusted.

## Discussion

All results are retrospective, cohort-level and hypothesis-generating. A site-disjoint split blocks leakage but does not control confounding; the coupling between label and institution remains and was quantified in 5 endpoints. Across 3 foundation models the ordering of the lung endpoints and the principal negative results were preserved, but whether an individual endpoint cleared the null varied by model, and no endpoint cleared it under all 3. This is ordering stability, not model independence.

Separately from the pre-registered protocol, we analysed endometrial cancer (TCGA-UCEC) as an exploratory out-of-protocol extension. MSI-H met the power criterion with 30 hold-out positives yet failed the null-exclusion test (AUROC 0.6236 against a threshold of 0.6710). Insufficient power alone therefore does not explain the predominantly non-confirmatory results reported here. Being outside the pre-registration, it is not included in the confirmation tally.

## Conclusion

The contribution of this study is not a more accurate predictor. It is a procedure for asking, endpoint by endpoint, **what substitution would risk at the point of treatment assignment**, and for reporting endpoints that current data cannot decide as undecided. Applied here, 1 endpoint was confirmed; the remainder either did not support substitution or were left undecided for falling below the pre-registered power criterion. That most apparent successes fell out at the confirmation, power or confounding stage is the central observation of this work. The procedure transfers directly to any study proposing an H&E-based surrogate.

---

**Figure 1. Site-confounding audit.** Observed hold-out AUROC against label–institution association (Cramér's V) per endpoint, coloured by leave-one-site-out verdict. Lung histological subtype is the most accurate result in the study (0.939) yet sits at V = 1.000, where morphological signal and site signature cannot be separated, and is therefore excluded from confirmation. Accuracy alone cannot decide substitutability.

**Figure 2. The power ceiling.** Hold-out positive counts per endpoint against the pre-registered confirmation threshold of 25, coloured by verdict; hatching marks positive controls. Most endpoints that cross the threshold are positive controls rather than confirmations, and most clinically actionable endpoints fall below it — the non-confirmatory results are largely undecided rather than negative.

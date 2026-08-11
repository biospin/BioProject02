# When is it safe to replace a molecular test with H&E? A cost-of-substitution frame across five cancers

*Two-page long abstract, GIW/ISCB-Asia 2026. Blind: no author, affiliation or funding is given. All numbers are measured and traceable to the full manuscript.*

## The gap

H&E histology can be mined for molecular status, and the field has shown this repeatedly for microsatellite instability, mutations and expression subtypes. Reported performance, however, is silent on the question a clinic actually faces: if the prediction is wrong, which treatment does the patient receive instead. The same AUROC carries very different consequences depending on where the error lands. Predictability and substitutability are two claims, and only the second licenses replacing a test.

## The frame

We define substitution cost by multiplying the confusion matrix by therapeutic distance, so that every prediction error becomes a displacement in treatment assignment under a routing fixed in advance. The lead indicator is the distance-independent misroute rate. The frame does not predict drug response; it measures only what a wrong marker call costs at the point of assignment. Applied axis by axis, it separates axes that can be substituted cheaply from axes that cannot, and, critically, from axes the data cannot yet decide.

## Design

Five cancers under one pre-registered protocol: breast (TCGA-BRCA, ~1,010 diagnostic slides) as anchor, plus lung (1,026), colorectal (523), gastric (439) and head and neck (468). Slides were tiled at 20x into 256x256 patches with Otsu tissue selection, capped at 5,000 tiles per patient, and embedded with UNI v1 (1024-d). Patient scores came from CLAM-SB attention MIL. Evaluation used a site-disjoint holdout, so slides from one tissue source site never appear in both training and evaluation. Every endpoint carries three controls: a five-seed label-shuffled null (chance-exclusion requires real AUROC > null mean + 2 SD), a prevalence baseline, and a subtype-only or pixel-mean baseline. Confidence intervals are 1,000-fold bootstrap. Adjudication thresholds come only from a sealed pre-registration, including the power rule that fewer than 25 holdout positives leaves an axis undecided.

## What survived

Of about fifteen axes, **one** powered, non-control confirmation emerged.

| Axis | AUROC | Positives | Verdict |
|---|---|---|---|
| Head and neck HPV | 0.959 [0.921-0.986] | 26 | **Confirmed** (single FM family; see limits) |
| Lung LUSC histology | 0.939 [0.905-0.967] | 153 | Positive control, **disqualified by audit** |
| Gastric MSI-H | 0.860 | 24 | Undecided, one positive short |
| Lung KRAS-G12C | 0.681 | 14 | Undecided; below a no-image baseline (0.793) |
| Gastric ERBB2 amp. | 0.644 | 14 | No signal (shuffle-null 0.641) |
| Breast HER2 | 0.599 | near chance | **Negative anchor** |

Head and neck HPV is the only axis where substitution can even be discussed. It is shaped by a viral infection with a real morphological correlate (non-keratinising, basaloid), which extends the frame's "morphological correlate" clause to a new kind of alteration. Even here the result is qualified: chance-exclusion passed in UNI and UNI2-h but failed in Virchow2 (0.9199 against a threshold of 0.9234), and the site audit found label-site structure at Cramer's V = 0.378.

## What the audit disqualified

The frame earns its keep by removing a result that looked good. Lung histology scored 0.939, the highest positive control in the study. The site audit then gave V(site, label) = 1.000: TCGA institution codes coincide perfectly with LUAD/LUSC status, so morphology cannot be separated from the site signature. A number that would ordinarily be reported as a success is instead reported as undecidable.

Lung KRAS-G12C shows the same lesson from the other side. It reached 0.681, but a baseline using no image at all, predicting from histology type alone, reached 0.793. With 14 holdout positives this axis is undecided under our own rule, so we record the contrast as an observation and draw no mechanistic conclusion from it.

## What failed, honestly

In the breast anchor, anti-HER2 routing from H&E-predicted subtype misassigned every candidate (misroute rate 1.00). Per-axis cost flips between endocrine and chemotherapy depending on the routing scheme (0.378 versus 0.035; 0.105 versus 0.510), so only the anti-HER2 rate and the confidence interval of the headline contrast are robust to that choice. The operating-point analysis that would fix these thresholds in advance is not yet complete, and we therefore report the misroute rate without extending it into a safety verdict.

Attaching a real treatment outcome gave the same answer. In an exploratory check on an external pCR cohort, the anti-HER2 axis did not stratify pathological complete response (0.533 [0.411-0.653]), short of the 0.80 [0.69-0.88] benchmark reported for a measured-HER2 model. This is an outcome check, not independent validation.

Most clinically actionable axes never reached decidability: lung EGFR 15 positives, lung KRAS 14, gastric ERBB2 14, gastric MSI-H 24, gastric EBV 7, head and neck EGFR amplification 17, against a pre-registered threshold of 25. Gastric MSI came one patient short and the criterion was not lowered.

## Limits, stated in front

All results are retrospective, cohort-level and hypothesis-level. Site-disjoint splitting blocks leakage but not confounding: label-site coupling remains, and was quantified in five endpoints. Across three foundation models the ordering of lung endpoints was preserved and the negative results reproduced, but whether an individual axis clears chance-exclusion varied by model, and no single cell of the map passed in all three. This is ordering stability, not model independence.

## Why this matters

The contribution is not a better predictor. It is a way of asking, per axis, whether substitution is safe, and of saying plainly which axes the available data cannot decide. Applied here, the answer is that one axis held and the rest still need the molecular test itself rather than an AI substitute. The same instrument is what makes a negative result reportable and an apparently strong result reviewable, and it transfers directly to any group proposing an H&E surrogate for a molecular assay.

---

**Fig 1.** Observed substitution-cost map: misassignment loss overlaid on the confusion matrix weighted by therapeutic distance, per axis and cancer.

**Fig 2.** Power ceiling: holdout positives per axis against the pre-registered decidability threshold of 25, showing which axes are negative and which are merely undecided.

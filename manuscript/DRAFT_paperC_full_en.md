# Paper C — Full English Draft v1 (IMRaD)

> **Status**: English rendering of the Korean full draft ([`DRAFT_paperC_full_ko.md`](DRAFT_paperC_full_ko.md)) v2. Korean first → team review → English, per the team decision. KO/EN parity is machine-checked with `agents/critic/scripts/manuscript_parity_ko_en.py`.
> **All numbers are measured** (UNI canonical, from result files); none were introduced here. Status `hypothesis_only`, retrospective, `critic_status: pending`.
> **Section owners** (SECTION_ASSIGNMENT_paperC.md): Abstract/Intro/Discussion = lead author, Results/Methods = kkkim (numbers and provenance), R5/R6 = sjpark, R7/cost = braveji, Table1/external validation = jamie.
> Target: npj Precision Oncology (IMRaD, assertive Results subheadings). Citations are provisional until `verify_citations.py` passes.
> **v2 revision (2026-08-06)**: incorporates the 2-round cross-examined consensus of the 3-way GPT/Gemini council and the TE review. "Decision map" → "observed spectrum", contributions downgraded, scope of the HPV verdict made explicit, "directionally consistent law" removed, operating-point dependence stated, leakage vs confounding separated, misassignment-cost terminology defined and unified. No number changed.

---

## Abstract

That a tumour's molecular phenotype can be predicted from haematoxylin-and-eosin (H&E) histology, and that such a prediction may clinically replace molecular testing, are two different claims. We propose a cost-of-substitution frame that separates them. Applying the frame across cancers — converting prediction errors into the misassignment cost of a pre-specified treatment routing (a normalised measure of how far treatment assignment is displaced, not a monetary cost) — we confirmed a powered positive signal for HPV in head and neck cancer and quantified, for most mutation and amplification axes, that the present data cannot decide. Across five cancers (breast as the anchor plus lung, colorectal, gastric and head and neck) we sealed and tested a pre-registered morphological-correlate law under one protocol, but powered confirmation is limited. The two ends of the observed spectrum are fixed by measurement: an axis that is legible in morphology (head and neck HPV, holdout AUROC 0.959 — the only powered, non-control positive result in the pre-registered holdout of the primary model UNI; lung LUSC histology 0.939 as a positive control), and a negative anchor that showed no signal supporting substitution in this cohort and routing definition (breast HER2 0.599). In the breast anchor, anti-HER2 routing driven by H&E-predicted subtype failed consistently on the HER2 axis in this cohort and routing definition (misassignment rate 1.00), and in the Yale cohort the anti-HER2 axis did not stratify real pathological complete response (pCR) either (AUROC 0.533 [0.411–0.653]) — an honest negative that shows, as cost, where molecular testing remains necessary. Most clinically important mutation and amplification axes are exploratory because holdout positives fall short of 25 under our pre-registered site-disjoint split. Some exploratory results are compatible with the morphological-correlate hypothesis, but we lacked the power to establish the direction of the law across mutation and amplification axes. We propose "safety of substitution", not "predictability", as the decision criterion. All results are retrospective and hypothesis-level and require prospective validation.

---

## 1. Introduction

Predicting molecular status from H&E histology is by now a mature field. Microsatellite instability, gene mutations and expression subtypes have been predicted with deep learning [Coudray 2018; Kather 2019, 2020; Naik 2020], and pathology foundation models have pushed this further into molecular subtypes and drug sensitivity [Fernandez-Romero 2026; Dawood 2024]. That these targets *can* be predicted is well established.

But being predictable does not mean it is acceptable to replace a molecular test clinically. Reporting predictive performance alone is silent about the clinical cost of substitution — the loss incurred when a wrong prediction assigns the wrong treatment. The same AUROC carries entirely different clinical consequences depending on which treatment decision the error lands in. This gap is where the present work sits.

We propose a cost-of-substitution frame. By converting prediction errors into the misclassification cost of treatment routing, we ask, for each molecular axis, whether H&E can substitute cheaply or whether molecular testing is required. The criterion is safety of substitution, not predictability. The frame does not predict drug response; it operationalises only the substitution cost from marker to treatment assignment.

We test this with a pre-registered morphological-correlate law across five cancers, anchored on breast (plus lung, colorectal, gastric and head and neck). The law states that H&E can cheaply stand in for a test only when the molecular alteration has a morphological correlate recognisable at H&E resolution. The five cancers are a deliberate boundary for testing the law, not an open pan-cancer atlas expansion; and sealing predictions before results does not by itself confer confirmatory strength — it provides claim discipline that suppresses post-hoc selection.

This paper makes five contributions. First, the cost-of-substitution frame itself, together with the separation of confirmable axes from undecided ones obtained by applying one pre-registered protocol across five cancers. Second, honest negatives for axes that are not legible in morphology. Third, the observation that in the breast HER2 axis no signal supporting H&E-based substitution was found, with the external pCR cohort and the spatial-transcriptomics analysis presented only as an exploratory outcome check and a provisional mechanistic hypothesis, respectively. Fourth, claim discipline: explicit adjudication of insufficient power on many axes. Fifth, the framing of a different question — "when is substitution safe?" — rather than a contest over predictive accuracy. Unlike single-cohort breast prediction [Fernandez-Romero 2026] or drug-sensitivity prediction [Dawood 2024], this study contributes a methodological frame that applies one pre-registered evaluation protocol and a substitution-cost lens across a multi-cancer cohort and couples it to an external treatment-outcome anchor.

---

## 2. Results

### R0. What this paper actually establishes

We tested about fifteen endpoints across five cancers under pre-registration. Of these, exactly one powered, non-control confirmation was obtained: HPV in head and neck cancer. Most remaining mutation and amplification axes fell short of twenty-five holdout positives and therefore remain undecided under the pre-registered rule. The text accordingly does not claim that "the law was validated across five cancers".

We establish two things. First, both ends of the map are fixed by measurement under one protocol: which axes are clearly legible in morphology and which are not, measured against identical controls and adjudication criteria. Second, we quantify why the middle of the map cannot be decided at present. That is the power ceiling of R2.

### R1. The substitution-cost spectrum observed in the pre-registered site-disjoint split across five cancers — confirmable axes versus undecided axes

This section converts per-axis substitutability into cost and lays it out as a map. The central figure is Fig2, which overlays cost on the confusion matrix weighted by therapeutic distance; per-axis cost and the confidence interval of the headline contrast are shown in Fig3.

**The legible end.** In the holdout of the primary model UNI, head and neck HPV reached AUROC 0.959 [0.921–0.986] with 26 positives, well above the pre-registered threshold of 0.80 (the limits that remain under model substitution and the site-label structure audit are stated in footnote † to Table R1). This axis is shaped not by a mutation but by a viral infection (non-keratinising, basaloid morphology), so it illustrates a possible extension of the law's "morphological correlate" clause to a new kind (confirmation is confined to the HPV axis). The positive controls behaved as expected: lung LUSC histology 0.939 [0.905–0.967] (153 positives) and head and neck grade 0.815 [0.742–0.882] (41 positives).

**The illegible end.** Breast HER2 is 0.599, effectively at chance; in this cohort and routing definition it shows no signal supporting H&E-based substitution and therefore serves as the negative anchor. Gastric ERBB2 amplification is 0.644, but the shuffle-null is 0.641 — effectively identical, so no signal should be inferred. Lung KRAS-G12C is 0.681, yet a baseline that uses no image at all and predicts from histology alone reaches 0.793, higher still. The apparent predictive power therefore comes from LUAD skew rather than from mutation morphology.

Every endpoint is reported alongside a shuffle-null (5-seed), a prevalence baseline (0.5) and a pixel-mean baseline; the lung mutation axes additionally carry a subtype-only baseline. Epistemic status must also be distinguished. Lung, gastric and head and neck were sealed-forward tests with predictions committed before results, whereas colorectal was analysed after results were already available and is therefore excluded from the tally of powered, sealed confirmations.

**Table R1 — Observed substitution-cost spectrum (UNI canonical). "Cost" here is not monetary: it is treatment misassignment loss (misassignment rate).**

| Cancer | Axis | Role | AUROC [95% CI] | Control | Morphological correlate | Verdict |
|---|---|---|---|---|---|---|
| Head and neck | HPV | Legible axis (viral) | 0.959 [0.921–0.986] | 26 positives | Present (non-keratinising, basaloid) | **Single-FM, site-disjoint confirmation** (model-independence and site confounding untested) † |
| Lung | LUSC histology | Positive control | 0.939 [0.905–0.967] | 153 positives | Morphology itself | Pass ‡ |
| Head and neck | Grade | Positive control | 0.815 [0.742–0.882] | 41 positives | Present | Pass |
| Colorectal | BRAF V600E | Retrospective | 0.868 [0.780–0.938] | 15 positives | Present (serrated/MSI co-occurrence) | Consistent; retrospective, underpowered, exploratory (excluded from confirmation tally) |
| Gastric | MSI-H | Legible axis | 0.860 (development 0.899) | 24 positives | Present (immune) | Undecided (1 short) |
| Lung | EGFR activating | Graded | 0.852 | 15 positives | Partial | Undecided |
| Lung | KRAS-G12C | Required axis | 0.681 (subtype-only 0.793) | 14 positives | Absent (histology skew) | Undecided |
| Gastric | ERBB2 amplification | Required axis (breast replicate) | 0.644 (shuffle 0.641) | 14 positives | Absent | Underpowered; no observed signal |
| Breast | HER2 | Anchor (required axis) | 0.599 | near-random | Absent | **No signal supporting substitution · negative anchor** |
| Gastric | Lauren diffuse | (Original positive control) | 0.536 (development 0.963) | pixel-mean 0.631 | Weakly present | Site-split case (R4) |

† HPV robustness passed 5-seed chance-exclusion in only 2 of 3 foundation models (UNI and UNI2-h) and failed in Virchow2 (real 0.9199 < threshold 0.9234; see R5). The site audit also found site-label structuring (Cramér's V = 0.397). HPV is the single powered anchor that fixes one end of the map — not a generalisation of the law and not a model-independent confirmation.
‡ For lung histology (positive control) the site audit gave V(site, label) = 1.000: TCGA-LUAD/LUSC institution codes coincide 100% with histology, so the morphological signal cannot be separated from the site signature. This limit is stated explicitly wherever the positive control is interpreted.

### R2. Our pre-registered split cannot decide the mutation axes — the power ceiling

This limit becomes visible only after applying the same site-disjoint protocol across five cancers. Clinically important mutation and amplification axes repeatedly fell short of the threshold of twenty-five positives in our pre-registered holdout (Table R2).

In other words, in the single site-disjoint split we chose, most actionable mutations were not adequately powered. We do not generalise this to "public data make it impossible in principle". Power might be recovered with grouped or leave-one-site-out cross-validation; we keep that in the Supplement as exploratory.

The threshold was not adjusted after the fact. Gastric MSI came one patient short at 24, and we did not lower the criterion from 25 to 24; not moving the goalposts is itself a reason to trust the result. Deciding the substitutability of mutation axes will therefore require institutional cohorts or prospective collection, and until then the middle of the map is left open.

**Table R2 — Power ceiling**

| Axis | Holdout positives | Verdict |
|---|---|---|
| Lung EGFR activating | 15 | Undecided |
| Lung KRAS-G12C | 14 | Undecided |
| Gastric ERBB2 amplification | 14 | Underpowered · no observed signal |
| Gastric MSI-H | 24 | Undecided (1 short of threshold) |
| Gastric EBV | 7 | Exploratory |
| Head and neck EGFR amplification | 17 | Undecided |

### R3. Breast anchor — anti-HER2 routing from predicted subtype does not support substitution in this cohort

Under the pre-specified routing definition and in this cohort, anti-HER2 assignment based on H&E-predicted subtype did not support identification of treatment candidates (anti-HER2 misassignment rate 1.00). The misassignment rate and its cost interpretation depend on the stated operating point, however, and the analysis that pre-specifies that threshold is not yet complete. This is an observation showing, as misassignment loss, that H&E substitution may not be safe in this region.

One constraint must be stated honestly. Per-axis cost flips between endocrine therapy and chemotherapy depending on the routing scheme (0.378 versus 0.035; 0.105 versus 0.510). The only claims robust to a change of scheme are the anti-HER2 misassignment rate of 1.00 and the fact that the confidence interval of the headline contrast excludes 0; we do not extend these into a claim that "the other axes are safe".

### R4. Gastric Lauren diffuse is a site-split artefact, not an absence of morphology

An earlier skeleton presented this result as evidence for an axis genuinely invisible to morphology; our own diagnosis does not support that reading.

Lauren diffuse was originally a positive control. Signet-ring and diffuse-type tumours have strong H&E morphology and should have scored high, yet the result was 0.536. The cause is not illegibility. In the same pipeline gastric MSI generalised normally, from 0.899 in development to 0.860 in holdout, whereas Lauren alone fell from 0.963 to 0.536 — a drop of 0.43. Moreover the low-resolution pixel-mean baseline (0.631) exceeded the MIL model (0.536), so a weak morphological signal does exist and the model failed to capture it. The direct cause is that Lauren prevalence varies sharply across institutions and the site-disjoint split concentrated high-prevalence institutions in the evaluation set (46 per cent in training versus 88 per cent in evaluation).

The text therefore describes this case as a methodological instance in which site-disjoint evaluation correctly blocked shortcut learning, and confines the low-confidence verdict to gastric Lauren. MSI in the same cohort remains valid. We do not write that "H&E cannot see Lauren". The representative cases for the thesis that predictability and substitutability are different claims are breast HER2 and lung KRAS, not Lauren.

### R5. The ordering of axes in the map is preserved across foundation models (Supplement)

Holding slides, site-disjoint holdout and endpoints fixed, we retrained CLAM after swapping only the embedding space (UNI 1024-d, Virchow2 2560-d, UNI2-h 1536-d). The claim of this section concerns ordering, not absolute values.

The centre of gravity is the preserved ordering in lung. Across all three embedding spaces the three lung endpoints kept the order histology > EGFR > KRAS, Spearman correlation against UNI was 1.000 for both newer models, and 5-seed chance-exclusion passed 6 of 6 in lung. This is ordering stability, however — not model generality and not confirmation.

Single-cell results diverge by model, and we report this rather than hide it (Table R5). The headline, head and neck HPV, passed in UNI and UNI2-h, but in Virchow2 the point estimate was equally high (0.9199) while the shuffle-null spread was wider, so it did not clear the pre-specified criterion. Colorectal BRAF likewise passed in only two of three models. By contrast the negative results — the Lauren failure and the ERBB2 absence of signal — reproduce consistently in all three.

One case shows plainly that clearing chance-exclusion is not itself evidence of signal. Head and neck EGFR amplification is formally recorded as passing in UNI2-h, yet its real AUROC is 0.505, essentially chance; the shuffle-null spread was narrow, so the threshold sat correspondingly low. That is a pass earned by a low bar rather than by performance, and we do not mark this axis as passing or positive.

What this section can state therefore narrows to two things: the ordering of axes in the lung map was preserved across three models, and the negative results reproduced independently of model. Conversely, we do not write that the findings were "confirmed independently of the foundation model".

**Table R5 — Multiple foundation models (5-seed canonical)**

| Endpoint | UNI | Virchow2 | UNI2-h | 5-seed chance-exclusion |
|---|---|---|---|---|
| Head and neck HPV | 0.9594 | 0.9199 | 0.9559 | UNI and UNI2-h pass / **Virchow2 fails** |
| Colorectal BRAF | 0.8676 | 0.8798 | 0.8978 | UNI and Virchow2 pass / **UNI2-h fails** |
| Gastric MSI-H | 0.8599 | 0.8795 | 0.8670 | Both newer models pass |
| Gastric Lauren (positive control) | 0.5364 | 0.6404 | 0.6033 | All three fail |
| Gastric ERBB2 amplification | 0.6444 | 0.6682 | 0.5845 | Both newer models fail |
| Lung (histology > EGFR > KRAS) | Order preserved | Order preserved | Order preserved | Spearman 1.000 · 6/6 |

### R6. The anti-HER2 axis does not stratify the real treatment-outcome anchor either

We used the Yale pCR cohort to check, exploratorily, whether the anti-HER2 axis score stratifies real treatment outcome. The anti-HER2 axis score was computed by frozen transfer, used to stratify pathological complete response (pCR) in the Yale cohort, and evaluated by AUROC with bootstrap confidence intervals, then compared against a measured-HER2 probability baseline with DeLong's test. The pre-specified comparison benchmark (a calibration reference, not a pass/fail criterion) was defined as approaching and overlapping the cross-validated AUC of 0.80 [0.69–0.88] reported by Farahmand and colleagues, and we make no claim of exceeding it.

The result was AUROC 0.533 [0.411–0.653]: the anti-HER2 axis did not stratify pCR from the H&E-predicted phenotype. The anti-HER2 axis therefore showed no signal supporting substitution in the external outcome anchor either. This is an honest negative and is not promoted to independent validation. We report plainly that it falls short of Farahmand's 0.80.

### R7. Mechanism suggested by spatial transcriptomics (supporting, provisional · critic pending)

This is an exploratory look at the "why" behind the map using public spatial transcriptomics. Everything here is `hypothesis_only` and has not passed Critic, so it should be read as mechanistic support rather than as a headline.

Even in confirmed HER2-positive tumours (8 patients), some tumour spots show ERBB2 levels indistinguishable from the non-tumour reference on the same section. The median probability that a tumour spot's ERBB2 falls below the reference is 0.158; in all 8 patients the confidence interval excludes 0 and the kill-test that rules out diffusion and depth artefacts is passed. Because a patient carries only one label, these low-expression regions cannot be represented, so this strengthens a candidate mechanism for subtype-routing error — that "HER2 is not substitutable" may arise from information the label discards rather than from noise in the prediction (we do not assert a limit in principle).

By contrast the spatial correlate predicted in colorectal did not emerge at Visium resolution. A 55 µm spot is coarser than nuclear resolution and cannot reach lymphocyte-specific texture; this is a substrate and resolution limit, not a biological refutation. The colorectal spatial mechanism therefore remains an open question, and the appropriate test is a substrate with co-registered H&E.

---

## 3. Discussion

Our map takes "safety of substitution", not "predictability", as its criterion. The core of the frame is that the boundary differs by axis and that this boundary is quantified as clinical cost.

Identifying axes that are not legible in morphology is itself information the map provides. The value of the frame lies in flagging axes where H&E substitution is dangerous, such as breast HER2 and lung KRAS; gastric Lauren is excluded from this list because it is a site-split artefact rather than an absence of morphology.

In breast HER2, routing from predicted subtype failed consistently in this cohort and routing definition, which indicates as cost a region where molecular testing remains necessary. We state the scheme dependence of per-axis cost honestly and restrict the robust claims to the anti-HER2 misassignment rate of 1.00 and the confidence interval of the contrast. Furthermore, when real treatment-outcome stratification was attached to the retrospective map, anti-HER2 pCR stratification was not significant (0.533), and this negative is consistent with the argument of the map.

The limits are placed in front. All results are retrospective, cohort-level and `hypothesis_only`; they are not claims of individual-level benefit. The site-disjoint split prevented leakage in which slides from the same institution enter both training and evaluation, but the coupling between label and institution (confounding) remains, which limits interpreting performance as a pure morphological signal; multi-institution generalisation remains subject to further prospective validation. In particular, a site/batch confounding audit confirmed in five endpoints that the site-disjoint split confounds labels with the tissue source site — lung histology (positive control) at V = 1.000, where morphology and site signature cannot be separated; head and neck HPV at V = 0.397; gastric Lauren, whose prevalence shifts from 0.46 to 0.88; and lung EGFR and KRAS, which also show significant site-label association. This is a necessary condition for confounding, not proof that "the model reads site". Site predictability from H&E and leave-one-site-out performance will adjudicate; until then this limit is stated wherever the two anchors are interpreted.

On model independence, the relative AUROC ordering among lung endpoints (histology > EGFR > KRAS) and the principal negative results were preserved across all three foundation models evaluated, whereas whether an individual molecular axis clears chance-exclusion varied by model. This is ordering stability, not model independence of the law as a whole, and no single cell of the map passed in all three models.

The clinical and research implications are as follows. This observational map identifies negative axes where H&E substitution is clearly dangerous (breast HER2) and undecided axes that present data cannot adjudicate, and thereby serves as a decision frame for prioritising future prospective validation. Where H&E screening would actually reduce cost cannot be recommended before prospective validation, and this paper makes no clinical recommendation and no claim of wholesale replacement. The value concentrates on molecular tests that are expensive, slow or scarce, and on resource-limited settings. In short, our contribution is not "beating the gold standard" but "making predictable, as a map, when inexpensive H&E can pre-screen or triage molecular testing and when it cannot".

---

## 4. Methods

### M1. Cohorts and labels
Breast cancer (TCGA-BRCA, about 1,010 diagnostic slides) serves as the anchor, together with lung, colorectal, gastric and head and neck — five cancers in total. Slide counts per cohort are measured in the result JSON files (colorectal 523, lung 1,026, gastric 439, head and neck 468). Label provenance and patient-level splits are managed under `agents/data/`, and the pre-registered axis boundaries are recorded in the sealed document.

### M2. Tiling and embedding
Each whole-slide image was tiled into 256×256 pixel patches at 20× magnification, tissue was separated from background by Otsu thresholding, and a cap of 5,000 tiles per patient was imposed. The headline embedding is UNI v1 (1024-d); for the model-independence test the same coordinates were re-extracted with Virchow2 (2560-d) and UNI2-h (1536-d). Tiles were resized to 224×224 and channel-normalised with ImageNet statistics. H&E stain normalisation was not applied, and the resulting uncorrected stain variation is stated as a limitation.

### M3. Model and training
We used CLAM-SB attention MIL (hidden 512, attention 256, 40–50 epochs, seed fixed at 42). Predictions were produced per slide and then aggregated per patient.

### M4. Evaluation design
All evaluation was performed on a site-disjoint holdout. Slides from the same tissue source site (TSS) were prevented from entering training and evaluation simultaneously, blocking leakage via institutional fingerprints. Three controls were used: a shuffle-null, a prevalence baseline (0.5) and a subtype-only or pixel-mean baseline. Confidence intervals are reported as 1,000-fold bootstrap 95% CIs.

### M5. The cost-of-substitution frame
Substitution cost is defined by multiplying the confusion matrix by therapeutic distance, giving the misclassification cost incurred where the treatment chosen from the measured marker and the treatment chosen from the H&E-predicted marker diverge. The lead indicator is the distance-independent misroute rate. This frame does not predict drug response.

### M6. Pre-registration and claim discipline
Adjudication thresholds are cited only from the sealed pre-registration document. The power rule (fewer than 25 positives → exploratory → INCONCLUSIVE) is not moved after seeing results and is applied symmetrically to confirmation and refutation. All outputs are `hypothesis_only` and retrospective.

### M7. The Yale anchor
The anti-HER2 axis score was computed by frozen transfer, used to stratify pCR in the Yale cohort, and evaluated by AUROC with bootstrap 95% confidence intervals, then compared with the measured-HER2 probability baseline using DeLong's test. The pre-specified benchmark was defined as approaching and overlapping Farahmand and colleagues' 0.80 [0.69–0.88], and we report plainly that the result, 0.533 [0.411–0.653], falls short of it.

### M8. Multi-model robustness
CLAM was retrained from scratch in each foundation-model embedding space (the coordinate systems differ, so the predictive model must be refitted separately for the comparison to be at the same level). The adjudication criterion is 5-seed shuffle-null chance-exclusion (real AUROC > null mean + 2 × standard deviation, ddof = 1), with seeds 42, 1, 2, 3 and 4. Determinism was verified by 2 re-runs at identical seeds.

### M9. Site/batch confounding audit
For each endpoint we quantified whether the site-disjoint split confounds the label with the tissue source site (TSS). We computed Cramér's V between site and label with a permutation p-value, the train/test prevalence shift, and a permutation test of the site concentration of test positives. This analysis examines a necessary condition for confounding; the final adjudication of whether the model actually uses site rests on site predictability from H&E and on leave-one-site-out performance.

---

## Figures and tables

- **Fig1** Pipeline schematic (H&E → embedding → phenotype → routing misassignment rate)
- **Fig2** Observed map overlaying misassignment loss on confusion × distance (central figure)
- **Fig3** Per-axis misassignment loss and the confidence interval of the headline contrast
- **Fig4** (planned) Power ceiling — holdout positives per axis and the boundary of decidability
- **Fig5** (planned) HER2 misassignment detail — treatment-category misassignment rates by routing scheme
- **SFig1** (planned) Multi-model comparison — order preservation across UNI/Virchow2/UNI2-h and the cells that diverge
- **Table R1** Observed substitution-cost spectrum · **Table R2** Power ceiling · **Table R5** Multiple foundation models (Supplement)
- **Table 1** (planned) Cohort characteristics — n, label prevalence and split for the 5 cancers

## Open items

- Citations are provisional (brackets) until machine-verified by `verify_citations.py`.
- Table 1 (cohort characteristics) and the reporting-standard checklist mapping (TRIPOD+AI, CLAIM) will be attached as Supplement.
- When the operating-point analysis (#3) and Phase 2 of the site audit from the publication requirements (BIOP02-121) arrive, footnote † to Table R1 and the limits in the Discussion will be updated.
- KO/EN parity is verified with `manuscript_parity_ko_en.py`; any divergence is resolved in favour of the Korean source until the English becomes canonical at submission.

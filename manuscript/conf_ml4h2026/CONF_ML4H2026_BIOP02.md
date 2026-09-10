# Safety of Substitution: Cost-Aware Evaluation of H&E-Based Molecular Test Replacement Across Five Cancers

## Abstract

That a tumour's molecular phenotype can be predicted from haematoxylin-and-eosin (H&E) histology, and that such a prediction may clinically replace molecular testing, are different claims. We propose a cost-of-substitution frame that converts prediction errors into the misassignment cost of a pre-specified treatment routing. Across five cancers (breast as the anchor plus lung, colorectal, gastric and head and neck), we sealed and tested a pre-registered morphological-correlate law under one protocol, but powered confirmation is limited. The observed spectrum is fixed by measurement at two ends: head and neck HPV, a morphology-legible viral axis, reached holdout AUROC 0.959 and was the only powered, non-control positive result in the pre-registered holdout of the primary model UNI; lung LUSC histology reached 0.939 as a positive control. By contrast, breast HER2 showed no signal supporting substitution in this cohort and routing definition, with AUROC 0.599 and anti-HER2 misassignment rate 1.00. The underlying HER2 phenotype prediction remained near chance under H&E stain normalisation, so the HER2 negative is not an artefact of stain variation, although the routing/cost step itself was not re-run under normalisation. Most clinically important mutation and amplification axes are exploratory because holdout positives fall short of 25 under our pre-registered site-disjoint split. Some exploratory results are compatible with the morphological-correlate hypothesis, but we lacked the power to establish the direction of the law across mutation and amplification axes. We propose safety of substitution, not predictability, as the decision criterion.

## 1. Introduction

AI analysis of histopathological H&E images has expanded across organs as digital pathology has spread [CITE-I1], with weakly supervised multiple-instance learning and pathology foundation models supporting work in urological cancers, breast cancer, pancreatic cancer and other settings [CITE-I2] [CITE-I3] [CITE-I4] [CITE-I5] [CITE-I6]. A persistent target has been molecular-state prediction from images, because IHC staining and tissue-destructive molecular tests are generally costly and slow, whereas H&E is relatively inexpensive and already acquired in routine care [CITE-I7]. Molecular tests guide diagnosis, prognosis and treatment across cancer types [CITE-I8], and molecular state can often be predicted from H&E [CITE-I9].

Prediction alone, however, does not establish that a molecular test can be replaced. The same AUROC can have different clinical consequences depending on which treatment decision the error changes [CITE-I10] [CITE-I11]. We therefore ask when H&E substitution is safe, not simply when a label is predictable.

Our frame converts prediction errors into the misassignment cost of treatment routing. It does not predict drug response and takes no drug structure as input. It operationalises only the substitution cost from marker to treatment assignment.

We test a pre-registered morphological-correlate law across five cancers: breast as the anchor plus lung, colorectal, gastric and head and neck. The law states that H&E can cheaply stand in for a test only when the molecular alteration has a morphological correlate recognisable at H&E resolution. These cancers are a deliberate boundary, not an open pan-cancer atlas expansion; and sealing predictions before results provides claim discipline rather than automatic confirmatory strength.

This paper makes four contributions. First, it introduces a cost-of-substitution frame and applies one pre-registered protocol across five cancers to separate confirmable axes from undecided ones. Second, it reports an honest negative anchor: breast HER2 shows no signal supporting H&E-based substitution, and this negative is robust to H&E stain normalisation at the phenotype-prediction level. Third, it explicitly adjudicates insufficient power on mutation and amplification axes rather than reporting only axes that score high. Fourth, it frames a different question from single-cohort breast prediction [CITE-I12], including Fernandez-Romero 2026 [CITE-I12], and from drug-sensitivity prediction [CITE-I13]: when substitution for a molecular test is safe.

## 2. Results

We tested about fifteen endpoints across five cancers under pre-registration. Exactly one powered, non-control confirmation was obtained: HPV in head and neck cancer. Most remaining mutation and amplification axes fell short of twenty-five holdout positives and therefore remain undecided under the pre-registered rule. We therefore do not claim that the law was validated across five cancers. We establish two things: both ends of the map are fixed by measurement under one protocol, and the middle of the map cannot yet be decided because of the power ceiling described in R2.

### R1. Substitution-Cost Spectrum

This section converts per-axis substitutability into cost. Figure 1 overlays cost on the confusion matrix weighted by therapeutic distance; per-axis cost and the confidence interval of the headline contrast are shown in Figure A1.

In the holdout of the primary model UNI [CITE-M5], head and neck HPV reached AUROC 0.959 [0.921–0.986] with 26 positives, above the pre-registered threshold of 0.80. This axis is shaped by viral infection rather than by a mutation, and may extend the law's morphological-correlate clause to non-keratinising, basaloid morphology, but confirmation is confined to HPV. Positive controls behaved as expected: lung LUSC histology 0.939 [0.905–0.967] with 153 positives, and head and neck grade 0.815 [0.742–0.882] with 41 positives.

At the illegible end, breast HER2 was 0.599, effectively at chance; in this cohort and routing definition it shows no signal supporting H&E-based substitution and serves as the negative anchor. Gastric ERBB2 amplification was 0.644, while the shuffle-null was 0.641, so no signal should be inferred. Lung KRAS-G12C was 0.681, but a baseline using no image and predicting from histology alone reached 0.793; the apparent predictive power therefore comes from LUAD skew rather than mutation morphology.

Every endpoint is reported alongside a shuffle-null, a prevalence baseline and a pixel-mean baseline; lung mutation axes also carry a subtype-only baseline. Epistemic status differs by cohort: lung, gastric and head and neck were sealed-forward tests with predictions committed before results, whereas colorectal was analysed after results were already available and is excluded from the tally of powered, sealed confirmations.

**Table R1. Observed substitution-cost spectrum (UNI canonical). Cost is treatment misassignment loss.**

| Cancer | Axis | Role | AUROC [95% CI] | Holdout n_pos / control baseline | Morphological correlate | Verdict |
|---|---|---|---|---|---|---|
| Head and neck | HPV | Legible axis (viral) | 0.959 [0.921–0.986] | 26 positives | Present (non-keratinising, basaloid) | Single-FM, site-disjoint confirmation (model-independence and site confounding untested) |
| Lung | LUSC histology | Positive control | 0.939 [0.905–0.967] | 153 positives | Morphology itself | Passes chance-exclusion; excluded from the confirmation tally (site signature inseparable) |
| Head and neck | Grade | Positive control | 0.815 [0.742–0.882] | 41 positives | Present | Pass |
| Colorectal | BRAF V600E | Retrospective | 0.882 [0.817–0.938] | 15 positives | Present (serrated/MSI co-occurrence) | Consistent; retrospective, underpowered, exploratory |
| Gastric | MSI-H | Legible axis | 0.860 (development 0.899) | 24 positives | Present (immune) | Undecided (1 short) |
| Lung | EGFR activating | Graded | 0.852 | 15 positives | Partial | Undecided |
| Lung | KRAS-G12C | Required axis | 0.681 (subtype-only 0.793) | 14 positives | Absent (histology skew) | Undecided |
| Gastric | ERBB2 amplification | Required axis | 0.644 (shuffle 0.641) | 14 positives | Absent | Underpowered; no observed signal |
| Breast | HER2 | Anchor | 0.599 | near-random | Absent | No signal supporting substitution; negative anchor |
| Gastric | Lauren diffuse | Original positive control | 0.536 (development 0.963) | pixel-mean 0.631 | Weakly present | Site-split case (R4) |

HPV robustness passed 5-seed chance-exclusion in only 2 of 3 foundation models: UNI and UNI2-h [CITE-M23] passed, while Virchow2 [CITE-M6] did not clear the pre-specified criterion (real 0.9199 < threshold 0.9234, margin −0.0035). The site audit also found site-label structuring (Cramér's V = 0.378). HPV is therefore the single powered anchor that fixes one end of the map, not a generalisation of the law and not a model-independent confirmation. For lung histology, V(site, label) = 1.000, so morphology and site signature cannot be separated. The HPV and MSI-H axes were robust to tile subsampling, but slide-level reproducibility was not established; predictions diverged between multiple slides from the same patient (TCGA-QK-A6IF, 0.92 vs 0.001). Clinical substitution on these axes therefore requires multi-centre prospective validation, multi-slide reproducibility and verification of tumour-region contribution.

### R2. Power Ceiling

Clinically important mutation and amplification axes repeatedly fell short of the threshold of twenty-five positives in the pre-registered holdout. In the single site-disjoint split we chose, most actionable mutations were not adequately powered. We do not generalise this to public data being impossible in principle; power might be recovered with grouped or leave-one-site-out cross-validation, which we treat as exploratory.

The threshold was not adjusted after the fact. Gastric MSI came one patient short at 24, and we did not lower the criterion from 25 to 24. Deciding substitutability of mutation axes will therefore require institutional cohorts or prospective collection, and until then the middle of the map is left open.

**Table R2. Power ceiling**

| Axis | Holdout positives | Verdict |
|---|---|---|
| Lung EGFR activating | 15 | Undecided |
| Lung KRAS-G12C | 14 | Undecided |
| Gastric ERBB2 amplification | 14 | Underpowered; no observed signal |
| Gastric MSI-H | 24 | Undecided (1 short of threshold) |
| Gastric EBV | 7 | Exploratory |
| Head and neck EGFR amplification | 17 | Undecided |

### R3. Breast Anchor

Under the pre-specified routing definition and in this cohort, anti-HER2 assignment based on H&E-predicted subtype did not support identification of treatment candidates: anti-HER2 misassignment rate 1.00. The misassignment rate and cost interpretation depend on the stated operating point, and the analysis that pre-specifies that threshold is not yet complete. This is an observation showing, as misassignment loss, that H&E substitution may not be safe in this region.

Per-axis cost flips between endocrine therapy and chemotherapy depending on the routing scheme (0.378 versus 0.035; 0.105 versus 0.510). The only claims robust to a change of scheme are the anti-HER2 misassignment rate of 1.00 and the fact that the confidence interval of the headline contrast excludes 0; we do not extend these into a claim that other axes are safe.

The HER2 negative is not an artefact of stain variation at the level of phenotype prediction. In a stain-normalisation robustness check on the breast anchor, using Macenko normalisation with embeddings re-extracted and CLAM attention MIL [CITE-M9] re-trained on the same folds, HER2 phenotype prediction remained near chance: AUROC 0.641 versus 0.599 without normalisation in Table R1. ER stayed high (0.917 versus 0.901) and PAM50 was preserved (0.740 versus 0.759). The rank of the anchor endpoints, ER high > PAM50 mid > HER2 near-chance, was preserved with and without stain normalisation. Two limits remain: the routing/cost pipeline was not re-run under normalisation, and no shuffle-null was computed for stain-normalised runs. This robustness check covers the breast anchor only.

### R4. Gastric Lauren

Lauren diffuse was originally a positive control. Signet-ring and diffuse-type tumours have strong H&E morphology and should have scored high, yet the result was 0.536. The cause is not illegibility. In the same pipeline, gastric MSI generalised from 0.899 in development to 0.860 in holdout, whereas Lauren fell from 0.963 to 0.536, a drop of 0.43. The low-resolution pixel-mean baseline, 0.631, exceeded the MIL model, 0.536, so a weak morphological signal exists and the model failed to capture it. The direct cause is that Lauren prevalence varies sharply across institutions and the site-disjoint split concentrated high-prevalence institutions in the evaluation set: 46 per cent in training versus 88 per cent in evaluation.

We therefore describe this case as a methodological instance in which site-disjoint evaluation correctly blocked shortcut learning, and confine the low-confidence verdict to gastric Lauren. MSI in the same cohort remains valid. We do not write that H&E cannot see Lauren. The representative cases for the thesis that predictability and substitutability are different claims are breast HER2 and lung KRAS.

### R5. Foundation Models

Foundation-model robustness is moved to Appendix A. In brief, lung endpoint ordering was preserved across UNI, Virchow2 and UNI2-h (histology > EGFR > KRAS; Spearman 1.000 against UNI for both newer models), and the principal negatives reproduced. However, individual molecular axes did not clear chance-exclusion in all models: HPV passed in UNI and UNI2-h but not Virchow2, and colorectal BRAF passed in UNI and Virchow2 but not UNI2-h. This is rank stability and negative-result reproducibility, not model independence of the law.

### R6. External Treatment-Outcome Anchor

As an exploratory check, the anti-HER2 axis score was computed by frozen transfer and used to stratify pathological complete response in an external cohort, evaluated by AUROC with bootstrap confidence intervals and compared against a measured-HER2 probability baseline with DeLong's test [CITE-M12]. This result is `critic_status: pending` and is not promoted to the Abstract or headline claims. It is retained as a pending pointer only: the anti-HER2 axis did not stratify pCR from the H&E-predicted phenotype, directionally consistent with the retrospective map's HER2 negative. Full method and the provisional value are in Appendix C.

### R7. Spatial Mechanism

Spatial transcriptomics analyses are moved to Appendix B because they are `hypothesis_only` and Critic pending. In brief, HER2-positive tumours showed low-expression tumour regions that may help explain subtype-routing error, but mRNA differs from protein and amplification, a spot is not a cell, and the spatial cohort is not the same cohort. The colorectal spatial correlate did not emerge at Visium resolution, leaving that mechanism open.

## 3. Discussion

Our map takes safety of substitution, not predictability, as its criterion. The core of the frame is that the boundary differs by axis and that this boundary is quantified as clinical cost.

Identifying axes not legible in morphology is useful in itself. The frame flags axes where H&E substitution is dangerous, such as breast HER2 and lung KRAS. Gastric Lauren is excluded from this list because it is a site-split artefact rather than an absence of morphology.

In breast HER2, routing from predicted subtype failed consistently in this cohort and routing definition, indicating as cost a region where molecular testing remains necessary. We state the scheme dependence of per-axis cost and restrict robust claims to the anti-HER2 misassignment rate of 1.00 and the confidence interval of the contrast. This negative is not a stain artefact at the phenotype-prediction level: under stain normalisation on the breast anchor, HER2 remained near chance while ER and PAM50 were preserved. The external treatment-outcome anchor is directionally consistent with the HER2 negative, but remains `critic_status: pending`.

Fernandez-Romero 2026 [CITE-I12] is convergent prior work on the HER2 axis rather than a priority boundary. The difference is the question asked: they quantify how much performance drops across breast cohorts, whereas we ask when substitution for a molecular test is safe. The output metric also differs: they report macro-F1/PR-AUC degradation, while we report misassignment rate against a pre-defined treatment-routing rule. The scope differs as well: their study is breast-only, whereas ours uses breast as an anchor plus lung, colorectal, gastric and head and neck. Finally, their split design is patient-stratified random cross-validation, while ours is pre-registered site-disjoint evaluation with sealed scoring. Any causal explanation for the difference in degradation is only a hypothesis, because metrics, foundation models and inclusion criteria differ.

The limits are placed in front. All results are retrospective, cohort-level and `hypothesis_only`; they are not claims of individual-level benefit. The site-disjoint split prevented leakage in which slides from the same tissue source site enter both training and evaluation, but label-institution coupling remains and limits interpretation as pure morphology. The audit confirmed site-label structuring in multiple endpoints: lung histology at V = 1.000, head and neck HPV at V = 0.378, gastric Lauren with prevalence shifting from 0.46 to 0.88, and lung EGFR and KRAS with significant site-label association. This is a necessary condition for confounding, not proof that the model reads site. Site predictability from H&E and leave-one-site-out performance are needed to adjudicate the confounding question.

Stain variation is a separate limit. H&E stain normalisation was not applied in the main pipeline; uncorrected stain variation is a known source of domain shift in pathology imaging [CITE-M17]. The breast-anchor robustness check preserved the HER2-negative pattern, but the cross-cancer headline axes, head and neck HPV and lung histology, were not stain-verified. The two headline results most vulnerable to scanner or stain critique therefore carry site-confounding flags and are not yet stain-verified.

On model independence, the relative AUROC ordering among lung endpoints and the principal negative results were preserved across three foundation models, whereas whether an individual molecular axis clears chance-exclusion varied by model. This is ordering stability, not model independence of the law as a whole.

PAM50 provenance is stated explicitly because the endpoint carries weight in the breast anchor. The canonical PAM50 endpoint is CLAM-MB, uni_v1, 4-class (`pam50_clam_mb_uni_v1_4class`), not the v2 CLAM-SB endpoint used for ER/PR/HER2. PAM50 labels from the manifest nearest-centroid computation [CITE-M2] show 57.0 % concordance (514/902) against cBioPortal PanCancer Atlas SUBTYPE labels [CITE-M3], i.e. 43.0 % discordance (388/902), with largest disagreements LumB↔LumA and Normal→LumA. Coverage was 97.2 %, so the fallback condition for using local labels because cBioPortal coverage is short was not met. This remains a label-source reconciliation limit, not a hidden error.

Clinically, this observational map identifies negative axes where H&E substitution is clearly dangerous, undecided axes that present data cannot adjudicate, and morphology-legible axes that justify prospective validation. The paper makes no clinical recommendation and no claim of wholesale replacement. Its contribution is not beating the gold standard, but making predictable, as a map, when inexpensive H&E can pre-screen or triage molecular testing and when it cannot.

## 4. Methods

### M1. Cohorts and Labels

Breast cancer (TCGA-BRCA, about 1,010 diagnostic slides) [CITE-M1] served as the anchor, together with lung (TCGA-LUAD/LUSC) [CITE-M18], colorectal (TCGA-COAD/READ) [CITE-M19], gastric (TCGA-STAD) [CITE-M20] and head and neck (TCGA-HNSC) [CITE-M21], five cancers in total. Slide counts per cohort were measured in result JSON files: colorectal 523, lung 1,026, gastric 439, head and neck 468.

For the breast PAM50 endpoint, the canonical analysis endpoint is CLAM-MB, uni_v1, 4-class (`pam50_clam_mb_uni_v1_4class`). The labels use a nearest-centroid computation [CITE-M2] as implemented in genefu [CITE-M22]. The manifest labels and cBioPortal PanCancer Atlas SUBTYPE labels [CITE-M3] agree on 57.0 % of overlapping patients (514/902; 43.0 % discordance). The discordance is reported transparently.

### M4. Evaluation Design

All evaluation was performed on a site-disjoint holdout. Slides from the same tissue source site were prevented from entering training and evaluation simultaneously, blocking leakage via institutional fingerprints [CITE-M10]; validation and test were combined for power. Three controls were used: a shuffle-null, a prevalence baseline (0.5) and a subtype-only or pixel-mean baseline. Confidence intervals are reported as 1,000-fold bootstrap 95% CIs [CITE-M11]; where patient clustering matters, CIs were recomputed at the patient level.

### M5. Cost-of-Substitution Frame

Substitution cost is defined by multiplying the confusion matrix by therapeutic distance, giving the misassignment cost incurred where the treatment chosen from the measured marker and the treatment chosen from the H&E-predicted marker diverge. The lead indicator is the distance-independent misroute rate. This frame does not predict drug response and takes no drug structure as input.

### M6. Claim Discipline

Adjudication thresholds are cited only from the sealed pre-registration document, not from slides or observed values. The power rule, fewer than 25 positives → exploratory → INCONCLUSIVE, is not moved after seeing results and is applied symmetrically to confirmation and refutation. All outputs are `hypothesis_only` and retrospective.

## Appendix A. R5 Foundation-Model Robustness

Holding slides, site-disjoint holdout and endpoints fixed, we retrained CLAM after swapping only the embedding space: UNI 1024-d, Virchow2 2560-d and UNI2-h 1536-d. The claim concerns ordering, not absolute values, and not model independence of individual axes.

Across all three embedding spaces, lung endpoints kept the order histology > EGFR > KRAS. Spearman correlation against UNI was 1.000 for both newer models, and 5-seed chance-exclusion passed 6 of 6 in lung. This is ordering stability, not model generality and not confirmation.

Single-endpoint results diverged by model. Head and neck HPV passed in UNI and UNI2-h, but in Virchow2 the point estimate was high (0.9199) while the shuffle-null spread was wider, so it did not clear the pre-specified criterion. Colorectal BRAF passed in only two of three models: UNI and Virchow2; UNI2-h did not clear the low-power shuffle-null.

Two kinds of negative must be distinguished. Gastric Lauren fails chance-exclusion in all three (0.536 / 0.640 / 0.603), reproducing the site-confounding failure of R4 and not proving absence of morphological signal. Gastric ERBB2 amplification fails in all three (0.644 / 0.668 / 0.585) because real ≈ null in every case, consistent with absence of signal. Lumping them would re-introduce the error R4 corrects.

Head and neck EGFR amplification shows that clearing chance-exclusion is not itself evidence of signal. It is formally recorded as passing in UNI2-h, yet its real AUROC is 0.505, essentially chance; the shuffle-null spread was narrow, so the threshold sat correspondingly low.

**Table R5. Multiple foundation models (5-seed canonical)**

| Endpoint | UNI | Virchow2 | UNI2-h | 5-seed chance-exclusion |
|---|---|---|---|---|
| Head and neck HPV | 0.9594 | 0.9199 | 0.9559 | UNI and UNI2-h pass / Virchow2 fails (margin −0.0035) |
| Colorectal BRAF | 0.8676 | 0.8798 | 0.8978 | UNI and Virchow2 pass / UNI2-h fails |
| Gastric MSI-H | 0.8599 | 0.8795 | 0.8670 | Both newer models pass |
| Gastric Lauren (positive control) | 0.5364 | 0.6404 | 0.6033 | All three fail (site-confounding, reproduced) |
| Gastric ERBB2 amplification | 0.6444 | 0.6682 | 0.5845 | All three fail (signal absent, reproduced) |
| Lung (histology > EGFR > KRAS) | Order preserved | Order preserved | Order preserved | Spearman 1.000; 6/6 |

## Appendix B. R7 Spatial Transcriptomics

This exploratory analysis examines a possible mechanism behind the map using public spatial transcriptomics. Everything here is `hypothesis_only` and has not passed Critic, so it should be read as mechanistic support rather than as a headline.

Even in confirmed HER2-positive tumours (8 patients), some tumour spots show ERBB2 levels indistinguishable from the non-tumour reference on the same section. The median probability that a tumour spot's ERBB2 falls below the reference is 0.158; in all 8 patients the confidence interval excludes 0 and the kill-test that rules out diffusion and depth artefacts is passed (interior-only 7/8, depth-conditioned 3/3). Because a patient carries only one label, these low-expression regions cannot be represented. This strengthens a candidate mechanism for subtype-routing error: HER2 may not be substitutable because the label discards information, rather than because the prediction is noisy. We do not assert a limit in principle. Limits are that mRNA differs from protein and amplification, a spot is not a cell, and the ST cohort is not our TCGA cohort.

By contrast, the spatial correlate predicted in colorectal did not emerge at Visium resolution. A 55 µm spot is coarser than nuclear resolution and cannot reach lymphocyte-specific texture; this is a substrate and resolution limit, not a biological refutation. The colorectal spatial mechanism remains open, and the appropriate test is a substrate with co-registered H&E.

## Appendix C. Additional Methods

### M2. Tiling and Embedding

Each whole-slide image was tiled into 256×256 pixel patches at 20× magnification, tissue was separated from background by Otsu thresholding [CITE-M4], and a cap of 5,000 tiles per patient was imposed. The headline embedding is UNI v1 (1024-d) [CITE-M5]. For the model-independence test, the same coordinates were re-extracted with Virchow2 [CITE-M6] (2560-d, CLS token concatenated with mean patch token, register tokens excluded) and UNI2-h (1536-d) [CITE-M23]. The slide-level EXAONE Path 2.0 [CITE-M7] interface is incompatible with the coordinate-based pipeline and was excluded from the robustness set. Tiles were resized to 224×224 and channel-normalised with ImageNet statistics [CITE-M8]. H&E stain normalisation was not applied in the main pipeline.

### M3. Model and Training

We used CLAM-SB attention MIL [CITE-M9] with hidden 512, attention 256, 40–50 epochs and seed fixed at 42. Predictions were produced per slide and then aggregated per patient.

### M7. External pCR Anchor

The anti-HER2 axis score was computed by frozen transfer, meaning the anchor model was applied without further training, used to stratify pCR in an external cohort [CITE-M25], and evaluated by AUROC with bootstrap 95% confidence intervals. It was then compared with the measured-HER2 probability baseline using DeLong's test [CITE-M12]. The pre-specified benchmark was defined as approaching and overlapping the benchmark of Farahmand and colleagues [CITE-M13] (0.80, 95% CI 0.69 to 0.88). This anchor is provisional and is not carried into the Abstract or headline claims.

### M8. Multi-Model Robustness

Because embedding spaces are not interchangeable across foundation models [CITE-M14], CLAM was refitted from scratch in each space so that the comparison is made at the same level. The adjudication criterion is 5-seed shuffle-null chance-exclusion: real AUROC > null mean + 2 × standard deviation, ddof = 1, with seeds 42, 1, 2, 3 and 4. Determinism was verified by 2 re-runs at identical seeds. Final multi-FM Critic sign-off is in progress.

### M9. Site/Batch Confounding Audit

For each endpoint, we quantified whether the site-disjoint split confounds the label with the tissue source site. We computed Cramér's V [CITE-M15] between site and label with a permutation p-value, the train/test prevalence shift, and a permutation test of the site concentration of test positives. This analysis examines a necessary condition for confounding; final adjudication of whether the model actually uses site rests on site predictability from H&E and on leave-one-site-out performance.

### M10. Stain-Normalisation Robustness

To test whether the anchor results are an artefact of uncorrected H&E stain variation, embeddings were re-extracted from the breast-anchor slides with Macenko stain normalisation [CITE-M16], torchstain 1.3.0 [CITE-M24], and a fixed dense-tissue reference tile. CLAM was re-trained on the same folds for ER, HER2 and PAM50. Only phenotype prediction was re-run, not the routing/cost pipeline, and no shuffle-null was computed for the stain-normalised runs. This robustness check covers the breast anchor only; cross-cancer re-extraction under stain normalisation is deferred.

## Figures and Tables

Main text carries one figure. At four pages, a larger figure set cannot be accommodated, and the remaining panels are supporting rather than load-bearing, so they are placed in the appendix where there is no length limit.

**Figure 1 (main text)** Observed map overlaying misassignment loss on the confusion matrix weighted by therapeutic distance. This is the central result of the paper: it fixes both ends of the spectrum in one panel.
`figures/fig01_cost_map.pdf`

**Appendix figures**

**Figure A1** Per-axis misassignment loss and the confidence interval of the headline contrast.
`figures/figA1_axis_cost.pdf`

**Figure A2** Power ceiling: holdout positives per axis and the boundary of decidability (R2, Table R2).
`figures/figA2_power_ceiling.pdf`

**Figure A3** Site confounding audit: site-label association per endpoint (R1 footnote, Appendix C M9).
`figures/figA3_site_confounding.pdf`

**Figure A4** Multi-model comparison: order preservation across UNI, Virchow2 and UNI2-h, and the diverging single endpoints (Appendix A, Table R5).
`<FILL: 아직 렌더되지 않음>`

A pipeline schematic was dropped rather than newly drawn. No such figure exists in the repository, and the pipeline is fully described in M1 and M4.

<!-- CONDENSATION LOG -->

Main-text word count excluding appendix and this log: approximately 3,180 words.

Abstract: Trimmed prose while retaining the distinction between predictability and substitution, five-cancer scope, HPV positive, HER2 negative, stain-normalisation caveat, power limitation, retrospective status and prospective-validation requirement. Deleted only circulation comments.

Introduction: Compressed background literature and contribution list. Kept the cost-of-substitution frame, five-cancer boundary, claim-discipline caveat and distinction from prior breast prediction and drug-sensitivity work. Deleted only venue/team-circulation framing and redundant prose.

R0: Converted from a numbered subsection into an untitled lead-in paragraph as requested. Kept the single powered non-control confirmation, the undecided mutation/amplification axes, and the explicit non-claim that the law was validated across five cancers.

R1: Kept the spectrum, Table R1, HPV caveats, positive controls, HER2 negative, ERBB2 null comparison, KRAS subtype-only baseline and epistemic-status distinction. Shortened figure narration. Deleted only duplicate provenance comments and internal review notes.

R2: Kept the twenty-five-positive rule, all Table R2 axes and the refusal to lower 25 to 24. Moved exploratory split alternatives into brief text rather than expanded supplement discussion. Deleted no substantive limitation.

R3: Kept anti-HER2 misassignment rate, scheme dependence, contrast caveat, stain-normalisation robustness, and the limits that routing/cost was not re-run and no shuffle-null was computed. Deleted only internal change-note text.

R4: Kept the site-split artefact interpretation, all numeric comparisons, and the warning not to interpret Lauren as morphology-invisible. Deleted only draft-history phrasing.

R5: Moved detailed foundation-model robustness to Appendix A. Left the main-text defence against model artefact: lung ordering preserved, negatives reproduced, but individual axes vary by model and the law is not model-independent.

R6: Kept in the main text as provisional and Critic pending, with no headline promotion. Moved method detail to Appendix C. Deleted the external cohort institution name for double-blind compliance.

R7: Moved spatial-transcriptomics detail to Appendix B. Left a main-text pointer and preserved the hypothesis-only and Critic-pending limits.

Discussion: Compressed overall interpretation while keeping safety of substitution as the criterion, HER2 and KRAS as dangerous substitution axes, Lauren exclusion, retrospective hypothesis-level status, site/batch confounding limits, stain-variation limits, model-independence caveat, PAM50 provenance, and clinical non-recommendation. Added the requested Fernandez-Romero 2026 positioning as convergent prior work and convergent HER2-axis evidence without priority claims.

Methods: Main text retains only cohort definitions, evaluation design, cost frame and claim discipline. Moved tiling, embedding, model/training, pCR anchor, multi-model robustness, site audit and stain-normalisation implementation to Appendix C. Removed visible repository paths and sealed-document filenames for double-blind compliance.

Appendix A: Contains detailed R5 content and Table R5. Preserved all model-specific numbers and caveats.

Appendix B: Contains detailed R7 spatial-transcriptomics content. Preserved hypothesis-only status, all spatial-transcriptomics numbers, and all biological and substrate limitations.

Appendix C: Contains M2, M3 and M7–M10 methods moved from the main text. Removed repository paths and internal provenance filenames. Kept citation markers and all numeric values exactly as copied from the source.

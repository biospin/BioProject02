# Paper C — ML4H 2026 Circulation Draft v2 (Full IMRaD)

> **Status.** Updated full draft for **kkkim (Leader) review** and team circulation ahead of ML4H 2026. This is a *review draft*, not a submission. Built on top of the v1 full draft ([`DRAFT_paperC_full_en.md`](DRAFT_paperC_full_en.md)) and the detailed section skeletons ([`sections/`](sections/)), refreshed against the latest result files (multi-FM 5-seed, BIOP02-147 stain-normalisation, PAM50 label-source reconciliation). Change log = [`DRAFT_ML4H_v2_CHANGELOG.md`](DRAFT_ML4H_v2_CHANGELOG.md).
> **All numbers are measured** from result files; each headline value carries an inline `<!-- src: ... -->` comment so kkkim can cross-check. No number was introduced from memory or from slides. Status `hypothesis_only`, retrospective, `critic_status: pending`.
> **Claim discipline.** Paper C is a pre-registered five-cancer study (breast anchor + lung, colorectal, gastric, head and neck — a deliberate boundary, not an open pan-cancer atlas). This is **not** a drug-response-prediction model (no drug structure input, hypothesis-only output). Headline claims stay **provisional** until the pre-registered law and held-out tests clear Critic sign-off.
> **Venue note.** Prior project artifacts targeted npj Precision Oncology + medRxiv ([`SUBMISSION_PREP.md`](SUBMISSION_PREP.md) L4). This draft is written as a **venue-neutral full IMRaD** manuscript so it can serve either target; **ML4H 2026 length/format constraints are `<FILL: ML4H 2026 CFP 원문 — 사람 확정>`** and a 29 KB IMRaD draft likely needs compression for a workshop-style venue (Leader decision).
> **Author-facing metadata is unconfirmed.** Authors, order, affiliation, corresponding author/email, funding/acknowledgments (GPU provider), and COI are all `<FILL: 팀 확정>` and must be settled by the team before any public release.

---

## Abstract

That a tumour's molecular phenotype can be predicted from haematoxylin-and-eosin (H&E) histology, and that such a prediction may clinically replace molecular testing, are two different claims. We propose a cost-of-substitution frame that separates them. Applying the frame across cancers — converting prediction errors into the misassignment cost of a pre-specified treatment routing (a normalised measure of how far treatment assignment is displaced, not a monetary cost) — we confirmed a powered positive signal for HPV in head and neck cancer and quantified, for most mutation and amplification axes, that the present data cannot decide. Across five cancers (breast as the anchor plus lung, colorectal, gastric and head and neck) we sealed and tested a pre-registered morphological-correlate law under one protocol, but powered confirmation is limited. The two ends of the observed spectrum are fixed by measurement: an axis that is legible in morphology (head and neck HPV, holdout AUROC 0.959 — the only powered, non-control positive result in the pre-registered holdout of the primary model UNI; lung LUSC histology 0.939 as a positive control), and a negative anchor that showed no signal supporting substitution in this cohort and routing definition (breast HER2 0.599). In the breast anchor, anti-HER2 routing driven by H&E-predicted subtype failed consistently on the HER2 axis in this cohort and routing definition (misassignment rate 1.00) — an honest negative that shows, as cost, where molecular testing remains necessary. The underlying HER2 phenotype prediction remained near chance under H&E stain normalisation, so the HER2 negative is not an artefact of stain variation (the routing/cost step itself was not re-run under normalisation). Most clinically important mutation and amplification axes are exploratory because holdout positives fall short of 25 under our pre-registered site-disjoint split. Some exploratory results are compatible with the morphological-correlate hypothesis, but we lacked the power to establish the direction of the law across mutation and amplification axes. We propose "safety of substitution", not "predictability", as the decision criterion. All results are retrospective and hypothesis-level and require prospective validation.

<!-- v2 change: Yale pCR 0.533 result REMOVED from Abstract (critic_status pending → provisional, not promotable to body). Stain-normalisation robustness of the HER2 negative added. -->

---

## 1. Introduction

Research using AI to analyse histopathological H&E images has been pursued across several organs as digital pathology has spread [CITE-I1]. With the wider use of CLAM-family weakly supervised multiple-instance learning [CITE-I2], work expanded in urological cancers [CITE-I3], breast cancer [CITE-I4], pancreatic cancer [CITE-I5], and other settings, and knowledge distillation and pathology foundation models have improved performance [CITE-I6]. Within this field, there has been persistent interest in predicting the molecular state of tissue from images. The reason lies in what is being replaced. IHC staining and tissue-destructive molecular tests, the usual methods for assessing molecular state, are generally costly and slow, whereas H&E staining is relatively inexpensive and is already acquired in routine care [CITE-I7]. Yet these molecular tests play important roles in early detection, prognostic prediction, and treatment direction across several cancer types [CITE-I8]. If inexpensive images can substitute for expensive tests, the potential gain is large. And the basic fact that molecular state can be learned and predicted from H&E has been shown repeatedly [CITE-I9].

But being predictable does not mean it is acceptable to replace a molecular test clinically. Reporting predictive performance alone is silent about the clinical cost of substitution — the loss incurred when a wrong prediction assigns the wrong treatment [CITE-I10]. The same AUROC carries entirely different clinical consequences depending on which treatment decision the error lands in [CITE-I11]. This gap is where the present work sits.

We propose a cost-of-substitution frame. By converting prediction errors into the misassignment cost of treatment routing, we ask, for each molecular axis, whether H&E can substitute cheaply or whether molecular testing is required. The criterion is safety of substitution, not predictability. The frame does not predict drug response; it operationalises only the substitution cost from marker to treatment assignment, and it takes no drug structure as input.

We test this with a pre-registered morphological-correlate law across five cancers, anchored on breast (plus lung, colorectal, gastric and head and neck). The law states that H&E can cheaply stand in for a test only when the molecular alteration has a morphological correlate recognisable at H&E resolution. The five cancers are a deliberate boundary for testing the law, not an open pan-cancer atlas expansion; and sealing predictions before results does not by itself confer confirmatory strength — it provides claim discipline that suppresses post-hoc selection.

This paper makes four contributions. First, the cost-of-substitution frame itself, together with the separation of confirmable axes from undecided ones obtained by applying one pre-registered protocol across five cancers. Second, an honest negative anchor: the breast HER2 axis shows no signal supporting H&E-based substitution, and this negative is robust to H&E stain normalisation. Third, claim discipline — explicit adjudication of insufficient power on the many mutation and amplification axes that our pre-registered split cannot decide, rather than reporting only the axes that happen to score high. Fourth, the framing of a different question — "when is substitution safe?" — rather than a contest over predictive accuracy. Unlike single-cohort breast prediction [CITE-I12] or drug-sensitivity prediction [CITE-I13], this study contributes a methodological frame that applies one pre-registered evaluation protocol and a substitution-cost lens across a multi-cancer cohort. An external treatment-outcome check (Yale pCR) and a spatial-transcriptomics mechanistic look are reported only as provisional, Critic-pending exploratory analyses (§R6, §R7), not as contributions.

<!-- v2 change: contribution list cut from five to four. v1 (iii) "Yale + ST 비용 증명" and (iv) "Yale 앵커" removed as standalone contributions because Yale is critic-pending and ST is hypothesis_only. -->

---

## 2. Results

### R0. What this paper actually establishes

We tested about fifteen endpoints across five cancers under pre-registration. Of these, exactly one powered, non-control confirmation was obtained: HPV in head and neck cancer. Most remaining mutation and amplification axes fell short of twenty-five holdout positives and therefore remain undecided under the pre-registered rule. The text accordingly does not claim that "the law was validated across five cancers".

We establish two things. First, both ends of the map are fixed by measurement under one protocol: which axes are clearly legible in morphology and which are not, measured against identical controls and adjudication criteria. Second, we quantify why the middle of the map cannot be decided at present. That is the power ceiling of R2.

### R1. The substitution-cost spectrum observed in the pre-registered site-disjoint split across five cancers — confirmable axes versus undecided axes

This section converts per-axis substitutability into cost and lays it out as a map. The central figure is Fig2, which overlays cost on the confusion matrix weighted by therapeutic distance; per-axis cost and the confidence interval of the headline contrast are shown in Fig3.

**The legible end.** In the holdout of the primary model UNI, head and neck HPV reached AUROC 0.959 [0.921–0.986] with 26 positives, well above the pre-registered threshold of 0.80 (the limits that remain under model substitution and the site-label structure audit are stated in footnote † to Table R1). <!-- src: experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md L17 (0.9594, n_pos=26); pre-reg threshold 0.80 = SUBSTITUTABILITY_LAW_PREREGISTRATION.md --> This axis is shaped not by a mutation but by a viral infection (non-keratinising, basaloid morphology), so it illustrates a possible extension of the law's "morphological correlate" clause to a new kind (confirmation is confined to the HPV axis). The positive controls behaved as expected: lung LUSC histology 0.939 [0.905–0.967] (153 positives) and head and neck grade 0.815 [0.742–0.882] (41 positives). <!-- src: LAW_HELDOUT_SCOREBOARD.md L18, L20 -->

**The illegible end.** Breast HER2 is 0.599, effectively at chance; in this cohort and routing definition it shows no signal supporting H&E-based substitution and therefore serves as the negative anchor. <!-- src: LAW_HELDOUT_SCOREBOARD.md L31 (0.599, anchor near-random) --> Gastric ERBB2 amplification is 0.644, but the shuffle-null is 0.641 — effectively identical, so no signal should be inferred (this is why the earlier "blind hit" citation was withdrawn in the G2 review). <!-- src: LAW_HELDOUT_SCOREBOARD.md L25 (real 0.6444 ≈ null 0.6406) --> Lung KRAS-G12C is 0.681, yet a baseline that uses no image at all and predicts from histology alone reaches 0.793, higher still. The apparent predictive power therefore comes from LUAD skew rather than from mutation morphology. <!-- src: LAW_HELDOUT_SCOREBOARD.md L22; experiments/crosscancer/LUNG_NSCLC/full/SUBTYPE_BASELINE_NOTE.md -->

Every endpoint is reported alongside a shuffle-null (5-seed), a prevalence baseline (0.5) and a pixel-mean baseline; the lung mutation axes additionally carry a subtype-only baseline. Epistemic status must also be distinguished. Lung, gastric and head and neck were sealed-forward tests with predictions committed before results, whereas colorectal was analysed after results were already available and is therefore excluded from the tally of powered, sealed confirmations. <!-- src: LAW_HELDOUT_SCOREBOARD.md "인식론 구분"; COLORECTAL/full/LAW_TEST.md top banner -->

**Table R1 — Observed substitution-cost spectrum (UNI canonical). "Cost" here is not monetary: it is treatment misassignment loss (misassignment rate).**

| Cancer | Axis | Role | AUROC [95% CI] | Holdout n_pos / control baseline | Morphological correlate | Verdict |
|---|---|---|---|---|---|---|
| Head and neck | HPV | Legible axis (viral) | 0.959 [0.921–0.986] | 26 positives | Present (non-keratinising, basaloid) | **Single-FM, site-disjoint confirmation** (model-independence and site confounding untested) † |
| Lung | LUSC histology | Positive control | 0.939 [0.905–0.967] | 153 positives | Morphology itself | Pass ‡ |
| Head and neck | Grade | Positive control | 0.815 [0.742–0.882] | 41 positives | Present | Pass |
| Colorectal | BRAF V600E | Retrospective | 0.882 [0.817–0.938] | 15 positives | Present (serrated/MSI co-occurrence) | Consistent; retrospective, underpowered, exploratory (excluded from confirmation tally) |
| Gastric | MSI-H | Legible axis | 0.860 (development 0.899) | 24 positives | Present (immune) | Undecided (1 short) |
| Lung | EGFR activating | Graded | 0.852 | 15 positives | Partial | Undecided |
| Lung | KRAS-G12C | Required axis | 0.681 (subtype-only 0.793) | 14 positives | Absent (histology skew) | Undecided |
| Gastric | ERBB2 amplification | Required axis (breast replicate) | 0.644 (shuffle 0.641) | 14 positives | Absent | Underpowered; no observed signal |
| Breast | HER2 | Anchor (required axis) | 0.599 | near-random | Absent | **No signal supporting substitution · negative anchor** |
| Gastric | Lauren diffuse | (Original positive control) | 0.536 (development 0.963) | pixel-mean 0.631 | Weakly present | Site-split case (R4) |

<!-- v2 change: CRC BRAF corrected from v1's mismatched "0.868 [0.780–0.938]" to the point+CI pair reported together in COLORECTAL/full/LAW_TEST.md L14 = 0.8817 [0.817, 0.938] (holdout161, the canonical routing split). The 5-seed R5 value 0.8676 is a DIFFERENT split (holdout151) — see LAW_TEST.md L18 numeric-consistency note. -->

† HPV robustness passed 5-seed chance-exclusion in only 2 of 3 foundation models (UNI and UNI2-h) and did not clear the pre-specified criterion in Virchow2 (real 0.9199 < threshold 0.9234, margin −0.0035 — a wide shuffle-null spread, not signal absence; see R5). <!-- src: experiments/crosscancer/MULTIFM_COMPARISON.md §5; CROSSCHECK_5SEED_MULTIFM.md HPV/virchow2 row --> The site audit also found site-label structuring (Cramér's V = 0.378). HPV is the single powered anchor that fixes one end of the map — not a generalisation of the law and not a model-independent confirmation. <!-- src: experiments/kkkim/20260805_site_audit/site_audit_results.json -->
‡ For lung histology (positive control) the site audit gave V(site, label) = 1.000: TCGA-LUAD/LUSC institution codes coincide 100% with histology, so the morphological signal cannot be separated from the site signature. This limit is stated explicitly wherever the positive control is interpreted. <!-- src: site_audit_results.json -->

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

<!-- src: LAW_HELDOUT_SCOREBOARD.md 통합 표, n_pos column -->

### R3. Breast anchor — anti-HER2 routing from predicted subtype does not support substitution in this cohort

Under the pre-specified routing definition and in this cohort, anti-HER2 assignment based on H&E-predicted subtype did not support identification of treatment candidates (anti-HER2 misassignment rate 1.00). <!-- src: experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost.json, therapeutic_distance.json --> The misassignment rate and its cost interpretation depend on the stated operating point, however, and the analysis that pre-specifies that threshold is not yet complete. This is an observation showing, as misassignment loss, that H&E substitution may not be safe in this region.

One constraint must be stated honestly. Per-axis cost flips between endocrine therapy and chemotherapy depending on the routing scheme (0.378 versus 0.035; 0.105 versus 0.510). The only claims robust to a change of scheme are the anti-HER2 misassignment rate of 1.00 and the fact that the confidence interval of the headline contrast excludes 0; we do not extend these into a claim that "the other axes are safe".

The HER2 negative is not an artefact of stain variation, at the level of phenotype prediction. In a stain-normalisation robustness check on the breast anchor (Macenko normalisation, embeddings re-extracted and CLAM re-trained on the same folds), the HER2 *phenotype* prediction remained near chance (AUROC 0.641 versus 0.599 without normalisation in Table R1 — slightly higher, still far below the legible axes), while ER stayed high (0.917 versus 0.901) and PAM50 was preserved (0.740 versus 0.759). <!-- src: experiments/kkkim/20260819_stain_norm_robustness/clam_rerun/sjpark/{her2_status,er_status,pam50}_clam*_uni_stainnorm/metrics.json (0.6408, 0.9166, 0.7396); non-normalised anchor values from Table R1 / LAW_HELDOUT_SCOREBOARD.md --> The rank of the anchor endpoints (ER high > PAM50 mid > HER2 near-chance) is therefore preserved with and without stain normalisation, indicating that "H&E cannot cheaply substitute for HER2" is not produced by uncorrected stain differences. Two scope limits are stated honestly: the routing/cost pipeline (misassignment rate 1.00) was **not** re-run under normalisation — only phenotype prediction was; and no shuffle-null was computed for the stain-normalised runs, so "near chance" here rests on the value and its comparison to ER/PAM50, not on a null. This robustness check covers the breast anchor only; the headline cross-cancer results (HPV, lung) could not be re-checked because their raw slides were lost and re-extraction is deferred (see Discussion, Limitations).

<!-- v2 change: stain-normalisation robustness paragraph added (BIOP02-147). Numbers are the stain-normalised triplet reported as their own robustness check; a precise paired before/after table is NOT built because the matched non-normalised baseline provenance is ambiguous (scoreboard anchor HER2=0.599 vs same-fold uni_v1 metrics.json HER2=0.5509). Comparison stated qualitatively per that ambiguity. -->

### R4. Gastric Lauren diffuse is a site-split artefact, not an absence of morphology

An earlier skeleton presented this result as evidence for an axis genuinely invisible to morphology; our own diagnosis does not support that reading.

Lauren diffuse was originally a positive control. Signet-ring and diffuse-type tumours have strong H&E morphology and should have scored high, yet the result was 0.536. The cause is not illegibility. In the same pipeline gastric MSI generalised normally, from 0.899 in development to 0.860 in holdout, whereas Lauren alone fell from 0.963 to 0.536 — a drop of 0.43. Moreover the low-resolution pixel-mean baseline (0.631) exceeded the MIL model (0.536), so a weak morphological signal does exist and the model failed to capture it. The direct cause is that Lauren prevalence varies sharply across institutions and the site-disjoint split concentrated high-prevalence institutions in the evaluation set (46 per cent in training versus 88 per cent in evaluation). <!-- src: experiments/crosscancer/GASTRIC_STAD/full/LAUREN_POSCONTROL_DIAGNOSIS.md; LAW_HELDOUT_SCOREBOARD.md 결론 #3 -->

The text therefore describes this case as a methodological instance in which site-disjoint evaluation correctly blocked shortcut learning, and confines the low-confidence verdict to gastric Lauren. MSI in the same cohort remains valid. We do not write that "H&E cannot see Lauren". The representative cases for the thesis that predictability and substitutability are different claims are breast HER2 and lung KRAS, not Lauren.

### R5. The ordering of axes in the map is preserved across foundation models (Supplement)

Holding slides, site-disjoint holdout and endpoints fixed, we retrained CLAM after swapping only the embedding space (UNI 1024-d, Virchow2 2560-d, UNI2-h 1536-d). The claim of this section concerns ordering, not absolute values, and not model independence of individual axes.

The centre of gravity is the preserved ordering in lung. Across all three embedding spaces the three lung endpoints kept the order histology > EGFR > KRAS, Spearman correlation against UNI was 1.000 for both newer models, and 5-seed chance-exclusion passed 6 of 6 in lung. <!-- src: experiments/crosscancer/CROSSCHECK_5SEED_MULTIFM.md (Spearman 1.000, 6/6 PASS) --> This is ordering stability, however — not model generality and not confirmation.

Single-endpoint results diverge by model, and we report this rather than hide it (Table R5). The headline, head and neck HPV, passed in UNI and UNI2-h, but in Virchow2 the point estimate was equally high (0.9199) while the shuffle-null spread was wider, so it did not clear the pre-specified criterion. Colorectal BRAF likewise passed in only two of three models (UNI and Virchow2; UNI2-h did not clear the low-power shuffle-null). <!-- src: MULTIFM_COMPARISON.md §1, §5 -->

Two kinds of negative must be distinguished, because both reproduce across all three models but for different reasons. Gastric Lauren fails chance-exclusion in all three (0.536 / 0.640 / 0.603) — this is the **site-confounding failure** of R4 reproducing model-independently, i.e. the artefact is not specific to UNI, not an absence of morphological signal. Gastric ERBB2 amplification fails in all three (0.644 / 0.668 / 0.585) because real ≈ null in every case — this is a genuine **absence of signal**. Lumping the two would re-introduce the very error R4 corrects. <!-- src: MULTIFM_COMPARISON.md §5 "lauren·erbb2는 전 FM FAIL(각각 site-교란·신호0)" -->

One case shows plainly that clearing chance-exclusion is not itself evidence of signal. Head and neck EGFR amplification is formally recorded as passing in UNI2-h, yet its real AUROC is 0.505, essentially chance; the shuffle-null spread was narrow, so the threshold sat correspondingly low. That is a pass earned by a low bar rather than by performance, and we do not mark this axis as passing or positive. <!-- src: 02_results.md R5 paragraph; braveji G2 finding (BIOP02-101) -->

What this section can state therefore narrows to two things: the ordering of axes in the lung map was preserved across three models, and the negative results reproduced independently of model. Conversely, we do not write that the findings were "confirmed independently of the foundation model": the headline single-endpoint confirmations (head and neck HPV, colorectal BRAF) each cleared 5-seed chance-exclusion in only two of three models, so this is rank stability, not model independence.

**Table R5 — Multiple foundation models (5-seed canonical)**

| Endpoint | UNI | Virchow2 | UNI2-h | 5-seed chance-exclusion |
|---|---|---|---|---|
| Head and neck HPV | 0.9594 | 0.9199 | 0.9559 | UNI and UNI2-h pass / **Virchow2 fails (margin −0.0035)** |
| Colorectal BRAF | 0.8676 | 0.8798 | 0.8978 | UNI and Virchow2 pass / **UNI2-h fails** |
| Gastric MSI-H | 0.8599 | 0.8795 | 0.8670 | Both newer models pass |
| Gastric Lauren (positive control) | 0.5364 | 0.6404 | 0.6033 | All three fail (site-confounding, reproduced) |
| Gastric ERBB2 amplification | 0.6444 | 0.6682 | 0.5845 | All three fail (signal absent, reproduced) |
| Lung (histology > EGFR > KRAS) | Order preserved | Order preserved | Order preserved | Spearman 1.000 · 6/6 |

<!-- src: CROSSCHECK_5SEED_MULTIFM.md, MULTIFM_COMPARISON.md (5-seed canonical). Colorectal BRAF row here uses the 5-seed holdout151 values (0.8676 etc.), distinct from Table R1's holdout161 routing value 0.882 — different splits, same marker, CI-consistent. -->

### R6. External treatment-outcome anchor (Yale pCR) — provisional, Critic pending

As an exploratory check, the anti-HER2 axis score was computed by frozen transfer and used to stratify pathological complete response (pCR) in the Yale cohort, evaluated by AUROC with bootstrap confidence intervals and compared against a measured-HER2 probability baseline with DeLong's test. The pre-specified comparison benchmark (a calibration reference, not a pass/fail criterion) was defined as approaching and overlapping the cross-validated AUC of 0.80 [0.69–0.88] reported by Farahmand and colleagues.

**This result is `critic_status: pending` and is not promoted to the body.** It is retained here as a pending pointer only: the anti-HER2 axis did not stratify pCR from the H&E-predicted phenotype, consistent in direction with the retrospective map's HER2 negative, but the number is held out of the Abstract and headline claims until Critic sign-off. Full method and the provisional value are in M7; the Discussion treats it as an empirical anchor that is still awaiting sign-off ("실증 이빨 대기").

<!-- v2 change: R6 demoted. v1 stated AUROC 0.533 [0.411–0.653] as a full result in R6, Abstract, M7, and Discussion. Per task instruction (A3/A4 critic_status pending → provisional, 본문 승격 금지) the number is pulled from Abstract and headline, retained only in M7 (methods-with-provisional-value) and as a pending pointer here. -->

### R7. Mechanism suggested by spatial transcriptomics (supporting, provisional · Critic pending)

This is an exploratory look at the "why" behind the map using public spatial transcriptomics. Everything here is `hypothesis_only` and has not passed Critic, so it should be read as mechanistic support rather than as a headline.

Even in confirmed HER2-positive tumours (8 patients), some tumour spots show ERBB2 levels indistinguishable from the non-tumour reference on the same section. The median probability that a tumour spot's ERBB2 falls below the reference is 0.158; in all 8 patients the confidence interval excludes 0 and the kill-test that rules out diffusion and depth artefacts is passed (interior-only 7/8, depth-conditioned 3/3). <!-- src: 02_results.md R7; experiments/kkkim/angle_A_spatial_erbb2/ --> Because a patient carries only one label, these low-expression regions cannot be represented, so this strengthens a candidate mechanism for subtype-routing error — that "HER2 is not substitutable" may arise from information the label discards rather than from noise in the prediction (we do not assert a limit in principle). Limits: mRNA differs from protein and amplification; a spot is not a cell; and the ST cohort is not our TCGA cohort (mechanistic demonstration, not same-cohort validation).

By contrast the spatial correlate predicted in colorectal did not emerge at Visium resolution. A 55 µm spot is coarser than nuclear resolution and cannot reach lymphocyte-specific texture; this is a substrate and resolution limit, not a biological refutation. The colorectal spatial mechanism therefore remains an open question, and the appropriate test is a substrate with co-registered H&E.

---

## 3. Discussion

Our map takes "safety of substitution", not "predictability", as its criterion. The core of the frame is that the boundary differs by axis and that this boundary is quantified as clinical cost.

Identifying axes that are not legible in morphology is itself information the map provides. The value of the frame lies in flagging axes where H&E substitution is dangerous, such as breast HER2 and lung KRAS; gastric Lauren is excluded from this list because it is a site-split artefact rather than an absence of morphology.

In breast HER2, routing from predicted subtype failed consistently in this cohort and routing definition, which indicates as cost a region where molecular testing remains necessary. We state the scheme dependence of per-axis cost honestly and restrict the robust claims to the anti-HER2 misassignment rate of 1.00 and the confidence interval of the contrast. This negative is not a stain artefact: under stain normalisation on the breast anchor, HER2 remained near chance while ER and PAM50 were preserved. An external treatment-outcome anchor (Yale pCR) is being attached to give the retrospective map empirical teeth; its provisional result is directionally consistent with the HER2 negative, but it is `critic_status: pending` and is not promoted until Critic sign-off.

The limits are placed in front. All results are retrospective, cohort-level and `hypothesis_only`; they are not claims of individual-level benefit.

**Site/batch confounding and stain-variation limits — the two "is it really morphology?" attacks, together.** The site-disjoint split prevented leakage in which slides from the same institution enter both training and evaluation, but the coupling between label and institution (confounding) remains, which limits interpreting performance as a pure morphological signal. A site/batch confounding audit confirmed in five endpoints that the site-disjoint split confounds labels with the tissue source site — lung histology (positive control) at V = 1.000, where morphology and site signature cannot be separated; head and neck HPV at V = 0.378; gastric Lauren, whose prevalence shifts from 0.46 to 0.88; and lung EGFR and KRAS, which also show significant site-label association. This is a necessary condition for confounding, not proof that "the model reads site". Separately, H&E stain normalisation was not applied in the main pipeline; a stain-normalisation robustness check preserved the breast anchor pattern (HER2 near-chance, ER high, PAM50 preserved), but **this check covers the breast anchor only** — the cross-cancer headline axes (head and neck HPV, lung histology) could not be re-checked because their raw slides were lost and re-extraction is deferred. The two headline results a reviewer would most likely attack as scanner/stain artefacts are therefore exactly the ones that carry the site-confounding flags and are not yet stain-verified; we state this openly. Site predictability from H&E and leave-one-site-out performance will adjudicate the confounding question; until then these limits are stated wherever the two anchors are interpreted. <!-- src: site_audit_results.json; experiments/kkkim/20260819_stain_norm_robustness/ (BRCA anchor only); GPU return / raw loss noted in RESUME.md -->

On model independence, the relative AUROC ordering among lung endpoints (histology > EGFR > KRAS) and the principal negative results were preserved across all three foundation models evaluated, whereas whether an individual molecular axis clears chance-exclusion varied by model. This is ordering stability, not model independence of the law as a whole: the headline single-endpoint confirmations (HPV, colorectal BRAF) each cleared chance-exclusion in only two of three foundation models. We note that a 20-seed re-check indicated the Virchow2 HPV threshold stabilises (to ≈0.837) and would flip that cell to a pass, but **this verdict change is not adopted** pending braveji's Critic confirmation (BIOP02-123); the reported status remains "2 of 3 models". <!-- src: 04_discussion.md item 6; experiments/kkkim/20260820_shuffle_null_20seed/ -->

**Anchor phenotype-prediction reliability (breast).** Four limitations are placed in front rather than hidden. (i) The added value of morphology is endpoint-specific and not additive over trivial baselines: ER/PR prediction beats a slide-mean-embedding baseline externally (+0.128/+0.223) but is overtaken by a subtype-only baseline externally, and HER2 does not beat even the mean-embedding baseline; among the four endpoints only PAM50 4-class clears a valid baseline (mean-embedding) both internally and externally with non-overlapping CIs (+0.089/+0.165). (ii) Attention-counterfactual fidelity is claimed at the probability level only (10–23× over random removal), not at slide-ranking (AUROC) level, because MIL signal is redundant. (iii) HER2 is an honest negative (reject on both baseline and cross-dataset checks), the map's anchor, not a pipeline failure. (iv) Therapeutic hypotheses inherit cell-line-to-patient transfer limits and are `hypothesis_only`. <!-- src: 04_discussion.md Limitations 1–4; experiments/braveji/BIOP02-75_critic_gate/GATE_STATUS.md -->

**PAM50 label-source note.** PAM50 carries weight in this paper (it is the one anchor endpoint clearing a valid baseline internally and externally). The manifest PAM50 labels (local/genefu computation, Parker 2009) show 57.0 % concordance (514/902) against the cBioPortal PanCancer Atlas SUBTYPE labels, i.e. 43.0 % discordance (388/902), with the largest disagreements being LumB↔LumA and Normal→LumA. <!-- src: agents/data/manifests/pam50_source_reconcile_biop02-74.json (concordance_pct=57.0, n_match=514/n_overlap=902) --> Because measured cBioPortal coverage of the manifest cohort is high (97.2 %), the pre-registered fallback condition for using the local/genefu labels (`split_policy_v0.md §10`: fallback authorised only if cBioPortal coverage is short) was **not** met. Which PAM50 label source is canonical for the anchor endpoint is therefore an open reconciliation item for Methods; this is flagged rather than resolved here. <!-- src: pam50_source_reconcile_biop02-74.json policy_check field -->

The clinical and research implications are as follows. This observational map identifies negative axes where H&E substitution is clearly dangerous (breast HER2) and undecided axes that present data cannot adjudicate, and thereby serves as a decision frame for prioritising future prospective validation. Where H&E screening would actually reduce cost cannot be recommended before prospective validation, and this paper makes no clinical recommendation and no claim of wholesale replacement. The value concentrates on molecular tests that are expensive, slow or scarce, and on resource-limited settings. In short, our contribution is not "beating the gold standard" but "making predictable, as a map, when inexpensive H&E can pre-screen or triage molecular testing and when it cannot".

---

## 4. Methods

### M1. Cohorts and labels
Breast cancer (TCGA-BRCA, about 1,010 diagnostic slides) serves as the anchor, together with lung, colorectal, gastric and head and neck — five cancers in total. Slide counts per cohort are measured in the result JSON files (colorectal 523, lung 1,026, gastric 439, head and neck 468). <!-- src: 03_methods.md M1 --> Label provenance and patient-level splits are managed under `agents/data/`, and the pre-registered axis boundaries are recorded in the sealed document (`experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md`). For the breast PAM50 endpoint, the manifest labels (local/genefu, Parker 2009) and the cBioPortal PanCancer Atlas SUBTYPE labels agree on 57.0 % of overlapping patients (514/902; 43.0 % discordance); because cBioPortal coverage of the cohort is high (97.2 %), the pre-registered fallback condition (`split_policy_v0.md §10`) for using the local labels was not met, and canonicalisation of the PAM50 label source is an open reconciliation item. <!-- src: pam50_source_reconcile_biop02-74.json -->

### M2. Tiling and embedding
Each whole-slide image was tiled into 256×256 pixel patches at 20× magnification, tissue was separated from background by Otsu thresholding, and a cap of 5,000 tiles per patient was imposed. The headline embedding is UNI v1 (1024-d); for the model-independence test the same coordinates were re-extracted with Virchow2 (2560-d, CLS token concatenated with mean patch token, register tokens excluded) and UNI2-h (1536-d). The slide-level EXAONE Path 2.0 interface is incompatible with the coordinate-based pipeline and was excluded from the robustness set. Tiles were resized to 224×224 and channel-normalised with ImageNet statistics. H&E stain normalisation was not applied in the main pipeline; the resulting uncorrected stain variation is stated as a limitation and separately probed by the stain-normalisation robustness check (M10). <!-- src: 03_methods.md M2 -->

### M3. Model and training
We used CLAM-SB attention MIL (hidden 512, attention 256, 40–50 epochs, seed fixed at 42). Predictions were produced per slide and then aggregated per patient. <!-- src: 03_methods.md M3; experiments/crosscancer/run_mil_cost.py -->

### M4. Evaluation design
All evaluation was performed on a site-disjoint holdout. Slides from the same tissue source site (TSS) were prevented from entering training and evaluation simultaneously, blocking leakage via institutional fingerprints; validation and test were combined for power. Three controls were used: a shuffle-null, a prevalence baseline (0.5) and a subtype-only or pixel-mean baseline. Confidence intervals are reported as 1,000-fold bootstrap 95% CIs; where patient clustering matters (receptor routing), CIs were recomputed at the patient level. <!-- src: 03_methods.md M4 -->

### M5. The cost-of-substitution frame
Substitution cost is defined by multiplying the confusion matrix by therapeutic distance, giving the misassignment cost incurred where the treatment chosen from the measured marker and the treatment chosen from the H&E-predicted marker diverge. The lead indicator is the distance-independent misroute rate. This frame does not predict drug response and takes no drug structure as input. <!-- src: 03_methods.md M5; experiments/kkkim/20260710_cost_of_substitution/ -->

### M6. Pre-registration and claim discipline
Adjudication thresholds are cited only from the sealed pre-registration document, not from slides or observed values. The power rule (fewer than 25 positives → exploratory → INCONCLUSIVE) is not moved after seeing results and is applied symmetrically to confirmation and refutation. All outputs are `hypothesis_only` and retrospective. <!-- src: 03_methods.md M6 -->

### M7. The Yale anchor (provisional, Critic pending)
The anti-HER2 axis score was computed by frozen transfer (the anchor model applied without further training), used to stratify pCR in the Yale cohort, and evaluated by AUROC with bootstrap 95% confidence intervals, then compared with the measured-HER2 probability baseline using DeLong's test. The pre-specified benchmark was defined as approaching and overlapping Farahmand and colleagues' 0.80 [0.69–0.88]. The provisional result is AUROC 0.533 [0.411–0.653] — the anti-HER2 axis did not stratify pCR from the H&E-predicted phenotype, directionally consistent with the map's HER2 negative — but this value is `critic_status: pending` and is not carried into the Abstract or headline claims. <!-- src: 02_results.md R6 (0.533 [0.411–0.653]); status pending per task instruction -->

### M8. Multi-model robustness
CLAM was retrained from scratch in each foundation-model embedding space (the coordinate systems differ, so the predictive model must be refitted separately for the comparison to be at the same level). The adjudication criterion is 5-seed shuffle-null chance-exclusion (real AUROC > null mean + 2 × standard deviation, ddof = 1), with seeds 42, 1, 2, 3 and 4. Determinism was verified by 2 re-runs at identical seeds (colorectal BRAF Virchow2 seed 42 = 0.8798 reproduced). Canonical results are in `CROSSCHECK_5SEED_MULTIFM.md` and `MULTIFM_COMPARISON.md`. sjpark independently recomputed from committed source (BIOP02-101, cross-check PASS); braveji's final multi-FM Critic sign-off is in progress. <!-- src: 03_methods.md M8; MULTIFM_COMPARISON.md header -->

### M9. Site/batch confounding audit
For each endpoint we quantified whether the site-disjoint split confounds the label with the tissue source site (TSS). We computed Cramér's V between site and label with a permutation p-value, the train/test prevalence shift, and a permutation test of the site concentration of test positives. This analysis examines a necessary condition for confounding; the final adjudication of whether the model actually uses site rests on site predictability from H&E and on leave-one-site-out performance. <!-- src: 03_methods.md M9; site_audit_results.json -->

### M10. Stain-normalisation robustness (breast anchor)
To test whether the anchor results are an artefact of uncorrected H&E stain variation, embeddings were re-extracted from the breast-anchor slides with Macenko stain normalisation (torchstain 1.3.0, a fixed dense-tissue reference tile), and CLAM was re-trained on the same folds (`split_policy_v0`, fold hash 5995f29d3978b831) for ER, HER2 and PAM50. The HER2 phenotype prediction remained near chance (AUROC 0.641), ER stayed high (0.917) and PAM50 was preserved (0.740); the anchor rank ER > PAM50 > HER2 matches the non-normalised anchor ordering (Table R1: ER 0.901, PAM50 0.759, HER2 0.599). Only phenotype prediction was re-run, not the routing/cost pipeline, and no shuffle-null was computed for the stain-normalised runs. This robustness check covers the breast anchor only; cross-cancer raw slides were lost and re-extraction under stain normalisation is deferred. <!-- src: experiments/kkkim/20260819_stain_norm_robustness/RESUME.md; clam_rerun/sjpark/*/metrics.json (0.6408/0.9166/0.7396) -->

---

## Figures and tables

- **Fig1** Pipeline schematic (H&E → embedding → phenotype → routing misassignment rate)
  `[Figure 1: pipeline — WSI tiling → UNI embedding → CLAM MIL phenotype → marker-to-treatment routing → misassignment rate]`
- **Fig2** Observed map overlaying misassignment loss on confusion × distance (central figure)
  `[Figure 2: central map — per-axis substitution cost across five cancers, legible end (HPV/histology) to illegible end (HER2/ERBB2)]`
- **Fig3** Per-axis misassignment loss and the confidence interval of the headline contrast
  `[Figure 3: per-axis cost with 95% CI; headline contrast CI excluding 0]`
- **Fig4** (planned) Power ceiling — holdout positives per axis and the boundary of decidability
  `[Figure 4: holdout n_pos per axis vs the 25-positive pre-registered threshold; verdict-coloured, positive controls hatched]`
- **Fig5** (planned) HER2 misassignment detail — treatment-category misassignment rates by routing scheme
  `[Figure 5: anti-HER2 misassignment rate = 1.00; scheme-dependence of endocrine/chemo cost]`
- **SFig1** (planned) Multi-model comparison — order preservation across UNI/Virchow2/UNI2-h and the cells that diverge
  `[SFigure 1: lung order preserved (Spearman 1.000); diverging single cells (HPV/Virchow2, BRAF/UNI2-h)]`
- **Table R1** Observed substitution-cost spectrum · **Table R2** Power ceiling · **Table R5** Multiple foundation models (Supplement)
- **Table 1** (planned) Cohort characteristics — n, label prevalence and split for the 5 cancers `<FILL: jamie — S5 in SUBMISSION_PREP.md>`

## Open items and gates (for kkkim review)

- **Author-facing metadata unconfirmed** — authors/order, affiliation, corresponding author + email, funding/acknowledgments (**GPU provider Modulabs must be named**, per project README), COI, ORCID. `<FILL: 팀 확정>`. This is the critical path (BIOP02-114).
- **Yale (R6/M7) is `critic_status: pending`** — provisional, kept out of Abstract/headline; body promotion only after Critic sign-off.
- **20-seed HPV/Virchow2 flip not adopted** — status stays "2 of 3 models" pending braveji (BIOP02-123).
- **PAM50 label source** — 57.0 % concordance with cBioPortal; fallback condition not met (coverage 97.2 %). Canonical label source is an open Methods reconciliation item (BIOP02-74).
- **Stain-normalisation covers breast anchor only** — cross-cancer headline (HPV, lung) not stain-verified (raw lost).
- **braveji 7-point Critic final sign-off (BIOP02-75)** pending for the whole Paper C.
- **Citations** are provisional (brackets) until machine-verified by `agents/critic/scripts/verify_citations.py`.
- **Venue** — npj Precision Oncology vs ML4H 2026: format/length constraints `<FILL: ML4H 2026 CFP 원문 — 사람 확정>`; compression likely needed for a workshop venue (Leader decision).
- **Reporting-standard mappings** (TRIPOD+AI done; CLAIM/PROBAST/STROBE pending) and **Table 1 (cohort characteristics)** to be attached as Supplement.

---

## References (working)

Markers `[CITE-Ix]` in the text resolve here. This section grows section by section; re-verify with `verify_citations.py` before submission.

### Introduction

Markers `[CITE-I1]`–`[CITE-I9]` in the text resolve here. Every entry was checked against the source or publisher page; nothing is entered from memory. Re-verify with `verify_citations.py` before submission.

**[CITE-I1]** Spread of digital pathology and computer-aided pathology
- Nam, S., Chong, Y., Jung, C. K., Kwak, T. Y., Lee, J. Y., Park, J., ... & Go, H. (2020). Introduction to digital pathology and computer-aided pathology. *Journal of Pathology and Translational Medicine, 54*(2), 125–134.

**[CITE-I2]** Uptake of weakly supervised WSI learning and CLAM-family MIL
- Lu, M. Y., Williamson, D. F. K., Chen, T. Y., Chen, R. J., Barbieri, M., & Mahmood, F. (2021). Data-efficient and weakly supervised computational pathology on whole-slide images. *Nature Biomedical Engineering, 5*(6), 555–570. https://doi.org/10.1038/s41551-020-00682-w
- Ilse, M., Tomczak, J., & Welling, M. (2018). Attention-based deep multiple instance learning. *Proceedings of the 35th International Conference on Machine Learning (PMLR), 80*, 2127–2136.

**[CITE-I3]** H&E AI studies in urological (prostate, bladder) cancer
- Paik, I., Lee, G., Lee, J., Kwak, T. Y., & Ha, H. K. (2025). Artificial intelligence–driven digital pathology in urological cancers: Current trends and future directions. *Prostate International*.
- Cho, Y., Shin, D., Hong, S., Lee, J., Park, S., Lee, G., ... & Ha, H. K. (2026). Efficient AI-driven multi-section whole slide image analysis for biochemical recurrence prediction in prostate cancer. *arXiv*. https://arxiv.org/abs/2603.20273

**[CITE-I4]** H&E WSI AI studies in breast cancer
- Lee, G., Lee, J., Kwak, T. Y., Kim, S. W., Kwon, Y., Kim, C., & Chang, H. (2025). Assessing the risk of recurrence in early-stage breast cancer through H&E stained whole slide images. *Scientific Reports, 15*(1), 35069.
- Lee, J., Lee, G., Kwak, T. Y., Kim, S. W., Jin, M. S., Kim, C., & Chang, H. (2024). MurSS: A multi-resolution selective segmentation model for breast cancer. *Bioengineering, 11*(5), 463.
- Lee, G., Kim, C., Kwak, T. Y., Kim, S. W., & Chang, H. (2023). Predicting protein receptor status from H&E-stained images in breast cancer. *Cancer Research, 83*(7_Supplement), 5404.

**[CITE-I5]** Extension to pancreatic and other organs
- Lee, J., Lee, G., Kwak, T. Y., Kim, S. W., & Chang, H. (2022). A deep learning based pancreatic adenocarcinoma survival prediction model applicable to adenocarcinoma of other organs. *Cancer Research, 82*(12_Supplement), 5060.

**[CITE-I6]** Knowledge distillation and pathology foundation models improving performance
- Cho, Y., Lee, S., Lee, G., Lee, M., Park, J., & Shin, D. (2026). G2L: From giga-scale to cancer-specific large-scale pathology foundation models via knowledge distillation. *Proceedings of the AAAI Conference on Artificial Intelligence*. (arXiv:2510.11176)
- Kim, H., Kwak, T. Y., Chang, H., Kim, S. W., & Kim, I. (2023). RCKD: Response-based cross-task knowledge distillation for pathological image analysis. *Bioengineering, 10*(11), 1279.
- Chen, R. J., Ding, T., Lu, M. Y., Williamson, D. F. K., Jaume, G., Song, A. H., ... & Mahmood, F. (2024). Towards a general-purpose foundation model for computational pathology. *Nature Medicine, 30*(3), 850–862. https://doi.org/10.1038/s41591-024-02857-3

**[CITE-I7]** Cost and turnaround burden of IHC and tissue-destructive molecular tests relative to H&E
- Erfani, P., Gaga, E., Hakizimana, E., Kayitare, E., Mugunga, J. C., Shyirambere, C., Milner, D. A., Shulman, L. N., Ruhangaza, D., & Fadelu, T. (2023). Breast cancer molecular diagnostics in Rwanda: A cost-minimization study of immunohistochemistry versus a novel GeneXpert mRNA expression assay. *Bulletin of the World Health Organization, 101*(1), 10–19. https://doi.org/10.2471/BLT.22.288800
- Sharma, A., Shah, P., Ranade, M., Pai, T., Sahay, A., Patil, A., Shet, T., Gupta, H., Chauhan, D., Somal, P., Sancheti, S., & Desai, S. (2025). Digital pathology enabling lean management of HER2/neu testing in breast cancer. *Journal of Pathology Informatics, 19*, 100515. https://doi.org/10.1016/j.jpi.2025.100515

**[CITE-I8]** Clinical role of molecular tests in early detection, prognosis and treatment direction
- Zhou, Y., Tao, L., Qiu, J., Xu, J., Yang, X., Zhang, Y., Tian, X., Guan, X., Cen, X., & Zhao, Y. (2024). Tumor biomarkers for diagnosis, prognosis and targeted therapy. *Signal Transduction and Targeted Therapy, 9*, 132. https://doi.org/10.1038/s41392-024-01823-2

**[CITE-I9]** Repeated demonstrations that molecular state can be predicted from H&E
- Coudray, N., Ocampo, P. S., Sakellaropoulos, T., Narula, N., Snuderl, M., Fenyö, D., Moreira, A. L., Razavian, N., & Tsirigos, A. (2018). Classification and mutation prediction from non–small cell lung cancer histopathology images using deep learning. *Nature Medicine, 24*(10), 1559–1567. https://doi.org/10.1038/s41591-018-0177-5
- Kather, J. N., Pearson, A. T., Halama, N., Jäger, D., Krause, J., Loosen, S. H., ... & Luedde, T. (2019). Deep learning can predict microsatellite instability directly from histology in gastrointestinal cancer. *Nature Medicine, 25*(7), 1054–1056. https://doi.org/10.1038/s41591-019-0462-y
- Kather, J. N., Heij, L. R., Grabsch, H. I., Loeffler, C., Echle, A., Muti, H. S., ... & Luedde, T. (2020). Pan-cancer image-based detection of clinically actionable genetic alterations. *Nature Cancer, 1*(8), 789–799. https://doi.org/10.1038/s43018-020-0087-6
- Naik, N., Madani, A., Esteva, A., Keskar, N. S., Press, M. F., Ruderman, D., ... & Socher, R. (2020). Deep learning-enabled breast cancer hormonal receptor status determination from base-level H&E stains. *Nature Communications, 11*(1), 5727. https://doi.org/10.1038/s41467-020-19334-3
- Schmauch, B., Romagnoni, A., Pronier, E., Saillard, C., Maillé, P., Calderaro, J., ... & Wainrib, G. (2020). A deep learning model to predict RNA-Seq expression of tumours from whole slide images. *Nature Communications, 11*(1), 3877. https://doi.org/10.1038/s41467-020-17678-4


**[CITE-I10]** Clinical decision loss of substituting a molecular test — performance alone does not establish clinical acceptability
- Vickers, A. J., Van Calster, B., & Steyerberg, E. W. (2016). Net benefit approaches to the evaluation of prediction models, molecular markers, and diagnostic tests. *BMJ, 352*, i6. https://doi.org/10.1136/bmj.i6
- Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. *Medical Decision Making, 26*(6), 565–574. https://doi.org/10.1177/0272989X06295361
- Van Calster, B., Collins, G. S., Vickers, A. J., Wynants, L., Kerr, K. F., Barreñada, L., ... & Steyerberg, E. W. (2025). Evaluation of performance measures in predictive artificial intelligence models to support medical decisions: Overview and guidance. *The Lancet Digital Health, 7*(12), 100916.

**[CITE-I11]** Biomarkers guide different diagnostic, prognostic and targeted-treatment decisions, so the consequence of an error depends on the downstream decision
- `zhou-2024-tumor-biomarkers` · `chakravarty-2017-oncokb` · `griffith-2017-civic`

**[CITE-I12]** Prior single-cohort or breast-focused H&E studies predicting receptor status, subtype or biomarkers
- `tafavvoghi-2024-jpi` · `farahmand-2022-modpathol` · `gamble-2021-commsmed` · `naik-2020-natcommun` · `couture-2018-npjbc` · `fernandez-romero-2026-domaingen` (프로젝트가 기록한 최근접 스쿱)

**[CITE-I13]** Prior histology-based work framing the task as drug-sensitivity prediction
- `dawood-2024-hids`

**카운슬 판정 기록 (codex 집필 → agy 적대검토 → codex 반박 1회 → Claude 정리).** 초안의 I10–I20 표식 11개 중 7개를 삭제했다. 사유는 전부 동일 — **우리 논문 자신의 주장·설계·결과·기여에 인용을 붙인 것**이다. 특히 (a) 논지 문장 "But being predictable does not mean..." 에 선행연구를 걸면 4문단 뒤 기여 주장("다른 질문의 정립")과 자기모순이 된다. (b) 염색정규화·conformal 문헌을 기여 목록에 붙인 것은 인용 채우기였다. (c) 사전등록 근거로 leakage·site-batch 문헌을 든 것은 논거가 다르다.
남은 자리가 4개뿐인 것은 Introduction ¶2–¶5 가 대부분 우리 프레임 설명이기 때문이다. **인용 밀도는 Methods(현재 0개)와 Results(현재 2개)에서 확보해야 한다.**
⚠️ **To complete before submission.** Full author lists for Kather 2019, Kather 2020, Naik 2020 and Schmauch 2020 are not yet confirmed and are left as `et al.`; APA 7 lists up to 20 authors. Volume/issue/pages are unconfirmed for Paik 2025; AAAI publication details for G2L 2026; final venue for Cho 2026 (prostate).

# DRAFT_ML4H_v2 — Change log & review guide

> **What this is.** Companion to [`DRAFT_ML4H_v2_full.md`](DRAFT_ML4H_v2_full.md). Base = v1 full draft [`DRAFT_paperC_full_en.md`](DRAFT_paperC_full_en.md) + detailed skeletons [`sections/`](sections/). This is a **review draft for kkkim** — no commit/push/JIRA/Slack was done (human approval gate). v1 was **not** overwritten.
> **Numbers:** every headline value in v2 carries an inline `<!-- src: file -->` comment. Values were quoted from result files, never from memory or slides.

---

## (a) What was updated / corrected vs v1

### Structural (largest deltas — need kkkim's eye)

1. **Yale pCR demoted (biggest change).** v1 had AUROC **0.533 [0.411–0.653]** in the **Abstract**, as a full **Results R6**, in **Methods M7**, and in the **Discussion**. Because A3/A4 is `critic_status: pending` (task instruction: provisional, 본문 승격 금지, Discussion-only "실증 이빨 대기"), v2:
   - **removed 0.533 from the Abstract** (replaced the Yale sentence with the stain-normalisation robustness of the HER2 negative);
   - **collapsed R6 to a pending pointer** (states direction only, holds the number out of headline);
   - **kept M7** as methods-with-provisional-value, explicitly marked pending and excluded from Abstract/headline;
   - **Discussion** now treats Yale as an anchor "awaiting sign-off", not a result.
   - *Judgment point:* this is a demotion from text kkkim already reviewed in v1 — he may want to keep or re-promote depending on whether BIOP02-80/Critic has since signed off.

2. **Contribution list cut 5 → 4** (Introduction). v1's contributions (iii) "HER2 대체불가를 공간전사체 하한과 실제 치료결과로 비용 증명" and (iv) "Yale 실제 pCR 앵커" are overstated once Yale is pending and R7 (ST) is `hypothesis_only`. v2 lists four contributions and relegates Yale + ST to "provisional exploratory analyses, not contributions".

3. **Venue reframed to venue-neutral IMRaD for ML4H 2026 circulation.** v1 header targeted npj Precision Oncology; all prior project artifacts ([`SUBMISSION_PREP.md`](SUBMISSION_PREP.md) L4) also target npj-PO + medRxiv. Task names ML4H 2026. v2 is written venue-neutrally with a header note; **ML4H length/format left as `<FILL>`** (see §b).

### Numeric corrections

4. **CRC BRAF point+CI corrected.** v1 Table R1 = `0.868 [0.780–0.938]` — a **mismatched pair** (point from one file, CI from another). v2 Table R1 = **`0.882 [0.817, 0.938]`**, the point+CI reported *together* in `experiments/crosscancer/COLORECTAL/full/LAW_TEST.md` L14 (holdout161, the canonical routing split). The 5-seed multi-FM value `0.8676` (holdout151) is retained in Table R5 with an explicit note that it is a different split (same marker, CI-consistent). Source of the split ambiguity: `LAW_TEST.md` L18 numeric-consistency note.

5. **PAM50 label-source reconciliation added (57% correction).** New Methods M1 + Discussion note: manifest (local/genefu, Parker 2009) vs cBioPortal SUBTYPE agree on **57.0 % (514/902) = concordance**, i.e. **43.0 % discordance (388/902)**. Written precisely as "57 % concordance / 43 % discordance" (task flagged the "57 % 불일치" error — note: that erroneous phrasing was **not found anywhere in `manuscript/`**, so this is a first-time correct addition, not a fix to existing text). Also surfaced the `policy_check`: cBioPortal coverage 97.2 % is HIGH, so `split_policy_v0.md §10` fallback for local labels was **NOT met** → canonical PAM50 label source is an open Methods item. Source: `agents/data/manifests/pam50_source_reconcile_biop02-74.json`.

### New robustness content

6. **Stain-normalisation robustness added (BIOP02-147).** New Methods M10 + R3 paragraph + Discussion. Breast anchor, Macenko: **HER2 0.641, ER 0.917, PAM50 0.740** (`experiments/kkkim/20260819_stain_norm_robustness/clam_rerun/sjpark/*/metrics.json` = 0.6408/0.9166/0.7396). Framed as: HER2 stays near-chance with and without normalisation → the "H&E cannot substitute for HER2" headline is **not a stain-variation artefact**. Reported **qualitatively** (not as a paired before/after table) because the matched non-normalised baseline is provenance-ambiguous (scoreboard anchor HER2 = 0.599 vs same-fold `her2_status_uni_v1/metrics.json` = 0.5509). **Scope stated: breast anchor only** — cross-cancer headline (HPV, lung) not stain-verified (raw lost).

7. **Lauren vs ERBB2 "two kinds of FAIL" made explicit (R5).** Task phrasing risked flattening "Lauren 3/3 FAIL" into signal-absence. v2 keeps R4's diagnosis and, in R5, separates: **Lauren all-3-FAIL = the site-confounding artefact reproducing model-independently** (not signal absence); **ERBB2 all-3-FAIL = genuine signal absence (real ≈ null)**. Source: `MULTIFM_COMPARISON.md` §5.

8. **20-seed HPV/Virchow2 non-adoption stated (Discussion).** New: 20-seed indicated the Virchow2 HPV threshold stabilises (≈0.837) and *would* flip that cell to pass, but **not adopted** pending braveji (BIOP02-123); reported status stays "2 of 3 models". Source: `04_discussion.md` item 6; `experiments/kkkim/20260820_shuffle_null_20seed/`.

9. **Site-confounding + stain-scope co-located (Discussion).** Per review guidance, the site-audit limits (HPV V = 0.378; lung V = 1.000) and the stain-normalisation scope limit are placed in **one** Limitations paragraph, so it is clear that neither fully covers the headline HPV/lung results.

10. **Two anchor limitation blocks preserved** from `04_discussion.md` (BIOP02-75 critic gate): endpoint-specific baseline value, probability-level fidelity, HER2 honest negative, cell-line transfer.

### Unchanged from v1 (verified consistent)
- HPV 0.959 [0.921–0.986] n=26; lung LUSC 0.939; HN grade 0.815; breast HER2 0.599; ERBB2 0.644≈null 0.641; lung KRAS 0.681 / subtype-only 0.793; gastric MSI 0.860 (dev 0.899); Lauren 0.536 (dev 0.963), pixel-mean 0.631, prevalence 46→88 %; power ceiling table; Table R5 5-seed values; anti-HER2 misroute 1.00; ST Θ median 0.158.

---

## (b) Remaining `<FILL>` and gates

| Item | Status | Source / ticket |
|---|---|---|
| Authors, order, affiliation, corresponding + email, funding/ack (**Modulabs GPU**), COI, ORCID | ❌ `<FILL: 팀 확정>` — critical path | BIOP02-114 |
| Yale R6/M7 (0.533) | ⏳ `critic_status: pending` — provisional, out of headline | BIOP02-80 |
| 20-seed HPV/Virchow2 flip | ⏳ not adopted, stays "2/3 models" | BIOP02-123 |
| PAM50 canonical label source | ⏳ open reconciliation (fallback not met, coverage 97.2 %) | BIOP02-74 |
| Stain-norm cross-cancer (HPV, lung) | ❌ not verified (raw lost, deferred) | BIOP02-146/147 |
| braveji 7-point Critic final sign-off | ⏳ pending for whole Paper C | BIOP02-75 |
| Citations (bracketed) | ⏳ machine-verify before finalise | `verify_citations.py` |
| ML4H 2026 length/format constraints | ❌ `<FILL: CFP 원문 — 사람 확정>` | — |
| Table 1 (cohort characteristics) | ❌ planned Supplement | jamie / BIOP02-76 S5 |
| Reporting-standard mappings (CLAIM/PROBAST/STROBE) | ⏳ TRIPOD+AI done; rest pending | BIOP02-76 |
| Fig2/Fig3 real render + Fig4/Fig5/SFig1 | ❌ placeholders (`[Figure N: ...]`) | BIOP02-134 |

---

## (c) Key judgment points for kkkim

1. **Yale demotion** — is BIOP02-80/Critic still pending? If it has since signed off, R6 can be re-promoted and 0.533 returned to the Abstract. As of the sources read, it is pending, so v2 holds it out.
2. **Venue: npj-PO vs ML4H 2026** — every existing artifact targets npj-PO + medRxiv; only the task names ML4H. A 29 KB full IMRaD likely needs compression for ML4H. Decide target before format work; ML4H CFP numbers must be confirmed by a human (do not use search summaries as spec — same rule as `TARGET_JOURNAL_GUIDE.md` L15).
3. **PAM50 label source** — fallback for local/genefu labels was not authorised (cBioPortal coverage high). Since PAM50 is the only anchor endpoint clearing a valid baseline both internally and externally, which label set is canonical materially affects that claim. Needs a Methods decision, not a writer's guess.
4. **CRC BRAF split** — v2 uses 0.882 [0.817–0.938] (holdout161) in Table R1 and 0.868 (holdout151) in Table R5, both annotated. Confirm this is the intended split assignment; v1's 0.868 [0.780–0.938] pair was inconsistent.
5. **Stain-norm scope** — the check defends the breast HER2 negative but **not** the cross-cancer headline (HPV, lung), which are the results most exposed to a scanner/stain-artefact reviewer objection. Accept as an honest limitation, or fund cross-cancer re-extraction (RunPod, per project notes). Note two intrinsic scope limits now stated in R3/M10: the stain-norm run re-ran only *phenotype prediction*, not the routing/cost pipeline; and it carries no shuffle-null, so "near chance" rests on the value + ER/PAM50 comparison, not a null.
6. **Yale demoted from Results but R7 (ST) kept in Results** — both are `critic_status: pending`. Yale is pulled to a pending pointer; R7 stays in Results with numbers (as in v1). This asymmetry is defensible (ST is mechanistic support, Yale is an outcome claim) but kkkim should rule on whether R7 should likewise be demoted or explicitly labelled provisional-in-Results for consistency.

---

### Verification honesty note
- **Verified against files:** all Table R1/R2/R5 numbers, HPV/lung/HER2/ERBB2/KRAS/MSI/Lauren values, stain-norm triplet (metrics.json), PAM50 reconcile JSON, CRC BRAF point+CI provenance, multi-FM 2/3 & 3/3 FAIL framing, 20-seed non-adoption.
- **Not independently recomputed (writing task, no analysis run):** none of the AUROCs were re-derived — they were quoted from result files as the task requires.
- **Provenance-ambiguous, reported qualitatively:** stain-norm before/after (baseline anchor value 0.599 vs same-fold 0.5509).
- **Not resolved by writer (flagged for humans):** author metadata, Yale sign-off, PAM50 canonical source, ML4H format, venue choice.

# Cross-Cancer Decision Map — Breast ↔ Colorectal

`claim_level: hypothesis_only` · `critic_status: pending` · commit `d3a614f`
Comparison rule: **internal holdout vs internal holdout only.** Breast values are quoted verbatim
from the existing internal-holdout baselines (site-disjoint, n_val≈151); colorectal values are
from this run (site-disjoint holdout). External CPTAC transfer results are **isolated** in §4 and
never mixed into Tables 1–2.

> **Two quantities are kept strictly separate and never fused into one "cost" number (guardrail #1).**
> - **Part A / Table 1 = prediction-fidelity**: does H&E recover the *subtype* (breast PAM50 ↔ colorectal CMS)? Like-with-like: subtype ↔ subtype.
> - **Part B / Table 2 = routing substitution-cost**: what decision-fidelity is lost when H&E-predicted treatment markers route therapy (breast receptors ↔ colorectal mutations)? Like-with-like: mutation/receptor ↔ mutation/receptor.
> CMS is a **prognostic** subtype, not an NCCN treatment-routing axis (Buikhuisen, JNCI 2022). Its AUROC is reported as recovery fidelity only and is **never** promoted to a treatment cost.

---

## Table 1 — Subtype prediction-fidelity (internal holdout, subtype ↔ subtype)

H&E → molecular subtype recovery. Descriptive comparison across cancers (different cohorts/label
systems → not a head-to-head contest, no ranking).

| Cancer | Subtype endpoint | Model | AUROC (95% CI) | n_pos / n_holdout | Power flag |
|---|---|---|---|---|---|
| Breast | PAM50 (multiclass) | CLAM-MB | 0.759 | — | (existing baseline) |
| Colorectal | CMS1_vs_rest | CLAM-SB | **0.912** (0.828–0.973) | 19 / 132 | exploratory (low power) |
| Colorectal | CMS2_vs_rest | CLAM-SB | 0.871 (0.809–0.925) | 50 / 132 | well-powered |
| Colorectal | CMS3_vs_rest | CLAM-SB | 0.840 (0.738–0.927) | 21 / 132 | exploratory (low power) |
| Colorectal | CMS4_vs_rest | CLAM-SB | 0.661 (0.566–0.750) | 42 / 132 | well-powered, **weak signal** |

Reading:
- CMS1 (MSI/immune) shows the strongest morphological correlate (0.912) — consistent with known
  TIL/medullary morphology — but is low-power (n_pos 19, exploratory).
- CMS4 (mesenchymal/stromal) is the **weakest** despite being well-powered (n_pos 42): real 0.661
  with CI lower bound 0.566, and the single-draw shuffle-null (0.639) overlaps → near-null H&E
  signal. Reported honestly; not rescued.
- **Power (exploratory) ≠ signal strength**: CMS1 = strong signal / low power; CMS4 = solid power /
  weak signal. Kept orthogonal.
- **Prior work establishes feasibility, not us**: imCMS (Sirinukunwattana, Gut 2021) reports H&E→CMS
  AUC ≈ 0.84; Coudray 2018 (Nat Med) H&E→molecular. Our CMS1/CMS2 numbers land near/above 0.84 but
  this is a **different cohort and method, not head-to-head** — we make **no prediction-advancement
  claim** (guardrail #5). Our contribution is the decision-map / substitution-cost, not the prediction.
- PAM50 0.759 is descriptive only and is **never mapped to a treatment axis**. Several CMS endpoints
  exceed it, but cross-cancer with different label systems → comparable subtype-recovery fidelity, no ranking.

*(Note: Part A holdout n=132 CMS-labeled patients; Part B holdout n=161 treatment-labeled patients —
different denominators by design, since CMS and treatment markers cover different patient subsets.)*

---

## Table 2 — Treatment-routing substitution-cost (internal holdout, mutation ↔ mutation/receptor)

Lead metric = **misroute_rate** (measured marker vs H&E-predicted marker routing mismatch;
distance-free, defined identically to breast receptor-routing). MIL AUROC shown alongside.
Routing scheme was **pre-registered before computing cost** (`routing_scheme_preregistered.json`).

| Cancer | Marker → therapy axis | AUROC (95% CI) | misroute_rate | mean_cost | n_pos / n_holdout | Cost class (pre-reg) |
|---|---|---|---|---|---|---|
| Breast | ER → endocrine | 0.901 | (low) | — | — | **low** (H&E-visible) |
| Breast | HER2 → anti-HER2 | **0.599** (near-random) | (high) | — | — | **high** (H&E-blind, molecular test mandatory) |
| Colorectal | MSI-H → anti-PD-1 (KEYNOTE-177) | 0.918 (0.850–0.969) | 0.112 | null¹ | 21 / 161 (exploratory) | **low** ✓ confirmed |
| Colorectal | all-RAS/BRAF-WT → anti-EGFR (CRYSTAL, FIRE-3) | 0.705 (0.620–0.783) | **0.416** | null¹ | 84 / 161 | **high** ✓ confirmed |
| Colorectal | BRAF-V600 → BRAF+EGFR (BEACON) | 0.882 (0.817–0.938) | 0.099 | 0.086² | 15 / 161 (exploratory) | **partial** ✓ confirmed |

¹ `mean_cost = null` for MSI and anti-EGFR: the frozen cell-line map (`frozen_map.json`) **excludes
the ICI and antibody axes** (monoculture cannot capture ICI/ADCC efficacy), so no honest therapeutic
distance exists. A pre-registered *clinical* distance for these axes is a **human decision** (see §5).
misroute_rate carries the full cross-cancer comparison.
² BRAF `mean_cost = misroute_rate × frozen_map antiBRAF__baseline distance (0.868) = 0.099 × 0.868 ≈ 0.086`.
The fresh BRAF AUROC 0.882 (same split as MSI/anti-EGFR) agrees with the prior internal-holdout 0.868 within CI.

Reading:
- Pre-registered hypotheses all held: **MSI-H = low-cost** (0.918, misroute 0.112), **anti-EGFR =
  high-cost** (weakest AUROC 0.705, **highest misroute 0.416**), **BRAF = partial** (0.882).
- The anti-EGFR axis being **above chance** (0.705, not near-random) is expected: all-RAS status
  correlates with BRAF/MSI morphology, lending indirect signal; the dominant RAS component itself
  stays H&E-silent, which is why its misroute (0.416) is by far the highest.

---

## §3 — Core cross-cancer asymmetry

**Breast: the subtype system *is* the treatment-routing system.** PAM50 / receptor status maps
directly onto endocrine / anti-HER2 / chemo decisions. Prediction-fidelity and routing-cost live on
the same axis.

**Colorectal: subtype (prognostic) and routing (predictive) are *decoupled*.** CMS is prognostic and
does **not** define NCCN routing; routing lives in the **mutation axis** (MSI → ICI, all-RAS →
anti-EGFR, BRAF → combo). H&E recovers CMS moderately well, but that fidelity does **not** transfer
to therapy decisions.

**The colorectal analog of breast HER2 is not a CMS subtype — it is the all-RAS mutation axis.**
This is an **ordinal / decision-structure analogy, not a numeric equivalence**: in *each* cancer the
mutation-defined routing axis that is hardest for H&E (breast HER2 near-random 0.599; colorectal
anti-EGFR weakest-and-highest-misroute 0.705 / 0.416) is the highest-substitution-cost axis. all-RAS
is **not** claimed to be "as H&E-blind as HER2" — it is measurably above chance; the shared claim is
"the weakest-prediction / highest-cost routing axis within each cancer's own decision map."

> **Subtype ↔ mutation are NOT compared 1:1** (docs/ai-collaboration-cautions.md 사례1). Table 1
> compares subtype↔subtype; Table 2 compares mutation/receptor↔mutation/receptor. The HER2↔all-RAS
> link is a claim about *decision structure* (which routing axis is highest-cost), not a claim that a
> subtype equals a mutation.

Prior work cited for feasibility (not superseded, not beaten): imCMS (Sirinukunwattana, Gut 2021,
H&E→CMS AUC 0.84); Kather 2019 (Nat Med, H&E→MSI); Coudray 2018 (Nat Med, H&E→molecular). **Our
contribution is the cross-cancer decision map / substitution-cost, not the prediction itself.**

---

## §4 — External transfer (CPTAC) — ISOLATED, not in Tables 1–2

Breast external CPTAC transfer showed receptor-head degradation (majority-class collapse under
domain shift). This is reported **only** as a separate "transfer degradation" caveat and is **never**
placed in the internal-holdout comparison tables above. Colorectal has **no** external transfer set
in this analysis; all colorectal numbers are internal site-disjoint holdout. Do not compare breast
external transfer against colorectal internal holdout.

---

## §5 — Open items requiring human decision (not resolved here)

1. **mean_cost for MSI / anti-EGFR axes**: needs a separately pre-registered *clinical* therapeutic
   distance (frozen cell-line map excludes ICI/antibody axes). Until then, misroute_rate is the lead
   metric and mean_cost stays `null` for these two axes.
2. **Shuffle-null robustness (non-blocking)**: nulls are single-draw (seed=42), unstable at small
   n_pos — e.g. BRAF null swung 0.44→0.64 from a split change alone while real barely moved
   (0.868→0.882). Elevated (>0.5) nulls are **not** a leakage signal (leakage *depresses* the null);
   likely a label-independent CLAM bag-size confound (attention-sum ∝ tile count). Follow-up: average
   null over ~5 seeds, or correlate holdout proba with tile count. patient_overlap=0 and site-disjoint
   already verified. Chance-exclusion rests on bootstrap CI + real-vs-null margin, not the null point.
3. All outputs are `critic_status: pending` — not to be shared in `#biop02-experiments` until Critic pass.

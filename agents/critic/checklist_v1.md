# Critic Checklist v1 — SpatialPathoAgent (BIOP02)

**Scope:** BRCA-only phenotype experiments (ER / PR / HER2 / PAM50), MLP → attention MIL.
**Output:** every experiment must ship a `critic_report.json` conforming to
[`schemas/critic_report.schema.json`](../../schemas/critic_report.schema.json).
Results may be shared in `#biop02-experiments` **only** when `critic_status: pass`.

This document is the human-readable rubric behind that schema. Each of the 7 checks maps
1:1 to a key under `checks` in the schema (`data_leakage`, `baseline_comparison`,
`counterfactual_check`, `cross_dataset_check`, `biological_plausibility`, `drp_framing`,
`claim_level`). Per-check `status` ∈ `{pass, caution, reject, not_applicable}`.

---

## Governance rules (non-negotiable)

- **Owner ≠ Reviewer.** Never critique your own results. `reviewer` field must differ from `owner`.
- **Critic 총괄 = braveji.** braveji owns the 7-point rollup and the final `critic_status`.
  Biological sub-checks are delegated to a **non-owner**: #4 cross-dataset → jhans, #5 biological
  plausibility → sjpark (or jhans when sjpark is the owner).
- **Anti-self-reference.** The Critic must not set its own thresholds/controls. Baselines,
  significance tests, and pass thresholds are fixed here, not chosen per-experiment to fit a result.
- **claim_level = `hypothesis_only`** on every output. Any deviation needs written justification.
- **`critic_status` rollup:** `pass` requires every check to be `pass` or a justified
  `not_applicable`. Any `caution` → overall `caution`. Any `reject` → overall `reject`.

### Cross-review pairings (2026-06-09, gglee 이탈 반영)

| 작성자 (owner) | 지정 Critic reviewer |
|---|---|
| sjpark (모델링) | kkkim |
| kkkim (임베딩) | jamie |
| jamie (데이터/split) | braveji |
| jhans (TE) | braveji 총괄 (생물 sub-check: sjpark) |

---

## The 7 checks

### 1. Data leakage — `data_leakage`
Confirm no train/val/test contamination.
- **Evidence required:** split is **patient-level** (not slide-level); slides from the same case
  never cross splits; `predictions` indices map only to held-out patients; split is site-disjoint
  per `split_policy_v0` (locked — no post-lock changes).
- **pass:** patient-disjoint verified against the split file + prediction index.
- **caution:** structure looks right (split sizes consistent, site-disjoint) but patient-overlap
  not yet verified against artifacts.
- **reject:** any slide/patient appears in both train and eval.

### 2. Baseline comparison — `baseline_comparison`
The model must beat **all three** agreed trivial baselines, meaningfully.
- **Required baselines (fixed, not per-experiment):** `random`, `subtype-only` (PAM50 → endpoint),
  `pixel-mean`. (Note: embedding-mean ≠ pixel-mean — both the embedding-mean and pixel-mean
  references should be reported; embedding-mean is the strongest trivial bar for foundation-model
  features.)
- **Significance:** report a test for the model-vs-strongest-baseline gap (DeLong on AUC, or
  bootstrap 95% CI). A raw point-estimate delta is not sufficient.
- **pass:** model exceeds every required baseline **and** the gap over the strongest baseline is
  statistically significant.
- **caution:** a required baseline is missing, or the gap over the strongest baseline is within
  noise / not significance-tested.
- **reject:** model does not exceed the strongest trivial baseline.

### 3. Counterfactual check — `counterfactual_check`
Ranking/prediction must change when key features are removed (sanity that signal is real).
- **pass:** feature-removal / tile-ablation / attention-masking shifts outputs as expected.
- **not_applicable:** simple MLP baselines with no feature-attribution claim (defer to MIL stage,
  BIOP02-56). Mark `not_applicable` only when no claim exceeds baseline scope.
- **reject:** claims of learned morphology signal with no counterfactual support.

### 4. Cross-dataset check — `cross_dataset_check` *(sub-check: jhans)*
Consistency across datasets (TCGA train → CPTAC test; DepMap PRISM vs GDSC for TE).
- **pass:** external-set performance reported with **official** labels and degradation is characterized.
- **not_applicable:** endpoint is TCGA-only by design at this sprint — must be stated explicitly.
- **caution:** external eval uses provisional/self-produced labels (reviewer self-reference) → not final.

### 5. Biological plausibility — `biological_plausibility` *(sub-check: sjpark, non-owner)*
Morphology → phenotype (and pathway–drug links for TE) must be biologically sensible.
- **pass:** endpoint has known histologic correlates; negative results reported honestly
  (e.g. HER2 amplification is poorly reflected in H&E → near-chance AUC is expected, not a bug).
- **caution:** plausible but sub-check assigned to the owner (self-review) → reassign to non-owner.
- **reject:** biologically implausible claim, or therapeutic inference drawn from a bare baseline.

### 6. DRP framing check — `drp_framing`
No drug-response-prediction framing anywhere in outputs.
- **Prohibited wording:** "drug response prediction", "patient-specific optimal treatment",
  "personalized therapy"; recommending ICI/Pembrolizumab via cell-line transfer.
- **pass:** metrics/config/report text free of prohibited framing.
- **reject:** any prohibited expression present.

### 7. Claim-level check — `claim_level`
- **pass:** `claim_level: hypothesis_only` present in every artifact; `critic_status` not
  self-set to `pass` by the owner (owner leaves `pending`).
- **reject:** claim level escalated without written exception.

---

## Reviewer procedure

1. Verify `owner ≠ reviewer` and that the reviewer is the designated pairing above.
2. Open the five experiment artifacts (`config.yaml`, `metrics.json`, `predictions.npy`,
   `model.pt`, git `commit_hash`) — **verify numbers against the files**, do not trust the summary.
3. Fill each check `status` + `evidence[]` + `notes`. Put hard requirements into `required_followups`.
4. Set `critic_status` by the rollup rule. Share to `#biop02-experiments` only on `pass`.

*v1 — braveji (Critic 총괄). Anti-self-reference: thresholds/baselines fixed here, not per-result.*

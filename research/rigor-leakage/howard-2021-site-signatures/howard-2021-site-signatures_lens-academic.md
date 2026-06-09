# Lens: Academic — Howard 2021 as BIOP02's reviewer shield

## The gap in the papers we are scoped against
Our closest neighbors on **TCGA-BRCA H&E deep learning** — **Dawood 2024 (HiDS, npj Prec Oncol)** and the **Tafavvoghi 2024 (JPI)** survey landscape — report attractive AUROC/AUC-DRC numbers but **do not control for submitting-site confounding**. Dawood partitions at patient level (good, prevents tile leakage) yet a reviewer can still ask: *"How much of your signal is the institution's H&E protocol, not breast biology?"* Howard 2021 is the paper that turns that vague worry into a **quantified, citable threat** — and therefore into a defense we can pre-empt.

## How Howard shields us
1. **Names the failure mode precisely.** Site signatures are detectable at OVR AUROC up to 0.998 and **survive Macenko-style stain normalization + color augmentation** (residual OVR >0.850). So "we stain-normalized" is *not* a sufficient rebuttal — only **site-disjoint splitting** is. We cite this to justify going beyond what Dawood/Tafavvoghi did.
2. **Quantifies the optimism we avoid.** 91.1% of features lose AUROC and 35.7% of "significant" findings evaporate under preserved-site CV. We can state our ER/PR/HER2/PAM50 numbers are reported under the *stricter* regime, so they are **conservative, not inflated** — a reviewer-positive framing.
3. **Adds an equity argument.** BRCA ancestry leaked (0.798 → 0.507). Since BIOP02 is BRCA-only and ancestry/site are correlated in TCGA-BRCA, citing this lets us claim our split protocol also guards against **demographic shortcut learning**, not just accuracy inflation.

## split_policy_v0 implications (hand-off to jamie)
- **Lock the unit of disjointness at the site level, not just patient level.** Patient-disjoint (Bussola 2020) is necessary but *insufficient* — Howard shows the residual leak is institutional. Add `tss_code` (TCGA Tissue Source Site, the `XX` in `TCGA-XX-####`) as a grouping key.
- **Default = site-disjoint folds; preferred = QP site-preserved folds** so ER/PR/HER2/PAM50 class balance is maintained across folds (Sprint 1 ER status MLP onward, never changed after lock).
- **Record per-site outcome variation** before training (Howard recommendation #1) so we can report it in Paper A.
- This makes split_policy_v0 the **load-bearing rigor artifact**; once gglee (Critic) signs check #1 against this paper, our results are defensible against the exact reviewer objection Dawood/Tafavvoghi remain exposed to.

## Differentiation sentence (for Paper A intro/discussion)
> Unlike prior TCGA-BRCA histology models, we enforce submitting-site–disjoint cross-validation (Howard et al., 2021) and probe residual site information directly, ensuring reported phenotype-prediction performance is not attributable to institutional batch effects.

# Subramanian 2017 — Next-Generation Connectivity Map (L1000) — Core

**Subramanian A, Narayan R, Corsello SM, ... Golub TR. Cell, 2017.**
doi: 10.1016/j.cell.2017.10.049 | platform: https://clue.io

## 한 줄 요약 (TL;DR)
L1000은 **978개 landmark 유전자만** 측정하고 나머지 ~12,000개를 회귀로 추론하여,
RNA-seq의 ~1/1000 비용으로 **130만 개 이상의 perturbational profile**을 만든
대규모 Connectivity Map이다. 임의의 up/down 유전자 signature를 query하면
perturbagen들을 **connectivity score (signature reversal 포함)** 로 순위화한다.

## What it is
- A scaled successor to the original CMap (Lamb 2006). Instead of full transcriptome
  arrays, L1000 measures a reduced "landmark" set and **infers** the rest.
- Verified figures (PMC mirror; Cell fulltext returned 403):
  - **1,319,138 L1000 profiles** generated (the "first 1,000,000+").
  - **42,080 perturbagens**: 19,811 small molecules, 18,493 shRNAs, 3,462 cDNAs, 314 biologics.
  - **5,075 disease-associated genes** for the genetic perturbation arm.
  - Assay measures **1,058 probes → 978 landmark transcripts + 80 controls**.
  - Gene inference accurate (R_gene > 0.95) for **9,196 of 11,350 inferred genes (81%)**.
  - Detection: **Luminex FlexMap 3D** beads; two transcripts per bead color via
    2:1 mixing + k-means peak deconvolution (the famous "doublet" trick).
  - **Reagent cost ≈ $2 per L1000 assay.**

## Connectivity scoring (핵심 메커니즘)
A query signature (top up + top down genes) is scored against every reference
signature using a **weighted Kolmogorov–Smirnov enrichment statistic**, then summarized by:
1. **nominal p-value** (query vs reference similarity),
2. **FDR**,
3. **Tau (τ)** — normalized connectivity score comparing the observed enrichment
   to all others in the database (interpretable, cross-cell-line comparable).
A strongly **negative** connectivity (τ → −100) means the perturbagen **reverses**
the query signature — the basis of signature-reversal drug hypotheses.

## Why it matters for BIOP02
- Route 1 (PRISM/GDSC): morphology → phenotype → **viability** transfer.
- Route 2 (this paper): morphology → phenotype → **expression signature** →
  clue.io query → **reversal-ranked compounds**. No drug structure, no viability label.
- The two routes share NO readout, so agreement (Exp4) is a genuine convergence
  signal, not circular reasoning. Output stays `hypothesis_only`.

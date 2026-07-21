# Paper A — Methods (모델링 절) 초안 (BIOP02-72)

> 작성 sjpark · 2026-07-21 · 초안 v0.1
> 범위: 모델 구조 + 학습 설정 + 평가·통계 (데이터/임베딩 층은 kkkim 절과 연결)
> 근거: agents/modeling/configs/*.yaml, agents/modeling/baselines/attention_mil.py, experiments/sjpark/*/metrics.json
> 수치는 커밋된 아티팩트 기준. claim_level: hypothesis_only.

---

## M.1 Overview

We predict molecular phenotype from H&E whole-slide images (WSI) by (i) tiling each slide,
(ii) extracting per-tile morphology embeddings with a pathology foundation model, and
(iii) aggregating tile embeddings into a slide-level prediction with either mean-pooling
or attention-based multiple-instance learning (MIL). We treat four endpoints: ER, PR, and
HER2 status (binary) and PAM50 intrinsic subtype (4-class). The pipeline outputs
hypothesis-level phenotype predictions only; no drug structure is used as input.

## M.2 Input representation

Each slide *s* is represented as a bag of tile embeddings **X**ₛ ∈ ℝ^{Nₛ×1024}, where Nₛ is the
number of retained tiles (256×256 px at 20×, Otsu tissue mask, per-patient cap 5000; see Data
Methods) and 1024 is the UNI v1 embedding dimension. Tile embeddings are pre-computed and frozen;
no gradients flow into the foundation model.

## M.3 Models

**Mean-pooling MLP (SlideMLP).** As a simple non-attention aggregator, we mean-pool the tile
embeddings to a 1024-d slide vector and pass it through a two-layer MLP (hidden dims [512, 256],
ReLU, dropout 0.3) to a task head (1 unit for binary, *C* units for multi-class).

**Gated-attention MIL (CLAM).** We independently reimplemented the CLAM architecture
(Lu et al., *Nat. Biomed. Eng.* 2021) from the published equations. A shared encoder
(Linear 1024→512, ReLU, dropout 0.25) maps each tile embedding to a 512-d representation.
A gated-attention module (Ilse et al., 2018) computes tile weights
a = softmax(**w**ᵀ(tanh(**U h**) ⊙ σ(**V h**))), with U, V ∈ ℝ^{256×512}, and forms an
attention-pooled slide vector Σₙ aₙ hₙ.

- **CLAM-SB (binary; ER/PR/HER2):** single attention branch + single linear classifier (512→1).
- **CLAM-MB (multi-class; PAM50):** one gated-attention branch and one linear head (512→1) per
  class; class logits are concatenated and softmaxed. This lets each subtype attend to distinct
  morphology.

## M.4 Endpoints and labels

Binary endpoints map IHC status Positive→1 / Negative→0; Equivocal/Indeterminate slides are
excluded. PAM50 is modeled as **4 classes (LumA, LumB, Basal, HER2-E)**; the Normal-like class
is excluded per the split policy (§4; weak morphological signal, Tafavvoghi 2024), which removes
79/28/20 slides from train/val/test and 13 from the external CPTAC set (395→382).

## M.5 Data splits (leakage control)

All models use a single **patient-level, site-disjoint** split of the TCGA-BRCA cohort
(no patient or TSS submitting-site appears in more than one fold), locked and hash-identified
(`split_hash = 5995f29d3978b831`; patient-overlap = 0, site-disjoint verified over 37 sites).
For ER, train/val/test = 707/152/151 slides (endpoint-specific counts differ after label
filtering). CPTAC-BRCA is held out entirely as an external test cohort (per-endpoint n:
ER 387, PR 375, HER2 294, PAM50 382), with 0 patient overlap with TCGA.

## M.6 Training

Models are trained one slide per step (MIL convention, batch size 1) with the Adam optimizer.
CLAM uses lr = 2×10⁻⁴, up to 50 epochs with early stopping (patience 7, best val-loss checkpoint
restored); SlideMLP uses lr = 1×10⁻³, 10 epochs. Loss is binary cross-entropy (binary endpoints)
or cross-entropy (PAM50). Random seed = 42. No fine-tuning of the foundation model. Models are
trained on TCGA only; the external cohort is never seen during training or model selection.

## M.7 Baselines

To test whether morphology adds value beyond trivial predictors, we compare against:
(1) **random** (predicts the training prevalence);
(2) **mean-embed** — multinomial/logistic regression on the mean-pooled tile embedding
(a "pixel-mean" style non-attention baseline);
(3) **subtype-only** (binary endpoints only) — predicts P(label | PAM50 subtype) learned on the
training set. Because PAM50 is defined in part by ESR1/ERBB2 pathway activity, subtype-only is
partly circular for ER/PR/HER2 and is therefore reported as a **ceiling reference**, not a floor
the model must clear. For PAM50 itself, subtype-only is undefined (predicting PAM50 from PAM50),
so mean-embed is the operative baseline.

## M.8 Evaluation and statistics

Primary metric is AUC (macro one-vs-rest for PAM50), with AUPRC and balanced accuracy reported
alongside. 95% confidence intervals use the bootstrap (1000–2000 resamples). Model-vs-baseline
comparisons use a **paired bootstrap** (identical resample indices applied to both predictors)
so the CI is on the AUC *difference*; two-sided approximate p-values are reported. Predicted
probabilities per patient are retained for all models and baselines to support these tests.

Two additional controls guard against shortcut learning:

- **Label-shuffle null (anti-shortcut).** For each endpoint we retrain with train labels randomly
  permuted (5 seeds), evaluated on the true val/external labels. A genuine morphological signal
  must place the real AUC outside this null band; a result inside the band is reported as a
  negative result.
- **Counterfactual attention faithfulness.** We remove the top-10% attention-weighted tiles versus
  an equal number of random tiles and measure the change in prediction. We distinguish
  probability-level faithfulness (mean |Δ predicted probability|) from ranking-level (AUC drop),
  reporting each explicitly rather than a single "faithfulness confirmed" flag.

External validation follows a **frozen-transfer** protocol: the TCGA-trained model is applied to
CPTAC without any re-fitting or threshold re-selection.

## M.9 Reproducibility

Every experiment directory contains config.yaml, model.pt, metrics.json, predictions, and a
Critic report, with the git commit hash and `split_hash` recorded in metrics.json. Shared inputs
(embeddings, manifests) are referenced by `/workspace/...` absolute paths for independent
re-execution.

---

## (참고) 확정 수치 요약 — 결과 절과 교차확인용

| 엔드포인트 | 모델 | 내부 val AUC | 외부 CPTAC AUC | 비고 |
|---|---|---|---|---|
| ER | CLAM-SB | 0.901 | 0.894 | subtype_only(ceiling) 0.962 |
| PR | CLAM-SB | 0.777 | 0.778 | subtype_only 0.912 |
| HER2 | CLAM-SB | 0.599 | 0.530 | shuffle-null 안 (신호 없음) |
| PAM50 | CLAM-MB (4-class) | 0.805 | 0.818 | mean_embed 0.653, paired +0.165 (p≈0) |

*작성 지침: 위 표는 Methods가 아니라 Results 소관이므로 최종 원고에서는 Results로 이동. Methods에는 방법·설정만 남긴다.*

---

*상태: 초안 v0.1. 데이터/임베딩 층(M.2, M.5 일부)은 kkkim 절과 정합 필요. 통계 프레이밍(#8)은 braveji Critic 판정(subtype_only=ceiling, faithfulness=proba-level 한정)을 반영함.*

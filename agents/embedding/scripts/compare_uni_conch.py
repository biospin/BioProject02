#!/usr/bin/env python3
"""
BIOP02-48 — UNI vs CONCH foundation-model comparison (slide-level, TCGA-BRCA).

Head-to-head embedding-quality comparison of two foundation models on the SAME
1010-slide cohort, using the already-mean-pooled slide_features.npz produced by
embed_umap.py (UNI 1024-d, CONCH 512-d). Two axes:

  (1) Phenotype linear-probe AUROC — how much molecular-phenotype signal is
      linearly decodable from each model's slide embedding. LogisticRegression
      probe, patient-grouped stratified 5-fold CV (no patient leaks across folds),
      per label: ER / PR / HER2 (binary) + PAM50 (multiclass macro-OvR).
      Higher = more downstream-useful embedding.

  (2) Site-confound (Howard 2021) — macro site-AUROC, read from the existing
      site_probe_report.json of each model. Lower = less submitting-site batch
      signal. (UNI 0.9977 vs CONCH 0.9782 already on record.)

Both models are scored on the identical slide set per label (intersection of
available slide_ids ∩ labeled rows) so AUROC deltas are not driven by cohort
differences. This is an embedding-QC / model-selection sanity comparison
(claim_level: sanity) — NOT a phenotype-prediction modeling claim (that is
sjpark's MLP deliverable) and not a Critic-gated result.

Inputs:
  --manifest        final manifest CSV (case_id, slide_id, er/pr/her2_status, pam50, split)
  --uni-features    UNI slide_features.npz  (X, slide_ids, case_ids)
  --conch-features  CONCH slide_features.npz
  --uni-site / --conch-site   (optional) site_probe_report.json for each model
  --out-dir         output directory

Outputs:
  comparison_report.json   per-label UNI vs CONCH AUROC + CI + delta + site-confound
  comparison.md            human-readable table + interpretation
  phenotype_auroc.png      grouped bar chart (UNI vs CONCH per label)

Requires: numpy, scikit-learn, matplotlib.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# label -> (positive class, negative class) for binary IHC; pam50 handled as multiclass
BINARY = {
    "er_status": ("Positive", "Negative"),
    "pr_status": ("Positive", "Negative"),
    "her2_status": ("Positive", "Negative"),  # Equivocal/Indeterminate/NotEval dropped
}
MULTICLASS = {"pam50": ["Basal", "HER2", "LumA", "LumB", "Normal"]}


def load_manifest(path: Path) -> dict:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {r["slide_id"]: r for r in rows}


def load_features(path: Path):
    d = np.load(path, allow_pickle=True)
    X = np.asarray(d["X"], dtype=np.float64)
    sids = np.array([str(s) for s in d["slide_ids"]])
    return X, sids


def aligned_probe(X, sids, meta, label, pos_neg, seed, n_boot):
    """Patient-grouped stratified 5-fold logistic probe; returns AUROC + bootstrap CI."""
    y, groups, idx = [], [], []
    if pos_neg is not None:  # binary
        pos, neg = pos_neg
        for i, s in enumerate(sids):
            r = meta.get(s)
            if not r:
                continue
            v = r[label]
            if v == pos:
                y.append(1); groups.append(r["case_id"]); idx.append(i)
            elif v == neg:
                y.append(0); groups.append(r["case_id"]); idx.append(i)
        multiclass = False
    else:  # pam50 multiclass
        valid = set(MULTICLASS[label])
        for i, s in enumerate(sids):
            r = meta.get(s)
            if not r:
                continue
            v = r[label]
            if v in valid:
                y.append(v); groups.append(r["case_id"]); idx.append(i)
        multiclass = True

    y = np.array(y); groups = np.array(groups); Xi = X[np.array(idx)]
    n_splits = 5
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(max_iter=4000, C=1.0, class_weight="balanced"))
    proba = cross_val_predict(clf, Xi, y, groups=groups, cv=cv, method="predict_proba")

    if multiclass:
        classes = np.unique(y)
        auroc = float(roc_auc_score(y, proba, multi_class="ovr", average="macro", labels=classes))
        score = lambda yy, pp: float(roc_auc_score(yy, pp, multi_class="ovr",
                                                    average="macro", labels=classes))
    else:
        auroc = float(roc_auc_score(y, proba[:, 1]))
        score = lambda yy, pp: float(roc_auc_score(yy, pp[:, 1]))

    rng = np.random.default_rng(seed)
    n = len(y); boots = []
    for _ in range(n_boot):
        b = rng.integers(0, n, n)
        try:
            if multiclass and len(np.unique(y[b])) < len(np.unique(y)):
                continue
            if not multiclass and len(np.unique(y[b])) < 2:
                continue
            boots.append(score(y[b], proba[b]))
        except ValueError:
            continue
    lo, hi = (round(float(np.percentile(boots, 2.5)), 4),
              round(float(np.percentile(boots, 97.5)), 4)) if boots else (None, None)
    return {
        "auroc": round(auroc, 4), "ci95": [lo, hi],
        "n": int(n), "n_patients": int(len(np.unique(groups))),
        "positives": (None if multiclass else int(y.sum())),
        "task": ("multiclass_ovr_macro" if multiclass else "binary"),
    }


def read_site(path):
    if path and Path(path).exists():
        d = json.loads(Path(path).read_text())
        return {"macro_ovr_auroc": d.get("macro_ovr_auroc"), "ci95": d.get("ci95")}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--uni-features", required=True, type=Path)
    ap.add_argument("--conch-features", required=True, type=Path)
    ap.add_argument("--uni-site", type=Path)
    ap.add_argument("--conch-site", type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bootstrap", type=int, default=1000)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    meta = load_manifest(args.manifest)
    Xu, su = load_features(args.uni_features)
    Xc, sc = load_features(args.conch_features)
    print(f"UNI  {Xu.shape}  CONCH {Xc.shape}")

    labels = list(BINARY.items()) + [(k, None) for k in MULTICLASS]
    results = {}
    for label, pn in labels:
        ru = aligned_probe(Xu, su, meta, label, pn, args.seed, args.bootstrap)
        rc = aligned_probe(Xc, sc, meta, label, pn, args.seed, args.bootstrap)
        delta = round(ru["auroc"] - rc["auroc"], 4)
        results[label] = {"UNI": ru, "CONCH": rc, "delta_uni_minus_conch": delta,
                          "winner": "UNI" if delta > 0 else ("CONCH" if delta < 0 else "tie")}
        print(f"{label:12} UNI {ru['auroc']:.4f}  CONCH {rc['auroc']:.4f}  "
              f"Δ {delta:+.4f}  (n={ru['n']})")

    site = {"UNI": read_site(args.uni_site), "CONCH": read_site(args.conch_site)}

    report = {
        "exp": "BIOP02-48_uni_vs_conch",
        "claim_level": "sanity",
        "cohort": "TCGA-BRCA slide-level mean-pooled",
        "uni_dim": int(Xu.shape[1]), "conch_dim": int(Xc.shape[1]),
        "probe": "LogisticRegression(class_weight=balanced) | StratifiedGroupKFold(5) by case_id",
        "phenotype": results,
        "site_confound": site,
        "interpretation": (
            "Phenotype AUROC: higher = more linearly-decodable molecular signal in the slide "
            "embedding (model-selection signal, not a prediction claim). Site AUROC: lower = less "
            "submitting-site batch confound. Probe is patient-grouped so no patient leaks across folds."
        ),
    }
    out_json = args.out_dir / "comparison_report.json"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print("wrote", out_json)

    # markdown table
    lines = ["# BIOP02-48 — UNI vs CONCH embedding comparison (TCGA-BRCA, slide-level)", "",
             f"- UNI dim **{Xu.shape[1]}** · CONCH dim **{Xc.shape[1]}** · probe: LogReg + StratifiedGroupKFold(5) by patient",
             "- claim_level: **sanity** (embedding QC / model selection — not a Critic-gated prediction claim)", "",
             "## Phenotype linear-probe AUROC (higher = better)", "",
             "| Label | n | UNI | CONCH | Δ(UNI−CONCH) | winner |",
             "|---|---|---|---|---|---|"]
    for label, r in results.items():
        u, c = r["UNI"], r["CONCH"]
        lines.append(f"| {label} | {u['n']} | {u['auroc']:.4f} [{u['ci95'][0]}, {u['ci95'][1]}] "
                     f"| {c['auroc']:.4f} [{c['ci95'][0]}, {c['ci95'][1]}] "
                     f"| {r['delta_uni_minus_conch']:+.4f} | **{r['winner']}** |")
    lines += ["", "## Site-confound (Howard 2021; lower = less batch signal)", ""]
    if site["UNI"] and site["CONCH"]:
        lines += ["| Model | site macro-AUROC |", "|---|---|",
                  f"| UNI | {site['UNI']['macro_ovr_auroc']} |",
                  f"| CONCH | {site['CONCH']['macro_ovr_auroc']} |"]
    lines += ["", "## Interpretation", "", report["interpretation"]]
    (args.out_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", args.out_dir / "comparison.md")

    # grouped bar chart
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labs = list(results.keys())
    uni_v = [results[l]["UNI"]["auroc"] for l in labs]
    con_v = [results[l]["CONCH"]["auroc"] for l in labs]
    x = np.arange(len(labs)); w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, uni_v, w, label=f"UNI ({Xu.shape[1]}d)", color="#2c7fb8")
    ax.bar(x + w/2, con_v, w, label=f"CONCH ({Xc.shape[1]}d)", color="#de2d26")
    for xi, (uv, cv) in enumerate(zip(uni_v, con_v)):
        ax.text(xi - w/2, uv + .005, f"{uv:.3f}", ha="center", va="bottom", fontsize=8)
        ax.text(xi + w/2, cv + .005, f"{cv:.3f}", ha="center", va="bottom", fontsize=8)
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance")
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.set_ylabel("phenotype linear-probe AUROC")
    ax.set_ylim(0.45, 1.0)
    ax.set_title("BIOP02-48 — UNI vs CONCH slide-level phenotype probe (patient-grouped 5-fold CV)")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out_dir / "phenotype_auroc.png", dpi=150)
    print("wrote", args.out_dir / "phenotype_auroc.png")


if __name__ == "__main__":
    main()

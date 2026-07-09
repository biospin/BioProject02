#!/usr/bin/env python3
"""
BIOP02-48/-38 — N-way foundation-model embedding comparison (slide-level, TCGA-BRCA).

Generalizes compare_uni_conch.py to an arbitrary set of models (UNI / CONCH /
EXAONE / ...). Each model is scored with the IDENTICAL probe on the IDENTICAL
per-label slide set, so AUROC deltas reflect embedding quality, not cohort drift.

Axes (unchanged from the 2-way version):
  (1) Phenotype linear-probe AUROC — LogisticRegression(class_weight=balanced),
      patient-grouped StratifiedGroupKFold(5). ER/PR/HER2 binary + PAM50 macro-OvR.
      Higher = more linearly-decodable molecular signal. 1000x bootstrap 95% CI.
  (2) Site-confound (Howard 2021) — macro site-AUROC from each model's
      site_probe_report.json (optional). Lower = less submitting-site batch signal.

Per label the slide set is the INTERSECTION of labeled rows across ALL models
(common slide_ids) so every model is scored on exactly the same slides.

claim_level: sanity (embedding QC / model selection — NOT a Critic-gated
phenotype-prediction claim; that is sjpark's MLP deliverable).

Model spec:  --model NAME=features.npz[:site.json]   (repeatable)
  features.npz must contain X (n,dim) + slide_ids (+ case_ids used as CV groups).
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

BINARY = {
    "er_status": ("Positive", "Negative"),
    "pr_status": ("Positive", "Negative"),
    "her2_status": ("Positive", "Negative"),
}
MULTICLASS = {"pam50": ["Basal", "HER2", "LumA", "LumB", "Normal"]}


def load_manifest(path: Path) -> dict:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["slide_id"]: r for r in csv.DictReader(fh)}


def load_features(path: Path):
    d = np.load(path, allow_pickle=True)
    X = np.asarray(d["X"], dtype=np.float64)
    sids = np.array([str(s) for s in d["slide_ids"]])
    return X, sids


def labeled_slides(sids, meta, label, pos_neg):
    """Return {slide_id: (y, case_id)} for slides with a usable label."""
    out = {}
    if pos_neg is not None:
        pos, neg = pos_neg
        for s in sids:
            r = meta.get(s)
            if not r:
                continue
            if r[label] == pos:
                out[s] = (1, r["case_id"])
            elif r[label] == neg:
                out[s] = (0, r["case_id"])
    else:
        valid = set(MULTICLASS[label])
        for s in sids:
            r = meta.get(s)
            if r and r[label] in valid:
                out[s] = (r[label], r["case_id"])
    return out


def probe(X, sids, keep, label, multiclass, seed, n_boot):
    """LogReg probe on the given (already-common) slide set; AUROC + bootstrap CI."""
    pos = {s: i for i, s in enumerate(sids)}
    idx = [pos[s] for s in keep]
    Xi = X[np.array(idx)]
    y = np.array([keep[s][0] for s in keep])
    groups = np.array([keep[s][1] for s in keep])

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
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
    return {"auroc": round(auroc, 4), "ci95": [lo, hi],
            "n": int(n), "n_patients": int(len(np.unique(groups)))}


def read_site(path):
    if path and Path(path).exists():
        d = json.loads(Path(path).read_text())
        return d.get("macro_ovr_auroc")
    return None


def parse_model(spec):
    name, rest = spec.split("=", 1)
    feat, site = (rest.split(":", 1) + [None])[:2]
    return name, Path(feat), (Path(site) if site else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--model", action="append", required=True,
                    help="NAME=features.npz[:site.json] (repeatable)")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bootstrap", type=int, default=1000)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    meta = load_manifest(args.manifest)
    models = []  # (name, X, sids, site_path)
    for spec in args.model:
        name, feat, site = parse_model(spec)
        X, sids = load_features(feat)
        models.append((name, X, sids, site))
        print(f"{name:16} X{X.shape}  slides={len(sids)}")

    labels = list(BINARY.items()) + [(k, None) for k in MULTICLASS]
    results = {}
    for label, pn in labels:
        multiclass = pn is None
        # per-model labeled sets, then intersect to a common slide set
        per = {name: labeled_slides(sids, meta, label, pn) for name, _, sids, _ in models}
        common = set.intersection(*[set(d) for d in per.values()])
        common = sorted(common)
        row = {"n": len(common)}
        best_name, best_auroc = None, -1.0
        for name, X, sids, _ in models:
            keep = {s: per[name][s] for s in common}
            r = probe(X, sids, keep, label, multiclass, args.seed, args.bootstrap)
            row[name] = r
            if r["auroc"] > best_auroc:
                best_auroc, best_name = r["auroc"], name
        row["winner"] = best_name
        results[label] = row
        cells = "  ".join(f"{name} {row[name]['auroc']:.4f}" for name, *_ in models)
        print(f"{label:12} n={len(common):4}  {cells}  win={best_name}")

    site = {name: read_site(site_p) for name, _, _, site_p in models}
    dims = {name: int(X.shape[1]) for name, X, _, _ in models}

    report = {
        "exp": "BIOP02-48_model_comparison",
        "claim_level": "sanity",
        "cohort": "TCGA-BRCA slide-level",
        "models": [name for name, *_ in models],
        "dims": dims,
        "probe": "LogisticRegression(class_weight=balanced) | StratifiedGroupKFold(5) by case_id",
        "note": ("Per label all models scored on the identical intersection slide set. "
                 "UNI/CONCH = mean-pooled tile embeddings (256^2@20x, Otsu, cap 5000). "
                 "EXAONE = internal tiling+Macenko@0.5mpp; representation noted in model name "
                 "(patch_mean = apples-to-apples pooling, slide_global = EXAONE's own aggregation). "
                 "So deltas conflate model + tiling pipeline, not model alone."),
        "phenotype": results,
        "site_confound": site,
    }
    (args.out_dir / "comparison_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False))
    print("wrote", args.out_dir / "comparison_report.json")

    # markdown
    names = [name for name, *_ in models]
    hdr = "| Label | n | " + " | ".join(names) + " | winner |"
    sep = "|---|---|" + "|".join(["---"] * len(names)) + "|---|"
    lines = ["# BIOP02-48 — foundation-model embedding comparison (TCGA-BRCA, slide-level)", "",
             "- " + " · ".join(f"{n} **{dims[n]}d**" for n in names)
             + " · probe: LogReg + StratifiedGroupKFold(5) by patient",
             "- claim_level: **sanity** (embedding QC / model selection — not a Critic-gated claim)",
             "- per label: identical intersection slide set across all models", "",
             "## Phenotype linear-probe AUROC (higher = better)", "", hdr, sep]
    for label, r in results.items():
        cells = " | ".join(f"{r[n]['auroc']:.4f} [{r[n]['ci95'][0]}, {r[n]['ci95'][1]}]" for n in names)
        lines.append(f"| {label} | {r['n']} | {cells} | **{r['winner']}** |")
    lines += ["", "## Site-confound (Howard 2021; lower = less batch signal)", "",
              "| Model | site macro-AUROC |", "|---|---|"]
    for n in names:
        lines.append(f"| {n} | {site[n] if site[n] is not None else 'n/a'} |")
    lines += ["", "## Interpretation", "",
              "Phenotype AUROC: higher = more linearly-decodable molecular signal (model-selection "
              "signal, not a prediction claim). Site AUROC: lower = less submitting-site batch "
              "confound. Probe is patient-grouped so no patient leaks across folds.", "",
              "> Caveat: " + report["note"]]
    (args.out_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", args.out_dir / "comparison.md")

    # grouped bar chart
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labs = list(results.keys())
    x = np.arange(len(labs))
    w = 0.8 / len(names)
    colors = ["#2c7fb8", "#de2d26", "#31a354", "#756bb1", "#e6550d"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for j, n in enumerate(names):
        vals = [results[l][n]["auroc"] for l in labs]
        off = (j - (len(names) - 1) / 2) * w
        ax.bar(x + off, vals, w, label=f"{n} ({dims[n]}d)", color=colors[j % len(colors)])
        for xi, v in zip(x, vals):
            ax.text(xi + off, v + .005, f"{v:.3f}", ha="center", va="bottom", fontsize=7)
    ax.axhline(0.5, ls="--", c="gray", lw=1, label="chance")
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.set_ylabel("phenotype linear-probe AUROC")
    ax.set_ylim(0.45, 1.0)
    ax.set_title("BIOP02-48 — foundation-model slide-level phenotype probe (patient-grouped 5-fold CV)")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out_dir / "phenotype_auroc.png", dpi=150)
    print("wrote", args.out_dir / "phenotype_auroc.png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Exp2-A: SITE-CLASSIFIER PROBE — quantify residual submitting-site (tss_code) signal
in slide-level foundation-model embeddings (Howard 2021 site-confound).

A logistic-regression probe predicts the TCGA submitting site from slide-level
embeddings (tiles mean-pooled), evaluated with patient-grouped CV so no patient
leaks across folds. High macro one-vs-rest AUROC ⇒ embeddings encode site →
site-disjoint splitting (split_policy_v0) is justified and prior random-split
phenotype numbers are site-inflated. Reference: Howard 2021 reports site AUROC
0.964–0.998 surviving stain normalization; chance ≈ 0.5.

This binds Critic #1 (data leakage) and is the empirical half of Exp2
(research/experiment_plan.md). GPU not required.

Inputs:
  --manifest    manifest CSV from build_manifest.py (needs file_name, case_id, tss_code)
  --embeddings  directory of per-slide tile embeddings <stem><suffix>.npy (n_tiles × dim);
                slide stem = Path(file_name).stem (matches run_batch/stream output for UNI/CONCH)
  --features    (alt) precomputed slide-level features .npz with arrays X (n×d) + slide_ids
                — use this to skip per-slide loading.

Output: console summary + --report JSON (macro AUROC + bootstrap CI + per-site + shuffle baseline).

Requires: numpy, scikit-learn.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import GroupKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:  # pragma: no cover
    raise SystemExit("scikit-learn required: pip install scikit-learn")
try:  # patient-stratified-grouped CV preferred (sklearn >=1.0); else GroupKFold
    from sklearn.model_selection import StratifiedGroupKFold
except ImportError:  # pragma: no cover
    StratifiedGroupKFold = None


def load_manifest(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for col in ("file_name", "case_id", "tss_code"):
        if rows and col not in rows[0]:
            raise SystemExit(f"manifest missing column: {col} (rebuild with build_manifest.py)")
    return rows


def slide_features_from_dir(rows: list[dict], emb_dir: Path, suffix: str):
    """Mean-pool each slide's tile embeddings to one slide-level vector."""
    X, sites, groups, ids, missing = [], [], [], [], []
    for r in rows:
        stem = Path(r["file_name"]).stem  # ".svs" stripped
        p = emb_dir / f"{stem}{suffix}"
        if not p.exists():
            missing.append(stem)
            continue
        arr = np.load(p, mmap_mode="r")
        X.append(np.asarray(arr).mean(axis=0))
        sites.append(r["tss_code"])
        groups.append(r["case_id"])
        ids.append(r["slide_id"])
    if missing:
        print(f"WARN: {len(missing)} slides missing embeddings (skipped), e.g. {missing[:3]}")
    if not X:
        raise SystemExit("no slide embeddings found — check --embeddings / --emb-suffix")
    return np.vstack(X), np.array(sites), np.array(groups), np.array(ids)


def load_features_npz(path: Path, rows: list[dict]):
    d = np.load(path, allow_pickle=True)
    X = d["X"]
    sid = np.array([str(s) for s in d["slide_ids"]])
    meta = {r["slide_id"]: r for r in rows}
    keep = [i for i, s in enumerate(sid) if s in meta]
    X = X[keep]; sid = sid[keep]
    sites = np.array([meta[s]["tss_code"] for s in sid])
    groups = np.array([meta[s]["case_id"] for s in sid])
    return X, sites, groups, sid


def macro_ovr_auroc(y: np.ndarray, proba: np.ndarray, classes: np.ndarray) -> float:
    # only classes present in y can be scored OvR
    present = [i for i, c in enumerate(classes) if (y == c).sum() > 0 and (y != c).sum() > 0]
    if len(present) < 2:
        return float("nan")
    aucs = []
    for i in present:
        aucs.append(roc_auc_score((y == classes[i]).astype(int), proba[:, i]))
    return float(np.mean(aucs))


def per_site_auroc(y, proba, classes) -> dict:
    out = {}
    for i, c in enumerate(classes):
        if (y == c).sum() > 0 and (y != c).sum() > 0:
            out[str(c)] = round(float(roc_auc_score((y == c).astype(int), proba[:, i])), 4)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Exp2-A site-classifier probe on slide embeddings")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--embeddings", help="dir of per-slide tile embeddings")
    ap.add_argument("--features", help="alt: precomputed slide features .npz (X, slide_ids)")
    ap.add_argument("--emb-suffix", default="_uni_embeddings.npy")
    ap.add_argument("--min-site", type=int, default=10, help="drop sites with < this many slides")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--report", help="output JSON path")
    args = ap.parse_args()
    if not args.embeddings and not args.features:
        raise SystemExit("provide --embeddings or --features")

    rows = load_manifest(Path(args.manifest))
    if args.features:
        X, sites, groups, ids = load_features_npz(Path(args.features), rows)
    else:
        X, sites, groups, ids = slide_features_from_dir(rows, Path(args.embeddings), args.emb_suffix)

    # drop tiny sites (need a meaningful per-site classifier + CV)
    counts = {s: int((sites == s).sum()) for s in np.unique(sites)}
    keep_sites = {s for s, n in counts.items() if n >= args.min_site}
    mask = np.array([s in keep_sites for s in sites])
    X, sites, groups, ids = X[mask], sites[mask], groups[mask], ids[mask]
    dropped = {s: n for s, n in counts.items() if s not in keep_sites}
    if len(keep_sites) < 2:
        raise SystemExit(f"need >=2 sites with >={args.min_site} slides; have {len(keep_sites)}")

    n_splits = max(2, min(args.folds, min(counts[s] for s in keep_sites)))
    clf = make_pipeline(StandardScaler(),
                        LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"))
    if StratifiedGroupKFold is not None:
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=args.seed)
    else:
        cv = GroupKFold(n_splits=n_splits)  # no stratification (sklearn <1.0)

    proba = cross_val_predict(clf, X, sites, groups=groups, cv=cv, method="predict_proba")
    classes = np.unique(sites)  # cross_val_predict columns are sorted-class order
    auroc = macro_ovr_auroc(sites, proba, classes)
    per_site = per_site_auroc(sites, proba, classes)

    # bootstrap CI over slides (on out-of-fold predictions)
    rng = np.random.default_rng(args.seed)
    boots = []
    n = len(sites)
    for _ in range(args.bootstrap):
        idx = rng.integers(0, n, n)
        v = macro_ovr_auroc(sites[idx], proba[idx], classes)
        if not np.isnan(v):
            boots.append(v)
    lo, hi = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))) if boots else (float("nan"),) * 2

    # shuffle-label baseline (one grouped-CV run with permuted sites) ≈ chance 0.5
    perm = rng.permutation(n)
    proba_shuf = cross_val_predict(clf, X, sites[perm], groups=groups, cv=cv, method="predict_proba")
    auroc_shuf = macro_ovr_auroc(sites[perm], proba_shuf, np.unique(sites[perm]))

    report = {
        "exp": "Exp2-A_site_classifier_probe",
        "macro_ovr_auroc": round(auroc, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "shuffle_baseline_auroc": round(auroc_shuf, 4),
        "howard_reference": [0.964, 0.998],
        "n_slides": int(n), "n_sites": int(len(keep_sites)), "n_patients": int(len(np.unique(groups))),
        "cv_folds": n_splits, "min_site": args.min_site,
        "per_site_auroc": per_site,
        "dropped_sites": dropped,
        "interpretation": (
            "AUROC >> 0.5 ⇒ embeddings encode submitting-site → site-disjoint split justified, "
            "random-split phenotype numbers inflated (report site-disjoint as primary)."
        ),
    }
    print(json.dumps({k: report[k] for k in
                      ("macro_ovr_auroc", "ci95", "shuffle_baseline_auroc",
                       "n_slides", "n_sites", "n_patients", "cv_folds")}, indent=2))
    print(f"Howard 2021 reference site-AUROC: 0.964–0.998 | chance ≈ 0.5")
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()

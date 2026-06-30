#!/usr/bin/env python3
"""
BIOP02-63 — Fig 2: Embedding UMAP sanity for slide-level foundation-model features.

Mean-pools per-slide tile embeddings (n_tiles x dim) to a single slide vector,
runs UMAP to 2D, and renders panels colored by molecular subtype (PAM50), ER/PR/
HER2 IHC status, submitting site (tss_code — Howard 2021 site-confound sanity),
and patient-level split. Also dumps the slide-level feature matrix as .npz so it
can be reused by site_classifier_probe.py (--features) without re-loading tiles.

This is a sanity figure, not a model experiment — no claim_level / Critic gate.

Inputs:
  --manifest    final manifest CSV (case_id, slide_id, file_name, tss_code,
                er_status, pr_status, her2_status, pam50, split, ...)
  --embeddings  dir of per-slide embeddings <file_stem><suffix>.npy
  --suffix      filename suffix after the slide stem (default _uni_embeddings.npy)

Outputs (under --out-dir):
  slide_features.npz   X (n x dim) float32 + slide_ids + case_ids
  umap_coords.csv      slide_id, case_id, umap_x, umap_y, labels
  umap_<label>.png     one panel per categorical label
  umap_panels.png      combined grid

Requires: numpy, umap-learn, scikit-learn, matplotlib.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

LABEL_COLS = ["pam50", "er_status", "pr_status", "her2_status", "tss_code", "split"]
MISSING = {"", "na", "n/a", "none", "nan", "indeterminate", "unknown", "equivocal", "[not available]"}


def load_manifest(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def clean(val: str) -> str:
    v = (val or "").strip()
    return "NA" if v.lower() in MISSING else v


def stem_of(file_name: str) -> str:
    """file_name 'X.svs' -> 'X' (matches <stem>_uni_embeddings.npy)."""
    s = Path(file_name).name
    return s[:-4] if s.lower().endswith(".svs") else Path(s).stem


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--embeddings", required=True, type=Path)
    ap.add_argument("--suffix", default="_uni_embeddings.npy")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--n-neighbors", type=int, default=15)
    ap.add_argument("--min-dist", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_manifest(args.manifest)
    feats, slide_ids, case_ids, meta = [], [], [], []
    missing = 0
    for r in rows:
        npy = args.embeddings / f"{stem_of(r['file_name'])}{args.suffix}"
        if not npy.exists():
            missing += 1
            continue
        arr = np.load(npy)
        feats.append(arr.mean(axis=0).astype(np.float32))   # mean-pool tiles -> slide vector
        slide_ids.append(r["slide_id"])
        case_ids.append(r["case_id"])
        meta.append({c: clean(r.get(c, "")) for c in LABEL_COLS})
    if not feats:
        raise SystemExit("no embeddings matched the manifest — check --embeddings/--suffix")
    X = np.vstack(feats)
    print(f"loaded {X.shape[0]} slides x {X.shape[1]} dim  (manifest rows missing embeddings: {missing})")

    np.savez_compressed(
        args.out_dir / "slide_features.npz",
        X=X, slide_ids=np.array(slide_ids), case_ids=np.array(case_ids),
    )

    import umap
    from sklearn.preprocessing import StandardScaler

    Xs = StandardScaler().fit_transform(X)
    reducer = umap.UMAP(
        n_neighbors=args.n_neighbors, min_dist=args.min_dist,
        n_components=2, metric="cosine", random_state=args.seed,
    )
    emb = reducer.fit_transform(Xs)
    print("UMAP done:", emb.shape)

    # coords CSV
    with open(args.out_dir / "umap_coords.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slide_id", "case_id", "umap_x", "umap_y"] + LABEL_COLS)
        for i in range(len(slide_ids)):
            w.writerow([slide_ids[i], case_ids[i], f"{emb[i,0]:.4f}", f"{emb[i,1]:.4f}"]
                       + [meta[i][c] for c in LABEL_COLS])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def panel(ax, label_col, title):
        labels = np.array([m[label_col] for m in meta])
        cats = sorted(set(labels), key=lambda x: (x == "NA", x))
        cmap = plt.get_cmap("tab20" if len(cats) > 10 else "tab10")
        for j, c in enumerate(cats):
            mask = labels == c
            color = (0.8, 0.8, 0.8, 0.5) if c == "NA" else cmap(j % cmap.N)
            ax.scatter(emb[mask, 0], emb[mask, 1], s=6, color=color, label=f"{c} ({mask.sum()})", linewidths=0)
        ax.set_title(title, fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        ax.legend(markerscale=2, fontsize=6, loc="best", framealpha=0.6)

    titles = {
        "pam50": "PAM50 subtype", "er_status": "ER (IHC)", "pr_status": "PR (IHC)",
        "her2_status": "HER2 (IHC)", "tss_code": "Submitting site (TSS)", "split": "Patient split",
    }
    # individual panels
    for col in LABEL_COLS:
        fig, ax = plt.subplots(figsize=(7, 6))
        panel(ax, col, f"UNI slide-level UMAP — {titles[col]}")
        fig.tight_layout()
        fig.savefig(args.out_dir / f"umap_{col}.png", dpi=150)
        plt.close(fig)
    # combined grid
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    for ax, col in zip(axes.ravel(), LABEL_COLS):
        panel(ax, col, titles[col])
    fig.suptitle(f"BIOP02 — UNI slide-level embedding UMAP sanity (n={X.shape[0]})", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(args.out_dir / "umap_panels.png", dpi=150)
    plt.close(fig)
    print("wrote figures to", args.out_dir)


if __name__ == "__main__":
    main()

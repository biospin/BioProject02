#!/usr/bin/env python3
"""
BIOP02-48/-38 — Assemble EXAONE Path 2.0 per-slide npz into a single
slide_features.npz (X, slide_ids, case_ids), matching the format produced by
embed_umap.py for UNI/CONCH so the 3-way comparison runs on the identical layout.

EXAONE extract_exaone.py writes <stem_of(file_name)>_exaone.npz per slide with:
  slide_global (768,)  — EXAONE's own third-stage slide aggregation
  patch_mean   (768,)  — mean of first-stage per-tile features (apples-to-apples
                         with UNI/CONCH mean-pooling)

--rep selects which 768-d vector becomes X:
  patch_mean   (default) — comparable to UNI/CONCH mean-pooled slide vectors
  slide_global           — EXAONE's designed slide embedding

Slide matching uses stem_of(file_name) (== the EXAONE output basename), exactly
like embed_umap.py, so slide_ids/case_ids align with the UNI/CONCH feature sets.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def stem_of(file_name: str) -> str:
    s = Path(file_name).name
    return s[:-4] if s.lower().endswith(".svs") else Path(s).stem


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--exaone-dir", required=True, type=Path,
                    help="dir of <stem>_exaone.npz files")
    ap.add_argument("--rep", choices=["patch_mean", "slide_global"], default="patch_mean")
    ap.add_argument("--out", required=True, type=Path, help="output slide_features.npz")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, newline="") as fh:
        rows = list(csv.DictReader(fh))

    feats, slide_ids, case_ids, missing = [], [], [], []
    for r in rows:
        npz = args.exaone_dir / f"{stem_of(r['file_name'])}_exaone.npz"
        if not npz.exists():
            missing.append(r["slide_id"])
            continue
        d = np.load(npz)
        v = np.asarray(d[args.rep], dtype=np.float32).reshape(-1)
        if v.shape[0] != 768 or not np.isfinite(v).all():
            missing.append(r["slide_id"])  # treat malformed as missing (loud)
            print(f"BAD {r['slide_id']} shape={v.shape} finite={np.isfinite(v).all()}")
            continue
        feats.append(v)
        slide_ids.append(r["slide_id"])
        case_ids.append(r["case_id"])

    if not feats:
        raise SystemExit("no EXAONE features matched the manifest — check --exaone-dir")
    X = np.vstack(feats)
    print(f"rep={args.rep}  loaded {X.shape[0]} slides x {X.shape[1]} dim  "
          f"(manifest rows missing: {len(missing)})")
    if missing:
        print("missing slide_ids:", ", ".join(missing[:20]),
              ("..." if len(missing) > 20 else ""))

    np.savez_compressed(args.out, X=X,
                        slide_ids=np.array(slide_ids), case_ids=np.array(case_ids))
    print("wrote", args.out)


if __name__ == "__main__":
    main()

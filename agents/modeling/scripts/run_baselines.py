"""
Run all 3 trivial baselines and print comparison table.

Smoke-test (no real data):
    python agents/modeling/scripts/run_baselines.py --smoke_test

Real mode:
    python agents/modeling/scripts/run_baselines.py \
        --manifest /data/embeddings/biop02/embedding_manifest.csv \
        --label_col er_status
"""

import argparse
import json
import csv
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.trivial import RandomBaseline, MajorityBaseline, MeanEmbedBaseline, evaluate


def make_dummy_dataset(n_slides: int = 20, dim: int = 1024, seed: int = 42):
    rng = np.random.default_rng(seed)
    X = [rng.standard_normal((rng.integers(100, 500), dim)).astype(np.float32) for _ in range(n_slides)]
    y = np.array([i % 2 for i in range(n_slides)], dtype=np.float32)
    return X, y


def load_manifest_dataset(manifest_path: str, label_col: str):
    X, y = [], []
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            emb_path = row.get("embedding_path", "")
            label_val = row.get(label_col, "")
            if not emb_path or not label_val:
                continue
            X.append(np.load(emb_path))
            y.append(float(label_val))
    return X, np.array(y, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="")
    parser.add_argument("--label_col", default="er_status")
    parser.add_argument("--smoke_test", action="store_true")
    parser.add_argument("--out_dir", default="/workspace/agents/modeling/experiments/baselines")
    args = parser.parse_args()

    if args.smoke_test or not args.manifest or not Path(args.manifest).exists():
        print("Smoke-test mode: using dummy embeddings")
        X, y = make_dummy_dataset()
    else:
        X, y = load_manifest_dataset(args.manifest, args.label_col)

    n = len(X)
    split = int(n * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    print(f"Slides: train={len(X_train)} val={len(X_val)}\n")

    baselines = [
        ("random",     RandomBaseline()),
        ("majority",   MajorityBaseline()),
        ("mean_embed", MeanEmbedBaseline()),
    ]

    results = []
    for name, clf in baselines:
        clf.fit(X_train, y_train)
        proba = clf.predict_proba(X_val)
        m = evaluate(name, proba, y_val)
        results.append(m)
        print(f"[{name:12s}]  AUC={m['auc']}  AUPRC={m['auprc']}  BalAcc={m['balanced_accuracy']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "trivial_baselines.json").write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_dir}/trivial_baselines.json")


if __name__ == "__main__":
    main()

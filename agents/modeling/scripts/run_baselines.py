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
import datetime
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


LABEL_MAP = {"positive": 1.0, "negative": 0.0}

def load_manifest_dataset(manifest_path: str, label_col: str, split: str = None):
    X, y = [], []
    skipped = 0
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if split and row.get("split", "").lower() != split:
                continue
            emb_path = row.get("embedding_path", "")
            label_raw = row.get(label_col, "").strip().lower()
            if not emb_path or label_raw not in LABEL_MAP:
                skipped += 1
                continue
            X.append(np.load(emb_path))
            y.append(LABEL_MAP[label_raw])
    if skipped:
        print(f"  [skip] {skipped} rows (Equivocal/Indeterminate/missing)")
    return X, np.array(y, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="")
    parser.add_argument("--label_col", default="er")
    parser.add_argument("--smoke_test", action="store_true")
    parser.add_argument("--username", default="sjpark")
    parser.add_argument("--task", default="er_status")
    parser.add_argument("--tag", default="", help="실험 태그 (예: dummy_v1, uni_v1). 미지정 시 날짜 사용")
    parser.add_argument("--commit_hash", default="", help="git commit hash (서버 실행 시 로컬에서 명시적으로 전달)")
    parser.add_argument("--output_dir", default="/workspace/agents/modeling/experiments")
    args = parser.parse_args()

    smoke_test = args.smoke_test or not args.manifest or not Path(args.manifest).exists()

    if smoke_test:
        print("Smoke-test mode: using dummy embeddings")
        X, y = make_dummy_dataset()
        n = len(X)
        sp = int(n * 0.8)
        X_train, X_val = X[:sp], X[sp:]
        y_train, y_val = y[:sp], y[sp:]
    else:
        X_train, y_train = load_manifest_dataset(args.manifest, args.label_col, split="train")
        X_val,   y_val   = load_manifest_dataset(args.manifest, args.label_col, split="val")
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

    # 실험 디렉토리: experiments/<username>/<task>_<tag>_baselines/
    tag = args.tag if args.tag else datetime.datetime.now().strftime("%Y%m%d")
    suffix = f"{args.task}_{tag}_baselines" + ("_smoke" if smoke_test else "")
    out_dir = Path(args.output_dir) / args.username / suffix
    out_dir.mkdir(parents=True, exist_ok=True)

    import subprocess
    def get_git_hash():
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        except Exception:
            return "unknown"

    commit_hash = args.commit_hash if args.commit_hash else get_git_hash()

    output = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "task": args.task,
        "label_col": args.label_col,
        "manifest": args.manifest,
        "smoke_test": smoke_test,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "commit_hash": commit_hash,
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "baselines": results,
    }
    (out_dir / "trivial_baselines.json").write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_dir}/trivial_baselines.json")


if __name__ == "__main__":
    main()

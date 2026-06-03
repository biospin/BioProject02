"""
MLP baseline training script.

Smoke-test mode (no real embeddings):
    python agents/modeling/scripts/train.py \
        --config agents/modeling/configs/baseline_er_status.yaml \
        --smoke_test

Real mode (after embedding manifest is ready):
    python agents/modeling/scripts/train.py \
        --config agents/modeling/configs/baseline_er_status.yaml
"""

import argparse
import json
import random
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.mlp import SlideMLP


def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def make_dummy_dataset(n_slides: int, embedding_dim: int, seed: int):
    rng = np.random.default_rng(seed)
    dataset = []
    for i in range(n_slides):
        n_tiles = rng.integers(100, 500)
        emb = torch.tensor(rng.standard_normal((n_tiles, embedding_dim)).astype(np.float32))
        label = torch.tensor(float(i % 2))  # alternating 0/1
        dataset.append((emb, label))
    return dataset


LABEL_MAP = {"positive": 1.0, "negative": 0.0}

def load_manifest_dataset(manifest_path: str, label_col: str, split: str = None):
    """
    kkkim manifest 형식 지원:
    - split 컬럼으로 train/val/test 분리 (없으면 전체 반환)
    - 레이블: "Positive"→1, "Negative"→0, 나머지(Equivocal/Indeterminate 등) 제외
    """
    import csv
    dataset = []
    skipped = 0
    with open(manifest_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if split and row.get("split", "").lower() != split:
                continue
            emb_path = row.get("embedding_path", "")
            label_raw = row.get(label_col, "").strip().lower()
            if not emb_path or label_raw not in LABEL_MAP:
                skipped += 1
                continue
            emb = torch.tensor(np.load(emb_path))
            label = torch.tensor(LABEL_MAP[label_raw])
            dataset.append((emb, label))
    if skipped:
        print(f"  [skip] {skipped} rows (Equivocal/Indeterminate/missing)")
    return dataset


def train(config: dict, smoke_test: bool):
    set_seed(config["train"]["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    dim = config["embedding_dim"]

    manifest = config["data"]["embedding_manifest"]
    if smoke_test or not Path(manifest).exists():
        print("Smoke-test mode: using dummy embeddings")
        dataset = make_dummy_dataset(config["data"]["n_dummy_slides"], dim, config["train"]["seed"])
        n = len(dataset)
        split_idx = int(n * 0.8)
        train_set, val_set = dataset[:split_idx], dataset[split_idx:]
    else:
        print(f"Loading manifest: {manifest}")
        label_col = config["data"]["label_col"]
        train_set = load_manifest_dataset(manifest, label_col, split="train")
        val_set   = load_manifest_dataset(manifest, label_col, split="val")
    print(f"Slides: train={len(train_set)} val={len(val_set)}")

    model = SlideMLP(
        input_dim=dim,
        hidden_dims=config["model"]["hidden_dims"],
        dropout=config["model"]["dropout"],
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=config["train"]["lr"])
    criterion = nn.BCEWithLogitsLoss()

    best_val_loss = float("inf")
    for epoch in range(1, config["train"]["epochs"] + 1):
        model.train()
        train_loss = 0.0
        for emb, label in train_set:
            emb, label = emb.to(device), label.to(device)
            optimizer.zero_grad()
            logit = model(emb)
            loss = criterion(logit, label.unsqueeze(0))
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss, correct = 0.0, 0
        with torch.no_grad():
            for emb, label in val_set:
                emb, label = emb.to(device), label.to(device)
                logit = model(emb)
                val_loss += criterion(logit, label.unsqueeze(0)).item()
                pred = (torch.sigmoid(logit) > 0.5).float()
                correct += (pred == label).sum().item()

        avg_val = val_loss / max(len(val_set), 1)
        acc = correct / max(len(val_set), 1)
        print(f"Epoch {epoch:02d} | train_loss={train_loss/len(train_set):.4f} | val_loss={avg_val:.4f} | val_acc={acc:.3f}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val

    out_dir = Path(config["output_dir"]) / f"{config['task']}_smoke" if smoke_test else Path(config["output_dir"]) / config["task"]
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), out_dir / "model.pt")

    metrics = {
        "task": config["task"],
        "model": "SlideMLP",
        "embedding_model": config["embedding_model"],
        "smoke_test": smoke_test,
        "n_train": len(train_set),
        "n_val": len(val_set),
        "best_val_loss": round(best_val_loss, 4),
        "auc": None,
        "auprc": None,
        "balanced_accuracy": None,
        "commit_hash": get_git_commit_hash(),
        "wandb_run_id": None,
        "mlflow_run_id": None,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved: {out_dir}/model.pt + metrics.json")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke_test", action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    t0 = time.time()
    metrics = train(config, args.smoke_test)
    print(f"\nDone in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

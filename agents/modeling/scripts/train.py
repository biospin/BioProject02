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
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.mlp import SlideMLP


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


def load_manifest_dataset(manifest_path: str, label_col: str):
    import csv
    dataset = []
    with open(manifest_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            emb_path = row.get("embedding_path", "")
            label_val = row.get(label_col, "")
            if not emb_path or not label_val:
                continue
            emb = torch.tensor(np.load(emb_path))
            label = torch.tensor(float(label_val))
            dataset.append((emb, label))
    return dataset


def train(config: dict, smoke_test: bool):
    set_seed(config["train"]["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    dim = config["embedding_dim"]

    if smoke_test or not Path(config["data"]["embedding_manifest"]).exists():
        print("Smoke-test mode: using dummy embeddings")
        dataset = make_dummy_dataset(config["data"]["n_dummy_slides"], dim, config["train"]["seed"])
    else:
        print(f"Loading manifest: {config['data']['embedding_manifest']}")
        dataset = load_manifest_dataset(config["data"]["embedding_manifest"], config["data"]["label_col"])

    n = len(dataset)
    split = int(n * 0.8)
    train_set, val_set = dataset[:split], dataset[split:]
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
        "commit_hash": None,
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

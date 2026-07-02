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
import datetime
import json
import random
import shutil
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

PAM50_MAP = {"luma": 0, "lumb": 1, "basal": 2, "her2": 3, "normal": 4}
PAM50_CLASSES = ["LumA", "LumB", "Basal", "HER2", "Normal"]


def load_manifest_dataset(manifest_path: str, label_col: str, split: str = None):
    """
    kkkim manifest 형식 지원:
    - split 컬럼으로 train/val/test 분리 (없으면 전체 반환)
    - 레이블: "Positive"→1, "Negative"→0, 나머지(Equivocal/Indeterminate 등) 제외
    """
    import csv
    is_pam50 = label_col.lower() == "pam50"
    label_lookup = PAM50_MAP if is_pam50 else LABEL_MAP
    dataset = []
    skipped = 0
    with open(manifest_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if split and row.get("split", "").lower() != split:
                continue
            emb_path = row.get("embedding_path", "")
            label_raw = row.get(label_col, "").strip().lower()
            if not emb_path or label_raw not in label_lookup:
                skipped += 1
                continue
            emb = torch.tensor(np.load(emb_path))
            label_val = label_lookup[label_raw]
            label = torch.tensor(label_val, dtype=torch.long if is_pam50 else torch.float32)
            dataset.append((emb, label))
    if skipped:
        print(f"  [skip] {skipped} rows (unknown label/missing)")
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

    num_classes = config.get("num_classes", 1)
    is_multiclass = num_classes > 1

    model = SlideMLP(
        input_dim=dim,
        hidden_dims=config["model"]["hidden_dims"],
        dropout=config["model"]["dropout"],
        num_classes=num_classes,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=config["train"]["lr"])
    criterion = nn.CrossEntropyLoss() if is_multiclass else nn.BCEWithLogitsLoss()

    from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

    best_val_loss = float("inf")
    for epoch in range(1, config["train"]["epochs"] + 1):
        model.train()
        train_loss = 0.0
        for emb, label in train_set:
            emb, label = emb.to(device), label.to(device)
            optimizer.zero_grad()
            logit = model(emb)
            loss = criterion(logit.unsqueeze(0) if is_multiclass else logit, label.unsqueeze(0))
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss, correct = 0.0, 0
        with torch.no_grad():
            for emb, label in val_set:
                emb, label = emb.to(device), label.to(device)
                logit = model(emb)
                val_loss += criterion(logit.unsqueeze(0) if is_multiclass else logit, label.unsqueeze(0)).item()
                pred = logit.argmax() if is_multiclass else (torch.sigmoid(logit) > 0.5).float()
                correct += (pred == label).sum().item()

        avg_val = val_loss / max(len(val_set), 1)
        acc = correct / max(len(val_set), 1)
        print(f"Epoch {epoch:02d} | train_loss={train_loss/len(train_set):.4f} | val_loss={avg_val:.4f} | val_acc={acc:.3f}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val

    # val set 전체 예측으로 최종 지표 계산
    model.eval()
    all_proba, all_pred, all_label = [], [], []
    with torch.no_grad():
        for emb, label in val_set:
            emb = emb.to(device)
            logit = model(emb)
            if is_multiclass:
                proba = torch.softmax(logit, dim=-1).cpu().numpy().tolist()
                pred = int(logit.argmax().item())
            else:
                proba = torch.sigmoid(logit).item()
                pred = int(proba > 0.5)
            all_proba.append(proba)
            all_pred.append(pred)
            all_label.append(int(label.item()))

    auc = auprc = bal_acc = None
    if len(set(all_label)) > 1:
        if is_multiclass:
            auc = round(float(roc_auc_score(all_label, np.array(all_proba), multi_class="ovr", average="macro")), 4)
            auprc = None
        else:
            auc   = round(float(roc_auc_score(all_label, all_proba)), 4)
            auprc = round(float(average_precision_score(all_label, all_proba)), 4)
        bal_acc = round(float(balanced_accuracy_score(all_label, all_pred)), 4)
        print(f"\nVal metrics — AUC={auc}  AUPRC={auprc}  BalAcc={bal_acc}")
    else:
        print("\n[warn] val set에 클래스가 1개뿐 — AUC/AUPRC 계산 불가")

    # 실험 디렉토리: experiments/<username>/<task>_<tag>/
    username = config.get("username", "sjpark")
    tag      = config.get("tag", datetime.datetime.now().strftime("%Y%m%d"))
    suffix   = f"{config['task']}_{tag}" + ("_smoke" if smoke_test else "")
    out_dir  = Path(config["output_dir"]) / username / suffix
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), out_dir / "model.pt")

    # predictions.npy 저장
    if is_multiclass:
        # multiclass: dict로 저장 (proba shape N×C, pred/label shape N)
        np.savez(
            out_dir / "predictions.npz",
            proba=np.array(all_proba, dtype=np.float32),
            pred=np.array(all_pred, dtype=np.int32),
            label=np.array(all_label, dtype=np.int32),
        )
    else:
        predictions = np.array(list(zip(all_proba, all_pred, all_label)), dtype=np.float32)
        np.save(out_dir / "predictions.npy", predictions)

    # config.yaml 복사
    if config.get("_config_path"):
        shutil.copy(config["_config_path"], out_dir / "config.yaml")

    commit_hash = config.get("_commit_hash") or get_git_commit_hash()
    metrics = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "task": config["task"],
        "model": "SlideMLP",
        "embedding_model": config["embedding_model"],
        "smoke_test": smoke_test,
        "n_train": len(train_set),
        "n_val": len(val_set),
        "best_val_loss": round(best_val_loss, 4),
        "auc": auc,
        "auprc": auprc,
        "balanced_accuracy": bal_acc,
        "commit_hash": commit_hash,
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "wandb_run_id": None,
        "mlflow_run_id": None,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved: {out_dir}/")
    print(f"  model.pt / metrics.json / predictions.npy" +
          (" / config.yaml" if config.get("_config_path") else ""))
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke_test", action="store_true")
    parser.add_argument("--tag", default="", help="실험 태그 (예: dummy_v1, uni_v1). 미지정 시 날짜 사용")
    parser.add_argument("--commit_hash", default="", help="git commit hash (서버 실행 시 로컬에서 명시적으로 전달)")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)
    config["_config_path"] = args.config
    if args.tag:
        config["tag"] = args.tag
    if args.commit_hash:
        config["_commit_hash"] = args.commit_hash

    t0 = time.time()
    metrics = train(config, args.smoke_test)
    print(f"\nDone in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

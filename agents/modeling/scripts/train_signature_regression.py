"""
BIOP02-58 — Immune/proliferation signature score 회귀 (dummy 언블록 버전).

research/work_breakdown_v02.md T7(Exp7) 근거:
  "frozen UNI+회귀head로 proliferation/immune/ESR1/ERBB2/Hallmark 예측;
   ssGSEA train-only; per-sig Spearman+BH-FDR"

⚠️ 실제 TCGA-BRCA RNA-seq/ssGSEA 발현 데이터가 프로젝트 어디에도 없어
   dummy 연속값 타깃으로 파이프라인만 먼저 완성 (kkkim extract_dummy.py와
   동일 패턴). jamie가 발현 데이터를 확보하면 --manifest만 실제 파일로
   교체해 재실행하면 됨. 코드 변경 불필요하도록 설계.

기존 SlideMLP(mlp.py)를 회귀 head로 재사용: num_classes=n_signatures,
activation 없이 raw output, MSELoss.
평가: per-signature Spearman r + BH-FDR 다중검정 보정 (T7 요구사항).

Run (smoke test, dummy manifest):
    python agents/modeling/scripts/train_signature_regression.py --smoke_test

Run (실제 발현 데이터 도착 후):
    python agents/modeling/scripts/train_signature_regression.py \
        --config agents/modeling/configs/baseline_signature_regression.yaml \
        --tag real_v1 --commit_hash $(git rev-parse HEAD)
"""

import argparse
import csv
import datetime
import json
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from scipy.stats import spearmanr

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.mlp import SlideMLP

SIGNATURE_NAMES = ["proliferation", "immune", "ESR1", "ERBB2", "Hallmark_EMT"]


def get_git_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def bh_fdr(p_values: list) -> list:
    """Benjamini-Hochberg FDR correction. numpy만 사용 (statsmodels 의존성 없음)."""
    p = np.array(p_values)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(n)
    adjusted[order] = np.clip(ranked, 0, 1)
    return adjusted.tolist()


def make_dummy_targets(n_slides: int, n_sig: int, seed: int):
    """실제 ssGSEA 발현 데이터 부재 — dummy 연속값 타깃 (표준정규분포)."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_slides, n_sig)).astype(np.float32)


def make_dummy_dataset(n_slides: int, dim: int, n_sig: int, seed: int):
    rng = np.random.default_rng(seed)
    dataset = []
    targets = make_dummy_targets(n_slides, n_sig, seed)
    for i in range(n_slides):
        n_tiles = rng.integers(100, 500)
        emb = torch.tensor(rng.standard_normal((n_tiles, dim)).astype(np.float32))
        target = torch.tensor(targets[i])
        dataset.append((emb, target))
    return dataset


def load_manifest_dataset(manifest_path: str, signature_cols: list, split: str, seed: int = 42):
    """
    실제 manifest 사용 시 signature_cols가 CSV에 있으면 그 값을 쓰고,
    없으면(=아직 발현 데이터 미연결) 슬라이드별 결정론적 dummy 값을 생성.
    manifest 자체 구조(embedding_path, split)는 그대로 재사용 가능하도록 설계.
    """
    dataset = []
    with open(manifest_path, newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("split", "").lower() == split]

    has_real_cols = rows and all(c in rows[0] for c in signature_cols)

    for i, row in enumerate(rows):
        emb_path = row.get("embedding_path", "")
        if not emb_path:
            continue
        emb = torch.tensor(np.load(emb_path))
        if has_real_cols:
            target = torch.tensor([float(row[c]) for c in signature_cols], dtype=torch.float32)
        else:
            rng = np.random.default_rng(seed + i)  # 슬라이드별 결정론적 dummy
            target = torch.tensor(rng.standard_normal(len(signature_cols)).astype(np.float32))
        dataset.append((emb, target))

    return dataset, has_real_cols


def train(config: dict, smoke_test: bool):
    torch.manual_seed(config["train"]["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    dim = config["embedding_dim"]
    n_sig = len(SIGNATURE_NAMES)
    manifest = config["data"]["embedding_manifest"]

    using_dummy_targets = True
    if smoke_test or not Path(manifest).exists():
        print("Smoke-test mode: dummy embeddings + dummy signature targets")
        dataset = make_dummy_dataset(config["data"]["n_dummy_slides"], dim, n_sig, config["train"]["seed"])
        n = len(dataset)
        split_idx = int(n * 0.8)
        train_set, val_set = dataset[:split_idx], dataset[split_idx:]
    else:
        print(f"Loading manifest: {manifest}")
        train_set, has_real_train = load_manifest_dataset(manifest, SIGNATURE_NAMES, "train", config["train"]["seed"])
        val_set, has_real_val = load_manifest_dataset(manifest, SIGNATURE_NAMES, "val", config["train"]["seed"] + 10000)
        using_dummy_targets = not (has_real_train and has_real_val)
        if using_dummy_targets:
            print("  [warn] manifest에 signature 컬럼 없음 — dummy 타깃 사용 중 (실제 발현데이터 도착 전)")

    print(f"Slides: train={len(train_set)} val={len(val_set)}  (dummy_targets={using_dummy_targets})")

    model = SlideMLP(
        input_dim=dim,
        hidden_dims=config["model"]["hidden_dims"],
        dropout=config["model"]["dropout"],
        num_classes=n_sig,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=config["train"]["lr"])
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    best_state = None
    patience = config["train"].get("patience", 5)
    no_improve = 0

    for epoch in range(1, config["train"]["epochs"] + 1):
        model.train()
        train_loss = 0.0
        for emb, target in train_set:
            emb, target = emb.to(device), target.to(device)
            optimizer.zero_grad()
            pred = model(emb)
            loss = criterion(pred, target)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for emb, target in val_set:
                emb, target = emb.to(device), target.to(device)
                pred = model(emb)
                val_loss += criterion(pred, target).item()

        avg_val = val_loss / max(len(val_set), 1)
        print(f"Epoch {epoch:02d} | train_loss={train_loss/len(train_set):.4f} | val_loss={avg_val:.4f}")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"  [early stop] patience={patience} 도달, epoch {epoch}에서 중단")
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    # per-signature Spearman + BH-FDR
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for emb, target in val_set:
            pred = model(emb.to(device)).cpu().numpy()
            all_preds.append(pred)
            all_targets.append(target.numpy())
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)

    per_sig = []
    p_values = []
    for i, name in enumerate(SIGNATURE_NAMES):
        r, p = spearmanr(all_preds[:, i], all_targets[:, i])
        per_sig.append({"signature": name, "spearman_r": round(float(r), 4), "p_value": round(float(p), 4)})
        p_values.append(float(p))

    adjusted = bh_fdr(p_values)
    for i, adj_p in enumerate(adjusted):
        per_sig[i]["p_value_bh_fdr"] = round(float(adj_p), 4)
        per_sig[i]["significant_fdr_0.05"] = bool(adj_p < 0.05)

    print("\nPer-signature Spearman (BH-FDR corrected):")
    for s in per_sig:
        print(f"  {s['signature']:15s} r={s['spearman_r']:+.4f}  p={s['p_value']:.4f}  "
              f"p_adj={s['p_value_bh_fdr']:.4f}  sig={s['significant_fdr_0.05']}")

    tag = config.get("tag", datetime.datetime.now().strftime("%Y%m%d"))
    suffix = f"immune_signature_{tag}" + ("_smoke" if smoke_test else "")
    out_dir = Path(config["output_dir"]) / config.get("username", "sjpark") / suffix
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), out_dir / "model.pt")
    np.savez(out_dir / "predictions.npz", pred=all_preds, target=all_targets)

    if config.get("_config_path"):
        shutil.copy(config["_config_path"], out_dir / "config.yaml")

    commit_hash = config.get("_commit_hash") or get_git_hash()
    metrics = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "task": "immune_signature_regression",
        "model": "SlideMLP-regression",
        "embedding_model": config["embedding_model"],
        "smoke_test": smoke_test,
        "using_dummy_targets": using_dummy_targets,
        "signature_names": SIGNATURE_NAMES,
        "n_train": len(train_set),
        "n_val": len(val_set),
        "best_val_loss": round(best_val_loss, 4),
        "per_signature": per_sig,
        "commit_hash": commit_hash,
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "wandb_run_id": None,
        "mlflow_run_id": None,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved: {out_dir}/")
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="")
    parser.add_argument("--smoke_test", action="store_true")
    parser.add_argument("--tag", default="")
    parser.add_argument("--commit_hash", default="")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
        config["_config_path"] = args.config
    else:
        # smoke test용 기본 config
        config = {
            "task": "immune_signature_regression",
            "username": "sjpark",
            "embedding_model": "dummy",
            "embedding_dim": 1024,
            "model": {"hidden_dims": [512, 256], "dropout": 0.3},
            "train": {"epochs": 10, "lr": 1.0e-3, "patience": 5, "seed": 42, "n_dummy_slides": 20},
            "data": {"embedding_manifest": "", "n_dummy_slides": 20},
            "output_dir": "/workspace/agents/modeling/experiments",
        }

    if args.tag:
        config["tag"] = args.tag
    if args.commit_hash:
        config["_commit_hash"] = args.commit_hash

    t0 = time.time()
    train(config, args.smoke_test)
    print(f"\nDone in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

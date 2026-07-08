"""
Counterfactual check for CLAM-MB (PAM50, multi-class) — Critic #3.

CLAM-SB용 counterfactual_attention.py의 multi-class 확장.
각 슬라이드의 예측 클래스에 해당하는 attention branch의 top 타일을 제거하고
예측(softmax proba)이 얼마나 흔들리는지 확인 (top-attention 제거 vs 무작위 제거).

Run:
    python agents/modeling/scripts/counterfactual_attention_mb.py \
        --model experiments/sjpark/pam50_clam_mb_uni_v1/model.pt \
        --config agents/modeling/configs/baseline_pam50_clam.yaml \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --split val --remove_frac 0.1 \
        --out_dir experiments/sjpark/pam50_clam_mb_uni_v1/counterfactual/
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch
import yaml
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.attention_mil import CLAMMB

PAM50_MAP = {"luma": 0, "lumb": 1, "basal": 2, "her2": 3, "normal": 4}


def load_manifest(manifest_path, split):
    rows = []
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("split", "").lower() != split:
                continue
            label_raw = row.get("pam50", "").strip().lower()
            if label_raw not in PAM50_MAP:
                continue
            rows.append(row)
    return rows


def predict(model, emb, device):
    x = torch.tensor(emb).to(device)
    model.eval()
    with torch.no_grad():
        logits, weights = model(x)  # (num_classes,), (num_classes, N)
    proba = torch.softmax(logits, dim=-1).cpu().numpy()
    return proba, weights.cpu().numpy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--split", default="val")
    parser.add_argument("--remove_frac", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)
    num_classes = config["num_classes"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLAMMB(
        feature_dim=config["embedding_dim"],
        hidden_dim=config["model"]["hidden_dim"],
        att_dim=config["model"]["att_dim"],
        dropout=config["model"]["dropout"],
        num_classes=num_classes,
    ).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))

    rows = load_manifest(args.manifest, args.split)
    print(f"슬라이드 {len(rows)}장 PAM50 counterfactual 검증 (remove_frac={args.remove_frac})")

    rng = np.random.default_rng(args.seed)

    proba_full_list, proba_top_removed_list, proba_random_removed_list, labels = [], [], [], []
    per_slide = []

    for row in rows:
        emb = np.load(row["embedding_path"])
        n_tiles = emb.shape[0]
        n_remove = max(1, int(n_tiles * args.remove_frac))
        label = PAM50_MAP[row["pam50"].strip().lower()]

        proba_full, weights = predict(model, emb, device)
        pred_class = int(np.argmax(proba_full))
        # 예측 클래스에 해당하는 attention branch 기준으로 top 타일 선정
        branch_weights = weights[pred_class]  # (N,)

        top_idx = np.argsort(branch_weights)[-n_remove:]
        keep_mask_top = np.ones(n_tiles, dtype=bool)
        keep_mask_top[top_idx] = False
        proba_top_removed, _ = predict(model, emb[keep_mask_top], device)

        remaining_idx = np.setdiff1d(np.arange(n_tiles), top_idx)
        random_idx = rng.choice(remaining_idx, size=min(n_remove, len(remaining_idx)), replace=False)
        keep_mask_random = np.ones(n_tiles, dtype=bool)
        keep_mask_random[random_idx] = False
        proba_random_removed, _ = predict(model, emb[keep_mask_random], device)

        proba_full_list.append(proba_full)
        proba_top_removed_list.append(proba_top_removed)
        proba_random_removed_list.append(proba_random_removed)
        labels.append(label)

        delta_top = float(np.abs(proba_top_removed - proba_full).mean())
        delta_random = float(np.abs(proba_random_removed - proba_full).mean())
        per_slide.append({
            "slide_id": row["slide_id"],
            "label": label,
            "pred_class": pred_class,
            "n_tiles": n_tiles,
            "n_removed": n_remove,
            "delta_top": round(delta_top, 4),
            "delta_random": round(delta_random, 4),
        })

    labels = np.array(labels)
    proba_full_arr = np.array(proba_full_list)
    proba_top_arr = np.array(proba_top_removed_list)
    proba_random_arr = np.array(proba_random_removed_list)

    def macro_auc(proba):
        try:
            return roc_auc_score(labels, proba, multi_class="ovr", average="macro")
        except ValueError:
            return None

    auc_full = macro_auc(proba_full_arr)
    auc_top_removed = macro_auc(proba_top_arr)
    auc_random_removed = macro_auc(proba_random_arr)

    mean_abs_delta_top = float(np.mean([s["delta_top"] for s in per_slide]))
    mean_abs_delta_random = float(np.mean([s["delta_random"] for s in per_slide]))

    summary = {
        "n_slides": len(rows),
        "remove_frac": args.remove_frac,
        "auc_full": round(auc_full, 4) if auc_full else None,
        "auc_top_removed": round(auc_top_removed, 4) if auc_top_removed else None,
        "auc_random_removed": round(auc_random_removed, 4) if auc_random_removed else None,
        "mean_abs_proba_delta_top": round(mean_abs_delta_top, 4),
        "mean_abs_proba_delta_random": round(mean_abs_delta_random, 4),
        "faithfulness_confirmed": mean_abs_delta_top > mean_abs_delta_random,
    }

    print(f"AUC full/top/random: {summary['auc_full']} / {summary['auc_top_removed']} / {summary['auc_random_removed']}")
    print(f"Mean |Δproba| top={summary['mean_abs_proba_delta_top']}  random={summary['mean_abs_proba_delta_random']}")
    print(f"Faithfulness confirmed: {summary['faithfulness_confirmed']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "counterfactual_summary.json").write_text(json.dumps(summary, indent=2))
    (out_dir / "counterfactual_per_slide.json").write_text(json.dumps(per_slide, indent=2))
    print(f"Saved: {out_dir}/counterfactual_summary.json")


if __name__ == "__main__":
    main()

"""
Counterfactual check (Critic #3) — CLAM-SB attention의 실제 기여도 검증.

핵심 질문: "attention이 높다고 표시한 타일을 실제로 제거하면 예측이 무너지는가?"
검증 방법: top-attention 타일 제거 vs 동일 개수 무작위 타일 제거를 비교.
  attention이 진짜 신호를 담고 있다면 top-attention 제거가 무작위 제거보다
  AUC를 더 크게 떨어뜨려야 함 (faithfulness check).

Run:
    python agents/modeling/scripts/counterfactual_attention.py \
        --model experiments/sjpark/er_status_clam_uni_v2/model.pt \
        --config agents/modeling/configs/baseline_er_status_clam.yaml \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --split val --remove_frac 0.1 \
        --out_dir experiments/sjpark/er_status_clam_uni_v2/counterfactual/
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch
import yaml
from sklearn.metrics import roc_auc_score

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.attention_mil import CLAMSB

LABEL_MAP = {"positive": 1.0, "negative": 0.0}


def load_manifest(manifest_path, label_col, split):
    rows = []
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("split", "").lower() != split:
                continue
            label_raw = row.get(label_col, "").strip().lower()
            if label_raw not in LABEL_MAP:
                continue
            rows.append(row)
    return rows


def predict(model, emb: np.ndarray, device: str):
    x = torch.tensor(emb).to(device)
    model.eval()
    with torch.no_grad():
        logit, weights = model(x)
    return torch.sigmoid(logit).item(), weights.squeeze(-1).cpu().numpy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--split", default="val")
    parser.add_argument("--remove_frac", type=float, default=0.1, help="제거할 타일 비율")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLAMSB(
        feature_dim=config["embedding_dim"],
        hidden_dim=config["model"]["hidden_dim"],
        att_dim=config["model"]["att_dim"],
        dropout=config["model"]["dropout"],
    ).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))

    rows = load_manifest(args.manifest, config["data"]["label_col"], args.split)
    print(f"슬라이드 {len(rows)}장 counterfactual 검증 (remove_frac={args.remove_frac})")

    rng = np.random.default_rng(args.seed)

    proba_full, proba_top_removed, proba_random_removed, labels = [], [], [], []
    per_slide = []

    for row in rows:
        emb = np.load(row["embedding_path"])
        n_tiles = emb.shape[0]
        n_remove = max(1, int(n_tiles * args.remove_frac))

        p_full, weights = predict(model, emb, device)

        # top-attention 타일 제거
        top_idx = np.argsort(weights)[-n_remove:]
        keep_mask_top = np.ones(n_tiles, dtype=bool)
        keep_mask_top[top_idx] = False
        p_top_removed, _ = predict(model, emb[keep_mask_top], device)

        # 동일 개수 무작위 타일 제거 (top 제거 인덱스는 제외하고 뽑음, 공정 비교)
        remaining_idx = np.setdiff1d(np.arange(n_tiles), top_idx)
        random_idx = rng.choice(remaining_idx, size=min(n_remove, len(remaining_idx)), replace=False)
        keep_mask_random = np.ones(n_tiles, dtype=bool)
        keep_mask_random[random_idx] = False
        p_random_removed, _ = predict(model, emb[keep_mask_random], device)

        label = LABEL_MAP[row[config["data"]["label_col"]].strip().lower()]

        proba_full.append(p_full)
        proba_top_removed.append(p_top_removed)
        proba_random_removed.append(p_random_removed)
        labels.append(label)

        per_slide.append({
            "slide_id": row["slide_id"],
            "label": label,
            "n_tiles": n_tiles,
            "n_removed": n_remove,
            "proba_full": round(p_full, 4),
            "proba_top_removed": round(p_top_removed, 4),
            "proba_random_removed": round(p_random_removed, 4),
            "delta_top": round(p_top_removed - p_full, 4),
            "delta_random": round(p_random_removed - p_full, 4),
        })

    labels = np.array(labels)
    auc_full = roc_auc_score(labels, proba_full)
    auc_top_removed = roc_auc_score(labels, proba_top_removed)
    auc_random_removed = roc_auc_score(labels, proba_random_removed)

    mean_abs_delta_top = float(np.mean([abs(s["delta_top"]) for s in per_slide]))
    mean_abs_delta_random = float(np.mean([abs(s["delta_random"]) for s in per_slide]))

    summary = {
        "n_slides": len(rows),
        "remove_frac": args.remove_frac,
        "auc_full": round(float(auc_full), 4),
        "auc_top_removed": round(float(auc_top_removed), 4),
        "auc_random_removed": round(float(auc_random_removed), 4),
        "auc_drop_top": round(float(auc_full - auc_top_removed), 4),
        "auc_drop_random": round(float(auc_full - auc_random_removed), 4),
        "mean_abs_proba_delta_top": round(mean_abs_delta_top, 4),
        "mean_abs_proba_delta_random": round(mean_abs_delta_random, 4),
        "faithfulness_confirmed": (auc_full - auc_top_removed) > (auc_full - auc_random_removed),
    }

    print(f"\nAUC full              : {summary['auc_full']}")
    print(f"AUC top-removed       : {summary['auc_top_removed']}  (drop={summary['auc_drop_top']})")
    print(f"AUC random-removed    : {summary['auc_random_removed']}  (drop={summary['auc_drop_random']})")
    print(f"Mean |Δproba| top     : {summary['mean_abs_proba_delta_top']}")
    print(f"Mean |Δproba| random  : {summary['mean_abs_proba_delta_random']}")
    print(f"Faithfulness confirmed: {summary['faithfulness_confirmed']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "counterfactual_summary.json").write_text(json.dumps(summary, indent=2))
    (out_dir / "counterfactual_per_slide.json").write_text(json.dumps(per_slide, indent=2))
    print(f"\nSaved: {out_dir}/counterfactual_summary.json")


if __name__ == "__main__":
    main()

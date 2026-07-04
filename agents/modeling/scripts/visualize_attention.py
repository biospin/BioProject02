"""
CLAM-SB Attention map 시각화 — Critic #3 counterfactual 지원

각 슬라이드의 타일별 attention weight를 추출하고
상위/하위 타일 좌표를 coords.npy 기준으로 저장합니다.

Run:
    python agents/modeling/scripts/visualize_attention.py \
        --model experiments/sjpark/er_status_clam_uni_v2/model.pt \
        --config agents/modeling/configs/baseline_er_status_clam.yaml \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --split val \
        --out_dir /workspace/agents/modeling/experiments/sjpark/er_status_clam_uni_v2/attention/
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.attention_mil import CLAMSB

LABEL_MAP = {"positive": 1.0, "negative": 0.0}


def load_manifest(manifest_path, label_col, split, n_slides=10):
    rows = []
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("split", "").lower() != split:
                continue
            label_raw = row.get(label_col, "").strip().lower()
            if label_raw not in LABEL_MAP:
                continue
            rows.append(row)
            if len(rows) >= n_slides:
                break
    return rows


def extract_attention(model, emb: np.ndarray, device: str):
    x = torch.tensor(emb).to(device)
    model.eval()
    with torch.no_grad():
        logit, weights = model(x)
    proba = torch.sigmoid(logit).item()
    return proba, weights.squeeze(-1).cpu().numpy()  # (N,)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--split", default="val")
    parser.add_argument("--n_slides", type=int, default=10)
    parser.add_argument("--top_k", type=int, default=20, help="상위/하위 attention 타일 수")
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

    rows = load_manifest(args.manifest, config["data"]["label_col"], args.split, args.n_slides)
    print(f"슬라이드 {len(rows)}장 분석")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for row in rows:
        emb = np.load(row["embedding_path"])
        proba, weights = extract_attention(model, emb, device)

        top_idx    = np.argsort(weights)[-args.top_k:][::-1].tolist()
        bottom_idx = np.argsort(weights)[:args.top_k].tolist()

        result = {
            "slide_id": row["slide_id"],
            "true_label": row[config["data"]["label_col"]],
            "pred_prob": round(proba, 4),
            "pred_label": "Positive" if proba > 0.5 else "Negative",
            "n_tiles": len(weights),
            "top_attention_tiles": top_idx,
            "bottom_attention_tiles": bottom_idx,
            "attention_stats": {
                "max": round(float(weights.max()), 6),
                "min": round(float(weights.min()), 6),
                "mean": round(float(weights.mean()), 6),
                "std": round(float(weights.std()), 6),
            },
        }
        results.append(result)

        np.save(out_dir / f"{row['slide_id']}_attention.npy", weights)
        print(f"  {row['slide_id']}: prob={proba:.3f} label={row[config['data']['label_col']]} "
              f"top_weight={weights.max():.4f}")

    (out_dir / "attention_summary.json").write_text(
        __import__("json").dumps(results, indent=2)
    )
    print(f"\n저장 완료: {out_dir}/attention_summary.json")


if __name__ == "__main__":
    main()

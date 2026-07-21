"""
A3 (BIOP02-80 Yale 앵커) — frozen phenotype 모델을 Yale 임베딩에 적용해 축 점수 산출.

TCGA로 학습한 HER2 CLAM-SB 모델을 Yale 코호트에 **frozen transfer**(미세조정 금지)로 적용,
슬라이드별 항HER2 축 점수(= HER2 양성 확률)를 산출한다. A4(pCR 층화)의 입력.

Run:
    python agents/modeling/scripts/apply_frozen_axis_yale.py \
        --model experiments/sjpark/her2_status_clam_uni_v2/model.pt \
        --config agents/modeling/configs/baseline_her2_status_clam.yaml \
        --manifest /workspace/data/cache/biop02/yale/embedding_manifest_yale_uni.csv \
        --out experiments/sjpark/yale_antiher2_axis_scores.csv
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import torch
import yaml
import sys
sys.path.insert(0, "/workspace/agents")
from modeling.baselines.attention_mil import CLAMSB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLAMSB(
        feature_dim=cfg["embedding_dim"],
        hidden_dim=cfg["model"]["hidden_dim"],
        att_dim=cfg["model"]["att_dim"],
        dropout=cfg["model"]["dropout"],
    ).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))
    model.eval()  # frozen — Yale 미세조정 없음

    rows = [r for r in csv.DictReader(open(args.manifest)) if r.get("status", "done") == "done"]
    print(f"Yale 슬라이드: {len(rows)}장에 frozen HER2 축 적용")

    out_rows = []
    with torch.no_grad():
        for r in rows:
            emb = np.load(r["embedding_path"])
            x = torch.tensor(emb).to(device)
            logit, _ = model(x)
            score = float(torch.sigmoid(logit).item())
            out_rows.append({
                "slide_id": r["slide_id"],
                "case_id": r["case_id"],
                "n_tiles": r.get("n_tiles", ""),
                "antiher2_axis_score": round(score, 6),
            })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slide_id", "case_id", "n_tiles", "antiher2_axis_score"])
        w.writeheader()
        w.writerows(out_rows)

    s = np.array([o["antiher2_axis_score"] for o in out_rows])
    print(f"Saved: {out} ({len(out_rows)} rows)")
    print(f"축 점수 분포: min={s.min():.3f} median={np.median(s):.3f} max={s.max():.3f} mean={s.mean():.3f}")
    print("주의: frozen transfer (Yale fine-tune 없음). 모델 출처 = TCGA her2_status_clam_uni_v2.")


if __name__ == "__main__":
    main()

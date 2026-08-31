"""BIOP02-90 (kkkim 병목) — ER predictions_ext에 slide_id/case_id 인덱스 붙여 재생성.
kkkim PAM50 라우팅 CI를 환자단위(case_id 그룹)로 계산할 수 있도록 slide_id·case_id·확률·라벨 CSV."""
import csv
from pathlib import Path
import numpy as np
import torch, yaml
import sys
sys.path.insert(0, "/workspace/agents")
from modeling.baselines.attention_mil import CLAMSB

CFG = "/workspace/agents/modeling/configs/baseline_er_status_clam.yaml"
MODEL = "/workspace/agents/modeling/experiments/sjpark/er_status_clam_uni_v2/model.pt"
MANI = "/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"
OUT = "/workspace/agents/modeling/experiments/sjpark/er_status_clam_uni_v2/predictions_ext_indexed.csv"
LABEL_MAP = {"positive": 1, "negative": 0}

cfg = yaml.safe_load(open(CFG))
device = "cuda" if torch.cuda.is_available() else "cpu"
m = CLAMSB(feature_dim=cfg["embedding_dim"], hidden_dim=cfg["model"]["hidden_dim"],
           att_dim=cfg["model"]["att_dim"], dropout=cfg["model"]["dropout"]).to(device)
m.load_state_dict(torch.load(MODEL, map_location=device)); m.eval()

rows = [r for r in csv.DictReader(open(MANI))
        if r.get("split", "").strip() == "cptac_external" and r.get("er", "").strip().lower() in LABEL_MAP]
print(f"ER eval 대상(has_er): {len(rows)}장")

out = []
with torch.no_grad():
    for r in rows:
        x = torch.tensor(np.load(r["embedding_path"])).to(device)
        logit, _ = m(x)
        p = float(torch.sigmoid(logit).item())
        lab = LABEL_MAP[r["er"].strip().lower()]
        out.append({"slide_id": r["slide_id"], "case_id": r["case_id"],
                    "er_pred_prob": round(p, 6), "er_pred": int(p > 0.5), "er_true_label": lab})

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["slide_id", "case_id", "er_pred_prob", "er_pred", "er_true_label"])
    w.writeheader(); w.writerows(out)

# 검증: 기존 predictions_ext.npy(387,3)와 확률·라벨 정합
old = np.load("/workspace/agents/modeling/experiments/sjpark/er_status_clam_uni_v2/predictions_ext.npy")
new_p = np.array([o["er_pred_prob"] for o in out])
new_l = np.array([o["er_true_label"] for o in out])
match_p = np.allclose(np.sort(old[:, 0]), np.sort(new_p), atol=1e-4)
n_case = len(set(o["case_id"] for o in out))
print(f"Saved {OUT} ({len(out)} slides, {n_case} unique case_id)")
print(f"기존 predictions_ext.npy와 확률분포 정합: {match_p} | 라벨 합 old={int(old[:,2].sum())} new={int(new_l.sum())}")

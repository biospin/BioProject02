"""BIOP02-39 — ER status MLP ROC curve (kkkim 요청). MLP vs mean_embed baseline, TCGA-BRCA val, UNI v1."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.linear_model import LogisticRegression

BASE = Path("/workspace/agents/modeling/experiments/sjpark/er_status_uni_v1")
MANI = "/workspace/data/cache/biop02/embedding_manifest_uni.csv"
LABEL_MAP = {"positive": 1.0, "negative": 0.0}

# --- MLP 예측 (proba, pred, label) ---
mlp = np.load(BASE / "predictions.npy")
mlp_proba, mlp_label = mlp[:, 0], mlp[:, 2].astype(int)

# --- mean_embed baseline 재계산 (동일 val split) ---
def load(split):
    X, y = [], []
    for r in csv.DictReader(open(MANI)):
        if r.get("split", "").lower() != split:
            continue
        lab = r.get("er", "").strip().lower()
        if lab not in LABEL_MAP:
            continue
        X.append(np.load(r["embedding_path"]).mean(0))
        y.append(LABEL_MAP[lab])
    return np.array(X), np.array(y)

Xtr, ytr = load("train"); Xva, yva = load("val")
clf = LogisticRegression(max_iter=1000, random_state=42).fit(Xtr, ytr)
me_proba = clf.predict_proba(Xva)[:, 1]

assert np.array_equal(yva.astype(int), mlp_label), "val 라벨 순서 불일치"

def boot_ci(y, p, n=2000, seed=42):
    rng = np.random.default_rng(seed); a = []
    for _ in range(n):
        idx = rng.choice(len(y), len(y), replace=True)
        if len(np.unique(y[idx])) < 2:
            continue
        a.append(roc_auc_score(y[idx], p[idx]))
    return np.percentile(a, 2.5), np.percentile(a, 97.5)

auc_mlp = roc_auc_score(mlp_label, mlp_proba)
auc_me = roc_auc_score(mlp_label, me_proba)
lo, hi = boot_ci(mlp_label, mlp_proba)
lo2, hi2 = boot_ci(mlp_label, me_proba)

fpr_m, tpr_m, _ = roc_curve(mlp_label, mlp_proba)
fpr_e, tpr_e, _ = roc_curve(mlp_label, me_proba)

plt.figure(figsize=(6.2, 6))
plt.plot(fpr_m, tpr_m, color="#B0466A", lw=2.4,
         label=f"SlideMLP (UNI)   AUC {auc_mlp:.3f}  [{lo:.3f}, {hi:.3f}]")
plt.plot(fpr_e, tpr_e, color="#4A3F86", lw=2.0, ls="--",
         label=f"mean_embed (LR)  AUC {auc_me:.3f}  [{lo2:.3f}, {hi2:.3f}]")
plt.plot([0, 1], [0, 1], color="gray", lw=1, ls=":", label="chance (AUC 0.500)")
plt.xlabel("False Positive Rate", fontsize=11)
plt.ylabel("True Positive Rate", fontsize=11)
plt.title("ER status prediction — ROC (TCGA-BRCA val, UNI v1)\n"
          f"site-disjoint split, n_val={len(mlp_label)} (ER+ {int(mlp_label.sum())} / ER- {int((1-mlp_label).sum())})",
          fontsize=11)
plt.legend(loc="lower right", fontsize=9.5, frameon=True)
plt.grid(alpha=0.25)
plt.xlim(-0.01, 1.01); plt.ylim(-0.01, 1.01)
plt.tight_layout()
out = BASE / "roc_er_status_uni_v1.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved: {out}")
print(f"MLP AUC={auc_mlp:.4f} [{lo:.4f},{hi:.4f}] | mean_embed AUC={auc_me:.4f} [{lo2:.4f},{hi2:.4f}]")

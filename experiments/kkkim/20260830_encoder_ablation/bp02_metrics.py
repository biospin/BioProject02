"""ablation 결과에 AUPRC와 balanced accuracy를 추가하고 리포 규약의 metrics.json을 쓴다."""
import json, os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             balanced_accuracy_score)
from sklearn.preprocessing import StandardScaler

from bp02_encoder_ablation import ENCODERS, load_labels
from bp02_bootstrap import load_cached

TASKS = [("er", False), ("pr", False), ("her2", False), ("pam50_subtype", True)]
CACHE = os.path.expanduser("~/work/fmpretrain/cache_bp02")
CLIN = os.path.expanduser("~/data/clinical")
SPLIT = os.path.expanduser("~/data/split_policy_v1.csv")

split = pd.read_csv(SPLIT).set_index("case_id")["split"]
labels = load_labels(CLIN)
rows = []

for enc in ENCODERS:
    cases, Z = load_cached(CACHE, enc)
    idx = pd.Index(cases)
    for tgt, multi in TASKS:
        y = labels.reindex(idx)[tgt]
        sp_ = split.reindex(idx)
        ok = y.notna().to_numpy() & sp_.notna().to_numpy()
        if multi:
            vc = y[ok].value_counts()
            ok &= y.isin(vc[vc >= 20].index).to_numpy()
        tr = ok & (sp_ == "train").to_numpy()
        te = ok & (sp_ == "test").to_numpy()
        yv = y.to_numpy()
        ytr = yv[tr].astype(str) if multi else yv[tr].astype(int)
        yte = yv[te].astype(str) if multi else yv[te].astype(int)

        sc = StandardScaler().fit(Z[tr])
        clf = LogisticRegression(max_iter=5000, class_weight="balanced")
        clf.fit(sc.transform(Z[tr]), ytr)
        P = clf.predict_proba(sc.transform(Z[te]))
        pred = clf.predict(sc.transform(Z[te]))

        if multi:
            auc = roc_auc_score(yte, P, multi_class="ovr", average="macro")
            Yb = np.stack([(yte == c).astype(int) for c in clf.classes_], 1)
            auprc = average_precision_score(Yb, P, average="macro")
        else:
            auc = roc_auc_score(yte, P[:, 1])
            auprc = average_precision_score(yte, P[:, 1])
        rows.append({
            "embedding_model": enc, "task": tgt,
            "auc": round(float(auc), 4), "auprc": round(float(auprc), 4),
            "balanced_accuracy": round(float(balanced_accuracy_score(yte, pred)), 4),
            "n_train": int(tr.sum()), "n_val": int(te.sum()),
            "positives_test": (None if multi else int((yte == 1).sum())),
        })
        print(f"{enc:20s} {tgt:14s} auc={auc:.4f} auprc={auprc:.4f} "
              f"bacc={rows[-1]['balanced_accuracy']:.4f}", flush=True)

out = os.path.expanduser("~/work/fmpretrain/bp02_metrics_full.json")
json.dump(rows, open(out, "w"), indent=2)

# 리포 규약의 metrics.json — 대표 구성(ER, 염색 정규화 UNI) 기준
head = next(r for r in rows if r["embedding_model"] == "uni_stainnorm_v1"
            and r["task"] == "er")
metrics = {
    "schema_version": "0.1",
    "task": "er_status",
    "model": "LogisticRegression(class_weight=balanced) on mean-pooled embeddings",
    "embedding_model": "uni_stainnorm_v1",
    "smoke_test": False,
    "claim_level": "hypothesis_only",
    "n_train": head["n_train"], "n_val": head["n_val"],
    "auc": head["auc"], "auprc": head["auprc"],
    "balanced_accuracy": head["balanced_accuracy"],
    "best_val_loss": None,
    "commit_hash": None,
    "split_hash": "split_policy_v1.csv",
    "note": "인코더 4종 × 표현형 4종 ablation의 대표 구성. 전체는 bp02_metrics_full.json",
    "all_configs": rows,
}
json.dump(metrics, open(os.path.expanduser("~/work/fmpretrain/metrics.json"), "w"),
          indent=2)
print("[done] metrics.json + bp02_metrics_full.json")

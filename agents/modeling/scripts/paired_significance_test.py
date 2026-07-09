"""
CLAM vs subtype_only baseline paired bootstrap 유의성 검정.

두 모델이 같은 val set에서 예측하므로, CI가 겹치는지 눈으로 보는 것이 아니라
같은 리샘플 인덱스로 AUC 차이(CLAM - baseline)의 분포를 직접 구해 검정한다.
차이의 95% CI가 0을 포함하지 않으면 유의미한 차이로 판단.

Run:
    python agents/modeling/scripts/paired_significance_test.py \
        --clam_predictions experiments/sjpark/er_status_clam_uni_v2/predictions.npy \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --label_col er --aux_col pam50 \
        --out experiments/sjpark/er_status_clam_uni_v2/paired_significance.json
"""

import argparse
import csv
import json
from collections import defaultdict

import numpy as np
from sklearn.metrics import roc_auc_score

LABEL_MAP = {"positive": 1.0, "negative": 0.0}


def load_split(manifest_path, label_col, aux_col, split):
    labels, aux = [], []
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("split", "").lower() != split:
                continue
            label_raw = row.get(label_col, "").strip().lower()
            if label_raw not in LABEL_MAP:
                continue
            labels.append(LABEL_MAP[label_raw])
            aux.append(row.get(aux_col, "").strip())
    return np.array(labels, dtype=np.float32), aux


def fit_subtype_only(train_labels, train_aux):
    groups = defaultdict(list)
    for s, l in zip(train_aux, train_labels):
        groups[s].append(l)
    probs = {s: float(np.mean(ls)) for s, ls in groups.items()}
    default = float(train_labels.mean())
    return probs, default


def predict_subtype_only(aux_list, probs, default):
    return np.array([probs.get(s, default) for s in aux_list], dtype=np.float32)


def paired_bootstrap_diff(y_true, proba_a, proba_b, n_bootstrap=2000, seed=42):
    """AUC(a) - AUC(b) 의 bootstrap 분포. 같은 리샘플 인덱스로 둘 다 평가 (paired)."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    diffs = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        yt = y_true[idx]
        if len(np.unique(yt)) < 2:
            continue
        auc_a = roc_auc_score(yt, proba_a[idx])
        auc_b = roc_auc_score(yt, proba_b[idx])
        diffs.append(auc_a - auc_b)
    diffs = np.array(diffs)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    p_value_approx = 2 * min((diffs > 0).mean(), (diffs < 0).mean())
    return round(float(lo), 4), round(float(hi), 4), round(float(diffs.mean()), 4), round(float(p_value_approx), 4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clam_predictions", required=True, help="predictions.npy (proba,pred,label)")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--label_col", required=True)
    parser.add_argument("--aux_col", default="pam50")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    clam_preds = np.load(args.clam_predictions)
    clam_proba, clam_label = clam_preds[:, 0], clam_preds[:, 2]

    train_labels, train_aux = load_split(args.manifest, args.label_col, args.aux_col, "train")
    val_labels, val_aux = load_split(args.manifest, args.label_col, args.aux_col, "val")

    assert len(val_labels) == len(clam_label), (
        f"슬라이드 수 불일치: manifest val={len(val_labels)} vs predictions.npy={len(clam_label)}"
    )
    assert np.allclose(val_labels, clam_label), "label 순서 불일치 — manifest와 predictions.npy 정렬 확인 필요"

    probs, default = fit_subtype_only(train_labels, train_aux)
    subtype_proba = predict_subtype_only(val_aux, probs, default)

    auc_clam = roc_auc_score(val_labels, clam_proba)
    auc_subtype = roc_auc_score(val_labels, subtype_proba)

    lo, hi, mean_diff, p_approx = paired_bootstrap_diff(val_labels, clam_proba, subtype_proba)
    significant = not (lo <= 0 <= hi)

    result = {
        "n": len(val_labels),
        "auc_clam": round(float(auc_clam), 4),
        "auc_subtype_only": round(float(auc_subtype), 4),
        "diff_clam_minus_subtype": mean_diff,
        "diff_ci_95": [lo, hi],
        "p_value_approx": p_approx,
        "significant_at_0.05": significant,
        "interpretation": (
            "CLAM이 subtype_only보다 유의하게 우수함" if significant and mean_diff > 0 else
            "subtype_only가 CLAM보다 유의하게 우수함" if significant and mean_diff < 0 else
            "두 모델 간 유의한 차이 없음 (CI가 0을 포함)"
        ),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()

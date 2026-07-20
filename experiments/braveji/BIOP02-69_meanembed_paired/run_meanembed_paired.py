"""
BIOP02-69 / BIOP02-50 잔여 — CLAM vs mean_embed paired 유의성 (braveji Critic 독립 산출).

배경: run_baselines.py는 mean_embed proba를 계산하지만 **요약(trivial_baselines.json)만 저장**하고
per-patient proba를 남기지 않는다. 그래서 Critic #2의 "CLAM이 mean_embed를 유의하게 이기는가"를
paired bootstrap으로 검정할 수 없었다(BIOP02-50 recompute의 미해결 잔여).
이 스크립트는 /workspace 임베딩에서 mean_embed proba를 재생성해 그 공백을 메운다.

정의 재사용(재발명 금지): baseline은 sjpark 소유 `modeling.baselines.trivial.MeanEmbedBaseline`,
paired bootstrap은 `paired_significance_test.py`와 동일 방식(같은 리샘플 인덱스로 둘 다 평가).

무결성 가드: manifest에서 만든 y와 predictions.npy의 label 컬럼이 **정확히 일치**해야 진행한다
(불일치 = 정렬 붕괴 → 즉시 실패, 조용한 오답 방지).

Run (GPU 머신, /workspace 마운트 필요):
    python experiments/braveji/BIOP02-69_meanembed_paired/run_meanembed_paired.py \
        --task er --label_col er \
        --clam_predictions experiments/sjpark/er_status_clam_uni_v2/predictions.npy \
        --out_dir experiments/braveji/BIOP02-69_meanembed_paired/
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "agents"))
from modeling.baselines.trivial import MeanEmbedBaseline  # noqa: E402

LABEL_MAP = {"positive": 1.0, "negative": 0.0}
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_uni.csv"


def load_split(manifest, label_col, split):
    rows = []
    with open(manifest, newline="") as f:
        for r in csv.DictReader(f):
            if r.get("split", "").strip().lower() != split:
                continue
            lab = r.get(label_col, "").strip().lower()
            if lab not in LABEL_MAP:
                continue
            rows.append(r)
    return rows


def load_xy(rows, label_col):
    X = [np.load(r["embedding_path"]) for r in rows]
    y = np.array([LABEL_MAP[r[label_col].strip().lower()] for r in rows], dtype=float)
    return X, y


def paired_bootstrap_diff(y, pa, pb, n_bootstrap=2000, seed=42):
    """AUC(a)-AUC(b) bootstrap 분포. 동일 리샘플 인덱스로 둘 다 평가(paired)."""
    rng = np.random.default_rng(seed)
    diffs = []
    n = len(y)
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        yt = y[idx]
        if len(np.unique(yt)) < 2:
            continue
        diffs.append(roc_auc_score(yt, pa[idx]) - roc_auc_score(yt, pb[idx]))
    d = np.array(diffs)
    lo, hi = np.percentile(d, [2.5, 97.5])
    p = 2 * min((d <= 0).mean(), (d >= 0).mean())
    return float(lo), float(hi), float(d.mean()), float(min(p, 1.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--label_col", required=True)
    ap.add_argument("--clam_predictions", required=True)
    ap.add_argument("--manifest", default=MANIFEST, help="train fit용 manifest (TCGA)")
    ap.add_argument("--split", default="val")
    ap.add_argument("--test_manifest", default="", help="평가 manifest (외부검증 시 CPTAC). 미지정 시 --manifest")
    ap.add_argument("--test_label_col", default="", help="평가 manifest 라벨 컬럼 오버라이드")
    ap.add_argument("--n_bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    test_manifest = args.test_manifest or args.manifest
    test_label_col = args.test_label_col or args.label_col

    train_rows = load_split(args.manifest, args.label_col, "train")
    val_rows = load_split(test_manifest, test_label_col, args.split)
    print(f"[{args.task}] train={len(train_rows)} (fit: {Path(args.manifest).name})  "
          f"{args.split}={len(val_rows)} (eval: {Path(test_manifest).name})")

    Xtr, ytr = load_xy(train_rows, args.label_col)
    Xva, yva = load_xy(val_rows, test_label_col)

    clam = np.load(args.clam_predictions)
    clam_proba, clam_label = clam[:, 0], clam[:, 2]

    # 무결성 가드 — 정렬/표본 일치 확인
    if len(clam_label) != len(yva):
        raise SystemExit(f"[FAIL] n mismatch: clam={len(clam_label)} vs manifest {args.split}={len(yva)}")
    if not np.array_equal(clam_label.astype(float), yva):
        raise SystemExit("[FAIL] label 정렬 불일치 — predictions.npy 순서가 manifest val 순서와 다름")
    print("  정렬 가드 통과: clam label == manifest label")

    mb = MeanEmbedBaseline(seed=args.seed)
    mb.fit(Xtr, ytr)
    me_proba = mb.predict_proba(Xva)

    auc_clam = float(roc_auc_score(yva, clam_proba))
    auc_me = float(roc_auc_score(yva, me_proba))
    lo, hi, mean_diff, p = paired_bootstrap_diff(yva, clam_proba, me_proba,
                                                 args.n_bootstrap, args.seed)
    sig = (lo > 0) or (hi < 0)
    out = {
        "task": args.task,
        "split": args.split,
        "n": int(len(yva)),
        "n_pos": int(yva.sum()),
        "auc_clam": round(auc_clam, 4),
        "auc_mean_embed": round(auc_me, 4),
        "diff_clam_minus_mean_embed": round(mean_diff, 4),
        "diff_ci_95": [round(lo, 4), round(hi, 4)],
        "p_value_approx": round(p, 4),
        "significant_at_0.05": bool(sig),
        "n_bootstrap": args.n_bootstrap,
        "seed": args.seed,
        "baseline_def": "modeling.baselines.trivial.MeanEmbedBaseline (sjpark 소유 정의 재사용)",
        "note": "run_baselines.py가 proba를 저장하지 않아 공백이던 Critic #2 paired 검정을 braveji가 /workspace 임베딩에서 독립 산출",
    }
    print(json.dumps({k: out[k] for k in
                      ["auc_clam", "auc_mean_embed", "diff_clam_minus_mean_embed",
                       "diff_ci_95", "p_value_approx", "significant_at_0.05"]}, indent=2))

    od = Path(args.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    (od / f"paired_meanembed_{args.task}_{args.split}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))
    print(f"Saved: {od}/paired_meanembed_{args.task}_{args.split}.json")


if __name__ == "__main__":
    main()

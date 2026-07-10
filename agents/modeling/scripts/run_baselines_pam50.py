"""
PAM50 (5-class) trivial baselines — Critic #2 완결용.

random / majority / mean_embed multiclass baselines
CLAM-MB(BIOP02-53)의 AUC 0.7589와 비교하기 위함.

Run:
    python agents/modeling/scripts/run_baselines_pam50.py \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --tag clam_mb_uni_v1 --bootstrap_ci \
        --commit_hash $(git rev-parse HEAD)
"""

import argparse
import csv
import datetime
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.trivial import (
    MulticlassRandomBaseline,
    MulticlassMajorityBaseline,
    MulticlassMeanEmbedBaseline,
    evaluate_multiclass,
)

PAM50_MAP_5 = {"luma": 0, "lumb": 1, "basal": 2, "her2": 3, "normal": 4, "normal-like": 4}
PAM50_MAP_4 = {"luma": 0, "lumb": 1, "basal": 2, "her2": 3}  # §4 준수: Normal 제외


def pam50_map(num_classes):
    return PAM50_MAP_4 if num_classes == 4 else PAM50_MAP_5


def load_manifest(manifest_path: str, split: str, num_classes: int = 5):
    PAM50_MAP = pam50_map(num_classes)
    X, y = [], []
    skipped = 0
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("split", "").lower() != split:
                continue
            emb_path = row.get("embedding_path", "")
            label_raw = row.get("pam50", "").strip().lower()
            if not emb_path or label_raw not in PAM50_MAP:
                skipped += 1
                continue
            X.append(np.load(emb_path))
            y.append(PAM50_MAP[label_raw])
    if skipped:
        print(f"  [skip] {skipped} rows (unknown label/missing)")
    return X, np.array(y, dtype=np.int64)


def get_git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--tag", default="")
    parser.add_argument("--commit_hash", default="")
    parser.add_argument("--bootstrap_ci", action="store_true")
    parser.add_argument("--username", default="sjpark")
    parser.add_argument("--output_dir", default="/workspace/agents/modeling/experiments")
    parser.add_argument("--ext_manifest", default="", help="CPTAC 등 외부 test manifest — 지정 시 동일 fit된 baseline을 외부셋에도 평가 (CLAM-MB 외부검증과 동일 조건 비교용)")
    parser.add_argument("--ext_split", default="cptac_external")
    parser.add_argument("--num_classes", type=int, default=5, help="5=Normal 포함(기존), 4=§4 준수 Normal 제외")
    args = parser.parse_args()

    num_classes = args.num_classes
    X_train, y_train = load_manifest(args.manifest, split="train", num_classes=num_classes)
    X_val, y_val = load_manifest(args.manifest, split="val", num_classes=num_classes)
    print(f"Slides: train={len(X_train)} val={len(X_val)}  (num_classes={num_classes})\n")
    baselines = [
        ("random", MulticlassRandomBaseline(num_classes=num_classes)),
        ("majority", MulticlassMajorityBaseline(num_classes=num_classes)),
        ("mean_embed", MulticlassMeanEmbedBaseline(num_classes=num_classes)),
    ]

    results = []
    for name, clf in baselines:
        clf.fit(X_train, y_train)
        proba = clf.predict_proba(X_val)
        m = evaluate_multiclass(name, proba, y_val, num_classes, add_ci=args.bootstrap_ci)
        results.append(m)
        ci_str = f"  CI95={m['auc_ci_95']}" if args.bootstrap_ci and "auc_ci_95" in m else ""
        print(f"[{name:12s}]  AUC={m['auc']}  AUPRC={m['auprc']}  BalAcc={m['balanced_accuracy']}{ci_str}")

    ext_results = None
    ext_n_test = None
    if args.ext_manifest and Path(args.ext_manifest).exists():
        X_ext, y_ext = load_manifest(args.ext_manifest, split=args.ext_split, num_classes=num_classes)
        ext_n_test = len(X_ext)
        print(f"\n외부(CPTAC) 평가: n_test={ext_n_test} (split={args.ext_split})")
        if ext_n_test == 0:
            print(f"[warn] 0장 — ext_split({args.ext_split}) 확인 필요")
        else:
            ext_results = []
            for name, clf in baselines:
                proba_ext = clf.predict_proba(X_ext)
                m_ext = evaluate_multiclass(name, proba_ext, y_ext, num_classes, add_ci=args.bootstrap_ci)
                ext_results.append(m_ext)
                ci_str = f"  CI95={m_ext['auc_ci_95']}" if args.bootstrap_ci and "auc_ci_95" in m_ext else ""
                print(f"[ext:{name:8s}]  AUC={m_ext['auc']}  AUPRC={m_ext['auprc']}  BalAcc={m_ext['balanced_accuracy']}{ci_str}")

    tag = args.tag if args.tag else datetime.datetime.now().strftime("%Y%m%d")
    out_dir = Path(args.output_dir) / args.username / f"pam50_{tag}_baselines"
    out_dir.mkdir(parents=True, exist_ok=True)

    output = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "task": "pam50",
        "num_classes": num_classes,
        "manifest": args.manifest,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "commit_hash": args.commit_hash or get_git_hash(),
        "run_command": " ".join(sys.argv),
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "baselines": results,
    }
    if args.ext_manifest:
        output["ext_manifest"] = args.ext_manifest
        output["ext_split"] = args.ext_split
        output["ext_n_test"] = ext_n_test
        output["ext_baselines"] = ext_results
    (out_dir / "trivial_baselines.json").write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_dir}/trivial_baselines.json")


if __name__ == "__main__":
    main()

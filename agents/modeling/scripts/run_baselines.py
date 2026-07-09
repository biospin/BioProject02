"""
Run all 3 trivial baselines and print comparison table.

Smoke-test (no real data):
    python agents/modeling/scripts/run_baselines.py --smoke_test

Real mode:
    python agents/modeling/scripts/run_baselines.py \
        --manifest /data/embeddings/biop02/embedding_manifest.csv \
        --label_col er_status
"""

import argparse
import datetime
import json
import csv
import sys
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from modeling.baselines.trivial import RandomBaseline, SubtypeOnlyBaseline, MeanEmbedBaseline, evaluate, bootstrap_auc_ci


def make_dummy_dataset(n_slides: int = 20, dim: int = 1024, seed: int = 42):
    rng = np.random.default_rng(seed)
    X = [rng.standard_normal((rng.integers(100, 500), dim)).astype(np.float32) for _ in range(n_slides)]
    y = np.array([i % 2 for i in range(n_slides)], dtype=np.float32)
    return X, y


LABEL_MAP = {"positive": 1.0, "negative": 0.0}

def load_manifest_dataset(manifest_path: str, label_col: str, split: str = None, aux_col: str = None):
    X, y, aux = [], [], []
    skipped = 0
    with open(manifest_path, newline="") as f:
        for row in csv.DictReader(f):
            if split and row.get("split", "").lower() != split:
                continue
            emb_path = row.get("embedding_path", "")
            label_raw = row.get(label_col, "").strip().lower()
            if not emb_path or label_raw not in LABEL_MAP:
                skipped += 1
                continue
            X.append(np.load(emb_path))
            y.append(LABEL_MAP[label_raw])
            if aux_col:
                aux.append(row.get(aux_col, "").strip())
    if skipped:
        print(f"  [skip] {skipped} rows (Equivocal/Indeterminate/missing)")
    return X, np.array(y, dtype=np.float32), aux if aux_col else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="")
    parser.add_argument("--label_col", default="er")
    parser.add_argument("--smoke_test", action="store_true")
    parser.add_argument("--username", default="sjpark")
    parser.add_argument("--task", default="er_status")
    parser.add_argument("--tag", default="", help="실험 태그 (예: dummy_v1, uni_v1). 미지정 시 날짜 사용")
    parser.add_argument("--commit_hash", default="", help="git commit hash (서버 실행 시 로컬에서 명시적으로 전달)")
    parser.add_argument("--aux_col", default="pam50", help="subtype-only baseline용 보조 레이블 컬럼 (기본: pam50)")
    parser.add_argument("--bootstrap_ci", action="store_true", help="AUC bootstrap 95% CI 계산")
    parser.add_argument("--output_dir", default="/workspace/agents/modeling/experiments")
    parser.add_argument("--ext_manifest", default="", help="CPTAC 등 외부 test manifest 경로 — 지정 시 동일하게 fit된 baseline을 외부셋에도 평가 (CLAM 외부검증과 동일 조건 비교용)")
    parser.add_argument("--ext_split", default="cptac_external")
    parser.add_argument("--ext_label_col", default="", help="외부 manifest 라벨 컬럼명이 다를 경우 오버라이드 (미지정 시 --label_col 사용)")
    parser.add_argument("--ext_aux_col", default="", help="외부 manifest subtype 컬럼명이 다를 경우 오버라이드 (미지정 시 --aux_col 사용)")
    args = parser.parse_args()

    smoke_test = args.smoke_test or not args.manifest or not Path(args.manifest).exists()
    aux_col = args.aux_col if not smoke_test else None

    if smoke_test:
        print("Smoke-test mode: using dummy embeddings")
        X, y = make_dummy_dataset()
        n = len(X)
        sp = int(n * 0.8)
        X_train, X_val = X[:sp], X[sp:]
        y_train, y_val = y[:sp], y[sp:]
        sub_train = sub_val = None
    else:
        X_train, y_train, sub_train = load_manifest_dataset(args.manifest, args.label_col, split="train", aux_col=aux_col)
        X_val,   y_val,   sub_val   = load_manifest_dataset(args.manifest, args.label_col, split="val",   aux_col=aux_col)
    print(f"Slides: train={len(X_train)} val={len(X_val)}\n")

    baselines = [
        ("random",       RandomBaseline()),
        ("subtype_only", SubtypeOnlyBaseline()),
        ("mean_embed",   MeanEmbedBaseline()),
    ]

    results = []
    for name, clf in baselines:
        if name == "subtype_only" and sub_train is None:
            print(f"[{name:12s}]  skip (smoke_test 또는 aux_col 없음)")
            continue
        clf.fit(X_train, y_train, sub_train)
        proba = clf.predict_proba(X_val, sub_val)
        m = evaluate(name, proba, y_val, add_ci=args.bootstrap_ci)
        results.append(m)
        ci_str = f"  CI95={m['auc_ci_95']}" if args.bootstrap_ci and 'auc_ci_95' in m else ""
        print(f"[{name:12s}]  AUC={m['auc']}  AUPRC={m['auprc']}  BalAcc={m['balanced_accuracy']}{ci_str}")

    ext_results = None
    ext_n_test = None
    if args.ext_manifest and Path(args.ext_manifest).exists():
        ext_label_col = args.ext_label_col or args.label_col
        ext_aux_col = args.ext_aux_col or args.aux_col
        X_ext, y_ext, sub_ext = load_manifest_dataset(args.ext_manifest, ext_label_col, split=args.ext_split, aux_col=ext_aux_col)
        ext_n_test = len(X_ext)
        print(f"\n외부(CPTAC) 평가: n_test={ext_n_test} (label_col={ext_label_col}, split={args.ext_split})")
        if ext_n_test == 0:
            print(f"[warn] 0장 — ext_label_col({ext_label_col}) 또는 ext_split({args.ext_split}) 확인 필요")
        else:
            ext_results = []
            for name, clf in baselines:
                if name == "subtype_only" and sub_train is None:
                    continue
                proba_ext = clf.predict_proba(X_ext, sub_ext)
                m_ext = evaluate(name, proba_ext, y_ext, add_ci=args.bootstrap_ci)
                ext_results.append(m_ext)
                ci_str = f"  CI95={m_ext['auc_ci_95']}" if args.bootstrap_ci and 'auc_ci_95' in m_ext else ""
                print(f"[ext:{name:8s}]  AUC={m_ext['auc']}  AUPRC={m_ext['auprc']}  BalAcc={m_ext['balanced_accuracy']}{ci_str}")

    # 실험 디렉토리: experiments/<username>/<task>_<tag>_baselines/
    tag = args.tag if args.tag else datetime.datetime.now().strftime("%Y%m%d")
    suffix = f"{args.task}_{tag}_baselines" + ("_smoke" if smoke_test else "")
    out_dir = Path(args.output_dir) / args.username / suffix
    out_dir.mkdir(parents=True, exist_ok=True)

    import subprocess
    def get_git_hash():
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        except Exception:
            return "unknown"

    commit_hash = args.commit_hash if args.commit_hash else get_git_hash()

    output = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "task": args.task,
        "label_col": args.label_col,
        "manifest": args.manifest,
        "smoke_test": smoke_test,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "commit_hash": commit_hash,
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

"""BP02 인코더 ablation에 부트스트랩 신뢰구간과 쌍대 비교를 붙인다.

단일 test 분할의 점추정만으로는 인코더 간 차이를 주장할 수 없다.
같은 test 환자를 재표집해 각 인코더의 CI를 구하고, 인코더 쌍의 차이도
같은 재표집 인덱스로 계산해(paired) 차이의 CI를 낸다.
"""
import argparse, json, os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from bp02_encoder_ablation import ENCODERS, load_labels

TASKS = [("er", False), ("pr", False), ("her2", False), ("pam50_subtype", True)]


def load_cached(cache_dir, enc):
    z = np.load(os.path.join(cache_dir, f"{enc}_casemean.npz"), allow_pickle=True)
    return z["cases"].astype(str), z["Z"]


def score(y, P, multi):
    if multi:
        try:
            return roc_auc_score(y, P, multi_class="ovr", average="macro")
        except ValueError:
            return np.nan
    return roc_auc_score(y, P[:, 1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default=os.path.expanduser("~/work/fmpretrain/cache_bp02"))
    p.add_argument("--clin-dir", default=os.path.expanduser("~/data/clinical"))
    p.add_argument("--split", default=os.path.expanduser("~/data/split_policy_v1.csv"))
    p.add_argument("--out", default=os.path.expanduser(
        "~/work/fmpretrain/bp02_encoder_ablation_ci.json"))
    p.add_argument("--n-boot", type=int, default=1000)
    args = p.parse_args()

    split = pd.read_csv(args.split).set_index("case_id")["split"]
    labels = load_labels(args.clin_dir)
    rng = np.random.default_rng(0)
    out = {"n_boot": args.n_boot, "eval_split": "test", "tasks": {}}

    for tgt, multi in TASKS:
        probs, ytest, common = {}, None, None
        for enc in ENCODERS:
            cases, Z = load_cached(args.cache, enc)
            idx = pd.Index(cases)
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
            # 인코더마다 test 환자 집합이 같은지 확인해 paired 비교의 전제를 지킨다
            te_cases = cases[te]
            if common is None:
                common, ytest = te_cases, yte
            elif not np.array_equal(common, te_cases):
                raise RuntimeError(f"{enc}: test 환자 집합 불일치")
            probs[enc] = P

        n = len(ytest)
        boot_idx = [rng.integers(0, n, n) for _ in range(args.n_boot)]
        # 부트스트랩 표본에 클래스가 하나만 걸리면 AUROC가 정의되지 않아 건너뛴다
        per_enc, samples = {}, {}
        for enc, P in probs.items():
            vals = []
            for b in boot_idx:
                yb = ytest[b]
                if len(np.unique(yb)) < 2:
                    vals.append(np.nan)
                    continue
                vals.append(score(yb, P[b], multi))
            v = np.array(vals, dtype=float)
            samples[enc] = v
            ok = ~np.isnan(v)
            per_enc[enc] = {
                "auroc": float(score(ytest, P, multi)),
                "ci95": [float(np.percentile(v[ok], 2.5)),
                         float(np.percentile(v[ok], 97.5))],
                "n_test": int(n), "n_valid_boot": int(ok.sum()),
            }

        pairs = {}
        encs = list(probs)
        for i in range(len(encs)):
            for j in range(i + 1, len(encs)):
                a, b_ = encs[i], encs[j]
                d = samples[a] - samples[b_]
                d = d[~np.isnan(d)]
                lo, hi = np.percentile(d, [2.5, 97.5])
                pairs[f"{a} - {b_}"] = {
                    "delta": float(per_enc[a]["auroc"] - per_enc[b_]["auroc"]),
                    "ci95": [float(lo), float(hi)],
                    "excludes_zero": bool(lo > 0 or hi < 0),
                }

        out["tasks"][tgt] = {"per_encoder": per_enc, "pairwise": pairs}
        print(f"\n[{tgt}] n_test={n}")
        for enc, r in per_enc.items():
            print(f"  {enc:20s} AUROC={r['auroc']:.4f} "
                  f"CI95=[{r['ci95'][0]:.4f}, {r['ci95'][1]:.4f}]")
        sig = [k for k, v in pairs.items() if v["excludes_zero"]]
        print(f"  0을 포함하지 않는 쌍: {sig if sig else '없음'}")

    json.dump(out, open(args.out, "w"), indent=2)
    print(f"\n[done] {args.out}")


if __name__ == "__main__":
    main()

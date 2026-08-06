"""BIOP02-123 #2 LOSO/site-grouped 심판 — 앵커 endpoint 신호가 site로 설명되나.
같은 모델(mean-pool LR)에서 random CV vs site-grouped CV(GroupKFold on TSS) AUROC 비교.
site-grouped에서 test site가 train에 없음 → 하락하면 site-driven(🔴), 유지하면 site-독립(🟢).
CPU, 기존 임베딩 재사용."""
import argparse, csv, json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

META = "/workspace/data/cache/biop02_site_audit"
EMB = "/workspace/data/cache/biop02/crosscancer/{cohort}/uni_v1"

def oof_auc(X, y, groups=None, seed=42):
    oof = np.zeros(len(y))
    if groups is None:
        splitter = StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y)
    else:
        splitter = GroupKFold(5).split(X, y, groups)
    for tr, te in splitter:
        if len(set(y[tr])) < 2:
            oof[te] = y[tr].mean(); continue
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(StandardScaler().fit_transform(X[tr]), y[tr])
        oof[te] = clf.predict_proba(StandardScaler().fit(X[tr]).transform(X[te]))[:, 1]
    return roc_auc_score(y, oof)

def boot_ci(y, p, n=1000, seed=1):
    rng = np.random.default_rng(seed); a = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2: continue
        a.append(roc_auc_score(y[idx], p[idx]))
    return [round(float(np.percentile(a, 2.5)), 3), round(float(np.percentile(a, 97.5)), 3)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--endpoints", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = Path(META) / a.cohort
    labels = {r["case_id"]: r for r in csv.DictReader(open(d / "patient_labels.csv"))}
    site = {r["case_id"]: r["tss_code"] for r in csv.DictReader(open(d / "split.csv"))}
    emb_dir = Path(EMB.format(cohort=a.cohort))
    slides = []
    for p in sorted(emb_dir.glob("*_uni_embeddings.npy")):
        sid = p.name.replace("_uni_embeddings.npy", ""); cid = sid[:12]
        if cid in site: slides.append((cid, p))
    # case별 첫 슬라이드만 (환자단위)
    seen = {};
    for cid, p in slides: seen.setdefault(cid, p)
    Xall = {cid: np.load(p).mean(0).astype(np.float32) for cid, p in seen.items()}

    res = {"cohort": a.cohort, "endpoints": {}}
    for ep in a.endpoints.split(","):
        cids = [c for c in seen if c in labels and labels[c].get(ep) in ("0", "1")]
        y = np.array([int(labels[c][ep]) for c in cids])
        if len(set(y)) < 2 or y.sum() < 8:
            res["endpoints"][ep] = {"note": f"n_pos={int(y.sum())} 부족"}; continue
        X = np.stack([Xall[c] for c in cids])
        g = np.array([site[c] for c in cids])
        rand = oof_auc(X, y)
        grp = oof_auc(X, y, groups=g)
        drop = rand - grp
        res["endpoints"][ep] = {
            "n": len(y), "n_pos": int(y.sum()), "n_sites": len(set(g)),
            "random_cv_auroc": round(rand, 4), "site_grouped_cv_auroc": round(grp, 4),
            "drop_random_minus_grouped": round(drop, 4),
            "verdict": "🟢 site-독립(유지)" if drop < 0.05 else ("🟡 부분 site교란" if drop < 0.10 else "🔴 site-driven(하락)"),
        }
        print(f"  {ep:16s} random {rand:.3f} → site-grouped {grp:.3f} (drop {drop:+.3f}, n_pos={int(y.sum())}) {res['endpoints'][ep]['verdict']}", flush=True)
    json.dump(res, open(a.out, "w"), indent=2, ensure_ascii=False)
    print(f"Saved {a.out}\nDONE_{a.cohort}")

if __name__ == "__main__":
    main()

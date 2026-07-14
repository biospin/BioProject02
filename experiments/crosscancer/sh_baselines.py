#!/usr/bin/env python3
"""BLOCKER-3 remediation: pixel-mean baseline (전 암종·전 endpoint).

MIL(attention)이 아니라 슬라이드 임베딩을 단순 mean-pool → 환자 평균 → LogisticRegression.
목적(braveji): 라벨무관 mean-embedding/bag-size 교란이 AUROC를 얼마나 설명하는지 = 형태학 MIL의
'진짜 신호'를 재는 trivial baseline. MIL≈pixel-mean이면 attention 이득 없음.
GPU 불필요(CPU). 같은 split/holdout(val+test pooled, site-disjoint)/환자단위 agg로 MIL과 비교가능.

사용: python sh_baselines.py --cancer LUNG_NSCLC
출력: <cancer>/full/baseline_pixelmean.json
"""
import json, sys, time, argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
import run_mil_cost as m  # load_meta, bootstrap_auc

ENDPOINTS = {
    "LUNG_NSCLC":    ["histology_lusc", "egfr_activating", "kras_g12c"],
    "GASTRIC_STAD":  ["lauren_diffuse", "msi_h", "erbb2_amp", "ebv"],
    "HEADNECK_HNSC": ["hpv_pos", "egfr_amp", "grade_high"],
    "COLORECTAL":    ["msi_high", "anti_egfr_eligible", "braf_v600"],
}
HERE = Path(__file__).parent

def slide_mean(path):
    a = np.load(path).astype("float32")
    return a.mean(axis=0)  # (1024,)

def run_ep(slides, labels, ep, mean_cache):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    def rows(split):
        out = []
        for s in slides:
            lv = labels.get(s["case_id"], {}).get(ep, "")
            if s["split"] == split and lv != "":
                out.append((s, int(lv)))
        return out
    tr = rows("train"); hold = rows("val") + rows("test")
    if not tr or not hold or len({l for _, l in tr}) < 2:
        return {"status": "skip(insufficient)"}
    # 환자단위 mean 임베딩
    def pat_X(recs):
        by = defaultdict(list); yv = {}
        for s, y in recs:
            by[s["case_id"]].append(mean_cache[s["slide_id"]]); yv[s["case_id"]] = y
        cs = sorted(by); X = np.vstack([np.mean(by[c], axis=0) for c in cs]); Y = np.array([yv[c] for c in cs])
        return cs, X, Y
    _, Xtr, Ytr = pat_X(tr); ch, Xh, Yh = pat_X(hold)
    if len(set(Ytr)) < 2 or len(set(Yh)) < 2:
        return {"status": "skip(single-class)"}
    sc = StandardScaler().fit(Xtr)
    clf = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced").fit(sc.transform(Xtr), Ytr)
    p = clf.predict_proba(sc.transform(Xh))[:, 1]
    auc, lo, hi = m.bootstrap_auc(list(Yh), list(p))
    return {"auc": auc, "ci95": [lo, hi], "n_pos": int(Yh.sum()), "n_hold": len(Yh),
            "method": "pixel-mean(slide mean-pool→patient mean)→StandardScaler→LogReg(balanced)"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True, choices=list(ENDPOINTS))
    ap.add_argument("--endpoints")
    a = ap.parse_args()
    labels, split, slides = m.load_meta(a.cancer)
    eps = a.endpoints.split(",") if a.endpoints else ENDPOINTS[a.cancer]
    print(f"[{a.cancer}] slides={len(slides)} eps={eps} — mean-pool 캐시 구축...", flush=True)
    t0 = time.time()
    mean_cache = {s["slide_id"]: slide_mean(s["path"]) for s in slides}
    print(f"  캐시 {len(mean_cache)}개 ({time.time()-t0:.0f}s)", flush=True)
    res = {"track": a.cancer, "purpose": "pixel-mean baseline (BLOCKER-3)",
           "claim_level": "hypothesis_only", "critic_status": "pending", "endpoints": {}}
    for ep in eps:
        t = time.time(); r = run_ep(slides, labels, ep, mean_cache)
        res["endpoints"][ep] = r
        print(f"  {ep}: {r.get('auc', r.get('status'))} n_pos={r.get('n_pos')} ({time.time()-t:.0f}s)", flush=True)
    out = HERE / a.cancer / "full" / "baseline_pixelmean.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"wrote {out}", flush=True)

if __name__ == "__main__":
    main()

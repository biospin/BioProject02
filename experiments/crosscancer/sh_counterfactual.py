#!/usr/bin/env python3
"""7-point #3 counterfactual (특징 제거) — sealed-forward attention ablation.

CLAM-SB는 attention-MIL → "핵심 특징 제거" = full-bag attention 상위 타일 제거 후 재-forward.
top-k% 제거 시 AUROC 저하 ≫ random-k% 제거면, 예측이 특정 형태(고-attention 타일)에 **충실**함을 보임.
seed=42 real 모델(run_mil_cost.train_eval 학습경로 동일 복제)로 holdout 재채점.

각 endpoint: full / top-k 제거 / random-k 제거 / bottom-k 제거 (k=10,20%) 환자단위 AUROC.
사용: python sh_counterfactual.py --cancer HEADNECK_HNSC --endpoints hpv_pos --device cuda:0
출력: <cancer>/full/counterfactual_ablation.json
"""
import json, sys, time, argparse
from pathlib import Path
import numpy as np
import run_mil_cost as m

HERE = Path(__file__).parent
KS = [0.10, 0.20]
DEFAULT_EP = {"HEADNECK_HNSC": ["hpv_pos", "grade_high"], "LUNG_NSCLC": ["histology_lusc"],
              "GASTRIC_STAD": ["msi_h"]}

def train_model(slides, labels, endpoint, device, seed=42, epochs=40):
    """run_mil_cost.train_eval 학습경로 정확 복제 — 단 학습된 model 반환(ablation용)."""
    import torch, torch.nn as nn
    from attention_mil import CLAMSB
    from sklearn.metrics import roc_auc_score
    torch.manual_seed(seed); np.random.seed(seed)
    def rows(sp):
        return [(s, int(labels.get(s["case_id"], {}).get(endpoint, "") or -1))
                for s in slides if s["split"] == sp and labels.get(s["case_id"], {}).get(endpoint, "") != ""]
    tr_all = rows("train"); hold = rows("val") + rows("test")
    if not tr_all or not hold or len({l for _, l in tr_all}) < 2: return None, None, None
    pats = sorted({s["case_id"] for s, _ in tr_all})
    rng = np.random.default_rng(seed); rng.shuffle(pats)
    dev_pat = set(pats[:max(1, int(len(pats) * 0.15))])
    tr = [(s, y) for s, y in tr_all if s["case_id"] not in dev_pat]
    va = [(s, y) for s, y in tr_all if s["case_id"] in dev_pat]
    if len({l for _, l in tr}) < 2: return None, None, None
    dev = torch.device(device if torch.cuda.is_available() else "cpu")
    model = CLAMSB(feature_dim=1024, hidden_dim=512, att_dim=256, dropout=0.25).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=2e-4, weight_decay=1e-4)
    lossf = nn.BCEWithLogitsLoss()
    def emb(s): return torch.from_numpy(np.load(s["path"]).astype("float32")).to(dev)
    best_va = -1; best_state = None; bad = 0
    for ep in range(epochs):
        model.train(); order = np.random.permutation(len(tr))
        for i in order:
            s, y = tr[i]; opt.zero_grad()
            logit, _ = model(emb(s)); loss = lossf(logit, torch.tensor([float(y)], device=dev))
            loss.backward(); opt.step()
        model.eval(); yp = []; yt = []
        with torch.no_grad():
            for s, y in va:
                logit, _ = model(emb(s)); yp.append(torch.sigmoid(logit).item()); yt.append(y)
        va_auc = roc_auc_score(yt, yp) if len(set(yt)) > 1 else 0.5
        if va_auc > best_va: best_va = va_auc; best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}; bad = 0
        else:
            bad += 1
            if bad >= 7: break
    if best_state: model.load_state_dict(best_state)
    model.eval()
    return model, hold, dev

def proba_ablate(model, X, dev, mode, k):
    """X: (N,1024) np. mode: full/top/random/bottom. full-bag attention 기준 k% 제거."""
    import torch
    xt = torch.from_numpy(X.astype("float32")).to(dev)
    with torch.no_grad():
        logit, w = model(xt); w = w.squeeze(-1).cpu().numpy()  # (N,)
    N = len(w); nrm = max(1, int(round(k * N)))
    if mode == "full" or N - nrm < 2:
        with torch.no_grad(): lg, _ = model(xt); return float(torch.sigmoid(lg).item())
    order = np.argsort(w)  # asc (low att first)
    if mode == "top": keep = order[:N - nrm]          # 상위 att 제거
    elif mode == "bottom": keep = order[nrm:]         # 하위 att 제거
    else:
        rng = np.random.default_rng(0); keep = rng.choice(N, N - nrm, replace=False)
    with torch.no_grad():
        lg, _ = model(xt[np.sort(keep)]); return float(torch.sigmoid(lg).item())

def run_ep(slides, labels, endpoint, device):
    model, hold, dev = train_model(slides, labels, endpoint, device)
    if model is None: return {"status": "skip"}
    conds = ["full"] + [f"{mo}{int(k*100)}" for k in KS for mo in ("top", "random", "bottom")]
    from collections import defaultdict
    pp = {c: defaultdict(list) for c in conds}; yt = {}
    for s, y in hold:
        X = np.load(s["path"]); yt[s["case_id"]] = y
        pp["full"][s["case_id"]].append(proba_ablate(model, X, dev, "full", 0))
        for k in KS:
            for mo in ("top", "random", "bottom"):
                pp[f"{mo}{int(k*100)}"][s["case_id"]].append(proba_ablate(model, X, dev, mo, k))
    out = {}
    for c in conds:
        cs = sorted(pp[c]); y = [yt[x] for x in cs]; p = [float(np.mean(pp[c][x])) for x in cs]
        auc, lo, hi = m.bootstrap_auc(y, p)
        out[c] = {"auc": auc, "ci95": [lo, hi], "n_pos": int(sum(y)), "n": len(y)}
    full = out["full"]["auc"]
    out["_drop_vs_full"] = {c: (round(full - out[c]["auc"], 4) if out[c]["auc"] is not None else None)
                            for c in conds if c != "full"}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--endpoints")
    a = ap.parse_args()
    labels, split, slides = m.load_meta(a.cancer)
    eps = a.endpoints.split(",") if a.endpoints else DEFAULT_EP.get(a.cancer, [])
    print(f"[{a.cancer}] slides={len(slides)} eps={eps} device={a.device}", flush=True)
    res = {"track": a.cancer, "purpose": "counterfactual attention-ablation (7-point #3)",
           "claim_level": "hypothesis_only", "critic_status": "pending", "ablation_k": KS, "endpoints": {}}
    for ep in eps:
        t = time.time(); r = run_ep(slides, labels, ep, a.device); res["endpoints"][ep] = r
        d = r.get("_drop_vs_full", {})
        print(f"  {ep}: full={r.get('full',{}).get('auc')} | drop top10={d.get('top10')} random10={d.get('random10')} top20={d.get('top20')} random20={d.get('random20')} ({time.time()-t:.0f}s)", flush=True)
    out = HERE / a.cancer / "full" / "counterfactual_ablation.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"wrote {out}", flush=True)

if __name__ == "__main__":
    main()

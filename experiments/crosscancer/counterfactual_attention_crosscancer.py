#!/usr/bin/env python3
"""Cross-cancer Critic #3 — sealed-forward attention-faithfulness counterfactual.

braveji Critic 4차 재판정(PR #49)의 open item: 폐/위/두경부 sealed held-out에
'특징 제거' counterfactual 부재(shuffle-null은 라벨순열이지 특징제거 아님).

방법(BRCA counterfactual_attention.py와 동일 원리):
  1. [재현 게이트] run_mil_cost.train_eval을 verbatim 재현해 held-out AUC가
     저장값과 ±TOL 내인지 먼저 확인. 벗어나면 그 endpoint는 counterfactual 미부착(provenance 경고).
  2. [counterfactual] 재현된 바로 그 모델로 held-out 슬라이드마다 attention(N,1)을 얻어
     top-k% attention 타일 제거 vs 무작위 k% 제거 후 재예측 → 환자수준 AUC 낙폭 비교.
     faithful이면 top-att 제거가 무작위 제거보다 AUC를 더 크게 떨군다.

高-AUC(signal 있는) endpoint에서만 faithfulness 의미 有. 低-AUC(H&E-blind)는 N/A.

GPU 예약: cuda:1 (nvidia-smi 확인 후 유휴, #biop02-alerts Slack 도구 부재로 산출물에 명기).
claim_level=hypothesis_only, critic_status=pending, owner=kkkim(=braveji #3 증거, Critic 서명 아님).
Run: conda run -n spatialpatho python experiments/crosscancer/counterfactual_attention_crosscancer.py --device cuda:1
"""
import argparse, json, sys, time
from pathlib import Path
from collections import defaultdict
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "agents/modeling/baselines"))
import run_mil_cost as R  # load_meta, patient_agg, bootstrap_auc, CANCER_CFG

TOL = 0.01          # 재현 허용오차(cudnn/permutation 확률성 감안)
HIGH_AUC = 0.80     # 이상이면 faithfulness 테스트, 미만은 N/A
REMOVE_FRACS = [0.10, 0.20]

CANCERS = {
    "LUNG_NSCLC":    ["histology_lusc", "egfr_activating", "kras_g12c"],
    "GASTRIC_STAD":  ["msi_h", "ebv", "lauren_diffuse", "erbb2_amp"],
    "HEADNECK_HNSC": ["hpv_pos", "grade_high", "egfr_amp"],
}


def train_eval_model(slides, labels, endpoint, device, epochs=40, seed=42):
    """run_mil_cost.train_eval을 verbatim 복사 + 학습된 model 반환(attention 접근용).
    shuffle=False 경로만(real). 반환: (recs, best_va, model)."""
    import torch, torch.nn as nn
    from attention_mil import CLAMSB
    from sklearn.metrics import roc_auc_score
    torch.manual_seed(seed); np.random.seed(seed)
    def rows(split):
        out = []
        for s in slides:
            lv = labels.get(s["case_id"], {}).get(endpoint, "")
            if s["split"] == split and lv != "":
                out.append((s, int(lv)))
        return out
    tr_all = rows("train"); hold = rows("val") + rows("test")
    if not tr_all or not hold or len({l for _, l in tr_all}) < 2:
        return None, None, None
    pats = sorted({s["case_id"] for s, _ in tr_all})
    rng = np.random.default_rng(seed); rng.shuffle(pats)
    dev_pat = set(pats[:max(1, int(len(pats) * 0.15))])
    tr = [(s, y) for s, y in tr_all if s["case_id"] not in dev_pat]
    va = [(s, y) for s, y in tr_all if s["case_id"] in dev_pat]
    te = hold
    if len({l for _, l in tr}) < 2:
        return None, None, None
    dev = torch.device(device if torch.cuda.is_available() else "cpu")
    model = CLAMSB(feature_dim=1024, hidden_dim=512, att_dim=256, dropout=0.25).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=2e-4, weight_decay=1e-4)
    lossf = nn.BCEWithLogitsLoss()
    def emb(s): return torch.from_numpy(np.load(s["path"]).astype("float32")).to(dev)
    best_va = -1; best_state = None; patience = 7; bad = 0
    for ep in range(epochs):
        model.train(); order = np.random.permutation(len(tr))
        for i in order:
            s, y = tr[i]; opt.zero_grad()
            logit, _ = model(emb(s))
            loss = lossf(logit, torch.tensor([float(y)], device=dev))
            loss.backward(); opt.step()
        model.eval(); yp = []; yt = []
        with torch.no_grad():
            for s, y in va:
                logit, _ = model(emb(s)); yp.append(torch.sigmoid(logit).item()); yt.append(y)
        va_auc = roc_auc_score(yt, yp) if len(set(yt)) > 1 else 0.5
        if va_auc > best_va:
            best_va = va_auc; best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}; bad = 0
        else:
            bad += 1
            if bad >= patience: break
    if best_state: model.load_state_dict(best_state)
    model.eval(); recs = []
    with torch.no_grad():
        for s, y in te:
            logit, _ = model(emb(s)); recs.append({"case_id": s["case_id"], "proba": torch.sigmoid(logit).item(), "y": y})
    return recs, round(float(best_va), 4), model


def eval_with_removal(model, slides_hold, labels, endpoint, device, frac, mode, seed=42):
    """held-out 슬라이드마다 attention 상위 frac(또는 무작위 frac) 타일 제거 후 재예측 → 환자 AUC."""
    import torch
    dev = torch.device(device if torch.cuda.is_available() else "cpu")
    recs = []
    model.eval()
    with torch.no_grad():
        for s in slides_hold:
            lv = labels.get(s["case_id"], {}).get(endpoint, "")
            if lv == "": continue
            X = np.load(s["path"]).astype("float32")
            N = X.shape[0]
            if N < 5:  # 너무 적으면 원본 유지
                keep = np.arange(N)
            else:
                x = torch.from_numpy(X).to(dev)
                _, w = model(x)                       # (N,1) attention
                w = w.squeeze(-1).cpu().numpy()
                assert w.shape[0] == N, f"attention len {w.shape[0]} != tiles {N}"
                k = max(1, int(round(N * frac)))
                if mode == "top":
                    drop = np.argsort(-w)[:k]          # 최고 attention k개 제거
                elif mode == "random":
                    drop = np.random.default_rng(seed + hash(s["slide_id"]) % 10000).choice(N, k, replace=False)
                keep = np.setdiff1d(np.arange(N), drop)
            xk = torch.from_numpy(X[keep]).to(dev)
            logit, _ = model(xk)
            recs.append({"case_id": s["case_id"], "proba": torch.sigmoid(logit).item(), "y": int(lv)})
    pa = R.patient_agg(recs)
    y = [v[1] for v in pa.values()]; p = [v[0] for v in pa.values()]
    auc, lo, hi = R.bootstrap_auc(y, p)
    return auc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda:1")
    ap.add_argument("--cancers", nargs="+", default=list(CANCERS))
    ap.add_argument("--out", default=str(HERE.parent / "kkkim/20260716_crosscancer_subcheck_owner/counterfactual_faithfulness.json"))
    a = ap.parse_args()

    report = {"analysis": "Critic #3 sealed-forward attention-faithfulness counterfactual",
              "method": "top-attention vs random tile removal → held-out patient AUC 낙폭 비교",
              "owner": "kkkim", "role": "braveji #3 증거(Critic 서명 아님)",
              "claim_level": "hypothesis_only", "critic_status": "pending",
              "gpu": a.device, "tol": TOL, "high_auc_threshold": HIGH_AUC,
              "per_cancer": {}}

    for cancer in a.cancers:
        labels, split, slides = R.load_meta(cancer)
        stored = json.loads((HERE / cancer / "full/mil_cost_results.json").read_text())["endpoints"]
        hold = [s for s in slides if s["split"] in ("val", "test")]
        print(f"\n===== {cancer}: {len(slides)} slides ({len(hold)} held-out) =====")
        crep = {}
        for ep in CANCERS[cancer]:
            t = time.time()
            recs, va, model = train_eval_model(slides, labels, ep, a.device)
            if recs is None:
                crep[ep] = {"status": "skip(insufficient)"}; print(f"  {ep}: skip"); continue
            pa = R.patient_agg(recs); y = [v[1] for v in pa.values()]; p = [v[0] for v in pa.values()]
            repro_auc, lo, hi = R.bootstrap_auc(y, p)
            stored_auc = stored.get(ep, {}).get("real", {}).get("auc")
            delta = round(abs(repro_auc - stored_auc), 4) if (repro_auc is not None and stored_auc is not None) else None
            reproduced = (delta is not None and delta <= TOL)
            entry = {"stored_auc": stored_auc, "repro_auc": repro_auc, "delta": delta,
                     "reproduced_within_tol": reproduced, "n_pos": int(sum(y)), "n_holdout": len(pa)}
            print(f"  {ep}: stored={stored_auc} repro={repro_auc} Δ={delta} {'✓재현' if reproduced else '✗불일치'} ({time.time()-t:.0f}s)")
            # counterfactual: 재현 + high-AUC 에서만
            if reproduced and repro_auc is not None and repro_auc >= HIGH_AUC:
                cf = {"full_auc": repro_auc, "removal": {}}
                for frac in REMOVE_FRACS:
                    top = eval_with_removal(model, hold, labels, ep, a.device, frac, "top")
                    rnd = eval_with_removal(model, hold, labels, ep, a.device, frac, "random")
                    drop_top = round(repro_auc - top, 4) if top is not None else None
                    drop_rnd = round(repro_auc - rnd, 4) if rnd is not None else None
                    faithful = (drop_top is not None and drop_rnd is not None and drop_top > drop_rnd)
                    cf["removal"][f"{int(frac*100)}pct"] = {
                        "auc_top_removed": top, "auc_random_removed": rnd,
                        "drop_top": drop_top, "drop_random": drop_rnd,
                        "faithful(top>random)": faithful}
                    print(f"      remove {int(frac*100)}%: top-att→{top}(Δ{drop_top}) random→{rnd}(Δ{drop_rnd}) faithful={faithful}")
                entry["counterfactual"] = cf
            elif reproduced:
                entry["counterfactual"] = {"status": "N/A", "reason": f"AUC {repro_auc} < {HIGH_AUC} (H&E-blind, signal 없음→faithfulness 무의미)"}
            else:
                entry["counterfactual"] = {"status": "skip", "reason": "재현 실패 → 다른 모델에 counterfactual 부착 금지(provenance)"}
            crep[ep] = entry
        report["per_cancer"][cancer] = crep

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nsaved: {a.out}")


if __name__ == "__main__":
    main()

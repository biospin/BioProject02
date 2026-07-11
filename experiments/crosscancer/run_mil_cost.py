#!/usr/bin/env python3
"""
Cross-cancer MIL 학습 + cost-of-substitution (자율, advisor 게이트 내장).

각 endpoint를 {real, shuffle-null, prevalence-baseline} 3조건으로 평가 →
AUROC≈0.5가 'H&E-blind(가설확증)'인지 'MIL 고장'인지 shuffle/baseline으로 구분.
histology(LUAD/LUSC)=양성대조(H&E가 형태 봄, ~0.9 기대) — 실패 시 파이프라인 고장 플래그.
cost = 측정 vs 예측 치료축 라우팅 × frozen_map 치료거리.

입력(각 <cancer>/full/): embeddings/*_uni_embeddings.npy, patient_labels.csv, split.csv, ../frozen_map.json
출력: <cancer>/full/mil_cost_results.json  (+ per-endpoint 상세)
GPU 필요 — 임베딩 완료 후 실행(오케스트레이터가 count 게이트).
"""
import json, csv, sys, argparse, time
from pathlib import Path
from collections import defaultdict
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "agents/modeling/baselines"))

# endpoint→치료축, 축쌍 거리는 frozen_map.json에서
CANCER_CFG = {
 "LUNG_NSCLC": {
   "endpoints": ["histology_lusc", "egfr_activating", "kras_g12c"],   # histology=양성대조
   "positive_control": "histology_lusc",
   "route_axis": {"egfr_activating": "antiEGFR", "kras_g12c": "antiKRAS_G12C"},  # 우선순위 순
   "route_default": "chemo",
   "axis_key": {"antiEGFR":"antiEGFR","antiKRAS_G12C":"antiKRAS_G12C","chemo":"chemo"},
 },
 "COLORECTAL": {
   "endpoints": ["braf_v600e"],
   "positive_control": None,
   "route_axis": {"braf_v600e": "antiBRAF"},
   "route_default": "baseline",
   "axis_key": {"antiBRAF":"antiBRAF","baseline":"baseline"},
 },
}

def load_meta(cancer):
    d = HERE / cancer / "full"
    labels = {r["case_id"]: r for r in csv.DictReader(open(d/"patient_labels.csv"))}
    split = {r["case_id"]: r["split"] for r in csv.DictReader(open(d/"split.csv"))}
    # 임베딩 매니페스트: embeddings dir에서 직접(부분/완료 무관)
    slides = []
    for p in sorted((d/"embeddings").glob("*_uni_embeddings.npy")):
        sid = p.name.replace("_uni_embeddings.npy","")
        cid = sid[:12]
        if cid in split:
            slides.append({"slide_id":sid, "case_id":cid, "path":p, "split":split[cid]})
    return labels, split, slides

def bootstrap_auc(y, p, n=1000, seed=42):
    from sklearn.metrics import roc_auc_score
    y=np.array(y); p=np.array(p)
    if len(set(y))<2: return None, None, None
    rng=np.random.default_rng(seed)
    base=roc_auc_score(y,p); boots=[]
    for _ in range(n):
        idx=rng.integers(0,len(y),len(y))
        if len(set(y[idx]))<2: continue
        boots.append(roc_auc_score(y[idx],p[idx]))
    lo,hi=(np.percentile(boots,[2.5,97.5]) if boots else (None,None))
    return round(float(base),4), (round(float(lo),4) if lo is not None else None), (round(float(hi),4) if hi is not None else None)

def train_eval(slides, labels, endpoint, device, shuffle=False, epochs=40, seed=42):
    """CLAMSB 학습→test proba(슬라이드). 반환: (test_slide_records, val_auc)."""
    import torch, torch.nn as nn
    from attention_mil import CLAMSB
    torch.manual_seed(seed); np.random.seed(seed)
    def rows(split):
        out=[]
        for s in slides:
            lv=labels.get(s["case_id"],{}).get(endpoint,"")
            if s["split"]==split and lv!="":
                out.append((s, int(lv)))
        return out
    tr, va, te = rows("train"), rows("val"), rows("test")
    if not tr or not te or len({l for _,l in tr})<2: return None, None
    if shuffle:
        ys=[l for _,l in tr]; np.random.default_rng(seed).shuffle(ys); tr=[(s,y) for (s,_),y in zip(tr,ys)]
    dev=torch.device(device if torch.cuda.is_available() else "cpu")
    model=CLAMSB(feature_dim=1024, hidden_dim=512, att_dim=256, dropout=0.25).to(dev)
    opt=torch.optim.Adam(model.parameters(), lr=2e-4, weight_decay=1e-4)
    lossf=nn.BCEWithLogitsLoss()
    def emb(s): return torch.from_numpy(np.load(s["path"]).astype("float32")).to(dev)
    best_va=-1; best_state=None; patience=7; bad=0
    for ep in range(epochs):
        model.train(); order=np.random.permutation(len(tr))
        for i in order:
            s,y=tr[i]; opt.zero_grad()
            logit,_=model(emb(s))
            loss=lossf(logit, torch.tensor([float(y)],device=dev))
            loss.backward(); opt.step()
        # val
        model.eval(); yp=[]; yt=[]
        with torch.no_grad():
            for s,y in va:
                logit,_=model(emb(s)); yp.append(torch.sigmoid(logit).item()); yt.append(y)
        from sklearn.metrics import roc_auc_score
        va_auc=roc_auc_score(yt,yp) if len(set(yt))>1 else 0.5
        if va_auc>best_va: best_va=va_auc; best_state={k:v.cpu().clone() for k,v in model.state_dict().items()}; bad=0
        else:
            bad+=1
            if bad>=patience: break
    if best_state: model.load_state_dict(best_state)
    model.eval(); recs=[]
    with torch.no_grad():
        for s,y in te:
            logit,_=model(emb(s)); recs.append({"case_id":s["case_id"],"proba":torch.sigmoid(logit).item(),"y":y})
    return recs, round(float(best_va),4)

def patient_agg(recs):
    """슬라이드 proba→환자(평균). 반환 {case_id:(proba,y)}."""
    by=defaultdict(list)
    for r in recs: by[r["case_id"]].append((r["proba"],r["y"]))
    return {c:(float(np.mean([p for p,_ in v])), v[0][1]) for c,v in by.items()}

def run_endpoint(slides, labels, endpoint, device):
    out={}
    # real
    recs,va=train_eval(slides,labels,endpoint,device,shuffle=False)
    if recs is None: return {"status":"skip(insufficient)"}
    pa=patient_agg(recs); y=[v[1] for v in pa.values()]; p=[v[0] for v in pa.values()]
    auc,lo,hi=bootstrap_auc(y,p)
    out["real"]={"auc":auc,"ci95":[lo,hi],"n_test_patients":len(pa),"n_pos":int(sum(y)),"val_auc":va}
    # shuffle-null
    srecs,_=train_eval(slides,labels,endpoint,device,shuffle=True)
    if srecs:
        spa=patient_agg(srecs); sy=[v[1] for v in spa.values()]; sp=[v[0] for v in spa.values()]
        sa,_,_=bootstrap_auc(sy,sp); out["shuffle_null"]={"auc":sa}
    # prevalence baseline (train 양성률로 상수 예측 → AUROC 0.5)
    out["prevalence_baseline"]={"auc":0.5,"note":"상수예측 정의상 0.5"}
    out["patient_proba"]={c:round(v[0],4) for c,v in pa.items()}
    out["patient_true"]={c:v[1] for c,v in pa.items()}
    return out

def cost_routing(cancer, ep_results, labels, split):
    cfg=CANCER_CFG[cancer]
    fm=json.loads((HERE/cancer/"frozen_map.json").read_text())
    dist=fm["axis_pair_distance"]  # keys "A__B"
    def dd(a,b):
        if a==b: return 0.0
        for k in (f"{a}__{b}",f"{b}__{a}"):
            if k in dist: return dist[k]["therapeutic_distance"]
        return None
    # test 환자 집합 = route에 쓰는 endpoint 예측이 있는 환자
    route_eps=list(cfg["route_axis"].keys())
    # 측정/예측 축
    def axis(getter):
        # getter(ep, case) -> 0/1
        def f(case):
            for ep in route_eps:  # 우선순위 순
                if getter(ep, case)==1: return cfg["route_axis"][ep]
            return cfg["route_default"]
        return f
    # 측정
    meas_get=lambda ep,c: int(labels.get(c,{}).get(ep,"0") or 0)
    # 예측(proba>=0.5)
    pred_tbl={ep:ep_results.get(ep,{}).get("patient_proba",{}) for ep in route_eps}
    def pred_get(ep,c):
        v=pred_tbl.get(ep,{}).get(c)
        return int(v>=0.5) if v is not None else 0
    # test 환자 = 예측표에 등장하는 환자(교집합)
    test_cases=set()
    for ep in route_eps: test_cases|=set(pred_tbl[ep].keys())
    m_axis=axis(meas_get); p_axis=axis(pred_get)
    per=defaultdict(lambda:{"n":0,"mis":0,"cost":0.0}); rows=[]
    for c in sorted(test_cases):
        ma=m_axis(c); pa=p_axis(c); d=dd(ma,pa)
        if d is None: continue
        st=per[ma]; st["n"]+=1; st["cost"]+=d
        if ma!=pa: st["mis"]+=1
        rows.append({"case_id":c,"measured":ma,"pred":pa,"cost":d})
    summary={a:{"n":v["n"],"mean_cost":round(v["cost"]/v["n"],3) if v["n"] else None,
                "misroute_rate":round(v["mis"]/v["n"],3) if v["n"] else None} for a,v in per.items()}
    return {"per_axis":summary, "n_routed":len(rows), "axis_pair_distance":{k:v["therapeutic_distance"] for k,v in dist.items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--smoke", action="store_true", help="현 부분 임베딩으로 histology만 빠르게")
    a=ap.parse_args()
    cfg=CANCER_CFG[a.cancer]
    labels, split, slides=load_meta(a.cancer)
    print(f"{a.cancer}: {len(slides)} 슬라이드(임베딩 존재), {len(labels)} 라벨환자")
    eps = [cfg["positive_control"]] if (a.smoke and cfg["positive_control"]) else cfg["endpoints"]
    results={"cancer":a.cancer,"n_slides":len(slides),"claim_level":"hypothesis_only","critic_status":"pending","endpoints":{}}
    for ep in eps:
        t=time.time(); r=run_endpoint(slides,labels,ep,a.device)
        results["endpoints"][ep]=r
        real=r.get("real",{}); sh=r.get("shuffle_null",{})
        print(f"  {ep}: real AUC={real.get('auc')} CI{real.get('ci95')} n+={real.get('n_pos')}/{real.get('n_test_patients')} | shuffle={sh.get('auc')} ({time.time()-t:.0f}s)")
    # 양성대조 게이트
    pc=cfg["positive_control"]
    if pc and pc in results["endpoints"]:
        pca=results["endpoints"][pc].get("real",{}).get("auc")
        gate = (pca is not None and pca>=0.75)
        results["positive_control_gate"]={"endpoint":pc,"auc":pca,"pass":gate,
            "note":"histology(형태학) AUROC>=0.75 = H&E/파이프라인 정상. 미달이면 MIL 고장 의심."}
        print(f"  [양성대조 {pc}] AUROC={pca} → {'PASS' if gate else 'FAIL(파이프라인 점검)'}")
    if not a.smoke:
        results["cost_of_substitution"]=cost_routing(a.cancer, results["endpoints"], labels, split)
        print("  cost:", json.dumps(results["cost_of_substitution"]["per_axis"], ensure_ascii=False))
    out=HERE/a.cancer/"full"/("mil_cost_smoke.json" if a.smoke else "mil_cost_results.json")
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"  wrote {out}")

if __name__=="__main__":
    main()

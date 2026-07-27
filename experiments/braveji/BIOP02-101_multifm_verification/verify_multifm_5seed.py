import json, subprocess, statistics, math
def sh(p):
    r=subprocess.run(['git','show',f'pr73:{p}'],capture_output=True,text=True)
    return r.stdout if r.returncode==0 else None

files=[
 ('LUNG_NSCLC','uni2h','experiments/crosscancer/LUNG_NSCLC/full/shuffle_null_robustness_uni2h.json'),
 ('LUNG_NSCLC','virchow2','experiments/crosscancer/LUNG_NSCLC/full/shuffle_null_robustness_virchow2.json'),
 ('COLORECTAL','uni2h','experiments/crosscancer/COLORECTAL/full/shuffle_null_robustness_uni2h.json'),
 ('COLORECTAL','virchow2','experiments/crosscancer/COLORECTAL/full/shuffle_null_robustness_virchow2.json'),
 ('HNSC','uni2h','experiments/crosscancer/HEADNECK_HNSC/full/shuffle_null_robustness_uni2h.json'),
 ('HNSC','virchow2','experiments/crosscancer/HEADNECK_HNSC/full/shuffle_null_robustness_virchow2.json'),
 ('HNSC-HPV','uni2h','experiments/crosscancer/HEADNECK_HNSC/full/shuffle_null_robustness_uni2h_hpv.json'),
 ('HNSC-HPV','virchow2','experiments/crosscancer/HEADNECK_HNSC/full/shuffle_null_robustness_virchow2_hpv.json'),
]
def evalrec(name,fm,raw):
    d=json.loads(raw)
    # find per-endpoint records: look for keys with real auroc + null list
    def walk(o,path=''):
        out=[]
        if isinstance(o,dict):
            keys=set(o.keys())
            realk=[k for k in keys if 'real' in k.lower() and ('auroc' in k.lower() or 'auc' in k.lower())]
            nullk=[k for k in keys if 'null' in k.lower() and isinstance(o[k],list)]
            if realk and nullk:
                out.append((path.strip('.'),o))
            for k,v in o.items(): out+=walk(v,path+k+'.')
        elif isinstance(o,list):
            for i,v in enumerate(o): out+=walk(v,path+f'[{i}].')
        return out
    recs=walk(d)
    if not recs:
        # maybe flat: print top keys
        print(f'  [{name}/{fm}] 구조 미상 — top keys: {list(d.keys())[:8]}')
        return
    for path,o in recs:
        rk=[k for k in o if 'real' in k.lower() and ('auroc' in k.lower() or 'auc' in k.lower())][0]
        nk=[k for k in o if 'null' in k.lower() and isinstance(o[k],list)][0]
        real=o[rk]; nulls=[x for x in o[nk] if isinstance(x,(int,float))]
        if not nulls: continue
        mu=statistics.mean(nulls); sd=statistics.stdev(nulls) if len(nulls)>1 else 0
        thr=mu+2*sd
        ok = real>thr
        print(f'  [{name}/{fm}] {path or rk}: real={real:.4f} null_mean={mu:.4f} sd={sd:.4f} thr(μ+2σ)={thr:.4f} → {"PASS" if ok else "FAIL"} (n_null={len(nulls)})')

for name,fm,p in files:
    raw=sh(p)
    if raw is None: print(f'  [{name}/{fm}] 파일 없음'); continue
    evalrec(name,fm,raw)

import csv, numpy as np
rows=list(csv.DictReader(open('/tmp/pam50_route.csv')))
case=np.array([r['case_id'] for r in rows])
axis=np.array([r['true_axis'] for r in rows])
cost=np.array([float(r['cost']) for r in rows])
n_slides=len(rows); n_pat=len(set(case))
print(f"입력: {n_slides} 슬라이드 / {n_pat} 환자 ({n_slides/n_pat:.2f} 슬/환)")
print(f"  축 분포: {dict((a,int((axis==a).sum())) for a in set(axis))}")

# point estimate
ct = cost[axis=="antiHER2"].mean() - cost[axis=="endocrine"].mean()
# patient-cluster bootstrap (script와 동일: seed42, default_rng, choice(pats,len,replace))
B,SEED=5000,42
pats=sorted(set(case)); idx_by={p:np.where(case==p)[0] for p in pats}
rng=np.random.default_rng(SEED); bh=[]; bax={a:[] for a in ["endocrine","antiHER2","chemo"]}
for _ in range(B):
    pick=rng.choice(pats,len(pats),replace=True)
    i=np.concatenate([idx_by[p] for p in pick]); a2=axis[i]
    if (a2=="antiHER2").sum()==0 or (a2=="endocrine").sum()==0: continue
    bh.append(cost[i][a2=="antiHER2"].mean()-cost[i][a2=="endocrine"].mean())
    for a in bax:
        if (a2==a).any(): bax[a].append(cost[i][a2==a].mean())
lo,hi=np.percentile(bh,[2.5,97.5])
print(f"\n[braveji 재계산] headline={ct:.4f}  patient-CI=[{lo:.4f}, {hi:.4f}]  0배제={lo>0}")
for a in bax:
    l,h=np.percentile(bax[a],[2.5,97.5]); print(f"  per_axis {a:10s} CI=[{l:.4f}, {h:.4f}]")
print(f"\n[커밋값 대조] headline=0.3396  patient-CI=[0.2508, 0.4254]  n_slides=382 n_patients=115")

import numpy as np, csv, json
from sklearn.metrics import roc_auc_score
CLS=['LumA','LumB','Basal','HER2']

def load_csv(p):
    rows=list(csv.DictReader(open(p)))
    y=np.array([CLS.index(r['true_label']) for r in rows])
    P=np.array([[float(r[f'proba_{c}']) for c in CLS] for r in rows])
    ids=[r['case_id'] for r in rows]
    return ids,y,P

def macro_auc(y,P):
    return roc_auc_score(y,P,multi_class='ovr',average='macro')

for tag,csvp,npz in [
  ('EXTERNAL(CPTAC)','experiments/sjpark/pam50_uni_v1_4class_baselines/mean_embed_proba_external_cptac.csv',
   'experiments/sjpark/pam50_clam_mb_uni_v1_4class/predictions_ext.npz'),
  ('INTERNAL(val)','experiments/sjpark/pam50_uni_v1_4class_baselines/mean_embed_proba_internal_val.csv',
   'experiments/sjpark/pam50_clam_mb_uni_v1_4class/predictions.npz'),
]:
    print(f'\n══ {tag} ══')
    ids,y_me,P_me=load_csv(csvp)
    d=np.load(npz,allow_pickle=True)
    print('  npz keys:',list(d.keys()))
    # find clam proba + labels
    P_cl=None;y_cl=None
    for k in d.keys():
        a=d[k]
        if a.ndim==2 and a.shape[1]==4 and a.shape[0]==len(y_me): P_cl=a
        elif a.ndim==1 and a.shape[0]==len(y_me) and a.dtype.kind in 'iu': y_cl=a
    if P_cl is None:
        print('  ! CLAM proba(N,4) 미발견 shapes:',{k:d[k].shape for k in d.keys()}); continue
    if y_cl is None: y_cl=y_me
    print(f'  n={len(y_me)}  label 일치: {int((y_cl==y_me).sum())}/{len(y_me)}')
    a_cl=macro_auc(y_cl,P_cl); a_me=macro_auc(y_me,P_me)
    print(f'  재계산 CLAM     AUC = {a_cl:.4f}')
    print(f'  재계산 mean_emb AUC = {a_me:.4f}')
    print(f'  재계산 diff         = {a_cl-a_me:+.4f}')
    # paired bootstrap
    rng=np.random.default_rng(42); diffs=[]
    n=len(y_me)
    for _ in range(2000):
        idx=rng.integers(0,n,n)
        if len(np.unique(y_me[idx]))<4: continue
        diffs.append(macro_auc(y_cl[idx],P_cl[idx])-macro_auc(y_me[idx],P_me[idx]))
    diffs=np.array(diffs)
    lo,hi=np.percentile(diffs,[2.5,97.5])
    print(f'  paired CI95         = [{lo:.4f}, {hi:.4f}]  (n_boot={len(diffs)})')
    print(f'  CI가 0 배제         = {"YES" if lo>0 else "NO"}')

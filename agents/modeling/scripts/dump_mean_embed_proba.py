"""braveji 요청 — PAM50 4-class mean_embed baseline의 per-patient 예측확률 산출·저장.
paired 검정(+0.165)의 형식 근거. 내부(TCGA val) + 외부(CPTAC) 둘 다."""
import csv, json
import numpy as np
from sklearn.linear_model import LogisticRegression

PAM50_MAP4 = {"luma":0,"lumb":1,"basal":2,"her2":3}  # §4: Normal 제외
CLASSES = ["LumA","LumB","Basal","HER2"]
TCGA="/workspace/data/cache/biop02/embedding_manifest_uni.csv"
CPTAC="/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"
OUT="/workspace/agents/modeling/experiments/sjpark/pam50_uni_v1_4class_baselines"

def load(mani, split):
    rows=[]
    for r in csv.DictReader(open(mani)):
        if r.get("split","").strip().lower()!=split: continue
        lab=r.get("pam50","").strip().lower()
        if lab not in PAM50_MAP4: continue
        rows.append(r)
    return rows

tr=load(TCGA,"train")
Xtr=np.stack([np.load(r["embedding_path"]).mean(0) for r in tr])
ytr=np.array([PAM50_MAP4[r["pam50"].strip().lower()] for r in tr])
clf=LogisticRegression(max_iter=1000, random_state=42).fit(Xtr,ytr)

def dump(rows, tag):
    proba=np.zeros((len(rows),4),np.float32)
    P=clf.predict_proba(np.stack([np.load(r["embedding_path"]).mean(0) for r in rows]))
    for i,c in enumerate(clf.classes_): proba[:,c]=P[:,i]
    path=f"{OUT}/mean_embed_proba_{tag}.csv"
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["slide_id","case_id","true_label"]+[f"proba_{c}" for c in CLASSES])
        for r,pr in zip(rows,proba):
            w.writerow([r["slide_id"],r["case_id"],CLASSES[PAM50_MAP4[r["pam50"].strip().lower()]]]+[round(float(x),6) for x in pr])
    print(f"Saved {path} ({len(rows)} rows)")
    return path

dump(load(TCGA,"val"), "internal_val")
dump(load(CPTAC,"cptac_external"), "external_cptac")
print("done — mean_embed per-patient proba (paired 검정 형식 근거)")

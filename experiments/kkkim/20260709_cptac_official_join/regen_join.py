import csv, os
STAGE="experiments/kkkim/20260709_cptac_official_join"
temp=f"{STAGE}/embedding_manifest_cptac_uni.temp395.csv"
offl=f"{STAGE}/cptac_brca_clinical_labels_v1.csv"
out =f"{STAGE}/embedding_manifest_cptac_uni_v1.csv"

# official labels by case_id
off={}
with open(offl) as f:
    for r in csv.DictReader(f):
        off[r["case_id"]]=r

rows=list(csv.DictReader(open(temp)))
outcols=["slide_id","case_id","embedding_path","embedding_shape","embedding_model",
         "er","pr","her2","pam50","has_er","has_pr","has_her2","has_pam50","has_labels","split"]

def hasflag(v): return "1" if str(v).strip() not in ("","0") else "0"

n_slides=len(rows); n_off=0; n_haslabels=0
old_labeled=0
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=outcols); w.writeheader()
    for r in rows:
        cid=r["case_id"]
        # old temp labeled?
        if any(str(r.get(k,"")).strip() for k in ("er","pr","her2","pam50")): old_labeled+=1
        o=off.get(cid)
        nr={k:r.get(k,"") for k in ("slide_id","case_id","embedding_path","embedding_shape","embedding_model","split")}
        if o:
            n_off+=1
            nr["er"]=o["er_status"]; nr["pr"]=o["pr_status"]; nr["her2"]=o["her2_status"]; nr["pam50"]=o["pam50"]
            nr["has_er"]=o["has_er"]; nr["has_pr"]=o["has_pr"]; nr["has_her2"]=o["has_her2"]; nr["has_pam50"]=o["has_pam50"]
            nr["has_labels"]=o["has_labels"]
            if o["has_labels"]=="1": n_haslabels+=1
        else:
            for k in ("er","pr","her2","pam50","has_er","has_pr","has_her2","has_pam50","has_labels"): nr[k]=""
        w.writerow(nr)
print(f"CPTAC 슬라이드 총계        : {n_slides}")
print(f"공식 라벨표에 case 매칭     : {n_off}/{n_slides}")
print(f"has_labels=1 (4종 라벨 가용): {n_haslabels}/{n_slides}")
print(f"[참고] 임시본에서 라벨 채워졌던 슬라이드: {old_labeled}/{n_slides}")
print(f"출력: {out}")

#!/usr/bin/env python3
"""
Cross-cancer site-disjoint patient-level split (BRCA split_policy_v0 로직 재사용, GPU 0).

- 단위=환자(case_id). site=TCGA TSS code(case_id[5:7]). 한 site는 한 fold에만(Howard).
- greedy LPT: 큰 site부터 가장 빈 fold에 통째 배정(70/15/15). RNG 없음(해시 tie-break) → 재현.
- 검증: patient-overlap==0, site-disjoint==True. split_hash=sha256(sorted (case_id,split))[:16].
입력: <cancer>/full/patient_labels.csv (case_id). 출력: <cancer>/full/split.csv + split_meta.json.
"""
import csv, json, hashlib
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).parent
RATIOS = (0.70, 0.15, 0.15); SEED = 42

def tss(case_id):
    p = case_id.split("-")
    return p[1] if len(p) >= 2 else "NA"

def assign(case_ids):
    site_cases = defaultdict(set)
    for c in case_ids: site_cases[tss(c)].add(c)
    sites = sorted(site_cases.items(), key=lambda x: (-len(x[1]),
                   hashlib.sha256(f"{SEED}:{x[0]}".encode()).hexdigest()))
    total = sum(len(v) for _, v in sites) or 1
    target = {"train":RATIOS[0]*total, "val":RATIOS[1]*total, "test":RATIOS[2]*total}
    assigned = {"train":0.0,"val":0.0,"test":0.0}; site_fold = {}
    for s, cases in sites:
        fold = max(("train","val","test"), key=lambda f: target[f]-assigned[f])
        site_fold[s] = fold; assigned[fold] += len(cases)
    return {c: site_fold[tss(c)] for c in case_ids}

def split_hash(fold_map):
    items = sorted(fold_map.items())
    return hashlib.sha256(repr(items).encode()).hexdigest()[:16]

def run(cancer):
    lab = HERE / cancer / "full" / "patient_labels.csv"
    if not lab.exists():
        print(f"[SKIP] {cancer}: patient_labels.csv 없음"); return
    case_ids = sorted({r["case_id"] for r in csv.DictReader(open(lab)) if r["case_id"]})
    fold = assign(case_ids)
    # 검증
    site_folds = defaultdict(set)
    for c, f in fold.items(): site_folds[tss(c)].add(f)
    bad_site = [s for s, fs in site_folds.items() if len(fs) > 1]
    assert not bad_site, f"SITE LEAK {bad_site[:5]}"
    dist = Counter(fold.values())
    out = HERE / cancer / "full" / "split.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case_id","tss_code","split"])
        for c in case_ids: w.writerow([c, tss(c), fold[c]])
    meta = {"cancer":cancer, "policy":"site-disjoint patient-level (split_policy_v0 로직)",
            "split_hash":split_hash(fold), "seed":SEED, "n_patients":len(case_ids),
            "n_sites":len(site_folds), "dist":dict(dist), "site_disjoint":True, "patient_overlap":0}
    (HERE / cancer / "full" / "split_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"{cancer}: {len(case_ids)}환자 {len(site_folds)}site  dist={dict(dist)}  "
          f"site-disjoint OK  hash={meta['split_hash']}")

if __name__ == "__main__":
    for c in ["LUNG_NSCLC","COLORECTAL"]:
        run(c)

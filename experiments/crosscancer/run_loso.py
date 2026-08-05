#!/usr/bin/env python3
"""BIOP02-121 MUST #2 강화 — 전면 LOSO(leave-one-site-out) 재학습 러너 [초안, braveji 검토용].

목적: #2 site 감사의 within-site AUROC(=LOSO 근사)를 정본 LOSO로 격상한다.
각 제출기관(TSS site)을 하나씩 test로 빼고 나머지 전 site로 CLAM을 재학습해,
그 site 환자를 예측한다. 모든 site를 한 번씩 빼면 각 환자는 "자기 site를 한 번도
못 본 모델"에게 정확히 한 번 예측된다 → 이 pooled AUROC가 정본 LOSO 추정이다.
pooled site-disjoint(기존 real.auc)와 대조해 site 일반화 저하를 계량한다(BIOP02-122 (B) 근거).

설계 핵심(하네스 재사용): run_mil_cost.train_eval은 슬라이드의 s["split"] 필드로
train("train") vs holdout("val"+"test")을 가른다. 따라서 **run_mil_cost.py를 수정하지 않고**
매 fold마다 slides의 split을 재지정하면 된다 — site S 슬라이드→"test", 그 외→"train".
train_eval이 train에서 15%를 dev(early-stop)로 자동 분리하므로 leakage 없음.

⚠️ 이 파일은 초안이다. 실제 GPU 재학습 launch는 braveji 슬롯 확보 + 하네스 관례 검토 후.
    --dry-run은 GPU/torch 없이 fold 계획만 출력(지금 검증용).

사용:
  python run_loso.py --cancer HEADNECK_HNSC --endpoints hpv_pos --dry-run           # 계획만(GPU 0)
  python run_loso.py --cancer HEADNECK_HNSC --endpoints hpv_pos --device cuda:0      # 실제 재학습
기본 endpoint = 각 암종 powered 앵커(n_pos>=25). exploratory는 소표본이라 제외(--endpoints로 강제 가능).
"""
import argparse, json, csv, os, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_mil_cost as R  # load_meta, train_eval, patient_agg, bootstrap_auc, FM_SPEC, CANCER_CFG, FEATURE_DIM

POWER_MIN_POS = 25
# 암종별 powered 앵커(검정력 있는 것만 LOSO 대상; 근거 = site_audit / operating_point 결과)
DEFAULT_ANCHORS = {
    "HEADNECK_HNSC": ["hpv_pos", "grade_high"],
    "LUNG_NSCLC": ["histology_lusc"],
    "GASTRIC_STAD": ["lauren_diffuse"],
    "COLORECTAL": [],   # BRAF 등 전부 exploratory(n_pos<25) → 기본 제외
}

def tss(case_id):
    parts = case_id.split('-')
    return parts[1] if case_id.startswith('TCGA') and len(parts) > 1 else 'NA'

def label_of(labels, case_id, ep):
    v = labels.get(case_id, {}).get(ep, "")
    return int(v) if v != "" else None

def fold_plan(slides, labels, ep):
    """endpoint별 site fold 계획: 라벨 있는 환자만, site별 n/n_pos."""
    per = defaultdict(lambda: {"cases": set(), "pos": 0})
    for s in slides:
        y = label_of(labels, s["case_id"], ep)
        if y is None:
            continue
        st = per[tss(s["case_id"])]
        if s["case_id"] not in st["cases"]:
            st["cases"].add(s["case_id"]); st["pos"] += y
    plan = {site: {"n_cases": len(v["cases"]), "n_pos": v["pos"]} for site, v in per.items()}
    total_pos = sum(v["n_pos"] for v in plan.values())
    total_cases = sum(v["n_cases"] for v in plan.values())
    return plan, total_cases, total_pos

def reassign_split(slides, holdout_site):
    """site S 슬라이드→'test', 그 외→'train'. (train_eval이 train에서 dev 자동분리)"""
    out = []
    for s in slides:
        s2 = dict(s)
        s2["split"] = "test" if tss(s["case_id"]) == holdout_site else "train"
        out.append(s2)
    return out

def run_endpoint_loso(slides, labels, ep, device, fm, epochs, seed):
    plan, tot_cases, tot_pos = fold_plan(slides, labels, ep)
    sites = sorted(plan)
    all_recs = []          # pooled: 각 환자 1회(자기 site 제외 모델 예측)
    per_site = {}
    for site in sites:
        held = plan[site]
        # 학습쪽(나머지)에 두 클래스가 있어야 train_eval이 돈다; 없으면 skip(그 site는 pooled서 빠짐)
        other_pos = tot_pos - held["n_pos"]; other_neg = (tot_cases - held["n_cases"]) - other_pos
        if other_pos < 1 or other_neg < 1 or held["n_cases"] < 1:
            per_site[site] = {"status": "skip(학습쪽 단일클래스 or holdout 0)", **held}
            continue
        s_fold = reassign_split(slides, site)
        recs, dev_auc = R.train_eval(s_fold, labels, ep, device, shuffle=False, epochs=epochs, seed=seed)
        if not recs:
            per_site[site] = {"status": "skip(train_eval None)", **held}
            continue
        pa = R.patient_agg(recs)
        y = [v[1] for v in pa.values()]; p = [v[0] for v in pa.values()]
        auc, lo, hi = R.bootstrap_auc(y, p) if len(set(y)) > 1 else (None, None, None)
        per_site[site] = {"status": "ok", "site_auc": auc, "ci95": [lo, hi],
                          "n": len(pa), "n_pos": int(sum(y)), "dev_auc": dev_auc}
        all_recs.extend(recs)
    # pooled LOSO
    ppa = R.patient_agg(all_recs)
    py = [v[1] for v in ppa.values()]; pp = [v[0] for v in ppa.values()]
    pooled_auc, plo, phi = R.bootstrap_auc(py, pp) if len(set(py)) > 1 else (None, None, None)
    return dict(endpoint=ep, n_sites=len(sites), n_sites_trained=sum(1 for v in per_site.values() if v.get("status") == "ok"),
                pooled_loso_auc=pooled_auc, pooled_ci95=[plo, phi],
                n_pooled=len(ppa), n_pos_pooled=int(sum(py)), per_site=per_site)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True,
                    help="<cancer>/full/{split.csv,patient_labels.csv,embeddings} 필요(CANCER_CFG 무관 — load_meta만 씀)")
    ap.add_argument("--endpoints", default="", help="쉼표구분. 비우면 powered 앵커 기본값")
    ap.add_argument("--fm", default="uni", choices=list(R.FM_SPEC))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true", help="fold 계획만(GPU/torch 불요)")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(HERE, a.cancer, "full", "split.csv")):
        print(f"[에러] {a.cancer}/full/split.csv 없음 — 암종 경로 확인."); return
    R.FEATURE_DIM = R.FM_SPEC[a.fm]["dim"]
    labels, split, slides = R.load_meta(a.cancer, a.fm)
    eps = [e.strip() for e in a.endpoints.split(",") if e.strip()] or DEFAULT_ANCHORS.get(a.cancer, [])
    if not eps:
        print(f"[{a.cancer}] 기본 powered 앵커 없음 — --endpoints로 지정 필요(exploratory 포함 시)."); return
    print(f"{a.cancer} | fm={a.fm}(dim={R.FEATURE_DIM}) | {len(slides)} 슬라이드 | endpoints={eps} | dry_run={a.dry_run}")

    if a.dry_run:
        for ep in eps:
            plan, tc, tp = fold_plan(slides, labels, ep)
            trainable = sum(1 for s, v in plan.items() if (tp - v["n_pos"]) >= 1 and (tc - v["n_cases"]) - (tp - v["n_pos"]) >= 1 and v["n_cases"] >= 1)
            print(f"\n[{ep}] 라벨환자 {tc} (양성 {tp}) · site {len(plan)}개 · 학습가능 fold {trainable}개")
            print(f"   {'site':6s} {'n_cases':>7s} {'n_pos':>5s}  (fold=이 site를 test로 hold)")
            for s in sorted(plan, key=lambda x: -plan[x]["n_cases"]):
                v = plan[s]; print(f"   {s:6s} {v['n_cases']:7d} {v['n_pos']:5d}")
            print(f"   ⇒ 예상 재학습 횟수 = {trainable} (각 CLAM {a.epochs}ep, early-stop). pooled 환자 = {tc}.")
        print("\n[dry-run] 실제 재학습 없음. GPU 슬롯 확보 후 --device로 launch.")
        return

    # 실제 재학습 (GPU)
    results = {"cancer": a.cancer, "fm": a.fm, "analysis": "leave_one_site_out",
               "claim_level": "hypothesis_only", "critic_status": "pending", "seed": a.seed, "endpoints": {}}
    for ep in eps:
        t = time.time()
        r = run_endpoint_loso(slides, labels, ep, a.device, a.fm, a.epochs, a.seed)
        results["endpoints"][ep] = r
        print(f"  {ep}: pooled LOSO AUC={r['pooled_loso_auc']} CI{r['pooled_ci95']} "
              f"(sites {r['n_sites_trained']}/{r['n_sites']}, n+={r['n_pos_pooled']}/{r['n_pooled']}) {time.time()-t:.0f}s")
    outdir = os.path.join(HERE, a.cancer, "full")
    outp = os.path.join(outdir, f"loso_results_{a.fm}.json")
    json.dump(results, open(outp, "w"), indent=2, ensure_ascii=False)
    print(f"[written] {outp}")

if __name__ == "__main__":
    main()

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

braveji 검토 보완 4건 반영(BIOP02-121 #16:25, 서명 전 조건):
  ① 분모 매칭 — skip site로 pooled 분모가 기존 real.auc와 달라짐 → excluded_sites·coverage 기록 +
     기존 site-disjoint real 예측을 LOSO 커버 case로 제한한 matched_real_auc 병기(mil_cost_results 있으면).
  ② ≥3 seed — 단일 seed CI는 재학습 확률성 미포함 → --seeds(기본 42,1,2)로 per-seed + mean±sd.
  ③ shuffle-null — LOSO 경로에도 shuffle-null 추가(각 seed 라벨 셔플 재학습 → pooled null AUROC).
  ④ 비-TCGA assert — 'NA'(TSS 없는 case_id)는 단일 fold로 뭉치지 않게 site fold에서 제외 + assert(--allow-na로 우회).
⚠️ 비용: ②×③으로 재학습이 (fold × seed수 × 2)로 늘어난다(예 HNSC hpv = 25×3×2 = 150회). launch는
    powered 1앵커(hpv)부터 + GPU 슬롯 조율(#biop02-alerts) 후. --seeds로 축소 가능(1차는 --seeds 42도).

사용:
  python run_loso.py --cancer HEADNECK_HNSC --endpoints hpv_pos --dry-run           # 계획만(GPU 0)
  python run_loso.py --cancer HEADNECK_HNSC --endpoints hpv_pos --device cuda:0      # 실제 재학습(seeds 42,1,2 + null)
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

def matched_real_auc(cancer, fm, ep, covered_cases):
    """보완①: pooled LOSO가 skip site로 분모가 달라지므로, 기존 site-disjoint real 예측을
    LOSO가 실제로 커버한 case_id로 제한해 '동일 분모' real AUROC를 병기한다.
    출처 = <cancer>/full/mil_cost_results{,_<fm>}.json 의 patient_proba/patient_true(홀드아웃 한정).
    반환 None = 원자료 없음/교집합 부족."""
    suf = "" if fm == "uni" else f"_{fm}"
    p = os.path.join(HERE, cancer, "full", f"mil_cost_results{suf}.json")
    if not os.path.exists(p):
        return None
    try:
        e = json.load(open(p)).get("endpoints", {}).get(ep, {})
        pr, tr = e.get("patient_proba"), e.get("patient_true")
        if not pr or not tr:
            return None
        keys = [k for k in pr if k in covered_cases and k in tr]
        y = [int(tr[k]) for k in keys]; pp = [float(pr[k]) for k in keys]
        if len(set(y)) < 2:
            return None
        auc, lo, hi = R.bootstrap_auc(y, pp)
        return {"matched_real_auc": auc, "ci95": [lo, hi], "n": len(keys), "n_pos": int(sum(y)),
                "note": "기존 site-disjoint real 예측을 LOSO 커버 case로 제한(동일 분모 대조; 홀드아웃 한정이라 n≤pooled)"}
    except Exception:
        return None


def one_loso_pass(slides, labels, ep, device, fm, epochs, seed, shuffle, sites, plan, tot_cases, tot_pos):
    """LOSO 한 바퀴(전 fold). shuffle=True면 shuffle-null(보완③). 'NA' site는 제외(보완④)."""
    all_recs, per_site, excluded = [], {}, []
    for site in sites:
        held = plan[site]
        other_pos = tot_pos - held["n_pos"]; other_neg = (tot_cases - held["n_cases"]) - other_pos
        if other_pos < 1 or other_neg < 1 or held["n_cases"] < 1:
            per_site[site] = {"status": "skip(학습쪽 단일클래스 or holdout 0)", **held}
            excluded.append(site); continue
        s_fold = reassign_split(slides, site)
        recs, dev_auc = R.train_eval(s_fold, labels, ep, device, shuffle=shuffle, epochs=epochs, seed=seed)
        if not recs:
            per_site[site] = {"status": "skip(train_eval None)", **held}
            excluded.append(site); continue
        pa = R.patient_agg(recs)
        y = [v[1] for v in pa.values()]; p = [v[0] for v in pa.values()]
        auc, lo, hi = R.bootstrap_auc(y, p) if len(set(y)) > 1 else (None, None, None)
        per_site[site] = {"status": "ok", "site_auc": auc, "ci95": [lo, hi],
                          "n": len(pa), "n_pos": int(sum(y)), "dev_auc": dev_auc}
        all_recs.extend(recs)
    ppa = R.patient_agg(all_recs)
    py = [v[1] for v in ppa.values()]; pp = [v[0] for v in ppa.values()]
    pooled_auc, plo, phi = R.bootstrap_auc(py, pp) if len(set(py)) > 1 else (None, None, None)
    covered = set(ppa.keys())
    return {"pooled_loso_auc": pooled_auc, "pooled_ci95": [plo, phi], "n_pooled": len(ppa),
            "n_pos_pooled": int(sum(py)), "per_site": per_site, "excluded_sites": excluded,
            "covered_cases": covered}


def run_endpoint_loso(slides, labels, ep, device, fm, epochs, seeds, cancer):
    plan, tot_cases, tot_pos = fold_plan(slides, labels, ep)
    # 보완④: 'NA'(비-TCGA case_id) fold는 실제 site가 아니므로 제외 + 계상
    n_na = plan.get("NA", {}).get("n_cases", 0)
    sites = sorted(s for s in plan if s != "NA")
    # 보완②: 다중 seed(재학습 확률성 포착). real + shuffle-null(보완③) 각각.
    real = [one_loso_pass(slides, labels, ep, device, fm, epochs, s, False, sites, plan, tot_cases, tot_pos) for s in seeds]
    null = [one_loso_pass(slides, labels, ep, device, fm, epochs, s, True,  sites, plan, tot_cases, tot_pos) for s in seeds]
    real_aucs = [r["pooled_loso_auc"] for r in real if r["pooled_loso_auc"] is not None]
    null_aucs = [r["pooled_loso_auc"] for r in null if r["pooled_loso_auc"] is not None]
    covered = real[0]["covered_cases"] if real else set()
    return dict(
        endpoint=ep, n_sites=len(sites), n_sites_trained=sum(1 for v in real[0]["per_site"].values() if v.get("status") == "ok") if real else 0,
        seeds=list(seeds),
        pooled_loso_auc_mean=round(float(np.mean(real_aucs)), 4) if real_aucs else None,     # 보완②
        pooled_loso_auc_per_seed=[round(a, 4) for a in real_aucs],
        pooled_loso_auc_sd=round(float(np.std(real_aucs, ddof=1)), 4) if len(real_aucs) > 1 else None,
        shuffle_null_loso_auc_mean=round(float(np.mean(null_aucs)), 4) if null_aucs else None,  # 보완③
        shuffle_null_loso_auc_per_seed=[round(a, 4) for a in null_aucs],
        n_pooled=real[0]["n_pooled"] if real else 0, n_pos_pooled=real[0]["n_pos_pooled"] if real else 0,
        excluded_sites=real[0]["excluded_sites"] if real else [],                              # 보완①(분모 투명)
        coverage=round(len(covered) / tot_cases, 3) if tot_cases else None,
        matched_real=matched_real_auc(cancer, fm, ep, covered),                                # 보완①(동일 분모 real)
        n_na_nonTCGA=n_na,                                                                       # 보완④
        per_site_seed0=real[0]["per_site"] if real else {})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True,
                    help="<cancer>/full/{split.csv,patient_labels.csv,embeddings} 필요(CANCER_CFG 무관 — load_meta만 씀)")
    ap.add_argument("--endpoints", default="", help="쉼표구분. 비우면 powered 앵커 기본값")
    ap.add_argument("--fm", default="uni", choices=list(R.FM_SPEC))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--seeds", default="42,1,2", help="보완②: 쉼표구분 ≥3 seed(재학습 확률성). 기본 42,1,2")
    ap.add_argument("--allow-na", action="store_true", help="비-TCGA(NA) case가 있어도 진행(보완④ assert 우회)")
    ap.add_argument("--dry-run", action="store_true", help="fold 계획만(GPU/torch 불요)")
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    if not os.path.exists(os.path.join(HERE, a.cancer, "full", "split.csv")):
        print(f"[에러] {a.cancer}/full/split.csv 없음 — 암종 경로 확인."); return
    R.FEATURE_DIM = R.FM_SPEC[a.fm]["dim"]
    labels, split, slides = R.load_meta(a.cancer, a.fm)
    eps = [e.strip() for e in a.endpoints.split(",") if e.strip()] or DEFAULT_ANCHORS.get(a.cancer, [])
    if not eps:
        print(f"[{a.cancer}] 기본 powered 앵커 없음 — --endpoints로 지정 필요(exploratory 포함 시)."); return
    print(f"{a.cancer} | fm={a.fm}(dim={R.FEATURE_DIM}) | {len(slides)} 슬라이드 | endpoints={eps} | seeds={seeds} | dry_run={a.dry_run}")

    # 보완④: 비-TCGA(NA) case_id assert — 'NA' 단일 fold로 뭉치는 것을 차단
    n_na_total = sum(1 for s in {sl["case_id"] for sl in slides} if tss(s) == "NA")
    if n_na_total > 0:
        msg = f"⚠️ 비-TCGA(NA) case_id {n_na_total}개 — LOSO site fold에서 제외됨(TSS 없음)."
        if not a.allow_na:
            print(f"[assert 실패] {msg} 의도된 것이면 --allow-na. (보완④)"); return
        print(f"[경고] {msg} --allow-na로 진행. (보완④)")

    if a.dry_run:
        for ep in eps:
            plan, tc, tp = fold_plan(slides, labels, ep)
            real_sites = [s for s in plan if s != "NA"]
            trainable = sum(1 for s in real_sites if (tp - plan[s]["n_pos"]) >= 1 and (tc - plan[s]["n_cases"]) - (tp - plan[s]["n_pos"]) >= 1 and plan[s]["n_cases"] >= 1)
            print(f"\n[{ep}] 라벨환자 {tc} (양성 {tp}) · site {len(real_sites)}개(NA 제외) · 학습가능 fold {trainable}개")
            print(f"   {'site':6s} {'n_cases':>7s} {'n_pos':>5s}  (fold=이 site를 test로 hold)")
            for s in sorted(real_sites, key=lambda x: -plan[x]["n_cases"]):
                v = plan[s]; print(f"   {s:6s} {v['n_cases']:7d} {v['n_pos']:5d}")
            if "NA" in plan:
                print(f"   {'NA':6s} {plan['NA']['n_cases']:7d} {plan['NA']['n_pos']:5d}  ← 비-TCGA, fold 제외(보완④)")
            print(f"   ⇒ 재학습 = {trainable} fold × {len(seeds)} seed(real) + × {len(seeds)}(shuffle-null) = {trainable*len(seeds)*2}회 (각 {a.epochs}ep).")
        print(f"\n[dry-run] 실제 재학습 없음. 보완②≥3seed·③shuffle-null·④NA제외 반영. GPU 슬롯 확보 후 --device로 launch.")
        return

    # 실제 재학습 (GPU)
    results = {"cancer": a.cancer, "fm": a.fm, "analysis": "leave_one_site_out",
               "claim_level": "hypothesis_only", "critic_status": "pending", "seeds": seeds,
               "n_na_nonTCGA_excluded": n_na_total, "endpoints": {}}
    for ep in eps:
        t = time.time()
        r = run_endpoint_loso(slides, labels, ep, a.device, a.fm, a.epochs, seeds, a.cancer)
        results["endpoints"][ep] = r
        mr = r.get("matched_real") or {}
        print(f"  {ep}: LOSO pooled AUC(mean over {len(seeds)}seed)={r['pooled_loso_auc_mean']} "
              f"±{r['pooled_loso_auc_sd']} / shuffle-null={r['shuffle_null_loso_auc_mean']} "
              f"| matched real={mr.get('matched_real_auc')}(n={mr.get('n')}) "
              f"| coverage={r['coverage']} excl_sites={len(r['excluded_sites'])} NA={r['n_na_nonTCGA']} {time.time()-t:.0f}s")
    outdir = os.path.join(HERE, a.cancer, "full")
    outp = os.path.join(outdir, f"loso_results_{a.fm}.json")
    json.dump(results, open(outp, "w"), indent=2, ensure_ascii=False, default=lambda o: list(o) if isinstance(o, set) else str(o))
    print(f"[written] {outp}")

if __name__ == "__main__":
    main()

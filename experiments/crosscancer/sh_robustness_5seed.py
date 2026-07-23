#!/usr/bin/env python3
"""BLOCKER-1 remediation: sealed-forward 전 endpoint 5-seed shuffle-null 강건성.

기존 run_mil_cost.train_eval을 그대로 호출(코드경로 불변 → seed42 real이 정본 재현).
각 endpoint: real(seed42) + shuffle-null 5 seed [42,1,2,3,4].
기준(대장과 동일): real_auroc > null_mean + 2*null_sd(ddof=1) → 미달=우연배제 강건성 미확보('실패', weak≠zero).

사용:
  python sh_robustness_5seed.py --cancer LUNG_NSCLC --device cuda:0
  python sh_robustness_5seed.py --cancer LUNG_NSCLC --endpoints histology_lusc --real-only   # 스모크(정본 재현 확인)
출력: <cancer>/full/shuffle_null_robustness.json (UNI) · shuffle_null_robustness_<fm>.json (다중 FM)
"""
import json, sys, time, argparse
from pathlib import Path
import numpy as np
import run_mil_cost as m

HERE = Path(__file__).parent
SEEDS = [42, 1, 2, 3, 4]
ENDPOINTS = {
    "LUNG_NSCLC":    ["histology_lusc", "egfr_activating", "kras_g12c"],
    "GASTRIC_STAD":  ["lauren_diffuse", "msi_h", "erbb2_amp", "ebv"],
    "HEADNECK_HNSC": ["hpv_pos", "egfr_amp", "grade_high"],
    # COLORECTAL: 다중 FM 재학습이 apples-to-apples로 돌린 유일 endpoint(run_mil_cost CANCER_CFG 기준).
    # MULTIFM_COMPARISON.md §4가 요구한 신형 FM 5-seed 우연배제 자리.
    "COLORECTAL":    ["braf_v600e"],
}

def one_auc(slides, labels, ep, device, shuffle, seed):
    recs, _ = m.train_eval(slides, labels, ep, device, shuffle=shuffle, seed=seed)
    if recs is None:
        return None
    pa = m.patient_agg(recs)
    y = [v[1] for v in pa.values()]; p = [v[0] for v in pa.values()]
    auc, _, _ = m.bootstrap_auc(y, p)
    return auc, int(sum(y)), len(pa)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True, choices=list(ENDPOINTS))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--endpoints", help="comma; 생략 시 암종 전 endpoint")
    ap.add_argument("--real-only", action="store_true", help="스모크: real(seed42)만")
    ap.add_argument("--fm", default="uni", choices=list(m.FM_SPEC),
                    help="foundation model 임베딩. uni=기존(기본, 출력 파일명 불변), virchow2/uni2h=다중 FM")
    ap.add_argument("--out")
    a = ap.parse_args()
    # 다중 FM: CLAMSB feature_dim을 해당 FM 차원으로(run_mil_cost 전역 세팅해 코드경로 재사용)
    m.FEATURE_DIM = m.FM_SPEC[a.fm]["dim"]
    labels, split, slides = m.load_meta(a.cancer, a.fm)
    if a.fm != "uni":
        print(f"[다중 FM] {a.fm} (dim={m.FEATURE_DIM}) 임베딩으로 5-seed 검정", flush=True)
    eps = a.endpoints.split(",") if a.endpoints else ENDPOINTS[a.cancer]
    print(f"[{a.cancer}] slides={len(slides)} labels={len(labels)} device={a.device} eps={eps}", flush=True)
    res = {"track": a.cancer, "purpose": "5-seed shuffle-null robustness (BLOCKER-1)",
           "fm": a.fm, "feature_dim": m.FEATURE_DIM,
           "claim_level": "hypothesis_only", "critic_status": "pending",
           "criterion": "real_auroc > null_mean + 2*null_sd (5 seed, ddof=1)",
           "shuffle_seeds": SEEDS, "endpoints": {}}
    for ep in eps:
        t = time.time()
        real = one_auc(slides, labels, ep, a.device, False, 42)
        if real is None:
            res["endpoints"][ep] = {"status": "skip(insufficient)"}; print(f"  {ep}: skip", flush=True); continue
        real_auc, n_pos, n_hold = real
        if a.real_only:
            print(f"  {ep}: real(seed42)={real_auc} n_pos={n_pos}/{n_hold} ({time.time()-t:.0f}s)", flush=True)
            res["endpoints"][ep] = {"real_auroc": round(real_auc, 4), "n_pos": n_pos, "n_hold": n_hold, "real_only": True}
            continue
        nulls = []
        for s in SEEDS:
            r = one_auc(slides, labels, ep, a.device, True, s)
            nulls.append(round(r[0], 4) if r else None)
        nn = [x for x in nulls if x is not None]
        nm = float(np.mean(nn)); nsd = float(np.std(nn, ddof=1)); thr = nm + 2 * nsd
        passed = bool(real_auc > thr)
        res["endpoints"][ep] = {"real_auroc": round(real_auc, 4), "n_pos": n_pos, "n_hold": n_hold,
                                "null_mean": round(nm, 4), "null_sd": round(nsd, 4),
                                "threshold": round(thr, 4), "pass": passed, "null_seeds": nulls}
        print(f"  {ep}: real {real_auc} vs thr {thr:.4f} → {'PASS' if passed else 'FAIL'}  null={nulls} ({time.time()-t:.0f}s)", flush=True)
    # UNI는 기존 파일명 유지(동작 불변), 다중 FM은 FM별 파일로 분리
    _fn = "shuffle_null_robustness.json" if a.fm == "uni" else f"shuffle_null_robustness_{a.fm}.json"
    out = Path(a.out) if a.out else HERE / a.cancer / "full" / _fn
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"wrote {out}", flush=True)

if __name__ == "__main__":
    main()

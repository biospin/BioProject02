#!/usr/bin/env python3
"""
STAD·HNSC MIL 학습 + 치환가능성 검정 (격리판) — run_mil_cost 헬퍼 재사용.

각 endpoint {real, shuffle-null, prevalence} CLAM-SB, val+test pooled holdout(site-disjoint) AUROC+CI.
- frozen_map(치료거리) 없음 → mean_cost=null, endpoint별 misroute_rate가 lead(과제 지시).
- n_pos<25 → exploratory 표기(검정력 부족; wide CI). HER2-amp가 여기 해당 예상(highlight).
- 양성대조: STAD=lauren_diffuse(강한 형태, 기대≥0.85), HNSC=grade_high(soft; SCC라 0.75 미달 가능
  → advisor: FAIL을 '파이프라인 고장'으로 읽지 말 것. HPV≥0.80이 de facto sanity).

출력: <cancer>/full/mil_cost_results.json
Usage: python sh_mil_cost.py --cancer GASTRIC_STAD --device cuda:0
"""
import json, sys, argparse, time
from pathlib import Path
from collections import defaultdict
import run_mil_cost as m

HERE = Path(__file__).parent
EXPLORATORY_NPOS = 25

CANCER_CFG = {
 "GASTRIC_STAD": {
   "endpoints": ["lauren_diffuse", "msi_h", "erbb2_amp", "ebv"],
   "positive_control": "lauren_diffuse",   # 강한 형태(양성대조)
   "route_axis": {"erbb2_amp": "antiHER2", "msi_h": "antiPD1"},  # 라우팅 축(우선순위)
   "route_default": "chemo",
 },
 "HEADNECK_HNSC": {
   "endpoints": ["hpv_pos", "egfr_amp", "grade_high"],
   "positive_control": "grade_high",       # soft(분화도); HPV≥0.80이 실질 sanity
   "route_axis": {"hpv_pos": "deescalate", "egfr_amp": "antiEGFR"},
   "route_default": "standard",
 },
}

def misroute_per_endpoint(results):
    """endpoint별 오분류율(proba>=0.5 vs true). frozen_map 없으므로 이게 cost lead."""
    mr={}
    for ep, r in results["endpoints"].items():
        pp=r.get("patient_proba",{}); pt=r.get("patient_true",{})
        if not pp: continue
        n=mis=0
        for c,proba in pp.items():
            true=pt.get(c)
            if true is None: continue
            n+=1; mis+=int(int(proba>=0.5)!=true)
        mr[ep]={"n":n,"misroute_rate":round(mis/n,3) if n else None,
                "auc":r.get("real",{}).get("auc"),
                "mean_cost":None,  # 임상 치료거리 frozen_map 미구축 → null(과제: misroute_rate lead)
                }
    return mr

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cancer", required=True, choices=list(CANCER_CFG))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--fm", default="uni", choices=list(m.FM_SPEC),
                    help="foundation model 임베딩 선택. uni=기존(기본, 동작 불변), virchow2/uni2h=다중 FM 견고성")
    a=ap.parse_args()
    # 다중 FM: CLAMSB feature_dim을 해당 FM 차원으로 (run_mil_cost 전역을 세팅해 재사용)
    m.FEATURE_DIM = m.FM_SPEC[a.fm]["dim"]
    cfg=CANCER_CFG[a.cancer]
    labels, split, slides = m.load_meta(a.cancer, a.fm)
    if a.fm != "uni":
        print(f"[다중 FM] {a.fm} (dim={m.FEATURE_DIM}) 임베딩으로 학습 — Paper C 모델 비의존성 검정")
    print(f"{a.cancer}: {len(slides)} 슬라이드(임베딩 존재), {len(labels)} 라벨환자")
    results={"cancer":a.cancer,"n_slides":len(slides),"claim_level":"hypothesis_only",
             "critic_status":"pending","exploratory_npos_threshold":EXPLORATORY_NPOS,
             "fm":a.fm,"feature_dim":m.FEATURE_DIM,"endpoints":{}}
    for ep in cfg["endpoints"]:
        t=time.time(); r=m.run_endpoint(slides, labels, ep, a.device)
        # exploratory 플래그
        npos=r.get("real",{}).get("n_pos")
        if npos is not None:
            r["exploratory"]= bool(npos < EXPLORATORY_NPOS)
        results["endpoints"][ep]=r
        real=r.get("real",{}); sh=r.get("shuffle_null",{})
        flag=" [EXPLORATORY n_pos<25]" if r.get("exploratory") else ""
        print(f"  {ep}: real AUC={real.get('auc')} CI{real.get('ci95')} "
              f"n+={real.get('n_pos')}/{real.get('n_holdout_patients')} | shuffle={sh.get('auc')}"
              f" ({time.time()-t:.0f}s){flag}")
    # 양성대조 게이트
    pc=cfg["positive_control"]
    if pc and pc in results["endpoints"]:
        pca=results["endpoints"][pc].get("real",{}).get("auc")
        gate=(pca is not None and pca>=0.75)
        soft=(a.cancer=="HEADNECK_HNSC")
        results["positive_control_gate"]={"endpoint":pc,"auc":pca,"pass":gate,"soft":soft,
            "note":("형태 양성대조 AUROC>=0.75 = H&E/파이프라인 정상." if not soft else
                    "grade는 SCC에서 soft 양성대조 — 미달이 파이프라인 고장 의미 아님. HPV>=0.80이 실질 sanity.")}
        print(f"  [양성대조 {pc}] AUROC={pca} → {'PASS' if gate else ('SOFT-FAIL' if soft else 'FAIL')}")
    # cost: frozen_map 없음 → endpoint별 misroute_rate lead(mean_cost=null)
    results["endpoint_misroute"]=misroute_per_endpoint(results)
    results["cost_note"]="frozen_map(임상 치료거리) 미구축 → mean_cost=null, misroute_rate가 lead 지표(과제 지시)."
    print("  misroute(per-endpoint, cost lead):",
          json.dumps({k:{"misroute_rate":v["misroute_rate"],"auc":v["auc"]} for k,v in results["endpoint_misroute"].items()}, ensure_ascii=False))
    # UNI는 기존 파일명 유지(동작 불변), 다중 FM은 FM별 파일로 분리
    fname = "mil_cost_results.json" if a.fm=="uni" else f"mil_cost_results_{a.fm}.json"
    out=HERE/a.cancer/"full"/fname
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"  wrote {out}")

if __name__=="__main__":
    main()

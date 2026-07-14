#!/usr/bin/env python3
"""
LUNG_NSCLC 전사체 아형 one-vs-rest MIL (run_mil_cost 헬퍼 재사용) — 격리판.

법칙 held-out 예측 #4: "전사체 아형 중 TRU 최고 AUROC" 검정용.
- LUAD 발현아형(TRU/PI/PP): one-vs-rest는 **LUAD 환자 내에서만**(rest=다른 LUAD 아형).
  → LUSC를 rest에 넣으면 histology를 재검출해 수치 부풀림(advisor 지적) → 금지.
- LUSC 아형(basal/classical/secretory/primitive): LUSC 내 ovr(탐색적 부가).
- 각 endpoint {real, shuffle-null, prevalence}, val+test pooled holdout(site-disjoint), AUROC+CI.
- n_pos<25 → exploratory(검정력 부족).

출력: <cancer>/full/mil_subtype_results.json
Usage: python sh_lung_subtype_mil.py --device cuda:1
"""
import json, csv, argparse, time
from pathlib import Path
import run_mil_cost as m

HERE = Path(__file__).parent
EXPLORATORY_NPOS = 25
CANCER = "LUNG_NSCLC"

LUAD_SUBS = ["TRU", "PI", "PP"]
LUSC_SUBS = ["basal", "classical", "secretory", "primitive"]

def build_subtype_labels():
    d = HERE / CANCER / "full"
    sd = {r["case_id"]: r for r in csv.DictReader(open(d/"subtype_labels.csv"))}
    labels = {}  # case_id -> {endpoint: "0"/"1"}
    for cid, r in sd.items():
        lu = r.get("luad_subtype", "").strip()
        ls = r.get("lusc_subtype", "").strip()
        ep = {}
        if lu in LUAD_SUBS:  # LUAD 환자만 LUAD-ovr에 참여
            for sub in LUAD_SUBS:
                ep[f"luad_{sub}_vs_rest"] = "1" if lu == sub else "0"
        if ls in LUSC_SUBS:  # LUSC 환자만 LUSC-ovr에 참여
            for sub in LUSC_SUBS:
                ep[f"lusc_{sub}_vs_rest"] = "1" if ls == sub else "0"
        if ep:
            labels[cid] = ep
    return labels

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda:1")
    a = ap.parse_args()
    _, split, slides = m.load_meta(CANCER)   # slides = 임베딩 존재 + split
    labels = build_subtype_labels()
    endpoints = [f"luad_{s}_vs_rest" for s in LUAD_SUBS] + [f"lusc_{s}_vs_rest" for s in LUSC_SUBS]
    print(f"{CANCER} subtype: {len(slides)} 슬라이드, {len(labels)} 아형라벨환자")
    results = {"cancer": CANCER, "task": "transcriptomic_subtype_ovr",
               "claim_level": "hypothesis_only", "critic_status": "pending",
               "exploratory_npos_threshold": EXPLORATORY_NPOS,
               "ovr_restriction": "LUAD-subtype ovr는 LUAD 내에서만, LUSC-subtype ovr는 LUSC 내에서만 (histology 재검출 방지)",
               "endpoints": {}}
    for ep in endpoints:
        t = time.time()
        r = m.run_endpoint(slides, labels, ep, a.device)
        npos = r.get("real", {}).get("n_pos")
        if npos is not None:
            r["exploratory"] = bool(npos < EXPLORATORY_NPOS)
        results["endpoints"][ep] = r
        real = r.get("real", {}); sh = r.get("shuffle_null", {})
        flag = " [EXPLORATORY n_pos<25]" if r.get("exploratory") else ""
        print(f"  {ep}: real AUC={real.get('auc')} CI{real.get('ci95')} "
              f"n+={real.get('n_pos')}/{real.get('n_holdout_patients')} | shuffle={sh.get('auc')}"
              f" ({time.time()-t:.0f}s){flag}")
    out = HERE / CANCER / "full" / "mil_subtype_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"  wrote {out}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Critic #5 독립 재계산 — braveji (BIOP02-59 / BIOP02-111 서명 전제 조건).

**목적:** jhans 커밋 산출물의 confidence를 원자료에서 독립적으로 재산출해 대조한다.
**독립성:** `endocrine_rule.py` 를 import 하지 않는다. 코드를 읽고 규칙을 여기 다시 구현했다.
           (같은 함수를 호출하면 재현일 뿐 독립 검증이 아니다.)

원자료: /workspace/experiments/jhans/20260702_consistency/consistency_scores.csv
        (GPU 머신, 2026-08-04 스냅샷 = consistency_scores_snapshot.csv, md5 52547edc…)

규칙 출처(읽고 재구현):
  agents/therapeutic_evidence/rules/endocrine_rule.py
    - DRUG_CLASS_MAP (L25-40)
    - _class_evidence  (L65-100)  : data_source=="both" 행이 있으면 그것만 평균, 없으면 전체 평균
    - _confidence_from_rho (L102-111): conf = min(0.95, clamp(mean_rho,0,1) + min(0.05*n_both, 0.1))
    - ET ± CDK4/6i 는 두 클래스 mean_rho 의 평균, n_both 는 합산 (L164-171)

사용: python3 recompute_braveji.py [--csv <path>] [--strict]
      불일치가 있으면 --strict 시 종료코드 1.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

DRUG_CLASS = {
    "ET":    ["TAMOXIFEN", "LETROZOLE", "ANASTROZOLE", "EXEMESTANE", "FULVESTRANT"],
    "CDK":   ["PALBOCICLIB", "RIBOCICLIB", "ABEMACICLIB"],
    "HER2":  ["LAPATINIB", "AFATINIB", "NERATINIB"],
    "CHEMO": ["PACLITAXEL", "DOCETAXEL", "DOXORUBICIN", "GEMCITABINE",
              "VINORELBINE", "ERIBULIN"],
}

# jhans 커밋 산출물의 값 (experiments/jhans/biological_plausibility/*.json, 커밋 07a32ee)
COMMITTED = {
    "Anti-HER2 (TKI)":     0.5927,
    "Endocrine ± CDK4/6i": 0.3448,
    "Cytotoxic chemo":     0.5682,
}


def load_rows(csv_path):
    rows = []
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            if r["spearman_rho"]:            # 빈 값(예: NELARABINE) 제외
                rows.append({"drug": r["drug_name"],
                             "rho": float(r["spearman_rho"]),
                             "src": r["data_source"]})
    return rows


def class_evidence(names, rows):
    matched = [r for r in rows if r["drug"] in names]
    if not matched:
        return {"n_found": 0, "n_both": 0, "mean_rho": None, "drugs": []}
    both = [r for r in matched if r["src"] == "both"]
    use = both if both else matched          # "both" 우선, 없으면 전체
    mean_rho = sum(r["rho"] for r in use) / len(use)
    return {"n_found": len(matched), "n_both": len(both), "mean_rho": round(mean_rho, 4),
            "drugs": [(r["drug"], r["rho"], r["src"])
                      for r in sorted(matched, key=lambda x: -x["rho"])]}


def confidence(mean_rho, n_both):
    if mean_rho is None:
        return 0.3                            # fallback
    base = max(0.0, min(1.0, mean_rho))
    return round(min(0.95, base + min(0.05 * n_both, 0.1)), 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(HERE / "consistency_scores_snapshot.csv"))
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    rows = load_rows(a.csv)
    et, cdk, her2, chemo = (class_evidence(DRUG_CLASS[k], rows)
                            for k in ("ET", "CDK", "HER2", "CHEMO"))

    rhos = [x["mean_rho"] for x in (et, cdk) if x["mean_rho"] is not None]
    combined = sum(rhos) / len(rhos) if rhos else None
    n_both_comb = et["n_both"] + cdk["n_both"]

    recomputed = {
        "Anti-HER2 (TKI)":     confidence(her2["mean_rho"], her2["n_both"]),
        "Endocrine ± CDK4/6i": confidence(combined, n_both_comb),
        "Cytotoxic chemo":     confidence(chemo["mean_rho"], chemo["n_both"]),
    }

    bad = []
    print(f"{'가설':<24}{'재계산':>10}{'커밋값':>10}{'차이':>12}  판정")
    for k, v in recomputed.items():
        c = COMMITTED[k]
        d = abs(v - c)
        ok = d < 1e-9
        if not ok:
            bad.append(k)
        print(f"{k:<24}{v:>10}{c:>10}{d:>12.2e}  {'일치' if ok else '불일치'}")

    print("\n--- 근거 상세 ---")
    print(f"HER2  mean_rho={her2['mean_rho']} n_both={her2['n_both']}  {her2['drugs']}")
    print(f"ET    mean_rho={et['mean_rho']} n_both={et['n_both']}  {et['drugs']}")
    print(f"CDK   mean_rho={cdk['mean_rho']} n_both={cdk['n_both']}  {cdk['drugs']}")
    print(f"결합  ({et['mean_rho']}+{cdk['mean_rho']})/2 = {round(combined, 4)}  n_both={n_both_comb}")
    print(f"CHEMO mean_rho={chemo['mean_rho']} n_both={chemo['n_both']}  {chemo['drugs']}")

    out = {
        "track": "Critic #5 biological plausibility 독립 재계산 (braveji)",
        "raw_source": "/workspace/experiments/jhans/20260702_consistency/consistency_scores.csv",
        "raw_md5": "52547edcff04c4585f46ebb761ff2718",
        "method": "endocrine_rule.py 를 import 하지 않고 규칙을 재구현해 산출",
        "recomputed": recomputed,
        "committed": COMMITTED,
        "all_match": not bad,
        "evidence": {"HER2": her2, "ET": et, "CDK": cdk, "CHEMO": chemo,
                     "combined_rho": round(combined, 4), "combined_n_both": n_both_comb},
    }
    (HERE / "VERIFICATION_braveji.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\n전체 일치: {not bad}")
    sys.exit(1 if (bad and a.strict) else 0)


if __name__ == "__main__":
    main()

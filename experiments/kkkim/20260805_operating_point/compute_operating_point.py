#!/usr/bin/env python3
"""BIOP02-124 #3 — 임상 operating-point 분석 (MUST, 게재 blocker).

AUROC만으론 '대체 가능/불가'를 못 정한다. 실제 결정 지표로 재계산한다:
endpoint별 sensitivity·specificity·PPV·NPV(threshold 0.5) + 유병률 민감도(Bayes).

입력(전부 기존 실측 예측 — 신규 데이터 없음):
- 교차암종: experiments/crosscancer/<C>/full/mil_cost_results.json 의 patient_proba/patient_true
- BRCA 수용체: experiments/sjpark/cptac_ext_predictions_indexed.csv(예측) +
  /workspace CPTAC manifest(true er/pr/her2)

산출: operating_point_results.json + 콘솔 표. threshold 0.5 고정(rule-in/rule-out 재조정은 후속).
"""
import csv, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
XC = REPO / "experiments/crosscancer"
CPTAC_PRED = REPO / "experiments/sjpark/cptac_ext_predictions_indexed.csv"
CPTAC_MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"
THR = 0.5

def oppoint(y, p, thr=THR):
    y = np.asarray(y).astype(int); p = np.asarray(p, float)
    pred = (p >= thr).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
    tn = int(((pred == 0) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    n = len(y); pos = int(y.sum())
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    ppv = tp / (tp + fp) if (tp + fp) else float("nan")
    npv = tn / (tn + fn) if (tn + fn) else float("nan")
    return {"n": n, "n_pos": pos, "prevalence": round(pos / n, 4), "thr": thr,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "sensitivity": round(sens, 4), "specificity": round(spec, 4),
            "ppv": round(ppv, 4), "npv": round(npv, 4)}

def bayes_prev_sensitivity(sens, spec, prevs=(0.05, 0.1, 0.2, 0.3)):
    """유병률별 PPV/NPV (sens·spec는 유병률 독립 → Bayes로 재투영). 대체 안전성의 핵심."""
    out = {}
    for pr in prevs:
        ppv = sens * pr / (sens * pr + (1 - spec) * (1 - pr)) if (sens * pr + (1 - spec) * (1 - pr)) else float("nan")
        npv = spec * (1 - pr) / (spec * (1 - pr) + (1 - sens) * pr) if (spec * (1 - pr) + (1 - sens) * pr) else float("nan")
        out[f"prev_{pr}"] = {"ppv": round(ppv, 4), "npv": round(npv, 4)}
    return out

def load_xc():
    recs = {}
    for cdir in sorted(XC.glob("*/full/mil_cost_results.json")):
        cancer = cdir.parts[-3]
        d = json.loads(cdir.read_text())
        for ep, e in d.get("endpoints", {}).items():
            if isinstance(e, dict) and "patient_proba" in e and "patient_true" in e:
                pr = e["patient_proba"]; tr = e["patient_true"]
                keys = list(pr.keys())
                y = [int(tr[k]) for k in keys]; p = [float(pr[k]) for k in keys]
                if len(set(y)) == 2:
                    recs[f"{cancer}:{ep}"] = (y, p)
    return recs

def load_brca_receptor():
    pred = {r["slide_id"]: r for r in csv.DictReader(open(CPTAC_PRED))}
    try:
        man = list(csv.DictReader(open(CPTAC_MANIFEST)))
    except FileNotFoundError:
        return {}
    out = {}
    for axis, pcol, tcol in [("ER", "er_pred_prob", "er"), ("PR", "pr_pred_prob", "pr"), ("HER2", "her2_pred_prob", "her2")]:
        # 환자 단위 집계: 슬라이드 proba 평균, true는 환자 대표값
        by_case = {}
        for r in man:
            sid = r["slide_id"]
            if sid not in pred: continue
            t = (r.get(tcol, "") or "").strip().lower()
            if t not in ("positive", "negative"): continue
            case = r["case_id"]
            by_case.setdefault(case, {"y": 1 if t == "positive" else 0, "p": []})
            by_case[case]["p"].append(float(pred[sid][pcol]))
        y = [v["y"] for v in by_case.values()]; p = [float(np.mean(v["p"])) for v in by_case.values()]
        if len(set(y)) == 2:
            out[f"BRCA:{axis}"] = (y, p)
    return out

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    data = {**load_xc(), **load_brca_receptor()}
    results = {}
    print(f"{'endpoint':28} {'n':>4} {'prev':>6} {'sens':>6} {'spec':>6} {'PPV':>6} {'NPV':>6}")
    for name, (y, p) in sorted(data.items()):
        op = oppoint(y, p)
        op["prevalence_sensitivity"] = bayes_prev_sensitivity(op["sensitivity"], op["specificity"])
        results[name] = op
        print(f"{name:28} {op['n']:>4} {op['prevalence']:>6.3f} {op['sensitivity']:>6.3f} "
              f"{op['specificity']:>6.3f} {op['ppv']:>6.3f} {op['npv']:>6.3f}")
    out = {"analysis": "BIOP02-124 #3 operating-point", "threshold": THR,
           "claim_level": "hypothesis_only", "critic_status": "pending",
           "note": "threshold 0.5 고정. sens/spec는 유병률 독립, PPV/NPV는 관측 유병률 기준 + prevalence_sensitivity(Bayes 재투영). rule-in/rule-out threshold 재조정·calibration(ECE)·decision-curve는 후속.",
           "endpoints": results}
    (HERE / "operating_point_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\nwrote {HERE/'operating_point_results.json'}  ({len(results)} endpoints)")

if __name__ == "__main__":
    main()

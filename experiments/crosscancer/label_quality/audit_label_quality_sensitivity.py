#!/usr/bin/env python3
"""
BIOP02-139 라벨 품질 민감도 분석 — 제외 전/후 AUROC 대조.

EXCLUSION_CRITERIA_PREREGISTRATION.md에서 사전등록한 기준을 그대로 적용한다
(이 스크립트를 짜기 전에 그 문서를 커밋했다 — 기준을 결과 보고 나서 바꾸지 않는다).

정본 예측 점수: <cohort>/full/mil_cost_results.json 의 endpoints.<ep>.patient_proba
(홀드아웃 환자만; run_mil_cost.py 가 만든 것과 동일 소스, 재학습 없음).
AUROC CI: run_mil_cost.py의 bootstrap_auc(n=1000, seed=42) 컨벤션을 그대로 재사용.

출력: label_quality_sensitivity_results.json
"""
import json, csv
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
CC = HERE.parent


def bootstrap_auc(y, p, n=1000, seed=42):
    """run_mil_cost.py:68 과 동일 컨벤션 (재구현이 아니라 그대로 옮김)."""
    y = np.array(y); p = np.array(p)
    if len(set(y)) < 2:
        return None, None, None
    rng = np.random.default_rng(seed)
    base = roc_auc_score(y, p); boots = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        boots.append(roc_auc_score(y[idx], p[idx]))
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if boots else (None, None))
    return round(float(base), 4), (round(float(lo), 4) if lo is not None else None), (round(float(hi), 4) if hi is not None else None)


def load_endpoint(cohort, ep):
    d = json.load(open(CC / cohort / "full" / "mil_cost_results.json"))
    e = d["endpoints"][ep]
    return e["patient_proba"], e["patient_true"], e["real"]["auc"], e["real"]["ci95"]


def load_msi_dual():
    rows = {}
    with open(HERE / "msi_dual_score.csv") as f:
        for r in csv.DictReader(f):
            rows[r["case_id"]] = r
    return rows


def load_mutation_vaf():
    by_ep = {}
    with open(HERE / "mutation_vaf.csv") as f:
        for r in csv.DictReader(f):
            by_ep.setdefault(r["endpoint"], {})[r["case_id"]] = float(r["vaf"]) if r["vaf"] else None
    return by_ep


def before_after(proba, true, exclude_ids, label):
    ids_all = sorted(proba)
    y_all = [true[c] for c in ids_all]
    p_all = [proba[c] for c in ids_all]
    ids_kept = [c for c in ids_all if c not in exclude_ids]
    y_kept = [true[c] for c in ids_kept]
    p_kept = [proba[c] for c in ids_kept]
    auc_b, lo_b, hi_b = bootstrap_auc(y_all, p_all)
    auc_a, lo_a, hi_a = bootstrap_auc(y_kept, p_kept)
    result = {
        "label": label,
        "n_holdout_before": len(ids_all), "n_excluded": len(ids_all) - len(ids_kept),
        "n_holdout_after": len(ids_kept),
        "auroc_before": auc_b, "ci95_before": [lo_b, hi_b],
        "auroc_after": auc_a, "ci95_after": [lo_a, hi_a],
    }
    print(f"  {label}: n_excluded={result['n_excluded']}/{result['n_holdout_before']} "
          f"AUROC {auc_b}{[lo_b,hi_b]} -> {auc_a}{[lo_a,hi_a] if auc_a else 'n/a(표본 부족)'}")
    return result


def msi_concordance():
    dual = load_msi_dual()
    n_both = agree = disagree = 0
    disagree_ids = []
    tp = fp = fn = tn = 0  # sensor=positive class 기준 2x2 (kappa용)
    for c, r in dual.items():
        if not r["msi_sensor_score"] or not r["msi_mantis_score"]:
            continue
        n_both += 1
        s = float(r["msi_sensor_score"]) >= 3.5
        m = float(r["msi_mantis_score"]) >= 0.4
        if s == m:
            agree += 1
        else:
            disagree += 1; disagree_ids.append(c)
        tp += s and m; tn += (not s) and (not m); fp += (not s) and m; fn += s and (not m)
    po = agree / n_both if n_both else None
    p_s_pos = (tp + fn) / n_both; p_m_pos = (tp + fp) / n_both
    pe = p_s_pos * p_m_pos + (1 - p_s_pos) * (1 - p_m_pos)
    kappa = (po - pe) / (1 - pe) if po is not None and pe < 1 else None
    return {
        "n_both_scores": n_both, "n_agree": agree, "n_disagree": disagree,
        "agreement_rate": round(po, 4) if po is not None else None,
        "cohens_kappa": round(kappa, 4) if kappa is not None else None,
        "disagree_case_ids": disagree_ids,
    }


def main():
    out = {}

    print("=== MSI (GASTRIC_STAD, msi_h) — MSIsensor vs MANTIS ===")
    conc = msi_concordance()
    print(f"  일치도: {conc['n_agree']}/{conc['n_both_scores']} (agreement={conc['agreement_rate']}, kappa={conc['cohens_kappa']})")
    proba, true, headline_auc, headline_ci = load_endpoint("GASTRIC_STAD", "msi_h")
    exclude = set(conc["disagree_case_ids"])
    res = before_after(proba, true, exclude, "msi_h (MANTIS/MSIsensor 불일치 제외)")
    res["headline_auc_ci95"] = [headline_auc, headline_ci]
    res["concordance"] = conc
    out["msi_h"] = res

    print("\n=== 변이 VAF (LUNG kras_g12c/egfr_activating, COLORECTAL braf_v600e) ===")
    vaf_by_ep = load_mutation_vaf()
    for cohort, ep in [("LUNG_NSCLC", "kras_g12c"), ("LUNG_NSCLC", "egfr_activating"), ("COLORECTAL", "braf_v600e")]:
        proba, true, headline_auc, headline_ci = load_endpoint(cohort, ep)
        vafs = vaf_by_ep.get(ep, {})
        low_vaf_positive = {c for c, v in vafs.items() if v is not None and v < 0.10 and true.get(c) == 1}
        # 저-VAF 양성 중 홀드아웃(patient_proba)에 실제로 들어있는 것만 배제 대상
        exclude = low_vaf_positive & set(proba)
        res = before_after(proba, true, exclude, f"{cohort}/{ep} (VAF<0.10 양성 제외)")
        res["headline_auc_ci95"] = [headline_auc, headline_ci]
        res["n_low_vaf_positive_total"] = len(low_vaf_positive)
        res["n_low_vaf_positive_in_holdout"] = len(exclude)
        out[f"{cohort}.{ep}"] = res

    out_path = HERE / "label_quality_sensitivity_results.json"
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)
    print(f"\nSaved {out_path}")


if __name__ == "__main__":
    main()

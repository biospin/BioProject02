"""
A4 (BIOP02-80 Yale 앵커) — 항HER2 축 점수가 실제 trastuzumab pCR을 층화하는지 검정.

입력: A3 축 점수 CSV(apply_frozen_axis_yale.py 산출) + pCR 라벨 CSV(kkkim/jhans 제공).
Primary: 축 점수의 pCR 예측 AUROC + bootstrap 95% CI (2000, 환자단위 리샘플).
DeLong: 축 점수 vs baseline_score(예: 임상 HER2 확률/IHC 등) AUC 차이 유의성(제공 시).
사전등록 반증조건: 축 AUROC 95% CI가 0.5를 포함하면 → "축이 pCR을 층화하지 못함"(음성결과).
성공기준(kkkim/Farahmand 2022): frozen-transfer AUROC가 in-cohort CV 천장 0.80[0.69,0.88]에 근접/겹침.

Run (라벨 도착 후):
    python agents/modeling/scripts/eval_axis_pcr_yale.py \
        --axis_csv experiments/sjpark/yale_antiher2_axis_scores.csv \
        --labels_csv /workspace/data/cache/biop02/yale/yale_pcr_labels.csv \
        --id_col case_id --pcr_col pcr --cohort_col cohort --cohort_value trastuzumab \
        --baseline_col her2_prob \
        --out experiments/sjpark/yale_axis_pcr_result.json

Smoke test (라벨 없이 코드 동작만 확인):
    python agents/modeling/scripts/eval_axis_pcr_yale.py --axis_csv ... --smoke_test --out /tmp/x.json
"""
import argparse
import csv
import json
from collections import defaultdict

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score


# ---------- DeLong (두 상관 ROC AUC 차이 검정) ----------
def _compute_midrank(x):
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    T2 = np.empty(N, dtype=float)
    T2[J] = T
    return T2


def _fast_delong(preds_sorted_transposed, label_1_count):
    m = label_1_count
    n = preds_sorted_transposed.shape[1] - m
    pos = preds_sorted_transposed[:, :m]
    neg = preds_sorted_transposed[:, m:]
    k = preds_sorted_transposed.shape[0]
    tx = np.empty([k, m], dtype=float)
    ty = np.empty([k, n], dtype=float)
    tz = np.empty([k, m + n], dtype=float)
    for r in range(k):
        tx[r, :] = _compute_midrank(pos[r, :])
        ty[r, :] = _compute_midrank(neg[r, :])
        tz[r, :] = _compute_midrank(preds_sorted_transposed[r, :])
    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx[:, :]) / n
    v10 = 1.0 - (tz[:, m:] - ty[:, :]) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, delongcov


def delong_test(y_true, score_a, score_b):
    """두 예측(같은 y_true)의 AUC 차이 p-value (correlated DeLong)."""
    order = np.argsort(-y_true.astype(int))
    label_1_count = int(y_true.sum())
    preds = np.vstack((score_a, score_b))[:, order]
    aucs, cov = _fast_delong(preds, label_1_count)
    var = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    if var <= 0:
        return float(aucs[0]), float(aucs[1]), None
    z = (aucs[0] - aucs[1]) / np.sqrt(var)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(aucs[0]), float(aucs[1]), float(p)


def bootstrap_auc_ci(y, s, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y)
    aucs = []
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        if len(np.unique(y[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y[idx], s[idx]))
    return round(float(np.percentile(aucs, 2.5)), 4), round(float(np.percentile(aucs, 97.5)), 4)


def load_axis(path):
    d = {}
    for r in csv.DictReader(open(path)):
        d.setdefault(r["case_id"], []).append(float(r["antiher2_axis_score"]))
    # 환자단위: 슬라이드 여러 장이면 평균
    return {k: float(np.mean(v)) for k, v in d.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis_csv", required=True)
    ap.add_argument("--labels_csv", default="")
    ap.add_argument("--id_col", default="case_id")
    ap.add_argument("--pcr_col", default="pcr")
    ap.add_argument("--cohort_col", default="")
    ap.add_argument("--cohort_value", default="")
    ap.add_argument("--baseline_col", default="", help="DeLong 비교용 baseline 점수 컬럼(선택)")
    ap.add_argument("--smoke_test", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    axis = load_axis(args.axis_csv)  # case_id -> mean axis score
    print(f"축 점수(환자단위): {len(axis)}명")

    if args.smoke_test:
        rng = np.random.default_rng(0)
        cases = list(axis)[:85]
        labels = {c: {"pcr": int(rng.integers(0, 2)), "baseline": float(rng.random())} for c in cases}
        print("[smoke] 무작위 pCR 라벨로 코드 동작만 확인")
    else:
        if not args.labels_csv:
            print("[대기] --labels_csv 미지정 — pCR 라벨(kkkim/jhans 제공) 필요. A4 실행 보류.")
            return
        labels = {}
        for r in csv.DictReader(open(args.labels_csv)):
            if args.cohort_col and args.cohort_value and r.get(args.cohort_col) != args.cohort_value:
                continue
            cid = r[args.id_col]
            labels[cid] = {"pcr": int(float(r[args.pcr_col])),
                           "baseline": float(r[args.baseline_col]) if args.baseline_col and r.get(args.baseline_col) else None}

    common = [c for c in labels if c in axis]
    y = np.array([labels[c]["pcr"] for c in common])
    s = np.array([axis[c] for c in common])
    print(f"매칭 환자: {len(common)} (pCR+ {int(y.sum())} / pCR- {int((1-y).sum())})")
    if len(np.unique(y)) < 2:
        print("[중단] pCR 클래스가 1개뿐 — AUROC 계산 불가")
        return

    auc = round(float(roc_auc_score(y, s)), 4)
    lo, hi = bootstrap_auc_ci(y, s)
    result = {
        "n_patients": len(common),
        "n_pcr_pos": int(y.sum()),
        "n_pcr_neg": int((1 - y).sum()),
        "axis_auroc": auc,
        "axis_auroc_ci_95": [lo, hi],
        "falsification_ci_includes_0.5": bool(lo <= 0.5 <= hi),
        "success_ref_farahmand_cv_auc": [0.80, 0.69, 0.88],
        "near_reference": bool(hi >= 0.69),  # CI 상단이 참조 CI 하단과 겹치는지(근접 기준)
    }

    base = np.array([labels[c]["baseline"] for c in common]) if all(labels[c].get("baseline") is not None for c in common) else None
    if base is not None:
        a_axis, a_base, p = delong_test(y, s, base)
        result["baseline_auroc"] = round(a_base, 4)
        result["delong_p_axis_vs_baseline"] = round(p, 4) if p is not None else None

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved: {args.out}")
    print("해석: axis_auroc_ci_95가 0.5를 포함하면 사전등록 반증조건 충족(축이 pCR 층화 못함=음성결과).")


if __name__ == "__main__":
    main()

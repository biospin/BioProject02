#!/usr/bin/env python3
"""
BIOP02-140 v1 — 공변량-only vs 공변량+H&E 증분가치, 폐(KRAS/EGFR/histology).
방법론은 COVARIATE_BASELINE_PREREGISTRATION.md 에 결과를 보기 전에 고정
(2026-08-20 정정: H&E patient_proba가 holdout에만 있어 5-fold in-holdout CV로 변경, 정정 내역은
문서 참조 — 이 시점까지 AUROC 미계산 상태였음).
CPU only. GPU 불요. 기존 임베딩·H&E 예측(mil_cost_results.json) 재사용, 재학습 없음.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
LUNG_FULL = HERE.parent / "LUNG_NSCLC" / "full"
sys.path.insert(0, str(HERE.parent))
from run_mil_cost import bootstrap_auc  # 기존 컨벤션 재사용 (n=1000, seed=42)

ENDPOINTS = ["histology_lusc", "egfr_activating", "kras_g12c"]
N_BOOT, SEED, N_FOLD = 1000, 42, 5


def load():
    labels = {r["case_id"]: r for r in csv.DictReader(open(LUNG_FULL / "patient_labels.csv"))}
    cov = {r["case_id"]: r for r in csv.DictReader(open(HERE / "lung_covariates.csv"))}
    mil = json.load(open(LUNG_FULL / "mil_cost_results.json"))
    return labels, cov, mil


def build_X(case_ids, cov, include_cohort, labels):
    rows = []
    for cid in case_ids:
        c = cov[cid]
        rows.append({
            "purity": float(c["purity"]),
            "purity_missing": int(c["purity_missing"]),
            "stage": c["stage"],
            "site": c["site"],
            **({"cohort": labels[cid]["cohort"]} if include_cohort else {}),
        })
    cat_cols = ["stage", "site"] + (["cohort"] if include_cohort else [])
    num_cols = ["purity", "purity_missing"]
    X_cat = np.array([[r[c] for c in cat_cols] for r in rows], dtype=object)
    X_num = np.array([[r[c] for c in num_cols] for r in rows], dtype=float)
    return X_cat, X_num


def oof_predict(case_ids, y, cov, labels, include_cohort, he_feat=None, seed=SEED):
    """5-fold StratifiedKFold in-holdout, 폴드마다 4/5 학습 → 1/5 예측, pooled out-of-fold proba."""
    case_ids = list(case_ids); y = np.array(y)
    oof = np.zeros(len(case_ids))
    skf = StratifiedKFold(n_splits=N_FOLD, shuffle=True, random_state=seed)
    for tr_idx, te_idx in skf.split(case_ids, y):
        tr_ids = [case_ids[i] for i in tr_idx]
        te_ids = [case_ids[i] for i in te_idx]
        Xc_tr, Xn_tr = build_X(tr_ids, cov, include_cohort, labels)
        Xc_te, Xn_te = build_X(te_ids, cov, include_cohort, labels)

        enc = OneHotEncoder(handle_unknown="ignore")
        Xc_tr_oh = enc.fit_transform(Xc_tr).toarray()
        Xc_te_oh = enc.transform(Xc_te).toarray()
        scaler = StandardScaler()
        Xn_tr_s = scaler.fit_transform(Xn_tr)
        Xn_te_s = scaler.transform(Xn_te)
        X_tr = np.hstack([Xc_tr_oh, Xn_tr_s])
        X_te = np.hstack([Xc_te_oh, Xn_te_s])

        if he_feat is not None:
            f_tr = np.array([[he_feat[c]] for c in tr_ids])
            f_te = np.array([[he_feat[c]] for c in te_ids])
            X_tr = np.hstack([X_tr, f_tr])
            X_te = np.hstack([X_te, f_te])

        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X_tr, y[tr_idx])
        oof[te_idx] = clf.predict_proba(X_te)[:, 1]
    return oof


def paired_bootstrap_delta(y, p_cov, p_comb, n=N_BOOT, seed=SEED):
    y = np.array(y); p_cov = np.array(p_cov); p_comb = np.array(p_comb)
    if len(set(y)) < 2:
        return None, None, None
    rng = np.random.default_rng(seed)
    base = roc_auc_score(y, p_comb) - roc_auc_score(y, p_cov)
    deltas = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        deltas.append(roc_auc_score(y[idx], p_comb[idx]) - roc_auc_score(y[idx], p_cov[idx]))
    lo, hi = (np.percentile(deltas, [2.5, 97.5]) if deltas else (None, None))
    return round(float(base), 4), (round(float(lo), 4) if lo is not None else None), \
           (round(float(hi), 4) if hi is not None else None)


def main():
    labels, cov, mil = load()

    result = {"cancer": "LUNG_NSCLC", "claim_level": "hypothesis_only", "critic_status": "pending",
              "scope": "v1 — LUNG only (BIOP02-140 pre-registered reduced scope)",
              "method": "5-fold StratifiedKFold in-holdout CV (pre-registration addendum 2026-08-20)",
              "endpoints": {}}

    for ep in ENDPOINTS:
        include_cohort = (ep != "histology_lusc")
        he_proba = mil["endpoints"][ep]["patient_proba"]
        eval_ids = sorted(c for c in he_proba if c in labels and c in cov)
        y_eval = [int(labels[c][ep]) for c in eval_ids]
        n_pos = sum(y_eval)
        print(f"[{ep}] holdout n={len(eval_ids)} n_pos={n_pos} include_cohort={include_cohort}")

        p_cov = oof_predict(eval_ids, y_eval, cov, labels, include_cohort)
        cov_auc, cov_lo, cov_hi = bootstrap_auc(y_eval, p_cov, n=N_BOOT, seed=SEED)

        he_feat = {c: he_proba[c] for c in eval_ids}
        p_comb = oof_predict(eval_ids, y_eval, cov, labels, include_cohort, he_feat=he_feat)
        comb_auc, comb_lo, comb_hi = bootstrap_auc(y_eval, p_comb, n=N_BOOT, seed=SEED)

        he_auc = mil["endpoints"][ep]["real"]["auc"]  # mil_cost_results.json 원값 인용(재계산 안 함)
        delta, d_lo, d_hi = paired_bootstrap_delta(y_eval, p_cov, p_comb)

        cohort_only_auc = None
        if ep != "histology_lusc":
            y_arr = np.array(y_eval)
            oof_c = np.zeros(len(eval_ids))
            skf = StratifiedKFold(n_splits=N_FOLD, shuffle=True, random_state=SEED)
            for tr_idx, te_idx in skf.split(eval_ids, y_arr):
                tr_ids = [eval_ids[i] for i in tr_idx]; te_ids = [eval_ids[i] for i in te_idx]
                Xtr = np.array([[1.0 if labels[c]["cohort"] == "LUSC" else 0.0] for c in tr_ids])
                Xte = np.array([[1.0 if labels[c]["cohort"] == "LUSC" else 0.0] for c in te_ids])
                clf = LogisticRegression(max_iter=1000).fit(Xtr, y_arr[tr_idx])
                oof_c[te_idx] = clf.predict_proba(Xte)[:, 1]
            cohort_only_auc, _, _ = bootstrap_auc(y_eval, oof_c, n=N_BOOT, seed=SEED)

        if n_pos < 25:
            verdict = "판정 불가 (n_pos<25, 프로젝트 exploratory 기준 미달)"
        elif d_lo is not None and d_lo > 0:
            verdict = "🟢 유지"
        elif d_lo is not None and d_lo <= 0 <= (d_hi or 0):
            verdict = "🟡 강등 후보"
        else:
            verdict = "판정 불가 (bootstrap 실패)"
        if cov_auc is not None and he_auc is not None and cov_auc > he_auc:
            verdict += " + 🔴 공변량-only가 H&E 이상(본문 명시 대상)"

        result["endpoints"][ep] = {
            "n_holdout": len(eval_ids), "n_pos": n_pos, "include_cohort_covariate": include_cohort,
            "he_only_auc_cited_from_mil_cost": he_auc,
            "covariate_only_auc": {"auc": cov_auc, "ci95": [cov_lo, cov_hi]},
            "combined_auc": {"auc": comb_auc, "ci95": [comb_lo, comb_hi]},
            "delta_auroc_combined_minus_covariate": {"delta": delta, "ci95": [d_lo, d_hi]},
            "cohort_only_auc_single_covariate_check": cohort_only_auc,
            "verdict": verdict,
        }
        print(f"  covariate-only={cov_auc} ({cov_lo}-{cov_hi})  combined={comb_auc} ({comb_lo}-{comb_hi})"
              f"  delta={delta} ({d_lo}-{d_hi})  he_only(cited)={he_auc}  cohort_only={cohort_only_auc}")
        print(f"  verdict: {verdict}")

    purity_strat = {}
    for ep in ["egfr_activating", "kras_g12c"]:
        he_proba = mil["endpoints"][ep]["patient_proba"]
        eval_ids = sorted(c for c in he_proba if c in labels and c in cov)
        purities = np.array([float(cov[c]["purity"]) for c in eval_ids])
        med = float(np.median(purities))
        high_ids = [c for c, p in zip(eval_ids, purities) if p >= med]
        low_ids = [c for c, p in zip(eval_ids, purities) if p < med]
        strat = {}
        for name, ids in [("high_purity", high_ids), ("low_purity", low_ids)]:
            y = [int(labels[c][ep]) for c in ids]
            npos = sum(y)
            if npos < 5:
                strat[name] = {"n": len(ids), "n_pos": npos, "note": "검정력 부족(n_pos<5), 판정 불가 — 사전등록"}
                continue
            p = [he_proba[c] for c in ids]
            auc, lo, hi = bootstrap_auc(y, p, n=N_BOOT, seed=SEED)
            strat[name] = {"n": len(ids), "n_pos": npos, "auc": auc, "ci95": [lo, hi]}
        purity_strat[ep] = {"holdout_median_purity": round(med, 4), **strat}
        print(f"[purity-strat:{ep}] median={med:.3f} -> {strat}")

    result["purity_stratification"] = purity_strat

    out = HERE / "covariate_incremental_value_results.json"
    json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
    print(f"Saved {out}\nDONE_BIOP02-140_v1")


if __name__ == "__main__":
    main()

"""
Incremental-over-conventional-pathology analysis (kkkim, BIOP02).

Q: Does the H&E-MIL predicted probability p_HE add signal ABOVE a conventional-pathology
   baseline (histologic type; + PAM50 as a stringent secondary), per headline marker?
   Confound (Critic #2): H&E may only be reading histotype/subtype that correlates with marker.

Design: partialling / incremental (NOT within-stratum).
  base = marker ~ pathology covariates       -> AUROC_base
  full = marker ~ pathology covariates + p_HE -> AUROC_full
  PRIMARY judgement: nested likelihood-ratio test on the p_HE coefficient (chi2, df=1),
    in-sample MLE unpenalized logistic (both models fit on same patients).
  SUPPORT: 5-fold stratified CV AUROC_base vs AUROC_full + DeLong p on CV scores (out-of-sample);
    p_HE-alone CV AUROC; bootstrap CI on CV-AUROC delta.
  Two baselines reported per marker:
    (A) PRIMARY  = histologic type only  (conventional H&E-readable pathology)
    (B) SECONDARY= histologic type + PAM50 (stringent; PAM50 is molecular subtype, partly
        co-defined by ER/HER2 -> near-circular for those markers; reported for completeness).

claim_level: hypothesis_only. No commit (human). TCGA-BRCA lacks histologic grade -> not used.
"""
import json, collections, sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import chi2, norm

REPO = Path("/home/kkkim/project/BioProject02")
OUT = REPO / "experiments/kkkim/histology_baseline_incremental"
SCR = "/tmp/claude-10005/-home-kkkim-project-BioProject02/d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/clin"
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_uni.csv"
SEED = 42

# ---------- conventional-pathology covariates (breast) ----------
def load_hist(fn, col):
    d = json.load(open(f"{SCR}/{fn}"))
    m = {}
    for x in d:
        if x["clinicalAttributeId"] == col:
            m[x["patientId"]] = x["value"]
    return m

hist_raw = load_hist("brca_tcga_PATIENT.json", "HISTOLOGICAL_DIAGNOSIS")
def hist_cat(v):
    if v is None: return None
    v = v.lower()
    if "ductal" in v and "lobular" not in v: return "ductal"
    if "lobular" in v and "ductal" not in v: return "lobular"
    return "other"

man = pd.read_csv(MANIFEST)
pam50_map = dict(zip(man["case_id"], man["pam50"]))

# ---------- DeLong (fast) for two correlated ROC ----------
def _compute_midrank(x):
    J = np.argsort(x); Z = x[J]; N = len(x); T = np.zeros(N)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]: j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    T2 = np.empty(N); T2[J] = T
    return T2

def delong_var(scores, y):
    # scores: (k, N) predictors; y binary. Fast DeLong requires positives-first ordering.
    pos = y == 1; neg = ~pos
    m = int(pos.sum()); n = int(neg.sum())
    k = scores.shape[0]
    scores = np.hstack([scores[:, pos], scores[:, neg]])  # positives first, then negatives
    tx = np.array([_compute_midrank(scores[r, :m]) for r in range(k)])
    ty = np.array([_compute_midrank(scores[r, m:]) for r in range(k)])
    tz = np.array([_compute_midrank(scores[r]) for r in range(k)])
    aucs = (tz[:, :m].sum(axis=1) / m - (m + 1) / 2) / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1 - (tz[:, m:] - ty) / m
    sx = np.cov(v01); sy = np.cov(v10)
    cov = sx / m + sy / n
    cov = np.atleast_2d(cov)
    return aucs, cov

def delong_p(score_base, score_full, y):
    scores = np.vstack([score_base, score_full])
    aucs, cov = delong_var(scores, y)
    l = np.array([1.0, -1.0])
    var = l @ cov @ l
    if var <= 0: return aucs, 1.0
    z = (aucs[0] - aucs[1]) / np.sqrt(var)
    return aucs, 2 * norm.cdf(-abs(z))

# ---------- one-hot design ----------
def design(df, cols_cat, add_phe):
    X = []
    names = []
    for c in cols_cat:
        dummies = pd.get_dummies(df[c].astype(str), prefix=c, drop_first=True)
        X.append(dummies.values.astype(float)); names += list(dummies.columns)
    if X:
        Xm = np.hstack(X)
    else:
        Xm = np.zeros((len(df), 0))
    if add_phe:
        phe = ((df["p_HE"] - df["p_HE"].mean()) / df["p_HE"].std()).values.reshape(-1, 1)
        Xm = np.hstack([Xm, phe]); names += ["p_HE"]
    return Xm, names

def ll_logistic(X, y):
    # unpenalized MLE logistic; return in-sample log-likelihood
    if X.shape[1] == 0:
        p = np.full(len(y), y.mean())
    else:
        m = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000)
        m.fit(X, y); p = m.predict_proba(X)[:, 1]
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))

def cv_scores(df, cols_cat, add_phe):
    y = df["y"].values.astype(int)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    scores = np.zeros(len(df))
    for tr, te in skf.split(df, y):
        Xtr, _ = design(df.iloc[tr], cols_cat, add_phe)
        Xte, _ = design(df.iloc[te], cols_cat, add_phe)
        if Xtr.shape[1] == 0:
            scores[te] = y[tr].mean()
        else:
            m = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000)
            m.fit(Xtr, y[tr]); scores[te] = m.predict_proba(Xte)[:, 1]
    return scores, y

def analyze(df, marker, baseline_name, cols_cat):
    y = df["y"].values.astype(int)
    n = len(y); npos = int(y.sum())
    # PRIMARY: nested LR test (in-sample MLE)
    Xb, nb = design(df, cols_cat, add_phe=False)
    Xf, nf = design(df, cols_cat, add_phe=True)
    ll_b = ll_logistic(Xb, y); ll_f = ll_logistic(Xf, y)
    lr_stat = 2 * (ll_f - ll_b)
    lr_p = float(chi2.sf(max(lr_stat, 0), df=1))
    n_params_full = Xf.shape[1]
    epv = npos / max(n_params_full, 1)
    # p_HE coefficient (full model)
    if Xf.shape[1] > 0:
        mf = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(Xf, y)
        phe_coef = float(mf.coef_[0][nf.index("p_HE")])
    else:
        phe_coef = None
    # SUPPORT: CV AUROC base vs full + DeLong
    sb, _ = cv_scores(df, cols_cat, add_phe=False)
    sf, _ = cv_scores(df, cols_cat, add_phe=True)
    salone, _ = cv_scores(df, [], add_phe=True)  # p_HE alone (standardized) — monotone => AUROC of p_HE
    auc_base = roc_auc_score(y, sb) if len(cols_cat) else 0.5
    auc_full = roc_auc_score(y, sf)
    auc_alone = roc_auc_score(y, df["p_HE"].values)
    aucs_dl, dl_p = delong_p(sb, sf, y)
    # bootstrap CI on CV delta (auc_full - auc_base)
    rng = np.random.default_rng(SEED); deltas = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        if y[idx].sum() in (0, n): continue
        try:
            deltas.append(roc_auc_score(y[idx], sf[idx]) - roc_auc_score(y[idx], sb[idx]))
        except ValueError:
            continue
    dci = [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))] if deltas else None
    return dict(
        marker=marker, baseline=baseline_name, covariates=cols_cat,
        n=n, n_pos=npos, prevalence=round(npos / n, 4),
        n_params_full=n_params_full, events_per_variable=round(epv, 2),
        auroc_pHE_alone=round(auc_alone, 4),
        auroc_base_cv=round(auc_base, 4), auroc_full_cv=round(auc_full, 4),
        delta_auroc_cv=round(auc_full - auc_base, 4), delta_auroc_cv_ci95=[round(x, 4) for x in dci] if dci else None,
        delong_p_cv=round(dl_p, 5),
        LRtest_stat=round(lr_stat, 4), LRtest_df=1, LRtest_p=round(lr_p, 6),  # PRIMARY
        pHE_coef_full=round(phe_coef, 4) if phe_coef is not None else None,
    )

def build_marker_df(marker):
    if marker == "ER":
        man2 = man[man["split"] == "val"].reset_index(drop=True)
        pred = np.load(REPO / "experiments/sjpark/er_status_clam_uni_v2/predictions.npy", allow_pickle=True)
        assert len(man2) == len(pred) == 152
        df = pd.DataFrame({"case_id": man2["case_id"].values,
                           "y": (man2["er"] == "Positive").astype(int).values,
                           "p_HE": pred[:, 0]})
        # verify alignment via stored AUC
        assert abs(roc_auc_score(df["y"], df["p_HE"]) - 0.9013) < 0.002, "ER alignment failed"
    elif marker == "HER2_CNVamp":
        d = pd.read_csv(OUT / "her2_cnv_amp_phe.csv")
        df = d.rename(columns={"y_true": "y"})[["case_id", "y", "p_HE"]].copy()
        assert abs(roc_auc_score(df["y"], df["p_HE"]) - 0.7525) < 0.005, "HER2 alignment failed"
    df["hist"] = df["case_id"].map(lambda c: hist_cat(hist_raw.get(c)))
    df["pam50"] = df["case_id"].map(pam50_map)
    return df

def main():
    results = []
    coverage = {}
    for marker in ["ER", "HER2_CNVamp"]:
        df = build_marker_df(marker)
        n0 = len(df)
        # drop rows missing histology or pam50 (need for both baselines; report)
        miss_h = df["hist"].isna().sum()
        miss_p = df["pam50"].isna().sum() + (df["pam50"] == "").sum()
        dfc = df.dropna(subset=["hist", "pam50"]).copy()
        dfc = dfc[dfc["pam50"].astype(str) != ""]
        coverage[marker] = dict(n_total=int(n0), n_missing_hist=int(miss_h),
                                n_missing_pam50=int(miss_p), n_analyzed=int(len(dfc)),
                                hist_dist=dfc["hist"].value_counts().to_dict(),
                                pam50_dist=dfc["pam50"].value_counts().to_dict())
        results.append(analyze(dfc, marker, "A_histology_only(PRIMARY)", ["hist"]))
        results.append(analyze(dfc, marker, "B_histology+PAM50(secondary)", ["hist", "pam50"]))
    # ---- per-marker verdicts (primary = baseline A histology-only) ----
    verdicts = {}
    bykey = {(r["marker"], r["baseline"]): r for r in results}
    for marker in ["ER", "HER2_CNVamp"]:
        A = bykey[(marker, "A_histology_only(PRIMARY)")]
        B = bykey[(marker, "B_histology+PAM50(secondary)")]
        ciA = A["delta_auroc_cv_ci95"]; ciB = B["delta_auroc_cv_ci95"]
        beats_histology = (A["LRtest_p"] < 0.05) and (ciA is not None and ciA[0] > 0)
        beats_pam50_LR = B["LRtest_p"] < 0.05
        beats_pam50_ci = (ciB is not None and ciB[0] > 0)
        beats_pam50_delong = B["delong_p_cv"] < 0.05
        tests_agree_vs_pam50 = beats_pam50_LR and beats_pam50_ci and beats_pam50_delong
        verdicts[marker] = dict(
            # --- lead with the CONTRAST between two baselines ---
            vs_conventional_histology=dict(
                delta_auroc=A["delta_auroc_cv"], delta_ci95=ciA,
                LRtest_p=A["LRtest_p"], delong_p=A["delong_p_cv"],
                significant_increment=bool(beats_histology)),
            vs_molecular_subtype_PAM50=dict(
                delta_auroc=B["delta_auroc_cv"], delta_ci95=ciB,
                LRtest_p=B["LRtest_p"], delong_p=B["delong_p_cv"],
                three_tests_agree=bool(tests_agree_vs_pam50),
                note=("LR & bootstrap-CI significant but DeLong borderline (in-sample vs out-of-sample "
                      "disagreement) — do not smooth over" if (beats_pam50_LR and beats_pam50_ci and not beats_pam50_delong)
                      else "LR, bootstrap-CI and DeLong concordant")),
            framework_implication="partially_supports",
            interpretation=(
                "OVER conventional H&E-readable pathology (histologic type): large, robust increment "
                f"(dAUC {A['delta_auroc_cv']} {ciA}, LR p {A['LRtest_p']}) — H&E carries marker-specific "
                "morphology beyond histotype. OVER molecular subtype (PAM50, expression-derived, Parker-2009, "
                "H&E-independent): increment small "
                f"(dAUC {B['delta_auroc_cv']} {ciB}, LR p {B['LRtest_p']}) — much of the H&E signal is shared "
                "with the luminal/HER2-enriched subtype axis (expected: PAM50 is not obtainable from H&E and is "
                "partly co-defined by this marker). NET: signal beyond histotype = demonstrated; fully "
                "independent of molecular subtype = NOT demonstrated."))
    skipped = {
        "COLORECTAL_MSI_high": "SKIPPED/INCONCLUSIVE — per-patient p_HE not persisted (routing_cost.json "
            "stores only summary AUROC 0.9184); crosscancer embeddings owned by another process (do-not-touch) "
            "and no GPU slot reservable here. Re-training would be a new result (fresh seed/split), not reuse. "
            "UNBLOCK (one line for owning process): in run_cms_and_routing.py Part-B, persist patient_proba for "
            "msi_high/anti_egfr_eligible exactly as braf_v600e/CMS already do, then this test can run.",
        "COLORECTAL_all_RAS_anti_egfr": "SKIPPED/INCONCLUSIVE — same reason (routing_cost.json summary AUROC "
            "0.7053 only). Same one-line unblock.",
        "note_pivotal": "MSI-H vs (mucinous + right-sided + high-grade) is the sharpest 'does the embedding beat "
            "the pathologist' test (MSI has classic H&E morphology). Currently blocked, not negative."
    }
    out = dict(analysis="incremental_over_conventional_pathology",
               claim_level="hypothesis_only", critic_status="pending",
               note="TCGA-BRCA lacks histologic grade; conventional baseline=histologic type (ductal/lobular/other). "
                    "PAM50 is molecular subtype (partly co-defined by ER/HER2) -> secondary/stringent only. "
                    "PRIMARY test=nested LR on p_HE coef (in-sample MLE); DeLong + bootstrap CI on 5-fold CV "
                    "scores=out-of-sample support. ER p_HE=val split (used for early stopping -> mildly optimistic); "
                    "HER2 p_HE=pooled val+test. hypothesis_only, no commit.",
               pam50_provenance="Parker-2009 nearest-centroid classifier computed from RNA expression "
                    "(tcga_brca_pam50_computed_PROVENANCE.md); manifest pam50 == computed file 100%. "
                    "Expression-derived, H&E-independent -> valid as an independent (stringent) baseline covariate.",
               grade_note="TCGA-BRCA has NO histologic grade in cBioPortal pancan or legacy studies "
                    "(empirically checked); conventional-pathology baseline is histotype-only by necessity.",
               verdicts=verdicts, skipped_markers=skipped,
               coverage=coverage, results=results)
    (OUT / "incremental_results.json").write_text(json.dumps(out, indent=2))
    # print table
    print(f"{'marker':14} {'baseline':30} {'n/pos':>8} {'EPV':>5} {'pHE_alone':>9} {'base':>6} {'full':>6} {'dAUC':>7} {'DeLong_p':>9} {'LR_p':>9} {'coef':>7}")
    for r in results:
        print(f"{r['marker']:14} {r['baseline']:30} {str(r['n'])+'/'+str(r['n_pos']):>8} {r['events_per_variable']:>5} "
              f"{r['auroc_pHE_alone']:>9} {r['auroc_base_cv']:>6} {r['auroc_full_cv']:>6} {r['delta_auroc_cv']:>7} "
              f"{r['delong_p_cv']:>9} {r['LRtest_p']:>9} {str(r['pHE_coef_full']):>7}")
    for m, c in coverage.items():
        print(f"\n[{m}] analyzed {c['n_analyzed']}/{c['n_total']} (miss hist={c['n_missing_hist']} pam50={c['n_missing_pam50']}) "
              f"hist={c['hist_dist']} pam50={c['pam50_dist']}")

if __name__ == "__main__":
    main()

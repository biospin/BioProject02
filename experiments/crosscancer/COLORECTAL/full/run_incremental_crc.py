"""Incremental-over-conventional-pathology analysis for COLORECTAL (kkkim, BIOP02).

Mirror of the BRCA harness (experiments/kkkim/histology_baseline_incremental/run_incremental.py):
does H&E-MIL p_HE add signal ABOVE a conventional-pathology baseline, per treatment marker?

Two markers, two different roles in the pre-registered substitutability law:
  * msi_high            = POSITIVE CONTROL. MSI has classic H&E morphology (mucinous, right-sided,
                          TIL-rich). n_pos=21 < 25 -> EXPLORATORY/INCONCLUSIVE by our own pre-reg
                          power rule, regardless of the number. Reported as corroboration, never as
                          the decider.
  * anti_egfr_eligible  = THE POWERED TEST of the law's risky prediction. anti-EGFR eligibility is
                          RAS/BRAF wild-type status, a pure point-mutation marker (law predicts
                          "no H&E correlate"). n_pos=84 -> can return a conclusive verdict.

Conventional-pathology baseline (PRIMARY) = {mucinous histotype, right/left sidedness}.
  TCGA-COADREAD has NO grade and NO oncotree in cBioPortal patient data (empirically 0/613);
  histotype (ICD_O_3_HISTOLOGY) and sidedness (ICD_O_3_SITE) are the two available covariates and
  happen to be the two textbook MSI correlates -> a fair, not thin, conventional baseline for MSI.
SECONDARY (stringent) = + CMS (molecular consensus subtype; the PAM50 analog, RNA-derived,
  not obtainable from H&E; partly co-defined with MSI via CMS1 -> near-circular, reported for completeness).

INTERPRETATION LIMIT (state up front): TIL density is not a structured TCGA covariate. "Embedding beats
  recorded covariates" is therefore NOT "embedding beats a pathologist who can grade TILs by eye."

claim_level: hypothesis_only. No commit (human). Reuses BRCA harness stats verbatim.
"""
import json, collections, sys, csv
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import chi2, norm

HERE = Path(__file__).parent
REPO = Path("/home/kkkim/project/BioProject02")
BRCA = REPO / "experiments/kkkim/histology_baseline_incremental"
SCR = "/tmp/claude-10005/-home-kkkim-project-BioProject02/d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/crc_clin"
SEED = 42

# ---- reuse BRCA harness stats functions verbatim (import the module) ----
sys.path.insert(0, str(BRCA))
import importlib.util
spec = importlib.util.spec_from_file_location("brca_inc", str(BRCA / "run_incremental.py"))
# NB: importing run_incremental.py executes module-level cBioPortal-breast loads (harmless side effects
# on brca scratch files). To avoid that, we copy only the pure functions below instead of importing.

# ---------- DeLong (copied verbatim from BRCA harness) ----------
def _compute_midrank(x):
    J = np.argsort(x); Z = x[J]; N = len(x); T = np.zeros(N); i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]: j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1; i = j
    T2 = np.empty(N); T2[J] = T; return T2

def delong_var(scores, y):
    pos = y == 1; neg = ~pos; m = int(pos.sum()); n = int(neg.sum()); k = scores.shape[0]
    scores = np.hstack([scores[:, pos], scores[:, neg]])
    tx = np.array([_compute_midrank(scores[r, :m]) for r in range(k)])
    ty = np.array([_compute_midrank(scores[r, m:]) for r in range(k)])
    tz = np.array([_compute_midrank(scores[r]) for r in range(k)])
    aucs = (tz[:, :m].sum(axis=1) / m - (m + 1) / 2) / n
    v01 = (tz[:, :m] - tx) / n; v10 = 1 - (tz[:, m:] - ty) / m
    sx = np.cov(v01); sy = np.cov(v10); cov = np.atleast_2d(sx / m + sy / n)
    return aucs, cov

def delong_p(score_base, score_full, y):
    aucs, cov = delong_var(np.vstack([score_base, score_full]), y)
    l = np.array([1.0, -1.0]); var = l @ cov @ l
    if var <= 0: return aucs, 1.0
    z = (aucs[0] - aucs[1]) / np.sqrt(var); return aucs, 2 * norm.cdf(-abs(z))

def design(df, cols_cat, add_phe):
    X = []; names = []
    for c in cols_cat:
        dummies = pd.get_dummies(df[c].astype(str), prefix=c, drop_first=True)
        X.append(dummies.values.astype(float)); names += list(dummies.columns)
    Xm = np.hstack(X) if X else np.zeros((len(df), 0))
    if add_phe:
        phe = ((df["p_HE"] - df["p_HE"].mean()) / df["p_HE"].std()).values.reshape(-1, 1)
        Xm = np.hstack([Xm, phe]); names += ["p_HE"]
    return Xm, names

def ll_logistic(X, y):
    if X.shape[1] == 0:
        p = np.full(len(y), y.mean())
    else:
        m = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(X, y)
        p = m.predict_proba(X)[:, 1]
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))

def design_cat(df, cols_cat):
    """Categorical dummies built on the WHOLE df -> columns identical across CV folds
    (avoids a rare level dropping out of a train fold and changing the column count)."""
    X = []
    for c in cols_cat:
        dummies = pd.get_dummies(df[c].astype(str), prefix=c, drop_first=True)
        X.append(dummies.values.astype(float))
    return np.hstack(X) if X else np.zeros((len(df), 0))

def cv_scores(df, cols_cat, add_phe):
    y = df["y"].values.astype(int)
    Xcat = design_cat(df, cols_cat)          # consistent columns across folds
    phe = df["p_HE"].values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    scores = np.zeros(len(df))
    for tr, te in skf.split(df, y):
        Xtr, Xte = Xcat[tr], Xcat[te]
        if add_phe:
            mu, sd = phe[tr].mean(), phe[tr].std()  # standardize on train fold only (no leakage)
            ptr = ((phe[tr] - mu) / sd).reshape(-1, 1); pte = ((phe[te] - mu) / sd).reshape(-1, 1)
            Xtr = np.hstack([Xtr, ptr]); Xte = np.hstack([Xte, pte])
        if Xtr.shape[1] == 0:
            scores[te] = y[tr].mean()
        else:
            m = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(Xtr, y[tr])
            scores[te] = m.predict_proba(Xte)[:, 1]
    return scores, y

def analyze(df, marker, baseline_name, cols_cat):
    y = df["y"].values.astype(int); n = len(y); npos = int(y.sum())
    Xb, nb = design(df, cols_cat, add_phe=False); Xf, nf = design(df, cols_cat, add_phe=True)
    ll_b = ll_logistic(Xb, y); ll_f = ll_logistic(Xf, y)
    lr_stat = 2 * (ll_f - ll_b); lr_p = float(chi2.sf(max(lr_stat, 0), df=1))
    n_params_full = Xf.shape[1]; epv = npos / max(n_params_full, 1)
    if Xf.shape[1] > 0:
        mf = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(Xf, y)
        phe_coef = float(mf.coef_[0][nf.index("p_HE")])
    else:
        phe_coef = None
    sb, _ = cv_scores(df, cols_cat, add_phe=False); sf, _ = cv_scores(df, cols_cat, add_phe=True)
    auc_base = roc_auc_score(y, sb) if len(cols_cat) else 0.5
    auc_full = roc_auc_score(y, sf); auc_alone = roc_auc_score(y, df["p_HE"].values)
    _, dl_p = delong_p(sb, sf, y)
    rng = np.random.default_rng(SEED); deltas = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        if y[idx].sum() in (0, n): continue
        try: deltas.append(roc_auc_score(y[idx], sf[idx]) - roc_auc_score(y[idx], sb[idx]))
        except ValueError: continue
    dci = [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))] if deltas else None
    return dict(marker=marker, baseline=baseline_name, covariates=cols_cat, n=n, n_pos=npos,
                prevalence=round(npos / n, 4), n_params_full=n_params_full, events_per_variable=round(epv, 2),
                auroc_pHE_alone=round(auc_alone, 4), auroc_base_cv=round(auc_base, 4),
                auroc_full_cv=round(auc_full, 4), delta_auroc_cv=round(auc_full - auc_base, 4),
                delta_auroc_cv_ci95=[round(x, 4) for x in dci] if dci else None,
                delong_p_cv=round(dl_p, 5), LRtest_stat=round(lr_stat, 4), LRtest_df=1,
                LRtest_p=round(lr_p, 6), pHE_coef_full=round(phe_coef, 4) if phe_coef is not None else None)

# ---------- colorectal covariates ----------
RIGHT = {"C18.0", "C18.1", "C18.2", "C18.3", "C18.4"}   # cecum..transverse (proximal)
LEFT = {"C18.5", "C18.6", "C18.7", "C19.9", "C20.9"}     # splenic flexure..rectum (distal)
def side_cat(v):
    if v in RIGHT: return "right"
    if v in LEFT: return "left"
    return "nos"   # C18.9 colon NOS, C80.9, C49.4
def hist_cat(v):
    if v == "8480/3": return "mucinous"
    if v == "8140/3": return "adenoNOS"
    return "other"

def load_clin():
    d = json.load(open(f"{SCR}/crc_all_patient.json"))
    by = collections.defaultdict(dict)
    for r in d: by[r["patientId"]][r["clinicalAttributeId"]] = r["value"]
    return by

def load_cms():
    m = {}
    for r in csv.DictReader(open(HERE / "cms_labels_authoritative.csv")):
        c = r["cms"]; m[r["case_id"]] = c if c in ("CMS1", "CMS2", "CMS3", "CMS4") else "NOLBL"
    return m

def main():
    phe_all = json.loads((HERE / "treatment_pHE.json").read_text())
    clin = load_clin(); cms = load_cms()
    tx = {r["case_id"]: r for r in csv.DictReader(open(HERE / "labels_treatment.csv"))}

    results = []; coverage = {}; verdicts = {}
    ROLE = {"msi_high": "positive_control(MSI classic H&E morphology; n_pos<25 EXPLORATORY by pre-reg)",
            "anti_egfr_eligible": "POWERED test of law's risky prediction (RAS/BRAF-wt = point-mutation status, 'no correlate')"}
    for marker in ("msi_high", "anti_egfr_eligible"):
        pp = phe_all[marker]["patient_proba"]; pt = phe_all[marker]["patient_true"]
        rows = []
        for c, proba in pp.items():
            cl = clin.get(c, {})
            rows.append(dict(case_id=c, y=int(pt[c]), p_HE=float(proba),
                             hist=hist_cat(cl.get("ICD_O_3_HISTOLOGY")),
                             side=side_cat(cl.get("ICD_O_3_SITE")),
                             cms=cms.get(c, "NOLBL")))
        df = pd.DataFrame(rows)
        n0 = len(df)
        # alignment: p_HE-alone AUROC must match the reproduced summary
        auc_alone = roc_auc_score(df["y"], df["p_HE"])
        tgt = phe_all[marker]["reproduced_auroc"]
        assert abs(auc_alone - tgt) < 0.01, f"{marker} p_HE misaligned {auc_alone} vs {tgt}"
        coverage[marker] = dict(n_total=int(n0), n_pos=int(df["y"].sum()),
                                exploratory_by_prereg=bool(phe_all[marker]["exploratory_by_prereg"]),
                                hist_dist=df["hist"].value_counts().to_dict(),
                                side_dist=df["side"].value_counts().to_dict(),
                                cms_dist=df["cms"].value_counts().to_dict())
        rA = analyze(df, marker, "A_conventional_pathology(PRIMARY)", ["hist", "side"])
        rB = analyze(df, marker, "B_+CMS_molecular(secondary)", ["hist", "side", "cms"])
        results += [rA, rB]
        ciA = rA["delta_auroc_cv_ci95"]
        beats = (rA["LRtest_p"] < 0.05) and (ciA is not None and ciA[0] > 0)
        exploratory = phe_all[marker]["exploratory_by_prereg"]
        verdicts[marker] = dict(
            role=ROLE[marker],
            vs_conventional_pathology=dict(delta_auroc=rA["delta_auroc_cv"], delta_ci95=ciA,
                                           LRtest_p=rA["LRtest_p"], delong_p=rA["delong_p_cv"],
                                           significant_increment=bool(beats)),
            vs_plus_CMS_molecular=dict(delta_auroc=rB["delta_auroc_cv"], delta_ci95=rB["delta_auroc_cv_ci95"],
                                       LRtest_p=rB["LRtest_p"], delong_p=rB["delong_p_cv"]),
            exploratory_by_prereg=bool(exploratory),
            verdict=("INCONCLUSIVE_by_power(n_pos<25) — positive-control corroboration only"
                     if exploratory else
                     ("increment_over_conventional_pathology_DEMONSTRATED" if beats
                      else "NO_increment_over_conventional_pathology")))
    out = dict(analysis="incremental_over_conventional_pathology_COLORECTAL",
               claim_level="hypothesis_only", critic_status="pending",
               conventional_baseline="ICD_O_3 histotype (mucinous/adenoNOS/other) + ICD_O_3 sidedness (right/left/nos). "
                    "TCGA-COADREAD has NO grade/oncotree in cBioPortal patient data (0/613 empirically).",
               interpretation_limit="TIL density is not a structured TCGA covariate; 'beats recorded covariates' is not "
                    "'beats a pathologist who can see TILs'.",
               law_framing="msi_high = positive control (predictable = known morphology). anti_egfr_eligible = the powered "
                    "test of the risky 'no-correlate' prediction. The colorectal verdict on the law rides on anti_egfr, "
                    "not MSI (which is INCONCLUSIVE by our own n_pos<25 rule).",
               verdicts=verdicts, coverage=coverage, results=results)
    (HERE / "incremental_crc_results.json").write_text(json.dumps(out, indent=2))
    print(f"{'marker':20} {'baseline':34} {'n/pos':>8} {'EPV':>5} {'alone':>6} {'base':>6} {'full':>6} {'dAUC':>7} {'DeLong':>8} {'LR_p':>9}")
    for r in results:
        print(f"{r['marker']:20} {r['baseline']:34} {str(r['n'])+'/'+str(r['n_pos']):>8} {r['events_per_variable']:>5} "
              f"{r['auroc_pHE_alone']:>6} {r['auroc_base_cv']:>6} {r['auroc_full_cv']:>6} {r['delta_auroc_cv']:>7} "
              f"{r['delong_p_cv']:>8} {r['LRtest_p']:>9}")
    print()
    for m, v in verdicts.items():
        print(f"[{m}] {v['verdict']}")
        print(f"    vs conventional: dAUC={v['vs_conventional_pathology']['delta_auroc']} "
              f"CI={v['vs_conventional_pathology']['delta_ci95']} LR_p={v['vs_conventional_pathology']['LRtest_p']}")

if __name__ == "__main__":
    main()

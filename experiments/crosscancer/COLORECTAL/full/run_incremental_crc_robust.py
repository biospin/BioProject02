"""Robustness of the colorectal incremental (advisor-requested discriminating check).

The anti_egfr increment over conventional pathology (+0.049, LR p 0.026, DeLong 0.041) is marginal:
all three tests sit just under 0.05, uncorrected across an 8-test grid (4 markers x 2 baselines), and
prior colorectal MIL was seed-fragile. Two checks decide whether "increment" survives:

  (1) Multiple-comparison correction (Bonferroni + Benjamini-Hochberg) on the PRIMARY nested-LR
      p-value grid. LR test is in-sample MLE -> CV-seed-independent, so it is the stable primary.
  (2) CV-seed robustness of the SUPPORT metrics (CV dAUROC, DeLong p) for the powered markers,
      across several StratifiedKFold seeds. If dAUROC flips sign / DeLong crosses 0.05 -> fragile.

If anti_egfr's +0.049 fails correction AND is seed-fragile -> read is "no robust increment for the
point-mutation marker" (law's prediction approximately holds), NOT "binary refuted".
hypothesis_only. Reuses run_incremental_crc.py pure functions (importing it does NOT run main()).
"""
import json, csv, collections
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

import importlib.util, sys
HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("rc", str(HERE / "run_incremental_crc.py"))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)  # defs only, no main()

SEEDS = [42, 0, 1, 7, 2024, 7777, 314]

def cv_delta(df, cols_cat, seed):
    """CV dAUROC (full vs base) and DeLong p at a given fold seed. Same design as run_incremental_crc."""
    y = df["y"].values.astype(int)
    Xcat = rc.design_cat(df, cols_cat); phe = df["p_HE"].values
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    sb = np.zeros(len(df)); sf = np.zeros(len(df))
    for tr, te in skf.split(df, y):
        # base
        Xtr, Xte = Xcat[tr], Xcat[te]
        if Xtr.shape[1] == 0: sb[te] = y[tr].mean()
        else:
            m = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(Xtr, y[tr])
            sb[te] = m.predict_proba(Xte)[:, 1]
        # full (+p_HE, standardized on train fold)
        mu, sd = phe[tr].mean(), phe[tr].std()
        ptr = ((phe[tr] - mu) / sd).reshape(-1, 1); pte = ((phe[te] - mu) / sd).reshape(-1, 1)
        Ftr = np.hstack([Xtr, ptr]); Fte = np.hstack([Xte, pte])
        m2 = LogisticRegression(penalty=None, solver="lbfgs", max_iter=5000).fit(Ftr, y[tr])
        sf[te] = m2.predict_proba(Fte)[:, 1]
    auc_b = roc_auc_score(y, sb) if len(cols_cat) else 0.5
    auc_f = roc_auc_score(y, sf)
    _, dl_p = rc.delong_p(sb, sf, y)
    return auc_f - auc_b, dl_p

def bh(pvals):
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(pvals, float); n = len(p); order = np.argsort(p)
    adj = np.empty(n); prev = 1.0
    for rank in range(n - 1, -1, -1):
        i = order[rank]; val = p[i] * n / (rank + 1); prev = min(prev, val); adj[i] = prev
    return adj

def main():
    phe_all = json.loads((HERE / "treatment_pHE.json").read_text())
    clin = rc.load_clin(); cms = rc.load_cms()
    # rebuild dfs identically to run_incremental_crc
    dfs = {}
    for marker in ("msi_high", "anti_egfr_eligible"):
        pp = phe_all[marker]["patient_proba"]; pt = phe_all[marker]["patient_true"]
        rows = [dict(case_id=c, y=int(pt[c]), p_HE=float(v),
                     hist=rc.hist_cat(clin.get(c, {}).get("ICD_O_3_HISTOLOGY")),
                     side=rc.side_cat(clin.get(c, {}).get("ICD_O_3_SITE")),
                     cms=cms.get(c, "NOLBL")) for c, v in pp.items()]
        dfs[marker] = pd.DataFrame(rows)

    # ---- (1) primary LR grid + correction ----
    # LR p-values are seed-independent; recompute from the saved results grid for all 4 conventional +
    # 4 secondary tests (breast ER/HER2 come from the BRCA file; colorectal from this run).
    brca = json.loads((Path("/home/kkkim/project/BioProject02/experiments/kkkim/histology_baseline_incremental/incremental_results.json")).read_text())
    grid = []  # (label, LR_p, powered)
    for r in brca["results"]:
        base = "conv" if "PRIMARY" in r["baseline"] else "molsub"
        grid.append((f"BRCA/{r['marker']}/{base}", r["LRtest_p"], True))
    crc = json.loads((HERE / "incremental_crc_results.json").read_text())
    for r in crc["results"]:
        base = "conv" if "PRIMARY" in r["baseline"] else "molsub"
        powered = not (r["marker"] == "msi_high")  # msi exploratory by power
        grid.append((f"CRC/{r['marker']}/{base}", r["LRtest_p"], powered))
    labels = [g[0] for g in grid]; pv = [g[1] for g in grid]
    bh_adj = bh(pv); bonf = [min(1.0, p * len(pv)) for p in pv]
    correction = []
    for (lab, p, powered), a, b in zip(grid, bh_adj, bonf):
        correction.append({"test": lab, "LR_p_raw": p, "BH_adj": round(float(a), 5),
                           "Bonferroni": round(float(b), 5), "powered": powered,
                           "survives_BH": bool(a < 0.05), "survives_Bonf": bool(b < 0.05)})

    # ---- (2) CV-seed robustness for the two colorectal markers, conventional baseline ----
    seed_rob = {}
    for marker in ("msi_high", "anti_egfr_eligible"):
        deltas = []; dlps = []
        for s in SEEDS:
            d, dlp = cv_delta(dfs[marker], ["hist", "side"], s)
            deltas.append(round(d, 4)); dlps.append(round(dlp, 4))
        deltas = np.array(deltas); dlps = np.array(dlps)
        seed_rob[marker] = dict(
            baseline="conventional(hist+side)", seeds=SEEDS,
            dAUROC_by_seed=deltas.tolist(), dAUROC_mean=round(float(deltas.mean()), 4),
            dAUROC_min=round(float(deltas.min()), 4), dAUROC_max=round(float(deltas.max()), 4),
            frac_dAUROC_positive=round(float((deltas > 0).mean()), 3),
            delong_p_by_seed=dlps.tolist(),
            frac_delong_sig=round(float((dlps < 0.05).mean()), 3),
            n_pos=int(dfs[marker]["y"].sum()),
            exploratory_by_prereg=bool(marker == "msi_high"))

    out = dict(check="robustness_of_colorectal_incremental (advisor discriminating check)",
               claim_level="hypothesis_only", critic_status="pending",
               primary_metric="nested-LR p (in-sample, CV-seed-independent)",
               correction_grid=correction,
               seed_robustness=seed_rob,
               read_rule="anti_egfr 'increment' counts as ROBUST only if LR_p survives BH AND CV dAUROC "
                         "stays >0 across seeds AND DeLong<0.05 in majority of seeds. Otherwise read = "
                         "'no robust increment for the point-mutation marker' (law's prediction approx holds). "
                         "MSI stays INCONCLUSIVE by power regardless.")
    (HERE / "incremental_crc_robustness.json").write_text(json.dumps(out, indent=2))

    print("=== (1) PRIMARY LR grid + multiple-comparison correction ===")
    print(f"{'test':28} {'LR_p_raw':>10} {'BH_adj':>9} {'Bonf':>9} {'BH<.05':>7} {'Bonf<.05':>9} {'powered':>8}")
    for c in correction:
        print(f"{c['test']:28} {c['LR_p_raw']:>10.2e} {c['BH_adj']:>9.4f} {c['Bonferroni']:>9.4f} "
              f"{str(c['survives_BH']):>7} {str(c['survives_Bonf']):>9} {str(c['powered']):>8}")
    print("\n=== (2) CV-seed robustness (colorectal, conventional baseline) ===")
    for m, r in seed_rob.items():
        print(f"[{m}] n_pos={r['n_pos']} exploratory={r['exploratory_by_prereg']}")
        print(f"    dAUROC by seed {r['dAUROC_by_seed']}  mean={r['dAUROC_mean']} min={r['dAUROC_min']} max={r['dAUROC_max']} frac>0={r['frac_dAUROC_positive']}")
        print(f"    DeLong p by seed {r['delong_p_by_seed']}  frac<0.05={r['frac_delong_sig']}")

if __name__ == "__main__":
    main()

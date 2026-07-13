#!/usr/bin/env python3
"""
Su et al. 2025 IMC (Zenodo 13901180) — CRC "MSI-visible half" at CELL resolution.

Re-attempt of the CRC Angle A after the Visium-spot NULL (COLORECTAL/ST/README.md):
55 um spots were below nuclear resolution. IMC single-cell phenotypes + coordinates
are the resolution-appropriate substrate.

ESTIMAND — ABUNDANCE-CONTROLLED spatial organization (not abundance).
Density colocalization alone would only rediscover "MSI-H is immune-hot" (known biology,
the exact trap flagged in the Visium README). So we separate abundance from pattern:

  (A) Abundance (descriptive positive control, NOT the spatial result):
      lymphocyte fraction per patient, MSI-H vs MSS.

  (B) Pattern (PRIMARY): within-ROI permutation null on cell_type labels
      (positions + counts held fixed) -> abundance-controlled log2 enrichment:
        LL = lymphocyte-lymphocyte adjacency  -> aggregation beyond abundance (TIL hubs)
        LT = lymphocyte-tumor      adjacency  -> infiltration/mixing beyond chance
      log2(obs / null_mean) is scale-free (abundance-controlled effect size);
      z = (obs - null_mean)/null_std is significance-of-organization (inflates with n, secondary).
      Aggregate ROI -> patient (mean), patient = replication unit. MSI vs MSS: Mann-Whitney + effect size.

  (C) Discriminating check the advisor demanded: does the abundance-controlled metric
      still separate MSI/MSS once lymphocyte fraction is regressed out? (residual MSI vs MSS).

SCOPE HONESTY: AreaShape morphology here is IMC-SEGMENTATION morphology, and there is NO
co-registered H&E in this table. So this can show "cell-resolution immune ARCHITECTURE
differs MSI vs MSS" (a real lift over the Visium null) — it CANNOT by itself prove
"H&E-visible". The direct H&E claim needs the v2 H&E_annotations (unregistered pathologist
JPGs, 4 patients) + registration = heavy path, not run here.

claim_level: hypothesis_only · exploratory · patient = replication unit · no pooling.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import mannwhitneyu, spearmanr

HERE = Path(__file__).parent
CSV = Path("/tmp/claude-10005/-home-kkkim-project-BioProject02/"
           "d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/su_singlecell.csv")
MSI_MAP = Path("/tmp/claude-10005/-home-kkkim-project-BioProject02/"
               "d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/msi_map.json")

# Two PRE-DECLARED immune definitions (no post-hoc subset picking):
#  - "lymphocyte": broad adaptive/innate lymphoid compartment
#  - "CD8": cytotoxic compartment named in the hypothesis (CD8/GZMB/PD1)
IMMUNE_SETS = {
    "lymphocyte": {"CD8 T cell", "CD4 T cell", "NK-cells", "B cell", "Proliferative Immune"},
    "CD8":        {"CD8 T cell"},
}
TUMOR = {"Epithelial/Tumor", "Proliferative Tumor", "P53+ Tumor"}
RADII = [20.0, 30.0, 50.0]   # px ~= um (IMC ~1 um/px); primary = 30
RADIUS = 30.0
N_PERM = 500
MIN_LYMPH = 20       # per-ROI: need enough immune cells for a stable null
MIN_EDGES = 100
SEED = 42


def roi_stat(pairs, is_L, is_T, rng):
    """obs + permutation null for LL and LT adjacency counts within one ROI.
    `pairs` = precomputed (E,2) i<j neighbor edges at a given radius."""
    if len(pairs) < MIN_EDGES:
        return None
    src, dst = pairs[:, 0], pairs[:, 1]
    n = len(is_L)

    def counts(L, T):
        n_LL = int(np.sum(L[src] & L[dst]))
        n_LT = int(np.sum((L[src] & T[dst]) | (T[src] & L[dst])))
        return n_LL, n_LT

    obs_LL, obs_LT = counts(is_L, is_T)
    nullLL = np.empty(N_PERM); nullLT = np.empty(N_PERM)
    for k in range(N_PERM):
        p = rng.permutation(n)
        Lp, Tp = is_L[p], is_T[p]
        nullLL[k] = np.sum(Lp[src] & Lp[dst])
        nullLT[k] = np.sum((Lp[src] & Tp[dst]) | (Tp[src] & Lp[dst]))
    eps = 1e-9
    return {
        "n_cells": int(n), "n_edges": int(len(pairs)),
        "n_lymph": int(is_L.sum()), "n_tumor": int(is_T.sum()),
        "obs_LL": obs_LL, "null_LL": float(nullLL.mean()),
        "log2_LL": float(np.log2((obs_LL + eps) / (nullLL.mean() + eps))),
        "z_LL": float((obs_LL - nullLL.mean()) / (nullLL.std() + eps)),
        "obs_LT": obs_LT, "null_LT": float(nullLT.mean()),
        "log2_LT": float(np.log2((obs_LT + eps) / (nullLT.mean() + eps))),
        "z_LT": float((obs_LT - nullLT.mean()) / (nullLT.std() + eps)),
    }


def main():
    df = pd.read_csv(CSV)
    df = df[df.batch == "Cancer"].copy()          # exclude Control (adjacent normal)
    msi = json.load(open(MSI_MAP))

    def status(p):
        v = msi.get(p)
        if v in (True, "True", "TRUE"):  return "MSI-H"
        if v in (False, "False", "FALSE"): return "MSS"
        return None
    df["msi"] = df.alt_identifier.map(status)
    df = df[df.msi.notna()].copy()

    rng = np.random.default_rng(SEED)

    # precompute neighbor edges per ROI per radius (positions are fixed across label defs)
    roi_groups = {(pid, roi): g for (pid, roi), g in df.groupby(["alt_identifier", "Metadata"])}
    edges = {}   # (pid,roi,R) -> pairs
    for (pid, roi), g in roi_groups.items():
        coords = g[["AreaShape_Center_X", "AreaShape_Center_Y"]].to_numpy()
        tree = cKDTree(coords)
        for R in RADII:
            edges[(pid, roi, R)] = tree.query_pairs(R, output_type="ndarray")

    def compare(vals_msih, vals_mss):
        a, b = np.asarray(vals_msih), np.asarray(vals_mss)
        U, p = mannwhitneyu(a, b, alternative="two-sided")
        rbc = 2 * U / (len(a) * len(b)) - 1
        return {"MSI_H_median": round(float(np.median(a)), 4), "MSI_H_mean": round(float(a.mean()), 4),
                "n_MSI_H": len(a), "MSS_median": round(float(np.median(b)), 4),
                "MSS_mean": round(float(b.mean()), 4), "n_MSS": len(b),
                "p_two_sided": round(float(p), 4), "rank_biserial": round(float(rbc), 3)}

    # abundance (patient-level fraction) for each immune definition
    abundance = {}
    for name, S in IMMUNE_SETS.items():
        fr = df.groupby(["alt_identifier", "msi"]).apply(
            lambda g: g.cell_type.isin(S).mean(), include_groups=False).rename("frac").reset_index()
        abundance[name] = compare(fr[fr.msi == "MSI-H"].frac, fr[fr.msi == "MSS"].frac)

    results = {}
    per_patient_all = {}
    for name, S in IMMUNE_SETS.items():
        results[name] = {}
        for R in RADII:
            per_roi = []
            for (pid, roi), g in roi_groups.items():
                is_L = g.cell_type.isin(S).to_numpy()
                is_T = g.cell_type.isin(TUMOR).to_numpy()
                if is_L.sum() < MIN_LYMPH:
                    continue
                r = roi_stat(edges[(pid, roi, R)], is_L, is_T, rng)
                if r is None:
                    continue
                r.update(patient=pid, roi=roi, msi=g.msi.iloc[0])
                per_roi.append(r)
            roi_df = pd.DataFrame(per_roi)
            pat = roi_df.groupby(["patient", "msi"]).agg(
                n_roi=("roi", "nunique"), log2_LL=("log2_LL", "mean"), z_LL=("z_LL", "mean"),
                log2_LT=("log2_LT", "mean"), z_LT=("z_LT", "mean")).reset_index()
            g_msih = pat[pat.msi == "MSI-H"]; g_mss = pat[pat.msi == "MSS"]
            res = {"n_valid_roi": int(len(roi_df)), "n_MSI_H": len(g_msih), "n_MSS": len(g_mss),
                   "LL_aggregation_log2": compare(g_msih.log2_LL, g_mss.log2_LL),
                   "LT_mixing_log2": compare(g_msih.log2_LT, g_mss.log2_LT),
                   "LL_z_secondary": compare(g_msih.z_LL, g_mss.z_LL),
                   "LT_z_secondary": compare(g_msih.z_LT, g_mss.z_LT)}
            results[name][f"R{int(R)}"] = res
            if R == RADIUS:
                # abundance-control residual check on log2_LL at primary radius
                fr = df.groupby("alt_identifier").apply(
                    lambda g: g.cell_type.isin(S).mean(), include_groups=False).rename("frac")
                pat = pat.merge(fr, left_on="patient", right_index=True)
                x, y = pat.frac.to_numpy(), pat.log2_LL.to_numpy()
                b1, b0 = np.polyfit(x, y, 1); pat["resid"] = y - (b1 * x + b0)
                rho, prho = spearmanr(x, y)
                res["abundance_control_check"] = {
                    "spearman_log2LL_vs_frac": round(float(rho), 3), "p": round(float(prho), 4),
                    "residual_MSI_vs_MSS": compare(pat[pat.msi == "MSI-H"].resid, pat[pat.msi == "MSS"].resid)}
                per_patient_all[name] = pat.round(4).to_dict(orient="records")
                if name == "lymphocyte":
                    roi_df.round(4).to_csv(HERE / "per_roi_metrics.csv", index=False)

    out = {
        "dataset": "Su et al. 2025 npj Precision Oncology (PMC11973205), IMC single-cell, Zenodo 13901180",
        "claim_level": "hypothesis_only", "evidence_strength": "exploratory",
        "estimand": "abundance-controlled within-ROI permutation enrichment; log2(obs/null) scale-free "
                    "effect (LL=immune aggregation, LT=immune-tumor mixing); z secondary; patient=unit",
        "params": {"primary_radius_px_um": RADIUS, "radii_tested": RADII, "n_perm": N_PERM,
                   "min_immune_per_roi": MIN_LYMPH, "min_edges": MIN_EDGES,
                   "immune_sets": {k: sorted(v) for k, v in IMMUNE_SETS.items()}, "tumor_types": sorted(TUMOR)},
        "cohort": {"n_patients": 40, "n_MSI_H": 8, "n_MSS": 32,
                   "cell_type_note": "cell_type is marker-defined (CD8a/CD3/GranzB/etc.); MSI from WES (Suppl Table 2)"},
        "abundance_positive_control": abundance,
        "spatial_pattern": results,
        "per_patient_primary": per_patient_all,
        "scope_caveat": "No co-registered H&E in this path; AreaShape=IMC segmentation morphology, not H&E texture. "
                        "Shows cell-resolution IMMUNE ARCHITECTURE MSI vs MSS, NOT direct H&E-visibility. "
                        "v2 H&E_annotations (Zenodo 14602539, 3.8MB) = unregistered pathologist JPGs for 4 patients "
                        "(CR014/CR020/CR034/CR048) -> qualitative only; registration = heavy path, not run.",
    }
    (HERE / "su_imc_msi_colocation.json").write_text(json.dumps(out, indent=2))

    print("cohort: 40 patients (8 MSI-H / 32 MSS)")
    print("\n== ABUNDANCE (positive control, patient-level fraction) ==")
    for name in IMMUNE_SETS:
        c = abundance[name]
        print(f"  {name:11s} MSI-H med={c['MSI_H_median']:.3f}  MSS med={c['MSS_median']:.3f}  "
              f"p={c['p_two_sided']:.3f}  rbc={c['rank_biserial']:+.2f}")
    print("\n== SPATIAL PATTERN (abundance-controlled log2 enrichment) ==")
    for name in IMMUNE_SETS:
        for metric in ["LL_aggregation_log2", "LT_mixing_log2"]:
            c = results[name][f"R{int(RADIUS)}"][metric]
            print(f"  {name:11s} {metric:20s} MSI-H med={c['MSI_H_median']:+.3f}  "
                  f"MSS med={c['MSS_median']:+.3f}  p={c['p_two_sided']:.3f}  rbc={c['rank_biserial']:+.2f}")
    print("\n== radius sensitivity (LL log2 p-values) ==")
    for name in IMMUNE_SETS:
        ps = {r: results[name][r]["LL_aggregation_log2"]["p_two_sided"] for r in results[name]}
        print(f"  {name:11s} {ps}")
    return out


if __name__ == "__main__":
    main()

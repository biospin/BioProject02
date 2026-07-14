#!/usr/bin/env python3
"""
CRC "Angle A" — spatial test of the cost-of-substitution asymmetry hypothesis, ported from
the breast ERBB2-floor method (Andersson HER2+ ST, analyze_v2_overlap.py).

HYPOTHESIS (a priori, two symmetric halves on SAME data / SAME processing):
  (1) MSI-visible : IFN-γ / cytotoxic immune signature COLOCALIZES with H&E cellularity
                    -> morphology correlate exists -> H&E can partly substitute MSI testing.
  (2) RAS-silent  : MAPK-pathway downstream ACTIVITY proxy does NOT colocalize with H&E
                    -> no morphology correlate -> H&E cannot substitute -> high cost.
  Load-bearing contrast = within-sample Δρ = ρ_immune − ρ_MAPK (same spots, same norm).

RESULT (see JSONs): the predicted spatial asymmetry is NOT observed at Visium-spot / hires
resolution. |Δρ|<0.1, sign-inconsistent across 4 samples, and in CMS1/MSI immune does NOT
colocalize more than MAPK. Attributed to (a) resolution (55µm spot ≈ 14 px in 2000-px hires,
below nuclear resolution — the imCMS/Kather MSI-from-H&E signal lives in cell-scale texture
not accessible here) and (b) the shared-cellularity confound (Δρ differences it out, leaving
tiny effects). This is "not demonstrable at this substrate", NOT a biological refutation.
The one robust positive is EXPRESSION-level (CMS1 immune-hot vs CMS2 immune-cold), which
supports "an immune program exists in MSI" but NOT "it is H&E-visible."

Method port: threshold-free rank statistic (Spearman ρ of score vs continuous H&E density —
no arbitrary cut), spot-stratified bootstrap CI B=2000 (WITHIN-sample only; optimistic under
spatial autocorrelation — read effect size + cross-sample sign-consistency, not CI stars),
interior-only (hex 6-neighbor) edge control, patient=unit / no pooling. Density proxy =
hematoxylin optical density (nuclei-specific; positive control ρ(totalUMI,hem)=0.36–0.52).
Mean-darkness proxy kept as a SENSITIVITY check (Δρ sign flips between proxies — reported).

Data: GSE285505 (Iwane/Kyoto, Visium FFPE probe panel, 17,943 targeted genes).
claim_level: hypothesis_only ; critic_status: pending ; evidence_strength: exploratory
"""
import gzip, json
from pathlib import Path
import numpy as np, pandas as pd
import h5py
from scipy import sparse
from scipy.stats import spearmanr, rankdata
from sklearn.metrics import roc_auc_score
from PIL import Image

HERE = Path(__file__).parent
DATA = HERE / "data"
B = 2000
SEED = 42
Image.MAX_IMAGE_PIXELS = None

SAMPLES = {
    "GSM8703565": ("sample24", "CMS1", "MSI-immune (target)"),
    "GSM8703566": ("sample26", "CMS2", "canonical / MSS (control)"),
    "GSM8703563": ("sample19", "CMS4", "mesenchymal / stroma-rich"),
    "GSM8703564": ("sample20", "CMS4", "mesenchymal / stroma-rich"),
}
IMMUNE = ["CD8A", "GZMB", "STAT1", "GBP1", "IRF1", "CXCL9", "CXCL10"]
MAPK   = ["DUSP4", "DUSP6", "SPRY2", "ETV4", "ETV5", "PHLDA1", "AREG", "EREG"]
EPITH  = ["EPCAM", "KRT8", "KRT18", "KRT19", "CEACAM5"]
LYMPH  = ["CD8A", "GZMB"]           # lymphocyte-specific null cross-check
HOUSEKEEP = ["ACTB", "B2M"]         # depth-comparability control

# Ruifrok–Johnston H&E OD deconvolution (standard reference vectors)
_M = np.array([[0.65, 0.70, 0.29], [0.07, 0.99, 0.11], [0.27, 0.57, 0.78]])
_M = _M / np.linalg.norm(_M, axis=1, keepdims=True)
_MINV = np.linalg.inv(_M)


def hematoxylin_od(img):
    rgb = img.astype(float) + 1.0
    od = -np.log10(rgb / 256.0)
    hema = (od.reshape(-1, 3) @ _MINV)[:, 0].reshape(img.shape[0], img.shape[1])
    return hema  # higher = more nuclei (hematoxylin)


def load_sample(gsm):
    with h5py.File(DATA / f"{gsm}_filtered_feature_bc_matrix.h5", "r") as f:
        m = f["matrix"]
        X = sparse.csc_matrix((m["data"][:], m["indices"][:], m["indptr"][:]),
                              shape=tuple(m["shape"][:]))
        names = np.array([x.decode() for x in m["features"]["name"][:]])
        barcodes = np.array([b.decode() for b in m["barcodes"][:]])
    total_umi = np.asarray(X.sum(axis=0)).ravel()
    sf = total_umi.astype(float).copy(); sf[sf == 0] = 1.0
    Xn = X.multiply(1.0 / sf).multiply(1e4).tocsr(); Xn.data = np.log1p(Xn.data)
    n2r = {n: i for i, n in enumerate(names)}

    def detect(genes):
        Xr = X.tocsr()
        rec = {}
        for g in genes:
            if g in n2r:
                row = Xr[n2r[g]].toarray().ravel()
                rec[g] = {"detect_frac": round(float((row > 0).mean()), 3),
                          "mean_count": round(float(row.mean()), 3)}
            else:
                rec[g] = "미확보 (not on probe panel)"
        return rec

    def score(genes):
        pres = [g for g in genes if g in n2r]; miss = [g for g in genes if g not in n2r]
        if not pres:
            return np.full(X.shape[1], np.nan), pres, miss
        sub = Xn[[n2r[g] for g in pres], :].toarray()
        mu = sub.mean(1, keepdims=True); sd = sub.std(1, keepdims=True); sd[sd == 0] = 1.0
        return ((sub - mu) / sd).mean(0), pres, miss

    imm, imm_p, imm_m = score(IMMUNE)
    mpk, mpk_p, mpk_m = score(MAPK)
    epi, _, _ = score(EPITH)
    lymph, _, _ = score(LYMPH)          # CD8A+GZMB-only (lymphocyte-specific)
    df = pd.DataFrame({"barcode": barcodes, "immune": imm, "mapk": mpk,
                       "epith": epi, "lymph": lymph, "total_umi": total_umi})
    # depth-comparability control block (guards against depth-artifact in the expression positive)
    Xr = X.tocsr()
    depth_ctrl = {"median_umi": int(np.median(total_umi)),
                  "housekeeping_detect": {g: (round(float((Xr[n2r[g]].toarray().ravel() > 0).mean()), 3)
                                              if g in n2r else "미확보") for g in HOUSEKEEP},
                  "ifn_cp10k_mean": {g: (round(float(Xn[n2r[g]].toarray().ravel().mean()), 3)
                                         if g in n2r else "미확보") for g in ["STAT1", "GBP1", "IRF1", "CXCL9"]}}

    pos = pd.read_csv(gzip.open(DATA / f"{gsm}_tissue_positions_list.csv.gz"), header=None,
                      names=["barcode", "in_tissue", "row", "col", "pxl_row", "pxl_col"])
    pos = pos[pos["in_tissue"] == 1]
    df = df.merge(pos, on="barcode", how="inner")

    sc = json.loads(gzip.open(DATA / f"{gsm}_scalefactors_json.json.gz").read().decode())
    hs = sc["tissue_hires_scalef"]
    r = max(4, int(round(sc["spot_diameter_fullres"] * hs / 2)))
    img = np.array(Image.open(DATA / f"{gsm}_tissue_hires_image.png").convert("RGB"))
    hema = hematoxylin_od(img); gray = img.mean(2)
    H, W = hema.shape
    hem_d, dark_d = [], []
    for _, s in df.iterrows():
        y = int(round(s["pxl_row"] * hs)); x = int(round(s["pxl_col"] * hs))
        y0, y1 = max(0, y - r), min(H, y + r + 1); x0, x1 = max(0, x - r), min(W, x + r + 1)
        ph = hema[y0:y1, x0:x1]; pg = gray[y0:y1, x0:x1]
        hem_d.append(float(ph.mean()) if ph.size else np.nan)
        dark_d.append(float(1 - pg.mean() / 255) if pg.size else np.nan)
    df["density_hem"] = hem_d          # PRIMARY morphology proxy (nuclei-specific)
    df["density_dark"] = dark_d        # SENSITIVITY proxy (generic darkness)

    occ = set(zip(df["row"], df["col"]))
    def interior(rr, cc):
        nb = [(rr, cc - 2), (rr, cc + 2), (rr - 1, cc - 1), (rr - 1, cc + 1),
              (rr + 1, cc - 1), (rr + 1, cc + 1)]
        return all(n in occ for n in nb)
    df["interior"] = [interior(rr, cc) for rr, cc in zip(df["row"], df["col"])]
    return df, {"immune": detect(IMMUNE), "mapk": detect(MAPK)}, (imm_m, mpk_m), depth_ctrl


def rho_ci(x, y, seed=SEED):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y)); x, y = x[ok], y[ok]
    if len(x) < 10:
        return None, None, int(len(x))
    rho = float(spearmanr(x, y).statistic)
    rng = np.random.default_rng(seed); n = len(x); rx, ry = rankdata(x), rankdata(y); vals = []
    for _ in range(B):
        idx = rng.integers(0, n, n); a, b = rx[idx], ry[idx]
        if a.std() and b.std():
            vals.append(float(np.corrcoef(a, b)[0, 1]))
    ci = [round(float(q), 3) for q in np.percentile(vals, [2.5, 97.5])] if vals else None
    return round(rho, 3), ci, int(len(x))


def delta_rho(df, dens="density_hem", seed=SEED):
    x = df[dens].values; imm = df["immune"].values; mpk = df["mapk"].values
    ok = ~(np.isnan(x) | np.isnan(imm) | np.isnan(mpk)); x, imm, mpk = x[ok], imm[ok], mpk[ok]
    if len(x) < 10:
        return None, None
    rx, ri, rm = rankdata(x), rankdata(imm), rankdata(mpk)
    d = float(np.corrcoef(rx, ri)[0, 1] - np.corrcoef(rx, rm)[0, 1])
    rng = np.random.default_rng(seed); n = len(x); dv = []
    for _ in range(B):
        idx = rng.integers(0, n, n); a, bi, bm = rx[idx], ri[idx], rm[idx]
        if a.std() and bi.std() and bm.std():
            dv.append(float(np.corrcoef(a, bi)[0, 1] - np.corrcoef(a, bm)[0, 1]))
    ci = [round(float(q), 3) for q in np.percentile(dv, [2.5, 97.5])] if dv else None
    return round(d, 3), ci


def compartment_theta(df, score):
    """Template-port Θ: immune enrichment in stroma vs tumor(epithelial-high) compartment.
    Θ_stroma = AUC(y=stroma, x=score) = P(stroma spot score > tumor spot score).
    Measures immune COMPARTMENTALIZATION, NOT H&E visibility (won't rescue headline)."""
    d = df.dropna(subset=["epith", score])
    if len(d) < 60:
        return None
    lo, hi = np.percentile(d["epith"], [33.3, 66.7])
    tumor = d[d["epith"] >= hi]; stroma = d[d["epith"] <= lo]
    if len(tumor) < 20 or len(stroma) < 20:
        return None
    y = np.r_[np.ones(len(stroma)), np.zeros(len(tumor))]
    x = np.r_[stroma[score].values, tumor[score].values]
    return round(float(roc_auc_score(y, x)), 3)


def run():
    per = []
    for gsm, (lab, cms, role) in SAMPLES.items():
        df, detect, missing, depth_ctrl = load_sample(gsm)
        di = df[df["interior"]]
        rho_i_h, ci_i_h, n = rho_ci(df["immune"], df["density_hem"])
        rho_m_h, ci_m_h, _ = rho_ci(df["mapk"], df["density_hem"])
        rho_lymph_h, ci_lymph_h, _ = rho_ci(df["lymph"], df["density_hem"])
        rho_i_int, ci_i_int, _ = rho_ci(di["immune"], di["density_hem"])
        rho_m_int, ci_m_int, _ = rho_ci(di["mapk"], di["density_hem"])
        rho_i_d, _, _ = rho_ci(df["immune"], df["density_dark"])
        rho_m_d, _, _ = rho_ci(df["mapk"], df["density_dark"])
        drho_h, drho_h_ci = delta_rho(df, "density_hem")
        drho_d, drho_d_ci = delta_rho(df, "density_dark")
        rho_umi, ci_umi, _ = rho_ci(df["total_umi"], df["density_hem"])
        rec = {
            "gsm": gsm, "sample": lab, "cms": cms, "role": role, "n_spots": int(len(df)),
            "n_interior": int(df["interior"].sum()),
            "PRIMARY_density_proxy": "hematoxylin_OD",
            "poscontrol_rho_totalUMI_vs_hem": rho_umi, "poscontrol_ci95": ci_umi,
            "rho_immune_vs_hem": rho_i_h, "rho_immune_vs_hem_ci95": ci_i_h,
            "rho_mapk_vs_hem": rho_m_h, "rho_mapk_vs_hem_ci95": ci_m_h,
            "rho_lymph_CD8A_GZMB_only_vs_hem": rho_lymph_h,
            "rho_lymph_only_vs_hem_ci95": ci_lymph_h,
            "depth_control": depth_ctrl,
            "rho_immune_interior": rho_i_int, "rho_immune_interior_ci95": ci_i_int,
            "rho_mapk_interior": rho_m_int, "rho_mapk_interior_ci95": ci_m_int,
            "delta_rho_immune_minus_mapk_HEM": drho_h, "delta_rho_HEM_ci95": drho_h_ci,
            "delta_rho_immune_minus_mapk_DARK": drho_d, "delta_rho_DARK_ci95": drho_d_ci,
            "sensitivity_rho_immune_vs_darkness": rho_i_d,
            "sensitivity_rho_mapk_vs_darkness": rho_m_d,
            "compartment_theta_immune_stroma_vs_tumor": compartment_theta(df, "immune"),
            "compartment_theta_mapk_stroma_vs_tumor": compartment_theta(df, "mapk"),
            "gene_detection": detect,
            "genes_missing": {"immune": missing[0], "mapk": missing[1]},
        }
        per.append(rec)
    (HERE / "_per_sample.json").write_text(json.dumps(per, indent=2, ensure_ascii=False))

    # console
    print(f"{'sample':9}{'cms':6}{'ρi_hem':>8}{'ρm_hem':>8}{'Δρ_hem':>8}{'Δρ_dark':>9}{'umi_ctl':>9}")
    for r in per:
        print(f"{r['sample']:9}{r['cms']:6}{str(r['rho_immune_vs_hem']):>8}{str(r['rho_mapk_vs_hem']):>8}"
              f"{str(r['delta_rho_immune_minus_mapk_HEM']):>8}{str(r['delta_rho_immune_minus_mapk_DARK']):>9}"
              f"{str(r['poscontrol_rho_totalUMI_vs_hem']):>9}")
    return per


if __name__ == "__main__":
    run()
    print("wrote _per_sample.json")

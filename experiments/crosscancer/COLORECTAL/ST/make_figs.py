#!/usr/bin/env python3
"""CRC Angle A figures — honest exploratory (null spatial asymmetry, resolution-limited).
fig_crc_st_msi_visible.png / fig_crc_st_ras_silent.png. English labels, constrained_layout."""
import gzip, json
from pathlib import Path
import numpy as np, pandas as pd, h5py
from scipy import sparse
from scipy.stats import rankdata
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})
HERE = Path(__file__).parent; DATA = HERE / "data"
per = json.load(open(HERE / "_per_sample.json"))
by = {r["cms"]: r for r in per}
CMS_ORDER = ["CMS1", "CMS2", "CMS4", "CMS4"]
GSM = {"CMS1": "GSM8703565", "CMS2": "GSM8703566"}
IMMUNE = ["CD8A", "GZMB", "STAT1", "GBP1", "IRF1", "CXCL9", "CXCL10"]
MAPK = ["DUSP4", "DUSP6", "SPRY2", "ETV4", "ETV5", "PHLDA1", "AREG", "EREG"]
_M = np.array([[0.65, 0.70, 0.29], [0.07, 0.99, 0.11], [0.27, 0.57, 0.78]])
_M = _M / np.linalg.norm(_M, axis=1, keepdims=True); _MINV = np.linalg.inv(_M)


def load(gsm, genes):
    with h5py.File(DATA / f"{gsm}_filtered_feature_bc_matrix.h5") as f:
        m = f["matrix"]; X = sparse.csc_matrix((m["data"][:], m["indices"][:], m["indptr"][:]),
                                                shape=tuple(m["shape"][:]))
        names = np.array([x.decode() for x in m["features"]["name"][:]])
        bc = np.array([b.decode() for b in m["barcodes"][:]])
    umi = np.asarray(X.sum(0)).ravel(); sf = umi.astype(float).copy(); sf[sf == 0] = 1
    Xn = X.multiply(1 / sf).multiply(1e4).tocsr(); Xn.data = np.log1p(Xn.data)
    n2r = {n: i for i, n in enumerate(names)}
    rows = [n2r[g] for g in genes if g in n2r]
    sub = Xn[rows, :].toarray(); mu = sub.mean(1, keepdims=True); sd = sub.std(1, keepdims=True); sd[sd == 0] = 1
    score = ((sub - mu) / sd).mean(0)
    pos = pd.read_csv(gzip.open(DATA / f"{gsm}_tissue_positions_list.csv.gz"), header=None,
                      names=["barcode", "in_tissue", "row", "col", "pxl_row", "pxl_col"])
    pos = pos[pos.in_tissue == 1].merge(pd.DataFrame({"barcode": bc, "score": score, "umi": umi}), on="barcode")
    sc = json.loads(gzip.open(DATA / f"{gsm}_scalefactors_json.json.gz").read().decode()); hs = sc["tissue_hires_scalef"]
    img = np.array(Image.open(DATA / f"{gsm}_tissue_hires_image.png").convert("RGB"))
    return pos, img, hs, sc


def hema(img):
    od = -np.log10((img.astype(float) + 1) / 256.0)
    return (od.reshape(-1, 3) @ _MINV)[:, 0].reshape(img.shape[0], img.shape[1])


def panel_overlay(ax, pos, img, hs, title, cmap="magma"):
    ax.imshow(img); ax.set_xticks([]); ax.set_yticks([])
    x = pos.pxl_col * hs; y = pos.pxl_row * hs
    s = pos["score"].values; vmin, vmax = np.percentile(s, [5, 95])
    sc = ax.scatter(x, y, c=s, cmap=cmap, s=5, vmin=vmin, vmax=vmax, alpha=0.85, linewidths=0)
    ax.set_title(title, fontsize=8.5, loc="left")
    plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.02, label="signature z")


def panel_forest(ax, key, ctr_key, title, hi_label, lo_label, xmax=0.35):
    labs = [f"{r['sample']}\n{r['cms']}" for r in per]
    rho = [r[key] for r in per]; ci = [r[key + "_ci95"] for r in per]
    ctr = [r[ctr_key] for r in per]
    y = np.arange(len(per))[::-1]
    for yi, r, c in zip(y, rho, ci):
        if c: ax.plot(c, [yi, yi], color="#37527a", lw=2, zorder=2)
    ax.scatter(rho, y, s=45, color="#37527a", zorder=3, label=hi_label, edgecolors="white", linewidths=0.7)
    ax.scatter(ctr, y, s=38, color="#d1495b", marker="s", zorder=3, label=lo_label, alpha=0.8)
    ax.axvline(0, ls="--", lw=1, color="gray")
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=7.5)
    ax.set_xlim(-0.15, xmax); ax.set_xlabel("Spearman ρ (signature vs H&E hematoxylin density)")
    ax.set_title(title, fontsize=8.5, loc="left"); ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.grid(axis="x", ls=":", lw=0.5, alpha=0.5)


# ============ FIG 1: MSI-visible ============
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), constrained_layout=True,
                         gridspec_kw={"width_ratios": [1, 1, 1.15]})
p1, im1, hs1, _ = load(GSM["CMS1"], IMMUNE)
panel_overlay(axes[0], p1, im1, hs1, "A  CMS1/MSI (sample24) — immune signature on H&E\n(IFN-γ/cytotoxic; no visible clustering to dense regions)")
# expression contrast bar
ax = axes[1]
genes = ["STAT1", "GBP1", "IRF1", "CXCL9"]
c1 = [by["CMS1"]["gene_detection"]["immune"][g]["detect_frac"] for g in genes]
c2 = [by["CMS2"]["gene_detection"]["immune"][g]["detect_frac"] for g in genes]
xx = np.arange(len(genes)); w = 0.38
ax.bar(xx - w / 2, c1, w, label="CMS1 / MSI", color="#37527a")
ax.bar(xx + w / 2, c2, w, label="CMS2 / MSS", color="#c9c9c9", edgecolor="black", lw=0.4)
ax.set_xticks(xx); ax.set_xticklabels(genes, fontsize=8); ax.set_ylabel("spot detection fraction")
ax.set_title("B  EXPRESSION-level immune-hot vs cold (real)\nNOT a spatial-morphology correlate", fontsize=8.5, loc="left")
ax.legend(fontsize=7.5, frameon=False)
panel_forest(axes[2], "rho_immune_vs_hem", "rho_mapk_vs_hem",
             "C  Spatial colocalization ρ — NULL/not demonstrable\nimmune ρ≈0 in MSI, not > MAPK; sign varies by sample",
             "immune signature", "MAPK proxy (ref)")
fig.suptitle("CRC Angle A — MSI-visible half: immune program is EXPRESSION-real but H&E-morphology colocalization "
             "is NOT demonstrable at Visium-spot/hires resolution (exploratory, n_MSI=1, hypothesis-only)",
             fontsize=9.3, fontweight="bold")
fig.savefig(HERE / "fig_crc_st_msi_visible.png", dpi=190, bbox_inches="tight")
plt.close(fig)

# ============ FIG 2: RAS-silent ============
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), constrained_layout=True,
                         gridspec_kw={"width_ratios": [1, 1, 1.15]})
p1m, im1m, hs1m, _ = load(GSM["CMS1"], MAPK)
panel_overlay(axes[0], p1m, im1m, hs1m, "A  CMS1 (sample24) — MAPK activity proxy on H&E\n(DUSP4/6,SPRY2,ETV4/5,PHLDA1,AREG,EREG)", cmap="viridis")
# Δρ bars both proxies
ax = axes[1]
dh = [r["delta_rho_immune_minus_mapk_HEM"] for r in per]
dd = [r["delta_rho_immune_minus_mapk_DARK"] for r in per]
labs = [f"{r['cms']}" for r in per]; xx = np.arange(len(per)); w = 0.38
ax.bar(xx - w / 2, dh, w, label="hematoxylin proxy", color="#37527a")
ax.bar(xx + w / 2, dd, w, label="darkness proxy (sens.)", color="#e0a458", edgecolor="black", lw=0.4)
ax.axhline(0, color="gray", lw=1)
ax.set_xticks(xx); ax.set_xticklabels(labs, fontsize=8); ax.set_ylim(-0.12, 0.12)
ax.set_ylabel("Δρ = ρ_immune − ρ_MAPK")
ax.set_title("B  Asymmetry contrast Δρ — near-zero, sign-inconsistent\nand FLIPS between proxies (CMS1: −.083 vs +.064)", fontsize=8.5, loc="left")
ax.legend(fontsize=7.5, frameon=False)
panel_forest(axes[2], "rho_mapk_vs_hem", "poscontrol_rho_totalUMI_vs_hem",
             "C  MAPK proxy ρ — 'NOT silent' (weak +0.08–0.17)\npos-control totalUMI↔hem 0.36–0.52 validates proxy",
             "MAPK proxy", "totalUMI (pos-ctrl)", xmax=0.6)
fig.suptitle("CRC Angle A — RAS-silent half: MAPK proxy is ACTIVITY-based (no KRAS status), weakly POSITIVE with "
             "cellularity ('not silent'); visible/silent asymmetry NOT observed (exploratory, hypothesis-only)",
             fontsize=9.3, fontweight="bold")
fig.savefig(HERE / "fig_crc_st_ras_silent.png", dpi=190, bbox_inches="tight")
plt.close(fig)
print("wrote fig_crc_st_msi_visible.png, fig_crc_st_ras_silent.png")

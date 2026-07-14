#!/usr/bin/env python3
"""Figure for Su IMC MSI co-location (abundance vs abundance-controlled spatial pattern)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
d = json.load(open(HERE / "su_imc_msi_colocation.json"))
pp = d["per_patient_primary"]     # {"lymphocyte":[...], "CD8":[...]}

COL = {"MSI-H": "#c0392b", "MSS": "#2c3e50"}


def strip(ax, recs, col, title, ylab, hline=None):
    for i, grp in enumerate(["MSS", "MSI-H"]):
        v = [r[col] for r in recs if r["msi"] == grp]
        x = np.random.default_rng(0).normal(i, 0.06, len(v))
        ax.scatter(x, v, s=26, color=COL[grp], alpha=0.75, edgecolor="w", linewidth=0.4, zorder=3)
        ax.hlines(np.median(v), i - 0.22, i + 0.22, color=COL[grp], lw=2.4, zorder=4)
    if hline is not None:
        ax.axhline(hline, color="grey", ls="--", lw=0.9, zorder=1)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["MSS\n(n=32)", "MSI-H\n(n=8)"])
    ax.set_title(title, fontsize=10.5); ax.set_ylabel(ylab, fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)


fig, ax = plt.subplots(1, 4, figsize=(15, 4.2))

# panel A: CD8 abundance (patient fraction) -- positive control
strip(ax[0], pp["CD8"], "frac", "A. CD8 abundance\n(positive control)", "CD8 fraction / patient")
c = d["abundance_positive_control"]["CD8"]
ax[0].text(0.5, 0.97, f"p={c['p_two_sided']}  rbc={c['rank_biserial']:+.2f}\n(1.6x, NS)",
           transform=ax[0].transAxes, ha="center", va="top", fontsize=8.5)

# panel B: lymphocyte LL aggregation (abundance-controlled)
strip(ax[1], pp["lymphocyte"], "log2_LL", "B. Lymphocyte aggregation\n(abundance-controlled)",
      "log2(obs/null) LL", hline=0)
c = d["spatial_pattern"]["lymphocyte"]["R30"]["LL_aggregation_log2"]
ax[1].text(0.5, 0.03, f"both >0 (hubs in BOTH)\np={c['p_two_sided']}  rbc={c['rank_biserial']:+.2f}",
           transform=ax[1].transAxes, ha="center", va="bottom", fontsize=8.5)

# panel C: CD8 LL aggregation
strip(ax[2], pp["CD8"], "log2_LL", "C. CD8 aggregation\n(abundance-controlled)", "log2(obs/null) LL", hline=0)
c = d["spatial_pattern"]["CD8"]["R30"]["LL_aggregation_log2"]
ax[2].text(0.5, 0.03, f"not MSI-specific\np={c['p_two_sided']}  rbc={c['rank_biserial']:+.2f}",
           transform=ax[2].transAxes, ha="center", va="bottom", fontsize=8.5)

# panel D: lymphocyte-tumor mixing
strip(ax[3], pp["lymphocyte"], "log2_LT", "D. Immune-tumor mixing\n(abundance-controlled)",
      "log2(obs/null) LT", hline=0)
c = d["spatial_pattern"]["lymphocyte"]["R30"]["LT_mixing_log2"]
ax[3].text(0.5, 0.97, f"both <0 (exclusion)\nMSI-H less excluded\np={c['p_two_sided']}  rbc={c['rank_biserial']:+.2f}",
           transform=ax[3].transAxes, ha="center", va="top", fontsize=8.5)

fig.suptitle("Su et al. 2025 CRC IMC (cell resolution) — MSI-H vs MSS immune spatial architecture "
             "[hypothesis_only, exploratory, n=8 MSI-H]", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(HERE / "fig_su_imc_msi.png", dpi=150)
print("saved fig_su_imc_msi.png")

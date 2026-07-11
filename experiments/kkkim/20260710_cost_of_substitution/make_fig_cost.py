#!/usr/bin/env python3
"""C1 결과 2패널 그림: (A) 라우팅 스킴별(PAM50 vs receptor) 축별 오라우팅율 —
Anti-HER2만 라우팅-불변 100% / endocrine·chemo는 반전.  (B) 치료축 거리 히트맵.
영문 라벨(한글 폰트 부재 tofu 방지), constrained_layout(겹침/넘침 방지)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                     "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})

HERE = Path(__file__).parent
B_pam = json.loads((HERE / "patient_routing_cost.json").read_text())["per_axis"]
B_rec = json.loads((HERE / "patient_routing_cost_receptor.json").read_text())["per_axis"]
D = json.loads((HERE / "therapeutic_distance.json").read_text())["axis_pair_distance"]

# ---- data: axis order HER2 first (robust highlight) ----
order = ["antiHER2", "endocrine", "chemo"]
labels = ["Anti-HER2\n(ERBB2-amp)", "Endocrine\n(ER+)", "Chemo\n(TNBC/basal)"]
mis_pam = [B_pam[a]["misroute_rate"] * 100 for a in order]
mis_rec = [B_rec[a]["misroute_rate"] * 100 for a in order]
n_pam = [B_pam[a]["n"] for a in order]
n_rec = [B_rec[a]["n"] for a in order]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.7), constrained_layout=True,
                               gridspec_kw={"width_ratios": [1.25, 1.0]})

# ===== Panel A: grouped bars — PAM50 vs receptor mis-route =====
x = np.arange(len(order)); w = 0.36
b1 = ax1.bar(x - w/2, mis_pam, w, label="PAM50 routing", color="#8aa9c9",
             edgecolor="black", linewidth=0.6, zorder=3)
b2 = ax1.bar(x + w/2, mis_rec, w, label="Receptor routing", color="#37527a",
             edgecolor="black", linewidth=0.6, zorder=3)
ax1.set_ylim(0, 138)
ax1.set_yticks([0, 20, 40, 60, 80, 100])
ax1.set_ylabel("Mis-route rate (%)  —  wrong therapy axis")
ax1.set_xticks(x); ax1.set_xticklabels(labels)
ax1.set_title("A  Only anti-HER2 fails invariantly; endocrine & chemo flip with routing",
              loc="left", fontweight="bold", fontsize=10)
ax1.grid(axis="y", ls=":", lw=0.6, alpha=0.5, zorder=0)
ax1.legend(loc="upper right", frameon=False, fontsize=9, bbox_to_anchor=(1.0, 0.86))
for xi, v in zip(x - w/2, mis_pam):
    ax1.text(xi, v + 2.5, f"{v:.0f}%", ha="center", va="bottom", fontsize=8.6)
for xi, v in zip(x + w/2, mis_rec):
    ax1.text(xi, v + 2.5, f"{v:.0f}%", ha="center", va="bottom", fontsize=8.6, fontweight="bold")
# highlight HER2 as the robust (mandatory-molecular) axis — annotation kept above bar labels
ax1.axvspan(-0.5, 0.5, color="#d1495b", alpha=0.07, zorder=0)
ax1.text(0, 136, "routing-invariant\n→ molecular test mandatory", ha="center", va="top",
         fontsize=8.0, color="#a13045", fontweight="bold", linespacing=1.25)

# ===== Panel B: heatmap =====
ax_order = ["endocrine", "antiHER2", "chemo"]
ax_lab = ["Endocrine", "Anti-HER2", "Chemo"]
M = np.zeros((3, 3))
for i, a in enumerate(ax_order):
    for j, b in enumerate(ax_order):
        if i == j:
            M[i, j] = 0.0
        else:
            key = f"{a}__{b}" if f"{a}__{b}" in D else f"{b}__{a}"
            M[i, j] = D[key]["therapeutic_distance"]
im = ax2.imshow(M, cmap="magma_r", vmin=0, vmax=0.85, aspect="equal")
ax2.set_xticks(range(3)); ax2.set_yticks(range(3))
ax2.set_xticklabels(ax_lab); ax2.set_yticklabels(ax_lab)
ax2.set_title("B  Distance between therapy axes", loc="left", fontweight="bold")
for i in range(3):
    for j in range(3):
        v = M[i, j]
        ax2.text(j, i, "—" if i == j else f"{v:.2f}", ha="center", va="center",
                 fontsize=11, color=("#888" if i == j else ("white" if v > 0.45 else "black")),
                 fontweight="bold")
ax2.set_xticks(np.arange(-.5, 3, 1), minor=True)
ax2.set_yticks(np.arange(-.5, 3, 1), minor=True)
ax2.grid(which="minor", color="white", linewidth=1.4)
ax2.tick_params(which="minor", length=0)
cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
cb.set_label("Therapeutic distance (1 − Kendall τ)", fontsize=9)

fig.suptitle("H&E→subtype substitution: anti-HER2 axis is uniformly unsafe across routings  "
             "(CPTAC external, hypothesis-only)",
             fontsize=11.2, fontweight="bold")
fig.savefig(HERE / "fig_cost_of_substitution.png", dpi=200, bbox_inches="tight")
print("wrote fig_cost_of_substitution.png  mis_pam", [round(v) for v in mis_pam],
      "mis_rec", [round(v) for v in mis_rec])

#!/usr/bin/env python3
"""C1 예비 결과 2패널 그림: (A) 축별 치환 비용 막대  (B) 치료축 거리 히트맵.
영문 라벨(한글 폰트 부재 tofu 방지), constrained_layout(겹침/넘침 방지)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                     "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})

HERE = Path(__file__).parent
B = json.loads((HERE / "patient_routing_cost.json").read_text())["per_axis"]
D = json.loads((HERE / "therapeutic_distance.json").read_text())["axis_pair_distance"]

# ---- data (ascending cost: cheap -> catastrophic) ----
order = ["chemo", "endocrine", "antiHER2"]
labels = ["Chemo\n(TNBC/basal)", "Endocrine\n(ER+)", "Anti-HER2\n(ERBB2-amp)"]
cost = [B[a]["mean_cost"] for a in order]
mis = [B[a]["misroute_rate"] * 100 for a in order]
n = [B[a]["n"] for a in order]
colors = ["#4c9f70", "#e6a23c", "#d1495b"]  # green(safe) / amber / red(danger)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6), constrained_layout=True,
                               gridspec_kw={"width_ratios": [1.15, 1.0]})

# ===== Panel A: bar =====
x = np.arange(len(order))
bars = ax1.bar(x, cost, width=0.62, color=colors, edgecolor="black", linewidth=0.6, zorder=3)
ax1.set_ylim(0, 0.86)
ax1.set_ylabel("Substitution cost\n(0 = correct routing, 1 = max therapeutic distance)")
ax1.set_xticks(x)
ax1.set_xticklabels([f"{l}\nn={nn}" for l, nn in zip(labels, n)])
ax1.set_title("A  Therapeutic cost of using H&E-predicted subtype", loc="left", fontweight="bold")
ax1.grid(axis="y", ls=":", lw=0.6, alpha=0.5, zorder=0)
for xi, c, m in zip(x, cost, mis):
    ax1.text(xi, c + 0.018, f"{c:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax1.text(xi, c / 2, f"mis-route\n{m:.0f}%", ha="center", va="center", fontsize=8.5,
             color="white", fontweight="bold")
# headline contrast bracket (antiHER2 vs endocrine)
y0 = 0.80
ax1.annotate("", xy=(2, y0), xytext=(1, y0),
             arrowprops=dict(arrowstyle="<->", lw=1.1, color="#333"))
ax1.text(1.5, y0 + 0.012, "Δ = 0.34  (95% CI 0.28–0.40, excludes 0)",
         ha="center", va="bottom", fontsize=8.6, color="#333")

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

fig.suptitle("H&E→subtype substitution cost is therapy-axis-dependent  (CPTAC, PAM50 routing, preliminary)",
             fontsize=11.5, fontweight="bold")
fig.savefig(HERE / "fig_cost_of_substitution.png", dpi=200, bbox_inches="tight")
print("wrote fig_cost_of_substitution.png", M.shape, "cost", [round(c,3) for c in cost])

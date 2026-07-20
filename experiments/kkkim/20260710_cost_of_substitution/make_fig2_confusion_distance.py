#!/usr/bin/env python3
"""Fig 2 (⭐ DECISIVE, research-plan §9) — label↔therapy 해리 2-panel:
(A) CPTAC H&E 상태-confusion matrix (row-normalized, true axis -> predicted axis),
(B) therapeutic-distance matrix d_a.
곱(confusion x distance = cost 기여분)을 (A) 오분류 셀에 overlay 주석으로 표시.
결론: anti-HER2 행은 100% 오분류 + 먼 치료거리 = 비용 폭발(켜짐).
      endocrine 행은 5% 오분류 + 가까운 치료거리 = 비용 거의 0(안 켜짐).
영문 라벨(한글 폰트 tofu 방지), constrained_layout. house style = make_fig_cost.py 따름."""
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
routing_path = HERE / "patient_routing_cost_receptor.json"
dist_path = HERE / "therapeutic_distance.json"
R = json.loads(routing_path.read_text())
Dj = json.loads(dist_path.read_text())

confusion = R["confusion_true_to_pred"]   # true axis -> {predicted axis: n}
D = Dj["axis_pair_distance"]

axes = ["endocrine", "antiHER2", "chemo"]
labels = ["Endocrine\n(ER+)", "Anti-HER2\n(ERBB2-amp)", "Chemo\n(TNBC/basal)"]


def dist(a, b):
    if a == b:
        return 0.0
    key = f"{a}__{b}" if f"{a}__{b}" in D else f"{b}__{a}"
    return D[key]["therapeutic_distance"]


# ---- (A) confusion matrix, row-normalized; predicted-antiHER2 column always 0
# (H&E receptor head never predicts antiHER2 externally -> entire column empty) ----
C = np.zeros((3, 3))          # rows=true, cols=predicted, raw n
for i, ta in enumerate(axes):
    row = confusion.get(ta, {})
    for j, pa in enumerate(axes):
        C[i, j] = row.get(pa, 0)
row_n = C.sum(axis=1, keepdims=True)
Cprop = np.divide(C, row_n, out=np.zeros_like(C), where=row_n > 0)

# cost contribution per cell = misroute proportion x therapeutic distance (0 on diagonal)
Cost = np.zeros((3, 3))
for i, ta in enumerate(axes):
    for j, pa in enumerate(axes):
        if i != j:
            Cost[i, j] = Cprop[i, j] * dist(ta, pa)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 5.0), constrained_layout=True,
                               gridspec_kw={"width_ratios": [1.15, 1.0]})

# ===== Panel A: confusion matrix (row-normalized %) + cost overlay on off-diagonal =====
im1 = ax1.imshow(Cprop, cmap="Blues", vmin=0, vmax=1.0, aspect="equal")
ax1.set_xticks(range(3)); ax1.set_yticks(range(3))
ax1.set_xticklabels(labels); ax1.set_yticklabels(labels)
ax1.set_xlabel("H&E-predicted axis")
ax1.set_ylabel("Ground-truth axis")
ax1.set_title("A  Status-confusion (CPTAC ext.)",
              loc="left", fontweight="bold", fontsize=10)
for i in range(3):
    for j in range(3):
        p = Cprop[i, j]
        n = int(C[i, j])
        txt_color = "white" if p > 0.55 else "black"
        if i == j:
            ax1.text(j, i, f"{p*100:.0f}%\n(n={n})", ha="center", va="center",
                      fontsize=9.5, color=txt_color, fontweight="bold")
        else:
            cost_txt = f"cost {Cost[i, j]:.3f}" if n > 0 else ""
            ax1.text(j, i, f"{p*100:.0f}% (n={n})\n{cost_txt}", ha="center", va="center",
                      fontsize=8.6, color=("#b3001b" if Cost[i, j] >= 0.15 else txt_color),
                      fontweight=("bold" if Cost[i, j] >= 0.15 else "normal"))
ax1.set_xticks(np.arange(-.5, 3, 1), minor=True)
ax1.set_yticks(np.arange(-.5, 3, 1), minor=True)
ax1.grid(which="minor", color="white", linewidth=1.4)
ax1.tick_params(which="minor", length=0)
# highlight: anti-HER2 row = lights up (never predicted, high cost); endocrine row = stays dark (low cost)
ax1.axhspan(0.5, 1.5, xmin=0, xmax=1, color="#d1495b", alpha=0.06, zorder=0)
ax1.annotate("predicted-antiHER2 column is empty\n(H&E receptor head never fires)",
             xy=(1, -0.5), xytext=(1, -1.15), ha="center", va="bottom",
             fontsize=8.0, color="#a13045", style="italic",
             arrowprops=dict(arrowstyle="-", color="#a13045", lw=0.8))
ax1.set_ylim(2.5, -1.6)
cb1 = fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
cb1.set_label("Row-normalized frequency", fontsize=9)

# ===== Panel B: therapeutic-distance matrix (unchanged methodology from make_fig_cost.py) =====
M = np.zeros((3, 3))
for i, a in enumerate(axes):
    for j, b in enumerate(axes):
        M[i, j] = dist(a, b)
im2 = ax2.imshow(M, cmap="magma_r", vmin=0, vmax=0.85, aspect="equal")
ax2.set_xticks(range(3)); ax2.set_yticks(range(3))
ax2.set_xticklabels(labels); ax2.set_yticklabels(labels)
ax2.set_title("B  Distance between therapy axes", loc="left", fontweight="bold", fontsize=10)
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
cb2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
cb2.set_label("Therapeutic distance (1 − Kendall τ)", fontsize=9)

fig.suptitle("Label↔therapy dissociation: anti-HER2 axis lights up (never predicted × far in "
             "therapy space); endocrine stays dark (rare miss × close)  —  CPTAC external, "
             "hypothesis-only",
             fontsize=11.0, fontweight="bold")

fig.text(0.5, -0.02, "cost overlay (panel A, off-diagonal) = row-normalized mis-route frequency × panel-B therapeutic distance",
          ha="center", va="top", fontsize=8.3, color="#444")

out_png = HERE / "fig2_confusion_distance.png"
out_pdf = HERE / "fig2_confusion_distance.pdf"
fig.savefig(out_png, dpi=200, bbox_inches="tight")
fig.savefig(out_pdf, bbox_inches="tight")

meta = {
    "figure": "Fig 2 (research-plan §9, DECISIVE)",
    "jira": "BIOP02-91 / BIOP02-66 (FIGURES_INDEX.md)",
    "sources": [str(routing_path.relative_to(HERE.parents[2])),
                str(dist_path.relative_to(HERE.parents[2]))],
    "claim_level": "hypothesis_only",
    "critic_status": R.get("critic_status", "pending"),
    "note": "Cost overlay = row-normalized mis-route proportion x therapeutic distance; "
            "reproduces per_axis.mean_cost in patient_routing_cost_receptor.json "
            "(endocrine 0.035, antiHER2 0.416, chemo 0.51) as a cross-check.",
    "confusion_row_normalized": {axes[i]: {axes[j]: round(float(Cprop[i, j]), 4) for j in range(3)}
                                  for i in range(3)},
    "cost_overlay": {axes[i]: {axes[j]: round(float(Cost[i, j]), 4) for j in range(3) if i != j}
                      for i in range(3)},
    "cross_check_row_sum_vs_mean_cost": {
        axes[i]: {"row_sum_cost": round(float(Cost[i].sum()), 4),
                  "json_mean_cost": R["per_axis"][axes[i]]["mean_cost"]}
        for i in range(3)
    },
}
(HERE / "fig2_confusion_distance.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print("wrote fig2_confusion_distance.{png,pdf,json}")
print(json.dumps(meta["cross_check_row_sum_vs_mean_cost"], indent=2))

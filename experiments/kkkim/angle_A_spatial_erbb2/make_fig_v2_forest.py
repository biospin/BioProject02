#!/usr/bin/env python3
"""Angle A v2 headline 그림: (A) 환자별 Θ_overlap forest(CI) (B) robustness(raw/interior/depth).
Θ=P(tumor spot ERBB2 ≤ ref spot ERBB2). 영문 라벨, constrained_layout."""
import json
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":10,"axes.titlesize":10.5,"font.family":"DejaVu Sans",
                     "axes.spines.top":False,"axes.spines.right":False})
HERE=Path(__file__).parent
d=json.loads((HERE/"spatial_erbb2_floor_v2.json").read_text())
P=d["per_patient"]; pats=[r["patient"] for r in P]
theta=[r["theta_overlap"] for r in P]
ci=[r["theta_ci95"] for r in P]
lo=[c[0] for c in ci]; hi=[c[1] for c in ci]
tint=[r.get("theta_interior") for r in P]; tdep=[r.get("theta_depth_cond") for r in P]
med=d["summary"]["theta_median"]

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11.4,4.5),constrained_layout=True,gridspec_kw={"width_ratios":[1.0,1.15]})
y=np.arange(len(pats))[::-1]
# Panel A: forest
for yi,t,l,h in zip(y,theta,lo,hi):
    ax1.plot([l,h],[yi,yi],color="#37527a",lw=2,zorder=2)
ax1.scatter(theta,y,s=55,color="#37527a",zorder=3,edgecolors="white",linewidths=0.8)
ax1.axvline(med,ls="--",lw=1,color="#d1495b",alpha=0.8,zorder=1)
ax1.text(med+0.008,0.2,f"median {med}",color="#d1495b",fontsize=8.5,ha="left",va="center")
ax1.set_yticks(y); ax1.set_yticklabels([f"Pt {p}" for p in pats])
ax1.set_ylim(-0.6,len(pats)-0.4)
ax1.set_xlim(0,0.55); ax1.set_xlabel("Θ = P(tumor spot ERBB2 ≤ background spot ERBB2)\n(higher → more tumor area at background level)")
ax1.set_title("A  Threshold-free overlap floor — nonzero (CI excl. 0) in 8/8",loc="left",fontweight="bold",fontsize=9.5)
ax1.grid(axis="x",ls=":",lw=0.6,alpha=0.5)

# Panel B: robustness (raw vs interior vs depth-conditioned)
x=np.arange(len(pats)); w=0.27
ax2.bar(x-w,theta,w,label="Θ raw",color="#37527a",edgecolor="black",lw=0.5)
ax2.bar(x,[v if v is not None else 0 for v in tint],w,label="Θ interior-only (diffusion ctrl)",color="#8aa9c9",edgecolor="black",lw=0.5)
ax2.bar(x+w,[v if v is not None else 0 for v in tdep],w,label="Θ depth-conditioned",color="#cddcec",edgecolor="black",lw=0.5)
ax2.axhline(0.03,ls=":",lw=1,color="#d1495b",alpha=0.7)
ax2.text(len(pats)-0.5,0.045,"survival floor 0.03",ha="right",fontsize=7.5,color="#d1495b")
ax2.set_xticks(x); ax2.set_xticklabels([f"{p}" for p in pats]); ax2.set_xlabel("Patient")
ax2.set_ylabel("Θ_overlap"); ax2.set_ylim(0,0.5)
ax2.set_title("B  Survives robustness: interior 7/8, depth-cond 3/3(high-ρ)",loc="left",fontweight="bold",fontsize=9.5)
ax2.legend(loc="upper left",frameon=False,fontsize=7.8)
ax2.grid(axis="y",ls=":",lw=0.6,alpha=0.5)

fig.suptitle("Spatial ERBB2 overlap = irreducible floor on subtype-substitution (Andersson HER2+ ST, n=8, hypothesis-only)",
             fontsize=10.3,fontweight="bold")
fig.savefig(HERE/"fig_erbb2_floor_v2.png",dpi=200,bbox_inches="tight")
print("wrote fig_erbb2_floor_v2.png | Θ median",med,"range",d["summary"]["theta_range"])

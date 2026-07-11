#!/usr/bin/env python3
"""Angle A 그림: (A) 환자별 배경-이하 ERBB2 종양면적%(역치 3종) (B) 한 종양 공간 오버레이.
영문 라벨(tofu 방지), constrained_layout."""
import json, glob
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent; DATA = HERE / "data"
plt.rcParams.update({"font.size":10,"axes.titlesize":11,"font.family":"DejaVu Sans",
                     "axes.spines.top":False,"axes.spines.right":False})
d = json.loads((HERE/"spatial_erbb2_floor.json").read_text())
pat = [r["patient"] for r in d["threshold_50pct"]["per_patient"] if "low_erbb2_tumor_area_frac" in r]
def fr(pct): return {r["patient"]:r["low_erbb2_tumor_area_frac"]*100
                     for r in d[f"threshold_{pct}pct"]["per_patient"] if "low_erbb2_tumor_area_frac" in r}
f50,f90,f95 = fr(50),fr(90),fr(95)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11.4,4.6),constrained_layout=True,gridspec_kw={"width_ratios":[1.35,1.0]})
# Panel A: grouped bars
x=np.arange(len(pat)); w=0.27
ax1.bar(x-w,[f50[p] for p in pat],w,label="≤ background median (strict)",color="#37527a",edgecolor="black",lw=0.5)
ax1.bar(x,  [f90[p] for p in pat],w,label="≤ background 90th pct",color="#8aa9c9",edgecolor="black",lw=0.5)
ax1.bar(x+w,[f95[p] for p in pat],w,label="≤ background 95th pct",color="#cddcec",edgecolor="black",lw=0.5)
ax1.set_xticks(x); ax1.set_xticklabels([f"Pt {p}" for p in pat])
ax1.set_ylabel("Tumor area with ERBB2 at HER2-negative\nbackground level (%)")
ax1.set_ylim(0,100)
ax1.set_title("A  Even in confirmed HER2+ tumors, tumor area sits at HER2-negative ERBB2",
              loc="left",fontweight="bold",fontsize=9.5)
ax1.grid(axis="y",ls=":",lw=0.6,alpha=0.5)
ax1.legend(loc="upper right",frameon=False,fontsize=8)
med50=d["threshold_50pct"]["summary"]["median_low_frac"]*100
ax1.axhline(med50,ls="--",lw=1,color="#37527a",alpha=0.7)
ax1.text(len(pat)-0.5,med50+2,f"strict median {med50:.0f}%",ha="right",fontsize=8,color="#37527a")

# Panel B: 한 종양 공간 오버레이 (배경-이하 종양 spot 강조) — 대표 = strict에서 가장 높은 환자
rep=max(f50,key=f50.get)
sec=next(r["section"] for r in d["threshold_50pct"]["per_patient"] if r.get("patient")==rep)
cm=pd.read_csv(DATA/"count-matrices"/f"{sec}.tsv.gz",sep="\t",index_col=0)
meta=pd.read_csv(DATA/f"{sec}_labeled_coordinates.tsv",sep="\t").dropna(subset=["x","y","label"])
meta["key"]=meta["x"].round().astype(int).astype(str)+"x"+meta["y"].round().astype(int).astype(str)
meta=meta[meta["key"].isin(cm.index)]
tot=cm.sum(axis=1).replace(0,np.nan); erbb2=np.log1p(cm["ERBB2"]/tot*1e4)
meta["erbb2"]=meta["key"].map(erbb2)
TUMOR={"invasive cancer","cancer in situ"}; REF={"adipose tissue","connective tissue","immune infiltrate"}
ref=meta[meta["label"].isin(REF)]; thr=np.percentile(ref["erbb2"].dropna(),50)
tum=meta[meta["label"].isin(TUMOR)].dropna(subset=["erbb2"])
low=tum[tum["erbb2"]<=thr]; high=tum[tum["erbb2"]>thr]
oth=meta[~meta["label"].isin(TUMOR)]
ax2.scatter(oth["x"],oth["y"],s=14,c="#dddddd",label="non-tumor",edgecolors="none")
ax2.scatter(high["x"],high["y"],s=16,c="#d1495b",label="tumor, ERBB2 high",edgecolors="none")
ax2.scatter(low["x"],low["y"],s=16,c="#37527a",label="tumor, ERBB2 ≤ bg (floor)",edgecolors="none")
ax2.set_title(f"B  Patient {rep}: {f50[rep]:.0f}% of tumor at background ERBB2",loc="left",fontweight="bold",fontsize=9.5)
ax2.set_xlabel("array x"); ax2.set_ylabel("array y"); ax2.invert_yaxis()
ax2.legend(loc="upper right",frameon=True,fontsize=7.5,markerscale=1.3)
ax2.set_aspect("equal")

fig.suptitle("Spatial ERBB2 heterogeneity imposes an irreducible floor on subtype-substitution cost  "
             "(Andersson HER2+ ST, n=8, hypothesis-only)",fontsize=10.5,fontweight="bold")
fig.savefig(HERE/"fig_erbb2_floor.png",dpi=200,bbox_inches="tight")
print(f"wrote fig_erbb2_floor.png (대표 Pt {rep}, sec {sec})")

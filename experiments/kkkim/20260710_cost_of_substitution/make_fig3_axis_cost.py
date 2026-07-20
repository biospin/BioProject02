#!/usr/bin/env python3
"""Fig 3 (research-plan §9) — 축별 치환비용 + headline 대비.

§9 스펙: "cost_a 막대 + cost_antiHER2−cost_endocrine CI(0 배제). receptor-status(primary) &
PAM50(secondary) 나란히, construction vs empirical 분리(§2.5)."

Fig 2(confusion×distance, 결정그림)에서 분리된 별도 그림 — Fig2=왜(메커니즘), Fig3=얼마(크기·불확실성).
재료는 기존 검증 JSON 재사용(신규 계산 없음): patient_routing_cost{,_receptor}.json.

⚠️ 정직성(honest_reading 준수): raw per-axis cost는 라우팅 스킴 의존(endocrine/chemo가 뒤집힘).
robust한 것은 ① antiHER2 misroute=1.00(스킴 불문) ② headline contrast(antiHER2−endocrine) CI가 0 배제.
그래서 이 그림은 두 라우팅을 나란히 보여 "무엇이 흔들리고 무엇이 안 흔들리는지"를 그림 자체로 드러낸다.
영문 라벨(tofu 방지), constrained_layout. house style = make_fig_cost.py / make_fig2_*.py 따름.
"""
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
PAM = json.loads((HERE / "patient_routing_cost.json").read_text())
REC = json.loads((HERE / "patient_routing_cost_receptor.json").read_text())

AXES = ["antiHER2", "endocrine", "chemo"]
LABELS = ["Anti-HER2\n(ERBB2-amp)", "Endocrine\n(ER+)", "Chemo\n(TNBC/basal)"]

def per_axis(d, key):
    return [d["per_axis"][a][key] for a in AXES]

cost_rec = per_axis(REC, "mean_cost")
cost_pam = per_axis(PAM, "mean_cost")
mis_rec = [v * 100 for v in per_axis(REC, "misroute_rate")]
mis_pam = [v * 100 for v in per_axis(PAM, "misroute_rate")]

# ⚠️ 두 JSON의 contrast 키 경로가 다름(스키마 불일치): receptor=per_axis.headline_contrast,
# PAM50=최상위 headline_contrast_antiHER2_minus_endocrine. 둘 다 value+ci95+excludes_zero 보유.
hc_rec = REC["per_axis"]["headline_contrast"]
hc_pam = PAM.get("headline_contrast_antiHER2_minus_endocrine", {})
assert hc_rec.get("ci95") and hc_pam.get("ci95"), "두 라우팅 모두 CI가 있어야 'both routings' 주장 가능"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.6), constrained_layout=True,
                               gridspec_kw={"width_ratios": [1.5, 1.0]})

# ===== Panel A: 축별 cost — 두 라우팅 나란히(무엇이 흔들리나) =====
x = np.arange(len(AXES)); w = 0.36
b1 = ax1.bar(x - w/2, cost_pam, w, label="PAM50 routing", color="#8aa9c9",
             edgecolor="black", linewidth=0.6, zorder=3)
b2 = ax1.bar(x + w/2, cost_rec, w, label="Receptor routing (primary)", color="#37527a",
             edgecolor="black", linewidth=0.6, zorder=3)
ax1.set_ylim(0, 1.06)   # 상단 여백 = 주석/막대라벨 겹침 방지(육안 QA)
ax1.set_ylabel("Substitution cost  (mis-route rate × therapeutic distance)")
ax1.set_xticks(x); ax1.set_xticklabels(LABELS)
ax1.set_title("A  Per-axis substitution cost — routing-dependent except anti-HER2",
              loc="left", fontweight="bold", fontsize=10)
ax1.grid(axis="y", ls=":", lw=0.6, alpha=0.5, zorder=0)
ax1.legend(loc="upper right", frameon=False, fontsize=9)
for xi, v, m in zip(x - w/2, cost_pam, mis_pam):
    ax1.text(xi, v + 0.015, f"{v:.3f}\n({m:.0f}%)", ha="center", va="bottom", fontsize=8.2)
for xi, v, m in zip(x + w/2, cost_rec, mis_rec):
    ax1.text(xi, v + 0.015, f"{v:.3f}\n({m:.0f}%)", ha="center", va="bottom", fontsize=8.2,
             fontweight="bold")
# anti-HER2 = routing-invariant 100% mis-route
ax1.axvspan(-0.5, 0.5, color="#d1495b", alpha=0.07, zorder=0)
ax1.text(0, 0.99, "mis-route 100% under BOTH routings\n→ molecular test mandatory",
         ha="center", va="top", fontsize=8.2, color="#a13045", fontweight="bold",
         linespacing=1.25, transform=ax1.get_xaxis_transform())
# (endocrine·chemo가 라우팅에 따라 뒤집힌다는 caveat는 범례와 겹쳐 하단 캡션으로 이동 — 육안 QA)

# ===== Panel B: headline contrast (antiHER2 − endocrine) — 무엇이 안 흔들리나 =====
rows = [("Receptor routing\n(primary)", hc_rec), ("PAM50 routing\n(secondary)", hc_pam)]
ys = np.arange(len(rows))[::-1]
for y, (name, hc) in zip(ys, rows):
    if not hc:
        continue
    v = hc["value"]; lo, hi = hc["ci95"]
    ax2.errorbar(v, y, xerr=[[v - lo], [hi - v]], fmt="o", color="#37527a",
                 ecolor="#37527a", elinewidth=2, capsize=5, markersize=8, zorder=3)
    ax2.text(v, y + 0.16, f"{v:.3f}  [{lo:.3f}, {hi:.3f}]", ha="center", va="bottom",
             fontsize=9, fontweight="bold")
ax2.axvline(0, color="#d1495b", ls="--", lw=1.2, zorder=2)
ax2.text(0, -0.62, "null (no contrast)", color="#a13045", fontsize=8.2, ha="center", va="top")
ax2.set_yticks(ys); ax2.set_yticklabels([r[0] for r in rows])
ax2.set_ylim(-0.75, len(rows) - 0.25)
ax2.set_xlabel("cost(anti-HER2) − cost(endocrine)")
ax2.set_title("B  Headline contrast — CI excludes 0 under both routings",
              loc="left", fontweight="bold", fontsize=10)
ax2.grid(axis="x", ls=":", lw=0.6, alpha=0.5)

fig.suptitle("Substitution cost is routing-dependent per axis, but the anti-HER2 − endocrine "
             "contrast is robust  (CPTAC external, hypothesis-only)",
             fontsize=11.0, fontweight="bold")
fig.text(0.5, -0.03,
         "Bars = mean cost (mis-route % in parens). Panel B = bootstrap 95% CI; excludes 0 → contrast robust to routing scheme.\n"
         "Honest reading: endocrine · chemo per-axis cost FLIPS between routings (0.378↔0.035, 0.105↔0.510) → NOT a safety claim. "
         "Robust = anti-HER2 mis-route 1.00 under both + the contrast above.",
         ha="center", va="top", fontsize=8.3, color="#444", linespacing=1.4)

out_png = HERE / "fig3_axis_cost.png"
fig.savefig(out_png, dpi=200, bbox_inches="tight")
fig.savefig(HERE / "fig3_axis_cost.pdf", bbox_inches="tight")

meta = {
    "figure": "Fig 3 (research-plan §9) — 축별 cost + headline 대비",
    "jira": "BIOP02-91 / FIGURES_INDEX",
    "relation_to_fig2": "Fig2=메커니즘(confusion×distance, 왜), Fig3=크기·불확실성(얼마)",
    "sources": ["patient_routing_cost.json (PAM50 routing)",
                "patient_routing_cost_receptor.json (receptor routing, primary)"],
    "claim_level": "hypothesis_only",
    "critic_status": REC.get("critic_status", "pending"),
    "per_axis_cost": {"receptor": dict(zip(AXES, cost_rec)), "pam50": dict(zip(AXES, cost_pam))},
    "misroute_pct": {"receptor": dict(zip(AXES, mis_rec)), "pam50": dict(zip(AXES, mis_pam))},
    "headline_contrast": {"receptor": hc_rec, "pam50": hc_pam},
    "honest_reading": REC.get("honest_reading", ""),
    "note": "raw per-axis cost는 라우팅 스킴 의존(endocrine/chemo 반전) — 안전 주장 근거 아님. "
            "robust = antiHER2 misroute 1.00(스킴 불문) + headline contrast CI 0 배제.",
}
(HERE / "fig3_axis_cost.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
print("wrote fig3_axis_cost.{png,pdf,json}")
print("receptor cost:", dict(zip(AXES, cost_rec)))
print("pam50    cost:", dict(zip(AXES, cost_pam)))
print("contrast receptor:", hc_rec, "| pam50:", hc_pam)

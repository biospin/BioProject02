#!/usr/bin/env python3
"""GIW 2026 long abstract 그림 2장 (v2).

v1 문제:
  Fig2 에서 홀드아웃 양성 25 이상을 전부 초록으로 칠했다. 그런데 25 를 넘은 건
  대부분 양성대조(폐 조직형 153 · HNSC grade 41 · 위 Lauren 31)이고 실제 확증은
  HPV 하나다. 초록 = 통과로 읽혀서 초록에 새로 넣은 판정 체계와 어긋난다.
  -> 판정별 색 + 양성대조는 빗금으로 구분한다.
  Fig1 라벨 겹침·범례 순서도 고친다.

모든 수치는 정본에서 읽는다.
"""
import json, os, re, glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = "/home/gglee/project/BioProject02"
SA = os.path.join(ROOT, "experiments/crosscancer/site_audit")
OUT = os.path.join(ROOT, "manuscript/figures")
os.makedirs(OUT, exist_ok=True)
SCORE = os.path.join(ROOT, "experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md")

ROW2EP = {
    ("두경부", "hpv"): ("hpv_pos", "HNSC HPV"),
    ("두경부", "grade_high"): ("grade_high", "HNSC grade"),
    ("두경부", "egfr_amp"): ("egfr_amp", "HNSC EGFR amp"),
    ("폐", "histology lusc"): ("histology_lusc", "Lung LUSC histology"),
    ("폐", "egfr_activating"): ("egfr_activating", "Lung EGFR"),
    ("폐", "kras_g12c"): ("kras_g12c", "Lung KRAS-G12C"),
    ("위", "lauren_diffuse"): ("lauren_diffuse", "Gastric Lauren"),
    ("위", "msi_h"): ("msi_h", "Gastric MSI-H"),
    ("위", "erbb2_amp"): ("erbb2_amp", "Gastric ERBB2 amp"),
    ("위", "ebv"): ("ebv", "Gastric EBV"),
}
# 정본 스코어보드에서 '양성대조'로 명시된 엔드포인트
POSCTRL = {"histology_lusc", "grade_high", "lauren_diffuse"}

VERDICT = {  # 초록의 판정 체계와 1:1
    "hpv_pos":          "Confirmed",
    "histology_lusc":   "Audit-excluded",
    "lauren_diffuse":   "Audit-excluded",
    "erbb2_amp":        "No signal",
    "msi_h":            "Undecided",
    "egfr_activating":  "Undecided",
    "kras_g12c":        "Undecided",
    "egfr_amp":         "Undecided",
    "ebv":              "Undecided",
    "grade_high":       "Positive control",
}
VCOL = {"Confirmed": "#1e8449", "Audit-excluded": "#c0392b",
        "No signal": "#566573", "Undecided": "#bdc3c7",
        "Positive control": "#5dade2"}
VLAB = {"Positive control": "Positive control (passed)"}


def parse_scoreboard():
    out = {}
    for line in open(SCORE, encoding="utf-8"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        cancer, ep = cells[0], cells[1].lower().replace("**", "")
        key = next((v for (c, e), v in ROW2EP.items() if cancer == c and e in ep), None)
        if not key:
            continue
        m = re.search(r"(\d\.\d+)", cells[3])
        n = re.search(r"^(\d+)$", cells[4].strip())
        if m and n:
            out[key[0]] = {"label": key[1], "auroc": float(m.group(1)), "n_pos": int(n.group(1))}
    return out


def parse_cramers():
    v = {}
    for f in glob.glob(os.path.join(SA, "site_audit_*.json")):
        for ep, r in (json.load(open(f)).get("label_site_imbalance") or {}).items():
            v[ep] = r["cramers_v_label_vs_site"]
    return v


def parse_loso():
    d = json.load(open(os.path.join(SA, "SITE_AUDIT_VERDICT.json")))
    return {ep: r for eps in d["loso_by_endpoint"].values() for ep, r in eps.items()}


score, cram, loso = parse_scoreboard(), parse_cramers(), parse_loso()

# ══════════════════════════ Fig 1 ══════════════════════════
LOSO_ORDER = [("🟢", "#27ae60", "site-independent  (LOSO drop < 0.05)"),
              ("🟡", "#e67e22", "partial confounding  (0.05–0.10)"),
              ("🔴", "#c0392b", "site-driven  (> 0.10)")]

def loso_style(ep):
    v = loso.get(ep, {}).get("verdict", "")
    for mark, col, lab in LOSO_ORDER:
        if mark in v:
            return col, lab
    return "#7f8c8d", "not audited"

# 라벨 위치 수동 조정 — 겹침 해소
NUDGE = {
    "histology_lusc": (-0.025, 0.000, "right"),
    "msi_h":          (0.020, 0.011, "left"),
    "egfr_activating": (0.020, -0.013, "left"),
    "grade_high":     (0.020, -0.002, "left"),
    "hpv_pos":        (0.020, 0.008, "left"),
    "ebv":            (0.020, 0.004, "left"),
}

fig, ax = plt.subplots(figsize=(7.2, 5.0))
for ep, r in score.items():
    if ep not in cram:
        continue
    x, y = cram[ep], r["auroc"]
    col, _ = loso_style(ep)
    ax.scatter(x, y, s=95, c=col, edgecolors="black", linewidths=0.7, zorder=3)
    dx, dy, ha = NUDGE.get(ep, (0.020, 0.004, "left"))
    ax.annotate(r["label"], (x, y), xytext=(x + dx, y + dy), ha=ha, fontsize=8.4, zorder=4)

ax.axvspan(0.5, 1.06, color="#c0392b", alpha=0.055, zorder=0)
ax.text(0.80, 0.995, "strong label–site association", fontsize=8.2,
        c="#c0392b", ha="center", alpha=0.9)
ax.annotate("highest accuracy in the study,\nbut V = 1.000 — morphology and\nsite signature are inseparable",
            xy=(1.00, 0.930), xytext=(0.82, 0.685), fontsize=8.0, color="#c0392b",
            ha="center", va="top",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#c0392b", lw=0.7, alpha=0.92),
            arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.0,
                            connectionstyle="arc3,rad=-0.18"))

ax.set_xlabel("Label–institution association  (Cramér's V)", fontsize=10)
ax.set_ylabel("Sealed hold-out AUROC", fontsize=10)
ax.set_title("Accuracy alone does not separate morphology from site signature",
             fontsize=10.8, pad=11)
ax.set_xlim(-0.02, 1.10)
ax.set_ylim(0.48, 1.02)
ax.grid(alpha=0.22, ls="--", lw=0.6)
ax.set_axisbelow(True)

present = {loso_style(ep)[1] for ep in score if ep in cram}
handles = [Line2D([0], [0], marker="o", ls="", mfc=c, mec="black", mew=0.7, ms=8, label=lab)
           for _, c, lab in LOSO_ORDER if lab in present]
ax.legend(handles=handles, fontsize=7.9, loc="lower left", framealpha=0.93,
          title="Leave-one-site-out audit", title_fontsize=8.2)

fig.tight_layout()
p1 = os.path.join(OUT, "GIW2026_fig1_site_confounding.png")
fig.savefig(p1, dpi=300); fig.savefig(p1.replace(".png", ".pdf"))
print("wrote", p1)

# ══════════════════════════ Fig 2 ══════════════════════════
items = sorted(score.items(), key=lambda kv: kv[1]["n_pos"])
fig2, ax2 = plt.subplots(figsize=(7.4, 4.6))
for i, (ep, r) in enumerate(items):
    v = VERDICT[ep]
    ax2.barh(i, r["n_pos"], color=VCOL[v], edgecolor="black", linewidth=0.6,
             hatch="///" if ep in POSCTRL else None, zorder=3)
    ax2.text(r["n_pos"] + 1.8, i, str(r["n_pos"]), va="center", fontsize=8.4)

ax2.axvline(25, color="#c0392b", lw=1.8, ls="--", zorder=5)
ax2.text(27, -0.75, "pre-registered confirmation threshold (25 positives)",
         color="#c0392b", fontsize=8.4, va="center")

ax2.set_yticks(range(len(items)))
ax2.set_yticklabels([r["label"] for _, r in items], fontsize=8.8)
ax2.set_xlabel("Hold-out positive patients", fontsize=10)
ax2.set_title("Crossing the power threshold is not the same as confirmation",
              fontsize=10.8, pad=11)
ax2.set_xlim(0, max(r["n_pos"] for _, r in items) * 1.15)
ax2.grid(axis="x", alpha=0.22, ls="--", lw=0.6)
ax2.set_axisbelow(True)

order = ["Confirmed", "Audit-excluded", "No signal", "Undecided", "Positive control"]
used = [v for v in order if v in {VERDICT[ep] for ep, _ in items}]
h2 = [Patch(facecolor=VCOL[v], edgecolor="black", lw=0.6, label=VLAB.get(v, v)) for v in used]
h2.append(Patch(facecolor="white", edgecolor="black", lw=0.6, hatch="///",
                label="hatched = positive control"))
ax2.legend(handles=h2, fontsize=7.8, loc="lower right", framealpha=0.95,
           title="Verdict", title_fontsize=8.2)

fig2.tight_layout()
p2 = os.path.join(OUT, "GIW2026_fig2_power_ceiling.png")
fig2.savefig(p2, dpi=300); fig2.savefig(p2.replace(".png", ".pdf"))
print("wrote", p2)

print("\n=== 정본 대조용 ===")
for ep, r in sorted(score.items(), key=lambda kv: -kv[1]["auroc"]):
    print(f"  {r['label']:22s} AUROC {r['auroc']:.4f}  n_pos {r['n_pos']:4d}  "
          f"V {cram.get(ep, float('nan')):.3f}  {VERDICT[ep]:16s}"
          f"{'  [pos-ctrl]' if ep in POSCTRL else ''}")

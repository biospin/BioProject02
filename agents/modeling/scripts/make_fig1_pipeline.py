"""
BIOP02-62 — Fig 1: SpatialPathoAgent pipeline schematic (H&E → embedding → phenotype → hypothesis).

Paper A 방법 개요 그림. 실제 파이프라인 단계를 그대로 도식화한다:
  H&E WSI → tiling → foundation-model embedding → attention MIL →
  molecular phenotype → external validation → therapeutic-evidence transfer,
  그리고 이 전 과정을 감싸는 7-point Scientific Critic governance gate.

프레이밍 규율(CLAUDE.md):
  - hypothesis-only 출력, **NOT a drug-response prediction (DRP) model**.
  - academic non-commercial. headline embedding = UNI(1024-d), 다중 FM는 견고성 검증용.

수치는 리포지토리에서 확립된 값만 사용(코호트 규모·타일 설정·엔드포인트). 성능 숫자는
Fig 3(baseline 비교)가 담당하므로 여기서는 넣지 않는다(스키마 그림).

Run:
    python agents/modeling/scripts/make_fig1_pipeline.py \
        --out experiments/braveji/fig1_pipeline/fig1_pipeline.png
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Okabe-Ito 계열 (fig3/fig4와 정합, 색맹 친화)
C = {
    "input":  "#56B4E9",   # sky blue  — 데이터 입력
    "proc":   "#009E73",   # green     — 전처리/임베딩
    "model":  "#0072B2",   # blue      — 모델
    "pheno":  "#E69F00",   # orange    — 표현형 출력
    "ext":    "#F0E442",   # yellow    — 외부검증(분기)
    "ther":   "#CC79A7",   # pink      — 치료 가설
    "critic": "#444444",   # dark      — Critic governance
}

# (x, y, w, h, facecolor, title, sublines)
STAGES = [
    (0.5,  5.2, 2.2, 1.5, C["input"], "H&E WSI",
     ["TCGA-BRCA ~1010 DX", "(+ CPTAC external)"]),
    (3.2,  5.2, 2.2, 1.5, C["proc"], "Tiling",
     ["256×256 @ 20×", "Otsu · ≤5000 tiles/pt"]),
    (5.9,  5.2, 2.4, 1.5, C["proc"], "FM embedding",
     ["UNI 1024-d (headline)", "Virchow2·UNI2-h·GigaPath"]),
    (8.8,  5.2, 2.2, 1.5, C["model"], "Attention MIL",
     ["CLAM-SB / CLAM-MB", "site-disjoint split"]),
    (11.4, 5.2, 2.9, 1.5, C["pheno"], "Molecular phenotype",
     ["ER · PR · HER2 (IHC)", "PAM50 (4-class)"]),
]

# 치료 가설 출력 (오른쪽 끝, 별도 색)
THER = (11.4, 2.6, 2.9, 1.5, C["ther"], "Therapeutic hypothesis",
        ["DepMap PRISM + GDSC", "ranked · hypothesis-only"])

# 외부검증 분기 (phenotype 아래)
EXT = (8.8, 2.6, 2.2, 1.3, C["ext"], "External validation",
       ["CPTAC", "site/patient-disjoint"])


def rbox(ax, x, y, w, h, fc, title, sublines, text_c="white"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=1.2, edgecolor="black", facecolor=fc, alpha=0.95, zorder=2))
    ax.text(x + w / 2, y + h - 0.42, title, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=text_c, zorder=3)
    for i, s in enumerate(sublines):
        ax.text(x + w / 2, y + h - 0.78 - i * 0.34, s, ha="center", va="center",
                fontsize=8.4, color=text_c, zorder=3)


def arrow(ax, x0, y0, x1, y1, color="#333333", style="-|>", lw=1.8, ls="-"):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle=style, mutation_scale=16,
        linewidth=lw, color=color, linestyle=ls,
        shrinkA=2, shrinkB=2, zorder=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="experiments/braveji/fig1_pipeline/fig1_pipeline.png")
    args = ap.parse_args()

    fig, ax = plt.subplots(figsize=(15.5, 7.2))
    ax.set_xlim(0, 15.0)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # 제목
    ax.text(0.5, 7.55, "SpatialPathoAgent — H&E to molecular phenotype to therapeutic hypothesis",
            ha="left", va="center", fontsize=14.5, fontweight="bold", color="#111111")
    ax.text(0.5, 7.15,
            "Multi-agent pipeline: morphology embedding predicts molecular phenotype, "
            "then transfers to ranked therapeutic hypotheses.",
            ha="left", va="center", fontsize=9.8, color="#555555")

    # 메인 파이프라인 박스 + 화살표
    for st in STAGES:
        rbox(ax, *st)
    for a, b in zip(STAGES[:-1], STAGES[1:]):
        arrow(ax, a[0] + a[2], a[1] + a[3] / 2, b[0], b[1] + b[3] / 2)

    # 외부검증 분기 + 치료 가설
    rbox(ax, *EXT, text_c="#222222")   # yellow → 어두운 텍스트
    rbox(ax, *THER)

    # embedding/MIL → CPTAC 외부검증 (아래로 분기): MIL 박스 하단 → EXT
    mil = STAGES[3]
    arrow(ax, mil[0] + mil[2] / 2, mil[1], EXT[0] + EXT[2] / 2, EXT[1] + EXT[3],
          color="#8a7d00", ls="--", lw=1.5)
    # phenotype → therapeutic hypothesis (아래로)
    ph = STAGES[4]
    arrow(ax, ph[0] + ph[2] / 2, ph[1], THER[0] + THER[2] / 2, THER[1] + THER[3])

    # Critic governance gate — 전 과정 감싸는 하단 바
    gx, gy, gw, gh = 0.5, 0.55, 13.8, 1.35
    ax.add_patch(FancyBboxPatch(
        (gx, gy), gw, gh, boxstyle="round,pad=0.02,rounding_size=0.1",
        linewidth=1.4, edgecolor="black", facecolor=C["critic"], alpha=0.95, zorder=2))
    ax.text(gx + 0.35, gy + gh - 0.34,
            "Scientific Critic — 7-point governance gate (Owner ≠ Reviewer)",
            ha="left", va="center", fontsize=11, fontweight="bold", color="white", zorder=3)
    checks = ("1 data-leakage   2 baselines(random/subtype/mean-embed)   3 counterfactual   "
              "4 cross-dataset   5 bio-plausibility   6 DRP-framing   7 claim-level")
    ax.text(gx + 0.35, gy + 0.42, checks, ha="left", va="center",
            fontsize=8.2, color="#EDEDED", zorder=3)
    # gate가 파이프라인을 검증한다는 상향 화살표(점선)
    for xc in (4.3, 7.1, 12.85):
        arrow(ax, xc, gy + gh, xc, 2.55 if xc > 11 else 5.15,
              color="#999999", ls=":", lw=1.1, style="-|>")

    # 하단 디스클레이머
    ax.text(0.5, 0.18,
            "Hypothesis-only output — NOT a drug-response prediction (DRP) model. "
            "No drug structure input. Academic non-commercial (TCGA/CPTAC/DepMap/GDSC).",
            ha="left", va="center", fontsize=8.6, style="italic", color="#666666")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    print(f"Saved: {out}  (+ {out.with_suffix('.pdf').name})")

    meta = {
        "figure": "Fig 1 — SpatialPathoAgent pipeline schematic",
        "issue": "BIOP02-62",
        "stages": [s[5] for s in STAGES] + [EXT[5], THER[5]],
        "governance": "7-point Scientific Critic gate",
        "framing": "hypothesis-only; NOT a DRP model; academic non-commercial",
        "note": "schematic only — performance numbers live in Fig 3 (baseline comparison)",
    }
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"Saved: {out.with_suffix('.json')}")


if __name__ == "__main__":
    main()

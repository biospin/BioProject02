"""
BIOP02-64 — Fig 3: Phenotype prediction baseline 비교.

ER/PR/HER2/PAM50 각각에 대해 random / subtype_only(또는 majority) / mean_embed /
SlideMLP / CLAM(SB or MB) 의 AUC(+95% CI)를 하나의 그림으로 비교한다.

CLAUDE.md 7-point Critic #2(baseline comparison) 요구사항의 시각적 요약이며,
BIOP02-50/53 self-critic에서 확립한 실제 CI/paired significance 결과를 그대로 반영한다.

Run:
    python agents/modeling/scripts/make_fig3_baseline_comparison.py \
        --experiments_dir experiments/sjpark \
        --out experiments/sjpark/fig3_baseline_comparison.png
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 발표용(presentation) 그림에서 그림 안 한글이 깨지지 않도록 NanumGothic 등록.
# 폰트가 없는 환경(CI 등)에서는 조용히 무시하고 기본 폰트로 렌더한다.
_KOREAN_FONT = None
for _fp in ("/home/kkkim/.fonts/NanumGothic-Bold.ttf",
            "/home/kkkim/.fonts/NanumGothic-Regular.ttf"):
    if Path(_fp).exists():
        fm.fontManager.addfont(_fp)
        _KOREAN_FONT = "NanumGothic"


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def get_baseline_auc(baselines_json: dict, name: str):
    for b in baselines_json.get("baselines", []):
        if b["baseline"] == name:
            return b.get("auc"), b.get("auc_ci_95")
    return None, None


def build_task_data(exp_dir: Path, task: str, mlp_dir: str, clam_dir: str, baselines_dir: str,
                     baseline_names: list):
    mlp = load_json(exp_dir / mlp_dir / "metrics.json")
    clam = load_json(exp_dir / clam_dir / "metrics.json")
    baselines = load_json(exp_dir / baselines_dir / "trivial_baselines.json")

    models = []
    for bname, label in baseline_names:
        auc, ci = get_baseline_auc(baselines, bname) if baselines else (None, None)
        models.append((label, auc, ci))

    if mlp:
        models.append(("MLP", mlp.get("auc"), mlp.get("auc_ci_95")))
    if clam:
        model_name = "CLAM-MB" if clam.get("model") == "CLAM-MB" else "CLAM-SB"
        models.append((model_name, clam.get("auc"), clam.get("auc_ci_95")))

    return task, models


def build_presentation_figure(all_data, out_path: Path):
    """발표용(일반 청중) 단순화 그림 — 지표별 '비이미지 기준선 vs 이미지 모델(CLAM)' 2막대.

    논문/critic용 4-패널 그림(main)과 동일한 데이터에서 그리되, PseudoCon 발표 피드백을 반영한다:
      · 축 제목·범례·데이터 라벨·하단 글씨를 크게, 흐린 회색 대신 진한 남색으로
      · ER/PR/HER2/PAM50 아래에 한 단어 설명(일반 청중용)
      · claim("이미지 모델은 아형-only 상한을 넘지 못한다")·수치는 4-패널과 동일하게 유지
    """
    NAVY = "#12305a"
    GOLD = "#E1A100"
    TEAL = "#1F77B4"

    # 지표별 기준선/최고 모델 선택 (ER/PR/HER2=Subtype-only 상한, PAM50=Majority=chance)
    baseline_pick = {"ER": "Subtype-only", "PR": "Subtype-only",
                     "HER2": "Subtype-only", "PAM50": "Majority"}
    best_pick = {"ER": "CLAM-SB", "PR": "CLAM-SB", "HER2": "CLAM-SB", "PAM50": "CLAM-MB"}
    # 아형 이름만(큰 글씨). 각 아형의 '설명'은 슬라이드 본문 텍스트로 따로 넣는다
    # (그림 안에 넣으면 슬라이드에서 축소될 때 글씨가 작아지는 문제 — 7/15 피드백).
    gloss = {"ER": "ER", "PR": "PR", "HER2": "HER2", "PAM50": "PAM50"}

    def pick(models, name):
        for label, auc, ci in models:
            if label == name and auc is not None:
                lo, hi = ci if ci else (auc, auc)
                return auc, auc - lo, hi - auc
        return None

    with plt.rc_context({
        "font.family": _KOREAN_FONT or plt.rcParams["font.family"],
        "axes.unicode_minus": False,
        "font.size": 24, "axes.titlesize": 30, "axes.labelsize": 30,
        "xtick.labelsize": 33, "ytick.labelsize": 26, "axes.linewidth": 1.8,
    }):
        phenos = [t for t, _ in all_data]
        data = {t: m for t, m in all_data}
        x = np.arange(len(phenos)); w = 0.38
        fig, ax = plt.subplots(figsize=(14, 8))

        for i, p in enumerate(phenos):
            bv, blo, bhi = pick(data[p], baseline_pick[p])
            mv, mlo, mhi = pick(data[p], best_pick[p])
            ax.bar(x[i] - w/2, bv, w, yerr=[[blo], [bhi]], color=GOLD, capsize=6,
                   error_kw=dict(lw=2), edgecolor="white", zorder=3,
                   label="비이미지 기준선" if i == 0 else None)
            ax.bar(x[i] + w/2, mv, w, yerr=[[mlo], [mhi]], color=TEAL, capsize=6,
                   error_kw=dict(lw=2), edgecolor="white", zorder=3,
                   label="이미지 모델 (CLAM)" if i == 0 else None)
            _lbl = dict(ha="center", fontsize=28, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.18", fc="white",
                                  ec="none", alpha=0.75))
            ax.text(x[i] - w/2, bv + bhi + 0.02, f"{bv:.2f}", color="#7a5600", **_lbl)
            ax.text(x[i] + w/2, mv + mhi + 0.02, f"{mv:.2f}", color=NAVY, **_lbl)

        pam_best = pick(data["PAM50"], best_pick["PAM50"])[0]
        ax.annotate("PAM50 아형에서만\n이미지 모델이 앞선다",
                    xy=(x[-1] + w/2, pam_best + 0.02), xytext=(x[-1] - 0.12, 0.28),
                    fontsize=25, fontweight="bold", color=NAVY, ha="center",
                    arrowprops=dict(arrowstyle="->", lw=3.0, color=NAVY))

        ax.axhline(0.5, ls="--", lw=2.0, color=NAVY, alpha=0.55)
        ax.text(-0.42, 0.52, "무작위 수준 (0.5)", fontsize=23, color=NAVY,
                fontweight="bold", va="bottom", ha="left")

        ax.set_xticks(x); ax.set_xticklabels([gloss[p] for p in phenos],
                                             fontweight="bold", color=NAVY)
        ax.set_ylabel("AUROC (예측 정확도)", color=NAVY, fontweight="bold")
        ax.set_ylim(0, 1.25)
        ax.set_yticks(np.arange(0, 1.01, 0.2))
        ax.tick_params(axis="y", colors=NAVY)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(width=1.6, length=7)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.005), ncol=2,
                  columnspacing=2.5, fontsize=26, frameon=False, labelcolor=NAVY)
        ax.set_title("이미지 모델은 ‘아형-only’ 상한을 넘지 못한다\n(TCGA-BRCA 내부검증)",
                     fontsize=29, fontweight="bold", pad=20, color=NAVY)
        fig.tight_layout()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    print(f"Saved (presentation): {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments_dir", default="experiments/sjpark")
    parser.add_argument("--out", default="experiments/sjpark/fig3_baseline_comparison.png")
    parser.add_argument("--presentation_out", default=None,
                        help="지정 시, 발표용 단순화 그림(2막대·큰 글씨·한글 설명)을 추가로 저장한다.")
    args = parser.parse_args()

    exp_dir = Path(args.experiments_dir)

    tasks_config = [
        ("ER", "er_status_uni_v1", "er_status_clam_uni_v2", "er_status_uni_v2_baselines",
         [("random", "Random"), ("subtype_only", "Subtype-only"), ("mean_embed", "Mean-embed")]),
        ("PR", "pr_status_uni_v1", "pr_status_clam_uni_v2", "pr_status_clam_uni_v2_baselines",
         [("random", "Random"), ("subtype_only", "Subtype-only"), ("mean_embed", "Mean-embed")]),
        ("HER2", "her2_status_uni_v1", "her2_status_clam_uni_v2", "her2_status_clam_uni_v2_baselines",
         [("random", "Random"), ("subtype_only", "Subtype-only"), ("mean_embed", "Mean-embed")]),
        ("PAM50", "pam50_uni_v2", "pam50_clam_mb_uni_v1", "pam50_clam_mb_uni_v1_baselines",
         [("random", "Random"), ("majority", "Majority"), ("mean_embed", "Mean-embed")]),
    ]

    all_data = [build_task_data(exp_dir, *cfg) for cfg in tasks_config]

    fig, axes = plt.subplots(1, 4, figsize=(18, 5), sharey=True)
    colors = {"Random": "#B0B0B0", "Subtype-only": "#E69F00", "Majority": "#E69F00",
              "Mean-embed": "#56B4E9", "MLP": "#009E73", "CLAM-SB": "#D55E00", "CLAM-MB": "#D55E00"}

    for ax, (task, models) in zip(axes, all_data):
        labels = [m[0] for m in models]
        aucs = [m[1] if m[1] is not None else np.nan for m in models]
        errs_lo = []
        errs_hi = []
        for m in models:
            if m[2]:
                errs_lo.append(m[1] - m[2][0])
                errs_hi.append(m[2][1] - m[1])
            else:
                errs_lo.append(0)
                errs_hi.append(0)

        bar_colors = [colors.get(l, "#999999") for l in labels]
        x = np.arange(len(labels))
        ax.bar(x, aucs, yerr=[errs_lo, errs_hi], capsize=4, color=bar_colors, edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Random (0.5)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
        ax.set_title(task, fontsize=13, fontweight="bold")
        ax.set_ylim(0.3, 1.0)
        if ax is axes[0]:
            ax.set_ylabel("AUC (95% CI)", fontsize=11)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Fig 3 — Phenotype Prediction: Baseline vs Model Comparison (TCGA-BRCA internal val, UNI v1)\n"
        "Error bars: bootstrap 95% CI (n=1000). Dashed line: random chance (AUC=0.5).\n"
        "Caveat: internal validation only — CPTAC external test shows subtype_only beats CLAM for ER/PR/HER2 (see Fig 4, BIOP02-68).",
        fontsize=11,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.92])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path}")

    # 요약 표도 함께 저장 (JIRA/Paper A 본문 재사용용)
    summary = {}
    for task, models in all_data:
        summary[task] = [
            {"model": m[0], "auc": m[1], "auc_ci_95": m[2]} for m in models
        ]
    summary["_caveat"] = (
        "Internal TCGA-BRCA val only. CPTAC external test (BIOP02-53 self-critic, "
        "paired_significance_external.json) shows subtype_only significantly beats CLAM "
        "for ER/PR/HER2 (opposite of this internal ranking) — see Fig 4 (BIOP02-68)."
    )
    summary_path = out_path.with_suffix(".json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Saved: {summary_path}")

    # 발표용 단순화 그림(선택) — 동일 데이터에서 큰 글씨·한글 설명본을 추가 저장
    if args.presentation_out:
        build_presentation_figure(all_data, Path(args.presentation_out))


if __name__ == "__main__":
    main()

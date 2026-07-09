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
import numpy as np


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments_dir", default="experiments/sjpark")
    parser.add_argument("--out", default="experiments/sjpark/fig3_baseline_comparison.png")
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


if __name__ == "__main__":
    main()

"""
BIOP02-68 — Fig 4: External validation + anti-shortcut sanity lock.

각 태스크(ER/PR/HER2/PAM50)에 대해 CLAM의 내부(TCGA val) AUC, 외부(CPTAC) AUC,
그리고 외부에서의 최우수 trivial baseline AUC를 나란히 비교한다.

"Sanity lock" 판정 = CLAM이 외부셋에서 최우수 baseline을 paired bootstrap 기준
유의하게 상회하는가 (paired_significance_external.json). 실패 시 CLAM이 내부에서
보인 성능이 형태학적 신호가 아니라 subtype-상관 아티팩트(shortcut)일 가능성을 의미.

Run:
    python agents/modeling/scripts/make_fig4_external_sanity_lock.py \
        --experiments_dir experiments/sjpark \
        --out experiments/sjpark/fig4_external_sanity_lock.png
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


TASKS = [
    {
        "label": "ER",
        "clam_dir": "er_status_clam_uni_v2",
        "baselines_dir": "er_status_uni_v2_ext_baselines",
        "best_baseline_name": "subtype_only",
        "sig_diff_key": "diff_clam_minus_subtype",
        "sig_auc_key": "auc_subtype_only",
    },
    {
        "label": "PR",
        "clam_dir": "pr_status_clam_uni_v2",
        "baselines_dir": "pr_status_uni_v2_ext_baselines",
        "best_baseline_name": "subtype_only",
        "sig_diff_key": "diff_clam_minus_subtype",
        "sig_auc_key": "auc_subtype_only",
    },
    {
        "label": "HER2",
        "clam_dir": "her2_status_clam_uni_v2",
        "baselines_dir": "her2_status_uni_v2_ext_baselines",
        "best_baseline_name": "subtype_only",
        "sig_diff_key": "diff_clam_minus_subtype",
        "sig_auc_key": "auc_subtype_only",
    },
    {
        "label": "PAM50",
        "clam_dir": "pam50_clam_mb_uni_v1",
        "baselines_dir": "pam50_uni_v1_ext_baselines",
        "best_baseline_name": "mean_embed",
        "sig_diff_key": "diff_clam_minus_mean_embed",
        "sig_auc_key": "auc_mean_embed",
    },
]


def get_baseline(baselines_json: dict, name: str):
    for b in (baselines_json or {}).get("ext_baselines", []) or []:
        if b["baseline"] == name:
            return b.get("auc"), b.get("auc_ci_95")
    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments_dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    exp_dir = Path(args.experiments_dir)

    fig, axes = plt.subplots(1, 4, figsize=(18, 5.5))
    summary = {}

    for ax, task in zip(axes, TASKS):
        metrics = load_json(exp_dir / task["clam_dir"] / "metrics.json")
        baselines = load_json(exp_dir / task["baselines_dir"] / "trivial_baselines.json")
        sig = load_json(exp_dir / task["clam_dir"] / "paired_significance_external.json")

        int_auc, int_ci = (metrics or {}).get("auc"), (metrics or {}).get("auc_ci_95")
        ext_auc, ext_ci = (metrics or {}).get("ext_auc"), (metrics or {}).get("ext_auc_ci_95")
        base_auc, base_ci = get_baseline(baselines, task["best_baseline_name"])

        bars = [
            ("CLAM\n(internal)", int_auc, int_ci, "#4C72B0"),
            ("CLAM\n(external)", ext_auc, ext_ci, "#DD8452"),
            (f"{task['best_baseline_name']}\n(external)", base_auc, base_ci, "#999999"),
        ]

        labels = [b[0] for b in bars]
        aucs = [b[1] if b[1] is not None else 0 for b in bars]
        errs_lo = [(b[1] - b[2][0]) if b[1] is not None and b[2] else 0 for b in bars]
        errs_hi = [(b[2][1] - b[1]) if b[1] is not None and b[2] else 0 for b in bars]
        colors = [b[3] for b in bars]

        x = np.arange(len(labels))
        ax.bar(x, aucs, yerr=[errs_lo, errs_hi], capsize=4, color=colors, edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0.3, 1.05)
        if ax is axes[0]:
            ax.set_ylabel("AUC (95% CI)", fontsize=11)
        ax.grid(axis="y", alpha=0.3)

        passed = bool(sig and sig.get("significant_at_0.05") and sig.get(task["sig_diff_key"], -1) > 0)
        verdict = "PASS" if passed else "FAIL"
        color = "#2A9D5C" if passed else "#D62839"
        ax.set_title(f"{task['label']}  [{verdict}]", fontsize=13, fontweight="bold", color=color)

        summary[task["label"]] = {
            "internal_auc": int_auc,
            "internal_auc_ci_95": int_ci,
            "external_auc": ext_auc,
            "external_auc_ci_95": ext_ci,
            "external_best_baseline": task["best_baseline_name"],
            "external_best_baseline_auc": base_auc,
            "external_best_baseline_ci_95": base_ci,
            "paired_diff_clam_minus_baseline": sig.get(task["sig_diff_key"]) if sig else None,
            "p_value_approx": sig.get("p_value_approx") if sig else None,
            "sanity_lock": "PASS" if passed else "FAIL",
        }

    fig.suptitle(
        "Fig 4 — External Validation & Anti-Shortcut Sanity Lock (TCGA train → CPTAC test, UNI v1)\n"
        "PASS = CLAM significantly beats best external trivial baseline (paired bootstrap, n=2000).\n"
        "FAIL = CLAM's internal ranking does not survive external test — internal AUC may reflect a subtype/site-correlated shortcut, not genuine morphology.",
        fontsize=11,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.88])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path}")

    summary_path = out_path.with_suffix(".json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Saved: {summary_path}")

    print("\n요약:")
    for label, s in summary.items():
        print(f"  {label:6s} internal={s['internal_auc']}  external={s['external_auc']}  "
              f"vs {s['external_best_baseline']}={s['external_best_baseline_auc']}  -> {s['sanity_lock']}")


if __name__ == "__main__":
    main()

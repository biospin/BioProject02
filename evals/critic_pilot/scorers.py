"""Deterministic scorers for BIOP02 Critic checklist items #6, #2, #7.

Pure python — no inspect_ai import here on purpose, so that:
  1. the scoring logic is unit-testable without an eval harness,
  2. `run_pilot.py` (fallback runner) and `critic_pilot.py` (Inspect eval)
     share exactly one implementation.

Each scorer takes a parsed critic_report dict (schemas/critic_report.schema.json)
plus an optional resolved metrics.json dict, and returns a Verdict.

Status vocabulary matches the schema: pass | caution | reject | not_applicable.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Verdict:
    status: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reasons": self.reasons}


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def _iter_text(node: Any, path: str = "", skip_prefix: str | None = None) -> list[tuple[str, str]]:
    """Yield (json_path, text) for every string in the report.

    `skip_prefix` excludes a subtree. See SELF_REFERENCE_EXEMPT below for why
    that is necessary rather than merely convenient.
    """
    if skip_prefix and path.startswith(skip_prefix):
        return []
    out: list[tuple[str, str]] = []
    if isinstance(node, str):
        out.append((path or "$", node))
    elif isinstance(node, dict):
        for k, v in node.items():
            out.extend(_iter_text(v, f"{path}.{k}" if path else k, skip_prefix))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_iter_text(v, f"{path}[{i}]", skip_prefix))
    return out


# A check's own evidence/notes are META-COMMENTARY ABOUT THE CHECK, not claims
# the experiment makes. A reviewer attesting to checklist #6 writes, verbatim,
# from a real 2026-07-17 report:
#
#   "금지 표현('drug response prediction', 'personalized therapy',
#    'patient-specific treatment') 미발견"
#
# i.e. the reviewer quotes the banned phrases in order to record that they are
# ABSENT. Scanning that subtree flags the report for proving its own compliance.
# Measured against real artifacts: 3 of 12 reports (25%) were false-positived
# this way before this exemption existed.
#
# TRADE-OFF (documented in README): this opens a loophole — a genuine violation
# hidden inside checks.drp_framing.notes is now missed. Accepted because a 25%
# false-positive rate makes the scorer unusable, whereas the loophole requires a
# reviewer to write a violation into the very field attesting there is none.
SELF_REFERENCE_EXEMPT = {
    "drp_framing": "checks.drp_framing",
    "claim_level": "checks.claim_level",
}


def load_report(path: str | Path) -> dict[str, Any]:
    """Load a critic_report, stripping harness-only keys.

    `_case_meta` is fixture scaffolding, not part of critic_report.schema.json
    (which sets additionalProperties: false). It must never be scored — its
    prose describes the defect and would otherwise trip the text scanners,
    making a case fail for the wrong reason.
    """
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    doc.pop("_case_meta", None)
    return doc


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_metrics_for(report: dict[str, Any], case_path: str | Path) -> dict[str, Any] | None:
    """Resolve experiment.metrics_path.

    Two real layouts are supported:
      * fixture:  a `<case>.metrics.json` sidecar next to the case file;
      * repo:     experiments/<user>/<exp>/metrics.json, a repo-relative path
                  as written by real critic_report.json files.
    """
    mp = (report.get("experiment") or {}).get("metrics_path")
    if not mp:
        return None
    if not str(mp).endswith(".json"):
        # Real case: experiments/crosscancer points metrics_path at a .md
        # scoreboard. Parsing it raised JSONDecodeError and crashed the loader.
        return None
    for cand in (Path(case_path).parent / Path(mp).name, REPO_ROOT / mp, Path(mp)):
        if cand.exists() and cand.is_file():
            try:
                with open(cand, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
    return None


def get_ci(d: dict[str, Any]) -> list[float] | None:
    """Bootstrap CI accessor.

    Real metrics.json uses `auc_ci_95`; the schema names neither. Both spellings
    are accepted rather than silently missing the field (which would make every
    real experiment look like it had no CI).
    """
    for key in ("auc_ci95", "auc_ci_95"):
        v = d.get(key)
        if isinstance(v, list) and len(v) == 2:
            return [float(v[0]), float(v[1])]
    return None


def load_baselines_for(
    report: dict[str, Any], case_path: str | Path, metrics: dict[str, Any] | None
) -> dict[str, dict[str, Any]] | None:
    """Resolve trivial baselines into {name: {auc, auprc, ...}}.

    Real BIOP02 layout (verified 2026-07-17 against 10 experiments): baselines do
    NOT live in metrics.json. They are a separate run at
    `experiments/<user>/<exp>_baselines/trivial_baselines.json`, where `baselines`
    is a LIST of {"baseline": name, "auc":..., "auprc":...}.
    The fixture layout embeds a `baselines` DICT in metrics.json. Both are read.
    """
    # (a) fixture form: dict inside metrics.json
    if metrics and isinstance(metrics.get("baselines"), dict):
        return metrics["baselines"]

    # (b) real form: sibling *_baselines/trivial_baselines.json
    mp = (report.get("experiment") or {}).get("metrics_path")
    if mp:
        exp_dir = (REPO_ROOT / mp).parent
        cand = exp_dir.parent / f"{exp_dir.name}_baselines" / "trivial_baselines.json"
        if cand.exists():
            with open(cand, encoding="utf-8") as f:
                doc = json.load(f)
            entries = doc.get("baselines")
            if isinstance(entries, list):
                return {e["baseline"]: e for e in entries if isinstance(e, dict) and "baseline" in e}
    return None


# --------------------------------------------------------------------------
# #6 DRP Framing Check
# checklist_v1.md §#6: grep 0건 + claim_level == hypothesis_only -> pass
#                      금지 표현 1건 이상 -> reject
# --------------------------------------------------------------------------

# Sourced verbatim from checklist_v1.md #6 grep + CLAUDE.md "Absolute Prohibitions",
# extended with the Korean equivalents the prohibition list names.
DRP_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"drug\s+response\s+prediction", "DRP framing: 'drug response prediction'"),
    (r"\bDRP\s+model\b", "DRP framing: 'DRP model'"),
    (r"personali[sz]ed\s+therapy", "DRP framing: 'personalized therapy'"),
    (r"patient[-\s]specific.{0,20}treatment", "DRP framing: 'patient-specific ... treatment'"),
    (r"optimal\s+treatment", "DRP framing: 'optimal treatment'"),
    (r"predict.{0,20}drug\s+response", "DRP framing: 'predict ... drug response'"),
    (r"환자\s*맞춤", "DRP framing: '환자 맞춤'"),
    (r"맞춤\s*(형)?\s*치료", "DRP framing: '맞춤 치료'"),
    (r"최적\s*(의)?\s*치료", "DRP framing: '최적 치료'"),
    (r"약물\s*반응\s*예측", "DRP framing: '약물 반응 예측'"),
]

ALLOWED_TASKS = {"er_status", "pr_status", "her2_status", "pam50"}


def score_drp_framing(
    report: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    baselines: dict[str, dict[str, Any]] | None = None,
) -> Verdict:
    reasons: list[str] = []

    for jpath, text in _iter_text(report, skip_prefix=SELF_REFERENCE_EXEMPT["drp_framing"]):
        for pat, label in DRP_FORBIDDEN_PATTERNS:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                reasons.append(f"{label} @ {jpath}: '{m.group(0)}'")

    # checklist #6 names four exact task tokens, but real reports use composite
    # descriptors ("molecular_phenotype_mil (er/pr/her2_status)"). Require that an
    # allowed token APPEARS, rather than that the field equals one — equality would
    # reject legitimate MIL experiments on naming style alone.
    task = (report.get("experiment") or {}).get("task")
    if task is not None and not any(t in task for t in ALLOWED_TASKS):
        reasons.append(
            f"experiment.task='{task}' names none of {sorted(ALLOWED_TASKS)} (checklist #6)"
        )

    claim = report.get("claim_level")
    if claim != "hypothesis_only":
        reasons.append(f"claim_level='{claim}' != 'hypothesis_only' (checklist #6 -> reject)")

    if reasons:
        return Verdict("reject", reasons)
    return Verdict("pass", ["no forbidden DRP expression; task allowed; claim_level=hypothesis_only"])


# --------------------------------------------------------------------------
# #7 Claim-Level Check
# checklist_v1.md §#7: hypothesis_only 명시 + 표현 수준 적절 -> pass
#                      약간 과장 -> caution ; "predicts clinical outcome" 류 -> reject
# --------------------------------------------------------------------------

CLAIM_REJECT_PATTERNS: list[tuple[str, str]] = [
    (r"predicts?\s+clinical\s+outcome", "overclaim: 'predicts clinical outcome'"),
    (r"clinically\s+actionable", "overclaim: 'clinically actionable'"),
    (r"ready\s+for\s+clinical\s+use", "overclaim: 'ready for clinical use'"),
    (r"can\s+replace\s+(IHC|molecular\s+testing)", "overclaim: 'can replace IHC/molecular testing'"),
    (r"임상(적)?\s*(으로)?\s*적용\s*가능", "overclaim: '임상 적용 가능'"),
]

CLAIM_CAUTION_PATTERNS: list[tuple[str, str]] = [
    (r"\bgenerali[sz]es?\s+to\s+all\b", "possible overreach: 'generalizes to all'"),
    (r"\bproves?\b", "possible overreach: 'proves'"),
    (r"\bdemonstrates?\s+that\s+.{0,30}\bcauses?\b", "possible overreach: causal 'demonstrates ... causes'"),
    (r"\bconfirms?\s+that\b", "possible overreach: 'confirms that'"),
]

VALID_CRITIC_STATUS = {"pass", "caution", "reject"}
REQUIRED_CHECK_KEYS = {
    "data_leakage",
    "baseline_comparison",
    "counterfactual_check",
    "cross_dataset_check",
    "biological_plausibility",
    "drp_framing",
    "claim_level",
}


def score_claim_level(
    report: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    baselines: dict[str, dict[str, Any]] | None = None,
) -> Verdict:
    reasons: list[str] = []
    hard_reject = False

    # (a) field presence / value
    if "claim_level" not in report:
        reasons.append("missing required field 'claim_level' (schema + checklist #7)")
        hard_reject = True
    elif report["claim_level"] != "hypothesis_only":
        reasons.append(f"claim_level='{report['claim_level']}' != 'hypothesis_only'")
        hard_reject = True

    if "critic_status" not in report:
        reasons.append("missing required field 'critic_status' (schema)")
        hard_reject = True
    elif report["critic_status"] not in VALID_CRITIC_STATUS:
        reasons.append(
            f"critic_status='{report['critic_status']}' not in {sorted(VALID_CRITIC_STATUS)}"
        )
        hard_reject = True

    checks = report.get("checks")
    if not isinstance(checks, dict):
        reasons.append("missing required field 'checks' (schema)")
        hard_reject = True
    else:
        missing = REQUIRED_CHECK_KEYS - set(checks)
        if missing:
            reasons.append(f"checks missing item(s): {sorted(missing)}")
            hard_reject = True

    # (b) aggregation consistency — checklist_v1.md 최종 판정 규칙
    if isinstance(checks, dict) and report.get("critic_status") in VALID_CRITIC_STATUS:
        statuses = [
            c.get("status")
            for c in checks.values()
            if isinstance(c, dict) and c.get("status") != "not_applicable"
        ]
        if "reject" in statuses:
            expected = "reject"
        elif "caution" in statuses:
            expected = "caution"
        else:
            expected = "pass"
        if report["critic_status"] != expected:
            reasons.append(
                f"critic_status='{report['critic_status']}' inconsistent with checks "
                f"(rollup rule -> '{expected}')"
            )
            hard_reject = True

    # (c) claim language level
    caution_hits: list[str] = []
    for jpath, text in _iter_text(report, skip_prefix=SELF_REFERENCE_EXEMPT["claim_level"]):
        for pat, label in CLAIM_REJECT_PATTERNS:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                reasons.append(f"{label} @ {jpath}: '{m.group(0)}'")
                hard_reject = True
        for pat, label in CLAIM_CAUTION_PATTERNS:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                caution_hits.append(f"{label} @ {jpath}: '{m.group(0)}'")

    if hard_reject:
        return Verdict("reject", reasons)
    if caution_hits:
        return Verdict("caution", caution_hits)
    return Verdict("pass", ["claim_level=hypothesis_only; critic_status consistent; no overclaim language"])


# --------------------------------------------------------------------------
# #2 Baseline Comparison
# checklist_v1.md §#2: 3종 baseline(random / subtype-only / pixel-mean) 전부 존재 +
#   model AUC >= max(baseline)+0.03 + CI 비겹침 -> pass
#   +0.01~0.03 OR CI 겹침 -> caution
#   미달 OR 수치 누락 -> reject
# --------------------------------------------------------------------------

# checklist_v1.md #2 names exactly these three. NOT changed to match practice:
# a survey of all 10 real *_baselines/trivial_baselines.json on 2026-07-17 found
# {random, majority|subtype_only, mean_embed} and NEVER pixel_mean. Whether
# mean_embed (mean of UNI embeddings) may stand in for pixel-mean (mean of raw
# pixels) is a Critic-policy question owned by braveji — CLAUDE.md forbids this
# eval from setting its own controls, so the checklist's list is used verbatim
# and the divergence is surfaced as a reject for a human to adjudicate.
REQUIRED_BASELINES = ["random", "subtype_only", "pixel_mean"]
MARGIN_PASS = 0.03
MARGIN_CAUTION = 0.01


def score_baseline_comparison(
    report: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    baselines: dict[str, dict[str, Any]] | None = None,
) -> Verdict:
    reasons: list[str] = []

    if metrics is None:
        return Verdict("reject", ["metrics.json not resolvable from experiment.metrics_path (#2: 수치 누락)"])

    if not isinstance(baselines, dict) or not baselines:
        return Verdict("reject", ["no trivial baselines resolvable (#2: baseline 수치 누락)"])

    missing = [b for b in REQUIRED_BASELINES if b not in baselines]
    if missing:
        reasons.append(
            f"required baseline(s) absent: {missing}; present: {sorted(baselines)}"
        )
        return Verdict("reject", reasons)

    model_auc = metrics.get("auc")
    if not isinstance(model_auc, (int, float)):
        return Verdict("reject", ["metrics.json 'auc' missing or non-numeric (#2: 수치 누락)"])

    b_aucs: dict[str, float] = {}
    for b in REQUIRED_BASELINES:
        v = baselines[b].get("auc") if isinstance(baselines[b], dict) else None
        if not isinstance(v, (int, float)):
            return Verdict("reject", [f"baseline '{b}' has no numeric auc (#2: 수치 누락)"])
        b_aucs[b] = float(v)

    max_b = max(b_aucs.values())
    max_b_name = max(b_aucs, key=b_aucs.__getitem__)
    margin = model_auc - max_b

    if margin < MARGIN_CAUTION:
        return Verdict(
            "reject",
            [f"model auc={model_auc:.3f} vs best baseline '{max_b_name}'={max_b:.3f} "
             f"(margin {margin:+.3f} < {MARGIN_CAUTION}) -> baseline 미달"],
        )

    # AUPRC vs subtype-only (불균형 데이터 필수)
    model_auprc = metrics.get("auprc")
    sub_auprc = baselines["subtype_only"].get("auprc") if isinstance(baselines["subtype_only"], dict) else None
    if isinstance(model_auprc, (int, float)) and isinstance(sub_auprc, (int, float)):
        if model_auprc < sub_auprc:
            reasons.append(
                f"auprc={model_auprc:.3f} < subtype_only auprc={sub_auprc:.3f} (#2 AUPRC 요건 미달)"
            )
            return Verdict("reject", reasons)
    else:
        reasons.append("auprc comparison unavailable (model or subtype_only auprc missing)")

    # bootstrap CI overlap
    ci_overlap = False
    m_ci = get_ci(metrics)
    if m_ci is not None:
        for b in REQUIRED_BASELINES:
            b_ci = get_ci(baselines[b])
            if b_ci is not None:
                if m_ci[0] <= b_ci[1]:
                    ci_overlap = True
                    reasons.append(
                        f"bootstrap CI overlap: model lower={m_ci[0]:.3f} <= "
                        f"'{b}' upper={b_ci[1]:.3f}"
                    )
    else:
        reasons.append("model auc_ci95 absent — CI non-overlap unverified")
        ci_overlap = True

    if margin < MARGIN_PASS:
        reasons.insert(
            0,
            f"margin over best baseline '{max_b_name}' = {margin:+.3f} "
            f"(in {MARGIN_CAUTION}~{MARGIN_PASS} band)",
        )
        return Verdict("caution", reasons)
    if ci_overlap:
        return Verdict("caution", reasons)

    return Verdict(
        "pass",
        [f"all 3 baselines present; margin {margin:+.3f} >= {MARGIN_PASS} over "
         f"'{max_b_name}'={max_b:.3f}; CI non-overlapping"],
    )


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------

def load_context(case_path: str | Path) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, dict[str, Any]] | None]:
    """Load (report, metrics, baselines) for a case or a real experiment."""
    report = load_report(case_path)
    metrics = load_metrics_for(report, case_path)
    baselines = load_baselines_for(report, case_path, metrics)
    return report, metrics, baselines


SCORERS = {
    "drp_framing": score_drp_framing,          # checklist #6
    "claim_level": score_claim_level,          # checklist #7
    "baseline_comparison": score_baseline_comparison,  # checklist #2
}

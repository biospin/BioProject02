"""Inspect eval suite — BIOP02 Critic checklist items #6, #7, #2.

Formalizes three of the seven checklist items (agents/critic/checklist_v1.md) as
Inspect tasks, per the harness memo §5.2 ("7항목 체크리스트 -> 항목별 scorer로 인코딩")
and §5.4 ("파일럿 1개: BIOP02 Critic 3개 항목만 Inspect로 -> 메트릭 통과 확인 -> 확장").

The checks are DETERMINISTIC — they read a critic_report.json artifact and apply
the checklist's own thresholds. No LLM is involved in the judgement, so the eval
runs with the built-in mock model and needs no API key:

    inspect eval critic_pilot.py --model mockllm/model

This is deliberate. checklist_v1.md #6 is literally a grep, #7 is field presence
plus a rollup rule, and #2 is a numeric margin — encoding them as an LLM judge
would add nondeterminism to checks that have exact answers. It also honours the
CLAUDE.md prohibition on "Critic agent setting its own thresholds": every
threshold here is quoted from the checklist, not invented by a model.

Tasks:
    critic_drp_framing          -> checklist #6
    critic_claim_level          -> checklist #7
    critic_baseline_comparison  -> checklist #2
    critic_coverage_corpus      -> the 6 real 2026-07-17 failures (coverage measurement)
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import Generate, TaskState, solver

from scorers import SCORERS, load_context

ROOT = Path(__file__).parent
SV_DIR = ROOT / "cases" / "scorer_validation"
RC_DIR = ROOT / "cases" / "regression_corpus"


def _case_files(d: Path) -> list[Path]:
    return sorted(p for p in d.glob("*.json") if not p.name.endswith(".metrics.json"))


def _build_dataset(dirs: list[Path], scorer_name: str) -> MemoryDataset:
    samples: list[Sample] = []
    for d in dirs:
        for p in _case_files(d):
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            meta = doc.get("_case_meta")
            if not meta or scorer_name not in (meta.get("expected") or {}):
                # pipeline-only corpus records (RC-01..03) carry no critic_report
                # and no expectation for this scorer — excluded by construction.
                continue
            samples.append(
                Sample(
                    input=f"Apply checklist item '{scorer_name}' to {p.name}",
                    target=meta["expected"][scorer_name],
                    id=p.stem,
                    metadata={
                        "case_path": str(p),
                        "scorer_name": scorer_name,
                        "kind": meta.get("kind", meta.get("classification", "")),
                        "intent": meta.get("intent", meta.get("class_reason", "")),
                        "expected_is_a_miss": meta.get("expected_is_a_miss", False),
                    },
                )
            )
    return MemoryDataset(samples)


@solver
def apply_checklist_item():
    """Runs the deterministic checklist scorer. Never calls the model."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        case_path = state.metadata["case_path"]
        fn = SCORERS[state.metadata["scorer_name"]]
        report, metrics, baselines = load_context(case_path)
        verdict = fn(report, metrics, baselines)
        state.output.completion = verdict.status
        state.metadata["reasons"] = verdict.reasons
        return state

    return solve


@scorer(metrics=[accuracy(), stderr()])
def checklist_status_match():
    """Correct iff the scorer's verdict equals the checklist-derived expectation."""

    async def score(state: TaskState, target: Target) -> Score:
        predicted = (state.output.completion or "").strip()
        expected = target.text.strip()
        reasons = "; ".join(state.metadata.get("reasons", [])) or "(no reasons)"
        return Score(
            value=CORRECT if predicted == expected else INCORRECT,
            answer=predicted,
            explanation=f"expected={expected} predicted={predicted} :: {reasons}",
            metadata={
                "kind": state.metadata.get("kind"),
                "expected_is_a_miss": state.metadata.get("expected_is_a_miss"),
            },
        )

    return score


def _item_task(scorer_name: str) -> Task:
    return Task(
        dataset=_build_dataset([SV_DIR, RC_DIR], scorer_name),
        solver=apply_checklist_item(),
        scorer=checklist_status_match(),
    )


@task
def critic_drp_framing() -> Task:
    """checklist_v1.md #6 — prohibited DRP framing / task field / claim_level."""
    return _item_task("drp_framing")


@task
def critic_claim_level() -> Task:
    """checklist_v1.md #7 — claim_level + critic_status presence, rollup consistency, overclaim language."""
    return _item_task("claim_level")


@task
def critic_baseline_comparison() -> Task:
    """checklist_v1.md #2 — random / subtype-only / pixel-mean baselines and margin."""
    return _item_task("baseline_comparison")


@task
def critic_coverage_corpus() -> Task:
    """Coverage measurement over the 6 real 2026-07-17 failures only.

    NOTE ON READING THIS TASK'S SCORE: a high score here does NOT mean the
    failures were caught. RC-04/05/06 have expected='pass' for all three scorers
    because the pilot's three items provably do not cover cohort-size, citation,
    or unit errors. 'Correct' here means 'the scorer behaved as the gap analysis
    predicts'. The finding is in cases/regression_corpus/*.json -> _case_meta
    .needs_scorer, and in the coverage table printed by run_pilot.py.
    """
    samples: list[Sample] = []
    for scorer_name in SCORERS:
        samples.extend(_build_dataset([RC_DIR], scorer_name).samples)
    for s in samples:
        s.id = f"{s.id}::{s.metadata['scorer_name']}"
    return Task(
        dataset=MemoryDataset(samples),
        solver=apply_checklist_item(),
        scorer=checklist_status_match(),
    )

"""Standalone runner — same scorers as the Inspect eval, no harness required.

Purpose is not to duplicate Inspect. It reports the two things an Inspect
accuracy score does not show on its own:

  1. the per-scorer CONFUSION MATRIX (does the scorer both fire and stay silent?),
  2. the COVERAGE TABLE over the 6 real 2026-07-17 failures (what the pilot misses).

    /opt/envs/spatialpatho/bin/python run_pilot.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from scorers import SCORERS, load_context

ROOT = Path(__file__).parent
SV_DIR = ROOT / "cases" / "scorer_validation"
RC_DIR = ROOT / "cases" / "regression_corpus"


def case_files(d: Path) -> list[Path]:
    return sorted(p for p in d.glob("*.json") if not p.name.endswith(".metrics.json"))


def run_all() -> tuple[list[dict], list[dict]]:
    results: list[dict] = []
    corpus_records: list[dict] = []
    for d in (SV_DIR, RC_DIR):
        for p in case_files(d):
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            meta = doc.get("_case_meta")
            if meta is None:
                corpus_records.append(doc)  # RC-01..03 pipeline records
                continue
            report, metrics, baselines = load_context(p)
            for name, fn in SCORERS.items():
                exp = (meta.get("expected") or {}).get(name)
                if exp is None:
                    continue
                v = fn(report, metrics, baselines)
                results.append({
                    "case": p.stem,
                    "layer": meta.get("layer"),
                    "scorer": name,
                    "expected": exp,
                    "predicted": v.status,
                    "ok": v.status == exp,
                    "reasons": v.reasons,
                    "kind": meta.get("kind", meta.get("classification")),
                    "meta": meta,
                })
    return results, corpus_records


SCHEMA_PATH = ROOT.parent.parent / "schemas" / "critic_report.schema.json"


def validate_fixtures() -> tuple[int, int, list[str]]:
    """Every case report must conform to schemas/critic_report.schema.json.

    Cases that intentionally violate the schema (missing claim_level, missing a
    check) are expected to fail validation — that IS their defect. Everything
    else must validate, which is what makes the fixtures credible.
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return 0, 0, ["jsonschema not installed — fixture validation skipped"]

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        validator = Draft202012Validator(json.load(f))

    conform, intentional = 0, 0
    notes: list[str] = []
    for d in (SV_DIR, RC_DIR):
        for p in case_files(d):
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            meta = doc.pop("_case_meta", None)
            if meta is None:
                continue
            errs = list(validator.iter_errors(doc))
            expects_schema_defect = p.stem in {
                "claim_fail_01_missing_field", "claim_fail_04_missing_check",
                "drp_fail_03_task_field",
            }
            if errs and not expects_schema_defect:
                notes.append(f"{p.stem}: UNEXPECTED schema error: {errs[0].message}")
            elif errs:
                intentional += 1
            else:
                conform += 1
    return conform, intentional, notes


def main() -> int:
    results, corpus_records = run_all()

    print("=" * 78)
    print("BIOP02 Critic pilot — deterministic scorers for checklist #6 / #7 / #2")
    print("=" * 78)

    conform, intentional, notes = validate_fixtures()
    print(f"\n[fixture check] {conform} case reports conform to "
          f"critic_report.schema.json; {intentional} violate it by design.")
    for n in notes:
        print(f"  !! {n}")

    # ---------------- Layer A: scorer validation --------------------------
    sv = [r for r in results if r["layer"] == "scorer_validation"]
    print("\n[Layer A] SCORER VALIDATION — crafted PASS/FAIL pairs\n")
    print(f"{'case':<38} {'scorer':<21} {'exp':<9} {'got':<9} ok")
    print("-" * 78)
    for r in sorted(sv, key=lambda x: (x["scorer"], x["case"])):
        print(f"{r['case']:<38} {r['scorer']:<21} {r['expected']:<9} "
              f"{r['predicted']:<9} {'OK' if r['ok'] else 'FAIL <<<'}")

    print("\nConfusion matrix per scorer (expected -> predicted):\n")
    for name in SCORERS:
        rows = [r for r in sv if r["scorer"] == name]
        cm: dict[tuple[str, str], int] = defaultdict(int)
        for r in rows:
            cm[(r["expected"], r["predicted"])] += 1
        n_ok = sum(1 for r in rows if r["ok"])
        fires = sum(1 for r in rows if r["expected"] != "pass")
        silent = sum(1 for r in rows if r["expected"] == "pass")
        print(f"  {name}: {n_ok}/{len(rows)} correct "
              f"({fires} must-fire, {silent} must-stay-silent)")
        for (e, p), c in sorted(cm.items()):
            mark = "" if e == p else "   <-- MISMATCH"
            print(f"      expected={e:<9} predicted={p:<9} n={c}{mark}")

    sv_ok = sum(1 for r in sv if r["ok"])
    print(f"\n  Layer A total: {sv_ok}/{len(sv)} correct")

    # ---------------- Layer B: real failure corpus ------------------------
    print("\n" + "=" * 78)
    print("[Layer B] REGRESSION CORPUS — 6 real failures of 2026-07-17")
    print("=" * 78)
    print("\nCoverage: does any of the 3 pilot scorers catch the failure?\n")

    covered = 0
    print(f"{'id':<7} {'classification':<40} caught?")
    print("-" * 78)
    for rec in sorted(corpus_records, key=lambda d: d["case_id"]):
        print(f"{rec['case_id']:<7} {rec['classification']:<40} n/a (no critic_report artifact)")

    rc = [r for r in results if r["layer"] == "regression_corpus"]
    by_case: dict[str, list[dict]] = defaultdict(list)
    for r in rc:
        by_case[r["case"]].append(r)
    for case, rows in sorted(by_case.items()):
        meta = rows[0]["meta"]
        flagged = [r["scorer"] for r in rows if r["predicted"] != "pass"]
        caught = bool(flagged)
        covered += caught
        print(f"{meta['case_id']:<7} {meta['classification']:<40} "
              f"{'YES: ' + ','.join(flagged) if caught else 'NO  (miss — as predicted)'}")

    print(f"\n  Real failures caught by the 3 pilot scorers: {covered}/6")
    print("  Out of eval scope (pipeline smoke, no artifact to review): "
          f"{len(corpus_records)}/6")
    print(f"  Doc/claim failures needing scorers this pilot does not have: "
          f"{len(by_case) - covered}/6")

    print("\nGap analysis — scorers required to close the corpus:\n")
    for case, rows in sorted(by_case.items()):
        meta = rows[0]["meta"]
        if meta.get("needs_scorer"):
            print(f"  {meta['case_id']}  {meta['title']}")
            print(f"        -> {meta['needs_scorer']}\n")
    for rec in sorted(corpus_records, key=lambda d: d["case_id"]):
        print(f"  {rec['case_id']}  {rec['title']}")
        print(f"        -> {rec['proposed_guard']}\n")

    # ---------------- verdict --------------------------------------------
    rc_ok = sum(1 for r in rc if r["ok"])
    all_ok = sv_ok + rc_ok
    total = len(results)
    print("=" * 78)
    print(f"TOTAL: {all_ok}/{total} scorer outputs matched expectation "
          f"(Layer A {sv_ok}/{len(sv)}, Layer B {rc_ok}/{len(rc)})")
    print("=" * 78)

    failures = [r for r in results if not r["ok"]]
    if failures:
        print("\nMISMATCHES:")
        for r in failures:
            print(f"  {r['case']} / {r['scorer']}: expected {r['expected']}, "
                  f"got {r['predicted']}")
            for reason in r["reasons"]:
                print(f"      - {reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

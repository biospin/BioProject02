"""Mutation test — proves the case set actually constrains the scorers.

An eval that a stub scorer can ace is measuring nothing. This replaces each
real scorer with degenerate ones (always-pass / always-reject) and asserts the
case set rejects them. Run after any change to cases/.

    /opt/envs/spatialpatho/bin/python mutation_check.py
"""

from __future__ import annotations

import sys

import scorers
from scorers import Verdict
from run_pilot import run_all

MUTANTS = {
    "always_pass": lambda r, m, b=None: Verdict("pass", ["stub"]),
    "always_reject": lambda r, m, b=None: Verdict("reject", ["stub"]),
    "always_caution": lambda r, m, b=None: Verdict("caution", ["stub"]),
}


def main() -> int:
    real = dict(scorers.SCORERS)
    baseline, _ = run_all()
    base_ok = sum(1 for r in baseline if r["ok"])
    print(f"real scorers:      {base_ok}/{len(baseline)} correct")

    failed_to_kill: list[str] = []
    for mut_name, mut_fn in MUTANTS.items():
        for target in real:
            scorers.SCORERS.clear()
            scorers.SCORERS.update(real)
            scorers.SCORERS[target] = mut_fn
            results, _ = run_all()
            rows = [r for r in results if r["scorer"] == target]
            ok = sum(1 for r in rows if r["ok"])
            killed = ok < len(rows)
            status = "killed" if killed else "SURVIVED <<<"
            print(f"  {target:<21} := {mut_name:<14} -> {ok}/{len(rows)} correct  [{status}]")
            if not killed:
                failed_to_kill.append(f"{target} := {mut_name}")

    scorers.SCORERS.clear()
    scorers.SCORERS.update(real)

    if failed_to_kill:
        print("\nFAIL — case set does not constrain these mutants:")
        for f in failed_to_kill:
            print(f"  {f}")
        return 1
    print("\nAll mutants killed: every scorer is genuinely constrained by the cases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

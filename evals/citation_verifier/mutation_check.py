#!/usr/bin/env python3
"""Mutation test — proves the case set actually constrains the verifier.

An eval a stub can ace is measuring nothing. We swap in degenerate/buggy
implementations and assert the cases reject each one.

Two mutants are REGRESSION REPLICAS of real medsci `verify_refs.py` bugs. If
either ever survives, we have reintroduced the bug we wrote this tool to avoid:

  * always_verified    -- the "silent OK" failure mode in general
  * doi_fail_passes    -- verify_refs.py L557-560: DOI lookup fails -> weak title
                          search -> any hit returns OK (a fake DOI passes)
  * no_year_check      -- verify_refs.py parses year_guess but never compares it

Runs offline from cache.json when present (verdicts are always recomputed --
a cache hit replays the raw API payload, it is never a stored pass).

    python3 mutation_check.py
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "agents", "critic", "scripts")))

import verify_citations as vc  # noqa: E402
from run_cases import run_all  # noqa: E402

# Captured before any patching: mutants that delegate must call the REAL one,
# not whatever is currently bound to vc.verify_one (that recurses forever).
REAL_VERIFY_ONE = vc.verify_one


def mut_always_verified(entry, cache):
    return {"id": entry.get("id"), "verdict": vc.VERIFIED, "notes": ["stub"]}


def mut_always_notfound(entry, cache):
    return {"id": entry.get("id"), "verdict": vc.NOT_FOUND, "notes": ["stub"]}


def mut_always_needs_human(entry, cache):
    return {"id": entry.get("id"), "verdict": vc.NEEDS_HUMAN, "notes": ["stub"]}


def mut_no_year_check(entry, cache):
    """medsci replica: parse the year, never compare it."""
    orig = vc.check_year
    vc.check_year = lambda cited, rec: (True, "stub: year not actually checked")
    try:
        return REAL_VERIFY_ONE(entry, cache)
    finally:
        vc.check_year = orig


def mut_doi_fail_passes(entry, cache):
    """medsci replica (L557-560): if the DOI does not resolve, fall back to a
    title search and accept ANY hit as a pass."""
    orig = vc.resolve_source

    def weak(e, c):
        rec, notes = orig(e, c)
        if rec is None:
            cands = vc.search_crossref(e.get("title"), e.get("first_author"), c)
            if cands:  # <-- the bug: any hit at all is good enough
                return cands[0], notes + ["stub: accepted first search hit"]
        return rec, notes

    vc.resolve_source = weak
    try:
        return REAL_VERIFY_ONE(entry, cache)
    finally:
        vc.resolve_source = orig


def mut_always_claim_unsupported(entry, cache):
    """Rubber-stamp every claim as unsupported. Must die on ctrl_claim_supported,
    proving the claim layer discriminates rather than always firing."""
    orig = vc.check_claim
    vc.check_claim = lambda claim, abstract: (vc.CLAIM_UNSUPPORTED, ["stub"])
    try:
        return REAL_VERIFY_ONE(entry, cache)
    finally:
        vc.check_claim = orig


def mut_break_pubmed_fallback(entry, cache):
    """Disable the PubMed efetch fallback. Must die on ctrl_pubmed_fallback (a
    Cell record with no CrossRef abstract), proving the fallback is real and
    load-bearing rather than dead code."""
    orig = vc.fetch_abstract_pubmed
    vc.fetch_abstract_pubmed = lambda doi, cache: ""
    try:
        return REAL_VERIFY_ONE(entry, cache)
    finally:
        vc.fetch_abstract_pubmed = orig


def mut_ignore_claims(entry, cache):
    """Drop the abstract layer -- medsci's scope (bibliography only)."""
    e = {k: v for k, v in entry.items() if k != "claims"}
    return REAL_VERIFY_ONE(e, cache)


MUTANTS = {
    "always_verified": mut_always_verified,
    "always_notfound": mut_always_notfound,
    "always_needs_human": mut_always_needs_human,
    "no_year_check": mut_no_year_check,
    "doi_fail_passes": mut_doi_fail_passes,
    "ignore_claims": mut_ignore_claims,
    "always_claim_unsupported": mut_always_claim_unsupported,
    "break_pubmed_fallback": mut_break_pubmed_fallback,
}


def main():
    baseline = run_all()
    base_ok = sum(1 for r in baseline if r["ok"])
    print(f"real verifier:  {base_ok}/{len(baseline)} cases correct")
    if base_ok != len(baseline):
        print("  baseline is not green -- fix that before trusting mutation results")

    print("\nmutant                 kills                                    status")
    print("-" * 78)
    survived = []
    real = REAL_VERIFY_ONE
    for name, fn in MUTANTS.items():
        vc.verify_one = fn
        try:
            results = run_all()
        finally:
            vc.verify_one = real
        killers = [r["id"] for r in results if not r["ok"]]
        ok = len(results) - len(killers)
        if killers:
            shown = ", ".join(killers[:3]) + ("..." if len(killers) > 3 else "")
            print(f"{name:<22} {shown:<40} killed ({ok}/{len(results)})")
        else:
            print(f"{name:<22} {'-':<40} SURVIVED <<<")
            survived.append(name)

    print()
    if survived:
        print("FAIL — case set does not constrain these mutants:")
        for s in survived:
            print(f"  {s}")
        return 1
    print("All mutants killed — every check is genuinely constrained by the cases.")
    print("Regression replicas (always_verified / doi_fail_passes / no_year_check) "
          "are dead: the medsci bugs cannot reappear unnoticed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

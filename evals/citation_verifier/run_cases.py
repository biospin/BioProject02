#!/usr/bin/env python3
"""Run the BIOP02 citation-verifier case set and check each verdict.

    python3 run_cases.py            # uses/creates cache.json
    python3 run_cases.py --refresh  # ignore cache, hit the live APIs
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "..", "agents", "critic", "scripts")
sys.path.insert(0, os.path.abspath(SCRIPTS))

import verify_citations as vc  # noqa: E402

CASES = os.path.join(HERE, "cases", "biop02_failure_set.json")
CACHE = os.path.join(HERE, "cache.json")


def load_entries():
    with open(CASES, "r", encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def run_all(cache_path=CACHE):
    entries = load_entries()
    cache = vc.Cache(cache_path)
    results = []
    for e in entries:
        r = vc.verify_one(e, cache)
        r["expected"] = e["expected"]
        # A case may list `accept` when the load-bearing guarantee is broader than
        # one exact label (e.g. fabrications: what matters is "never VERIFIED").
        accept = e.get("accept") or [e["expected"]]
        r["ok"] = r["verdict"] in accept
        results.append(r)
    cache.save()
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="ignore cache; hit live APIs")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    cache_path = None if args.refresh else CACHE
    results = run_all(cache_path)

    w = max(len(r["id"]) for r in results)
    print(f"{'case'.ljust(w)}  {'expected'.ljust(17)} {'actual'.ljust(17)} ")
    print("-" * (w + 40))
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL <<<"
        print(f"{r['id'].ljust(w)}  {r['expected'].ljust(17)} {r['verdict'].ljust(17)} {mark}")

    if args.verbose:
        for r in results:
            print(f"\n== {r['id']} -> {r['verdict']}")
            for n in r["notes"]:
                print(f"     - {n}")

    n_ok = sum(1 for r in results if r["ok"])
    print(f"\n{n_ok}/{len(results)} cases correct")

    # Hard invariants, independent of expected-value bookkeeping.
    fails = []
    by_id = {r["id"]: r for r in results}
    for cid in ("reg_fake_doi", "err1_williams_fabricated"):
        if by_id[cid]["verdict"] == vc.VERIFIED:
            fails.append(f"INVARIANT VIOLATED: {cid} was VERIFIED")
    for cid in ("ctrl_farahmand", "ctrl_koudijs", "ctrl_kaczmarzyk",
                "ctrl_claim_supported", "ctrl_pubmed_fallback"):
        if by_id[cid]["verdict"] != vc.VERIFIED:
            fails.append(f"FALSE POSITIVE: control {cid} -> {by_id[cid]['verdict']}")
    for f in fails:
        print(f"  {f}")

    return 0 if (n_ok == len(results) and not fails) else 1


if __name__ == "__main__":
    sys.exit(main())

"""Runs the 3 pilot scorers against REAL experiments/*/critic_report.json.

Read-only. Writes nothing, changes no experiment, and its verdicts are NOT
critic_status — a human reviewer owns that (Owner != Reviewer).

Why this exists: the fixtures in cases/ were authored by the same person who
wrote the scorers, so they cannot prove the scorers' *input contract* matches
reality. Only real artifacts can. This is the check that caught the fact that
baselines live in a sibling `*_baselines/trivial_baselines.json` rather than
inside metrics.json.

    /opt/envs/spatialpatho/bin/python run_real_artifacts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from scorers import SCORERS, REPO_ROOT, load_context


def main() -> int:
    reports = sorted((REPO_ROOT / "experiments").rglob("critic_report.json"))
    if not reports:
        print("no real critic_report.json found")
        return 0

    print("=" * 88)
    print("Pilot scorers vs REAL BIOP02 artifacts (read-only; NOT a critic_status)")
    print("=" * 88)
    print(f"\n{'experiment':<44} {'drp':<9} {'claim':<9} {'baseline':<9} loaded")
    print("-" * 88)

    rows = []
    for rp in reports:
        rel = rp.relative_to(REPO_ROOT).parent.as_posix().replace("experiments/", "")
        try:
            report, metrics, baselines = load_context(rp)
        except Exception as e:  # noqa: BLE001
            print(f"{rel:<44} LOAD ERROR: {type(e).__name__}: {e}")
            rows.append((rel, "error", "error", "error"))
            continue
        verdicts = {}
        for name, fn in SCORERS.items():
            try:
                verdicts[name] = fn(report, metrics, baselines).status
            except Exception as e:  # noqa: BLE001
                verdicts[name] = f"ERR:{type(e).__name__}"
        loaded = f"m={'Y' if metrics else 'N'} b={len(baselines) if baselines else 0}"
        print(f"{rel:<44} {verdicts['drp_framing']:<9} {verdicts['claim_level']:<9} "
              f"{verdicts['baseline_comparison']:<9} {loaded}")
        rows.append((rel, *verdicts.values()))

    print(f"\n{len(rows)} real reports scored, 0 crashes."
          if all("error" not in r for row in rows for r in row[1:])
          else f"\n{len(rows)} real reports scored, some errors above.")

    print("\nNOTE: these verdicts are the pilot's opinion, not an adjudication.")
    print("Known open question (braveji owns): checklist #2 requires a 'pixel_mean'")
    print("baseline. Paper A (BRCA/sjpark) has never run one — its 10 baseline runs use")
    print("{random, majority|subtype_only, mean_embed}. The scorer therefore rejects on")
    print("a missing pixel_mean rather than silently accepting mean_embed as a stand-in")
    print("(they are different: mean of UNI embeddings vs mean of raw pixels).\n"
          "CORRECTION (kkkim 2026-07-17): Paper C (cross-cancer) DID run pixel-mean --\n"
          "  experiments/crosscancer/<cancer>/full/baseline_pixelmean.json. This scorer\n"
          "  did not scan those files. See README 'range correction'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

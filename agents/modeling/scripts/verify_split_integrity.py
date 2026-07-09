"""
BIOP02-53 braveji Critic followup — split integrity assert 로그.

manifest의 split 컬럼 기준으로 patient-level(case_id) 및 site-level(TCGA TSS 코드)
disjointness를 assert로 검증하고 결과를 로그(json)로 남긴다. CLAM/MLP 학습 스크립트와
독립적으로 언제든 재실행 가능 — split_policy가 바뀔 때마다 재검증하는 용도.

Run:
    python agents/modeling/scripts/verify_split_integrity.py \
        --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
        --out experiments/sjpark/site_disjoint_verification.json
"""

import argparse
import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def tss_code(case_id: str) -> str:
    parts = case_id.split("-")
    if len(parts) >= 2 and parts[0] == "TCGA":
        return parts[1]
    return f"UNKNOWN:{case_id}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    split_sites = defaultdict(set)
    split_cases = defaultdict(set)
    n_rows = defaultdict(int)

    with open(args.manifest, newline="") as f:
        for row in csv.DictReader(f):
            split = row.get("split", "").strip()
            case_id = row.get("case_id", "").strip()
            if not split or not case_id:
                continue
            split_sites[split].add(tss_code(case_id))
            split_cases[split].add(case_id)
            n_rows[split] += 1

    splits = sorted(split_sites.keys())
    site_overlaps = {}
    case_overlaps = {}
    for a, b in combinations(splits, 2):
        key = f"{a}_{b}"
        site_overlaps[key] = sorted(split_sites[a] & split_sites[b])
        case_overlaps[key] = sorted(split_cases[a] & split_cases[b])

    all_site_clear = all(len(v) == 0 for v in site_overlaps.values())
    all_case_clear = all(len(v) == 0 for v in case_overlaps.values())

    result = {
        "manifest": args.manifest,
        "n_rows_per_split": dict(n_rows),
        "n_unique_sites_per_split": {k: len(v) for k, v in split_sites.items()},
        "site_overlap": {k: len(v) for k, v in site_overlaps.items()},
        "site_overlap_detail": {k: v for k, v in site_overlaps.items() if v},
        "case_id_overlap": {k: len(v) for k, v in case_overlaps.items()},
        "case_id_overlap_detail": {k: v for k, v in case_overlaps.items() if v},
        "site_disjoint": all_site_clear,
        "patient_disjoint": all_case_clear,
    }

    print(json.dumps(result, indent=2))

    assert all_case_clear, f"patient-level leakage 발견: {result['case_id_overlap_detail']}"
    assert all_site_clear, f"site-level leakage 발견: {result['site_overlap_detail']}"
    print("\n[ASSERT PASS] site-disjoint AND patient-disjoint 확인됨.")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

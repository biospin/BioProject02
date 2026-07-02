#!/usr/bin/env python3
"""
split_policy_v0: Patient-level stratified 70/15/15 train/val/test split.

- Stratifies on ER status (Positive vs non-Positive)
- Each case_id appears in exactly one split
- seed=42 for reproducibility

Input:  /home/kkkim/data/tcga_brca_wsi_clinical_500.csv
Output: /home/kkkim/data/split_policy_v0.csv
        /home/kkkim/data/split_stats.txt
"""

import csv
import random
import collections
import os

MANIFEST = "/home/kkkim/data/tcga_brca_wsi_clinical_500.csv"
OUT_SPLIT = "/home/kkkim/data/split_policy_v0.csv"
OUT_STATS = "/home/kkkim/data/split_stats.txt"
SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
# TEST_RATIO = 0.15 (remainder)


def load_manifest(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_patient_er(rows):
    """Return dict: case_id -> ER label (one per patient; take first occurrence)."""
    patient_er = {}
    for row in rows:
        cid = row["case_id"]
        if cid not in patient_er:
            patient_er[cid] = row["er"]
    return patient_er


def stratified_split(patient_er, train_r, val_r, seed):
    """Stratify on ER Positive vs other, then split."""
    rng = random.Random(seed)

    # Group case_ids by ER stratum
    strata = collections.defaultdict(list)
    for cid, er in patient_er.items():
        stratum = "Positive" if er == "Positive" else "NonPositive"
        strata[stratum].append(cid)

    train, val, test = [], [], []

    for stratum, cases in sorted(strata.items()):  # sorted for determinism
        shuffled = cases[:]
        rng.shuffle(shuffled)
        n = len(shuffled)
        n_train = round(n * train_r)
        n_val = round(n * val_r)
        # test gets the remainder
        train.extend(shuffled[:n_train])
        val.extend(shuffled[n_train:n_train + n_val])
        test.extend(shuffled[n_train + n_val:])

    return train, val, test


def write_split_csv(rows, split_map, out_path):
    """Write original manifest rows + 'split' column."""
    with open(out_path, "w", newline="") as f:
        fieldnames = list(rows[0].keys()) + ["split"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out_row = dict(row)
            cid = row["case_id"]
            out_row["split"] = split_map.get(cid, "UNKNOWN")
            writer.writerow(out_row)


def compute_stats(rows, split_map):
    """Compute per-split ER distribution stats."""
    # split -> er -> count
    stats = collections.defaultdict(lambda: collections.defaultdict(int))
    case_splits = collections.defaultdict(set)

    for row in rows:
        cid = row["case_id"]
        sp = split_map.get(cid, "UNKNOWN")
        er = row["er"]
        stats[sp][er] += 1
        case_splits[sp].add(cid)

    return stats, case_splits


def write_stats(rows, split_map, out_path):
    stats, case_splits = compute_stats(rows, split_map)

    # ER unique values
    all_er = sorted(set(r["er"] for r in rows))
    all_splits = ["train", "val", "test"]

    lines = []
    lines.append("=" * 60)
    lines.append("split_policy_v0 — Distribution Summary")
    lines.append("=" * 60)
    lines.append(f"Total slides in manifest : {len(rows)}")

    total_patients = len(set(r["case_id"] for r in rows))
    lines.append(f"Total unique patients    : {total_patients}")
    lines.append("")

    # Patient-level split counts
    lines.append("[ Patient counts per split ]")
    for sp in all_splits:
        n = len(case_splits[sp])
        pct = 100 * n / total_patients if total_patients else 0
        lines.append(f"  {sp:6s}: {n:4d} patients ({pct:.1f}%)")
    lines.append("")

    # Slide-level counts
    slide_per_split = collections.Counter(split_map.get(r["case_id"], "UNKNOWN") for r in rows)
    lines.append("[ Slide counts per split ]")
    for sp in all_splits:
        n = slide_per_split[sp]
        pct = 100 * n / len(rows) if rows else 0
        lines.append(f"  {sp:6s}: {n:4d} slides  ({pct:.1f}%)")
    lines.append("")

    # ER distribution per split
    lines.append("[ ER status per split (slide-level) ]")
    header = f"  {'Split':6s}  " + "  ".join(f"{er:12s}" for er in all_er) + "  Total"
    lines.append(header)
    for sp in all_splits:
        sp_total = sum(stats[sp].values())
        row_parts = [f"  {sp:6s}  "]
        for er in all_er:
            cnt = stats[sp].get(er, 0)
            pct = 100 * cnt / sp_total if sp_total else 0
            row_parts.append(f"{cnt:4d}({pct:4.1f}%)  ")
        row_parts.append(f"{sp_total:4d}")
        lines.append("".join(row_parts))
    lines.append("")

    # ER Positive ratio per split
    lines.append("[ ER Positive ratio per split ]")
    for sp in all_splits:
        sp_total = sum(stats[sp].values())
        pos = stats[sp].get("Positive", 0)
        pct = 100 * pos / sp_total if sp_total else 0
        lines.append(f"  {sp:6s}: {pos}/{sp_total} = {pct:.1f}% ER+")
    lines.append("")
    lines.append("=" * 60)

    text = "\n".join(lines)
    with open(out_path, "w") as f:
        f.write(text)
    return text


def validate(rows, split_map):
    errors = []

    # All case_ids must be assigned
    for row in rows:
        cid = row["case_id"]
        if split_map.get(cid, "UNKNOWN") == "UNKNOWN":
            errors.append(f"UNASSIGNED case_id: {cid}")

    # No case_id in more than one split
    case_to_splits = collections.defaultdict(set)
    for cid, sp in split_map.items():
        case_to_splits[cid].add(sp)
    for cid, splits in case_to_splits.items():
        if len(splits) > 1:
            errors.append(f"case_id {cid} in multiple splits: {splits}")

    return errors


def main():
    print(f"Loading manifest: {MANIFEST}")
    rows = load_manifest(MANIFEST)
    print(f"  Loaded {len(rows)} slides")

    patient_er = get_patient_er(rows)
    n_patients = len(patient_er)
    print(f"  Unique patients: {n_patients}")

    train_cases, val_cases, test_cases = stratified_split(
        patient_er, TRAIN_RATIO, VAL_RATIO, SEED
    )
    print(f"  Split (patient): train={len(train_cases)}, val={len(val_cases)}, test={len(test_cases)}")

    # Build case_id -> split map
    split_map = {}
    for cid in train_cases:
        split_map[cid] = "train"
    for cid in val_cases:
        split_map[cid] = "val"
    for cid in test_cases:
        split_map[cid] = "test"

    # Validate
    errors = validate(rows, split_map)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        raise RuntimeError("Validation failed — see errors above")
    print("  Validation: PASSED (no duplicate assignments)")

    # Write outputs
    write_split_csv(rows, split_map, OUT_SPLIT)
    print(f"  Written: {OUT_SPLIT}")

    stats_text = write_stats(rows, split_map, OUT_STATS)
    print(f"  Written: {OUT_STATS}")
    print()
    print(stats_text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build the TCGA-BRCA slide manifest by joining the NAS slide inventory with TCGA
CDR clinical labels, then assigning a deterministic patient-level split.

This regenerates the manifest that was lost with the expired GPU server
(jamie's original method: NAS file listing + TCGA CDR clinical join). Keep the
output under version control (agents/data/manifests/) so it never depends on a
single machine again.

Inputs:
  --inventory  CSV from list_nas_wsi.py (slide_id, case_id, slide_type, file_name, source_path)
  --clinical   TCGA biotab clinical_patient_brca.txt (tab-separated; bcr_patient_barcode key)

Output manifest columns:
  case_id, slide_id, slide_type, file_name, source_path,
  er_status, pr_status, her2_status, pam50, split, has_labels

Example:
  python agents/data/scripts/build_manifest.py \
      --inventory agents/data/manifests/tcga_brca_nas_inventory.csv \
      --clinical  /path/to/clinical_patient_brca.txt \
      --out       agents/data/manifests/tcga_brca_manifest.csv \
      --slide-types DX
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

# TCGA biotab column names -> manifest column
CLINICAL_COLS = {
    "er_status_by_ihc": "er_status",
    "pr_status_by_ihc": "pr_status",
    "her2_status_by_ihc": "her2_status",
}
# values that mean "no usable label"
MISSING = {"", "[not available]", "[not applicable]", "[unknown]", "[discrepancy]",
           "indeterminate", "equivocal", "not performed", "na"}


def read_clinical(path: Path) -> dict[str, dict[str, str]]:
    """Parse TCGA biotab clinical file. The file has multiple header/description
    rows; we locate the header containing bcr_patient_barcode and keep only data
    rows whose barcode matches the TCGA patient pattern."""
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as fh:
        reader = csv.reader(fh, delimiter="\t")
        rows = list(reader)
    header_idx = None
    for i, row in enumerate(rows):
        if "bcr_patient_barcode" in [c.strip().lower() for c in row]:
            header_idx = i
            break
    if header_idx is None:
        raise SystemExit(f"bcr_patient_barcode column not found in {path}")
    header = [c.strip().lower() for c in rows[header_idx]]
    bidx = header.index("bcr_patient_barcode")
    col_idx = {src: header.index(src) for src in CLINICAL_COLS if src in header}

    out: dict[str, dict[str, str]] = {}
    for row in rows[header_idx + 1:]:
        if len(row) <= bidx:
            continue
        barcode = row[bidx].strip()
        # data rows only: TCGA-XX-XXXX
        parts = barcode.split("-")
        if len(parts) != 3 or parts[0] != "TCGA":
            continue
        rec = {dst: "" for dst in CLINICAL_COLS.values()}
        for src, dst in CLINICAL_COLS.items():
            if src in col_idx and col_idx[src] < len(row):
                rec[dst] = row[col_idx[src]].strip()
        out[barcode] = rec
    return out


def is_label(value: str) -> bool:
    return value.strip().lower() not in MISSING


def split_for(case_id: str, seed: int, ratios: tuple[float, float, float]) -> str:
    h = int(hashlib.sha256(f"{seed}:{case_id}".encode()).hexdigest(), 16)
    x = (h % 1_000_000) / 1_000_000
    if x < ratios[0]:
        return "train"
    if x < ratios[0] + ratios[1]:
        return "val"
    return "test"


def main() -> None:
    ap = argparse.ArgumentParser(description="Join NAS inventory + TCGA CDR clinical into a manifest")
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--clinical", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slide-types", default="DX",
                    help="comma list of slide types to keep (e.g. DX or DX,TS); 'all' keeps everything")
    ap.add_argument("--split-seed", type=int, default=42)
    ap.add_argument("--split-ratio", default="0.7,0.15,0.15", help="train,val,test")
    ap.add_argument("--require-labels", action="store_true",
                    help="drop slides whose patient has no usable ER/PR/HER2 label")
    args = ap.parse_args()

    keep_types = None if args.slide_types.lower() == "all" else set(
        t.strip().upper() for t in args.slide_types.split(",") if t.strip()
    )
    ratios = tuple(float(x) for x in args.split_ratio.split(","))
    if len(ratios) != 3 or abs(sum(ratios) - 1.0) > 1e-6:
        raise SystemExit("--split-ratio must be three numbers summing to 1.0")

    clinical = read_clinical(Path(args.clinical))

    with Path(args.inventory).open(newline="", encoding="utf-8") as fh:
        inv = list(csv.DictReader(fh))

    out_rows = []
    n_filtered_type = n_no_clinical = 0
    for r in inv:
        if keep_types is not None and r["slide_type"].upper() not in keep_types:
            n_filtered_type += 1
            continue
        labels = clinical.get(r["case_id"])
        if labels is None:
            n_no_clinical += 1
            labels = {dst: "" for dst in CLINICAL_COLS.values()}
        has_labels = int(any(is_label(labels[c]) for c in ("er_status", "pr_status", "her2_status")))
        if args.require_labels and not has_labels:
            continue
        out_rows.append({
            "case_id": r["case_id"],
            "slide_id": r["slide_id"],
            "slide_type": r["slide_type"],
            "file_name": r["file_name"],
            "source_path": r["source_path"],
            "er_status": labels["er_status"],
            "pr_status": labels["pr_status"],
            "her2_status": labels["her2_status"],
            "pam50": "",  # not in biotab clinical_patient; fill from a separate PAM50 source later
            "split": split_for(r["case_id"], args.split_seed, ratios),
            "has_labels": has_labels,
        })

    out_rows.sort(key=lambda x: x["slide_id"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["case_id", "slide_id", "slide_type", "file_name", "source_path",
              "er_status", "pr_status", "her2_status", "pam50", "split", "has_labels"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    patients = {r["case_id"] for r in out_rows}
    by_split: dict[str, int] = {}
    for r in out_rows:
        by_split[r["split"]] = by_split.get(r["split"], 0) + 1
    labeled = sum(r["has_labels"] for r in out_rows)
    print(f"Wrote {out}")
    print(f"slides={len(out_rows)} patients={len(patients)} labeled_slides={labeled}")
    print(f"split={by_split} filtered_by_type={n_filtered_type} slides_without_clinical={n_no_clinical}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build the TCGA-BRCA slide manifest by joining the NAS slide inventory with TCGA
CDR clinical labels, then assigning a SITE-DISJOINT, patient-level split.

This regenerates the manifest that was lost with the expired GPU server, and
implements split_policy_v0 (agents/data/split_policy_v0.md): the split unit is
the patient (case_id), and no TCGA submitting site (tss_code) — hence no patient —
is ever shared across train/val/test (Howard 2021 site-confound; Bussola
patient-level). Keep the output + split_manifest_meta.json under version control.

Inputs:
  --inventory  CSV from list_nas_wsi.py (slide_id, case_id, slide_type, file_name, source_path)
  --clinical   TCGA biotab clinical_patient_brca.txt (tab-separated; bcr_patient_barcode key)
  --pam50      (optional) CSV mapping case_id->pam50 (cBioPortal TCGA-BRCA PAM50; Parker 2009 classifier)

Output manifest columns:
  case_id, slide_id, slide_type, file_name, source_path, tss_code,
  er_status, pr_status, her2_status, pam50,
  has_er, has_pr, has_her2, has_pam50, split, has_labels

Example:
  python agents/data/scripts/build_manifest.py \
      --inventory agents/data/manifests/tcga_brca_nas_inventory.csv \
      --clinical  /path/to/clinical_patient_brca.txt \
      --pam50     /path/to/cbioportal_pam50.csv \
      --out       agents/data/manifests/tcga_brca_manifest.csv \
      --slide-types DX
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
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
# PAM50 values that are present but not a usable phenotype target (policy §4)
PAM50_MISSING = MISSING | {"normal", "normal-like", "normallike"}


def read_clinical(path: Path) -> dict[str, dict[str, str]]:
    """Parse TCGA biotab clinical file. The file has multiple header/description
    rows; we locate the header containing bcr_patient_barcode and keep only data
    rows whose barcode matches the TCGA patient pattern."""
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
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
        parts = barcode.split("-")
        if len(parts) != 3 or parts[0] != "TCGA":  # data rows only: TCGA-XX-XXXX
            continue
        rec = {dst: "" for dst in CLINICAL_COLS.values()}
        for src, dst in CLINICAL_COLS.items():
            if src in col_idx and col_idx[src] < len(row):
                rec[dst] = row[col_idx[src]].strip()
        out[barcode] = rec
    return out


def read_pam50(path: Path) -> dict[str, str]:
    """Optional case_id->PAM50 map (cBioPortal). Accepts case_id|bcr_patient_barcode
    and pam50|subtype columns."""
    m: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as fh:
        for row in csv.DictReader(fh):
            low = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            cid = low.get("case_id") or low.get("bcr_patient_barcode") or ""
            val = low.get("pam50") or low.get("subtype") or low.get("pam50_subtype") or ""
            if cid:
                m["-".join(cid.split("-")[:3])] = val
    return m


def is_label(value: str) -> bool:
    return value.strip().lower() not in MISSING


def tss_code(case_id: str) -> str:
    """TCGA submitting site = 2nd barcode token (TCGA-<TSS>-<participant>)."""
    parts = case_id.split("-")
    return parts[1] if len(parts) >= 2 else "NA"


def assign_site_disjoint_splits(rows: list[dict], ratios: tuple[float, float, float],
                                seed: int) -> dict[str, str]:
    """train/val/test assignment in which NO submitting site (and hence no patient)
    spans folds. v0 = deterministic greedy bin-packing of whole sites by patient
    count (PreservedSiteCV QP is the preferred upgrade; split_policy_v0.md §8.2).
    Returns {case_id: fold}."""
    site_cases: dict[str, set] = defaultdict(set)
    for r in rows:
        site_cases[tss_code(r["case_id"])].add(r["case_id"])
    sites = [(s, len(c)) for s, c in site_cases.items()]
    total = sum(n for _, n in sites) or 1
    target = {"train": ratios[0] * total, "val": ratios[1] * total, "test": ratios[2] * total}
    # deterministic order: large sites first, hash tie-break (no RNG → resume-safe)
    sites.sort(key=lambda x: (-x[1], hashlib.sha256(f"{seed}:{x[0]}".encode()).hexdigest()))
    assigned = {"train": 0.0, "val": 0.0, "test": 0.0}
    site_fold: dict[str, str] = {}
    for s, n in sites:
        fold = max(("train", "val", "test"), key=lambda f: target[f] - assigned[f])
        site_fold[s] = fold
        assigned[fold] += n
    return {r["case_id"]: site_fold[tss_code(r["case_id"])] for r in rows}


def assert_no_cross_fold(rows: list[dict]) -> None:
    """Leakage gate (binds Critic #1): no site and no patient may span >1 fold."""
    site_folds: dict[str, set] = defaultdict(set)
    case_folds: dict[str, set] = defaultdict(set)
    for r in rows:
        site_folds[r["tss_code"]].add(r["split"])
        case_folds[r["case_id"]].add(r["split"])
    bad_site = [k for k, v in site_folds.items() if len(v) > 1]
    bad_case = [k for k, v in case_folds.items() if len(v) > 1]
    if bad_site:
        raise SystemExit(f"LEAKAGE: site(s) span >1 fold: {bad_site[:5]}")
    if bad_case:
        raise SystemExit(f"LEAKAGE: case(s) span >1 fold: {bad_case[:5]}")


def split_hash(rows: list[dict]) -> str:
    items = sorted((r["case_id"], r["split"]) for r in rows)
    return hashlib.sha256(repr(items).encode()).hexdigest()[:16]


def write_split_meta(rows: list[dict], path: Path, ratios, seed: int) -> dict:
    n = len(rows) or 1
    by_split = Counter(r["split"] for r in rows)
    patients_by_split: dict[str, set] = defaultdict(set)
    sites_by_split: dict[str, set] = defaultdict(set)
    for r in rows:
        patients_by_split[r["split"]].add(r["case_id"])
        sites_by_split[r["split"]].add(r["tss_code"])
    er_balance = {}
    for f in ("train", "val", "test"):
        fr = [r for r in rows if r["split"] == f]
        er_balance[f] = {
            "er_pos": sum(1 for r in fr if r["er_status"].strip().lower() == "positive"),
            "er_neg": sum(1 for r in fr if r["er_status"].strip().lower() == "negative"),
        }
    meta = {
        "policy": "split_policy_v0",
        "split_hash": split_hash(rows),
        "seed": seed,
        "target_ratios": {"train": ratios[0], "val": ratios[1], "test": ratios[2]},
        "achieved_slide_fractions": {k: round(v / n, 4) for k, v in sorted(by_split.items())},
        "patients_per_split": {k: len(v) for k, v in sorted(patients_by_split.items())},
        "sites_per_split": {k: len(v) for k, v in sorted(sites_by_split.items())},
        "er_balance_per_split": er_balance,
        "n_slides": len(rows),
        "n_patients": len({r["case_id"] for r in rows}),
        "n_sites": len({r["tss_code"] for r in rows}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description="Join NAS inventory + TCGA CDR clinical into a site-disjoint manifest")
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--clinical", required=True)
    ap.add_argument("--pam50", help="optional CSV: case_id,pam50 (cBioPortal TCGA-BRCA)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--split-meta", help="split_manifest_meta.json path (default: alongside --out)")
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
    pam50_map = read_pam50(Path(args.pam50)) if args.pam50 else {}

    with Path(args.inventory).open(newline="", encoding="utf-8") as fh:
        inv = list(csv.DictReader(fh))

    out_rows: list[dict] = []
    n_filtered_type = n_no_clinical = 0
    for r in inv:
        if keep_types is not None and r["slide_type"].upper() not in keep_types:
            n_filtered_type += 1
            continue
        labels = clinical.get(r["case_id"])
        if labels is None:
            n_no_clinical += 1
            labels = {dst: "" for dst in CLINICAL_COLS.values()}
        pam50 = pam50_map.get(r["case_id"], "")
        has_er = int(is_label(labels["er_status"]))
        has_pr = int(is_label(labels["pr_status"]))
        has_her2 = int(is_label(labels["her2_status"]))
        has_pam50 = int(pam50.strip().lower() not in PAM50_MISSING)
        has_labels = int(has_er or has_pr or has_her2)
        if args.require_labels and not has_labels:
            continue
        out_rows.append({
            "case_id": r["case_id"],
            "slide_id": r["slide_id"],
            "slide_type": r["slide_type"],
            "file_name": r["file_name"],
            "source_path": r["source_path"],
            "tss_code": tss_code(r["case_id"]),
            "er_status": labels["er_status"],
            "pr_status": labels["pr_status"],
            "her2_status": labels["her2_status"],
            "pam50": pam50,
            "has_er": has_er,
            "has_pr": has_pr,
            "has_her2": has_her2,
            "has_pam50": has_pam50,
            "has_labels": has_labels,
        })

    # site-disjoint, patient-level split (two-pass: all rows known before assigning)
    case_to_fold = assign_site_disjoint_splits(out_rows, ratios, args.split_seed)
    for r in out_rows:
        r["split"] = case_to_fold[r["case_id"]]
    assert_no_cross_fold(out_rows)  # Critic #1 leakage gate

    out_rows.sort(key=lambda x: x["slide_id"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["case_id", "slide_id", "slide_type", "file_name", "source_path", "tss_code",
              "er_status", "pr_status", "her2_status", "pam50",
              "has_er", "has_pr", "has_her2", "has_pam50", "split", "has_labels"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    meta_path = Path(args.split_meta) if args.split_meta else out.parent / "split_manifest_meta.json"
    meta = write_split_meta(out_rows, meta_path, ratios, args.split_seed)

    labeled = sum(r["has_labels"] for r in out_rows)
    print(f"Wrote {out}")
    print(f"slides={len(out_rows)} patients={meta['n_patients']} sites={meta['n_sites']} labeled_slides={labeled}")
    print(f"split(slides)={dict(Counter(r['split'] for r in out_rows))} "
          f"patients_per_split={meta['patients_per_split']} sites_per_split={meta['sites_per_split']}")
    print(f"has(er/pr/her2/pam50)="
          f"{sum(r['has_er'] for r in out_rows)}/{sum(r['has_pr'] for r in out_rows)}/"
          f"{sum(r['has_her2'] for r in out_rows)}/{sum(r['has_pam50'] for r in out_rows)}")
    print(f"split_hash={meta['split_hash']} filtered_by_type={n_filtered_type} "
          f"slides_without_clinical={n_no_clinical}")
    print(f"Wrote {meta_path}")


if __name__ == "__main__":
    main()

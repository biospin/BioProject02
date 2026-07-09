#!/usr/bin/env python3
"""
Build the authoritative CPTAC-BRCA clinical label table (BIOP02-55): map ER/PR/
HER2/PAM50 onto the CPTAC-BRCA external-test cohort and verify it does not
collide, at the patient level, with the locked TCGA-BRCA split_policy_v0
cohort (agents/data/split_policy_v0.md).

This supersedes the provisional label file kkkim produced on 2026-07-03 under
time pressure (experiments/kkkim/20260703_cptac_labels/, see
DECISION_rule_adjustment.md) while this Data Agent deliverable was late. Same
public source, same join-key fix; this version additionally (a) applies the
official label-missingness policy from split_policy_v0.md SS4 instead of
blanking equivocal/normal-like values outright, (b) anchors on the full IDC
imaging cohort (agents/data/manifests/cptac_brca_idc_inventory.csv, 198
patients) rather than only the 122-patient cBioPortal cohort, and (c) verifies
zero patient-id collision against the locked 1010-patient TCGA manifest.

Source: cBioPortal study `brca_cptac_2020` (Krug et al., Cell 2020,
Proteogenomic landscape of breast cancer; PMID 33212010), 122 samples.

Output columns:
  case_id, cbioportal_patient_id, join_key_resolved, has_imaging,
  er_status, pr_status, her2_status, pam50,
  has_er, has_pr, has_her2, has_pam50, has_labels, source

Example:
  python agents/data/scripts/build_cptac_labels.py \
      --idc-inventory agents/data/manifests/cptac_brca_idc_inventory.csv \
      --tcga-manifest agents/data/manifests/tcga_brca_manifest.csv \
      --out agents/data/manifests/cptac_brca_clinical_labels_v1.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CBIOPORTAL_API_BASE = "https://www.cbioportal.org/api"
STUDY_ID = "brca_cptac_2020"
SOURCE_LABEL = "cBioPortal brca_cptac_2020 (Krug 2020 Cell)"

# Same missing-value policy as build_manifest.py / split_policy_v0.md SS4, so
# TCGA and CPTAC has_* flags mean exactly the same thing downstream.
MISSING = {"", "[not available]", "[not applicable]", "[unknown]", "[discrepancy]",
           "indeterminate", "equivocal", "not performed", "na"}
PAM50_MISSING = MISSING | {"normal", "normal-like", "normallike"}

# PAM50 and TUMOR_STAGE are sample-level cBioPortal attributes (1 sample/patient
# in this cohort); everything else is patient-level.
PATIENT_FIELDS = {
    "ER_UPDATED_CLINICAL_STATUS": "er_status",
    "PR_CLINICAL_STATUS": "pr_status",
    "ERBB2_UPDATED_CLINICAL_STATUS": "her2_status",
}
SAMPLE_FIELDS = {"PAM50": "pam50"}
STATUS_FIELDS = {"er_status", "pr_status", "her2_status"}
# cBioPortal's CPTAC study emits "Her2" for the HER2-enriched PAM50 class; the
# TCGA-side PAM50 source (split_policy_v0.md SS10) emits "HER2". Normalize so
# both cohorts use the same class label (kkkim's DECISION_rule_adjustment.md
# applied the same fix).
PAM50_ALIASES = {"her2": "HER2"}


def is_label(value: str) -> bool:
    return value.strip().lower() not in MISSING


def fetch_json(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def load_clinical(clinical_type: str, cache: Path, refresh: bool) -> list[dict]:
    if cache.exists() and not refresh:
        return json.loads(cache.read_text())
    url = f"{CBIOPORTAL_API_BASE}/studies/{STUDY_ID}/clinical-data?clinicalDataType={clinical_type}&projection=SUMMARY"
    data = fetch_json(url)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data))
    return data


def normalize_case_id(cbioportal_patient_id: str) -> tuple[str, bool]:
    """cBioPortal prefixes numeric-leading patient IDs with 'X' (e.g. X01BR001);
    the case_id join key used elsewhere in this repo (IDC inventory, TCGA
    manifest style) does not have that prefix. Returns (case_id, resolved)."""
    match = re.match(r"^X(\d.*)$", cbioportal_patient_id)
    if match:
        return match.group(1), True
    return cbioportal_patient_id, False


def normalize_status(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().capitalize()


def normalize_pam50(value: str | None) -> str:
    if not value:
        return ""
    return PAM50_ALIASES.get(value.strip().lower(), value.strip())


def pivot(rows: list[dict], fields: dict[str, str]) -> dict[str, dict[str, str]]:
    wide: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        key = fields.get(row["clinicalAttributeId"])
        if key:
            wide[row["patientId"]][key] = row["value"]
    return wide


def read_idc_case_ids(path: Path) -> set[str]:
    with path.open(newline="") as f:
        return {r["case_id"] for r in csv.DictReader(f)}


def read_tcga_case_ids(path: Path) -> set[str]:
    with path.open(newline="") as f:
        return {r["case_id"] for r in csv.DictReader(f)}


def build_rows(
    idc_case_ids: set[str], patient_wide: dict[str, dict[str, str]], sample_wide: dict[str, dict[str, str]]
) -> tuple[list[dict[str, str]], list[str]]:
    cbio_ids = sorted(set(patient_wide) | set(sample_wide))

    by_case_id: dict[str, tuple[str, bool, dict[str, str]]] = {}
    unresolved_join: list[str] = []
    for cbio_id in cbio_ids:
        case_id, resolved = normalize_case_id(cbio_id)
        merged = {**patient_wide.get(cbio_id, {}), **sample_wide.get(cbio_id, {})}
        by_case_id[case_id] = (cbio_id, resolved, merged)
        if not resolved:
            unresolved_join.append(cbio_id)

    all_case_ids = sorted(idc_case_ids | set(by_case_id))
    rows: list[dict[str, str]] = []
    for case_id in all_case_ids:
        has_imaging = case_id in idc_case_ids
        cbio_id, resolved, merged = by_case_id.get(case_id, (None, None, {}))

        er_status = normalize_status(merged.get("er_status"))
        pr_status = normalize_status(merged.get("pr_status"))
        her2_status = normalize_status(merged.get("her2_status"))
        pam50 = normalize_pam50(merged.get("pam50"))

        has_er = int(is_label(er_status))
        has_pr = int(is_label(pr_status))
        has_her2 = int(is_label(her2_status))
        has_pam50 = int(pam50.strip().lower() not in PAM50_MISSING)
        has_labels = int(bool(has_er or has_pr or has_her2 or has_pam50))

        rows.append({
            "case_id": case_id,
            "cbioportal_patient_id": cbio_id or "",
            "join_key_resolved": "yes" if resolved else ("no" if resolved is False else ""),
            "has_imaging": "yes" if has_imaging else "no",
            "er_status": er_status,
            "pr_status": pr_status,
            "her2_status": her2_status,
            "pam50": pam50,
            "has_er": has_er,
            "has_pr": has_pr,
            "has_her2": has_her2,
            "has_pam50": has_pam50,
            "has_labels": has_labels,
            "source": SOURCE_LABEL if cbio_id else "",
        })
    return rows, unresolved_join


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["case_id", "cbioportal_patient_id", "join_key_resolved", "has_imaging",
              "er_status", "pr_status", "her2_status", "pam50",
              "has_er", "has_pr", "has_her2", "has_pam50", "has_labels", "source"]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idc-inventory", type=Path,
                    default=ROOT / "agents" / "data" / "manifests" / "cptac_brca_idc_inventory.csv")
    ap.add_argument("--tcga-manifest", type=Path,
                    default=ROOT / "agents" / "data" / "manifests" / "tcga_brca_manifest.csv")
    ap.add_argument("--out", type=Path,
                    default=ROOT / "agents" / "data" / "manifests" / "cptac_brca_clinical_labels_v1.csv")
    ap.add_argument("--patient-cache", type=Path,
                    default=ROOT / "agents" / "data" / "manifests" / "cptac_brca_clinical_raw_patient.json")
    ap.add_argument("--sample-cache", type=Path,
                    default=ROOT / "agents" / "data" / "manifests" / "cptac_brca_clinical_raw_sample.json")
    ap.add_argument("--refresh", action="store_true", help="re-fetch from cBioPortal instead of using the cache")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    idc_case_ids = read_idc_case_ids(args.idc_inventory)
    tcga_case_ids = read_tcga_case_ids(args.tcga_manifest)

    patient_rows = load_clinical("PATIENT", args.patient_cache, args.refresh)
    sample_rows = load_clinical("SAMPLE", args.sample_cache, args.refresh)
    patient_wide = pivot(patient_rows, PATIENT_FIELDS)
    sample_wide = pivot(sample_rows, SAMPLE_FIELDS)

    rows, unresolved_join = build_rows(idc_case_ids, patient_wide, sample_wide)
    write_csv(args.out, rows)

    overlap = tcga_case_ids & idc_case_ids
    n_imaging = sum(1 for r in rows if r["has_imaging"] == "yes")
    n_labeled = sum(1 for r in rows if r["has_imaging"] == "yes" and r["has_labels"])

    print(f"Wrote {args.out}")
    print(f"rows={len(rows)} idc_imaging_patients={len(idc_case_ids)} "
          f"labeled_and_imaged={n_labeled} unresolved_join_keys={len(unresolved_join)}")
    print(f"has(er/pr/her2/pam50) among imaged patients="
          f"{sum(r['has_er'] for r in rows if r['has_imaging']=='yes')}/"
          f"{sum(r['has_pr'] for r in rows if r['has_imaging']=='yes')}/"
          f"{sum(r['has_her2'] for r in rows if r['has_imaging']=='yes')}/"
          f"{sum(r['has_pam50'] for r in rows if r['has_imaging']=='yes')}")
    print(f"CPTAC-vs-TCGA case_id collisions (must be 0): {len(overlap)}")
    if overlap:
        print(f"WARNING: leakage — colliding case_ids: {sorted(overlap)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

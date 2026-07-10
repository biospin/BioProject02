#!/usr/bin/env python3
"""
List CPTAC-BRCA Slide Microscopy (H&E WSI) series from NCI Imaging Data Commons
(IDC) and write a committed slide inventory CSV.

CPTAC-BRCA is the external hold-out test cohort (split_policy_v0.md). Unlike the
TCGA raw slides (Synology NAS, .svs), CPTAC-BRCA in IDC is stored as **DICOM-WSI**
in public GCS/AWS buckets, addressable by SeriesInstanceUID and downloadable with
no auth via idc-index (s5cmd under the hood). This is the IDC counterpart of
list_nas_wsi.py — it turns the IDC index into a reproducible, committed inventory.

Output CSV columns (consumed by stream_download_embed_idc.py):
    slide_id, case_id, series_uid, series_description, series_size_mb, source_path
  - case_id     = IDC PatientID (e.g. 01BR001)
  - slide_id    = <PatientID>_<NN>  (stable per-patient index, sorted by series_uid)
  - source_path = SeriesInstanceUID (the IDC download handle)
  - file_name   = slide_id (a DICOM series is a folder of .dcm, not one file)

Prereq:  pip install idc-index   (downloads a ~hundreds-MB parquet index on first use)

Example:
    python agents/data/scripts/list_idc_cptac.py \
        --out agents/data/manifests/cptac_brca_idc_inventory.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

# CPTAC-BRCA collection id as it appears in the IDC index (lowercase).
COLLECTION = "cptac_brca"


def query_sm_series(collection: str):
    """Return CPTAC SM (Slide Microscopy) series as a list of dict rows."""
    from idc_index import IDCClient

    client = IDCClient.client()
    sql = f"""
        SELECT collection_id, PatientID, SeriesInstanceUID,
               SeriesDescription, series_size_MB
        FROM index
        WHERE collection_id = '{collection}' AND Modality = 'SM'
        ORDER BY PatientID, SeriesInstanceUID
    """
    df = client.sql_query(sql)
    return df.to_dict("records")


def build_rows(records: list[dict]) -> list[dict]:
    rows: list[dict] = []
    per_patient: dict[str, int] = {}
    for r in records:
        case_id = str(r["PatientID"]).strip()
        per_patient[case_id] = per_patient.get(case_id, 0) + 1
        slide_id = f"{case_id}_{per_patient[case_id]:02d}"
        rows.append({
            "slide_id": slide_id,
            "case_id": case_id,
            "series_uid": str(r["SeriesInstanceUID"]).strip(),
            "series_description": str(r.get("SeriesDescription", "")).strip(),
            "series_size_mb": f"{float(r['series_size_MB']):.1f}",
            # source_path == the IDC handle; stream_download_embed_idc.py downloads
            # the DICOM series by this SeriesInstanceUID.
            "source_path": str(r["SeriesInstanceUID"]).strip(),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="List CPTAC-BRCA IDC SM series into an inventory CSV")
    ap.add_argument("--out", required=True, help="Output inventory CSV path")
    ap.add_argument("--collection", default=COLLECTION, help="IDC collection_id (default: cptac_brca)")
    args = ap.parse_args()

    records = query_sm_series(args.collection)
    rows = build_rows(records)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["slide_id", "case_id", "series_uid", "series_description",
              "series_size_mb", "source_path"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    patients = len({r["case_id"] for r in rows})
    total_gb = sum(float(r["series_size_mb"]) for r in rows) / 1024
    print(f"Wrote {out}")
    print(f"slides={len(rows)} patients={patients} total~{total_gb:.1f}GB")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
List WSI files from the BIOP02 Synology NAS share and write a slide inventory CSV.

The NAS shared link is the only surviving permanent source of the TCGA-BRCA raw
slides after the GPU server expired (see agents/data/README.md). This script
turns that share into a committed, reproducible inventory so the slide list is
never trapped on a single machine again.

Source share (see guide/runbooks/download_wsi_from_synology_nas.md):
    https://gofile.me/7uPdW/I1KGZnZWx
    -> radisen-nas2 QuickConnect, sharing_id=I1KGZnZWx, folder /wsi

Output CSV columns: slide_id, case_id, slide_type, file_name, source_path

Example:
    python agents/data/scripts/list_nas_wsi.py \
        --out agents/data/manifests/tcga_brca_nas_inventory.csv

Note: runs against the live NAS over QuickConnect relay (can be slow). Designed
to be run from the data/compute environment, not necessarily a laptop.
"""
from __future__ import annotations

import argparse
import csv
import http.cookiejar
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi"
DEFAULT_SHARING_ID = "I1KGZnZWx"
DEFAULT_FOLDER = "/wsi"

# TCGA slide barcode, e.g. TCGA-3C-AALI-01Z-00-DX1
SLIDE_RE = re.compile(r"^(TCGA-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-([A-Z]+)\d*)")


def _make_opener() -> urllib.request.OpenerDirector:
    cj = http.cookiejar.CookieJar()
    ctx = ssl.create_default_context()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx),
    )


def _get_json(opener, url: str, data: bytes | None = None, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, data=data)
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def login(opener, sharing_id: str, password: str = "") -> None:
    url = f"{BASE}/SYNO.Core.Sharing.Login"
    data = urllib.parse.urlencode(
        {
            "api": "SYNO.Core.Sharing.Login",
            "version": "1",
            "method": "login",
            "sharing_id": f'"{sharing_id}"',
            "password": f'"{password}"',
        }
    ).encode()
    res = _get_json(opener, url, data=data)
    if not res.get("success"):
        raise SystemExit(f"NAS login failed for sharing_id={sharing_id}: {res.get('error')}")


def list_folder(opener, sharing_id: str, folder: str, limit: int = 100):
    offset = 0
    while True:
        params = urllib.parse.urlencode(
            {
                "api": "SYNO.FolderSharing.List",
                "version": "2",
                "method": "list",
                "_sharing_id": f'"{sharing_id}"',
                "offset": str(offset),
                "limit": str(limit),
                "sort_by": "name",
                "sort_direction": "asc",
                "folder_path": f'"{folder}"',
            }
        )
        res = _get_json(opener, f"{BASE}?{params}")
        if not res.get("success"):
            raise SystemExit(f"List failed at offset={offset}: {res.get('error')}")
        files = res.get("data", {}).get("files", [])
        if not files:
            break
        for f in files:
            yield f
        if len(files) < limit:
            break
        offset += limit


def parse_slide(name: str) -> dict | None:
    m = SLIDE_RE.match(name)
    if not m:
        return None
    slide_id, slide_type = m.group(1), m.group(2)
    case_id = "-".join(slide_id.split("-")[:3])  # TCGA-XX-XXXX
    return {"slide_id": slide_id, "case_id": case_id, "slide_type": slide_type}


def main() -> None:
    ap = argparse.ArgumentParser(description="List NAS WSI share into a slide inventory CSV")
    ap.add_argument("--out", required=True, help="Output inventory CSV path")
    ap.add_argument("--sharing-id", default=DEFAULT_SHARING_ID)
    ap.add_argument("--folder", default=DEFAULT_FOLDER)
    ap.add_argument("--password", default="")
    args = ap.parse_args()

    opener = _make_opener()
    login(opener, args.sharing_id, args.password)

    rows, skipped = [], 0
    for f in list_folder(opener, args.sharing_id, args.folder):
        if f.get("isdir"):
            continue
        name = f.get("name", "")
        if not name.endswith(".svs"):
            continue
        parsed = parse_slide(name)
        if parsed is None:
            skipped += 1
            print(f"WARN: unparseable slide name skipped: {name}", file=sys.stderr)
            continue
        parsed["file_name"] = name
        parsed["source_path"] = f.get("path", f"{args.folder}/{name}")
        rows.append(parsed)

    rows.sort(key=lambda r: r["slide_id"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["slide_id", "case_id", "slide_type", "file_name", "source_path"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    patients = len({r["case_id"] for r in rows})
    by_type: dict[str, int] = {}
    for r in rows:
        by_type[r["slide_type"]] = by_type.get(r["slide_type"], 0) + 1
    print(f"Wrote {out}")
    print(f"slides={len(rows)} patients={patients} by_type={by_type} skipped={skipped}")


if __name__ == "__main__":
    main()

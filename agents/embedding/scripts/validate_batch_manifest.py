"""
Validate a TCGA-BRCA WSI batch manifest before tiling/embedding jobs.

The batch runner only requires slide_path, but this preflight check helps catch
missing paths, duplicated slide identifiers, and rough runtime/storage needs
before reserving a GPU slot.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {"slide_path"}
RECOMMENDED_COLUMNS = {"slide_id", "case_id", "file_id"}
WSI_SUFFIXES = {".svs", ".tif", ".tiff", ".ndpi", ".mrxs"}
DEFAULT_TILES_PER_SLIDE = 5000
DEFAULT_EMBEDDING_DIM = 1024
DEFAULT_SECONDS_PER_SLIDE = 131.2  # pilot: 5.6 s tiling + 125.6 s UNI
FLOAT32_BYTES = 4


def clean_id(value: str) -> str:
    keep = []
    for ch in value.strip():
        keep.append(ch if ch.isalnum() or ch in {"-", "_", "."} else "_")
    cleaned = "".join(keep).strip("_")
    return cleaned or "unknown_slide"


def slide_id_for(row: dict[str, str]) -> str:
    explicit = (row.get("slide_id") or "").strip()
    if explicit:
        return clean_id(explicit)
    return clean_id(Path((row.get("slide_path") or "").strip()).stem)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Manifest has no header: {path}")
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]
    return list(reader.fieldnames), rows


def validate(args: argparse.Namespace) -> dict[str, Any]:
    fields, rows = read_rows(Path(args.manifest))
    field_set = set(fields)
    errors: list[str] = []
    warnings: list[str] = []

    missing_required = sorted(REQUIRED_COLUMNS - field_set)
    if missing_required:
        errors.append(f"missing required columns: {missing_required}")

    missing_recommended = sorted(RECOMMENDED_COLUMNS - field_set)
    if missing_recommended:
        warnings.append(f"missing recommended columns: {missing_recommended}")

    seen_ids: dict[str, int] = {}
    seen_paths: dict[str, int] = {}
    suffix_counts: dict[str, int] = {}
    missing_paths: list[str] = []

    for line_no, row in enumerate(rows, start=2):
        slide_path = (row.get("slide_path") or "").strip()
        if not slide_path:
            errors.append(f"line {line_no}: empty slide_path")
            continue

        sid = slide_id_for(row)
        if sid in seen_ids:
            errors.append(f"line {line_no}: duplicate slide_id {sid!r} first seen at line {seen_ids[sid]}")
        else:
            seen_ids[sid] = line_no

        if slide_path in seen_paths:
            errors.append(f"line {line_no}: duplicate slide_path first seen at line {seen_paths[slide_path]}")
        else:
            seen_paths[slide_path] = line_no

        suffix = Path(slide_path).suffix.lower()
        suffix_counts[suffix or "<none>"] = suffix_counts.get(suffix or "<none>", 0) + 1
        if suffix and suffix not in WSI_SUFFIXES:
            warnings.append(f"line {line_no}: unusual WSI suffix {suffix!r}: {slide_path}")

        if args.check_exists and not Path(slide_path).exists():
            missing_paths.append(slide_path)

    if missing_paths:
        sample = ", ".join(missing_paths[:5])
        more = "" if len(missing_paths) <= 5 else f" (+{len(missing_paths) - 5} more)"
        errors.append(f"missing slide files: {sample}{more}")

    n_slides = len(rows)
    embedding_bytes = n_slides * args.tiles_per_slide * args.embedding_dim * FLOAT32_BYTES
    coords_bytes = n_slides * args.tiles_per_slide * 2 * 8
    total_seconds = n_slides * args.seconds_per_slide

    return {
        "manifest": str(args.manifest),
        "n_slides": n_slides,
        "columns": fields,
        "suffix_counts": suffix_counts,
        "estimates": {
            "tiles_per_slide": args.tiles_per_slide,
            "embedding_dim": args.embedding_dim,
            "embedding_gib": round(embedding_bytes / (1024**3), 2),
            "coords_mib": round(coords_bytes / (1024**2), 2),
            "wall_clock_hours": round(total_seconds / 3600, 2),
        },
        "warnings": warnings,
        "errors": errors,
        "ok": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight-check a WSI batch manifest")
    parser.add_argument("--manifest", required=True, help="CSV with slide_path and optional slide_id/case_id/file_id")
    parser.add_argument("--check_exists", action="store_true", help="Fail if slide_path files are absent on this machine")
    parser.add_argument("--tiles_per_slide", type=int, default=DEFAULT_TILES_PER_SLIDE)
    parser.add_argument("--embedding_dim", type=int, default=DEFAULT_EMBEDDING_DIM)
    parser.add_argument("--seconds_per_slide", type=float, default=DEFAULT_SECONDS_PER_SLIDE)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    report = validate(args)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Manifest: {report['manifest']}")
        print(f"Slides  : {report['n_slides']}")
        print(f"Columns : {', '.join(report['columns'])}")
        print(f"Suffixes: {report['suffix_counts']}")
        est = report["estimates"]
        print(
            "Estimate: "
            f"{est['wall_clock_hours']} h, "
            f"{est['embedding_gib']} GiB embeddings, "
            f"{est['coords_mib']} MiB coords"
        )
        for warning in report["warnings"]:
            print(f"WARN: {warning}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
        print("OK" if report["ok"] else "FAILED")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

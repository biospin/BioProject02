#!/usr/bin/env python3
"""
Streaming pipeline for CPTAC-BRCA from NCI Imaging Data Commons (IDC):
download DICOM-WSI series -> tile -> embed -> delete raw, one series at a time,
so peak disk stays small (a few series) instead of the whole ~120 GB cohort.

This is the IDC counterpart of stream_download_embed.py (which streams TCGA .svs
from the Synology NAS). The only thing that changes is the *source*: instead of
the Synology FolderSharing API, each row is a CPTAC SeriesInstanceUID fetched
from IDC public buckets via idc-index (s5cmd, no auth). Tiling, embedding, the
delete-as-you-go disk policy, resumability and per-slide status logging are the
same as the NAS pipeline.

Per manifest row (from list_idc_cptac.py):
  1. download the DICOM series (source_path = SeriesInstanceUID) into --cache-dir
  2. tile_wsi.py    -> coords .npy
  3. extract_<model>.py -> embedding .npy
  4. delete the downloaded series dir   (unless --keep-raw)

Resumable: rows whose embedding already exists are skipped. A status row is
written to --output-manifest after every series so a crash loses at most one.

⚠️ DICOM-WSI READER CAVEAT (verify on server, GPU box):
  CPTAC-BRCA in IDC is DICOM-WSI (a *series* = a folder of .dcm), not .svs.
  tile_wsi.py opens slides with OpenSlide; reading DICOM-WSI needs OpenSlide
  >= 4.0 (openslide-bin ships 4.x). OpenSlide opens a DICOM WSI from the path to
  one instance file in the series (it discovers the rest in the same dir). This
  adapter passes that representative .dcm via --slide. If tile_wsi/OpenSlide
  cannot open it, fallbacks are: (a) upgrade openslide-bin, or (b) convert the
  series to a pyramidal TIFF (e.g. wsidicom / dicom2tiff) before tiling. This is
  the one integration point not yet validated end-to-end.

Example:
  python agents/data/scripts/stream_download_embed_idc.py \
      --manifest agents/data/manifests/cptac_brca_idc_inventory.csv \
      --config   agents/embedding/configs/tile_config.yaml \
      --cache-dir     /home/pseudoer/data/cache/biop02/cptac_raw \
      --tile-dir      /home/pseudoer/data/cache/biop02/cptac_tiles \
      --embedding-dir /home/pseudoer/data/embeddings/biop02/cptac/uni_v1 \
      --output-manifest /home/pseudoer/data/embeddings/biop02/cptac/stream_status.csv \
      --embedding-model uni
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]  # agents/data/scripts -> repo root

EXTRACTORS = {
    "uni": "agents/embedding/scripts/extract_uni.py",
    "conch": "agents/embedding/scripts/extract_conch.py",
    "exaone": "agents/embedding/scripts/extract_exaone.py",
    "dummy": "agents/embedding/scripts/extract_dummy.py",
}
EMB_SUFFIX = {"uni": "_uni_embeddings.npy", "conch": "_conch_embeddings.npy",
              "exaone": "_exaone_embeddings.npy", "dummy": "_dummy_embeddings.npy"}
GPU_MODELS = {"uni", "conch", "exaone"}


def download_series(series_uid: str, dest_dir: Path) -> Path:
    """Download one IDC DICOM series via idc-index. Returns the series dir.

    Skips the download if the series dir already holds .dcm files (resume).
    """
    series_dir = dest_dir / series_uid
    if series_dir.is_dir() and any(series_dir.glob("*.dcm")):
        return series_dir
    from idc_index import IDCClient  # imported lazily so --help works without it

    dest_dir.mkdir(parents=True, exist_ok=True)
    client = IDCClient.client()
    # idc-index lays the series out under downloadDir; dirTemplate flattens it to
    # <downloadDir>/<SeriesInstanceUID>/*.dcm for a predictable path.
    client.download_dicom_series(
        seriesInstanceUID=series_uid,
        downloadDir=str(dest_dir),
        dirTemplate="%SeriesInstanceUID",
    )
    return series_dir


def _representative_dcm(series_dir: Path) -> Path | None:
    """Largest .dcm in the series — the base (highest-res) WSI level for OpenSlide."""
    dcms = sorted(series_dir.glob("*.dcm"), key=lambda p: p.stat().st_size, reverse=True)
    return dcms[0] if dcms else None


def _run(cmd: list[str]) -> tuple[int, float]:
    print("$ " + " ".join(cmd), flush=True)
    t0 = time.time()
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False).returncode
    return rc, time.time() - t0


def _emb_path(emb_dir: Path, model: str, slide_id: str, stem: str) -> Path:
    base = stem if model in GPU_MODELS else slide_id
    return emb_dir / f"{base}{EMB_SUFFIX[model]}"


def _write(out: Path, rows: list[dict]) -> None:
    fields = ["slide_id", "case_id", "series_uid", "downloaded_mb", "coords_path",
              "embedding_path", "download_seconds", "tile_seconds", "embed_seconds",
              "status", "error"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def _dir_mb(p: Path) -> float:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / (1024 * 1024)


def main() -> None:
    ap = argparse.ArgumentParser(description="Streaming IDC download -> tile -> embed -> delete raw")
    ap.add_argument("--manifest", required=True, help="CSV from list_idc_cptac.py (slide_id, case_id, source_path=SeriesInstanceUID)")
    ap.add_argument("--config", required=True, help="tile_config.yaml")
    ap.add_argument("--cache-dir", required=True, help="temp dir for downloaded DICOM series (kept small by deletion)")
    ap.add_argument("--tile-dir", required=True)
    ap.add_argument("--embedding-dir", required=True)
    ap.add_argument("--output-manifest", required=True)
    ap.add_argument("--embedding-model", choices=list(EXTRACTORS) + ["none"], default="uni")
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--keep-raw", action="store_true", help="do not delete the DICOM series after embedding")
    ap.add_argument("--cleanup-tiles", action="store_true", help="also delete coords after embedding")
    ap.add_argument("--limit", type=int, default=0, help="process only first N rows (0=all)")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if args.embedding_model in EXTRACTORS:
        extractor = REPO_ROOT / EXTRACTORS[args.embedding_model]
        if not extractor.exists():
            raise SystemExit(f"extractor not found on this branch: {extractor}")

    with Path(args.manifest).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]
    for col in ("source_path", "slide_id"):
        if rows and col not in rows[0]:
            raise SystemExit(f"manifest missing required column: {col}")

    cache_dir = Path(args.cache_dir)
    tile_dir = Path(args.tile_dir)
    emb_dir = Path(args.embedding_dir)
    results: list[dict] = []

    for i, row in enumerate(rows, 1):
        sid = row["slide_id"]
        series_uid = row["source_path"]
        case_id = row.get("case_id", "")
        coords = tile_dir / f"{sid}_coords.npy"
        emb = _emb_path(emb_dir, args.embedding_model, sid, sid) if args.embedding_model != "none" else None
        res = {"slide_id": sid, "case_id": case_id, "series_uid": series_uid,
               "status": "started", "error": ""}
        print(f"\n[{i}/{len(rows)}] {sid} ({series_uid})", flush=True)

        try:
            if emb is not None and emb.exists() and not args.overwrite:
                res["status"] = "done_cached"; res["embedding_path"] = str(emb)
                results.append(res); _write(Path(args.output_manifest), results); continue

            # 1) download DICOM series from IDC
            t0 = time.time()
            series_dir = download_series(series_uid, cache_dir)
            res["download_seconds"] = f"{time.time() - t0:.1f}"
            slide = _representative_dcm(series_dir)
            if slide is None:
                res["status"] = "download_empty"; res["error"] = "no .dcm in series dir"
                results.append(res); _write(Path(args.output_manifest), results); continue
            res["downloaded_mb"] = f"{_dir_mb(series_dir):.1f}"

            # 2) tile (OpenSlide reads the DICOM-WSI via the representative instance)
            if args.overwrite or not coords.exists():
                rc, t = _run([sys.executable, "agents/embedding/scripts/tile_wsi.py",
                              "--slide", str(slide), "--config", args.config, "--out", str(coords)])
                res["tile_seconds"] = f"{t:.1f}"
                if rc != 0:
                    res["status"] = "tile_failed"; res["error"] = f"tile_wsi rc={rc}"
                    results.append(res); _write(Path(args.output_manifest), results); continue
            res["coords_path"] = str(coords)

            # 3) embed
            if args.embedding_model != "none":
                cmd = [sys.executable, EXTRACTORS[args.embedding_model],
                       "--coords", str(coords), "--out_dir", str(emb_dir)]
                if args.embedding_model in GPU_MODELS:
                    cmd += ["--batch_size", str(args.batch_size), "--device", args.device]
                rc, t = _run(cmd)
                res["embed_seconds"] = f"{t:.1f}"
                if rc != 0:
                    res["status"] = "embed_failed"; res["error"] = f"extractor rc={rc}"
                    results.append(res); _write(Path(args.output_manifest), results); continue
                res["embedding_path"] = str(emb)

            # 4) delete raw series to keep peak disk small
            if not args.keep_raw and series_dir.exists():
                shutil.rmtree(series_dir, ignore_errors=True)
            if args.cleanup_tiles and coords.exists():
                coords.unlink()
                coords.with_suffix(".json").unlink(missing_ok=True)
            res["status"] = "done"
        except Exception as exc:  # keep the batch moving
            res["status"] = "error"; res["error"] = repr(exc)
        results.append(res)
        _write(Path(args.output_manifest), results)
        print(f"status={res['status']} {res.get('error','')}", flush=True)

    done = sum(1 for r in results if r["status"] in ("done", "done_cached"))
    print(f"\nWrote {args.output_manifest}\ndone={done} total={len(results)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Streaming pipeline: NAS download -> tiling -> embedding -> delete raw, one slide
at a time, so peak disk stays small (a few slides) instead of holding the whole
~1.5 TB cohort.

This is the recovery of the download pipeline that was lost with the expired GPU
server. The raw .svs are streamed from the Synology NAS (the only permanent
source), processed, and deleted; only the small embeddings (+coords, logs)
survive. Run it from a NAS-reachable compute box.

Per manifest row:
  1. download source_path from NAS to --cache-dir (resumable)
  2. tile_wsi.py    -> coords .npy
  3. extract_<model>.py -> embedding .npy
  4. delete raw .svs   (unless --keep-raw)

Resumable: rows whose embedding already exists are skipped. A status row is
written to --output-manifest after every slide so a crash loses at most one slide.

Reuses the proven Synology session from list_nas_wsi.py and the embedding
scripts under agents/embedding/scripts/.

Example:
  python agents/data/scripts/stream_download_embed.py \
      --manifest agents/data/manifests/tcga_brca_manifest.csv \
      --config   agents/embedding/configs/tile_config.yaml \
      --cache-dir   /data/cache/biop02/raw \
      --tile-dir    /data/cache/biop02/tiles \
      --embedding-dir /data/embeddings/biop02/uni_v1 \
      --output-manifest /data/embeddings/biop02/stream_status.csv \
      --embedding-model uni
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]  # agents/data/scripts -> repo root
sys.path.insert(0, str(SCRIPT_DIR))
from list_nas_wsi import BASE, DEFAULT_SHARING_ID, _make_opener, login  # noqa: E402

EXTRACTORS = {
    "uni": "agents/embedding/scripts/extract_uni.py",
    "conch": "agents/embedding/scripts/extract_conch.py",
    "exaone": "agents/embedding/scripts/extract_exaone.py",
    "dummy": "agents/embedding/scripts/extract_dummy.py",
}
EMB_SUFFIX = {"uni": "_uni_embeddings.npy", "conch": "_conch_embeddings.npy",
              "exaone": "_exaone_embeddings.npy", "dummy": "_dummy_embeddings.npy"}
GPU_MODELS = {"uni", "conch", "exaone"}


def _download_url(sharing_id: str, source_path: str) -> str:
    hex_path = source_path.encode("utf-8").hex()
    params = urllib.parse.urlencode({
        "api": "SYNO.FolderSharing.Download", "version": "2", "method": "download",
        "_sharing_id": f'"{sharing_id}"', "dlink": f'"{hex_path}"',
        "mode": "download", "stdhtml": "false",
    })
    return f"{BASE}?{params}"


def remote_size(opener, sharing_id: str, source_path: str) -> int | None:
    req = urllib.request.Request(_download_url(sharing_id, source_path))
    req.add_header("Range", "bytes=0-0")
    try:
        with opener.open(req, timeout=60) as r:
            cr = r.headers.get("Content-Range")  # e.g. "bytes 0-0/1680123456"
            r.read(1)
        if cr and "/" in cr:
            return int(cr.rsplit("/", 1)[1])
    except Exception:
        return None
    return None


def download_slide(opener, sharing_id: str, source_path: str, out_path: Path,
                   expected: int | None) -> int:
    have = out_path.stat().st_size if out_path.exists() else 0
    if expected is not None and have == expected:
        return have  # already complete
    if expected is not None and have > expected:
        out_path.unlink()  # corrupt/partial larger than source -> restart
        have = 0
    req = urllib.request.Request(_download_url(sharing_id, source_path))
    mode = "wb"
    if have:
        req.add_header("Range", f"bytes={have}-")
        mode = "ab"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with opener.open(req, timeout=600) as r, out_path.open(mode) as f:
        shutil.copyfileobj(r, f, length=1024 * 1024)
    return out_path.stat().st_size


def _run(cmd: list[str]) -> tuple[int, float]:
    print("$ " + " ".join(cmd), flush=True)
    t0 = time.time()
    rc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False).returncode
    return rc, time.time() - t0


def _emb_path(emb_dir: Path, model: str, slide_id: str, file_name: str) -> Path:
    stem = Path(file_name).stem if model in GPU_MODELS else slide_id
    return emb_dir / f"{stem}{EMB_SUFFIX[model]}"


def _write(out: Path, rows: list[dict]) -> None:
    fields = ["slide_id", "case_id", "file_name", "source_path", "downloaded_bytes",
              "coords_path", "embedding_path", "download_seconds", "tile_seconds",
              "embed_seconds", "status", "error"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    ap = argparse.ArgumentParser(description="Streaming NAS download -> tile -> embed -> delete raw")
    ap.add_argument("--manifest", required=True, help="manifest CSV (needs source_path, slide_id, file_name)")
    ap.add_argument("--config", required=True, help="tile_config.yaml")
    ap.add_argument("--cache-dir", required=True, help="temp dir for raw .svs (kept small by deletion)")
    ap.add_argument("--tile-dir", required=True)
    ap.add_argument("--embedding-dir", required=True)
    ap.add_argument("--output-manifest", required=True)
    ap.add_argument("--embedding-model", choices=list(EXTRACTORS) + ["none"], default="uni")
    ap.add_argument("--sharing-id", default=DEFAULT_SHARING_ID)
    ap.add_argument("--password", default="")
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--keep-raw", action="store_true", help="do not delete raw .svs after embedding")
    ap.add_argument("--cleanup-tiles", action="store_true", help="also delete coords after embedding")
    ap.add_argument("--limit", type=int, default=0, help="process only first N rows (0=all)")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if args.embedding_model in EXTRACTORS:
        extractor = REPO_ROOT / EXTRACTORS[args.embedding_model]
        if not extractor.exists():
            raise SystemExit(f"extractor not found on this branch: {extractor}\n"
                             f"(conch/exaone live on feat/BIOP02-31 — merge first or use uni/dummy)")

    with Path(args.manifest).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]
    for col in ("source_path", "slide_id", "file_name"):
        if rows and col not in rows[0]:
            raise SystemExit(f"manifest missing required column: {col}")

    opener = _make_opener()
    login(opener, args.sharing_id, args.password)

    cache_dir = Path(args.cache_dir)
    tile_dir = Path(args.tile_dir)
    emb_dir = Path(args.embedding_dir)
    results: list[dict] = []

    for i, row in enumerate(rows, 1):
        sid, fname, spath = row["slide_id"], row["file_name"], row["source_path"]
        case_id = row.get("case_id", "")
        coords = tile_dir / f"{sid}_coords.npy"
        emb = _emb_path(emb_dir, args.embedding_model, sid, fname) if args.embedding_model != "none" else None
        res = {"slide_id": sid, "case_id": case_id, "file_name": fname,
               "source_path": spath, "status": "started", "error": ""}
        print(f"\n[{i}/{len(rows)}] {sid}", flush=True)

        try:
            # resumable skip
            if emb is not None and emb.exists() and not args.overwrite:
                res["status"] = "done_cached"
                res["embedding_path"] = str(emb)
                results.append(res); _write(Path(args.output_manifest), results); continue

            raw = cache_dir / fname
            t0 = time.time()
            exp = remote_size(opener, args.sharing_id, spath)
            got = download_slide(opener, args.sharing_id, spath, raw, exp)
            res["download_seconds"] = f"{time.time() - t0:.1f}"
            res["downloaded_bytes"] = got
            if exp is not None and got != exp:
                res["status"] = "download_size_mismatch"
                res["error"] = f"expected {exp} got {got}"
                results.append(res); _write(Path(args.output_manifest), results); continue

            if args.overwrite or not coords.exists():
                rc, t = _run([sys.executable, "agents/embedding/scripts/tile_wsi.py",
                              "--slide", str(raw), "--config", args.config, "--out", str(coords)])
                res["tile_seconds"] = f"{t:.1f}"
                if rc != 0:
                    res["status"] = "tile_failed"; res["error"] = f"tile_wsi rc={rc}"
                    results.append(res); _write(Path(args.output_manifest), results); continue
            res["coords_path"] = str(coords)

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

            # cleanup to keep peak disk small
            if not args.keep_raw and raw.exists():
                raw.unlink()
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

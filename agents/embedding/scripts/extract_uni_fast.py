"""
Fast UNI v1 extractor — SSD-staged .svs + parallel tile reading (DataLoader workers).

Produces embeddings BIT-FOR-BIT comparable to extract_uni.py (same load_uni model,
same transform, same coord order); only the I/O path differs, so outputs can be
mixed with files already made by extract_uni.py. Designed for HDD-bound storage:
the raw .svs is copied to SSD once, then 5000 random tile reads hit SSD in parallel
instead of thrashing a spinning disk. Same output filename → resumable skip works.

Run:
    python agents/embedding/scripts/extract_uni_fast.py \
        --coords ~/data/tiles/TCGA-xxx_coords.npy \
        --out_dir ~/data/embeddings/biop02/tcga/uni_v1 \
        [--batch_size 64] [--device cuda:0] [--num_workers 6] [--no_stage]
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from extract_uni import load_uni  # identical offline model + transform


class TileDataset(Dataset):
    """Reads one tile per index; opens its own slide handle lazily per worker."""
    def __init__(self, slide_path, coords, read_size, transform):
        self.slide_path = str(slide_path)
        self.coords = coords
        self.read_size = int(read_size)
        self.transform = transform
        self._slide = None

    def __len__(self):
        return len(self.coords)

    def _handle(self):
        if self._slide is None:
            import openslide
            self._slide = openslide.OpenSlide(self.slide_path)
        return self._slide

    def __getitem__(self, idx):
        x, y = int(self.coords[idx][0]), int(self.coords[idx][1])
        img = self._handle().read_region((x, y), 0, (self.read_size, self.read_size)).convert("RGB")
        return self.transform(img)


def extract(coords_path, out_dir, batch_size=64, device="cuda",
            num_workers=6, stage_dir="/workspace/data/cache/biop02/_stage", no_stage=False):
    coords_path = Path(coords_path)
    meta = json.loads(coords_path.with_suffix(".json").read_text())
    coords = np.load(coords_path)
    slide_src = meta["slide"]
    read_size = meta.get("read_size", meta["tile_size"])
    n = len(coords)

    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    model, transform = load_uni(device)

    out_path = Path(out_dir); out_path.mkdir(parents=True, exist_ok=True)
    slide_name = Path(slide_src).stem
    emb_file = out_path / f"{slide_name}_uni_embeddings.npy"

    slide_path = slide_src
    staged = None
    if not no_stage:
        sd = Path(stage_dir); sd.mkdir(parents=True, exist_ok=True)
        staged = sd / f"{os.getpid()}_{Path(slide_src).name}"
        t0 = time.time(); shutil.copy(slide_src, staged)
        slide_path = str(staged)
        print(f"  staged→SSD {time.time()-t0:.1f}s", flush=True)

    try:
        ds = TileDataset(slide_path, coords, read_size, transform)
        dl = DataLoader(ds, batch_size=batch_size, num_workers=num_workers, shuffle=False,
                        pin_memory=(device != "cpu"),
                        prefetch_factor=(4 if num_workers > 0 else None))
        emb = np.empty((n, 1024), dtype=np.float32)
        i = 0; t0 = time.time()
        with torch.inference_mode():
            for batch in dl:
                batch = batch.to(device, non_blocking=True)
                feats = model(batch)
                k = feats.shape[0]
                emb[i:i+k] = feats.float().cpu().numpy(); i += k
        assert i == n, f"count mismatch {i}!={n}"
        np.save(emb_file, emb)
        print(f"Saved     : {emb_file} shape={emb.shape} compute={time.time()-t0:.1f}s", flush=True)
    finally:
        if staged and Path(staged).exists():
            Path(staged).unlink()
    return emb_file


def main():
    ap = argparse.ArgumentParser(description="Fast UNI extractor (SSD staging + parallel reads)")
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--num_workers", type=int, default=6)
    ap.add_argument("--stage_dir", default="/workspace/data/cache/biop02/_stage")
    ap.add_argument("--no_stage", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    f = extract(a.coords, a.out_dir, a.batch_size, a.device, a.num_workers, a.stage_dir, a.no_stage)
    print(f"Done in {time.time()-t0:.1f}s → {f}")


if __name__ == "__main__":
    main()

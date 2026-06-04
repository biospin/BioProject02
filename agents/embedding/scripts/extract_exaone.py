"""
EXAONE Path 2.0 tile embedding extractor (LGAI-EXAONE/EXAONE-Path-2.0, 768-dim).

Reads tile coordinates from coords.npy + coords.json (produced by tile_wsi.py),
extracts per-tile embeddings using EXAONE Path 2.0, and saves as float32 .npy.

Requirements:
    pip install transformers
    export HF_TOKEN=hf_xxx   # gated model — HuggingFace access token 필요

Run:
    export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}
    time python agents/embedding/scripts/extract_exaone.py \
        --coords /workspace/data/cache/biop02/tiles/TCGA-xxx_coords.npy \
        --out_dir /workspace/data/cache/biop02/embeddings/exaone_v1/ \
        [--batch_size 32] [--device cuda]
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_exaone(device: str) -> tuple:
    """Load EXAONE Path 2.0 from HuggingFace hub. Returns (model, processor)."""
    from transformers import AutoImageProcessor, AutoModel

    print("  Loading EXAONE Path 2.0 from HuggingFace (LGAI-EXAONE/EXAONE-Path-2.0) …")
    processor = AutoImageProcessor.from_pretrained("LGAI-EXAONE/EXAONE-Path-2.0")
    model = AutoModel.from_pretrained("LGAI-EXAONE/EXAONE-Path-2.0")
    model = model.to(device)
    model.eval()

    return model, processor


# ---------------------------------------------------------------------------
# Tile reading
# ---------------------------------------------------------------------------

def read_tile(slide, x: int, y: int, read_size: int) -> Image.Image:
    region = slide.read_region((x, y), 0, (read_size, read_size))
    return region.convert("RGB")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract(
    coords_path: str,
    out_dir: str,
    batch_size: int = 32,
    device: str = "cuda",
) -> Path:
    import openslide

    coords_path = Path(coords_path)
    meta_path = coords_path.with_suffix(".json")

    coords = np.load(coords_path)
    meta = json.loads(meta_path.read_text())

    slide_path = meta["slide"]
    read_size  = meta.get("read_size", meta["tile_size"])
    n_tiles    = len(coords)

    print(f"Slide     : {slide_path}")
    print(f"Tiles     : {n_tiles}  read_size={read_size}")
    print(f"Device    : {device}")

    if device == "cuda" and not torch.cuda.is_available():
        print("  [warn] CUDA unavailable — falling back to CPU")
        device = "cpu"

    model, processor = load_exaone(device)

    slide = openslide.OpenSlide(slide_path)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    slide_name = Path(slide_path).stem
    emb_file = out_path / f"{slide_name}_exaone_embeddings.npy"

    embeddings = np.empty((n_tiles, 768), dtype=np.float32)

    with torch.inference_mode():
        for start in tqdm(range(0, n_tiles, batch_size), desc="  Extracting", unit="batch"):
            end   = min(start + batch_size, n_tiles)
            batch = coords[start:end]

            imgs = [read_tile(slide, int(x), int(y), read_size) for x, y in batch]

            # AutoImageProcessor handles resize + normalization for the full batch
            inputs = processor(images=imgs, return_tensors="pt").to(device)
            outputs = model(**inputs)

            # CLS token (position 0) from last hidden state → 768-dim patch features
            feats = outputs.last_hidden_state[:, 0, :]
            embeddings[start:end] = feats.cpu().numpy()

    slide.close()
    np.save(emb_file, embeddings)

    print(f"Saved     : {emb_file}  shape={embeddings.shape}")
    return emb_file


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract EXAONE Path 2.0 tile embeddings from a WSI"
    )
    parser.add_argument("--coords",     required=True, help="Path to coords .npy file")
    parser.add_argument("--out_dir",    required=True, help="Output directory")
    parser.add_argument("--batch_size", type=int, default=32,  help="Tiles per GPU batch (default: 32)")
    parser.add_argument("--device",     default="cuda",        help="cuda or cpu (default: cuda)")
    args = parser.parse_args()

    t0 = time.time()
    emb_file = extract(args.coords, args.out_dir, args.batch_size, args.device)
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s  →  {emb_file}")


if __name__ == "__main__":
    main()

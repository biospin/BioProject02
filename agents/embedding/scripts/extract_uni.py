"""
UNI v1 tile embedding extractor (MahmoodLab/UNI, 1024-dim).

Reads tile coordinates from coords.npy + coords.json (produced by tile_wsi.py),
extracts per-tile embeddings using UNI v1, and saves as float32 .npy.

coords.json의 read_size 필드를 사용하므로 tile_wsi.py의 MPP scale 보정이
자동 반영됩니다 (40× 슬라이드라면 512×512 읽고 224×224로 리사이즈).

Requirements:
    export HF_TOKEN=hf_xxx   # gated model — HuggingFace access token 필요
    # 또는: huggingface-cli login

Run:
    export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}
    time python agents/embedding/scripts/extract_uni.py \
        --coords /workspace/data/cache/biop02/pilot_tiles/TCGA-xxx_coords.npy \
        --out_dir /workspace/data/cache/biop02/pilot_embeddings/ \
        [--batch_size 64] [--device cuda]
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_uni(device: str) -> tuple:
    """Load UNI v1 from HuggingFace hub. Returns (model, transform)."""
    import timm

    print("  Loading UNI v1 from HuggingFace (MahmoodLab/UNI) …")
    model = timm.create_model(
        "hf-hub:MahmoodLab/UNI",
        pretrained=True,
        init_values=1e-5,
        dynamic_img_size=True,
    )
    model = model.to(device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])

    return model, transform


# ---------------------------------------------------------------------------
# Tile reading
# ---------------------------------------------------------------------------

def read_tile(slide, x: int, y: int, read_size: int) -> Image.Image:
    """Read a tile from the slide at level-0 coordinates and return RGB PIL image."""
    region = slide.read_region((x, y), 0, (read_size, read_size))
    return region.convert("RGB")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract(
    coords_path: str,
    out_dir: str,
    batch_size: int = 64,
    device: str = "cuda",
) -> Path:
    import openslide

    coords_path = Path(coords_path)
    meta_path = coords_path.with_suffix(".json")

    coords = np.load(coords_path)                       # (N, 2) int64, level-0 px
    meta = json.loads(meta_path.read_text())

    slide_path = meta["slide"]
    read_size  = meta.get("read_size", meta["tile_size"])  # fallback for old coords.json
    n_tiles    = len(coords)

    print(f"Slide     : {slide_path}")
    print(f"Tiles     : {n_tiles}  read_size={read_size}")
    print(f"Device    : {device}")

    if device == "cuda" and not torch.cuda.is_available():
        print("  [warn] CUDA unavailable — falling back to CPU")
        device = "cpu"

    model, transform = load_uni(device)

    slide = openslide.OpenSlide(slide_path)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    slide_name = Path(slide_path).stem
    emb_file = out_path / f"{slide_name}_uni_embeddings.npy"

    embeddings = np.empty((n_tiles, 1024), dtype=np.float32)

    with torch.inference_mode():
        for start in tqdm(range(0, n_tiles, batch_size), desc="  Extracting", unit="batch"):
            end   = min(start + batch_size, n_tiles)
            batch = coords[start:end]

            imgs = [read_tile(slide, int(x), int(y), read_size) for x, y in batch]
            tensor = torch.stack([transform(img) for img in imgs]).to(device)

            feats = model(tensor)                       # (B, 1024)
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
        description="Extract UNI v1 tile embeddings from a WSI"
    )
    parser.add_argument("--coords",     required=True, help="Path to coords .npy file")
    parser.add_argument("--out_dir",    required=True, help="Output directory")
    parser.add_argument("--batch_size", type=int, default=64,    help="Tiles per GPU batch (default: 64)")
    parser.add_argument("--device",     default="cuda",           help="cuda or cpu (default: cuda)")
    args = parser.parse_args()

    t0 = time.time()
    emb_file = extract(args.coords, args.out_dir, args.batch_size, args.device)
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s  →  {emb_file}")


if __name__ == "__main__":
    main()

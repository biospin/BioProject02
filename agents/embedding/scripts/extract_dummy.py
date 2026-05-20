"""
Dummy embedding extractor — unblocks Modeling Agent while awaiting HF approval.
Outputs torch.randn(N, 1024) to match UNI v1 embedding dimension.
"""

import argparse
import numpy as np
from pathlib import Path


def extract_dummy(coords_path: str, out_dir: str, dim: int = 1024, seed: int = 42):
    coords = np.load(coords_path)
    n_tiles = len(coords)

    rng = np.random.default_rng(seed)
    embeddings = rng.standard_normal((n_tiles, dim)).astype(np.float32)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    slide_name = Path(coords_path).stem.replace("_coords", "")
    emb_file = out_path / f"{slide_name}_dummy_embeddings.npy"
    np.save(emb_file, embeddings)

    print(f"Saved dummy embeddings: {emb_file}  shape={embeddings.shape}  dim={dim}")
    return emb_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dummy tile embeddings")
    parser.add_argument("--coords", required=True, help="Path to coords .npy file")
    parser.add_argument("--out_dir", required=True, help="Output directory")
    parser.add_argument("--dim", type=int, default=1024, help="Embedding dimension (default: 1024 = UNI v1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    extract_dummy(args.coords, args.out_dir, args.dim, args.seed)

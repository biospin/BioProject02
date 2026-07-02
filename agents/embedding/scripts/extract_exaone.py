#!/usr/bin/env python3
"""
BIOP02-48/-38 — EXAONE Path 2.0 slide-level feature extraction (TCGA-BRCA).

EXAONE Path 2.0 (LGAI-EXAONE/EXAONE-Path-2.0, 768-dim) has a *slide-level*
interface that differs fundamentally from UNI/CONCH: the model takes the .svs
path directly and performs tiling + Macenko normalization internally, so the
coords.npy per-tile loop used for UNI/CONCH does NOT apply here.

model(svs_path) -> (act1, act2, act3):
  - act1 (N_tiles, 768) : first-stage per-small-tile features (tissue tiles only)
  - act2 (N_large, 768) : second-stage
  - act3 (1, 768)       : third-stage GLOBAL slide embedding (the model's own
                          slide aggregation — use this as the slide-level rep)

We save two slide-level 768-d representations per slide so downstream probes
can pick apples-to-apples with UNI/CONCH mean-pooling:
  - slide_global : act3[0]        (EXAONE's designed slide embedding)
  - patch_mean   : act1.mean(0)   (mean-pooled, comparable to UNI/CONCH pooling)

Output: <out_dir>/<slide_id>_exaone.npz  {slide_global, patch_mean, n_patches, dim}
Resumable: existing outputs are skipped. Shardable across GPUs via --shard-idx/--num-shards.

Note: EXAONE's forward uses torch.compile (inductor/triton). If /tmp is mounted
noexec the triton .so fails to map — set TRITON_CACHE_DIR / TORCHINDUCTOR_CACHE_DIR
to an exec-allowed dir (e.g. $HOME/.cache/*), which the runner does.

Usage (single shard on cuda:0):
  CUDA_VISIBLE_DEVICES=0 python extract_exaone.py \
      --slides-dir ~/data/tcga_brca_wsi \
      --repo-dir agents/embedding/exaone_path2/repo \
      --out-dir ~/data/embeddings/biop02/tcga/exaone_v2 \
      --shard-idx 0 --num-shards 3
"""
import argparse
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import torch


def slide_id_from_path(p: Path) -> str:
    # TCGA-3C-AALI-01Z-00-DX1.<uuid>.svs -> TCGA-3C-AALI-01Z-00-DX1.<uuid>
    return p.name[: -len(".svs")] if p.name.endswith(".svs") else p.stem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides-dir", help="dir of *.svs (glob+shard mode)")
    ap.add_argument("--slides-file", help="text file, one .svs path per line "
                    "(explicit-list mode; overrides --slides-dir/--shard-idx). "
                    "Lets us reprocess/quarantine specific slides without index shifts.")
    ap.add_argument("--repo-dir", required=True, help="EXAONE repo dir (exaonepath.py + pytorch_model.bin)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--shard-idx", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--target-mpp", type=float, default=0.5)
    ap.add_argument("--batch-size", type=int, default=128)
    args = ap.parse_args()

    repo = Path(args.repo_dir).expanduser().resolve()
    sys.path.insert(0, str(repo))
    from exaonepath import EXAONEPathV20  # noqa: E402

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.slides_file:
        with open(args.slides_file) as f:
            shard = [Path(ln.strip()).expanduser() for ln in f if ln.strip()]
        tag = f"[list {Path(args.slides_file).name}]"
        print(f"{tag} explicit-list n={len(shard)} "
              f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES','?')}", flush=True)
    else:
        if not args.slides_dir:
            ap.error("one of --slides-dir or --slides-file is required")
        slides = sorted(Path(args.slides_dir).expanduser().glob("*.svs"))
        shard = [s for i, s in enumerate(slides) if i % args.num_shards == args.shard_idx]
        tag = f"[shard {args.shard_idx}/{args.num_shards}]"
        print(f"{tag} total={len(slides)} this-shard={len(shard)} "
              f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES','?')}", flush=True)

    # load model once
    t0 = time.time()
    model = EXAONEPathV20()
    sd = torch.load(str(repo / "pytorch_model.bin"), map_location=model.device, weights_only=True)
    model.load_state_dict(sd, strict=True)
    model.eval()
    print(f"{tag} model loaded in {time.time()-t0:.1f}s device={model.device}", flush=True)

    done = failed = skipped = 0
    for k, svs in enumerate(shard, 1):
        sid = slide_id_from_path(svs)
        out = out_dir / f"{sid}_exaone.npz"
        if out.exists():
            skipped += 1
            continue
        t1 = time.time()
        try:
            with torch.no_grad():
                act1, act2, act3 = model(str(svs), target_mpp=args.target_mpp,
                                         first_stg_batch_size=args.batch_size)
            slide_global = act3.float().reshape(-1).cpu().numpy()      # (768,)
            patch_mean = act1.float().mean(0).cpu().numpy()            # (768,)
            n_patches = int(act1.shape[0])
            # tmp must end in ".npz" or np.savez appends ".npz" and os.replace
            # then can't find the file it thinks it wrote (prior rename bug).
            tmp = out.with_suffix(".tmp.npz")
            np.savez(tmp, slide_global=slide_global, patch_mean=patch_mean,
                     n_patches=np.int64(n_patches), dim=np.int64(slide_global.shape[0]))
            os.replace(tmp, out)
            done += 1
            print(f"{tag} [{k}/{len(shard)}] {sid[:24]} n_patch={n_patches} "
                  f"dim={slide_global.shape[0]} {time.time()-t1:.1f}s", flush=True)
        except Exception:
            failed += 1
            print(f"{tag} [{k}/{len(shard)}] FAIL {sid[:24]}\n{traceback.format_exc()}", flush=True)

    print(f"{tag} DONE done={done} skipped={skipped} failed={failed}", flush=True)


if __name__ == "__main__":
    main()

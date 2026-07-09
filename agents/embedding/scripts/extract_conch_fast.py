"""
Fast CONCH extractor — model loaded once, loops a shard of slides; per slide:
SSD-stage the .svs + parallel tile reading (DataLoader). Output bit-identical to
extract_conch.py (same load_conch model+preprocess, same encode_image call, same
coord order); only the I/O path differs. Same output filename → resumable skip.

Run (one shard on one GPU):
  python agents/embedding/scripts/extract_conch_fast.py \
      --shard-file shard0.txt --out_dir <dir> --device cuda:0 [--num_workers 6]
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "0")   # CONCH gated; token valid → allow fetch/cache
import argparse, json, shutil, sys, time
from pathlib import Path
import numpy as np, torch
from torch.utils.data import Dataset, DataLoader

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from extract_conch import load_conch  # identical model + preprocess

class TileDataset(Dataset):
    def __init__(self, slide_path, coords, read_size, transform):
        self.slide_path=str(slide_path); self.coords=coords
        self.read_size=int(read_size); self.transform=transform; self._s=None
    def __len__(self): return len(self.coords)
    def _h(self):
        if self._s is None:
            import openslide; self._s=openslide.OpenSlide(self.slide_path)
        return self._s
    def __getitem__(self, i):
        x,y=int(self.coords[i][0]),int(self.coords[i][1])
        img=self._h().read_region((x,y),0,(self.read_size,self.read_size)).convert("RGB")
        return self.transform(img)

def embed_one(coords_path, out_dir, model, preprocess, device, bs, nw, stage_dir, no_stage, overwrite):
    meta=json.loads(Path(coords_path).with_suffix(".json").read_text())
    coords=np.load(coords_path); slide_src=meta["slide"]
    read_size=meta.get("read_size", meta["tile_size"]); n=len(coords)
    out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    emb_file=out/f"{Path(slide_src).stem}_conch_embeddings.npy"
    if emb_file.exists() and not overwrite:
        return "cached", emb_file
    slide_path=slide_src; staged=None
    if not no_stage:
        sd=Path(stage_dir); sd.mkdir(parents=True, exist_ok=True)
        staged=sd/f"{os.getpid()}_{Path(slide_src).name}"; shutil.copy(slide_src, staged); slide_path=str(staged)
    try:
        ds=TileDataset(slide_path, coords, read_size, preprocess)
        dl=DataLoader(ds, batch_size=bs, num_workers=nw, shuffle=False,
                      pin_memory=(device!="cpu"), prefetch_factor=(4 if nw>0 else None))
        emb=np.empty((n,512), dtype=np.float32); i=0
        with torch.inference_mode():
            for b in dl:
                b=b.to(device, non_blocking=True)
                f=model.encode_image(b, proj_contrast=False, normalize=False)
                k=f.shape[0]; emb[i:i+k]=f.float().cpu().numpy(); i+=k
        assert i==n, f"{i}!={n}"
        np.save(emb_file, emb)
    finally:
        if staged and Path(staged).exists(): Path(staged).unlink()
    return "done", emb_file

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shard-file"); ap.add_argument("--coords")
    ap.add_argument("--out_dir", required=True); ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch_size", type=int, default=64); ap.add_argument("--num_workers", type=int, default=6)
    ap.add_argument("--stage_dir", default="/workspace/data/cache/biop02/_stage_conch"); ap.add_argument("--no_stage", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a=ap.parse_args()
    if a.shard_file:
        items=[l.strip() for l in open(a.shard_file) if l.strip().endswith(".npy")]
    else:
        items=[a.coords]
    dev=a.device if (a.device=="cpu" or torch.cuda.is_available()) else "cpu"
    model, preprocess = load_conch(dev)
    done=skip=fail=0; t0=time.time()
    for j,c in enumerate(items,1):
        try:
            st,f=embed_one(c, a.out_dir, model, preprocess, dev, a.batch_size, a.num_workers, a.stage_dir, a.no_stage, a.overwrite)
            if st=="cached": skip+=1
            else: done+=1
            print(f"[{j}/{len(items)}] {st} {Path(c).stem} ({done}d/{skip}s/{fail}f) {time.time()-t0:.0f}s", flush=True)
        except Exception as e:
            fail+=1; print(f"[{j}/{len(items)}] FAIL {Path(c).stem}: {repr(e)[:100]}", flush=True)
    print(f"shard done: done={done} skip={skip} fail={fail}", flush=True)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""BRCA 염색정규화 UNI 재추출 큐 러너 (BIOP02-147).

모델·normalizer를 한 번만 로드하고 shard의 coords 목록을 순회한다(기존 출력 skip=재개).
사용: python run_stainnorm_queue.py --shard 0 --nshards 3 --device cuda:0
출력: ~/data/embeddings/biop02/tcga/uni_stainnorm_v1/<slide>_uni_stainnorm_embeddings.npy
"""
import argparse, glob, json, sys, time
from pathlib import Path
import numpy as np, torch
from PIL import Image
from torchvision import transforms

HERE = Path(__file__).parent
REF_TILE = HERE / "reference_tile.png"
COORDS_DIR = "/home/kkkim/data/tiles"
OUT_DIR = "/home/kkkim/data/embeddings/biop02/tcga/uni_stainnorm_v1"


def load_uni(device):
    import timm
    m = timm.create_model("hf-hub:MahmoodLab/uni", pretrained=True, init_values=1e-5,
                          dynamic_img_size=True).to(device).eval()
    tf = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                             transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))])
    return m, tf


def make_norm():
    import torchstain
    to255 = transforms.Compose([transforms.ToTensor(), transforms.Lambda(lambda x: x*255)])
    n = torchstain.normalizers.MacenkoNormalizer(backend="torch")
    n.fit(to255(Image.open(REF_TILE).convert("RGB")))
    return n, to255


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=3)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--batch_size", type=int, default=64)
    a = ap.parse_args()

    import openslide
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    cjs = sorted(glob.glob(f"{COORDS_DIR}/*_coords.json"))
    mine = [c for i, c in enumerate(cjs) if i % a.nshards == a.shard]
    dev = a.device if torch.cuda.is_available() else "cpu"
    model, tf = load_uni(dev)
    normalizer, to255 = make_norm()
    log = HERE / f"queue_shard{a.shard}.log"
    def w(m):
        with open(log, "a") as f: f.write(m+"\n")
        print(m, flush=True)
    w(f"[shard {a.shard}/{a.nshards}] slides={len(mine)} dev={dev} start={time.strftime('%H:%M:%S')}")

    done = 0
    for cj in mine:
        meta = json.loads(Path(cj).read_text())
        coords = np.load(cj.replace(".json", ".npy"))
        stem = Path(meta["slide"]).stem
        outf = Path(OUT_DIR) / f"{stem}_uni_stainnorm_embeddings.npy"
        if outf.exists():
            done += 1; continue
        rs = meta.get("read_size", meta["tile_size"])
        try:
            sl = openslide.OpenSlide(meta["slide"])
        except Exception as e:
            w(f"  OPENFAIL {stem}: {e}"); continue
        emb = np.empty((len(coords), 1024), dtype=np.float32); nfail = 0
        t0 = time.time()
        with torch.inference_mode():
            for s in range(0, len(coords), a.batch_size):
                e = min(s+a.batch_size, len(coords)); pil = []
                for x, y in coords[s:e]:
                    im = sl.read_region((int(x), int(y)), 0, (rs, rs)).convert("RGB")
                    try:
                        Inorm, _, _ = normalizer.normalize(I=to255(im), stains=False)
                        im = Image.fromarray(Inorm.numpy().astype(np.uint8))
                    except Exception:
                        nfail += 1
                    pil.append(im)
                emb[s:e] = model(torch.stack([tf(p) for p in pil]).to(dev)).cpu().numpy()
        sl.close()
        np.save(outf, emb)
        (Path(OUT_DIR)/f"{stem}_stainnorm_meta.json").write_text(json.dumps(
            {"slide": stem, "n_tiles": int(len(coords)), "n_stainnorm_fail": int(nfail)}))
        done += 1
        w(f"  [{done}/{len(mine)}] {stem} tiles={len(coords)} fail={nfail} {time.time()-t0:.0f}s")
    w(f"[shard {a.shard}] DONE {done}/{len(mine)} end={time.strftime('%H:%M:%S')}")
    (HERE / f"queue_shard{a.shard}.status").write_text(f"DONE {done}/{len(mine)}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""UNI v1 임베딩 추출 — Macenko 염색정규화 적용판 (BIOP02-147).

extract_uni.py와 동일한 coords/read_size/transform을 쓰되, read_tile 직후에
torchstain MacenkoNormalizer로 각 타일을 고정 reference에 정규화한 뒤 UNI에 넣는다.
정규화 실패 타일(조직 부족·특이행렬)은 원본으로 폴백하고 카운트한다.

출력: <out_dir>/<slide_stem>_uni_stainnorm_embeddings.npy  (float32 N×1024)
      + <slide_stem>_stainnorm_meta.json (실패 타일 수 등)
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

REF_TILE = Path(__file__).parent / "reference_tile.png"  # 고정 reference (재현성)


def load_uni(device):
    import timm
    model = timm.create_model(
        "hf-hub:MahmoodLab/uni", pretrained=True, init_values=1e-5, dynamic_img_size=True
    ).to(device).eval()
    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])
    return model, transform


def make_normalizer():
    import torchstain
    to255 = transforms.Compose([transforms.ToTensor(), transforms.Lambda(lambda x: x * 255)])
    ref = Image.open(REF_TILE).convert("RGB")
    n = torchstain.normalizers.MacenkoNormalizer(backend="torch")
    n.fit(to255(ref))
    return n, to255


def stain_normalize(norm, to255, tile_pil):
    """Macenko 정규화된 PIL 반환. 실패 시 원본 반환(+실패 플래그)."""
    try:
        Inorm, _, _ = norm.normalize(I=to255(tile_pil), stains=False)
        arr = Inorm.numpy().astype(np.uint8)
        return Image.fromarray(arr), False
    except Exception:
        return tile_pil, True


def extract(coords_path, out_dir, batch_size=64, device="cuda"):
    import openslide
    coords_path = Path(coords_path)
    meta = json.loads(coords_path.with_suffix(".json").read_text())
    coords = np.load(coords_path)
    slide_path = meta["slide"]
    read_size = meta.get("read_size", meta["tile_size"])
    n_tiles = len(coords)
    slide_name = Path(slide_path).stem
    out_path = Path(out_dir); out_path.mkdir(parents=True, exist_ok=True)
    emb_file = out_path / f"{slide_name}_uni_stainnorm_embeddings.npy"
    if emb_file.exists():
        print(f"SKIP (exists): {emb_file.name}"); return emb_file

    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    model, transform = load_uni(device)
    normalizer, to255 = make_normalizer()
    slide = openslide.OpenSlide(slide_path)

    embeddings = np.empty((n_tiles, 1024), dtype=np.float32)
    n_fail = 0
    with torch.inference_mode():
        for start in range(0, n_tiles, batch_size):
            end = min(start + batch_size, n_tiles)
            batch = coords[start:end]
            pil = []
            for x, y in batch:
                t = slide.read_region((int(x), int(y)), 0, (read_size, read_size)).convert("RGB")
                tn, failed = stain_normalize(normalizer, to255, t)
                n_fail += failed
                pil.append(tn)
            tensor = torch.stack([transform(im) for im in pil]).to(device)
            embeddings[start:end] = model(tensor).cpu().numpy()
    slide.close()
    np.save(emb_file, embeddings)
    (out_path / f"{slide_name}_stainnorm_meta.json").write_text(json.dumps(
        {"slide": slide_name, "n_tiles": n_tiles, "n_stainnorm_fail": int(n_fail),
         "fail_frac": round(n_fail / max(n_tiles, 1), 4), "read_size": read_size}, indent=2))
    print(f"Saved: {emb_file.name}  shape={embeddings.shape}  stainnorm_fail={n_fail}/{n_tiles}")
    return emb_file


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    extract(a.coords, a.out_dir, a.batch_size, a.device)

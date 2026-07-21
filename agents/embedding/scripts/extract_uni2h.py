"""
UNI2-h tile embedding extractor (MahmoodLab/UNI2-h, 1536-dim).

CLAUDE.md FM 표: UNI2-h = 다중 FM 견고성 검증용(Paper C 모델 비의존성). 헤드라인은 UNI v1(1024-d).

⚠️ UNI2-h는 **register token 8개**를 쓴다(Virchow2는 4개 — 혼동 금지). config.json:
  architecture=vit_giant_patch14_224, num_features=1536, global_pool="token", reg_tokens=8.
표준 사용법(모델 카드)은 CLS token pooling → **1536-d**. timm이 global_pool="token"으로
model(x)가 이미 CLS 벡터를 반환하므로 register token을 직접 슬라이싱할 필요가 없다
(Virchow2는 forward_features의 raw token을 직접 다뤄야 했던 것과 다름).

I/O 계약은 extract_uni.py / extract_virchow2.py와 동일:
  coords.npy + coords.json(read_size 포함) → <slide>_uni2h_embeddings.npy

Run:
    /opt/envs/spatialpatho/bin/python agents/embedding/scripts/extract_uni2h.py \
        --coords <coords.npy> --out_dir <dir> [--batch_size 32] [--device cuda]
"""

import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

EMB_DIM = 1536


def load_uni2h(device: str) -> tuple:
    """Load UNI2-h from local HF cache. Returns (model, transform). 스펙 = 모델 카드 timm_kwargs."""
    import timm
    from timm.data import resolve_data_config
    from timm.data.transforms_factory import create_transform

    timm_kwargs = {
        "img_size": 224,
        "patch_size": 14,
        "depth": 24,
        "num_heads": 24,
        "init_values": 1e-5,
        "embed_dim": 1536,
        "mlp_ratio": 2.66667 * 2,
        "num_classes": 0,
        "no_embed_class": True,
        "mlp_layer": timm.layers.SwiGLUPacked,
        "act_layer": torch.nn.SiLU,
        "reg_tokens": 8,
        "dynamic_img_size": True,
    }
    model = timm.create_model("hf-hub:MahmoodLab/UNI2-h", pretrained=True, **timm_kwargs)
    model.eval().to(device)
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))
    return model, transform


class TileDataset(torch.utils.data.Dataset):
    def __init__(self, slide_path, coords, read_size, transform):
        self.slide_path = str(slide_path)
        self.coords = coords
        self.read_size = read_size
        self.transform = transform
        self._h = None

    def __len__(self):
        return len(self.coords)

    def _handle(self):
        if self._h is None:
            import openslide
            self._h = openslide.OpenSlide(self.slide_path)
        return self._h

    def __getitem__(self, idx):
        x, y = int(self.coords[idx][0]), int(self.coords[idx][1])
        img = self._handle().read_region((x, y), 0, (self.read_size, self.read_size)).convert("RGB")
        return self.transform(img)


def extract(coords_path, out_dir, batch_size=32, device="cuda", num_workers=6):
    coords_path = Path(coords_path)
    meta = json.loads(coords_path.with_suffix(".json").read_text())
    coords = np.load(coords_path)
    slide_path = meta["slide"]
    read_size = meta["read_size"]
    name = coords_path.name.replace("_coords.npy", "")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    emb_file = out_dir / f"{name}_uni2h_embeddings.npy"

    model, transform = load_uni2h(device)
    ds = TileDataset(slide_path, coords, read_size, transform)
    dl = torch.utils.data.DataLoader(ds, batch_size=batch_size, num_workers=num_workers,
                                     pin_memory=True, shuffle=False)

    t0 = time.time()
    feats = []
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16, enabled=(device == "cuda")):
        for batch in tqdm(dl, desc=name, unit="batch"):
            batch = batch.to(device, non_blocking=True)
            out = model(batch)                       # global_pool="token" → (B, 1536) CLS 벡터
            feats.append(out.float().cpu())

    emb = torch.cat(feats).numpy().astype(np.float32)
    assert emb.shape == (len(coords), EMB_DIM), f"shape {emb.shape} != ({len(coords)}, {EMB_DIM})"
    assert np.isfinite(emb).all(), "non-finite embedding"
    np.save(emb_file, emb)
    print(f"[uni2h] {name}: {emb.shape} in {time.time()-t0:.1f}s → {emb_file}", flush=True)
    return emb_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--num_workers", type=int, default=6)
    a = ap.parse_args()
    extract(a.coords, a.out_dir, a.batch_size, a.device, a.num_workers)


if __name__ == "__main__":
    main()

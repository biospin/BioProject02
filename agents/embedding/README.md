# Embedding Agent

WSI tiling + foundation model feature extraction pipeline for TCGA-BRCA.

**Owner:** kkkim (gkkim)  
**Sprint 1 scope:** tile_wsi pilot → UNI v1 batch → embedding manifest for sjpark

---

## Quick Start

```bash
# 1. Environment setup (first time)
bash agents/embedding/setup.sh

export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

# 2. Pilot: tile 1 slide
time ~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
    --slide /data/raw/tcga/sample.svs \
    --config agents/embedding/configs/tile_config.yaml \
    --out outputs/pilot/coords.npy

# 3. Extract UNI embeddings
export HF_TOKEN=hf_xxx
time ~/miniconda3/bin/python agents/embedding/scripts/extract_uni.py \
    --coords outputs/pilot/coords.npy \
    --out_dir outputs/pilot/

# 4. Batch (TCGA-BRCA full run)
~/miniconda3/bin/python agents/embedding/scripts/validate_batch_manifest.py \
    --manifest data/manifests/tcga_brca_subset.csv

~/miniconda3/bin/python agents/embedding/scripts/run_batch_embedding.py \
    --manifest data/manifests/tcga_brca_subset.csv \
    --config agents/embedding/configs/tile_config.yaml \
    --tile_dir /workspace/data/cache/biop02/tiles \
    --embedding_dir /data/embeddings/biop02/uni_v1 \
    --output_manifest /data/embeddings/biop02/embedding_manifest.csv \
    --embedding_model uni
```

---

## Scripts

### `tile_wsi.py`

Tiles a WSI into 256×256 patches using an Otsu tissue mask.

| Parameter | Value |
|---|---|
| Tile size | 256×256 px |
| Target MPP | 0.5 μm/px (20×) |
| Tissue threshold | 0.1 (Otsu) |
| Cap per slide | 5,000 tiles (random sample, seed=42) |

**Output:**
- `coords.npy` — `(N, 2)` int64, columns = (x, y) in level-0 pixels
- `coords.json` — slide metadata (level, MPP, read_size, n_tiles, capped)

```bash
python agents/embedding/scripts/tile_wsi.py \
    --slide <path.svs> \
    --config agents/embedding/configs/tile_config.yaml \
    --out <out_dir>/coords.npy
```

---

### `extract_uni.py`

Extracts UNI v1 tile embeddings (MahmoodLab/UNI, 1024-dim).

Reads `coords.npy + coords.json` from `tile_wsi.py`. Uses `read_size` from the JSON so MPP scaling is applied correctly (e.g., 40× slides read 512×512 → resize to 224×224).

**Requirements:** `HF_TOKEN` env var or `huggingface-cli login` with approved MahmoodLab/UNI access.

**Output:** `<slide_stem>_uni_embeddings.npy` — `(N, 1024)` float32

```bash
export HF_TOKEN=hf_xxx
python agents/embedding/scripts/extract_uni.py \
    --coords <coords.npy> \
    --out_dir <embedding_dir> \
    [--batch_size 64] [--device cuda]
```

---

### `extract_dummy.py`

Unblocks sjpark (Modeling Agent) while UNI approval/extraction is pending.
Outputs `(N, 1024)` random float32 with the same filename convention as extract_uni.py.

---

### `run_batch_embedding.py`

Sequential batch runner: for each row in the manifest CSV, runs tile_wsi.py → extract_uni.py and writes a result manifest CSV row-by-row (safe to resume on crash).

**Input manifest columns:** `slide_path` (required), `slide_id`, `case_id`, `file_id` (optional)

**Output manifest columns:** `slide_id`, `coords_path`, `embedding_path`, `n_tiles`, `status`, `error`, ...

```bash
python agents/embedding/scripts/run_batch_embedding.py \
    --manifest <input.csv> \
    --config agents/embedding/configs/tile_config.yaml \
    --tile_dir <tile_dir> \
    --embedding_dir <emb_dir> \
    --output_manifest <result.csv> \
    --embedding_model uni   # uni | dummy | none
    [--overwrite] [--dry_run]
```

---

### `validate_batch_manifest.py`

Preflight check before reserving a GPU slot.

Checks: required columns, duplicate slide IDs/paths, missing files (with `--check_exists`), runtime/storage estimates.

```bash
python agents/embedding/scripts/validate_batch_manifest.py \
    --manifest <input.csv> \
    [--check_exists] [--json]
```

**Estimates (pilot baseline):** ~131s/slide (5.6s tiling + 125.6s UNI @ A100)

---

## Output Layout

```
/workspace/data/cache/biop02/tiles/
    <slide_id>_coords.npy
    <slide_id>_coords.json

/data/embeddings/biop02/uni_v1/
    <slide_stem>_uni_embeddings.npy

/data/embeddings/biop02/
    embedding_manifest.csv       ← consumed by sjpark (Modeling Agent)
```

Embeddings are **permanent storage** — do not delete without coordinating with sjpark.

---

## Batch Manifest Format

See `configs/batch_manifest_template.csv`:

```csv
slide_id,case_id,file_id,slide_path
TCGA-XX-XXXX-01Z-00-DX1,TCGA-XX-XXXX,<uuid>,/workspace/data/cache/biop02/wsi/TCGA-XX-XXXX-01Z-00-DX1.svs
```

---

## Infrastructure Notes

- GPU slots: reserve in `#biop02-alerts` before running (09–13 / 13–17 / 17–21 / 21–01 KST)
- `pyvips` must be imported before `torch` (libvips/libjpeg conflict)
- WSI raw data is S3 read-only; tiles go to `/data/cache/` (LRU 200 GB)
- TCGA-BRCA scope: ~150 slides (open-access subset, Paper A)

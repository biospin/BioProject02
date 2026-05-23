# PILOT_REPORT — BIOP02-30

**이슈:** BIOP02-30 — [S0] HF 승인 후 1 slide pilot + wall-clock 측정  
**담당:** kkkim  
**Sprint:** 0  
**날짜:** 2026-05-23

---

## 1. Pilot 슬라이드

| 항목 | 값 |
|---|---|
| 파일명 | `TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs` |
| 서버 경로 | `/workspace/data/cache/biop02/pilot_wsi/` |
| 파일 크기 | 1.6 GB |
| Scanner / Vendor | Aperio (aperio.AppMag = 40×) |
| Level 0 해상도 | 101184 × 74432 px |
| Level 수 | 4 (downsample: 1×, 4×, 16×, 64×) |
| MPP (openslide.mpp-x) | 0.250 μm/px (40×) |

---

## 2. 시스템 환경

| 항목 | 값 |
|---|---|
| 서버 | `121.126.38.195:2205` (A100 80GB × 1, 24 CPU, 188 GiB RAM) |
| Python | 3.13.13 (`~/miniconda3/bin/python`) |
| openslide-python | 1.4.3 |
| Pillow | 12.2.0 |
| numpy | 2.4.4 |
| GPU (타일링은 CPU) | 미사용 |

---

## 3. Tiling 설정

`agents/embedding/configs/tile_config.yaml` 기준:

| 파라미터 | 값 |
|---|---|
| `tile_size` | 256 px |
| `target_mpp` | 0.5 μm/px (≈ 20×) |
| `otsu.tissue_threshold` | 0.10 (10% 이상 조직 픽셀) |
| `otsu.downsample_factor` | 64 (썸네일 기준 마스크) |
| `per_patient_cap` | 5,000 타일 |
| `seed` | 42 |

---

## 4. 실행 명령

```bash
cd ~/project/BioProject02
export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

# 타일링
time ~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
  --slide /workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  --config agents/embedding/configs/tile_config.yaml \
  --out /workspace/data/cache/biop02/pilot_tiles/TCGA-3C-AALI-01Z-00-DX1_coords.npy

# 더미 임베딩
time ~/miniconda3/bin/python agents/embedding/scripts/extract_dummy.py \
  --coords /workspace/data/cache/biop02/pilot_tiles/TCGA-3C-AALI-01Z-00-DX1_coords.npy \
  --out_dir /workspace/data/cache/biop02/pilot_embeddings/
```

---

## 5. 측정 결과

### 5.1 Tiling

| 항목 | 값 |
|---|---|
| 선택된 level | 0 |
| 실제 MPP | 0.250 μm/px (40× 스캐너) |
| MPP scale | 2.0× (read_size=512 → resize to 256, 유효 해상도 0.5 μm/px) |
| 전체 후보 타일 (캡 적용 전) | 14,198 |
| 저장된 타일 수 (`n_tiles`) | 5,000 |
| per_patient_cap 적용 여부 | Yes (capped=True) |
| wall-clock 시간 | **5.6 s** |
| coords.npy 파일 크기 | 79 KB |
| coords.json 파일 크기 | 436 B |

### 5.2 더미 임베딩

| 항목 | 값 |
|---|---|
| 임베딩 shape | (5000, 1024) |
| 출력 파일 | `TCGA-3C-AALI-01Z-00-DX1_dummy_embeddings.npy` |
| wall-clock 시간 | **0.2 s** |
| 파일 크기 | 20 MB |

### 5.3 UNI v1 실제 임베딩

| 항목 | 값 |
|---|---|
| 모델 | UNI v1 (`MahmoodLab/UNI`, timm `hf-hub:`) |
| 임베딩 shape | (5000, 1024) |
| 출력 파일 | `TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-..._uni_embeddings.npy` |
| wall-clock 시간 | **125.6 s (2분 6초)** |
| 배치 크기 | 64 tiles/batch, ~1.54 s/batch |
| GPU | A100 80GB (cuda) |
| 300장 전체 추산 | ~10시간 |

---

## 6. 산출물 경로 (서버)

```
/workspace/data/cache/biop02/pilot_wsi/
  └── TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs  (1.6 GB)

/workspace/data/cache/biop02/pilot_tiles/
  ├── TCGA-3C-AALI-01Z-00-DX1_coords.npy   (79 KB, shape: 5000×2)
  └── TCGA-3C-AALI-01Z-00-DX1_coords.json  (418 B)

/workspace/data/cache/biop02/pilot_embeddings/
  ├── TCGA-3C-AALI-01Z-00-DX1_dummy_embeddings.npy          (20 MB, shape: 5000×1024)
  └── TCGA-3C-AALI-01Z-00-DX1..._uni_embeddings.npy         (20 MB, shape: 5000×1024)
```

---

## 7. coords.json

```json
{
  "slide": "/workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs",
  "slide_name": "TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291",
  "target_level": 0,
  "target_mpp": 0.5,
  "actual_mpp": 0.25,
  "scale": 2.0,
  "tile_size": 256,
  "read_size": 512,
  "level_dims": [101184, 74432],
  "n_tiles": 5000,
  "n_before_cap": 14198,
  "capped": true,
  "per_patient_cap": 5000
}
```

---

## 8. 관찰 사항 / 이슈

### ✅ MPP scale 자동 보정 적용 (tile_wsi.py 수정)

- 이 슬라이드는 Aperio 40× 스캐너 (mpp=0.25). Level 1 = 1.0 μm/px로 target 0.5에 가장 가까운 level이 0.
- `tile_wsi.py`에 `scale = target_mpp / actual_mpp` 로직 추가:
  - scale=2.0 → 512×512 픽셀을 읽고 256×256으로 리사이즈
  - 유효 해상도: 0.5 μm/px (20×) — foundation model 입력 기준과 일치
  - `read_size`, `scale` 필드가 coords.json에 기록됨 → 추출 스크립트에서 활용 가능
- TCGA-BRCA 슬라이드 전체에 자동 적용됨 (mpp 메타데이터 있는 슬라이드라면 scanner 무관)

### 조직 타일 비율

- scale 보정 후 grid 후보: 14,198장 (보정 전: 54,350장) — 그리드 간격이 2배로 넓어진 것이 정상.
- cap 5,000장 사용 → 조직 커버리지 정상.

---

## 9. 상태

| 단계 | 상태 |
|---|---|
| WSI 서버 업로드 | ✅ 완료 (1.6 GB) |
| 환경 설치 | ✅ openslide-python 1.4.3, numpy 2.4.4 |
| Tiling 실행 | ✅ 완료 (5.6 s, 5,000 tiles, scale=2.0 보정) |
| tile_wsi.py MPP scale 보정 | ✅ 완료 (read_size=512 → resize to 256) |
| 더미 임베딩 생성 | ✅ 완료 (0.2 s, shape 5000×1024) |
| UNI v1 실제 임베딩 추출 | ✅ 완료 (125.6 s, shape 5000×1024, GPU A100) |
| PILOT_REPORT.md 작성 | ✅ 완료 |

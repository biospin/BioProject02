# SpatialPathoAgent — WSI 임베딩 파이프라인 개요

> 작성: kkkim | 최초 작성: 2026-05-23 | 기준 코드: `agents/embedding/`

---

## 1. 왜 이 파이프라인이 필요한가

유방암 분자 아형(ER/PR/HER2, PAM50)을 확인하려면 IHC(면역조직화학) 검사가 필요하다.
하지만 IHC는 추가 비용과 시간이 들고, 일부 기관/데이터셋에서는 검사 결과가 누락되거나 표준화되지 않은 경우가 있다.

반면 H&E(헤마톡실린-에오신) 염색 슬라이드는 거의 모든 환자에게 존재하고, 디지털화된 형태로 대규모 아카이브가 공개되어 있다 (TCGA, CPTAC).

**핵심 질문:** H&E 슬라이드의 조직 형태(morphology)만 보고 분자 특성을 예측할 수 있는가?

이 파이프라인은 그 질문에 답하기 위한 첫 번째 단계다.

```
H&E WSI
  → 타일링 (tile_wsi.py)
  → 임베딩 추출 (extract_uni.py)
  → Phenotype 예측 (MLP / Attention MIL)  ← sjpark
  → Therapeutic Hypothesis               ← jhans
```

---

## 2. 파이프라인 전체 흐름

```
슬라이드 1장 (.svs, ~1.6 GB)
│
├─ [1단계] tile_wsi.py
│    Otsu 마스크로 조직 영역 감지
│    → 256×256 타일 추출 (20× 유효 해상도)
│    → 최대 5,000장 랜덤 샘플링
│    → coords.npy  (N×2, level-0 pixel 좌표)
│    → coords.json (메타데이터: mpp, scale, n_tiles ...)
│
├─ [2단계] extract_uni.py
│    UNI v1 모델로 각 타일 → 1024차원 벡터
│    → uni_embeddings.npy  (N×1024, float32)
│
└─ [3단계] MLP / Attention MIL  (sjpark)
     슬라이드 레벨 예측
     → ER status, PR status, HER2, PAM50
```

---

## 3. 1단계 — WSI 타일링 (`tile_wsi.py`)

### 왜 타일링이 필요한가

WSI 한 장은 10만×7만 픽셀 이상의 거대한 이미지다.
GPU 메모리에 통째로 올릴 수 없고, 대부분의 영역은 배경(유리)이다.
→ 조직이 있는 부분만 잘라서 모델에 입력한다.

### 설계 결정

| 파라미터 | 값 | 이유 |
|---|---|---|
| `tile_size` | 256 px | Foundation model 표준 입력 크기 |
| `target_mpp` | 0.5 μm/px (20×) | UNI/CONCH 학습 해상도 기준 |
| `tissue_threshold` | 0.10 | 배경 타일 제거 최소 조직 비율 |
| `per_patient_cap` | 5,000 | GPU 메모리 및 클래스 불균형 완화 |
| 마스크 방법 | Otsu + morphological closing | cv2 미사용, numpy/PIL만 사용 |

### MPP scale 보정 (중요)

TCGA-BRCA 슬라이드 대부분이 Aperio 40× 스캐너 (mpp=0.25)로 촬영됐다.
이 슬라이드에는 20×에 해당하는 피라미드 레벨이 없다.

```
Level 0: 0.25 μm/px (40×) → target 0.5와의 거리: 0.25
Level 1: 1.00 μm/px (10×) → target 0.5와의 거리: 0.50
```

단순 level 선택 시 Level 0(40×)이 선택되어 Foundation model 입력 기준과 불일치.

**해결:** `scale = target_mpp / actual_mpp = 2.0` 계산 →
512×512 픽셀을 읽고 256×256으로 리사이즈 → 유효 해상도 0.5 μm/px 확보.

```python
scale     = target_mpp / actual_mpp   # 0.5 / 0.25 = 2.0
read_size = round(tile_size * scale)  # 512
# → slide.read_region((x, y), 0, (512, 512)) 후 resize to 256×256
```

### 출력 형식

```
coords.npy   shape (N, 2), dtype int64
             columns: (x, y) in level-0 pixel space
             (openslide.read_region 입력 규약과 동일)

coords.json  {
               "slide": "...",
               "actual_mpp": 0.25,
               "scale": 2.0,
               "read_size": 512,
               "tile_size": 256,
               "n_tiles": 5000,
               "n_before_cap": 14198,
               "capped": true
             }
```

### 실행

```bash
export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

time ~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
  --slide /workspace/data/cache/biop02/pilot_wsi/<slide>.svs \
  --config agents/embedding/configs/tile_config.yaml \
  --out /workspace/data/cache/biop02/pilot_tiles/<slide>_coords.npy
```

---

## 4. 2단계 — 임베딩 추출 (`extract_uni.py`)

### Foundation Model이란

수백만 장의 병리 이미지로 사전학습된 대형 Vision Transformer 모델.
각 타일(256×256 이미지)을 입력하면 그 조직 패치의 특징을 압축한 벡터를 출력한다.

병리 도메인 지식이 모델에 이미 인코딩되어 있으므로, 적은 수의 레이블로도 효과적인 다운스트림 예측이 가능하다.

### UNI v1 선택 이유

| 모델 | 차원 | 학습 데이터 | 선택 여부 |
|---|---|---|---|
| **UNI v1** | 1024 | 100K+ 슬라이드, 다양한 암종 | ✅ Sprint 1 기본 |
| CONCH | 512 | 병리 + 텍스트 멀티모달 | Sprint 2 비교 예정 |
| EXAONE Path 2.0 | 768 | 공개 모델 | Sprint 2 비교 예정 |
| Virchow2 | 1280 | Paige AI 독점 데이터 | Sprint 2 비교 예정 |

### 처리 흐름

```
coords.npy의 각 (x, y) 좌표
  → slide.read_region((x, y), 0, (read_size, read_size))  # 512×512
  → PIL.Image.resize(224, 224)                            # UNI 입력 크기
  → ImageNet 정규화 (mean/std: 0.485/0.229, 0.456/0.224, 0.406/0.225)
  → UNI v1 ViT-L/16 forward
  → 1024차원 벡터
```

### 출력 형식

```
uni_embeddings.npy   shape (N, 1024), dtype float32
                     N = n_tiles (최대 5,000)
                     각 행 = 타일 1장의 morphology 특징 벡터
```

### 실행

```bash
# HuggingFace 로그인 필요 (최초 1회)
~/miniconda3/bin/hf auth login

time ~/miniconda3/bin/python agents/embedding/scripts/extract_uni.py \
  --coords /workspace/data/cache/biop02/pilot_tiles/<slide>_coords.npy \
  --out_dir /workspace/data/cache/biop02/pilot_embeddings/ \
  --batch_size 64 \
  --device cuda
```

---

## 5. 파일럿 측정 결과 (2026-05-23)

슬라이드: `TCGA-3C-AALI-01Z-00-DX1` (Aperio 40×, 1.6 GB)

| 단계 | wall-clock | 산출물 크기 | 비고 |
|---|---|---|---|
| 타일링 | 5.6 s | coords.npy 79 KB | 5,000 tiles / 14,198 candidates |
| UNI 임베딩 | 125.6 s | embeddings.npy 20 MB | 64 tiles/batch, A100 80GB |
| **합계 (1장)** | **~2분** | **~20 MB** | |
| **300장 추산** | **~10시간** | **~6 GB** | GPU 야간 슬롯 필요 |

---

## 6. 논문 Methods 초안 (영어)

> 이 섹션은 Paper A Methods 작성 시 직접 활용 가능한 초안이다.
> 수치는 파일럿 기준이며, 전체 데이터 처리 후 업데이트 필요.

### WSI Preprocessing

Whole-slide images (WSIs) were tiled at an effective magnification of 20× (0.5 μm/pixel). For slides scanned at 40× (0.25 μm/pixel), which constitutes the majority of TCGA-BRCA specimens, tiles were extracted by reading 512×512 pixel regions at the native level and resizing to 256×256 pixels, yielding an effective resolution of 0.5 μm/pixel. Tissue regions were identified using Otsu thresholding on grayscale thumbnails (downsample factor: 64×), followed by morphological closing (radius: 7 pixels) to fill gaps. Tiles with tissue coverage below 10% were discarded. A maximum of 5,000 tiles per slide were retained via random sampling (seed=42) to mitigate class imbalance and memory constraints.

### Feature Extraction

Tile-level morphological features were extracted using UNI v1 (Chen et al., 2024), a Vision Transformer Large (ViT-L/16) foundation model pretrained on over 100,000 pathology whole-slide images across diverse cancer types. Each 256×256 tile was resized to 224×224 pixels and normalized using ImageNet statistics (mean: [0.485, 0.456, 0.406]; std: [0.229, 0.224, 0.225]) prior to model inference. Features were extracted in batches of 64 on an NVIDIA A100 80GB GPU, yielding 1,024-dimensional float32 embeddings per tile. Wall-clock time for feature extraction averaged approximately 2 minutes per slide.

---

## 7. 참고문헌

> **읽는 순서 권장:** UNI → Attention MIL → CLAM → Otsu

### 이 파이프라인 직접 관련

| 논문 | 저자 | 저널/학회 | 링크 | 한 줄 |
|---|---|---|---|---|
| UNI v1 — 사용한 모델 | Chen et al. | Nature Medicine, 2024 | [HuggingFace](https://huggingface.co/MahmoodLab/UNI) · [arXiv:2308.15474](https://arxiv.org/abs/2308.15474) | 병리 특화 ViT-L, 100K+ 슬라이드 사전학습 |
| Attention-based Deep MIL | Ilse et al. | ICML, 2018 | [arXiv:1802.04712](https://arxiv.org/abs/1802.04712) | 타일 → 슬라이드 예측의 핵심 구조 |
| CLAM — MIL 실전 구현 | Lu et al. | Nature Biomed Eng, 2021 | [arXiv:2004.09666](https://arxiv.org/abs/2004.09666) | Attention MIL 표준 구현, WSI 분류 기준 |

### 데이터 & 인프라

| 소스 | 저자/기관 | 링크 | 한 줄 |
|---|---|---|---|
| TCGA-BRCA 데이터셋 | TCGA Network | [GDC Portal](https://portal.gdc.cancer.gov) | 유방암 공개 데이터, 본 프로젝트 주 데이터소스 |
| openslide — WSI 읽기 | Goode et al., 2013 | [openslide.org](https://openslide.org) | SVS/NDPI 등 WSI 포맷 처리 라이브러리 |

### 알고리즘 원본

| 알고리즘 | 저자 | 출처 | 한 줄 |
|---|---|---|---|
| Otsu 이진화 | Otsu, 1979 | IEEE Trans. Syst. Man Cybern. | 조직 마스크에 사용한 임계값 알고리즘 원본 |

### 더 읽을거리 (선택)

| 논문 | 추천 이유 |
|---|---|
| CONCH (Lu et al., 2024, Nature Medicine) | Sprint 2에서 UNI와 비교 예정인 멀티모달 모델 |
| TransMIL (Shao et al., 2021, NeurIPS) | Attention MIL의 Transformer 버전, Sprint 3 후보 |
| DSMIL (Li et al., 2021, CVPR) | Multi-scale MIL, Sprint 3 후보 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-05-23 | 최초 작성. Pilot 1장 수치 포함. |

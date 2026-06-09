# CLAM — Industry / Engineering Lens (toolkit reuse)

## TL;DR
CLAM repo는 단순한 모델이 아니라 **end-to-end WSI 전처리·추출·학습 toolkit**이다. BIOP02
embedding agent (kkkim) 입장에서 가장 가치 있는 부분은 모델보다 **앞단 파이프라인 (tissue
segmentation + tiling + feature extraction)** 재사용성이다. License: **GPLv3, non-commercial
academic** — 우리 academic publication-only scope와 호환.

## Pipeline (4 stages, mahmoodlab/CLAM)
1. **Segmentation & Patching — `create_patches_fp.py`**
   - background/hole 제외 후 tissue contour에서 patch 좌표 추출.
   - 주요 파라미터: `seg_level`, `sthresh`, `mthresh`, **`use_otsu`**, `close`,
     `a_t`(tissue area thr), `a_h`(hole thr), `max_n_holes`, `contour_fn`(four_pt/center/basic),
     `use_padding`.
   - 출력: tissue **PNG mask**, CSV metadata, patch 좌표 **.h5**.
   - 데이터셋별 preset: `tcga.csv`, `bwh_biopsy.csv`, `bwh_resection.csv`.
2. **Feature Extraction — `extract_features_fp.py`**
   - default encoder: **ResNet50 truncated → 1024-dim**.
   - encoder swap: `--model_name uni_v1` (UNI, 1024) / `conch_v1` (CONCH, 512),
     `UNI_CKPT_PATH` / `CONCH_CKPT_PATH` env var로 checkpoint 지정.
   - 출력: **.h5** (embedding + coords) + **.pt** (embedding only).
3. **Weakly-supervised training — `main.py`** : slide-level label만으로 MIL 학습.
   - `--model_type`: `clam_sb` / `clam_mb` / `mil`(generic baseline).
4. **Eval & Viz — `eval.py`, `create_heatmaps.py`** : per-fold checkpoint, attention heatmap.

## What we actually reuse vs. rebuild
| 단계 | 재사용 결정 | 이유 |
|---|---|---|
| **Otsu tissue segmentation** | **재사용/참조** | 우리 `tile_config.yaml`의 Otsu mask와 동일 원리. `use_otsu`, `sthresh`, `a_t` 파라미터를 우리 default 검증 reference로 활용 |
| Patch 좌표 .h5 포맷 | 참조 (정렬) | coords.npy 우리 산출물과 매핑 가능; downstream 호환 |
| **feature extraction encoder swap** | **재사용 가능** | UNI/CONCH 네이티브 지원 → 우리 FM embedding 추출 경로 단축 |
| CLAM-SB/MB 학습 코드 | **baseline 재현용** | modeling agent (sjpark) attention-MIL baseline 재현에 그대로 사용 |
| 자체 tiling 스크립트 | **유지** | per-patient cap 5000, 256×256@20×, S3 read-only 레이아웃 등 우리 인프라 제약 반영 필요 → CLAM을 fork하지 않고 우리 `tile_wsi.py` 유지하되 파라미터/포맷을 CLAM과 정합 |

## Engineering 주의점
- **License**: GPLv3 → 코드 직접 포함 시 우리 repo도 전염. **참조·재현 구현**을 권장하고,
  toolkit 자체는 별도 환경에서 baseline 실행용으로만 사용. 코드 copy-paste 금지, re-implement.
- **frozen encoder 전제**: CLAM은 encoder 고정 + attention만 학습. 우리도 동일 (FM embedding은
  pre-extract). GPU 슬롯은 feature extraction 단계에 집중하면 됨.
- **재현 가능성**: .h5/.pt 산출물 규격이 명확해 modeling agent와의 handoff (dummy→real embedding)
  계약을 CLAM 포맷에 맞추면 인터페이스 안정.

## Verdict (industry)
**전처리/추출 toolkit은 적극 재사용·정합, MIL 학습 코드는 baseline 재현용으로 분리 실행.**
GPLv3 때문에 코드 통합은 피하고, Otsu·tiling·encoder-swap 설계를 우리 파이프라인의
검증 기준선으로 가져온다.

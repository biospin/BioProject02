# Confluence 작업 완료 초안

> 이 파일의 내용은 Confluence에 직접 붙여넣을 수 있습니다. Claude 또는 Codex에서 Atlassian MCP 설정을 완료한 경우 "Confluence에 써줘"라고 요청하면 자동 업로드할 수 있고, MCP 미설정 시에는 수동으로 붙여넣습니다.
> 위치: VC 스페이스 > 프로젝트 진행-AI전용 > 프로젝트#02 > BIOP02-1 하위

---

## BIOP02-26

**페이지 제목:** `[S0] agents/embedding/setup.sh 작성 (임베딩 에이전트 환경 셋업 자동화)`

**설명**

Embedding Agent 작업 환경을 재현 가능하게 설치하는 setup.sh를 작성하고 A100 서버(Ubuntu 22.04, Python 3.10, CUDA 12.4)에서 전 패키지 설치 및 동작 확인 완료함. 팀원 누구든 스크립트 1회 실행으로 동일한 환경을 구성할 수 있도록 설치 흐름과 사후 검증 로직을 포함함.

진행 내역:

- `agents/embedding/setup.sh` 작성
- 설치 대상 패키지: pyvips (conda-forge), torch 2.6.0+cu124 · torchvision, openslide-python · openslide-bin, timm, huggingface_hub, numpy, tqdm, pillow
- 설치 후 자동 검증 코드 내장 — 각 패키지 import 성공 여부 및 CUDA 가용성 출력
- **주의 (환경 이슈 2건)**
  - pyvips는 torch보다 먼저 import해야 함 — torch의 libjpeg가 먼저 로드되면 libvips와 충돌 발생
  - 스크립트 실행 및 이후 모든 python 실행 시 `LD_LIBRARY_PATH=~/miniconda3/lib` 선행 설정 필요
- 설치 확인 결과: torch 2.6.0+cu124 CUDA=True, pyvips 3.1.1, openslide, timm, huggingface_hub 전 패키지 정상

사용 예시:

```bash
export LD_LIBRARY_PATH=~/miniconda3/lib:$LD_LIBRARY_PATH
bash agents/embedding/setup.sh
```

---

## BIOP02-27

**페이지 제목:** `[S0] tile_config.yaml + scripts/tile_wsi.py 작성 (WSI 타일링 구현)`

**설명**

H&E WSI(Whole Slide Image) 슬라이드를 256×256 크기의 패치로 잘라 조직 영역만 선별하는 타일링 파이프라인을 구현하고 단위 테스트 통과 확인함. 설정은 YAML로 분리하여 실험별 파라미터 변경이 코드 수정 없이 가능하도록 함.

진행 내역:

- `agents/embedding/configs/tile_config.yaml` 작성 — 타일링 파라미터 중앙 관리
  - tile_size=256, target_mpp=0.5 (20×), tissue_threshold=0.1, downsample_factor=64, per_patient_cap=5000
- `agents/embedding/scripts/tile_wsi.py` 작성
  - openslide 기반 슬라이드 읽기 및 MPP 메타데이터로 20× 레벨 자동 선택 (메타데이터 없으면 L1 fallback)
  - 순수 numpy/PIL로 Otsu 임계값 구현 — cv2 미사용 (환경 의존성 최소화)
  - 모폴로지 closing(PIL MaxFilter → MinFilter)으로 마스크 노이즈 제거
  - per_patient_cap 초과 시 랜덤 샘플링 (seed 고정으로 재현 가능)
- 출력 포맷: `coords.npy` (N, 2) int64 — level-0 픽셀 좌표 (openslide 규약), `coords.json` 메타데이터 companion
- 단위 테스트 통과: Otsu 정확도, 바이너리 closing, cap 로직, config 파싱

사용 예시:

```bash
export LD_LIBRARY_PATH=~/miniconda3/lib:$LD_LIBRARY_PATH
time ~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
    --slide /data/raw/tcga/sample.svs \
    --config agents/embedding/configs/tile_config.yaml \
    --out outputs/pilot/coords.npy
```

개념 설명:

이 스크립트가 하는 일을 비유하면, 유리 슬라이드 전체 사진(WSI)에서 실제 조직이 있는 부분만 찾아 우표 크기로 잘라내는 것입니다.

```
WSI (유리 슬라이드 전체 이미지)
       ↓  1단계: 전체를 작게 축소해서 "조직 있는 곳 지도" 만들기 (Otsu 마스크)
       ↓  2단계: 지도 기준으로 256×256 우표만 남기기 (tissue_threshold=10%)
       ↓  3단계: 5000장 초과 시 랜덤 5000장만 선택 (per_patient_cap)
       ↓
coords.npy  ← 선택된 타일의 좌표 목록
```

coords.npy는 extract_dummy.py와 이후 extract_uni.py가 공통으로 읽는 파일입니다.
tile_wsi.py → coords.npy → extract_*.py → embeddings.npy → [sjpark] MLP 학습 순서로 연결됩니다.

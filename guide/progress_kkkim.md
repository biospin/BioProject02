# kkkim 작업 진행 로그

## 2026-06-24

### BIOP02-54 CPTAC-BRCA 임베딩 추출 — 코드/검증 완료, GPU 서버 복구 대기

| JIRA | 태스크 | 커밋 |
|---|---|---|
| BIOP02-54 | CPTAC IDC 다운로드 어댑터 + 인벤토리 + DICOM 파이프라인 검증 | 0629100, 8918834 |

브랜치: `feat/BIOP02-54-kkkim-cptac-embed` (push 완료)

**만든 것**
- `agents/data/scripts/list_idc_cptac.py` — idc-index로 CPTAC-BRCA SM 시리즈 조회 → 인벤토리 CSV
- `agents/data/manifests/cptac_brca_idc_inventory.csv` — **653 슬라이드 / 198 환자 / 120.2 GB** (실측, idc-index)
- `agents/data/scripts/stream_download_embed_idc.py` — IDC DICOM 스트리밍: 다운로드(idc-index s5cmd) → 타일 → 임베딩 → raw 삭제. NAS판 `stream_download_embed.py`의 삭제/resumable 코어 재사용, 다운로드부만 IDC로 교체.
- `guide/runbooks/download_cptac_from_idc.md` — 실행 런북

**핵심 발견:** CPTAC-BRCA는 IDC에서 `.svs`가 아니라 **DICOM-WSI**. tile_wsi(OpenSlide)는 **OpenSlide ≥ 4.0** 필요.

**검증 완료 (macmini, OpenSlide 4.0.1):** 실제 슬라이드 `18BR017_01`로 전체 흐름 통과 — 다운로드 → DICOM 오픈(17280×19316, 3 levels, MPP 0.25) → Otsu 타일 103 → dummy 임베딩 (103,1024) → raw 삭제 → status=done. **다운로드/DICOM 타일링/삭제/resumable 코어 검증됨.**

**남은 것 (GPU 서버에서):** `--embedding-model uni`(torch cu124)로 `--limit 2` 검증 후 전량 추출.

### 인프라 — 신규 GPU 서버(HP-Z4-DSWS) 드라이버 교체 ⛔ 블로커

- 기존 드라이버 **470 (CUDA 11.4)** 이 프로젝트 검증 환경(torch cu124, CUDA 12.4)과 불일치 → GPU 임베딩 불가.
- `nvidia-driver-470 → 535` 교체: apt로 누적 드라이버(440/450/460/470) purge 후 `nvidia-driver-535` 설치, **DKMS 빌드 성공**(535.230.02, 5.14-oem·5.15-generic 양쪽).
- ⛔ **재부팅 후 JupyterHub/SSH 등 서비스 미기동** → 원격 접속 불가(ping은 정상). 본체 콘솔 복구 대기(Chanran, 물리 접근 어려움).
- 복구법: `Ctrl+Alt+F3` → `sudo systemctl restart jupyterhub ssh`, 멈추면 GRUB 이전 커널(5.14-oem). DKMS 양쪽 빌드라 복구 가능, 디스크/데이터 안전.
- 주의: autoremove가 시스템 CUDA 11.0 툴킷도 제거함(팀 nvcc 영향 가능 — 필요 시 CUDA 12.x 재설치).

### 보류
- BIOP02-54 Jira/Confluence 등록은 임베딩 추출 완료 후 일괄 등록 예정.

---

## 2026-05-18 (Sprint 0)

### 완료한 작업

| JIRA | 태스크 | 커밋 |
|---|---|---|
| BIOP02-27 | tile_config.yaml + tile_wsi.py 구현 | bc637de |

**tile_config.yaml** (`agents/embedding/configs/`)
- 256×256 @ 20× (target_mpp=0.5), Otsu tissue_threshold=0.1, downsample_factor=64, per_patient_cap=5000

**tile_wsi.py** (`agents/embedding/scripts/`)
- openslide 기반, MPP 메타데이터로 20× 레벨 자동 선택 (없으면 L1 fallback)
- 순수 numpy/PIL Otsu 구현 (cv2 미사용)
- coords.npy (N, 2) int64 — level-0 픽셀 좌표 (openslide.read_region 규약)
- coords.json 메타데이터 companion 자동 저장
- 브랜치: `feat/BIOP02-27-kkkim-tile-wsi`
- 단위 테스트 통과 (Otsu, binary closing, cap 로직, config 파싱)

**보류 중**
- 실제 슬라이드(.svs)로 1-slide pilot 미실행 — `/data/raw/tcga/sample.svs` 존재 확인 후 서버에서 실행 필요
- GitHub push 대기 (초대 수락 후: `git push origin feat/BIOP02-27-kkkim-tile-wsi`)

---

## 2026-05-17 (Sprint 0)

### 완료한 작업

| JIRA | 태스크 | 커밋 |
|---|---|---|
| BIOP02-25 | HF 5종 모델 접근 권한 신청 및 전종 승인 | 13ce19d |
| BIOP02-26 | agents/embedding/setup.sh 작성 및 전 패키지 설치 확인 | e3badf7 |
| BIOP02-28 | agents/embedding/scripts/extract_dummy.py 작성 및 동작 확인 | e3badf7 |

**서버 환경 확인 완료 (BIOP02-25 포함)**
- /workspace/agents/embedding/ 생성
- nvidia-smi: A100 80GB PCIe, CUDA 12.4, 유휴 상태
- df -h: 1.9TB 총 용량, 27GB 사용 중

**HF 모델 승인 현황**
- UNI v1 (MahmoodLab/UNI) ✅
- CONCH (MahmoodLab/CONCH) ✅
- EXAONE Path 2.0 — 공개 모델 ✅
- Virchow2 (paige-ai/Virchow2) ✅
- UNI2-h (MahmoodLab/UNI2-h) ✅
- 상세 내용: guide/hf_model_access.md

**환경 설치 현황 (~/miniconda3)**
- torch 2.6.0+cu124, CUDA=True ✅
- pyvips 3.1.1 ✅
- timm, huggingface_hub, openslide, numpy, PIL ✅
- 주의: pyvips는 torch보다 먼저 import 필요 (libjpeg 충돌 방지)
- 주의: LD_LIBRARY_PATH=~/miniconda3/lib 우선 설정 필요

---

### 미완료 — 내일 할 것

| JIRA | 태스크 | 기한 | 비고 |
|---|---|---|---|
| BIOP02-27 | 1-slide pilot 실행 (서버에서) | 5/19 | push 후 서버 접속해서 실행 |
| — | schemas/hypothesis.schema.json v0.1 | 5/21 | gglee draft 받은 후 진행 |
| — | README.md (agents/embedding/) | BIOP02-26,27,28 완료 후 | 한꺼번에 작성 |

---

### 보류 중

- **GitHub push 대기**: 초대 재전송 수락 후 push 예정
  - 로컬 커밋 미push 상태 (main: 13ce19d, e3badf7 / feat 브랜치: bc637de)
  - 수락 후: `git push origin main` 이후 `git push origin feat/BIOP02-27-kkkim-tile-wsi`

---

## 내일 시작하는 법

```bash
# 1. 서버 접속
ssh -p 2202 kkkim@61.109.239.220

# 2. 프로젝트 이동
cd ~/project/BioProject02

# 3. braveji가 권한 줬으면 push 먼저
git push origin main

# 4. 브랜치 이동 (이미 생성됨)
git checkout feat/BIOP02-27-kkkim-tile-wsi

# 5. Claude Code 실행
claude
```

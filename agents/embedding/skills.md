# Embedding Agent — Skills & Work Log

**Author**: Ka-Kyung Kim (@kkkim) | **Last updated**: 2026-06-03

---

## Sprint 0 (5/12 – 5/22)

### BIOP02-25 — HuggingFace 모델 접근 권한
- UNI v1, CONCH, EXAONE Path 2.0, Virchow v1, UNI2-h 5종 동시 신청
- 전종 승인 완료

### BIOP02-26 — setup.sh 작성
- Ubuntu 22.04, Python 3.10, CUDA 12.4 환경 기준
- pyvips(conda-forge) → torch → openslide-python 순서 설치 (libjpeg 충돌 방지)
- 산출물: [`setup.sh`](setup.sh)

### BIOP02-27 — tile_config.yaml + tile_wsi.py 구현
- 256×256 @ 20× (target_mpp=0.5), Otsu tissue mask, per-patient cap 5000, seed=42
- **핵심 수정 (BIOP02-30 pilot 중 발견)**: 40× 슬라이드 MPP scale 보정 추가
  - actual_mpp=0.25 → scale=2.0 → read_size=512, resize to 256
  - coords.json에 scale/read_size 기록하여 extract_uni.py가 자동 반영
- 산출물: [`scripts/tile_wsi.py`](scripts/tile_wsi.py), [`configs/tile_config.yaml`](configs/tile_config.yaml)

### BIOP02-28 — extract_dummy.py 작성
- sjpark(Modeling Agent) 언블로킹용 랜덤 (N, 1024) float32 출력
- 산출물: [`scripts/extract_dummy.py`](scripts/extract_dummy.py)

### BIOP02-29 — schemas/hypothesis.schema.json v0.1
- claim_level, critic_status 필드 포함

### BIOP02-30 — 1-slide pilot 완료
- 슬라이드: TCGA-3C-AALI-01Z-00-DX1 (40×, 1.6GB)
- Tiling: 5.6초, 5000 tiles (cap), 원본 14198개
- UNI v1 추출: 125.6초, 5000×1024 float32, 20MB
- 산출물: `/workspace/data/cache/biop02/pilot_tiles/`, `pilot_embeddings/`

---

## Sprint 1 (5/22 – 6/05)

### BIOP02-37 — 전체 tiling (진행 중)
- jamie manifest 지연으로 직접 착수
- NAS(Synology QuickConnect) API로 파일 목록 조회 및 다운로드 스크립트 구현
- 임상 데이터(TCGA CDR clinical_patient_brca.txt) 직접 다운로드 및 분석
- 슬라이드 선별 전략: ER- 전수(228) + HER2+/ER+ + 나머지 ER+ → 500장 임상 기반 manifest
- 산출물: `/home/kkkim/data/tcga_brca_wsi_clinical_500.csv`

### 인프라 작업 (BIOP02-37 착수 준비)
- NAS Synology FolderSharing API 다운로드 스크립트: `/home/kkkim/data/download_wsi.py`
- openslide 파일 유효성 검증 포함 (손상 파일 자동 감지/재다운로드)
- Auto-tiling 스크립트: `/home/kkkim/data/run_tiling.py` (다운로드 완료 파일부터 순차 처리)

---

## 주요 경로

| 항목 | 경로 |
|---|---|
| WSI 다운로드 | `/home/kkkim/data/tcga_brca_wsi/` |
| Tiles | `/home/kkkim/data/tiles/` |
| 임상 데이터 | `/home/kkkim/data/clinical/clinical_patient_brca.txt` |
| 임상 기반 manifest (500장) | `/home/kkkim/data/tcga_brca_wsi_clinical_500.csv` |
| 다운로드 로그 | `/home/kkkim/data/logs/` |
| Pilot tiles | `/workspace/data/cache/biop02/pilot_tiles/` |
| Pilot embeddings | `/workspace/data/cache/biop02/pilot_embeddings/` |

## 의존성 체인

```
jamie: BIOP02-21 (manifest) ──→ kkkim: BIOP02-37 (tiling)
jamie: BIOP02-41 (split lock)    kkkim: BIOP02-38 (UNI 추출)
                                       ↓
                              sjpark: BIOP02-39 (MLP)
                              sjpark: BIOP02-40 (baseline)
```

# Runbook — CPTAC-BRCA 임베딩 추출 (IDC gs:// 스트리밍)  [BIOP02-54]

CPTAC-BRCA(외부 hold-out test 코호트)를 **NCI Imaging Data Commons(IDC)** 에서
받아 임베딩을 추출한다. TCGA(Synology NAS, `.svs`)와 달리 CPTAC-BRCA는 IDC 공개
버킷에 **DICOM-WSI**로 있고, 인증 없이 `idc-index`(내부적으로 s5cmd)로 받는다.

- Jira: **BIOP02-54** · 브랜치: `feat/BIOP02-54-kkkim-cptac-embed`
- 규모(실측 2026-06-24): **653 H&E 슬라이드 / 198 환자 / 총 ~120.2 GB** (Modality=SM)
- 정책: split_policy_v0 — CPTAC는 학습/튜닝 비노출, 외부 test 전량.

## 0. 사전 준비 (신규 GPU 서버 HP-Z4-DSWS)

> ⚠️ 이 서버는 2026-06-24 드라이버 470→535 교체 중 재부팅 후 다운됨. **서버 복구
> (nvidia-smi에 535/CUDA 12.2 확인) 후** 진행. 상세: biospin worklog 2026-06-24.

```bash
# 임베딩 env (torch cu124 등) — agents/embedding/setup.sh 기반, 경로 /home/pseudoer
bash agents/embedding/setup.sh
# IDC 다운로드 도구
~/miniconda3/bin/pip install idc-index        # s5cmd 번들, 인증 불필요
```

디스크: `/home` 288 GB 여유 → **스트리밍 삭제 방식**이면 peak 수~수십 GB로 충분
(전량 120 GB를 동시에 두지 않는다).

## 1. 인벤토리(매니페스트) 생성 — 이미 커밋됨

`agents/data/manifests/cptac_brca_idc_inventory.csv` (653행)는 macmini에서 생성·커밋됨.
재생성이 필요하면:
```bash
python agents/data/scripts/list_idc_cptac.py \
    --out agents/data/manifests/cptac_brca_idc_inventory.csv
```
컬럼: `slide_id, case_id, series_uid, series_description, series_size_mb, source_path`
(`source_path` = SeriesInstanceUID = IDC 다운로드 핸들)

## 2. 스트리밍 다운로드 → 타일 → 임베딩 → 삭제

```bash
export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}
export HF_TOKEN=hf_xxx        # UNI/CONCH 등 gated 모델

# 먼저 1~2장으로 파이프라인 검증 (--limit), DICOM 리더 확인 후 전량
python agents/data/scripts/stream_download_embed_idc.py \
    --manifest agents/data/manifests/cptac_brca_idc_inventory.csv \
    --config   agents/embedding/configs/tile_config.yaml \
    --cache-dir     /home/pseudoer/data/cache/biop02/cptac_raw \
    --tile-dir      /home/pseudoer/data/cache/biop02/cptac_tiles \
    --embedding-dir /home/pseudoer/data/embeddings/biop02/cptac/uni_v1 \
    --output-manifest /home/pseudoer/data/embeddings/biop02/cptac/stream_status.csv \
    --embedding-model uni \
    --limit 2                 # ← 검증되면 이 줄 제거하고 전량 실행
```

- **Resumable**: 임베딩이 이미 있으면 skip. 매 슬라이드 status를 `--output-manifest`에
  flush → 크래시해도 1장만 손실.
- **삭제 정책**: 임베딩 직후 DICOM 시리즈 폴더 삭제(`--keep-raw`로 보존 가능).
- 여러 모델 비교(UNI/CONCH/EXAONE) 시: 한 슬라이드에 필요한 모델을 다 뽑고 삭제하거나
  그 subset만 `--keep-raw`로 받아 재다운로드를 피한다.

## ⚠️ 검증 안 된 통합 지점 — DICOM-WSI 리더

CPTAC 시리즈는 `.svs`가 아니라 **DICOM-WSI**(폴더 안 여러 `.dcm`)다. `tile_wsi.py`는
OpenSlide로 여는데, **DICOM 읽기는 OpenSlide ≥ 4.0** 필요(`openslide-bin`이 4.x 제공).
어댑터는 시리즈 폴더에서 **가장 큰 `.dcm`(베이스 레벨)** 을 `--slide`로 넘긴다.

`--limit 2`로 먼저 확인할 것:
- tile_wsi가 좌표를 정상 생성하는가? (OpenSlide가 DICOM을 여는가)
- 안 되면: (a) `openslide-bin` 업그레이드, (b) 시리즈를 피라미드 TIFF로 변환
  (`wsidicom`/`dicom2tiff`) 후 타일링. → 필요 시 tile_wsi에 디렉토리 입력 지원 추가.

## 3. 산출물 / 후속

- 임베딩 `.npy` → `/home/pseudoer/data/embeddings/biop02/cptac/uni_v1/`
- `stream_status.csv` (provenance) → **git 커밋** (성공/실패 추적, 손실 방지)
- 후속: BIOP02-63 (UMAP sanity), 외부 검증(TCGA train → CPTAC test).

## 참고
- 도구: idc-index 0.12.3 (`IDCClient.sql_query`, `download_dicom_series`)
- 컬렉션 id: `cptac_brca` (소문자), Modality `SM`
- 데이터 원칙: 코드·manifest·status는 git 3중 보관, raw는 캐시(삭제) — agents/data/README.md

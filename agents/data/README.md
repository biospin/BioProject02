# agents/data — 데이터 관리 전략 & 출처 인덱스 (BIOP02-21)

GPU 서버 사용기한 만료로 서버에만 있던 **raw 슬라이드 / 1010장 manifest / 다운로드 스크립트 / TCGA CDR 임상파일이 전부 유실**된 사건(2026-06) 이후, 같은 일이 반복되지 않도록 만든 데이터 관리 원칙과 출처 인덱스다.

## 핵심 원칙 — "한쪽에만 저장되면 잃는다"

> 재현 가능한 것(코드·manifest·문서·소형 메타데이터)은 **무조건 git**.
> 큰 바이너리(raw `.svs`)는 git에 넣지 않되, **출처 + 재취득 레시피를 git에** 둔다.
> ephemeral 컴퓨트(GPU 서버)는 **캐시일 뿐**, 원본(source of truth)이 아니다.

| 자산 | git 커밋 | 보관 위치 | 유실 시 복구 |
|---|---|---|---|
| 다운로드/manifest/전처리 **스크립트** | ✅ 필수 | git | — |
| **manifest CSV** (슬라이드·라벨·split) | ✅ 필수 (수 MB) | `agents/data/manifests/` | 재생성 스크립트 |
| **출처/결정 문서** | ✅ 필수 | git + JIRA + Confluence (3중) | — |
| raw `.svs` 슬라이드 (~1.5 TB) | ❌ 금지 (대용량) | NAS 원본 (영구) | `list_nas_wsi.py` + 다운로드 스크립트 |
| TCGA CDR 임상파일 | ⚠️ 라이선스 확인 후 (공개) | git 또는 재다운로드 | 공개 URL (아래) |
| 임베딩 `.npy` | ❌ git 금지 | 영구 스토리지 + provenance 기록 | 재추출 (비쌈 → 백업 권장) |

**철칙:** 서버에서 무언가를 만들면 그날 안에 git 브랜치에 push 한다. JIRA 댓글에만 남기지 않는다.

## 데이터 출처 인덱스 (single source of truth)

### 1. Raw WSI — Synology NAS 공유 (유일한 영구 원본)
- 단축링크: `https://gofile.me/7uPdW/I1KGZnZWx` (= QuickConnect `radisen-nas2`, `sharing_id=I1KGZnZWx`, 폴더 `/wsi`)
- `gofile.me`는 Synology QuickConnect 단축 도메인 (일반 파일호스트 gofile.io 아님)
- 전체 1133장 DX 슬라이드. 다운로드 API 상세 = `guide/runbooks/download_wsi_from_synology_nas.md`
- ⚠️ 전체 raw 장기보관 금지 — manifest subset만 받아 tiling/임베딩 후 raw 삭제(LRU)

### 2. 임상 라벨 — TCGA CDR (공개)
- 파일: `clinical_patient_brca.txt` (TCGA biotab, `bcr_patient_barcode` 기준 1097명)
- 출처: GDC TCGA-BRCA Clinical (biotab) — `nationwidechildrens.org_clinical_patient_brca.txt`
- 대안: TCGA-CDR 통합표 `TCGA-CDR-SupplementalTableS1.xlsx` (Liu et al., 2018, Cell) / cBioPortal
- 라벨: `er_status_by_ihc`, `pr_status_by_ihc`, `her2_status_by_ihc` (PAM50는 별도 소스)

### 3. CPTAC-BRCA — IDC `gs://` 버킷 (외부 검증 코호트)
- 저장 형식: DICOM-WSI(`.svs` 아님), 컬렉션 `cptac_brca`, Modality `SM`. 공개 버킷 — 인증 불필요(`idc-index`/s5cmd).
- 규모(실측 2026-06-24): 653 H&E 슬라이드 / 198 환자 / ~120.2 GB.
- 버킷 접근방법 요약: `agents/data/cptac_idc_bucket_access_memo.md` (BIOP02-22)
- 임베딩 추출 전체 파이프라인: `guide/runbooks/download_cptac_from_idc.md` (BIOP02-54)
- 임상 라벨: `agents/data/cptac_labels_v1.md` (BIOP02-55)

## 스크립트 (재구축 파이프라인)

```bash
# 1) NAS /wsi 전수 목록 → 슬라이드 인벤토리 CSV
python agents/data/scripts/list_nas_wsi.py \
    --out agents/data/manifests/tcga_brca_nas_inventory.csv

# 2) 인벤토리 + 임상파일 → 최종 manifest (라벨·patient-level split 포함)
python agents/data/scripts/build_manifest.py \
    --inventory agents/data/manifests/tcga_brca_nas_inventory.csv \
    --clinical  /path/to/clinical_patient_brca.txt \
    --out       agents/data/manifests/tcga_brca_manifest.csv

# 3) manifest 기반 스트리밍: NAS 다운로드 → tiling → 임베딩 → raw 삭제 (한 장씩, 디스크 최소)
python agents/data/scripts/stream_download_embed.py \
    --manifest agents/data/manifests/tcga_brca_manifest.csv \
    --config   agents/embedding/configs/tile_config.yaml \
    --cache-dir /data/cache/biop02/raw \
    --tile-dir  /data/cache/biop02/tiles \
    --embedding-dir /data/embeddings/biop02/uni_v1 \
    --output-manifest /data/embeddings/biop02/stream_status.csv \
    --embedding-model uni        # conch/exaone는 feat/BIOP02-31 머지 후 사용 가능
```

스트리밍 원칙: raw `.svs`는 임베딩 추출 직후 삭제 → 동시 디스크 사용 수십 GB,
1010장 처리 후 남는 건 임베딩 ~20GB. resumable(임베딩 존재 시 skip), 슬라이드마다
상태 CSV flush(크래시 시 최대 1장만 손실).

생성된 `*_inventory.csv` / `*_manifest.csv`는 **반드시 git 커밋**한다 (수 MB, 손실 방지 핵심).

## 관련 이슈
- BIOP02-21: TCGA-BRCA manifest / subset
- BIOP02-82: raw cache 대용량 저장소 결정 (DoD 미완 — 공용 볼륨 미확정)
- BIOP02-23: kkkim tiling/임베딩

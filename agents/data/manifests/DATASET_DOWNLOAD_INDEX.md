# 데이터셋 재다운로드 인덱스 (BIOP02-146 GPU 반납 대비)

> 작성 2026-08-19 (kkkim). **목적**: raw WSI는 백업하지 않고(용량 大, 재다운로드 가능) 재다운로드에 필요한 **file-id·case-id 리스트를 git으로 영구 보존**한다. 서버 반납 후 RunPod 등 새 환경에서 이 리스트만으로 raw를 복구하고 임베딩을 재추출할 수 있다.
> 원칙(CLAUDE.md): 영구 보존 = manifest·coords·embeddings·logs. raw `.svs`는 스트리밍→추출→삭제(단, 프로젝트 기간 한정 보관 예외).

## 재다운로드 방법 (GDC REST — gdc-client pip 불가 우회, memory `infra_gdc_api_download`)

```bash
# GDC file-id 리스트(manifest의 id 열) → REST /data 로 스트리밍 다운로드
# GDC `in` 연산자 500 버그 → `=`+`and` 우회. 진단슬라이드 = 파일명 -DX.
python agents/data/scripts/stream_download_embed.py --manifest <manifest.csv> --out ~/data/<dataset>
```

## 데이터셋별 리스트 (커버리지 실측 2026-08-19)

| 데이터셋 | 기대 규모 | 다운로드 리스트 (git) | 행수 | 비고 |
|---|---|---|---|---|
| **TCGA-BRCA** (앵커) | ~1010 DX-slide | `agents/data/manifests/tcga_brca_manifest.csv` | 1010 | case→slide 정본 |
| TCGA-BRCA (GDC file-id) | 전 slide 파일 | `agents/data/manifests/tcga_brca_gdc_manifest_v0.1.tsv` | 3112 | **raw 재다운로드용 file-id** (2026-08-19 git 편입) |
| TCGA-BRCA (slide meta) | — | `agents/data/manifests/tcga_brca_slide_manifest_v0.1.csv` | 3112 | slide 메타 (2026-08-19 git 편입) |
| **폐 LUNG_NSCLC** | 1026 | `experiments/crosscancer/LUNG_NSCLC/full/embedding_manifest_lung_nsclc_uni.csv` | 1052 | GDC manifest도 `LUNG_NSCLC/pilot/gdc_manifest.txt` |
| **대장 COLORECTAL** | 523 | `experiments/crosscancer/COLORECTAL/full/embedding_manifest_colorectal_uni.csv` | 622 | |
| **위 GASTRIC_STAD** | 439 | `experiments/crosscancer/GASTRIC_STAD/full/embedding_manifest_gastric_stad_uni.csv` | 442 | |
| **두경부 HEADNECK_HNSC** | 468 | `experiments/crosscancer/HEADNECK_HNSC/full/embedding_manifest_headneck_hnsc_uni.csv` | 472 | HPV 헤드라인 코호트 |
| UCEC (탐색적) | 사전등록 밖 | `experiments/crosscancer/UCEC/full/embedding_manifest_ucec_uni.csv` | 548 | 확증 집계 제외 |
| **CPTAC-BRCA** (외부검증) | ~120 환자 | `experiments/kkkim/20260709_cptac_official_join/embedding_manifest_cptac_uni_v1.csv` | 653 | IDC `gs://` bucket, `stream_download_embed_idc.py` |
| **Yale** (pCR 앵커) | HER2 pCR | `experiments/kkkim/20260717_her2_outcome_anchor/yale_download.csv` | 276 | TCIA, `yale_manifest.csv` 병행 |

**전 데이터셋 재다운로드 리스트 git 보존 확인.** raw가 사라져도 이 인덱스 → 원 데이터 복구 → 임베딩 재추출(§EMBEDDING_INVENTORY의 GPU 비용) 경로가 열려 있다.

## 미해결 (전송 전 확인)
- 폐/대장/위/두경부 embedding manifest 행수가 기대 슬라이드수보다 소폭 많음 = 다중FM(UNI/Virchow2/UNI2-h) 다중 파일 또는 slide 중복 — 재추출 시 dedup 규칙(case_id→fold)은 `split_policy_v0_folds.json` 기준.
- `/workspace crosscancer/`(2588 npy)와 per-cohort 디렉토리 중복 여부는 임베딩 전송 전 대조.

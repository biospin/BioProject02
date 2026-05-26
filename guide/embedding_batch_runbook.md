# Embedding batch runbook — manifest 확정 전 준비안

이 문서는 Paper A용 TCGA-BRCA subset manifest가 확정되면 바로 batch tiling과 UNI embedding 추출을 실행하기 위한 준비안이다.

## 1. Input manifest 형식

필수 컬럼은 `slide_path` 하나다. 가능하면 downstream 추적을 위해 `slide_id`, `case_id`, `file_id`도 함께 넣는다.

```csv
slide_id,case_id,file_id,slide_path
TCGA-EXAMPLE-01Z-00-DX1,TCGA-EXAMPLE,00000000-0000-0000-0000-000000000000,/workspace/data/cache/biop02/wsi/TCGA-EXAMPLE-01Z-00-DX1.svs
```

템플릿 파일: `agents/embedding/configs/batch_manifest_template.csv`

현재 subset 규모는 약 150장 확정이 아니라 300~500장 제안 상태다. 전체 TCGA WSI 다운로드는 하지 않고, 최종 확정된 subset manifest에 포함된 slide만 처리한다.

## 2. Manifest preflight

manifest가 오면 먼저 컬럼, 중복 slide, 파일 경로, 예상 runtime/storage를 확인한다. `--check_exists`는 WSI가 실제로 마운트된 서버에서만 붙인다.

```bash
cd ~/project/BioProject02

~/miniconda3/bin/python agents/embedding/scripts/validate_batch_manifest.py \
  --manifest /workspace/data/cache/biop02/manifests/tcga_brca_subset.csv \
  --check_exists
```

확인 기준:

- `slide_path`는 필수 컬럼이다. `slide_id`, `case_id`, `file_id`는 downstream 추적을 위해 권장한다.
- 중복 `slide_id` 또는 중복 `slide_path`가 있으면 실행 전에 jamie/data 담당자에게 manifest 수정을 요청한다.
- 150장 기준 예상 UNI runtime은 약 5.5시간, embedding 용량은 약 2.9 GiB다. 300~500장으로 늘어나면 약 10.9~18.2시간, 5.7~9.5 GiB를 예상한다.

## 3. Dry run

preflight가 통과하면 dry run으로 command와 output manifest 구조를 확인한다.

```bash
cd ~/project/BioProject02
export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

~/miniconda3/bin/python agents/embedding/scripts/run_batch_embedding.py \
  --manifest /workspace/data/cache/biop02/manifests/tcga_brca_subset.csv \
  --config agents/embedding/configs/tile_config.yaml \
  --tile_dir /workspace/data/cache/biop02/tiles \
  --embedding_dir /data/embeddings/biop02/uni_v1 \
  --output_manifest /data/embeddings/biop02/embedding_manifest.csv \
  --embedding_model uni \
  --dry_run
```

## 4. Batch tiling + UNI embedding

GPU 슬롯을 `#biop02-alerts`에 예약한 뒤 실행한다.

```bash
~/miniconda3/bin/python agents/embedding/scripts/run_batch_embedding.py \
  --manifest /workspace/data/cache/biop02/manifests/tcga_brca_subset.csv \
  --config agents/embedding/configs/tile_config.yaml \
  --tile_dir /workspace/data/cache/biop02/tiles \
  --embedding_dir /data/embeddings/biop02/uni_v1 \
  --output_manifest /data/embeddings/biop02/embedding_manifest.csv \
  --embedding_model uni \
  --batch_size 64 \
  --device cuda
```

중간 실패가 나도 `embedding_manifest.csv`는 처리된 slide까지 계속 갱신된다. 같은 명령을 다시 실행하면 이미 존재하는 output은 건너뛴다. 강제로 다시 만들 때만 `--overwrite`를 사용한다.

## 5. Output manifest 컬럼

`run_batch_embedding.py`는 downstream 전달용 CSV를 만든다.

| 컬럼 | 의미 |
|---|---|
| `slide_id` | slide 식별자. manifest에 없으면 `slide_path` stem 사용 |
| `case_id` | 환자/case 식별자 |
| `file_id` | GDC file id 또는 원천 file id |
| `slide_path` | 입력 WSI 경로 |
| `coords_path` | `coords.npy` 경로 |
| `coords_shape` | 예: `5000x2` |
| `coords_json_path` | tiling metadata JSON 경로 |
| `embedding_model` | `uni`, `dummy`, `none` |
| `embedding_path` | embedding `.npy` 경로 |
| `embedding_shape` | 예: `5000x1024` |
| `n_tiles` | cap 적용 후 tile 수 |
| `n_before_cap` | cap 적용 전 후보 tile 수 |
| `capped` | per-patient cap 적용 여부 |
| `tiling_seconds` | slide별 tiling wall-clock |
| `embedding_seconds` | slide별 embedding wall-clock |
| `status` | `done`, `tiled`, `tile_failed`, `embedding_failed`, `error` |
| `error` | 실패 사유 |

## 6. 실행 전/후 handoff 체크리스트

실행 전:

- jamie/data 담당자: 최종 subset manifest의 `slide_path`, `case_id`, `file_id` 확정
- braveji/ykji: `/data/embeddings/biop02/uni_v1` 사용 가능 여부 확인
- kkkim: manifest preflight + dry run 통과 확인
- kkkim: Slack `#biop02-alerts`에 GPU 슬롯 예약 메시지 남김
- sjpark: `embedding_manifest.csv` + slide별 `.npy` 형식이 모델링 입력으로 충분한지 확인

실행 후 sjpark에게 전달할 항목:

- `/data/embeddings/biop02/embedding_manifest.csv`
- slide별 `*_uni_embeddings.npy` 경로와 shape (`embedding_manifest.csv`의 `embedding_path`, `embedding_shape`)
- 실패 slide 목록 (`status != done`)과 재시도 여부
- 실행 시점 git commit hash

1-slide pilot 기준 tiling 5.6초, UNI 추출 125.6초였다. 150장은 계산만 약 5.5시간이고, 300~500장은 약 10.9~18.2시간이다. WSI I/O와 재시도 시간을 고려해 여유 슬롯을 잡는다.

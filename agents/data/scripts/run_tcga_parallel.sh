#!/usr/bin/env bash
# TCGA-BRCA UNI 임베딩 — 3워커 병렬 실행(GPU1). 샤딩으로 가속(코드 무수정).
# 인벤토리를 3등분해 stream_download_embed.py 3개를 동시 실행한다.
# 한 워커가 임베딩(GPU) 도는 동안 다른 워커가 다운로드(NAS) → GPU가 안 놂.
#
# 사용:
#   bash agents/data/scripts/run_tcga_parallel.sh
#
# - 이미 한 슬라이드는 자동 skip(resumable). 중복 실행 방지 가드 있음.
# - 진행: cat ~/data/embeddings/biop02/tcga/stream_status_shard*.csv | grep -c ',done,'
set -e
cd "$(dirname "$0")/../../.."                      # repo root
M="agents/data/manifests/tcga_brca_nas_inventory.csv"
DATA="$HOME/data"
PY="$HOME/miniconda3/bin/python"
K=3

if [ ! -f "$M" ]; then
  echo "ERROR: 인벤토리 없음: $M"
  echo "  먼저 받기: env -u LD_LIBRARY_PATH git checkout origin/feat/BIOP02-tcga-reembed-kkkim -- $M"
  exit 1
fi

mkdir -p "$DATA/logs" "$DATA/cache/biop02" "$DATA/embeddings/biop02/tcga/uni_v1"

echo "[1/2] 인벤토리 ${K}분할"
for i in $(seq 0 $((K-1))); do
  head -1 "$M" > "$DATA/tcga_shard$i.csv"
  awk -v k="$K" -v r="$i" 'NR>1 && (NR-2)%k==r' "$M" >> "$DATA/tcga_shard$i.csv"
done
wc -l "$DATA"/tcga_shard*.csv

echo "[2/2] ${K}워커 실행 (GPU1) — 이미 도는 샤드는 skip(죽은 것만 재시작)"
export LD_LIBRARY_PATH="$HOME/miniconda3/lib:${LD_LIBRARY_PATH:-}"
for i in $(seq 0 $((K-1))); do
  if pgrep -f "tcga_shard$i.csv" >/dev/null; then
    echo "  shard $i 이미 실행중 — skip"
    continue
  fi
  CUDA_VISIBLE_DEVICES=1 nohup "$PY" agents/data/scripts/stream_download_embed.py \
    --manifest "$DATA/tcga_shard$i.csv" \
    --config agents/embedding/configs/tile_config.yaml \
    --cache-dir "$DATA/cache/biop02/tcga_raw" \
    --tile-dir "$DATA/cache/biop02/tcga_tiles" \
    --embedding-dir "$DATA/embeddings/biop02/tcga/uni_v1" \
    --output-manifest "$DATA/embeddings/biop02/tcga/stream_status_shard$i.csv" \
    --embedding-model uni \
    >> "$DATA/logs/tcga_shard$i.log" 2>&1 &
done

sleep 3
N=$(pgrep -af stream_download_embed | grep -c tcga_shard || true)
echo "실행됨. tcga_shard 워커 수: $N  (${K}이면 정상)"

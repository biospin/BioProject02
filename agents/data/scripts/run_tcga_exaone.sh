#!/usr/bin/env bash
# TCGA-BRCA EXAONE Path 2.0 임베딩 — 슬라이드 단위 추출 (BIOP02-48/-38).
# EXAONE은 .svs 경로를 직접 받아 내부 타일링/정규화 → coords 불필요.
# GPU 3장(0,1,2)에 3-way 샤딩. 이미 추출된 슬라이드는 자동 skip(resumable).
#
# 사용: bash agents/data/scripts/run_tcga_exaone.sh
set -euo pipefail

PY=/home/kkkim/miniconda3/bin/python3
REPO_ROOT=/home/kkkim/project/BioProject02
SCRIPT="$REPO_ROOT/agents/embedding/scripts/extract_exaone.py"
EXAONE_REPO="$REPO_ROOT/agents/embedding/exaone_path2/repo"
SLIDES_DIR=/home/kkkim/data/tcga_brca_wsi
OUT_DIR=/home/kkkim/data/embeddings/biop02/tcga/exaone_v2
LOG_DIR="$REPO_ROOT/experiments/kkkim/logs"
NUM_SHARDS=3

mkdir -p "$OUT_DIR" "$LOG_DIR"

# triton/inductor 캐시를 exec 가능한 홈 경로로 (/tmp noexec 회피)
export TORCHINDUCTOR_CACHE_DIR=$HOME/.cache/torchinductor
export TRITON_CACHE_DIR=$HOME/.cache/triton
mkdir -p "$TORCHINDUCTOR_CACHE_DIR" "$TRITON_CACHE_DIR"

echo "[run] slides=$SLIDES_DIR out=$OUT_DIR shards=$NUM_SHARDS"
for SHARD in 0 1 2; do
  LOG="$LOG_DIR/exaone_shard${SHARD}.log"
  echo "[run] shard $SHARD -> cuda:$SHARD  log=$LOG"
  CUDA_VISIBLE_DEVICES=$SHARD nohup "$PY" "$SCRIPT" \
      --slides-dir "$SLIDES_DIR" \
      --repo-dir "$EXAONE_REPO" \
      --out-dir "$OUT_DIR" \
      --shard-idx "$SHARD" --num-shards "$NUM_SHARDS" \
      > "$LOG" 2>&1 &
  echo "[run] shard $SHARD PID=$!"
done
wait
echo "[run] all shards finished"

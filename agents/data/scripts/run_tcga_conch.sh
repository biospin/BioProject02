#!/usr/bin/env bash
# TCGA-BRCA CONCH 임베딩 — 로컬 타일에서 추출 (BIOP02-48).
# coords/슬라이드가 모두 로컬 SSD에 있으므로 다운로드/staging 불필요(--no_stage).
# cuda:0 에서 K워커 병렬(샤딩). 이미 한 슬라이드는 자동 skip(resumable).
#
# 사용: bash agents/data/scripts/run_tcga_conch.sh
# 진행: ls ~/data/embeddings/biop02/tcga/conch_v1/*_conch_embeddings.npy | wc -l   # 목표 1010
set -e
TILES="$HOME/data/tiles"
OUT="$HOME/data/embeddings/biop02/tcga/conch_v1"
LOGS="$HOME/data/logs"
PY="$HOME/miniconda3/bin/python"
SCRIPT="$HOME/project/BioProject02/agents/embedding/scripts/extract_conch_fast.py"
DEV="cuda:0"
K=3
NW=4

mkdir -p "$OUT" "$LOGS"
export LD_LIBRARY_PATH="$HOME/miniconda3/lib:${LD_LIBRARY_PATH:-}"

# 샤드 파일 생성 (coords .npy 목록을 K등분)
ls "$TILES"/*_coords.npy | sort > "$LOGS/conch_all_coords.txt"
TOTAL=$(wc -l < "$LOGS/conch_all_coords.txt")
echo "총 coords: $TOTAL → ${K}샤드"
for i in $(seq 0 $((K-1))); do
  awk -v k="$K" -v r="$i" 'NR%k==r' "$LOGS/conch_all_coords.txt" > "$LOGS/conch_shard$i.txt"
  echo "  shard$i: $(wc -l < "$LOGS/conch_shard$i.txt")"
done

echo "[실행] ${K}워커 ($DEV, no_stage) — 죽은 샤드만 재시작"
for i in $(seq 0 $((K-1))); do
  if pgrep -f "conch_shard$i.txt" >/dev/null; then
    echo "  shard$i 이미 실행중 — skip"; continue
  fi
  nohup "$PY" "$SCRIPT" \
    --shard-file "$LOGS/conch_shard$i.txt" \
    --out_dir "$OUT" \
    --device "$DEV" \
    --num_workers "$NW" \
    --batch_size 64 \
    --no_stage \
    >> "$LOGS/conch_shard$i.log" 2>&1 &
  echo "  shard$i 시작 PID $!  로그: $LOGS/conch_shard$i.log"
done
sleep 3
echo "실행 중 워커: $(pgrep -fc conch_shard || true)  (${K}이면 정상)"

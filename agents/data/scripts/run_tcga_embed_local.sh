#!/usr/bin/env bash
# TCGA-BRCA UNI 임베딩 — 기존 타일(/home/kkkim/data/tiles/) 활용, 재다운로드 없음
# 3 GPU 병렬 (GPU 0/1/2), 이미 완료된 슬라이드 자동 skip.
#
# 사용:
#   export HF_TOKEN=hf_xxx
#   export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}
#   bash agents/data/scripts/run_tcga_embed_local.sh
#
# 진행 확인:
#   ls ~/data/embeddings/biop02/tcga/uni_v1/ | wc -l   # 완료 수 (목표: 1010)
#   cat ~/data/logs/tcga_embed_gpu*.log | grep -c "Saved"
set -euo pipefail
cd "$(dirname "$0")/../../.."   # repo root

TILE_DIR="$HOME/data/tiles"
EMB_DIR="$HOME/data/embeddings/biop02/tcga/uni_v1"
LOG_DIR="$HOME/data/logs"
PY="$HOME/miniconda3/bin/python"
EXTRACTOR="agents/embedding/scripts/extract_uni.py"
K=3

mkdir -p "$EMB_DIR" "$LOG_DIR"

# coords.npy 목록 → 3분할
mapfile -t ALL_COORDS < <(ls "$TILE_DIR"/*_coords.npy 2>/dev/null | sort)
N="${#ALL_COORDS[@]}"
echo "총 coords: $N (목표: 1010)"

echo "[1/2] ${K}분할 파일 생성"
# 기존 shard 파일 초기화
for i in $(seq 0 $((K-1))); do
  echo "" > "$LOG_DIR/tcga_shard_coords_$i.txt"
done

for idx in "${!ALL_COORDS[@]}"; do
  shard=$((idx % K))
  echo "${ALL_COORDS[$idx]}" >> "$LOG_DIR/tcga_shard_coords_$shard.txt"
done
for i in $(seq 0 $((K-1))); do
  cnt=$(grep -c . "$LOG_DIR/tcga_shard_coords_$i.txt" 2>/dev/null || echo 0)
  echo "  shard $i: $cnt slides"
done

echo "[2/2] ${K}워커 실행 — 이미 실행 중인 shard는 skip"
export LD_LIBRARY_PATH="$HOME/miniconda3/lib:${LD_LIBRARY_PATH:-}"

for i in $(seq 0 $((K-1))); do
  PIDFILE="$LOG_DIR/tcga_embed_gpu$i.pid"
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
    echo "  GPU $i 워커(PID $(cat "$PIDFILE")) 이미 실행 중 — skip"
    continue
  fi

  # 각 shard를 별도 Python 프로세스로 실행
  nohup "$PY" - <<PYEOF >> "$LOG_DIR/tcga_embed_gpu$i.log" 2>&1 &
import subprocess, sys, os
from pathlib import Path

shard_file = "$LOG_DIR/tcga_shard_coords_$i.txt"
emb_dir = "$EMB_DIR"
extractor = "$EXTRACTOR"
gpu = "cuda:$i"

with open(shard_file) as f:
    coords_list = [l.strip() for l in f if l.strip() and l.strip().endswith('.npy')]

done = 0
skipped = 0
failed = 0

for coords_path in coords_list:
    import json
    meta_path = coords_path.replace('_coords.npy', '_coords.json')
    try:
        with open(meta_path) as mf:
            meta = json.load(mf)
        slide_name = Path(meta['slide']).stem
        emb_file = Path(emb_dir) / f"{slide_name}_uni_embeddings.npy"
        if emb_file.exists():
            skipped += 1
            print(f"[skip] {slide_name}", flush=True)
            continue
        print(f"[run ] {slide_name} → {gpu}", flush=True)
        result = subprocess.run(
            [sys.executable, extractor, "--coords", coords_path, "--out_dir", emb_dir,
             "--batch_size", "64", "--device", gpu],
            check=False
        )
        if result.returncode == 0:
            done += 1
        else:
            failed += 1
            print(f"[fail] {slide_name} rc={result.returncode}", flush=True)
    except Exception as e:
        failed += 1
        print(f"[error] {coords_path}: {e}", flush=True)

print(f"GPU $i 완료: done={done} skipped={skipped} failed={failed}", flush=True)
PYEOF

  echo $! > "$LOG_DIR/tcga_embed_gpu$i.pid"
  echo "  GPU $i 시작됨 (PID $!), 로그: $LOG_DIR/tcga_embed_gpu$i.log"
done

sleep 2
RUNNING=$(pgrep -f "tcga_embed_gpu" | wc -l || echo 0)
echo ""
echo "실행 중 워커: $RUNNING / $K"
echo "진행 확인: watch -n 30 \"ls $EMB_DIR | wc -l\""
echo "로그 확인: tail -f $LOG_DIR/tcga_embed_gpu{0,1,2}.log"

#!/bin/bash
# STAD 완료 시 GPU2 전용 HNSC 핵 워커(shard_hnscGPU2_*)를 정리 → 마스터 sh_embed.py가
# HNSC를 GPU 0/1/2 균등 배분으로 자동 재기동. (마스터는 STAD→HNSC 순차 내장.)
CC=/home/kkkim/project/BioProject02/experiments/crosscancer
LOG=$CC/GPU_REBALANCE_WATCHER.log
echo "[$(date '+%F %T')] watcher armed: STAD 완료 대기 (현재 emb=$(ls $CC/GASTRIC_STAD/full/embeddings/*_uni_embeddings.npy 2>/dev/null|wc -l)/442)" >> $LOG
while true; do
  ndone=$(ls $CC/GASTRIC_STAD/full/embeddings/*_uni_embeddings.npy 2>/dev/null | wc -l)
  if [ -f "$CC/GASTRIC_STAD/full/CANCER.done" ] || [ "$ndone" -ge 442 ]; then
    echo "[$(date '+%F %T')] STAD 완료 감지 (emb=$ndone). GPU2 전용 HNSC 핵 워커 정리." >> $LOG
    pkill -f "shard_hnscGPU2_" 2>/dev/null
    pkill -f "sh_embed_hnsc_gpu2.py" 2>/dev/null
    sleep 25
    echo "[$(date '+%F %T')] 정리 후 HNSC 워커 목록:" >> $LOG
    pgrep -af "run_embed_crosscancer.py --worker --cancer HEADNECK_HNSC" >> $LOG 2>/dev/null
    echo "[$(date '+%F %T')] GPU 상태:" >> $LOG
    nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader >> $LOG 2>/dev/null
    echo "[$(date '+%F %T')] watcher 종료 — 마스터가 HNSC를 3-GPU 균등으로 진행." >> $LOG
    break
  fi
  sleep 120
done

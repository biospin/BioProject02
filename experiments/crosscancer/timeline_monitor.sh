#!/usr/bin/env bash
# STAD MIL 결과 대기 + 25분 주기 재점검. 트리거 시 exit→메인 재호출.
cd /home/kkkim/project/BioProject02/experiments/crosscancer
start=$(date +%s)
while true; do
  [ -f GASTRIC_STAD/full/LAW_TEST.md ] && { echo "TRIGGER=stad_law_done t=$(date +%H:%M) S=$(ls GASTRIC_STAD/full/embeddings/*.npy 2>/dev/null|wc -l)"; exit 0; }
  [ $(( $(date +%s) - start )) -ge 1500 ] && { echo "TRIGGER=routine t=$(date +%H:%M) S=$(ls GASTRIC_STAD/full/embeddings/*.npy 2>/dev/null|wc -l)"; exit 0; }
  sleep 300
done

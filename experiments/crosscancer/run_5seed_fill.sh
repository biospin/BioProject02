#!/bin/bash
cd /home/kkkim/project/BioProject02/experiments/crosscancer
PY=/opt/envs/spatialpatho/bin/python
log(){ echo "[$(date '+%H:%M:%S')] $*" >> /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/5seed_fill.log; }
run(){ # cancer fm gpu
  log "▶ $1 / $2 (gpu $3) 시작"
  $PY sh_robustness_5seed.py --cancer $1 --fm $2 --device cuda:$3 >> /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/5seed_fill.log 2>&1
  log "  $1/$2 종료 rc=$?"
}
# GPU0: 대장 virchow2 → 폐 uni2h
( run COLORECTAL virchow2 0; run LUNG_NSCLC uni2h 0; touch /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/GPU0_DONE ) &
# GPU1: 대장 uni2h
( run COLORECTAL uni2h 1; touch /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/GPU1_DONE ) &
# GPU2: 폐 virchow2
( run LUNG_NSCLC virchow2 2; touch /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/GPU2_DONE ) &
wait
log "=== 전체 5seed fill 완료 ==="
touch /tmp/claude-10005/-home-kkkim-project-BioProject02/1e7a8c39-a076-48e5-ae4f-2bbb9917be89/scratchpad/ALL_5SEED_FILL_DONE

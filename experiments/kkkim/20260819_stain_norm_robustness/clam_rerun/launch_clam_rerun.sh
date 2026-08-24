#!/bin/bash
cd /home/kkkim/project/BioProject02
PY=/opt/envs/spatialpatho/bin/python
D=experiments/kkkim/20260819_stain_norm_robustness/clam_rerun
LOG=$D/clam_rerun.log
: > "$LOG"
for task in er_status her2_status pam50; do
  echo "===== $task (stain-norm) $(date -Iseconds) =====" >> "$LOG"
  $PY agents/modeling/scripts/train_mil.py --config $D/stainnorm_${task}.yaml --tag uni_stainnorm >> "$LOG" 2>&1
  echo "----- $task done -----" >> "$LOG"
done
echo "ALL_DONE $(date -Iseconds)" > $D/clam_rerun.done

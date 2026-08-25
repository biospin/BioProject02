#!/bin/bash
cd /home/kkkim/project/BioProject02/experiments/kkkim/20260820_shuffle_null_20seed
PY=/opt/envs/spatialpatho/bin/python
for fmg in uni:0 uni2h:1 virchow2:2; do
  f=${fmg%:*}; g=${fmg#*:}
  nohup $PY run_20seed.py --seeds 20 --fms $f --endpoints hpv_pos,egfr_amp --cancer HEADNECK_HNSC --device cuda:$g > f_${f}.out 2>&1 < /dev/null &
done
wait
echo "ALL_DONE $(date -Iseconds)" > launch_20seed.done

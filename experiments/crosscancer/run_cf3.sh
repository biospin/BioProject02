#!/bin/bash
# BIOP02-96 #3 counterfactual (attention-faithfulness) 전체 3암종 detached 러너.
# 세션이 끊겨도 완주하도록 setsid+nohup로 기동. 로그·done sentinel 남김.
cd /home/kkkim/project/BioProject02
source ~/miniconda3/etc/profile.d/conda.sh
LOG=experiments/crosscancer/CF3_HEARTBEAT.log
OUT=experiments/kkkim/20260716_crosscancer_subcheck_owner/counterfactual_faithfulness.json
DONE=experiments/crosscancer/CF3_DONE.json
rm -f "$DONE"
echo "[$(date '+%F %T')] CF3 시작 (cuda:1, LUNG/GASTRIC/HEADNECK, 재현게이트+top-att제거)" > "$LOG"
conda run -n spatialpatho python experiments/crosscancer/counterfactual_attention_crosscancer.py \
    --device cuda:1 --out "$OUT" >> "$LOG" 2>&1
RC=$?
echo "[$(date '+%F %T')] CF3 종료 rc=$RC" >> "$LOG"
python3 - "$RC" "$OUT" "$DONE" <<'PY'
import json, os, sys, datetime
rc, out, done = int(sys.argv[1]), sys.argv[2], sys.argv[3]
json.dump({"done": True, "rc": rc, "out": out, "out_exists": os.path.exists(out)},
          open(done, "w"), ensure_ascii=False)
PY

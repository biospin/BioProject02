#!/usr/bin/env bash
# 자동 리뷰 주기 스캔 (cron 스캐폴드 — 스터디 결정 후 활성화).
# config.cron.enabled=true 여야 실동작(오케스트레이터가 dry-run 가드).
# 활성화(예): crontab -e →  */30 * * * * /home/kkkim/project/BioProject02/agents/critic/cron_auto_review.sh
set -euo pipefail
ROOT="/home/kkkim/project/BioProject02"
PY="/home/kkkim/miniconda3/bin/python3"
CFG="$ROOT/agents/critic/auto_review_config.json"
LOG="$ROOT/agents/critic/cron_auto_review.log"

cd "$ROOT"
# cron.enabled 확인 (jq 없이 grep)
if ! grep -q '"enabled": true' <("$PY" -c "import json;print(json.dumps(json.load(open('$CFG'))['cron']))" 2>/dev/null); then
  echo "[$(date '+%F %T')] cron.enabled=false — 스킵" >> "$LOG"; exit 0
fi
# config.cron.scan_paths 각각 스캔 → gate + 큐 적재 + 알림
for p in $("$PY" -c "import json;print(' '.join(json.load(open('$CFG'))['cron']['scan_paths']))"); do
  echo "[$(date '+%F %T')] scan $p" >> "$LOG"
  "$PY" agents/critic/auto_review_orchestrator.py --scan "$p" >> "$LOG" 2>&1 || true
done
# AI 리뷰 대기 큐에 요청 발행(세션/OpenClaw가 drain하여 실제 에이전트 실행)
"$PY" agents/critic/auto_review_orchestrator.py --drain-queue >> "$LOG" 2>&1 || true

#!/usr/bin/env bash
# watchdog.sh — 다중 FM 임베딩 master와 재학습 러너가 죽으면 되살린다.
# 시스템 crontab에서 10분마다 호출. 세션이 끊겨도 시스템 cron이 유지되므로 주말 내내 감시.
# 재기동 안전성 근거:
#   - run_multifm.py master: idempotent(코호트별 GDC 재쿼리 + 완료 슬라이드 건너뜀). 완료 마커 MASTER_DONE.
#   - multifm_retrain_watcher.py: idempotent(결과 있으면 skip). 완료 마커 MULTIFM_RETRAIN_DONE.
# 둘 다 로그는 append(>>)로 이어 붙여 "완료" 판단 근거를 지우지 않는다.
set -u
PY=/opt/envs/spatialpatho/bin/python
EMB_DIR=/home/kkkim/project/BioProject02/experiments/kkkim/20260717_multifm_robustness
RT_DIR=/home/kkkim/project/BioProject02/experiments/crosscancer
WLOG="$EMB_DIR/watchdog.log"
ts() { date "+%F %T"; }
log() { echo "[$(ts)] $*" >> "$WLOG"; }

# --- 1) 임베딩 master ---
if [ -f "$EMB_DIR/MASTER_DONE" ]; then
    :  # 전체 완료 — 아무것도 안 함
elif pgrep -af "run_multifm.py" | grep -v -- '--worker' | grep -q run_multifm.py; then
    :  # master 살아있음
else
    log "⚠️ 임베딩 master 죽음 감지 — 재기동(이어받기, log append)"
    cd "$EMB_DIR" && setsid "$PY" run_multifm.py >> master.log 2>&1 < /dev/null &
    log "  relaunched master pid=$!"
fi

# --- 2) 재학습 러너 ---
if [ -f "$RT_DIR/MULTIFM_RETRAIN_DONE" ]; then
    :  # 완료
elif pgrep -f "multifm_retrain_watcher.py" >/dev/null; then
    :  # 살아있음
else
    log "⚠️ 재학습 러너 죽음 감지 — 재기동(idempotent)"
    cd "$RT_DIR" && setsid "$PY" multifm_retrain_watcher.py >> multifm_retrain.log 2>&1 < /dev/null &
    log "  relaunched retrain watcher pid=$!"
fi

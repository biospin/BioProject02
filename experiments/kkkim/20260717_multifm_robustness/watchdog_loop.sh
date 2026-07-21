#!/usr/bin/env bash
# watchdog_loop.sh — cron 없는 컨테이너용. watchdog.sh를 10분마다 무한 호출.
# setsid로 detached 실행(PPID=1)해 세션이 끊겨도 생존. 재기동: 아래 launch 커맨드 재실행.
# 한계: 이 루프 자체가 죽으면(리부트/OOM) 되살릴 상위 감시자 없음(cron 부재) — 재접속 시 생존 확인 권장.
set -u
DIR=/home/kkkim/project/BioProject02/experiments/kkkim/20260717_multifm_robustness
while true; do
    bash "$DIR/watchdog.sh"
    # 임베딩·재학습 둘 다 완료면 루프 종료(자원 정리)
    if [ -f "$DIR/MASTER_DONE" ] && [ -f /home/kkkim/project/BioProject02/experiments/crosscancer/MULTIFM_RETRAIN_DONE ]; then
        echo "[$(date '+%F %T')] 둘 다 완료 — watchdog_loop 종료" >> "$DIR/watchdog.log"
        break
    fi
    sleep 600
done

#!/bin/bash
# 147(염색정규화) 완료를 기다렸다가 shuffle-null 20-seed를 착수한다.
# 이유: 147이 CPU 27/32코어(Macenko)를 점유 → shuffle-null 학습의 데이터로딩 CPU가 굶어
#       병렬 실행 시 둘 다 기어감. 147 완료(전체 CPU 확보) 후 실행이 훨씬 빠르고 깨끗.
# 서버 cron 부재 → setsid 자기루프(memory infra_no_cron_use_detached_loop).
set -u
HERE="/home/kkkim/project/BioProject02/experiments/kkkim/20260820_shuffle_null_20seed"
S147="/home/kkkim/project/BioProject02/experiments/kkkim/20260819_stain_norm_robustness"
PY=/opt/envs/spatialpatho/bin/python
cd "$HERE"
log(){ echo "[$(date '+%m-%d %H:%M')] $*" >> watcher.log; }

log "watcher 시작 — 147 완료 대기"
while true; do
  d=0
  for s in 0 1 2; do [ -f "$S147/queue_shard${s}.status" ] && d=$((d+1)); done
  [ "$d" -eq 3 ] && { log "147 3샤드 완료 감지"; break; }
  sleep 600
done

# 검증: real-only 스모크(전체 CPU 확보돼 빠름). 출력 나오면 본실행.
log "검증 스모크(uni hpv_pos real-only)"
$PY run_20seed.py --seeds 1 --fms uni --endpoints hpv_pos --device cuda:0 >> watcher.log 2>&1
if ! ls "$HERE"/headneck_hnsc_1seed_uni.json >/dev/null 2>&1; then
  log "❌ 스모크 출력 없음 — 배선 문제. 본실행 보류(사람 확인 필요)."; exit 1
fi
log "✅ 스모크 통과 — 20-seed 본실행(3 FM × 3 GPU 병렬)"

$PY run_20seed.py --seeds 20 --fms uni      --endpoints hpv_pos,egfr_amp --device cuda:0 > f_uni.out      2>&1 &
$PY run_20seed.py --seeds 20 --fms uni2h    --endpoints hpv_pos,egfr_amp --device cuda:1 > f_uni2h.out    2>&1 &
$PY run_20seed.py --seeds 20 --fms virchow2 --endpoints hpv_pos,egfr_amp --device cuda:2 > f_virchow2.out 2>&1 &
wait
log "20-seed 본실행 완료 — 출력 headneck_hnsc_20seed_{uni,uni2h,virchow2}.json"
echo "DONE $(date -Iseconds)" > watcher.status

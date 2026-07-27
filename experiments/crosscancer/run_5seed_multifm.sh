#!/usr/bin/env bash
# 신형 FM 5-seed 우연배제 — 헤드라인(두경부 HPV) 먼저, 나머지 순차.
# 폐 임베딩과 GPU를 공유하므로 순차 실행(동시 다발 금지).
set -u
PY=/opt/envs/spatialpatho/bin/python
HERE=/home/kkkim/project/BioProject02/experiments/crosscancer
cd "$HERE"
log(){ echo "[$(date '+%F %T')] $*" >> "$HERE/5seed_multifm.log"; }
log "=== 시작: 신형 FM 5-seed ==="
# 1순위: 두경부 HPV(유일한 검정력 있는 CONFIRM) — 두 FM
for fm in virchow2 uni2h; do
  log "▶ HEADNECK_HNSC / $fm / hpv_pos"
  $PY sh_robustness_5seed.py --cancer HEADNECK_HNSC --fm $fm --endpoints hpv_pos \
      --device cuda:0 --out "$HERE/HEADNECK_HNSC/full/shuffle_null_robustness_${fm}_hpv.json" >> "$HERE/5seed_multifm.log" 2>&1
  log "  done $fm hpv (rc=$?)"
done
# 2순위: 두경부 전 endpoint, 위, 대장
for fm in virchow2 uni2h; do
  for c in HEADNECK_HNSC GASTRIC_STAD COLORECTAL; do
    log "▶ $c / $fm (전 endpoint)"
    $PY sh_robustness_5seed.py --cancer $c --fm $fm --device cuda:0 >> "$HERE/5seed_multifm.log" 2>&1
    log "  done $c/$fm (rc=$?)"
  done
done
touch "$HERE/FIVESEED_MULTIFM_DONE"
log "=== 전체 완료 ==="

#!/usr/bin/env bash
# Yale HER2 앵커 — 다운로드(PathDB HTTP) → 타일 → UNI 임베딩. detached, 재개가능, 앵커우선.
# 실행: setsid bash experiments/kkkim/20260717_yale_anchor/yale_pipeline.sh </dev/null >>LOG 2>&1 &
set -uo pipefail   # -e 없음: 개별 슬라이드 실패해도 계속
cd "$(git rev-parse --show-toplevel)"
DIR=experiments/kkkim/20260717_her2_outcome_anchor
RAW=/home/kkkim/data/yale_raw
EMB=/workspace/data/cache/biop02/yale/uni_v1
TILE=/workspace/data/cache/biop02/yale/coords
CFG=agents/embedding/configs/tile_config.yaml
OUTMAN=/workspace/data/cache/biop02/yale/embedding_manifest_yale_uni.csv
LOG=$DIR/pipeline.log
mkdir -p "$RAW" "$EMB" "$TILE"
log(){ echo "[$(date '+%F %T')] $*" >> "$LOG"; }

download_cohort(){  # $1=cohort
  local coh="$1" n=0 ok=0
  while IFS=, read -r imageid cohort url local; do
    [[ "$imageid" == "imageid" || "$cohort" != "$coh" ]] && continue
    n=$((n+1))
    [[ -f "$EMB/${imageid}_uni_embeddings.npy" ]] && { ok=$((ok+1)); continue; }   # 이미 임베딩됨
    if [[ -f "$local" && $(stat -c%s "$local" 2>/dev/null || echo 0) -gt 1000000 ]]; then ok=$((ok+1)); continue; fi
    if wget -q -c --timeout=120 --tries=5 --waitretry=15 --read-timeout=180 -O "$local" "$url" 2>>"$LOG"; then
      sz=$(stat -c%s "$local" 2>/dev/null || echo 0)
      if [[ $sz -gt 1000000 ]]; then ok=$((ok+1)); log "dl ok $imageid ($sz b)"; else log "dl ⚠ small $imageid ($sz)"; rm -f "$local"; fi
    else log "dl ✗ fail $imageid"; fi
  done < "$DIR/yale_download.csv"
  log "download[$coh]: $ok/$n present"
}

embed_cohort(){  # $1=cohort
  local coh="$1"
  local man="$DIR/_man_${coh}.csv" out="$DIR/_out_${coh}.csv"
  head -1 "$DIR/yale_manifest.csv" > "$man"
  awk -F, -v c="$coh" 'NR>1 && $4==c {print}' "$DIR/yale_manifest.csv" | while IFS=, read -r sp sid cid c2; do
    [[ -f "$sp" ]] && echo "$sp,$sid,$cid,$c2"
  done >> "$man"
  local nn=$(( $(wc -l < "$man") - 1 ))
  log "embed[$coh]: $nn slides present → run_batch_embedding"
  /opt/envs/spatialpatho/bin/python agents/embedding/scripts/run_batch_embedding.py \
    --manifest "$man" --config "$CFG" --tile_dir "$TILE" --embedding_dir "$EMB" \
    --output_manifest "$out" --embedding_model uni --device cuda >> "$LOG" 2>&1
  log "embed[$coh]: rc=$?"
}

log "=== Yale pipeline start (PID $$) ==="
# 1) 앵커 우선 — trastuzumab 85 완주
download_cohort Yale_trastuzumab_response_cohort
embed_cohort    Yale_trastuzumab_response_cohort
log "★ anchor cohort (trastuzumab 85) 완료"
# 2) HER2 cohort 191
download_cohort Yale_HER2_cohort
embed_cohort    Yale_HER2_cohort
# 통합 출력 매니페스트
{ cat "$DIR/_out_Yale_trastuzumab_response_cohort.csv" 2>/dev/null; tail -n +2 "$DIR/_out_Yale_HER2_cohort.csv" 2>/dev/null; } > "$OUTMAN" 2>/dev/null
nemb=$(ls "$EMB"/*.npy 2>/dev/null | wc -l)
echo "{\"done\": true, \"embeddings\": $nemb, \"emb_dir\": \"$EMB\", \"manifest\": \"$OUTMAN\"}" > "$DIR/YALE_PIPELINE_DONE.json"
log "=== ALL DONE: $nemb embeddings → $OUTMAN ==="

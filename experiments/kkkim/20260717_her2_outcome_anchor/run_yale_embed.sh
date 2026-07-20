#!/usr/bin/env bash
# Yale HER2 앵커 — 타일 + UNI 임베딩 (detached, 끊겨도 생존)
# 선행: Yale SVS가 ~/data/yale_raw/ 에 있고, yale_manifest.csv(slide_path 컬럼)가 준비돼야 함.
#       (다운로드는 이 스크립트 밖. RESUME_YALE.md의 옵션 참조 — TCIA Aspera/PathDB.)
# 실행: bash experiments/kkkim/20260717_yale_anchor/run_yale_embed.sh
# setsid + </dev/null: SSH 끊겨도(SIGHUP) 계속. run_batch_embedding.py는 파일 존재 시 skip(재개 가능).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

MANIFEST="experiments/kkkim/20260717_yale_anchor/yale_manifest.csv"
CONFIG="agents/embedding/configs/tile_config.yaml"
TILE_DIR="/workspace/data/cache/biop02/yale/coords"
EMB_DIR="/workspace/data/cache/biop02/yale/uni_v1"
OUT_MANIFEST="/workspace/data/cache/biop02/yale/embedding_manifest_yale_uni.csv"
LOG="experiments/kkkim/20260717_yale_anchor/embed.log"
DONE="experiments/kkkim/20260717_yale_anchor/YALE_EMBED_DONE.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "❌ 매니페스트 없음: $MANIFEST  (yale_manifest.csv에 slide_path 컬럼 필요 — RESUME_YALE.md 참조)"; exit 1
fi
mkdir -p "$TILE_DIR" "$EMB_DIR"

echo "▶ Yale UNI 임베딩 시작 (detached). 로그: $LOG"
setsid conda run -p /opt/envs/spatialpatho python agents/embedding/scripts/run_batch_embedding.py \
  --manifest "$MANIFEST" \
  --config "$CONFIG" \
  --tile_dir "$TILE_DIR" \
  --embedding_dir "$EMB_DIR" \
  --output_manifest "$OUT_MANIFEST" \
  --embedding_model uni \
  --device cuda \
  </dev/null >"$LOG" 2>&1 &
PID=$!
echo "PID: $PID  |  tail -f $LOG"
# 완료 감시(별도 detached): 출력 매니페스트 행수 == 입력 행수면 sentinel 기록
setsid bash -c "
  while kill -0 $PID 2>/dev/null; do sleep 30; done
  nin=\$(( \$(wc -l < '$MANIFEST') - 1 ))
  nout=0; [[ -f '$OUT_MANIFEST' ]] && nout=\$(( \$(wc -l < '$OUT_MANIFEST') - 1 ))
  echo '{\"done\": true, \"n_in\": '\$nin', \"n_out\": '\$nout', \"emb_dir\": \"$EMB_DIR\"}' > '$DONE'
" </dev/null >>"$LOG" 2>&1 &
echo "완료 감시 PID: $!  →  $DONE 생성 시 종료"

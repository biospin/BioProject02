#!/usr/bin/env bash
# BIOP02-80 A4 — Yale pCR 층화 검정 실행 스크립트
# /workspace 루트에서 실행: bash agents/therapeutic_evidence/scripts/run_yale_pcr.sh
set -euo pipefail

PYTHON=/opt/envs/spatialpatho/bin/python
OUT_DIR=/workspace/experiments/jhans/yale_pcr_a4_v1

# ── A3 완료 후 아래 경로를 sjpark 산출물로 업데이트 ──────────────────────────
# A3 output: sjpark가 frozen HER2 CLAM 모델을 Yale 임베딩에 적용한 결과 CSV
# 필수 컬럼: case_id, axis_score (HER2 확률)
# 선택 컬럼: her2_prob (DeLong baseline용; axis_score와 동일하거나 별도)
AXIS_SCORES="/workspace/experiments/sjpark/yale_axis_scores.csv"  # TODO: A3 완료 후 갱신

# Yale pCR 라벨 CSV (responder=1 / non=0)
# 컬럼: case_id, pcr
# 소스: TCIA HER2-TUMOR-ROIS 임상 XLSX → 변환
PCR_LABELS="/workspace/data/cache/biop02/yale/yale_pcr_labels.csv"  # TODO: 경로 확인

mkdir -p "$OUT_DIR"

$PYTHON agents/therapeutic_evidence/scripts/yale_pcr_stratification.py \
  --axis_scores  "$AXIS_SCORES" \
  --pcr_labels   "$PCR_LABELS" \
  --patient_col  case_id \
  --score_col    axis_score \
  --baseline_col her2_prob \
  --n_bootstrap  2000 \
  --out_dir      "$OUT_DIR" \
  2>&1 | tee "$OUT_DIR/run.log"

echo "Done → $OUT_DIR"

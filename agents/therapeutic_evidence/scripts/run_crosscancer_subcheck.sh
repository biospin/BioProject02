#!/usr/bin/env bash
set -euo pipefail

PYTHON=/opt/envs/spatialpatho/bin/python
OUT_DIR=/workspace/experiments/jhans/crosscancer_subcheck_v1

mkdir -p "$OUT_DIR"

$PYTHON agents/therapeutic_evidence/scripts/crosscancer_subcheck.py \
  --frozen_maps \
    experiments/crosscancer/COLORECTAL/frozen_map.json \
    experiments/crosscancer/LUNG_NSCLC/frozen_map.json \
  --gdsc /workspace/data/BIOP02-52/GDSC2_fitted_dose_response_27Oct23.xlsx \
  --model_csv /workspace/data/BIOP02-52/Model.csv \
  --prism_bowel "/workspace/data/BIOP02-96/PRISM_Repurposing_Secondary_(AUC)_subsetted_Bowel.csv" \
  --prism_lung  "/workspace/data/BIOP02-96/PRISM_Repurposing_Secondary_(AUC)_subsetted_Lung.csv" \
  --out_dir "$OUT_DIR" \
  2>&1 | tee "$OUT_DIR/run.log"

echo "Done. Results -> $OUT_DIR"

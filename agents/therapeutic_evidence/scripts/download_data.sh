#!/bin/bash
# BIOP02-52 v0.2 — DepMap PRISM 24Q2 + GDSC 8.5 데이터 다운로드
# 실행 위치: 서버 /workspace/agents/therapeutic_evidence/
# 사용법: bash download_data.sh

set -e
DATA_DIR="$(dirname "$0")/../../../experiments/jhans/20260702_consistency/data"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"
echo "== 다운로드 위치: $DATA_DIR =="

# ── DepMap 24Q2 ──────────────────────────────────────────────
echo "[1/5] Model.csv (DepMap 24Q2)"
if [ ! -f "Model.csv" ]; then
  wget -q --show-progress \
    "https://figshare.com/ndownloader/files/47503420" \
    -O Model.csv
else echo "  이미 존재, skip"; fi

echo "[2/5] PRISM Repurposing Compound List"
if [ ! -f "Repurposing_Public_24Q2_Extended_Secondary_Compound_List.csv" ]; then
  wget -q --show-progress \
    "https://figshare.com/ndownloader/files/47503426" \
    -O Repurposing_Public_24Q2_Extended_Secondary_Compound_List.csv
else echo "  이미 존재, skip"; fi

echo "[3/5] PRISM Repurposing Secondary Matrix (대용량 ~2GB)"
if [ ! -f "Repurposing_Public_24Q2_Extended_Secondary_Data_Matrix.csv" ]; then
  wget -q --show-progress \
    "https://figshare.com/ndownloader/files/47503429" \
    -O Repurposing_Public_24Q2_Extended_Secondary_Data_Matrix.csv
else echo "  이미 존재, skip"; fi

# ── GDSC Release 8.5 ─────────────────────────────────────────
echo "[4/5] GDSC2 Fitted Dose Response"
if [ ! -f "GDSC2_fitted_dose_response_25Feb2025.xlsx" ]; then
  wget -q --show-progress \
    "https://cancerrxgene.org/downloads/anova/GDSC2_fitted_dose_response_25Feb2025.xlsx" \
    -O GDSC2_fitted_dose_response_25Feb2025.xlsx
else echo "  이미 존재, skip"; fi

echo "[5/5] GDSC Screened Compounds rel 8.5"
if [ ! -f "screened_compounds_rel_8.5.csv" ]; then
  wget -q --show-progress \
    "https://cancerrxgene.org/downloads/anova/screened_compounds_rel_8.5.csv" \
    -O screened_compounds_rel_8.5.csv
else echo "  이미 존재, skip"; fi

echo ""
echo "== 다운로드 완료 =="
ls -lh "$DATA_DIR"

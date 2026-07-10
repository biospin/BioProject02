#!/bin/bash
# BIOP02-52 v0.2 — GDSC2 데이터 다운로드
# 실행 위치: /workspace/agents/therapeutic_evidence/
# 사용법: bash download_data.sh 2>&1 | tee download.log
#
# 주의:
#   Model.csv       — DepMap 26Q1, figshare WAF 차단 → 브라우저 다운로드 후 scp 수동 업로드
#   PRISM subsetted — DepMap Custom Downloads (BRCA_Breast 컨텍스트 선택) 후 scp 수동 업로드

set -e
DATA_DIR="/workspace/data/BIOP02-52"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"
echo "== 다운로드 위치: $DATA_DIR =="

# ── GDSC2 fitted dose response (Cell Model Passports) ─────────
echo "[1/2] GDSC2 Fitted Dose Response (27Oct23)"
if [ ! -f "GDSC2_fitted_dose_response_27Oct23.xlsx" ]; then
  wget -q --show-progress \
    "https://cmp.cog.sanger.ac.uk/download/GDSC2_fitted_dose_response_27Oct23.xlsx" \
    -O GDSC2_fitted_dose_response_27Oct23.xlsx
else echo "  이미 존재, skip"; fi

# ── GDSC Screened Compounds ───────────────────────────────────
echo "[2/2] GDSC Screened Compounds rel 8.5"
if [ ! -f "screened_compounds_rel_8.5.csv" ]; then
  wget -q --show-progress \
    "https://cmp.cog.sanger.ac.uk/download/screened_compounds_rel_8.5.csv" \
    -O screened_compounds_rel_8.5.csv
else echo "  이미 존재, skip"; fi

echo ""
echo "== 자동 다운로드 완료 =="
echo ""
echo "수동 업로드 필요 파일:"
echo "  Model.csv       → https://depmap.org/portal/download/all/ (DepMap 26Q1)"
echo "  PRISM subsetted → https://depmap.org/portal/download/custom/"
echo "                    (Model Context: BRCA_Breast, 약 378KB)"
echo ""
ls -lh "$DATA_DIR"

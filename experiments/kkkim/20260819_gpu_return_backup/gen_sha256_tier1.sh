#!/bin/bash
cd "$(dirname "$0")"
OUT=sha256_tier1_uniqueonly.txt
: > "$OUT"
echo "# 유일본 tier1 sha256 (다중FM BRCA + CONCH) — $(date -Iseconds)" >> "$OUT"
find /home/kkkim/data/multifm_archive/brca -name "*.npy" -type f 2>/dev/null | sort | while read f; do sha256sum "$f"; done >> "$OUT"
find /home/kkkim/data/embeddings/biop02/tcga/conch_v1 -name "*.npy" -type f 2>/dev/null | sort | while read f; do sha256sum "$f"; done >> "$OUT"
N=$(grep -c '^[0-9a-f]' "$OUT")
echo "DONE lines=$N $(date -Iseconds)" > sha256_tier1.status

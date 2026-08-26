#!/bin/bash
cd "$(dirname "$0")"
OUT=sha256_stainnorm_uni_v1.txt
: > "$OUT"
echo "# uni_stainnorm_v1 sha256 (147 산출, 백업 무결성) — $(date -Iseconds)" >> "$OUT"
find /home/kkkim/data/embeddings/biop02/tcga/uni_stainnorm_v1 -name "*.npy" -type f 2>/dev/null | sort | while read f; do sha256sum "$f"; done >> "$OUT"
echo "DONE lines=$(grep -c '^[0-9a-f]' "$OUT") $(date -Iseconds)" > sha256_stainnorm.status

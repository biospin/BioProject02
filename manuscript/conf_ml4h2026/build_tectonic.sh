#!/usr/bin/env bash
# ML4H 2026 축약본을 공식 jmlr(pmlr) 클래스로 빌드한다.
#
# 전제: tectonic 정적 바이너리 하나. brew·sudo·texlive 설치 불필요.
#   curl -sL -o tectonic.tar.gz \
#     "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-apple-darwin.tar.gz"
#   tar -xzf tectonic.tar.gz && mkdir -p ~/bin && mv tectonic ~/bin/ && chmod +x ~/bin/tectonic
#   (리눅스는 자산 이름의 x86_64-apple-darwin 을 x86_64-unknown-linux-musl 로 바꾼다)
#
# 첫 실행은 번들에서 클래스·폰트를 받아오느라 수십 초 걸리고, 이후는 캐시로 빠르다.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TECTONIC="${TECTONIC:-$HOME/bin/tectonic}"
SRC="$HERE/CONF_ML4H2026_BIOP02.tex"
OUT="${1:-$HERE/build}"

command -v "$TECTONIC" >/dev/null 2>&1 || { echo "tectonic 없음: $TECTONIC"; exit 1; }
[ -f "$SRC" ] || { echo "원본 .tex 없음: $SRC"; exit 1; }

mkdir -p "$OUT"
# 프리앰블 교체: 원본의 \maketitle 이후 본문만 떼어 공식 프리앰블에 붙인다.
python3 - "$SRC" "$HERE/preamble_ml4h_jmlr.tex" "$OUT/main.tex" <<'PY'
import sys
src, pre, out = sys.argv[1], sys.argv[2], sys.argv[3]
body = open(src, encoding="utf-8").read()
body = body.split("\\begin{document}", 1)[1].split("\\maketitle", 1)[1]
preamble = open(pre, encoding="utf-8").read()
# 프리앰블 파일의 주석 머리는 그대로 둬도 무방하다.
open(out, "w", encoding="utf-8").write(preamble + body)
print(f"[build] {out} 생성")
PY

# 그림을 빌드 폴더로
[ -d "$HERE/figures" ] && cp -R "$HERE/figures" "$OUT/" || true

cd "$OUT"
"$TECTONIC" -X compile main.tex
echo "[build] $OUT/main.pdf"

# 쪽수와 본문/부록 경계를 바로 보고한다 (pdftotext 있으면)
if command -v pdftotext >/dev/null 2>&1; then
  python3 - "$OUT/main.pdf" <<'PY'
import subprocess, sys
p = sys.argv[1]
pages = subprocess.run(["pdftotext","-layout",p,"-"],capture_output=True,text=True).stdout.split("\f")
valid = [x for x in pages if x.strip()]
print(f"[build] 총 {len(valid)}쪽")
for i, pg in enumerate(pages, 1):
    if "Appendix A" in pg:
        lines = pg.split("\n")
        tot = len([l for l in lines if l.strip()])
        idx = next(j for j, l in enumerate(lines) if "Appendix A" in l)
        before = len([l for l in lines[:idx] if l.strip()])
        print(f"[build] 본문 = {i-1 + before/tot:.2f}쪽  (Appendix A 가 p{i} 의 {round(before/tot*100)}% 지점)")
        print("[build] ML4H Findings 본문 제한 = 4쪽 (참고문헌·부록 제외)")
        break
PY
fi

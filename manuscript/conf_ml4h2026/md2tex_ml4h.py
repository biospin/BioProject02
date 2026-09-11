#!/usr/bin/env python3
"""CONF_ML4H2026_BIOP02.md -> LaTeX. 기계 변환이라 수치가 흔들리지 않는다.

ML4H 2026 공식 템플릿은 Overleaf 전용이라 여기서는 받을 수 없다.
그래서 본문을 표준 article 로 감싸 두고, 제출 시 \documentclass 부터
\begin{document} 직전까지를 ML4H 템플릿 프리앰블로 교체하면 된다.
본문 명령은 템플릿에 의존하지 않는 것만 쓴다.
"""
import re, sys

SRC = sys.argv[1]
OUT = sys.argv[2]

UNI = {
    "–": "--", "—": "---", "×": r"$\times$", "≈": r"$\approx$", "≫": r"$\gg$",
    "≤": r"$\le$", "≥": r"$\ge$", "−": "$-$", "±": r"$\pm$", "µ": r"$\mu$",
    "μ": r"$\mu$", "é": r"\'e", "→": r"$\rightarrow$", "↔": r"$\leftrightarrow$", "’": "'", "‘": "'",
    "“": "``", "”": "''", "…": r"\ldots{}", "\u00a0": "~", "§": r"\S{}",
}
SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#",
           "_": r"\_", "$": r"\$", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
           "^": r"\textasciicircum{}"}

def esc(s):
    out, i = [], 0
    while i < len(s):
        # `code` 는 \texttt 로
        if s[i] == "`":
            j = s.find("`", i + 1)
            if j > 0:
                inner = s[i+1:j]
                for k, v in SPECIAL.items():
                    inner = inner.replace(k, v)
                for k, v in UNI.items():
                    inner = inner.replace(k, v)
                out.append(r"\texttt{" + inner + "}"); i = j + 1; continue
        out.append(s[i]); i += 1
    t = "".join(out)
    # 이미 만든 명령을 다시 이스케이프하지 않도록 플레이스홀더로 보호
    guards = []
    def guard(m):
        guards.append(m.group(0)); return "\x00%d\x00" % (len(guards) - 1)
    t = re.sub(r"\\texttt\{[^}]*\}", guard, t)
    for k, v in SPECIAL.items():
        t = t.replace(k, v)
    for k, v in UNI.items():
        t = t.replace(k, v)
    t = re.sub(r"\x00(\d+)\x00", lambda m: guards[int(m.group(1))], t)
    # **굵게** -> \textbf
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    return t

lines = open(SRC, encoding="utf-8").read().splitlines()
# CONDENSATION LOG 이후는 제출본에 넣지 않는다
cut = next((n for n, l in enumerate(lines) if "CONDENSATION LOG" in l), len(lines))
lines = lines[:cut]

body, i, title = [], 0, ""
while i < len(lines):
    l = lines[i]
    if l.startswith("# ") and not title:
        title = esc(l[2:].strip()); i += 1; continue
    m = re.match(r"^(#{2,4})\s+(.*)", l)
    if m:
        lvl = len(m.group(1)); txt = esc(m.group(2).strip())
        if txt.lower() == "abstract":
            body.append(r"\begin{abstract}"); i += 1
            while i < len(lines) and not lines[i].startswith("#"):
                if lines[i].strip(): body.append(esc(lines[i].strip()))
                i += 1
            body.append(r"\end{abstract}"); continue
        cmd = {2: "section", 3: "subsection", 4: "subsubsection"}[lvl]
        body.append("\\%s*{%s}" % (cmd, txt)); i += 1; continue
    # 그림: **Figure 1 (main text)** ... `figures/xxx.pdf` 형태를 float 으로
    mfig = re.match(r"^\*\*(Figure\s+\d+)[^*]*\*\*\s*(.*)", l)
    if mfig and "figures/" in "\n".join(lines[i:i+3]):
        cap_lines = [mfig.group(2)]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].startswith(("#", "|", "**")):
            cap_lines.append(lines[j].strip()); j += 1
        cap = " ".join(cap_lines)
        mpath = re.search(r"`(figures/[^`]+\.pdf)`", cap)
        if mpath:
            path = mpath.group(1)
            cap = re.sub(r"\(?\s*`figures/[^`]+\.pdf`\s*\)?", "", cap).strip()
            body.append(r"\begin{figure}[t]\centering")
            body.append(r"\includegraphics[width=\columnwidth]{%s}" % path)
            body.append(r"\caption{%s}" % esc(cap))
            body.append(r"\end{figure}")
            i = j; continue

    if l.startswith("|"):                       # 표
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append(lines[i]); i += 1
        cells = [r.strip().strip("|").split("|") for r in rows]
        cells = [c for c in cells if not re.match(r"^[\s\-:|]+$", "|".join(c))]
        ncol = max(len(c) for c in cells)
        body.append(r"\begin{table}[ht]\centering\footnotesize")
        body.append(r"\begin{tabular}{" + "l" * ncol + "}\\hline")
        for n, c in enumerate(cells):
            c = [esc(x.strip()) for x in c] + [""] * (ncol - len(c))
            body.append(" & ".join(c) + r" \\" + (r"\hline" if n == 0 else ""))
        body.append(r"\hline\end{tabular}\end{table}")
        continue
    if l.strip().startswith("<!--"):
        while i < len(lines) and "-->" not in lines[i]: i += 1
        i += 1; continue
    if not l.strip():
        body.append(""); i += 1; continue
    body.append(esc(l.strip())); i += 1

PRE = r"""%% ML4H 2026 Findings track submission (BIOP02)
%% !! 제출 전 교체 필요 !!
%% ML4H 2026 공식 템플릿은 Overleaf 전용이라 이 파일에 포함할 수 없다.
%%   https://www.overleaf.com/latex/templates/machine-learning-for-health-ml4h-2026-template/sqgwhtyswgcy
%% 아래 \documentclass ~ \begin{document} 구간을 템플릿 프리앰블로 교체하고
%% 본문은 그대로 옮기면 된다. 본문은 템플릿 의존 명령을 쓰지 않는다.
%% 이중맹검: 저자·소속·사사는 camera-ready 에만 넣는다.
\documentclass[10pt]{article}
\usepackage[a4paper,margin=2.2cm]{geometry}
\usepackage{graphicx}\usepackage{amsmath,amssymb}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[hidelinks]{hyperref}\usepackage{caption}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\title{%s}
\author{}\date{}
\begin{document}
\maketitle
""" % title

open(OUT, "w", encoding="utf-8").write(PRE + "\n".join(body) + "\n\\end{document}\n")
print("제목: %s" % title)
print("본문 줄: %d" % len(body))

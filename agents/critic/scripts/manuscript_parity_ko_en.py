#!/usr/bin/env python3
"""
국/영문 정합 검증 (BIOP02, Week 19 결정) — 같은 원고의 KO ↔ EN 대조.

국문으로 먼저 쓰고 영문화하는 워크플로에서, 두 판본이 조용히 어긋나는 것을 막는다.
산문(문장)은 당연히 다르므로 대조하지 않는다. **판본이 같은 사실을 담는지**만 본다:
  1) heading 구조(개수·순서)
  2) 수치(전항) — 숫자로 적힌 값(AUROC·CI·표본수·%·p 등)이 양쪽에 다 있는가
  3) 인용([Author YEAR]) 개수·집합
  4) 표(개수·행수)
`check_number_drift.py`와 같은 철학: **판정하지 않는다** — 어느 쪽이 맞는지는 사람이 정한다.
어긋난 자리만 나열한다.

사용법:
    # 명시 쌍
    python3 agents/critic/scripts/manuscript_parity_ko_en.py --ko A_ko.md --en A_en.md
    # 섹션 디렉터리 자동 짝짓기 (<name>_ko.md ↔ <name>_en.md, 또는 sections_ko/ ↔ sections_en/)
    python3 agents/critic/scripts/manuscript_parity_ko_en.py --sections manuscript/sections
    # CI 차단용: 불일치 하나라도 있으면 exit 1
    python3 ... --strict

수치·인용만 대조하므로 국문이 숫자를 한글로 적은 것("다섯 암종")은 무시된다(=DATA 값만).
"""
import argparse, os, re, sys, glob

# ── 추출기 ───────────────────────────────────────────────────────────────

# 숫자 토큰: 소수/정수/퍼센트/과학표기. 반드시 '숫자'를 포함해야 함(한글 수사 제외).
NUM_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?:[eE][+-]?\d+)?%?")
# 인용: [Author 2024], [Kather 2019·2020], [Coudray 2018, ...]
CITE_RE = re.compile(r"\[[^\]\n]*\b(19|20)\d{2}[a-z]?\b[^\]\n]*\]")
CITE_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}[a-z]?\b")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$", re.M)
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)
SEP_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")  # |---|---| 구분행


def norm_num(tok):
    """0.9590 == 0.959, 26% -> ('26', pct). 표본수/AUROC 반올림 정합용."""
    pct = tok.endswith("%")
    t = tok[:-1] if pct else tok
    try:
        f = float(t)
    except ValueError:
        return tok
    # 정수는 정수로, 소수는 4dp로(반올림 오차 흡수)
    v = str(int(f)) if f == int(f) and "." not in t and "e" not in t.lower() else f"{round(f, 4):g}"
    return v + ("%" if pct else "")


def strip_code_and_paths(text):
    """코드블록·인라인코드·파일경로(파일:줄)의 숫자는 데이터 수치가 아니므로 제거."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)                     # 인라인 코드
    text = re.sub(r"[\w./-]+\.(?:py|md|json|csv|yaml|yml)\S*", " ", text)  # 경로
    text = re.sub(r"\bBIOP0\d-\d+\b", " ", text)               # 티켓번호
    return text


def extract(text):
    body = strip_code_and_paths(text)
    nums = {}
    for m in NUM_RE.findall(body):
        nums[norm_num(m)] = nums.get(norm_num(m), 0) + 1
    cites = {}
    for c in CITE_RE.finditer(body):
        for y in CITE_YEAR_RE.findall(c.group(0)):
            cites[y] = cites.get(y, 0) + 1
    headings = [(len(h), t.strip()) for h, t in HEADING_RE.findall(text)]
    rows = [r for r in TABLE_ROW_RE.findall(text) if not SEP_ROW_RE.match(r)]
    n_tables = len(re.findall(r"(?:^\s*\|.*\|\s*$\n)^\s*\|[\s:|-]+\|\s*$", text, re.M))
    return {"nums": nums, "cites": cites, "headings": headings,
            "rows": len(rows), "tables": n_tables}


def multiset_diff(a, b):
    """a에는 있고 b에는 부족한 것 -> {tok: 부족개수}."""
    miss = {}
    for tok, cnt in a.items():
        d = cnt - b.get(tok, 0)
        if d > 0:
            miss[tok] = d
    return miss


# ── 대조 ─────────────────────────────────────────────────────────────────

def compare(ko_text, en_text, label):
    ko, en = extract(ko_text), extract(en_text)
    issues = []

    # 1) heading 개수·레벨열
    ko_levels = [lv for lv, _ in ko["headings"]]
    en_levels = [lv for lv, _ in en["headings"]]
    if ko_levels != en_levels:
        issues.append(f"[heading] 구조 불일치: KO {len(ko_levels)}개 {ko_levels} ↔ EN {len(en_levels)}개 {en_levels}")

    # 2) 수치 전항
    only_ko = multiset_diff(ko["nums"], en["nums"])
    only_en = multiset_diff(en["nums"], ko["nums"])
    if only_ko:
        issues.append(f"[수치] EN에 빠진 KO 숫자: {_fmt(only_ko)}")
    if only_en:
        issues.append(f"[수치] KO에 빠진 EN 숫자: {_fmt(only_en)}")

    # 3) 인용(연도) 집합
    c_ko = multiset_diff(ko["cites"], en["cites"])
    c_en = multiset_diff(en["cites"], ko["cites"])
    if c_ko:
        issues.append(f"[인용] EN에 빠진 인용연도: {_fmt(c_ko)}")
    if c_en:
        issues.append(f"[인용] KO에 빠진 인용연도: {_fmt(c_en)}")

    # 4) 표 개수·행수
    if ko["tables"] != en["tables"]:
        issues.append(f"[표] 개수 불일치: KO {ko['tables']} ↔ EN {en['tables']}")
    elif ko["rows"] != en["rows"]:
        issues.append(f"[표] 행수 불일치: KO {ko['rows']} ↔ EN {en['rows']}")

    return issues


def _fmt(d, limit=20):
    items = sorted(d.items())
    s = ", ".join(f"{k}×{v}" if v > 1 else f"{k}" for k, v in items[:limit])
    if len(items) > limit:
        s += f" … (+{len(items) - limit})"
    return s


# ── 쌍 찾기 ──────────────────────────────────────────────────────────────

def find_pairs(args):
    if args.ko and args.en:
        return [(args.ko, args.en, os.path.basename(args.ko))]
    pairs = []
    if args.sections:
        d = args.sections
        # 패턴 A: <name>_ko.md ↔ <name>_en.md
        for ko in sorted(glob.glob(os.path.join(d, "*_ko.md"))):
            en = ko[:-6] + "_en.md"
            pairs.append((ko, en, os.path.basename(ko)[:-6]))
        # 패턴 B: sections/ 아래 ko/ 와 en/ 하위 디렉터리
        for ko in sorted(glob.glob(os.path.join(d, "ko", "*.md"))):
            en = os.path.join(d, "en", os.path.basename(ko))
            pairs.append((ko, en, os.path.basename(ko)))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="원고 국/영문 정합 검증(수치·heading·인용·표)")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ko"); ap.add_argument("--en")
    ap.add_argument("--sections", help="섹션 디렉터리(자동 짝짓기)")
    ap.add_argument("--strict", action="store_true", help="불일치 시 exit 1 (CI용)")
    args = ap.parse_args()

    pairs = find_pairs(args)
    if not pairs:
        print("대조할 KO/EN 쌍을 찾지 못했습니다. --ko/--en 또는 --sections 를 주세요.")
        print("(현재 원고는 국문만 존재할 수 있습니다 — 영문화 후 재실행하세요.)")
        return 0

    total = 0
    for ko_path, en_path, label in pairs:
        kp = os.path.join(args.repo, ko_path)
        ep = os.path.join(args.repo, en_path)
        if not os.path.exists(kp):
            print(f"— {label}: KO 없음 ({ko_path}) 건너뜀"); continue
        if not os.path.exists(ep):
            print(f"— {label}: EN 아직 없음 ({en_path}) — 영문화 대기"); continue
        issues = compare(open(kp, encoding="utf-8").read(),
                         open(ep, encoding="utf-8").read(), label)
        if not issues:
            print(f"✓ {label}: 정합 (heading·수치·인용·표 일치)")
        else:
            total += len(issues)
            print(f"✗ {label}: {len(issues)}건")
            for it in issues:
                print(f"    {it}")

    print(f"\n총 불일치 {total}건.", "판정은 사람이 — 어느 판본이 맞는지 확인 후 수정.")
    if args.strict and total:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

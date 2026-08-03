#!/usr/bin/env python3
"""
숫자 드리프트 체커 (BIOP02-107) — JSON 정본 ↔ markdown 대조.

원고가 스스로 요구한 대조(02_results.md "폐 완료 시 재작성 트리거" #5)를 자동화한다.
같은 수치가 4곳(원천 JSON + 3 markdown)에 흩어져 있고, 손으로 옮긴 곳은 낡는다.
이 도구는 JSON을 정본으로 삼아, markdown이 endpoint 곁에 적은 AUROC류 숫자가
원천의 알려진 값과 일치하는지 대조하고 "어긋난 자리"만 목록으로 낸다.
**판정하지 않는다** — 어느 쪽이 맞는지는 사람이 정한다. Critic 판단을 대체하지 않는다.

사용법:
    python3 agents/critic/scripts/check_number_drift.py [--repo <root>] [--strict]
    --strict : 드리프트가 하나라도 있으면 exit 1 (CI blocking용, BIOP02-106)
"""
import argparse, json, re, sys, glob, os

TOL = 0.004  # AUROC 반올림 허용오차

# markdown 줄에 이 키워드가 있으면 해당 endpoint로 간주 (소문자 대조)
KW = [
    (("histology", "조직형", "lusc"), "histology_lusc"),
    (("egfr 활성", "egfr_activating", "egfr활성"), "egfr_activating"),
    (("kras",), "kras_g12c"),
    (("braf",), "braf_v600e"),
    (("hpv",), "hpv_pos"),
    (("grade_high", "고분화", "grade"), "grade_high"),
    (("egfr 증폭", "egfr_amp", "egfr증폭"), "egfr_amp"),
    (("lauren",), "lauren_diffuse"),
    (("erbb2",), "erbb2_amp"),
    (("ebv",), "ebv"),
    (("msi_high", "cms1", "msi/면역"), "msi_high"),   # 대장
    (("msi_h", "msi-h", "msi "), "msi_h"),            # 위 (msi_high보다 뒤: 더 일반)
]

DOCS = [
    "manuscript/sections/02_results.md",
    "experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md",
    "experiments/crosscancer/MULTIFM_COMPARISON.md",
]

def collect_floats(obj, out):
    """dict/list 안의 모든 float를 4dp로 모은다(단일 스칼라만; 리스트=null_seeds 제외)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("null_seeds", "patient_proba", "patient_true"):
                continue
            collect_floats(v, out)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        f = float(obj)
        if 0.30 <= f <= 1.05:  # AUROC/threshold/null 대역
            out.add(round(f, 4))

def load_canonical(root):
    """endpoint -> {알려진 AUROC류 값 집합}. 전체 크로스암종 JSON에서 수집."""
    known = {}
    npos = {}
    pat = os.path.join(root, "experiments/crosscancer/*/full/*.json")
    files = [f for f in glob.glob(pat)
             if re.search(r"(shuffle_null_robustness|mil_cost_results)", os.path.basename(f))]
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        eps = d.get("endpoints", {})
        if not isinstance(eps, dict):
            continue
        for ep, rec in eps.items():
            if not isinstance(rec, dict):
                continue
            s = known.setdefault(ep, set())
            collect_floats(rec, s)
            n = rec.get("n_pos")
            if isinstance(n, int):
                npos.setdefault(ep, set()).add(n)
    return known, npos, files

def endpoints_on_line(line):
    low = line.lower()
    hits = []
    for kws, ep in KW:
        if any(k in low for k in kws):
            hits.append(ep)
    return hits

# CI/범위 안의 숫자(0.905–0.967)는 스킵 → 헤드라인 단일값만 검사
RANGE = re.compile(r"\d\.\d{1,4}\s*[–\-~]\s*\d\.\d{1,4}")
FLOAT = re.compile(r"(?<![\d.])0?\.\d{3,4}(?![\d])")

def check_doc(path, known, npos):
    """표(table) 행만 검사한다 — 행=endpoint 1:1이라 숫자↔endpoint 매핑이 명확.
    prose 안의 숫자(앵커 HER2·dev·pixel-mean 등)는 endpoint 귀속이 모호해 v1 범위에서 뺀다."""
    drifts = []
    if not os.path.exists(path):
        return drifts
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.strip()
        if not (s.startswith("|") and s.count("|") >= 3):
            continue  # 표 행만
        if re.match(r"^\|[\s:|\-]+\|?$", s):
            continue  # 구분선
        cells = [c.strip() for c in s.strip("|").split("|")]
        # 이 행이 가리키는 단일 endpoint (첫 매칭 셀 기준, 1개일 때만 — 모호행 스킵)
        row_eps = []
        for c in cells:
            e = endpoints_on_line(c)
            if e:
                row_eps.append(e[0])
        row_eps = list(dict.fromkeys(row_eps))
        if len(row_eps) != 1:
            continue  # endpoint가 0개거나 2개 이상인 행은 귀속 모호 → 스킵
        ep = row_eps[0]
        kv = known.get(ep, ())
        if not kv:
            continue  # 정본 JSON에 없는 endpoint(예: CMS) = v1 미포함
        # AUROC 셀에서 헤드라인 단일값 검사(범위=CI 제거)
        for c in cells:
            masked = RANGE.sub("   ", c)
            for m in FLOAT.finditer(masked):
                val = round(float(m.group()), 4)
                if not (0.40 <= val <= 1.02):
                    continue
                if not any(abs(val - k) <= TOL for k in kv):
                    drifts.append((i, val, [ep], sorted(kv), s[:90]))
    return drifts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    known, npos, files = load_canonical(a.repo)
    print(f"[check_number_drift] 정본 JSON {len(files)}개, endpoint {len(known)}종 로드")
    total = 0
    for doc in DOCS:
        p = os.path.join(a.repo, doc)
        drifts = check_doc(p, known, npos)
        if drifts:
            print(f"\n=== {doc} — 대조 불일치 {len(drifts)}건 (endpoint 곁 AUROC류가 원천에 없음) ===")
            for ln, val, eps, cand, txt in drifts:
                print(f"  L{ln}: {val}  (endpoint={','.join(eps)})  원천값={cand}")
                print(f"        | {txt}")
            total += len(drifts)
    print(f"\n[결과] 대조 불일치 후보 {total}건. **판정 아님** — 사람이 어느 쪽이 맞는지 확인.")
    print("       v1 범위: endpoint별 행 표만 검사(행=endpoint 1:1). "
          "FM별 행 표(MULTIFM 표)·prose·CMS/라우팅 JSON = 범위 밖(BIOP02-107 후속 확장). "
          "정본 JSON에 남은 stale 값은 '알려진 값'으로 통과하므로 JSON 정리는 별도.")
    if a.strict and total:
        sys.exit(1)

if __name__ == "__main__":
    main()

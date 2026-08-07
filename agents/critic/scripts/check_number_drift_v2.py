#!/usr/bin/env python3
"""
숫자 드리프트 체커 v2 (BIOP02-107 확장) — v1이 범위 밖으로 남긴 세 가지.

v1(`check_number_drift.py`)은 JSON 정본 ↔ markdown의 **endpoint별 표 행**(행=endpoint 1:1)만
검사하고, 스스로 범위 밖이라 명시한 것이 셋 있다: FM별 행 표(MULTIFM_COMPARISON.md), prose(산문)
속 수치, CMS/라우팅 비용 JSON. v2가 그 셋을 다룬다.

철학은 v1과 같다. **판정하지 않는다.** 접근도 v1을 그대로 잇는다 — v1의 "endpoint 키워드로 행을
정본 endpoint에 귀속시킨 뒤 그 endpoint의 값 집합과만 대조"하는 방식을, **표 행에서 모든 줄로
일반화**한다(v1은 "|"로 시작하는 표 행만 봄). endpoint 키워드가 없는 줄(예: MULTIFM_COMPARISON.md의
FM별 행 — endpoint가 앞선 절 제목에만 있고 행 자체엔 없음)은 **직전에 등장한 endpoint 키워드를
그대로 이어받는다**(문서를 위에서 아래로 읽는 사람과 같은 방식). 이 귀속을 못 하는 줄(같은 endpoint
문맥이 아직 한 번도 안 나온 줄)은 **검사하지 않고 건너뛴다** — 근거 없이 통과 처리하는 것보다
정직하다.

⚠️ **v1을 그대로 흉내 낸 "정본을 전부 하나로 합친 뒤 어딘가에 있으면 통과" 방식은 시도했다가
버렸다.** crosscancer 코퍼스는 1000종 넘는 실측 AUROC/비용값이 0~1.05 구간에 조밀하게 몰려 있어,
귀속 없이 전체와만 대조하면 임의의 값도 거의 항상 우연히 근처 값을 만나 통과한다(직접 확인:
전량 flatten 방식으로는 실제 주입 오류조차 못 잡음). **귀속(=v1과 같은 endpoint 버킷)이 없으면
이 체커는 사실상 무력하다** — 이건 설계 실수담이자, v2를 이 방식으로 만들면 안 되는 이유의 기록.

정본 코퍼스(v1보다 넓음. endpoint/axis 키를 가진 JSON을 전부 편입):
  - experiments/crosscancer/*/full/*.json (split_meta·smoke·partial 제외) — "endpoints" 또는
    "axes" 딕셔너리를 가진 파일 전부. FM별 파일(mil_cost_results_uni2h.json 등)도 포함되므로
    같은 endpoint에 UNI/Virchow2/UNI2-h 값이 함께 쌓인다(FM 구분 없이 endpoint로만 버킷 — FM별
    정밀 귀속은 하지 않는다. 참고: 이건규 #11709가 실측한 v1의 한계, "정본 어딘가 실재하면 통과"도
    그대로 물려받는다).
  - experiments/kkkim/20260710_cost_of_substitution/*.json — CMS/라우팅 비용(v1 정본 글롭 밖).
    "endocrine"·"antiHER2"·"chemo" 축 이름을 routing 키워드로 잡아 별도 버킷.

대조 대상은 v1과 동일한 3 문서지만 **모든 줄**(표+prose)을 본다.

사용법:
    python3 agents/critic/scripts/check_number_drift_v2.py [--repo <root>] [--strict]
    --strict : 미확인 수치가 하나라도 있으면 exit 1 (CI blocking용)
"""
import argparse, json, re, sys, glob, os

TOL = 0.004  # v1과 동일한 반올림 허용오차(AUROC류 + 3dp 반올림 흡수)

DOCS = [
    "manuscript/sections/02_results.md",
    "experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md",
    "experiments/crosscancer/MULTIFM_COMPARISON.md",
]

# v1 KW 재사용 + routing(CMS/비용) 축 추가
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
    (("cms1", "cms2", "cms3", "cms4"), "cms_subtype"),
    (("msi_high", "msi-high", "면역"), "msi_high"),         # 대장
    (("msi_h", "msi-h", "msi "), "msi_h"),                  # 위 (msi_high보다 뒤: 더 일반)
    (("anti_egfr", "anti-egfr", "항egfr"), "anti_egfr"),
    (("내분비", "endocrine"), "routing"),
    (("항her2", "antiher2", "her2축"), "routing"),
    (("화학요법", "chemo"), "routing"),
    (("라우팅", "routing", "오배정", "misroute", "축별 비용"), "routing"),
]

ENDPOINT_JSON_GLOB = "experiments/crosscancer/*/full/*.json"
ROUTING_JSON_GLOB = "experiments/kkkim/20260710_cost_of_substitution/*.json"
EXCLUDE_NAME = re.compile(r"split_meta|smoke|partial")

SKIP_KEYS = {"null_seeds", "patient_proba", "patient_true"}


def collect_floats(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            collect_floats(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_floats(v, out)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        f = float(obj)
        if 0.0 <= f <= 1.05:
            out.add(round(f, 4))


def endpoint_hits(text):
    low = text.lower()
    hits = []
    for kws, ep in KW:
        if any(k in low for k in kws):
            hits.append(ep)
    return list(dict.fromkeys(hits))


def load_canonical(root):
    """endpoint(=routing 포함) -> 값 집합. v1처럼 endpoint별로 버킷, FM/scheme은 안 나눔."""
    canon = {}
    files = []
    for f in glob.glob(os.path.join(root, ENDPOINT_JSON_GLOB)):
        if EXCLUDE_NAME.search(os.path.basename(f)):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):   # list형 JSON(shard_*.json·queue.json 등)은 d.get() 크래시 → 건너뜀 (BIOP02-107 kkkim 리뷰 🔴)
            continue
        recs = d.get("endpoints") or d.get("axes")
        if not isinstance(recs, dict):
            continue
        matched = False
        for ep_key, rec in recs.items():
            if not isinstance(rec, dict):
                continue
            eps = endpoint_hits(ep_key)
            if not eps:
                continue
            for ep in eps:
                s = canon.setdefault(ep, set())
                collect_floats(rec, s)
            matched = True
        if matched:
            files.append(f)
    for f in glob.glob(os.path.join(root, ROUTING_JSON_GLOB)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        s = canon.setdefault("routing", set())
        collect_floats(d, s)
        files.append(f)
    return canon, files


def strip_code_and_paths(text):
    """코드블록·인라인코드·파일경로·티켓번호 제거 (이건규 manuscript_parity_ko_en.py 재사용)."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"[\w./-]+\.(?:py|md|json|csv|yaml|yml)\S*", " ", text)
    text = re.sub(r"\bBIOP0\d-\d+\b", " ", text)
    return text


DEC = re.compile(r'(?<![\w.])[+\-−]?\d+\.\d+')  # BIOP01 check_manuscript_numbers.py 패턴


def claim_like(line, s, e):
    """수치가 '주장'스러운 문맥인지(DOI·날짜ID·버전·연도 배제). BIOP01 패턴 재사용."""
    tok = line[s:e]
    if e < len(line) and line[e] in "./":
        return False
    pre = line[max(0, s - 4):s]
    if pre.endswith("10.") or pre.endswith("/"):
        return False
    v = abs(float(tok.replace('+', '').replace('−', '-')))
    if 1900 <= v <= 2035:
        return False
    return True


def check_doc(path, canon):
    misses = []
    unattributed = 0
    if not os.path.exists(path):
        return misses, unattributed
    raw_text = open(path, encoding="utf-8").read()
    stripped = strip_code_and_paths(raw_text)
    context_ep = None
    for i, raw in enumerate(stripped.splitlines(), 1):
        hits = endpoint_hits(raw)
        if len(hits) == 1:
            context_ep = hits[0]
        elif len(hits) > 1:
            context_ep = None  # 모호한 줄은 문맥 갱신 안 함(v1의 "모호행 스킵"과 같은 정신)

        line = raw.replace('−', '-').replace('–', '-')
        nums = [(m.group(), m.start(), m.end()) for m in DEC.finditer(line)]
        if not nums:
            continue
        ep = hits[0] if len(hits) == 1 else context_ep
        if ep is None or ep not in canon:
            unattributed += len(nums)
            continue
        pool = canon[ep]
        for tok, s, e in nums:
            if not claim_like(line, s, e):
                continue
            val = float(tok.replace('+', ''))
            if not any(abs(val - k) <= TOL for k in pool):
                misses.append((i, tok, ep, raw.strip()[:100]))
    return misses, unattributed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    canon, files = load_canonical(a.repo)
    n_vals = sum(len(v) for v in canon.values())
    print(f"[check_number_drift_v2] 정본 JSON {len(files)}개, endpoint/axis {len(canon)}종"
          f"(routing 포함), 수치 {n_vals}건 로드")
    total = 0
    total_unattr = 0
    for doc in DOCS:
        p = os.path.join(a.repo, doc)
        misses, unattr = check_doc(p, canon)
        total_unattr += unattr
        if misses:
            print(f"\n=== {doc} — 정본 미확인 수치 {len(misses)}건 ===")
            for ln, tok, ep, txt in misses:
                print(f"  L{ln}: {tok}  (귀속 endpoint={ep})")
                print(f"        | {txt}")
            total += len(misses)
    print(f"\n[결과] 정본 미확인 후보 {total}건, 귀속 불가로 미검사 {total_unattr}건.")
    print("       **판정 아님** — endpoint 문맥에 귀속된 수치만 검사한다(v1과 동일 원칙,")
    print("       표 행 대신 모든 줄에 적용 + 직전 endpoint 문맥 승계). 귀속 불가(예: R7")
    print("       공간전사체 절처럼 endpoint 키워드가 아예 없는 문단)는 드리프트 여부를")
    print("       판단할 근거가 없어 건너뛴다 — 통과 처리가 아니라 미검사임에 유의.")
    if a.strict and total:
        sys.exit(1)


if __name__ == "__main__":
    main()

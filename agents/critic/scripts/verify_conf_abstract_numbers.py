#!/usr/bin/env python3
"""long abstract 수치 검증 — 엔드포인트 귀속 대조.

TOL=0.004: 초록은 소수 3자리, 정본 JSON 은 4자리라 정확일치로는 안 맞는다.
정본 드리프트 체커(check_number_drift.py)와 같은 허용오차를 쓴다.

v1 은 무력했다. 정본 JSON·markdown 의 모든 숫자를 한 집합으로 합쳐 "코퍼스
어딘가에 있으면 통과"로 만들었더니, 지어낸 값(유방 HER2 n_pos=88)도 코퍼스
어딘가에 88이 있다는 이유로 통과했다. 검사한 건 많은데 대조한 게 없었다.
류재면 님이 BIOP02-107 v2 에서 겪은 것과 같은 실패다.

v2 는 줄이 말하는 엔드포인트를 먼저 특정하고, 그 엔드포인트에 귀속된 값하고만
대조한다. 엔드포인트를 특정할 수 없는 줄은 검사하지 않고 건너뛴다 —
근거 없이 통과 처리하는 것보다 정직하다.

판정하지 않는다. 어긋난 자리만 낸다.
"""
import io, os, re, json, glob, sys

ROOT = "/home/gglee/project/BioProject02"
TOL = 0.004  # 반올림 허용오차 (check_number_drift.py 와 동일)
TARGET = os.path.join(ROOT, "manuscript/LONG_ABSTRACT_GIW2026_BIOP02_ko.md")

# 줄에 이 말이 있으면 해당 엔드포인트로 귀속
KW = [
    # 대장암 — '대장암 MSI-high' 가 'msi-h' 를 포함하므로 위암 규칙보다 먼저 둔다
    (("대장암 anti-egfr", "anti_egfr"), "anti_egfr"),
    (("대장암 msi-high", "msi_high"), "msi_high"),
    (("대장암 braf", "braf"), "braf_v600e"),
    (("두경부암 hpv", "hpv"), "hpv_pos"),
    (("lusc", "폐암 조직학적 아형", "폐암 lusc", "histology_lusc"), "histology_lusc"),
    (("위암 msi", "msi-h", "msi_h"), "msi_h"),
    (("kras",), "kras_g12c"),
    (("erbb2",), "erbb2_amp"),
    (("폐암 egfr", "egfr 활성", "egfr_activating"), "egfr_activating"),
    (("두경부암 egfr", "egfr 증폭", "egfr_amp"), "egfr_amp"),
    (("ebv",), "ebv"),
    (("유방암 her2", "항her2", "유방 | her2", "유방(anchor) | her2"), "_breast_her2"),
]

# 설정값·규약 — 정본 수치가 아니다
WHITELIST = {"0", "2026", "256", "20", "5000", "5,000", "1024", "1,024",
             "1000", "1,000", "5", "3", "2", "1", "25", "15", "4", "95", "0.5"}


def canon_by_endpoint():
    """endpoint -> 귀속된 수치 집합(4dp)."""
    by = {}

    def add(ep, v):
        try:
            f = float(v)
        except Exception:
            return
        by.setdefault(ep, set()).add(round(f, 4))

    for f in glob.glob(os.path.join(ROOT, "experiments/crosscancer/*/full/*.json")):
        if not re.search(r"(mil_cost_results|shuffle_null_robustness|routing_cost)",
                         os.path.basename(f)):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for ep, rec in (d.get("endpoints") or {}).items():
            stack = [rec]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k in ("patient_proba", "patient_true"):
                            continue
                        stack.append(v)
                elif isinstance(o, list):
                    stack.extend(o)
                elif isinstance(o, (int, float)) and not isinstance(o, bool):
                    add(ep, o)
        for key in ("endpoint_misroute", "endpoint_misroute_incl_histology"):
            for ep, rec in (d.get(key) or {}).items():
                if isinstance(rec, dict):
                    for v in rec.values():
                        if isinstance(v, (int, float)) and not isinstance(v, bool):
                            add(ep, v)

    # 스코어보드·정본 원고: 줄 단위로 엔드포인트를 특정해 그 줄의 숫자만 귀속
    for rel in ("experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md",
                "experiments/crosscancer/CROSS_CANCER_DECISION_MAP.md",
                "manuscript/DRAFT_paperC_full_ko.md"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        for line in io.open(p, encoding="utf-8"):
            ep = match_ep(line)
            if not ep:
                continue
            for m in re.finditer(r"\d+(?:\.\d+)?", line):
                add(ep, m.group(0))
    return by


def match_ep(line):
    low = line.lower()
    for keys, ep in KW:
        if any(k in low for k in keys):
            return ep
    return None


def main():
    by = canon_by_endpoint()
    t = io.open(TARGET, encoding="utf-8").read()

    missing, checked, skipped = [], 0, 0
    for ln_no, line in enumerate(t.split("\n"), 1):
        if line.startswith("#") or line.startswith("*GIW"):
            continue
        ep = match_ep(line)
        nums = [m for m in re.finditer(r"(?<![\w.])(\d+(?:,\d{3})*(?:\.\d+)?)(?![\w])", line)]
        if not nums:
            continue
        if not ep:
            skipped += len(nums)
            continue
        allow = by.get(ep, set())
        for m in nums:
            raw = m.group(1)
            if raw in WHITELIST:
                continue
            v = float(raw.replace(",", ""))
            checked += 1
            if not any(abs(v - a) <= TOL for a in allow):
                i = m.start()
                missing.append((ln_no, ep, raw, line.strip()[max(0, i - 35):i + 35]))

    print(f"엔드포인트 귀속 완료: {len(by)}개")
    print(f"대조한 수치 {checked}건 · 엔드포인트 미특정으로 건너뜀 {skipped}건")
    if not missing:
        print("\nRESULT: PASS — 귀속 엔드포인트의 정본에 없는 수치 0건")
        return 0
    print(f"\nRESULT: FAIL — 정본에서 못 찾은 수치 {len(missing)}건\n")
    for ln, ep, raw, ctx in missing:
        print(f"  L{ln}  [{ep}]  '{raw}'  …{ctx}…")
    return 1


if __name__ == "__main__":
    sys.exit(main())

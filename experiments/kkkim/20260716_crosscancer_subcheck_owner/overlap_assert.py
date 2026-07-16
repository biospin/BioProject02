#!/usr/bin/env python3
"""BIOP02-96 #1 data-leakage guard — patient(case)-overlap + TSS site-disjoint assert.

split.csv는 **case(환자) 단위** 파일이다(컬럼: case_id, tss_code, split). 한 행 = 한 환자.
이 스크립트는 train/val/test 3분할이 case_id 기준으로 서로소이고 TSS site도 겹치지 않음을 검증한다.

⚠️ 슬라이드 수가 아니라 case 수를 센다. split이 case 단위이므로, 한 환자가 다중 슬라이드를
가져도(예: HNSC 임베딩 472슬라이드 / 450환자, 22환자 다중) 그 환자의 모든 슬라이드는 같은
split에 귀속된다 → case-disjoint가 성립하면 슬라이드 누수도 없다.

실행(결정론적):
    python overlap_assert.py
    # split.csv 경로 커스텀: --root <repo>/experiments/crosscancer  --out patient_overlap_assert.json
"""
import argparse
import csv
import json
from itertools import combinations
from pathlib import Path

CANCERS = ["LUNG_NSCLC", "COLORECTAL", "HEADNECK_HNSC", "GASTRIC_STAD"]
SPLITS = ["train", "val", "test"]


def load_split(path):
    """split.csv → {split: (set(case_id), set(tss_code))}. 한 행 = 한 case."""
    per = {s: (set(), set()) for s in SPLITS}
    n_rows = 0
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            s = row["split"].strip()
            if s not in per:
                continue
            per[s][0].add(row["case_id"].strip())
            per[s][1].add(row["tss_code"].strip())
            n_rows += 1
    return per, n_rows


def assess(per, n_rows):
    all_cases = set().union(*(c for c, _ in per.values()))
    pairs = {}
    p_tot = t_tot = 0
    for a, b in combinations(SPLITS, 2):
        pc = len(per[a][0] & per[b][0])
        tc = len(per[a][1] & per[b][1])
        pairs[f"{a}∩{b}"] = {"patient": pc, "tss": tc}
        p_tot += pc
        t_tot += tc
    return {
        "n_cases": n_rows,               # split.csv 행 수 = case(환자) 수 (슬라이드 아님)
        "n_unique_cases": len(all_cases),
        "splits": {s: len(per[s][0]) for s in SPLITS},
        "pairs": pairs,
        "patient_overlap_total": p_tot,
        "tss_overlap_total": t_tot,
        "PASS_patient_disjoint": p_tot == 0,
        "site_disjoint": t_tot == 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2] / "crosscancer"),
                    help="crosscancer 루트(각 <암종>/full/split.csv)")
    ap.add_argument("--out", default=str(Path(__file__).with_name("patient_overlap_assert.json")))
    args = ap.parse_args()

    root = Path(args.root)
    result = {
        "assert": "patient-overlap==0 (case_id) + TSS site-disjoint",
        "by": "kkkim",
        "ticket": "BIOP02-96 #1 leakage guard",
        "note": "split.csv는 case(환자) 단위. n_cases=split.csv 행 수(슬라이드 아님). "
                "임베딩 슬라이드 수는 별개(embedding_manifest_*.csv 참조).",
        "per_cancer": {},
    }
    all_pass = True
    for c in CANCERS:
        sp = root / c / "full" / "split.csv"
        if not sp.exists():
            result["per_cancer"][c] = {"error": f"split.csv 없음: {sp}"}
            all_pass = False
            continue
        per, n_rows = load_split(sp)
        r = assess(per, n_rows)
        result["per_cancer"][c] = r
        all_pass = all_pass and r["PASS_patient_disjoint"] and r["site_disjoint"]
        print(f"{c}: cases={r['n_cases']} splits={r['splits']} "
              f"patient_overlap={r['patient_overlap_total']} tss_overlap={r['tss_overlap_total']} "
              f"-> {'PASS' if r['PASS_patient_disjoint'] and r['site_disjoint'] else 'FAIL'}")
    result["ALL_PASS_patient_disjoint"] = all_pass

    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nALL_PASS={all_pass}  wrote {args.out}")


if __name__ == "__main__":
    main()

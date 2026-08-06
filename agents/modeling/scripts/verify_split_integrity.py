"""
BIOP02-53 braveji Critic followup — split integrity assert 로그.

manifest의 split 컬럼 기준으로 patient-level(case_id) 및 site-level(TCGA TSS 코드)
disjointness를 assert로 검증하고 결과를 로그(json)로 남긴다. CLAM/MLP 학습 스크립트와
독립적으로 언제든 재실행 가능 — split_policy가 바뀔 때마다 재검증하는 용도.

계약 (BIOP02-130):
    - 입력 CSV에는 **split·case_id 컬럼이 반드시 있어야 한다.** 없으면 통과가 아니라 **실패**한다.
      (예전에는 split 컬럼이 없으면 전 행을 건너뛰고 "무결"로 통과했다 — 검사행 0의 공허한 통과.
       하필 문서가 사용법으로 가리키던 embedding_manifest_*.csv 에 split 컬럼이 없어,
       문서대로 실행하면 누수 검사가 작동하지 않는데 통과처럼 보였다. BIOP02-129 하네스가 적발.)
    - 검사한 행이 0이면 실패한다. "검사할 게 없었다"는 무결의 증거가 아니다.
    - 실패해도 결과 JSON을 기록한다(진단 가능하도록). 종료코드는 실패 시 1.

Run (정본 입력 = 코호트 split.csv):
    python agents/modeling/scripts/verify_split_integrity.py \
        --manifest experiments/crosscancer/LUNG_NSCLC/full/split.csv \
        --out experiments/sjpark/site_disjoint_verification.json

    # embedding_manifest 를 쓰려면 split 을 먼저 조인해야 한다(그 파일에는 split 컬럼이 없다).
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def tss_code(case_id: str) -> str:
    parts = case_id.split("-")
    if len(parts) >= 2 and parts[0] == "TCGA":
        return parts[1]
    return f"UNKNOWN:{case_id}"


def _write(out: str, payload: dict) -> None:
    """실패든 성공이든 결과 JSON을 남긴다 — 실패 시 보고서가 없으면 진단할 수 없다."""
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    split_sites = defaultdict(set)
    split_cases = defaultdict(set)
    n_rows = defaultdict(int)

    REQUIRED = ("split", "case_id")
    n_skipped = 0
    with open(args.manifest, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing = [c for c in REQUIRED if c not in header]
        if missing:
            # 공허통과 차단: 검사에 필요한 컬럼이 없으면 통과가 아니라 실패다.
            print(f"[FAIL] manifest에 필수 컬럼 없음: {missing}\n"
                  f"       파일: {args.manifest}\n"
                  f"       헤더: {header}\n"
                  f"       → split.csv 를 쓰거나, manifest에 split 을 조인한 뒤 재실행하십시오.",
                  file=sys.stderr)
            _write(args.out, {"manifest": args.manifest, "status": "FAIL",
                              "reason": "missing_required_columns", "missing": missing,
                              "header": header, "rows_checked": 0,
                              "site_disjoint": None, "patient_disjoint": None})
            return 1
        for row in reader:
            split = (row.get("split") or "").strip()
            case_id = (row.get("case_id") or "").strip()
            if not split or not case_id:
                n_skipped += 1
                continue
            split_sites[split].add(tss_code(case_id))
            split_cases[split].add(case_id)
            n_rows[split] += 1

    splits = sorted(split_sites.keys())
    site_overlaps = {}
    case_overlaps = {}
    for a, b in combinations(splits, 2):
        key = f"{a}_{b}"
        site_overlaps[key] = sorted(split_sites[a] & split_sites[b])
        case_overlaps[key] = sorted(split_cases[a] & split_cases[b])

    all_site_clear = all(len(v) == 0 for v in site_overlaps.values())
    all_case_clear = all(len(v) == 0 for v in case_overlaps.values())

    result = {
        "manifest": args.manifest,
        "n_rows_per_split": dict(n_rows),
        "n_unique_sites_per_split": {k: len(v) for k, v in split_sites.items()},
        "site_overlap": {k: len(v) for k, v in site_overlaps.items()},
        "site_overlap_detail": {k: v for k, v in site_overlaps.items() if v},
        "case_id_overlap": {k: len(v) for k, v in case_overlaps.items()},
        "case_id_overlap_detail": {k: v for k, v in case_overlaps.items() if v},
        "site_disjoint": all_site_clear,
        "patient_disjoint": all_case_clear,
    }

    n_checked = sum(n_rows.values())
    result["rows_checked"] = n_checked
    result["rows_skipped_blank"] = n_skipped

    print(json.dumps(result, indent=2))

    # 0행 통과 금지 — 검사할 게 없었다는 건 무결의 증거가 아니다.
    if n_checked == 0:
        result["status"] = "FAIL"
        result["reason"] = "no_rows_checked"
        _write(args.out, result)
        print(f"\n[FAIL] 검사된 행이 0입니다(빈 스킵 {n_skipped}행) — 통과로 판정하지 않습니다.",
              file=sys.stderr)
        return 1

    # 단일 split 그룹 통과 금지 (BIOP02-136) — 같은 이유의 다른 얼굴.
    # 그룹이 하나뿐이면 "그룹 간" disjoint 가 자명하게 성립해, 누수검사가 실제로는
    # 아무것도 대조하지 않고 PASS 가 찍힌다. train-only 매니페스트나 필터 버그로
    # test 행이 전부 탈락한 파일이 여기 걸린다.
    if len(n_rows) < 2:
        result["status"] = "FAIL"
        result["reason"] = "single_split_group"
        _write(args.out, result)
        print(f"\n[FAIL] split 그룹이 {len(n_rows)}개뿐입니다({list(n_rows)}) — "
              f"대조할 상대가 없어 disjoint 가 자명하게 성립하므로 통과로 판정하지 않습니다.\n"
              f"       → train/val/test 가 모두 담긴 split.csv 인지 확인하십시오.",
              file=sys.stderr)
        return 1

    # 누수는 assert 대신 명시적 실패로 알린다(보고서를 남기고, python -O 에서도 살아남도록).
    if not all_case_clear or not all_site_clear:
        result["status"] = "FAIL"
        result["reason"] = "leakage"
        _write(args.out, result)
        if not all_case_clear:
            print(f"[FAIL] patient-level leakage 발견: {result['case_id_overlap_detail']}", file=sys.stderr)
        if not all_site_clear:
            print(f"[FAIL] site-level leakage 발견: {result['site_overlap_detail']}", file=sys.stderr)
        return 1

    result["status"] = "PASS"
    _write(args.out, result)
    print(f"\n[PASS] site-disjoint AND patient-disjoint 확인됨 (검사 {n_checked}행).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

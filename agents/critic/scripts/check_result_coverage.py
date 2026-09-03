#!/usr/bin/env python3
"""결과 산출물 커버리지 게이트 — 원고에 반영되지 않은 실험 결과를 찾는다.

배경: CPTAC 외부검증 결과 5종이 분석 완료 상태로 원고에 한 번도 반영되지 않은
채 두 달이 지났다(PITFALLS_REGISTRY A9·C11). 기존 게이트는 '원고에 실린 것'의
타당성만 검증하고 '실려야 하는데 안 실린 것'은 보지 않는다. 이 스크립트가 그
구멍을 메운다.

판정 방식
  1. experiments/ 아래 결과 산출물을 열거한다.
  2. 각 산출물이 원고에서 참조되는지 두 경로로 확인한다.
       (a) 경로 참조 — <!-- src: ... --> 주석이나 본문에 파일명·디렉터리명이 등장
       (b) 수치 참조 — 산출물의 대표 수치가 원고 본문에 등장
  3. 어느 쪽에도 안 걸리면 results/EXCLUDED.md 에 제외 사유가 있는지 본다.
  4. 남은 것 = 미분류. 미분류가 0이어야 제출 가능하다.

사용
  python3 agents/critic/scripts/check_result_coverage.py
  python3 agents/critic/scripts/check_result_coverage.py --manuscript manuscript/DRAFT_ML4H_v2_full.md
  python3 agents/critic/scripts/check_result_coverage.py --json   # 기계 판독용

종료 코드: 미분류 0이면 0, 있으면 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 결과 산출물로 볼 파일 이름·패턴
ARTIFACT_NAMES = {"metrics.json", "ext_eval_summary.json"}
ARTIFACT_GLOBS = ["**/*_summary.json", "**/*_results.json", "**/*_eval*.json"]

# 결과가 아니라 운영·설정에 해당해 커버리지 대상에서 뺀다
SKIP_PARTS = {
    "_cache", "__pycache__", ".ipynb_checkpoints", "logs", "queue",
    "config", "configs", "manifest", "manifests",
}
SKIP_NAME_RE = re.compile(
    r"(config|manifest|queue|shard|DONE|watchdog|split_policy|registry\.jsonl)", re.I
)

# EXCLUDED.md 에서 '제외 확정'으로 인정할 태그. 이 태그가 붙은 줄에 경로가
# 적혀 있어야만 제외로 센다.
EXCLUDED_TAG = "[제외확정]"

# 대표 수치로 쓸 키 (성능 지표)
METRIC_KEYS = (
    "auc", "auroc", "ext_auc", "ext_auprc", "auprc",
    "balanced_accuracy", "ext_balanced_accuracy", "macro_f1", "f1",
)


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for cand in [cur, *cur.parents]:
        if (cand / ".git").exists() and (cand / "experiments").is_dir():
            return cand
    return cur


def collect_artifacts(root: Path) -> list[Path]:
    exp = root / "experiments"
    if not exp.is_dir():
        return []
    found: set[Path] = set()
    for p in exp.rglob("*.json"):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        if SKIP_NAME_RE.search(p.name):
            continue
        if p.name in ARTIFACT_NAMES:
            found.add(p)
            continue
        for pat in ARTIFACT_GLOBS:
            if p.match(pat):
                found.add(p)
                break
    return sorted(found)


def extract_metrics(path: Path) -> dict[str, float]:
    """산출물에서 대표 수치를 뽑는다. 중첩 dict 까지 훑는다."""
    out: dict[str, float] = {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return out

    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}{k}"
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if any(m in k.lower() for m in METRIC_KEYS):
                        out[key] = float(v)
                else:
                    walk(v, prefix=f"{key}.")
        elif isinstance(obj, list):
            for item in obj[:20]:
                walk(item, prefix=prefix)

    walk(data)
    return out


def number_variants(val: float) -> list[str]:
    """원고에 적힐 법한 표기 변형.

    소수 넷째·셋째 자리만 쓴다. 둘째 자리(0.53 등)는 우연 일치가 너무 많아
    커버리지 근거로 못 쓴다. 실제로 초판에서 2자리 매칭 때문에 미반영
    산출물이 전부 '반영됨'으로 통과했다.
    """
    variants = []
    for nd in (4, 3):
        s = f"{val:.{nd}f}"
        if s not in variants:
            variants.append(s)
    return variants


def load_manuscript(root: Path, explicit: list[str] | None) -> tuple[str, list[Path]]:
    if explicit:
        paths = [root / p for p in explicit]
    else:
        mdir = root / "manuscript"
        paths = sorted(mdir.glob("DRAFT_*full*.md")) if mdir.is_dir() else []
    text_parts, used = [], []
    for p in paths:
        if p.is_file():
            text_parts.append(p.read_text(encoding="utf-8", errors="replace"))
            used.append(p)
    return "\n".join(text_parts), used


def load_excluded(root: Path) -> tuple[str, Path | None]:
    for cand in (root / "results" / "EXCLUDED.md", root / "EXCLUDED.md"):
        if cand.is_file():
            return cand.read_text(encoding="utf-8", errors="replace"), cand
    return "", None


def classify(art: Path, root: Path, manu: str, excluded: str) -> dict:
    rel = art.relative_to(root).as_posix()
    parent = art.parent.name

    # 경로 토큰은 '구체적인' 것만 쓴다. 조부모 디렉터리는 팀원 핸들(sjpark 등)이라
    # 원고 본문에 그대로 등장해 전부 매칭시켜 버린다(초판 실패 원인).
    def specific(tok: str) -> bool:
        return bool(tok) and len(tok) >= 8 and ("_" in tok or "/" in tok)

    path_hit = None
    for token in (rel, parent):
        if specific(token) and token in manu:
            path_hit = token
            break

    metrics = extract_metrics(art)
    hits, misses = [], []
    for key, val in metrics.items():
        if val == 0 or abs(val) > 1e6:
            continue
        matched = next((v for v in number_variants(val) if v in manu), None)
        if matched:
            hits.append(f"{key}={val:g} (원고 '{matched}')")
        else:
            misses.append(f"{key}={val:g}")

    # 제외 인정은 `[제외확정]` 태그가 붙은 줄에서만. 태그를 요구하지 않으면
    # EXCLUDED.md 에 '반영 예정'으로 적어 둔 항목까지 제외로 읽혀, 이 게이트가
    # 스스로를 무력화한다.
    exc_hit = None
    if excluded:
        for line in excluded.splitlines():
            if EXCLUDED_TAG not in line:
                continue
            for token in (rel, parent):
                if specific(token) and token in line:
                    exc_hit = token
                    break
            if exc_hit:
                break

    if path_hit and not misses:
        status = "반영됨"
    elif hits and misses:
        status = "부분반영"
    elif hits or path_hit:
        status = "반영됨"
    elif exc_hit:
        status = "의도적 제외"
    else:
        status = "미분류"

    return {
        "path": rel,
        "status": status,
        "path_hit": path_hit,
        "metric_hits": hits,
        "metric_misses": misses,
        "excluded_hit": exc_hit,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="결과 산출물 커버리지 게이트")
    ap.add_argument("--root", default=None, help="저장소 루트 (기본: 자동 탐지)")
    ap.add_argument("--manuscript", action="append", default=None,
                    help="검사할 원고 파일 (반복 지정 가능, 기본: manuscript/DRAFT_*full*.md)")
    ap.add_argument("--json", action="store_true", help="JSON 으로 출력")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else find_repo_root(Path(__file__).parent)
    manu, manu_files = load_manuscript(root, args.manuscript)
    if not manu_files:
        print("[오류] 원고 파일을 찾지 못했습니다. --manuscript 로 지정하십시오.", file=sys.stderr)
        return 2
    excluded, exc_path = load_excluded(root)

    artifacts = collect_artifacts(root)
    rows = [classify(a, root, manu, excluded) for a in artifacts]

    counts = {"반영됨": 0, "부분반영": 0, "의도적 제외": 0, "미분류": 0}
    for r in rows:
        counts[r["status"]] += 1

    if args.json:
        print(json.dumps({"root": str(root), "counts": counts, "rows": rows},
                         ensure_ascii=False, indent=2))
        return 0 if counts["미분류"] == 0 else 1

    print("=" * 72)
    print("결과 산출물 커버리지 리포트")
    print("=" * 72)
    print(f"저장소   : {root}")
    print(f"원고     : {', '.join(p.relative_to(root).as_posix() for p in manu_files)}")
    print(f"제외목록 : {exc_path.relative_to(root).as_posix() if exc_path else '(없음 — results/EXCLUDED.md 미생성)'}")
    print(f"산출물   : {len(artifacts)}건")
    print()
    print(f"  반영됨      {counts['반영됨']:3d}")
    print(f"  부분반영    {counts['부분반영']:3d}   <- 일부 수치만 원고에 있음, 확인 요망")
    print(f"  의도적 제외 {counts['의도적 제외']:3d}")
    print(f"  미분류      {counts['미분류']:3d}   <- 제출 전 0 이어야 함")
    print()

    unclassified = [r for r in rows if r["status"] == "미분류"]
    if unclassified:
        print("-" * 72)
        print("미분류 (원고에 흔적 없음, 제외 사유도 없음)")
        print("-" * 72)
        for r in unclassified:
            print(f"\n  {r['path']}")
            if r["metric_misses"]:
                print(f"      미반영 수치: {', '.join(r['metric_misses'][:6])}")
            else:
                print("      (성능 지표 키 없음)")

    partial = [r for r in rows if r["status"] == "부분반영"]
    if partial:
        print()
        print("-" * 72)
        print("부분반영 (같은 파일 안에서 쓰인 수치와 안 쓰인 수치가 갈림)")
        print("-" * 72)
        for r in partial:
            print(f"\n  {r['path']}")
            print(f"      원고에 있음 : {', '.join(r['metric_hits'][:4])}")
            print(f"      원고에 없음 : {', '.join(r['metric_misses'][:6])}")

    if unclassified or partial:
        print()
        print("  조치: 원고에 반영하거나, results/EXCLUDED.md 에")
        print("        제외 사유·근거 등급(E1/E2/E3)·재검토 조건을 적으십시오.")
    else:
        print("미분류·부분반영 0건 — 커버리지 게이트 통과.")

    print()
    return 0 if counts["미분류"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

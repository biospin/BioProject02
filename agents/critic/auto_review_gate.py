#!/usr/bin/env python3
"""자동 리뷰 게이트 (결정론적, LLM 불필요, cron 가능).

정책: guide/AUTO_REVIEW_POLICY.md. 산출물(experiment 디렉토리 또는 파일/문서)을 받아
① 티어 분류(A/B/C) ② 하드룰 기계검사 → gate_report.json 생성 + critic_status 초기값 설정.
LLM 적대적 리뷰(paper-critic/reviewer)는 이 게이트가 ai_review_pending=true로 큐잉하고,
세션/OpenClaw가 이어 실행한다(이 스크립트는 사람·LLM 없이 돌아가는 기계 파트만 담당).

Usage:
  python agents/critic/auto_review_gate.py <path> [--tier A|B|C] [--owner NAME] [--write]
  python agents/critic/auto_review_gate.py --scan experiments/crosscancer  # 하위 산출물 일괄
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def rel(f: Path):
    try:
        return str(f.relative_to(ROOT))
    except ValueError:
        return str(f)

# --- 하드룰·티어 패턴을 config에서 로드 (프로젝트-불문; config 없으면 기본값 폴백) ---
_CFG_PATH = Path(__file__).resolve().parent / "auto_review_config.json"
_DEFAULT_HR = {
    "forbidden_phrases": [
        r"drug response prediction", r"personalized therapy", r"personalised therapy",
        r"patient-?specific[^\n]{0,20}treatment", r"optimal treatment",
        r"약물반응예측", r"개인 ?맞춤 ?치료"],
    "forbidden_safe_markers": ["금지", "아님", "않", "없", "not ", "n't", "prohibit", "forbidden",
        "avoid", "must not", "❌", "banned", "위반", "framing", "표현", "검출", "reference", "`",
        "regex", "grep", "anti-pattern", "안티패턴", "AP-0"],
    "meta_files": ["auto_review_gate.py", "AUTO_REVIEW_POLICY", "anti_patterns", "checklist",
        "AI_REVIEW_PROMPT", "auto_review_config"],
    "metrics_required": ["auc", "auprc", "balanced_accuracy", "n_train", "n_val",
        "model", "embedding_model", "commit_hash"],
    "claim_level_required_value": "hypothesis_only",
}
_DEFAULT_TIER = {
    "C": ["manuscript", "preprint", "paper_draft", "abstract", "headline",
          "SUBSTITUTABILITY_LAW", "PAPER_DIRECTION", "publish", "figure_main"],
    "A": ["guide/", "docs/", "README", "HANDOFF", "PROGRESS_DECISIONS",
          "setup", "infra", ".yaml", ".yml", "manifest", "RESUME_"],
}

def _load_rules():
    try:
        cfg = json.loads(_CFG_PATH.read_text())
        hr = {**_DEFAULT_HR, **cfg.get("hard_rules", {})}
        tr = cfg.get("tier_rules", {})
        tier = {"C": tr.get("C_path_patterns", _DEFAULT_TIER["C"]),
                "A": tr.get("A_path_patterns", _DEFAULT_TIER["A"])}
        return hr, tier
    except Exception:
        return _DEFAULT_HR, _DEFAULT_TIER

_HR, _TIER = _load_rules()
DRP_FORBIDDEN = _HR["forbidden_phrases"]
METRICS_REQUIRED = _HR["metrics_required"]
CLAIM_REQUIRED = _HR["claim_level_required_value"]
TIER_C_HINTS = _TIER["C"]
TIER_A_HINTS = _TIER["A"]


def classify_tier(p: Path, override=None):
    if override:
        return override.upper(), "override"
    marker = p / ".review_tier" if p.is_dir() else p.parent / ".review_tier"
    if marker.exists():
        return marker.read_text().strip().upper(), ".review_tier"
    s = str(p).lower()
    for h in TIER_C_HINTS:
        if h.lower() in s:
            return "C", f"hint:{h}"
    # experiment 디렉토리(결과물) = B
    if p.is_dir() and (list(p.glob("*metrics*.json")) or list(p.glob("*mil*.json")) or
                       list(p.glob("*routing_cost*.json")) or list(p.glob("*LAW_TEST*"))):
        return "B", "hint:results-dir"
    for h in TIER_A_HINTS:
        if h.lower() in s:
            return "A", f"hint:{h}"
    return "B", "default"  # 애매하면 B(사람 확인 남김) — A로 과대분류 금지


SKIP_DIRS = {"embeddings", "coords", "raw", "data", "_crosscancer_raw",
             "__pycache__", ".git", "tiles", "wsi", "svs"}

def iter_text_files(p: Path):
    exts = {".md", ".json", ".txt", ".yaml", ".yml", ".py"}  # csv 제외(대용량 라벨/좌표)
    if p.is_file():
        yield p; return
    for f in p.rglob("*"):
        if any(part in SKIP_DIRS for part in f.parts):   # 대용량/바이너리 폴더 스킵
            continue
        if f.is_file() and f.suffix.lower() in exts and f.stat().st_size < 2_000_000:
            yield f


# 금지어가 "위반"이 아니라 "금지 규칙 서술/참조"인 문맥 마커(오탐 제외) + 규칙정의 파일 스킵 — config에서
DRP_SAFE_MARKERS = _HR["forbidden_safe_markers"]
DRP_META_FILES = _HR["meta_files"]

def check_drp(p: Path):
    hits = []
    for f in iter_text_files(p):
        if any(m in f.name for m in DRP_META_FILES):
            continue
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines):
            low = line.lower()
            for pat in DRP_FORBIDDEN:
                if re.search(pat, low):
                    # 해당 줄 ±0 문맥에 부정/참조 마커 있으면 '규칙 서술'로 보고 제외
                    if any(mk.lower() in low for mk in DRP_SAFE_MARKERS):
                        continue
                    hits.append({"file": rel(f), "line": i + 1,
                                 "pattern": pat, "text": line.strip()[:120]})
    return hits


def check_claim_level(p: Path):
    """claim_level 이 나오면 hypothesis_only 여야 함. JSON·frontmatter·본문 스캔."""
    bad = []
    seen = False
    for f in iter_text_files(p):
        try:
            t = f.read_text(errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r'claim_level["\s:=]+([a-zA-Z_]+)', t):
            seen = True
            if m.group(1) != CLAIM_REQUIRED:
                bad.append({"file": rel(f), "value": m.group(1)})
    return seen, bad


def check_metrics(p: Path):
    """experiment 디렉토리면 metrics.json 필수필드 확인."""
    if not p.is_dir():
        return None
    mfs = list(p.glob("metrics.json")) or list(p.glob("*metrics*.json"))
    if not mfs:
        return {"present": False, "missing_fields": [], "note": "metrics.json 없음(결과 dir가 아닐 수 있음)"}
    try:
        d = json.loads(mfs[0].read_text())
    except Exception as e:
        return {"present": True, "parse_error": str(e)[:100]}
    missing = [k for k in METRICS_REQUIRED if k not in d or d[k] in (None, "")]
    return {"present": True, "file": rel(mfs[0]), "missing_fields": missing}


def gate(path: str, tier_override=None, owner=None):
    p = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path)
    if not p.exists():
        return {"error": f"경로 없음: {p}"}
    tier, tier_why = classify_tier(p, tier_override)

    drp = check_drp(p)
    cl_seen, cl_bad = check_claim_level(p)
    metrics = check_metrics(p)

    hard_fail = []
    if drp:
        hard_fail.append({"rule": "DRP 표현 검출", "detail": drp[:5]})
    if cl_bad:
        hard_fail.append({"rule": "claim_level != hypothesis_only", "detail": cl_bad[:5]})
    if metrics and metrics.get("missing_fields"):
        hard_fail.append({"rule": "metrics.json 필수필드 결측", "detail": metrics["missing_fields"]})

    # verdict
    human_items = []
    ai_review_pending = False
    if hard_fail:
        status = "blocked"
    elif tier == "A":
        status = "auto_pass"
    elif tier == "B":
        status = "provisional"; ai_review_pending = True
        human_items = ["AI 리뷰 후 비동기 1-클릭 확인(공유 전)"]
    else:  # C
        status = "needs_human"; ai_review_pending = True
        human_items = ["AI 적대적 리뷰가 surface한 판단항목 adjudicate",
                       "헤드라인 주장/공개/저자 대면은 사람 확정(owner≠reviewer)"]

    report = {
        "schema": "auto_review_gate/v1",
        "path": str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p),
        "tier": tier, "tier_reason": tier_why,
        "owner": owner or "unknown",
        "hard_rule_checks": {
            "drp_forbidden": {"pass": not drp, "hits": drp[:5]},
            "claim_level": {"seen": cl_seen, "pass": not cl_bad, "bad": cl_bad[:5]},
            "metrics_required": metrics,
        },
        "critic_status": status,
        "ai_review_pending": ai_review_pending,
        "ai_review_cmd": ("세션/OpenClaw에서: paper-critic + Critic 7-point 에이전트로 "
                          f"'{path}' 적대적 리뷰 → critic_report.json 갱신") if ai_review_pending else None,
        "human_adjudication_items": human_items,
        "note": "결정론적 기계검사만. 최종 pass/reject는 정책 Tier에 따라 AI리뷰+사람.",
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tier", choices=list("ABC"))
    ap.add_argument("--owner")
    ap.add_argument("--write", action="store_true", help="산출물 옆에 gate_report.json 기록")
    ap.add_argument("--scan", help="하위 experiment 디렉토리 일괄 게이트")
    a = ap.parse_args()

    targets = []
    if a.scan:
        base = (ROOT / a.scan) if not Path(a.scan).is_absolute() else Path(a.scan)
        for d in base.rglob("*"):
            if d.is_dir() and (list(d.glob("*metrics*.json")) or list(d.glob("*mil*.json")) or list(d.glob("*LAW_TEST*"))):
                targets.append(d)
        if not targets:
            print("스캔 결과 결과-디렉토리 없음"); return
    elif a.path:
        targets = [a.path]
    else:
        ap.error("path 또는 --scan 필요")

    for t in targets:
        rep = gate(str(t), a.tier, a.owner)
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        if a.write and "error" not in rep:
            tp = (ROOT / rep["path"])
            out = (tp / "gate_report.json") if tp.is_dir() else (tp.parent / f"{tp.stem}.gate_report.json")
            out.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
            print(f"  → {out}")


if __name__ == "__main__":
    main()

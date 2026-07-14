#!/usr/bin/env python3
"""자동 리뷰 오케스트레이터 (구조 완성·config로 활성화).

gate(결정론) → 큐(AI리뷰 대기) → 상태전환 → 알림(OpenClaw). config로 결정항목 주입.
`config.enabled=false`면 **dry-run**(무엇을 할지만 출력, 실제 행동 X) — 스터디 결정 전까지 안전 대기.

모드:
  --scan / <path>        : gate 실행 → gate_report.json + AI리뷰 대상은 큐 적재 + 알림
  --drain-queue          : 큐의 AI리뷰 대기 항목마다 '에이전트 호출 스펙'(review_request.json) 발행
                           → 세션/OpenClaw가 이걸 읽어 paper-critic/7-point 에이전트 실제 실행
  --confirm <path> --by X: 사람 1-클릭 확인 (provisional/needs_human → pass) 기록

의존성: 표준 라이브러리 + auto_review_gate. LLM/Slack 실호출은 훅(HOOK 표시)이라 세션/OpenClaw가 수행.
"""
import argparse, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import auto_review_gate as G

CONFIG = HERE / "auto_review_config.json"
QUEUE = HERE / "ai_review_queue.jsonl"        # AI리뷰 대기 (append-only)
STATUS = HERE / "review_status.json"          # 경로별 최신 상태
REQ_DIR = HERE / "review_requests"            # drain 시 에이전트 호출 스펙


def load_cfg():
    return json.loads(CONFIG.read_text())


def load_status():
    return json.loads(STATUS.read_text()) if STATUS.exists() else {}


def save_status(s):
    STATUS.write_text(json.dumps(s, ensure_ascii=False, indent=1))


def tier_from_cfg(path_str, cfg):
    """config 패턴으로 티어 재정의(게이트 힌트보다 우선)."""
    s = path_str.lower()
    for pat in cfg["tier_rules"]["C_path_patterns"]:
        if pat.lower() in s:
            return "C"
    for pat in cfg["tier_rules"]["A_path_patterns"]:
        if pat.lower() in s:
            return "A"
    return None  # 게이트 기본 분류에 위임


def notify(cfg, channel_key, msg, dry):
    ch = cfg["notify"].get(channel_key, "#biop02-dev")
    line = f"[auto-review→{ch}] {msg}"
    if dry or not cfg["enabled"]:
        print("  (dry) " + line)
    else:
        # HOOK: OpenClaw로 Slack 전송 (guide/openclaw_harness_runbook.md).
        #       실배선은 스터디 후. 현재는 로그만.
        print("  " + line)
        (HERE / "notify.log").open("a").write(line + "\n")


def run_gate(path, cfg, owner=None, dry=True):
    override = tier_from_cfg(str(path), cfg)
    rep = G.gate(str(path), tier_override=override, owner=owner)
    if "error" in rep:
        print(json.dumps(rep, ensure_ascii=False)); return rep
    # gate_report.json 기록
    tp = (ROOT / rep["path"])
    out = (tp / "gate_report.json") if tp.is_dir() else (tp.parent / f"{tp.stem}.gate_report.json")
    if not dry and cfg["enabled"]:
        out.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    st = rep["critic_status"]
    print(f"{rep['tier']}  {st:12s}  {rep['path']}")
    # 상태 갱신 + 알림 + 큐
    status = load_status()
    status[rep["path"]] = {"tier": rep["tier"], "critic_status": st, "owner": owner}
    if not dry and cfg["enabled"]:
        save_status(status)
    if st == "blocked":
        notify(cfg, "channel_blocked", f"BLOCKED {rep['path']} — 하드룰 위반", dry)
    elif rep["ai_review_pending"]:
        if not dry and cfg["enabled"]:
            with QUEUE.open("a") as q:
                q.write(json.dumps({"path": rep["path"], "tier": rep["tier"],
                                    "owner": owner, "status": st, "enqueued": time.strftime("%F %T")}) + "\n")
        notify(cfg, "channel_needs_human" if rep["tier"] == "C" else "channel_provisional",
               f"{st} {rep['path']} — AI 리뷰 대기(drain-queue)", dry)
    return rep


def drain_queue(cfg, dry=True):
    """큐의 각 항목에 대해 '에이전트 호출 스펙' 발행. 세션/OpenClaw가 실제 실행."""
    if not QUEUE.exists():
        print("큐 비어있음"); return
    REQ_DIR.mkdir(exist_ok=True)
    items = [json.loads(l) for l in QUEUE.read_text().splitlines() if l.strip()]
    seen = set()
    for it in items:
        if it["path"] in seen:
            continue
        seen.add(it["path"])
        # owner→reviewer 자동 배정 (cross_review_map)
        reviewer = cfg["cross_review_map"].get(it.get("owner"), "<assign>")
        spec = {
            "path": it["path"], "tier": it["tier"], "owner": it.get("owner"),
            "assigned_reviewer": reviewer,
            "agents": cfg["ai_review"]["agents"],
            "checklist": cfg["ai_review"]["checklist"],
            "prompt_template": cfg["ai_review"]["prompt_template"],
            "independent_passes": cfg["ai_review"]["independent_passes"],
            "verify_headline_numbers": cfg["ai_review"]["verify_headline_numbers"],
            "on_owner_eq_reviewer": (cfg["owner_ne_reviewer"] if reviewer == it.get("owner") else None),
            "produce": f"{it['path']}/critic_report.json (schema: schemas/critic_report.schema.json)",
            "next": "provisional→(사람 1-클릭 confirm) / needs_human→(사람 adjudicate)",
        }
        print(f"REVIEW-REQUEST  {it['path']}  → reviewer={reviewer}  agents={spec['agents']}")
        if not dry and cfg["enabled"]:
            (REQ_DIR / (it["path"].replace("/", "_") + ".req.json")).write_text(
                json.dumps(spec, ensure_ascii=False, indent=1))
    if dry or not cfg["enabled"]:
        print("  (dry) 발행만 시뮬레이션 — enabled=true면 review_requests/*.req.json 기록")


def confirm(path, by, cfg, dry=True):
    status = load_status()
    key = path if path in status else next((k for k in status if k.endswith(path)), None)
    if not key:
        print(f"상태에 없음: {path} (먼저 gate 실행)"); return
    prev = status[key]["critic_status"]
    status[key]["critic_status"] = "pass"
    status[key]["confirmed_by"] = by
    status[key]["confirmed_at"] = time.strftime("%F %T")
    print(f"CONFIRM {key}: {prev} → pass (by {by})")
    if not dry and cfg["enabled"]:
        save_status(status)
    else:
        print("  (dry) enabled=true면 review_status.json 갱신")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--scan")
    ap.add_argument("--owner")
    ap.add_argument("--drain-queue", action="store_true")
    ap.add_argument("--confirm")
    ap.add_argument("--by")
    ap.add_argument("--force-live", action="store_true", help="config.enabled 무시하고 실제 실행")
    a = ap.parse_args()
    cfg = load_cfg()
    dry = not (cfg["enabled"] or a.force_live)
    if dry:
        print("== DRY-RUN (config.enabled=false 또는 미결정) — 실제 행동 안 함 ==")

    if a.confirm:
        confirm(a.confirm, a.by or "unknown", cfg, dry); return
    if a.drain_queue:
        drain_queue(cfg, dry); return
    targets = []
    if a.scan:
        base = (ROOT / a.scan) if not Path(a.scan).is_absolute() else Path(a.scan)
        for d in base.rglob("*"):
            if d.is_dir() and (list(d.glob("*metrics*.json")) or list(d.glob("*mil*.json")) or list(d.glob("*LAW_TEST*"))):
                targets.append(str(d))
    elif a.path:
        targets = [a.path]
    else:
        ap.error("path 또는 --scan/--drain-queue/--confirm 필요")
    for t in targets:
        run_gate(t, cfg, a.owner, dry)


if __name__ == "__main__":
    main()

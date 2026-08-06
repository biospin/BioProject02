#!/usr/bin/env python3
"""
BIOP02 검수 하네스 — 도메인 mutation 러너 (BIOP02-129).

BIOP01 evals/reproducibility_pilot 골격을 벤치마킹하되, **mutation·detector는 BIOP02 도메인**이다.
velocity 의 claim_level 격상을 베끼지 않는다. 여기서 재는 것은 하나다:

    "BIOP02 실무자가 저지를 법한 실수를 심었을 때, 우리 게이트가 실제로 잡는가?"

집안 스타일과의 차이(의도적):
  - critic_pilot/citation_verifier 는 **scorer 를 교체**하는 mutation(레지스트리 몽키패치)이다.
    그건 "케이스가 스코어러를 구속하는가"를 잰다.
  - 여기서는 **데이터(산출물)를 변조**한다. split 누수·수치 드리프트·critic 위조는 코드가 아니라
    **데이터에서** 발생하는 실패이므로, 데이터 mutation 이라야 그 게이트를 실제로 시험한다.
  - detector 는 in-process import 가 아니라 **CLI 서브프로세스**로 부른다(종료코드/보고서가 계약이므로).

판정(BIOP02 어휘):
  CAUGHT      detector 가 mutated 산출물을 거부(비정상 종료 또는 보고서에 실패 기록)
  SURVIVED    detector 가 통과시킴 = 게이트 구멍 (이 하네스의 실패 조건)
  VACUOUS     control 에서도 detector 가 아무것도 검사하지 않음(빈 입력/스킵) = 통과가 무의미
  BROKEN      detector 가 control(무결)에서 실패 = 오탐, 케이스/도구 문제
  NOT_TESTED  실행 못 함(전제 데이터·GPU 부재 등) — 정직 기록(방법론 §10)

control-vs-mutated 델타: control 이 통과(0)하고 mutated 가 거부(≠0)일 때만 CAUGHT.
control 도 mutated 도 같은 결과면 그 detector 는 이 mutation 을 구속하지 못한다.

사용:
    python3 evals/validation_harness/run_validation.py            # 전체
    python3 evals/validation_harness/run_validation.py --case split_leak_patient
    python3 evals/validation_harness/run_validation.py --strict   # SURVIVED/VACUOUS 있으면 exit 1
"""
import argparse, csv, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES = Path(__file__).resolve().parent / "cases"

CAUGHT, SURVIVED, VACUOUS, BROKEN, NOT_TESTED = "CAUGHT", "SURVIVED", "VACUOUS", "BROKEN", "NOT_TESTED"


# ── detector 어댑터 ────────────────────────────────────────────────────────
# 조사 실측(2026-08-06): 두 detector 는 종료코드 계약이 서로 다르다. 어댑터로 흡수한다.
#  - verify_split_integrity.py : 실패를 bare assert 로 알림(AssertionError→exit 1, 보고서 미기록).
#                               python -O 에서는 assert 가 사라져 조용히 통과 → 하네스는 -O 를 쓰지 않는다.
#  - auto_review_gate.py       : verdict 와 무관하게 항상 exit 0 → 종료코드가 아니라 보고서를 읽어야 한다.

def run_split_integrity(manifest: Path, out: Path):
    """returns (ok, detail). ok=True 면 detector 가 '무결'로 판정."""
    script = REPO / "agents/modeling/scripts/verify_split_integrity.py"
    if not script.exists():
        return None, f"detector 없음: {script}"
    p = subprocess.run([sys.executable, str(script), "--manifest", str(manifest), "--out", str(out)],
                       capture_output=True, text=True, cwd=str(REPO))
    return p.returncode == 0, (p.stdout + p.stderr)


def rows_actually_checked(stdout: str) -> int:
    """detector 가 실제로 몇 행을 봤는지 — 0 이면 공허한 통과(VACUOUS) 판정 근거."""
    try:
        start = stdout.index("{")
        d = json.loads(stdout[start:stdout.rindex("}") + 1])
        return sum(d.get("n_rows_per_split", {}).values())
    except Exception:
        return -1


# ── mutation: split 누수 (★ BIOP02 최악의 실수) ────────────────────────────

def make_split_manifest(src_split: Path, dst: Path, mutation: str):
    """정본 split.csv 로부터 detector 입력(manifest)을 만들고, 요청된 변조를 심는다.

    mutation:
      none            무결 control
      patient_leak    test 환자 1명을 train 에도 추가(같은 환자 양쪽) ← 가장 비싼 실수
      site_leak       test 기관(tss)의 환자를 train 에 추가(기관 누수)
      drop_split_col  split 컬럼 자체를 제거(도구가 조용히 스킵하는지 시험)
    """
    rows = list(csv.DictReader(src_split.open()))
    if mutation == "drop_split_col":
        with dst.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["case_id", "tss_code"])
            w.writeheader()
            for r in rows:
                w.writerow({"case_id": r["case_id"], "tss_code": r["tss_code"]})
        return {"n": len(rows), "note": "split 컬럼 제거"}

    out = [dict(r) for r in rows]
    detail = {}
    if mutation == "patient_leak":
        victim = next(r for r in rows if r["split"] == "test")
        out.append({**victim, "split": "train"})     # 같은 case_id 가 train·test 양쪽에
        detail = {"leaked_case": victim["case_id"]}
    elif mutation == "site_leak":
        test_sites = {r["tss_code"] for r in rows if r["split"] == "test"}
        site = sorted(test_sites)[0]
        victim = next(r for r in rows if r["split"] == "test" and r["tss_code"] == site)
        # 같은 기관의 '다른' 환자 id 를 train 에 심는다(환자 누수 아님, 기관 누수만)
        fake = {"case_id": f"TCGA-{site}-9X9X", "tss_code": site, "split": "train"}
        out.append(fake)
        detail = {"leaked_site": site, "injected": fake["case_id"], "same_site_as": victim["case_id"]}

    with dst.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "tss_code", "split"])
        w.writeheader()
        w.writerows(out)
    detail["n"] = len(out)
    return detail


def case_split_leakage(cohort: str, mutation: str):
    src = REPO / f"experiments/crosscancer/{cohort}/full/split.csv"
    if not src.exists():
        return NOT_TESTED, f"정본 split 없음: {src}", {}
    tmp = Path(tempfile.mkdtemp(prefix="vh_"))
    try:
        ctrl, mut = tmp / "control.csv", tmp / "mutated.csv"
        make_split_manifest(src, ctrl, "none")
        detail = make_split_manifest(src, mut, mutation)

        ok_c, out_c = run_split_integrity(ctrl, tmp / "c.json")
        if ok_c is None:
            return NOT_TESTED, out_c, detail
        seen = rows_actually_checked(out_c)
        if seen == 0:
            return VACUOUS, "control 에서 검사된 행 0 — 통과가 무의미(입력 스키마 불일치)", detail
        if not ok_c:
            return BROKEN, f"control(무결)에서 실패 — 오탐:\n{out_c[-400:]}", detail

        ok_m, out_m = run_split_integrity(mut, tmp / "m.json")
        if ok_m:
            return SURVIVED, f"변조본을 통과시킴(검사행 {rows_actually_checked(out_m)})", detail
        return CAUGHT, _first_err(out_m), detail
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _first_err(s: str) -> str:
    for line in s.splitlines():
        if "leakage" in line or "AssertionError" in line:
            return line.strip()[:200]
    return s.strip().splitlines()[-1][:200] if s.strip() else ""


# ── mutation: 실제 산출물 manifest 로 detector 를 부를 때 ────────────────────

def case_real_manifest_vacuous():
    """실무 그대로: embedding_manifest 를 detector 에 물리면 무엇이 일어나는가.

    문서화된 사용법(verify_split_integrity.py 헤더)은 embedding_manifest 를 --manifest 로 준다.
    그런데 그 CSV 에 split 컬럼이 있는지가 계약의 핵심이다 — 없으면 전 행이 스킵되어
    '무결'로 통과한다. 이 케이스는 그 계약을 실증한다(변조 없음, 실물 그대로).
    """
    cands = sorted((REPO / "experiments/crosscancer").glob("*/full/embedding_manifest_*.csv"))
    if not cands:
        return NOT_TESTED, "embedding_manifest 없음", {}
    man = cands[0]
    cols = next(csv.reader(man.open()))
    tmp = Path(tempfile.mkdtemp(prefix="vh_"))
    try:
        ok, out = run_split_integrity(man, tmp / "r.json")
        if ok is None:
            return NOT_TESTED, out, {"manifest": str(man.relative_to(REPO))}
        seen = rows_actually_checked(out)
        detail = {"manifest": str(man.relative_to(REPO)), "columns": cols, "rows_checked": seen}
        if "split" not in cols and ok and seen == 0:
            return VACUOUS, "split 컬럼이 없어 전 행 스킵 → 아무것도 검사하지 않고 통과", detail
        return (CAUGHT if not ok else SURVIVED), f"검사행 {seen}", detail
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── mutation: critic_report 7항목 위조 ──────────────────────────────────────

def case_critic_forgery():
    """데이터가 뒷받침하지 않는데 7항목을 pass 로 적으면 잡히는가.

    현재 BIOP02 에 '보고서의 pass 주장 ↔ 증거파일' 대조 게이트가 커밋돼 있는지를 본다.
    없으면 SURVIVED 가 정답이며, 그것이 이 하네스가 드러내야 할 구멍이다.
    """
    src = REPO / "experiments/crosscancer/critic_report.json"
    if not src.exists():
        return NOT_TESTED, f"critic_report 없음: {src}", {}
    rep = json.loads(src.read_text())
    checks = rep.get("checks") or rep.get("checklist") or {}
    forged = {k: {"status": "pass", "evidence": [], "notes": "forged by validation harness"}
              for k in checks}
    detail = {"n_items": len(checks), "items": sorted(checks)}
    # 증거 리스트가 빈 채 전 항목 pass — 이를 거부하는 검증기가 있는가?
    gate = REPO / "agents/critic/auto_review_gate.py"
    if not gate.exists():
        return NOT_TESTED, "auto_review_gate 없음", detail
    tmp = Path(tempfile.mkdtemp(prefix="vh_"))
    try:
        d = tmp / "exp"; d.mkdir()
        (d / "critic_report.json").write_text(json.dumps({**rep, "checks": forged}, indent=2))
        (d / "mil_cost_results.json").write_text(json.dumps({"endpoints": {}}))
        p = subprocess.run([sys.executable, str(gate), str(d), "--write"],
                           capture_output=True, text=True, cwd=str(REPO))
        gp = d / "gate_report.json"
        verdict_txt = gp.read_text() if gp.exists() else (p.stdout + p.stderr)
        # auto_review_gate 는 항상 exit 0 → 보고서를 읽어 판정한다(어댑터).
        blocked = ("blocked" in verdict_txt) or ("needs_human" in verdict_txt)
        detail["gate_exit"] = p.returncode
        return (CAUGHT if blocked else SURVIVED), \
               ("gate 가 blocked/needs_human 로 막음" if blocked
                else "증거 없는 전항목 pass 를 통과시킴 — 위조 대조 게이트 부재"), detail
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── mutation: 원고 수치 드리프트 ────────────────────────────────────────────

def case_number_drift():
    """헤드라인 수치를 몰래 바꾸면 check_number_drift 가 잡는가.

    공정한 시험을 위해 두 조건을 지킨다(2026-08-06 실측으로 교정):
      1) 변조 위치는 detector 의 v1 범위인 **endpoint 1:1 행 표**(LAW_HELDOUT_SCOREBOARD)로 한다.
         prose·FM별 표는 도구가 범위 밖이라고 문서화했으므로 거기서의 미검출은 결함이 아니다.
      2) 위조값은 **어느 정본 JSON 에도 없는 값**을 쓴다. 정본에 존재하는 값으로 바꾸면
         도구가 '알려진 값'으로 통과시키는 게 정상이며, 그건 도구의 구멍이 아니다.
    """
    det = REPO / "agents/critic/scripts/check_number_drift.py"
    doc = REPO / "experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md"
    if not det.exists() or not doc.exists():
        return NOT_TESTED, "detector 또는 스코어보드 없음", {}
    orig = doc.read_text()
    TRUE, FAKE = "0.939", "0.9233"   # 0.9233 은 정본 JSON 어디에도 없음(사전 확인)
    if TRUE not in orig:
        return NOT_TESTED, f"기준 수치({TRUE})가 스코어보드에 없음", {}
    try:
        c = subprocess.run([sys.executable, str(det), "--strict"], capture_output=True, text=True, cwd=str(REPO))
        doc.write_text(orig.replace(TRUE, FAKE))
        m = subprocess.run([sys.executable, str(det), "--strict"], capture_output=True, text=True, cwd=str(REPO))
        detail = {"doc": doc.name, "control_exit": c.returncode, "mutated_exit": m.returncode,
                  "mutation": f"{TRUE}→{FAKE} (정본 부재값)"}
        if c.returncode != 0:
            return BROKEN, "control 에서 이미 드리프트 보고 — 기준선 오염", detail
        return (CAUGHT if m.returncode != 0 else SURVIVED), \
               ("--strict 가 드리프트로 차단" if m.returncode != 0 else "변조 수치를 통과시킴"), detail
    finally:
        doc.write_text(orig)   # 원본 복원(정본 훼손 금지)


# ── 케이스 등록 ────────────────────────────────────────────────────────────

REGISTRY = [
    ("split_leak_patient", "★환자 누수 — test 환자를 train 에도 넣음",
     lambda: case_split_leakage("LUNG_NSCLC", "patient_leak"), "verify_split_integrity.py"),
    ("split_leak_site", "★기관 누수 — test 기관 환자를 train 에 넣음",
     lambda: case_split_leakage("LUNG_NSCLC", "site_leak"), "verify_split_integrity.py"),
    ("split_drop_column", "split 컬럼 제거 — 도구가 조용히 스킵하는가",
     lambda: case_split_leakage("LUNG_NSCLC", "drop_split_col"), "verify_split_integrity.py"),
    ("real_manifest_contract", "실물 embedding_manifest 로 부를 때의 계약(변조 없음)",
     case_real_manifest_vacuous, "verify_split_integrity.py"),
    ("critic_report_forgery", "critic 7항목을 증거 없이 전부 pass 로 위조",
     case_critic_forgery, "auto_review_gate.py"),
    ("manuscript_number_drift", "스코어보드 헤드라인 수치 위조(0.939→0.9233, 정본 부재값)",
     case_number_drift, "check_number_drift.py --strict"),
]

# 이번 판에서 실행하지 못한 항목 — 정직 기록(방법론 §10). 없는 척하지 않는다.
NOT_TESTED_ITEMS = [
    ("operating_point_tamper", "임계 조작으로 지표 부풀리기",
     "operating-point 산출물(BIOP02-124)이 아직 없음 — 나오면 케이스 추가"),
    ("citation_fabrication", "가짜 인용", "evals/citation_verifier 가 이미 커버(중복 방지)"),
]


def main():
    ap = argparse.ArgumentParser(description="BIOP02 도메인 mutation 검수 하네스")
    ap.add_argument("--case", help="특정 케이스만 실행")
    ap.add_argument("--strict", action="store_true", help="SURVIVED/VACUOUS/BROKEN 있으면 exit 1")
    ap.add_argument("--json", dest="out", help="결과 JSON 경로")
    a = ap.parse_args()

    rows, bad = [], 0
    print("=== BIOP02 검수 하네스 — control vs mutated ===\n")
    for name, desc, fn, detector in REGISTRY:
        if a.case and a.case != name:
            continue
        try:
            verdict, note, detail = fn()
        except Exception as e:
            verdict, note, detail = BROKEN, f"{type(e).__name__}: {e}", {}
        mark = {CAUGHT: "✓", SURVIVED: "✗", VACUOUS: "!", BROKEN: "!", NOT_TESTED: "-"}[verdict]
        if verdict in (SURVIVED, VACUOUS, BROKEN):
            bad += 1
        print(f"[{mark} {verdict:10}] {name:26} {desc}")
        print(f"{'':15}detector: {detector}")
        if note:
            print(f"{'':15}→ {note}")
        rows.append({"case": name, "desc": desc, "detector": detector,
                     "verdict": verdict, "note": note, "detail": detail})

    print("\n" + "=" * 78)
    for name, desc, why in NOT_TESTED_ITEMS:
        print(f"[- NOT_TESTED] {name:26} {desc}\n{'':15}→ {why}")
        rows.append({"case": name, "desc": desc, "detector": None,
                     "verdict": NOT_TESTED, "note": why, "detail": {}})

    n_caught = sum(1 for r in rows if r["verdict"] == CAUGHT)
    n_hole = sum(1 for r in rows if r["verdict"] in (SURVIVED, VACUOUS))
    print(f"\n적발 {n_caught} / 게이트 구멍 {n_hole} / 미검사 "
          f"{sum(1 for r in rows if r['verdict'] == NOT_TESTED)} (총 {len(rows)})")
    print("⚠️ 이 표는 '게이트가 이 실수를 구속하는가'를 잰다. 초록색이 결함 부재를 뜻하지 않는다.")

    if a.out:
        Path(a.out).write_text(json.dumps({"results": rows}, ensure_ascii=False, indent=2))
        print(f"Saved: {a.out}")
    return 1 if (a.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())

"""게이트 공허통과 회귀 테스트 (BIOP02-130/131 수정 + BIOP02-136 잔여분).

이 프로젝트가 반복해 만난 실패 모양은 하나다 — **검사하지 못한 것을 통과로 처리하는 것**
(CLAUDE.md 금지항목 "도구가 '못 찾겠다'고 한 것을 통과로 처리하는 것").
게이트가 그 실패를 다시 만들지 않는지 합성 픽스처로 못 박는다.

각 케이스는 "이 입력에서 게이트가 **실패해야 한다**"를 검증한다. 통과 케이스도 함께 둔다 —
차단만 늘리고 정상 입력을 막으면 아무도 게이트를 켜지 않기 때문이다.

Run:
    python3 agents/critic/tests/test_gate_vacuous_pass.py
    (pytest 도 됨: pytest agents/critic/tests/test_gate_vacuous_pass.py)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERIFY_SPLIT = ROOT / "agents/modeling/scripts/verify_split_integrity.py"
REVIEW_GATE = ROOT / "agents/critic/auto_review_gate.py"

# --- 픽스처: (파일명, 내용, 기대 exit, 기대 reason) --------------------------
SPLIT_CASES = [
    ("no_split.csv",
     "slide_id,case_id,embedding_path\nS1,TCGA-AA-1111,/x/a.pt\nS2,TCGA-BB-2222,/x/b.pt\n",
     1, "missing_required_columns",
     "split 컬럼 부재 — 문서가 사용법으로 제시했던 embedding_manifest 경로 (BIOP02-130)"),
    ("header_only.csv",
     "slide_id,case_id,split\n",
     1, "no_rows_checked",
     "검사행 0 — '검사할 게 없었다'는 무결의 증거가 아니다 (BIOP02-130)"),
    ("single_group.csv",
     "slide_id,case_id,split\nS1,TCGA-AA-1111,train\nS2,TCGA-AA-1111,train\n",
     1, "single_split_group",
     "split 그룹 1개 — 대조 상대가 없어 disjoint 가 자명하게 성립 (BIOP02-136)"),
    ("leak.csv",
     "slide_id,case_id,split\nS1,TCGA-AA-1111,train\nS2,TCGA-AA-1111,test\n",
     1, "leakage",
     "실제 환자 누수 — 탐지 기능이 살아 있는지(차단만 늘고 탐지가 죽지 않았는지)"),
    ("ok.csv",
     "slide_id,case_id,split\nS1,TCGA-AA-1111,train\nS2,TCGA-BB-2222,test\n",
     0, None,
     "정상 입력 — 오탐 회귀 방지"),
]

FORGED_REPORT = {
    "checks": {
        "data_leakage": {"status": "pass", "evidence": []},
        "counterfactual": {"status": "pass", "evidence": ["evidence/nonexistent.json"]},
    },
    "critic_status": "pass", "claim_level": "hypothesis_only",
}
CLEAN_REPORT = {
    "checks": {
        "data_leakage": {"status": "pass",
                         "evidence": ["근거: split.csv site/case overlap 0 (재계산 확인)"]},
    },
    "critic_status": "pass", "claim_level": "hypothesis_only",
}


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode


def check_verify_split(tmp):
    fails = []
    for name, content, want_exit, want_reason, why in SPLIT_CASES:
        src = tmp / name
        src.write_text(content)
        out = tmp / f"{name}.result.json"
        rc = _run([sys.executable, str(VERIFY_SPLIT), "--manifest", str(src), "--out", str(out)])
        reason = None
        if out.exists():
            reason = json.loads(out.read_text()).get("reason")
        ok = (rc == want_exit) and (want_reason is None or reason == want_reason)
        print(f"  [{'OK ' if ok else 'FAIL'}] verify_split/{name}: "
              f"exit={rc}(기대 {want_exit}) reason={reason}(기대 {want_reason}) — {why}")
        if not ok:
            fails.append(name)
    return fails


def check_review_gate(tmp):
    fails = []
    forged = tmp / "forged_exp"
    forged.mkdir()
    (forged / "critic_report.json").write_text(json.dumps(FORGED_REPORT, ensure_ascii=False))
    clean = tmp / "clean_exp"
    clean.mkdir()
    (clean / "critic_report.json").write_text(json.dumps(CLEAN_REPORT, ensure_ascii=False))
    missing = tmp / "NO_SUCH_DIR"

    cases = [
        (forged, ["--strict"], 1, "증거 없는 pass 는 --strict 에서 차단 (BIOP02-131)"),
        (forged, [], 0, "기본 종료코드는 기존 호출부 호환 유지"),
        (missing, ["--strict"], 1, "경로 부재를 통과로 치지 않음 (BIOP02-136)"),
        (missing, [], 0, "경로 부재도 기본은 호환 유지"),
        (clean, ["--strict"], 0, "정상 리포트 — 오탐 회귀 방지"),
    ]
    for target, flags, want, why in cases:
        rc = _run([sys.executable, str(REVIEW_GATE), str(target), *flags])
        ok = rc == want
        label = f"{target.name}{' --strict' if flags else ''}"
        print(f"  [{'OK ' if ok else 'FAIL'}] review_gate/{label}: exit={rc}(기대 {want}) — {why}")
        if not ok:
            fails.append(label)
    return fails


def main():
    print("게이트 공허통과 회귀 테스트 (BIOP02-130/131/136)\n")
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        print("① verify_split_integrity.py")
        f1 = check_verify_split(tmp)
        print("\n② auto_review_gate.py")
        f2 = check_review_gate(tmp)
    total = len(SPLIT_CASES) + 5
    fails = f1 + f2
    print(f"\n결과: {total - len(fails)}/{total} 통과")
    if fails:
        print("실패:", ", ".join(fails))
        return 1
    return 0


# pytest 진입점
def test_gate_vacuous_pass():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())

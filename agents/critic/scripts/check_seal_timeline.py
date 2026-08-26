#!/usr/bin/env python3
"""회고적 사전등록 탐지 게이트 (Registry-Replay A2 → gate).

"sealed-forward"라 주장한 예측이 실제로는 결과보다 늦게 커밋됐는지를 git 커밋 시각으로 검증한다.
PITFALLS A2("봉인의 진위는 시각이 가른다") + Registry-Replay MISSED 3건 중 최우선 구멍을 메운다.
7종 CI 중 git 이력을 보는 게이트가 없어 이 사고를 못 잡았다 — 이 스크립트가 8번째 게이트다.

입력: seal manifest JSON
  {"seals": [
     {"claim": "폐 histology sealed-forward",
      "prediction_commit": "<sha>",  "result_commit": "<sha>"},        # 방식 A: 커밋 SHA
     {"claim": "...", "prediction_path": "<file>", "result_path": "<file>"}  # 방식 B: 파일 마지막 커밋
  ]}

판정: 각 seal에 대해 prediction 커밋 시각 < result 커밋 시각 이어야 통과.
      prediction >= result 이면 회고적(retrospective)이므로 "sealed-forward" 주장 무효 → FAIL.
규약: 결정론(커밋 시각은 불변). 게이트를 점수 좋게 손대는 것 금지(A5 골대이동).
"""
import argparse, json, subprocess, sys
from pathlib import Path


def commit_ct(sha: str) -> int:
    """커밋 SHA의 committer timestamp(epoch). 실패 시 예외."""
    out = subprocess.run(["git", "show", "-s", "--format=%ct", sha],
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise ValueError(f"커밋 시각 조회 실패: {sha} ({out.stderr.strip()})")
    return int(out.stdout.strip().splitlines()[-1])


def path_last_ct(path: str) -> int:
    """파일 경로의 마지막 커밋 committer timestamp(epoch)."""
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise ValueError(f"경로 커밋 시각 조회 실패: {path} ({out.stderr.strip()})")
    return int(out.stdout.strip())


def resolve(seal: dict):
    if "prediction_commit" in seal and "result_commit" in seal:
        return commit_ct(seal["prediction_commit"]), commit_ct(seal["result_commit"])
    if "prediction_path" in seal and "result_path" in seal:
        return path_last_ct(seal["prediction_path"]), path_last_ct(seal["result_path"])
    raise ValueError(f"seal에 prediction/result (commit 또는 path) 쌍이 없음: {seal.get('claim')}")


def main() -> int:
    ap = argparse.ArgumentParser(description="회고적 사전등록 탐지 게이트")
    ap.add_argument("manifest", help="seal manifest JSON")
    ap.add_argument("--json", help="결과 JSON 출력 경로")
    a = ap.parse_args()

    data = json.loads(Path(a.manifest).read_text())
    seals = data.get("seals", [])
    if not seals:
        print("[check_seal_timeline] seal 0건 — 검사 대상 없음(통과)")
        return 0

    results, failed = [], 0
    for s in seals:
        claim = s.get("claim", "(unnamed)")
        try:
            pred_ct, res_ct = resolve(s)
        except ValueError as e:
            print(f"  ERROR {claim}: {e}")
            results.append({"claim": claim, "verdict": "ERROR", "detail": str(e)})
            failed += 1
            continue
        ok = pred_ct < res_ct
        verdict = "SEALED-FORWARD" if ok else "RETROSPECTIVE"
        if not ok:
            failed += 1
        print(f"  {'PASS' if ok else 'FAIL'} {claim}: prediction_ct={pred_ct} "
              f"{'<' if ok else '>='} result_ct={res_ct} → {verdict}")
        results.append({"claim": claim, "prediction_ct": pred_ct,
                        "result_ct": res_ct, "verdict": verdict})

    summary = {"n_seals": len(seals), "n_failed": failed,
               "pass": failed == 0, "results": results}
    if a.json:
        Path(a.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    if failed:
        print(f"[check_seal_timeline] FAIL — {failed}/{len(seals)}건이 회고적(예측이 결과보다 늦음). "
              f"'sealed-forward' 주장 무효.")
        return 1
    print(f"[check_seal_timeline] PASS — {len(seals)}건 모두 예측이 결과보다 먼저 커밋됨.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

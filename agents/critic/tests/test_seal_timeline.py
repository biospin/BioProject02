#!/usr/bin/env python3
"""check_seal_timeline 게이트 자기검증 (비공허 mutation 테스트).

게이트가 "통과만 하는" 공허한 게이트가 아님을 증명한다:
  - 정상(예측이 결과보다 먼저 커밋) → PASS(exit 0)
  - mutant(예측이 결과보다 늦게 = 회고적) → FAIL(exit 1)
둘 다 기대대로여야 이 테스트가 통과한다. (critic-validators.yml의 게이트 mutation 규율)

임시 git 저장소를 만들어 커밋 시각을 GIT_COMMITTER_DATE로 통제한다 — 결정론·자기완결.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parents[1] / "scripts" / "check_seal_timeline.py"


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def git_commit(repo, fname, when_epoch, env0):
    (Path(repo) / fname).write_text(fname + "\n")
    run(["git", "add", fname], repo, env0)
    env = dict(env0)
    env["GIT_AUTHOR_DATE"] = f"{when_epoch} +0000"
    env["GIT_COMMITTER_DATE"] = f"{when_epoch} +0000"
    run(["git", "commit", "-m", f"add {fname}"], repo, env)
    sha = run(["git", "rev-parse", "HEAD"], repo, env0).stdout.strip()
    return sha


def main() -> int:
    with tempfile.TemporaryDirectory() as repo:
        env0 = dict(os.environ)
        env0["GIT_AUTHOR_NAME"] = env0["GIT_COMMITTER_NAME"] = "test"
        env0["GIT_AUTHOR_EMAIL"] = env0["GIT_COMMITTER_EMAIL"] = "test@test"
        run(["git", "init", "-q"], repo, env0)
        sha_pred = git_commit(repo, "prediction.txt", 1_700_000_000, env0)   # 먼저
        sha_res  = git_commit(repo, "result.txt",     1_700_009_999, env0)   # 나중

        ok_manifest = Path(repo) / "ok.json"
        ok_manifest.write_text(json.dumps({"seals": [
            {"claim": "정상 sealed-forward", "prediction_commit": sha_pred, "result_commit": sha_res}]}))
        mut_manifest = Path(repo) / "mut.json"
        mut_manifest.write_text(json.dumps({"seals": [
            {"claim": "회고적 mutant", "prediction_commit": sha_res, "result_commit": sha_pred}]}))

        r_ok  = run([sys.executable, str(GATE), str(ok_manifest)], repo, env0)
        r_mut = run([sys.executable, str(GATE), str(mut_manifest)], repo, env0)

        pass_ok  = r_ok.returncode == 0
        fail_mut = r_mut.returncode == 1
        print("정상 케이스 exit", r_ok.returncode, "(기대 0):", "OK" if pass_ok else "실패")
        print("mutant 케이스 exit", r_mut.returncode, "(기대 1):", "OK" if fail_mut else "실패")
        if pass_ok and fail_mut:
            print("✅ 게이트 비공허 확인 — 정상 통과 + 회고적 검출")
            return 0
        print("❌ 게이트가 공허하거나 오작동")
        print("  ok stdout:", r_ok.stdout.strip()[:200])
        print("  mut stdout:", r_mut.stdout.strip()[:200])
        return 1


if __name__ == "__main__":
    sys.exit(main())

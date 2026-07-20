#!/usr/bin/env python3
"""multifm_retrain_watcher.py — 다중 FM 임베딩 완료를 감지해 CLAM 재학습 자동 실행.

kkkim(Owner) 대행. Paper C 모델 비의존성 검정용. run_mil_cost.py를 --fm virchow2/uni2h로
호출한다. 대상 코호트 = CANCER_CFG에 있는 것(COLORECTAL·LUNG_NSCLC).

로직(idempotent, 재기동 안전):
- 각 (코호트, FM) 조합에 대해:
  * 임베딩이 목표 수(TARGET)에 도달했고, 아직 결과(mil_cost_results_<fm>.json)가 없으면 학습 실행.
  * 이미 결과 있으면 스킵.
- 임베딩 미완이면 대기(폴링). 모든 조합 완료되면 종료.

⚠️ Owner != Reviewer: 이 러너가 낸 결과는 critic_status: pending. sjpark/braveji 크로스체크 필수.
로그: multifm_retrain.log
"""
import subprocess, time, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = "/opt/envs/spatialpatho/bin/python"
RUN = HERE / "run_mil_cost.py"
LOG = HERE / "multifm_retrain.log"

# 대상: (코호트, 목표 임베딩 수).
# 2026-07-21 확장: 두경부·위 추가. 임베딩이 이미 끝났는데 폐(0/1052)를 기다리느라
# 재학습이 안 돌던 빈틈을 메움. 특히 두경부는 우리 유일한 검정력 있는 CONFIRM(HPV 0.9594)이 있어
# 다른 FM에서 재현되는지가 모델 비의존성 주장에 가장 값짐.
COHORTS = {"COLORECTAL": 622, "LUNG_NSCLC": 1052, "HEADNECK_HNSC": 472, "GASTRIC_STAD": 442}
# 암종별 실행 스크립트: 폐·대장=run_mil_cost.py(CANCER_CFG 보유) / 두경부·위=sh_mil_cost.py(격리판)
SCRIPT_BY_COHORT = {"COLORECTAL": "run_mil_cost.py", "LUNG_NSCLC": "run_mil_cost.py",
                    "HEADNECK_HNSC": "sh_mil_cost.py", "GASTRIC_STAD": "sh_mil_cost.py"}
FMS = ["virchow2", "uni2h"]
EMB = "/workspace/data/cache/biop02/{lc}/{fm}"
POLL_SEC = 600          # 10분 폴링
DEVICES = ["cuda:0", "cuda:1", "cuda:2"]


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def emb_count(cancer, fm):
    d = Path(EMB.format(lc=cancer.lower(), fm=fm))
    return len(list(d.glob("*_embeddings.npy"))) if d.exists() else 0


def result_exists(cancer, fm):
    return (HERE / cancer / "full" / f"mil_cost_results_{fm}.json").exists()


def train(cancer, fm, device):
    log(f"▶ 재학습 시작: {cancer} / {fm} (device={device})")
    t0 = time.time()
    script = HERE / SCRIPT_BY_COHORT.get(cancer, "run_mil_cost.py")
    r = subprocess.run([PY, str(script), "--cancer", cancer, "--fm", fm, "--device", device],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode == 0 and result_exists(cancer, fm):
        log(f"✅ 완료: {cancer}/{fm} ({time.time()-t0:.0f}s) → mil_cost_results_{fm}.json (critic_status pending)")
        return True
    log(f"❌ 실패: {cancer}/{fm} rc={r.returncode} :: {r.stderr[-300:]}")
    return False


def main():
    log(f"=== MULTIFM RETRAIN WATCHER start — 대상 {list(COHORTS)} × {FMS} ===")
    log("⚠️ Owner(kkkim 대행)=이 러너. Reviewer=sjpark/braveji 크로스체크 필수. 결과 critic_status pending.")
    pending = {(c, fm) for c in COHORTS for fm in FMS}
    di = 0
    while pending:
        done_now = set()
        for (c, fm) in sorted(pending):
            if result_exists(c, fm):
                log(f"skip {c}/{fm}: 결과 이미 있음"); done_now.add((c, fm)); continue
            n = emb_count(c, fm)
            if n >= COHORTS[c]:
                dev = DEVICES[di % len(DEVICES)]; di += 1
                if train(c, fm, dev):
                    done_now.add((c, fm))
            else:
                log(f"대기 {c}/{fm}: 임베딩 {n}/{COHORTS[c]}")
        pending -= done_now
        if pending:
            time.sleep(POLL_SEC)
    log("=== 모든 (코호트,FM) 재학습 완료 — WATCHER end. Reviewer 크로스체크로 넘어갈 것 ===")
    (HERE / "MULTIFM_RETRAIN_DONE").write_text(time.strftime("%F %T") + "\n")


if __name__ == "__main__":
    main()

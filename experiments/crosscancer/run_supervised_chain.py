#!/usr/bin/env python3
"""
Cross-cancer supervised 자동 체인 (임베딩 완료 감지 → 라벨 → split → MIL+cost).

- 게이트: 임베딩 master(run_embed --cancers) 전부 종료 시 시작(GPU 경합 회피, advisor).
  종료 후 실제 임베딩 수를 목표(폐1053/대장625) 대비 로깅(누락 명시, 가짜 완료 금지).
- 단계: fetch_labels.py → make_split.py → run_mil_cost.py(암종별, GPU 분산).
  각 단계 실패 시 해당 암종만 중단·로깅(다른 암종 계속). 결과=<cancer>/full/mil_cost_results.json.
- detached-safe: 하트비트 + DONE sentinel. 재실행 시 이미 있는 결과는 건너뜀(--force로 재계산).
"""
import subprocess, time, json, sys
from pathlib import Path

HERE = Path(__file__).parent
PY = "/home/kkkim/miniconda3/bin/python3"
TARGET = {"LUNG_NSCLC": 1053, "COLORECTAL": 625}
HB = HERE / "SUPERVISED_HEARTBEAT.log"

def log(m):
    line=f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(HB,"a") as f: f.write(line+"\n")

def embed_masters_alive():
    r=subprocess.run(["bash","-c","ps -eo cmd | grep 'run_embed_crosscancer.py --cancers' | grep -v grep | wc -l"],
                     capture_output=True, text=True)
    return int(r.stdout.strip() or "0")

def emb_count(cancer):
    return len(list((HERE/cancer/"full"/"embeddings").glob("*_uni_embeddings.npy")))

def run(cmd, tag, timeout):
    log(f"  RUN {tag}: {' '.join(cmd[-3:])}")
    r=subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode!=0:
        log(f"  FAIL {tag} rc={r.returncode}: {r.stderr[-500:]}")
        return False
    log(f"  OK {tag}\n{r.stdout[-800:]}")
    return True

def main():
    force = "--force" in sys.argv
    log(f"=== SUPERVISED CHAIN start (force={force}) — 임베딩 완료 대기 ===")
    # 1) 임베딩 master 종료 대기(폴링 10분)
    while embed_masters_alive() > 0:
        counts={c:emb_count(c) for c in TARGET}
        log(f"  임베딩 진행 중 (master {embed_masters_alive()}): {counts} — 대기")
        time.sleep(600)
    counts={c:emb_count(c) for c in TARGET}
    log(f"임베딩 master 종료 확인. 최종 임베딩 수: {counts} / 목표 {TARGET}")
    for c,t in TARGET.items():
        miss=t-counts[c]
        if miss>0: log(f"  ⚠️ {c}: {miss}장 누락({counts[c]}/{t}) — 실패/손상 슬라이드. MIL은 있는 것으로 진행(누락 명시).")

    # 2) 라벨 + split (GPU 0, idempotent)
    run([PY, str(HERE/"fetch_labels.py")], "fetch_labels", 900)
    run([PY, str(HERE/"make_split.py")], "make_split", 300)

    # 3) MIL + cost (암종별, GPU 분산: 폐=cuda:0, 대장=cuda:1)
    gpu={"LUNG_NSCLC":"cuda:0","COLORECTAL":"cuda:1"}
    for cancer in TARGET:
        out=HERE/cancer/"full"/"mil_cost_results.json"
        if out.exists() and not force:
            log(f"  {cancer}: 결과 이미 존재 — skip(--force로 재계산)"); continue
        ok=run([PY, str(HERE/"run_mil_cost.py"), "--cancer", cancer, "--device", gpu[cancer]],
               f"mil_cost:{cancer}", 14400)
        if not ok: log(f"  {cancer}: MIL 실패 — 다음 암종 계속")

    # 4) 요약
    summary={"finished_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
             "embedding_counts":counts,"targets":TARGET,"results":{}}
    for cancer in TARGET:
        rp=HERE/cancer/"full"/"mil_cost_results.json"
        if rp.exists():
            d=json.loads(rp.read_text())
            eps={ep:{"real":v.get("real",{}).get("auc"),"shuffle":v.get("shuffle_null",{}).get("auc")}
                 for ep,v in d.get("endpoints",{}).items()}
            summary["results"][cancer]={"endpoints":eps,"pos_control":d.get("positive_control_gate"),
                                        "cost":d.get("cost_of_substitution",{}).get("per_axis")}
    (HERE/"SUPERVISED_DONE.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    log(f"=== SUPERVISED CHAIN DONE ===\n{json.dumps(summary,indent=2,ensure_ascii=False)}")

if __name__=="__main__":
    main()

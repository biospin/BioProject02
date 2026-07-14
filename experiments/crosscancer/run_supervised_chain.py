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

def embed_master_alive(cancer):
    """해당 암종 임베딩 master가 살아있나(--cancers <cancer>)."""
    r=subprocess.run(["bash","-c",
        f"ps -eo cmd | grep 'run_embed_crosscancer.py --cancers {cancer}' | grep -v grep | wc -l"],
        capture_output=True, text=True)
    return int(r.stdout.strip() or "0") > 0

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
    log(f"=== SUPERVISED CHAIN start (force={force}) — 암종별 임베딩 완료 즉시 실행 ===")
    gpu={"LUNG_NSCLC":"cuda:0","COLORECTAL":"cuda:1"}
    labels_split_done=False
    pending=set(TARGET)
    while pending:
        for cancer in sorted(pending):
            if embed_master_alive(cancer):
                continue                              # 그 암종 아직 임베딩 중
            # --- 이 암종 임베딩 완료 → 즉시 chain ---
            cnt=emb_count(cancer); miss=TARGET[cancer]-cnt
            log(f"[{cancer}] 임베딩 master 종료. {cnt}/{TARGET[cancer]}" +
                (f" ⚠️ {miss}장 누락(실패/손상, 있는 것으로 진행)" if miss>0 else " (완료)"))
            # 라벨+split은 한 번만(양 암종 공통 cBioPortal, 임베딩 무관)
            if not labels_split_done:
                run([PY, str(HERE/"fetch_labels.py")], "fetch_labels", 900)
                run([PY, str(HERE/"make_split.py")], "make_split", 300)
                labels_split_done=True
            out=HERE/cancer/"full"/"mil_cost_results.json"
            if out.exists() and not force:
                log(f"  {cancer}: 결과 이미 존재 — skip(--force로 재계산)")
            else:
                ok=run([PY, str(HERE/"run_mil_cost.py"), "--cancer", cancer, "--device", gpu[cancer]],
                       f"mil_cost:{cancer}", 14400)
                if not ok: log(f"  {cancer}: MIL 실패 — 다음 암종 계속")
            pending.discard(cancer)
        if pending:
            still={c:emb_count(c) for c in pending}
            log(f"  임베딩 대기 중: {still}")
            time.sleep(300)
    counts={c:emb_count(c) for c in TARGET}

    # 요약
    summary={"finished_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
             "embedding_counts":counts,"targets":TARGET,"results":{}}
    for cancer in TARGET:
        rp=HERE/cancer/"full"/"mil_cost_results.json"
        if rp.exists():
            d=json.loads(rp.read_text())
            eps={ep:{"real":v.get("real",{}).get("auc"),"shuffle":v.get("shuffle_null",{}).get("auc")}
                 for ep,v in d.get("endpoints",{}).items()}
            summary["results"][cancer]={"endpoints":eps,"pos_control":d.get("positive_control_gate"),
                                        "cost_targeted":d.get("cost_of_substitution_targeted",{}).get("per_axis"),
                                        "misroute_incl_histology":d.get("endpoint_misroute_incl_histology")}
    (HERE/"SUPERVISED_DONE.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    log(f"=== SUPERVISED CHAIN DONE ===\n{json.dumps(summary,indent=2,ensure_ascii=False)}")

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""HNSC 임베딩을 물리 GPU2 전용으로 STAD와 '동시' 실행 (다운로드 병렬화).
- 병목=GDC 다운로드(load 4/32 여유), GPU2 유휴 → HNSC를 병렬로 올려 전체 처리율↑.
- 마스터 sh_embed(순차: STAD→HNSC)는 건드리지 않음. 마스터가 나중에 HNSC를 다시 돌려도
  run_embed_crosscancer.process_slide 가 idempotent skip 이라 이 프로세스가 만든 npy는 스킵됨(충돌 없음).
- run_worker 의 --gpu 는 로그 라벨일 뿐, 실제 디바이스는 CUDA_VISIBLE_DEVICES=2 로 고정."""
import os, sys, json, subprocess, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_embed_crosscancer as emb

PY = "/home/kkkim/miniconda3/bin/python3"
CANCER = "HEADNECK_HNSC"
NSHARDS = 3            # GPU2에 다운로드 스트림 3개(compute 여유, 병목=다운로드)
PHYS_GPU = "2"
HB = HERE / "EMBED_HNSC_GPU2_HEARTBEAT.log"

def log(m):
    with open(HB, "a") as f:
        f.write(f"[{time.strftime('%F %T')}] {m}\n")

emb.CANCERS[CANCER] = {"cohorts": ["TCGA-HNSC"]}
dirs = emb.make_dirs(CANCER)

recs, seen = [], set()
for cohort in emb.CANCERS[CANCER]["cohorts"]:
    for h in emb.gdc_query(cohort):
        if h["file_id"] not in seen:
            seen.add(h["file_id"]); recs.append(h)
log(f"HNSC(GPU2) queue = {len(recs)} slides")

shards = [[] for _ in range(NSHARDS)]
for i, r in enumerate(recs):
    shards[i % NSHARDS].append(r)

procs = []
for s in range(NSHARDS):
    if not shards[s]:
        continue
    sp = dirs["out"] / f"shard_hnscGPU2_{s}.json"
    sp.write_text(json.dumps(shards[s]))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=PHYS_GPU)
    # --gpu 는 int 타입(로그 라벨용). 마스터의 0/1/2와 안 겹치게 20+s 사용. 실제 디바이스는 CUDA_VISIBLE_DEVICES=2.
    cmd = [PY, str(HERE / "run_embed_crosscancer.py"), "--worker",
           "--cancer", CANCER, "--shard", str(sp), "--gpu", str(20 + s)]
    p = subprocess.Popen(cmd, env=env)
    procs.append(p)
    log(f"spawned HNSC worker shard{s} -> physGPU2 pid={p.pid} n={len(shards[s])}")

while any(p.poll() is None for p in procs):
    done = len(list(dirs["emb"].glob("*_uni_embeddings.npy")))
    alive = sum(1 for p in procs if p.poll() is None)
    log(f"HNSC(GPU2) heartbeat embeddings={done}/{len(recs)} alive_workers={alive}")
    time.sleep(60)
log("HNSC(GPU2) ALL DONE")

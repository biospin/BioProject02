#!/usr/bin/env python3
"""
STAD·HNSC 임베딩 마스터 (격리판) — run_embed_crosscancer 헬퍼 재사용, 자율 detached.

⚠️ 격리 이유(advisor): run_embed_crosscancer.run_master는 공유 sentinel EMBED_ALL.done를
   무조건 덮어씀(현재 COLORECTAL 트랙 소유) → 그걸 건드리지 않도록 마스터 루프를 자체 구동한다.
   워커는 run_embed_crosscancer.py --worker 그대로 스폰(워커는 CANCERS dict 불필요, make_dirs/process_slide만 씀).

- GDC 진단 WSI(-DX) 스트리밍 → tile → UNI 임베딩, per-slide LRU, idempotent skip.
- 폐 임베딩 동시 진행 중 → 워커 수 제한(기본 총 3 = GPU당 1)로 CPU/IO 포화 회피(I/O bound).
- 별도 sentinel: EMBED_STADHNSC.done / 하트비트: EMBED_STADHNSC_HEARTBEAT.log

Usage: python sh_embed.py [--shards 3] [--limit N]
"""
import argparse, json, os, subprocess, time
from pathlib import Path
import run_embed_crosscancer as emb

ROOT = emb.ROOT
PY = emb.PY
HERE = Path(__file__).parent
HB = HERE / "EMBED_STADHNSC_HEARTBEAT.log"

# 격리 CANCERS(임포트 dict에 주입 — gdc_query 코호트 결정에만 사용)
emb.CANCERS["GASTRIC_STAD"] = {"cohorts": ["TCGA-STAD"]}
emb.CANCERS["HEADNECK_HNSC"] = {"cohorts": ["TCGA-HNSC"]}

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(HB, "a") as f: f.write(line + "\n")

def run_cancer(cancer, nshards, limit):
    dirs = emb.make_dirs(cancer)
    mlog = dirs["out"] / "master.log"
    recs, seen = [], set()
    for cohort in emb.CANCERS[cancer]["cohorts"]:
        hits = emb.gdc_query(cohort)
        for h in hits:
            if h["file_id"] not in seen:
                seen.add(h["file_id"]); recs.append(h)
        emb.log(f"{cancer} {cohort}: {len(hits)} diagnostic slides", mlog)
    recs.sort(key=lambda r: r["size"])
    if limit: recs = recs[:limit]
    log(f"{cancer} QUEUE = {len(recs)} slides")
    (dirs["out"] / "queue.json").write_text(json.dumps(recs, indent=0))
    if not recs:
        log(f"{cancer} 빈 큐 — 스킵"); return 0, 0
    shards = [[] for _ in range(nshards)]
    for i, r in enumerate(recs): shards[i % nshards].append(r)
    procs = []
    for s in range(nshards):
        if not shards[s]: continue
        g = s % 3
        sp = dirs["out"] / f"shard_{s}_gpu{g}.json"
        sp.write_text(json.dumps(shards[s]))
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))
        cmd = [PY, str(emb.Path(emb.__file__).resolve()), "--worker", "--cancer", cancer,
               "--shard", str(sp), "--gpu", str(s)]
        p = subprocess.Popen(cmd, env=env)
        procs.append((s, p))
        log(f"{cancer} spawned worker shard{s}→gpu{g} pid={p.pid} n={len(shards[s])}")
    while any(p.poll() is None for _, p in procs):
        done = len(list(dirs["emb"].glob("*_uni_embeddings.npy")))
        log(f"{cancer} heartbeat: embeddings={done}/{len(recs)} alive={[g for g,p in procs if p.poll() is None]}")
        time.sleep(60)
    n_emb = len(list(dirs["emb"].glob("*_uni_embeddings.npy")))
    log(f"{cancer} COMPLETE embeddings={n_emb}/{len(recs)}")
    emb.build_manifest(cancer, dirs, recs)
    (dirs["out"] / "CANCER.done").write_text(json.dumps({"n_queued": len(recs), "n_emb": n_emb}))
    return len(recs), n_emb

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", type=int, default=3, help="총 워커수(GPU 라운드로빈). 폐 동시진행이면 3 권장")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--cancers", nargs="+", default=["GASTRIC_STAD", "HEADNECK_HNSC"])
    a = ap.parse_args()
    log(f"=== STAD/HNSC MASTER start cancers={a.cancers} shards={a.shards} limit={a.limit} ===")
    summary = {}
    for cancer in a.cancers:
        nq, ne = run_cancer(cancer, a.shards, a.limit)
        summary[cancer] = {"n_queued": nq, "n_emb": ne}
    (HERE / "EMBED_STADHNSC.done").write_text(
        json.dumps({"summary": summary, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                   indent=2, ensure_ascii=False))
    log(f"=== STAD/HNSC MASTER ALL DONE {summary} ===")

if __name__ == "__main__":
    main()

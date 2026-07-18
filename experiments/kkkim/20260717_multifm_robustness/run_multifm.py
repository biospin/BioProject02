#!/usr/bin/env python3
"""
다중 FM 견고성(Paper C: 치환가능성 법칙의 모델 비의존성) — Virchow2 임베딩 드라이버.

목적: 헤드라인 UNI v1(1024-d)로 세운 결정지도가 **FM을 바꿔도 유지되는가**를 검정하기 위한
Virchow2(2560-d) 임베딩 생산. ⚠️ 이 스크립트의 산출물은 **임베딩까지**다 — "법칙이 모델
비의존적이다"는 주장은 sjpark의 downstream CLAM 재학습이 있어야 성립한다(그 전엔 미검증).

`experiments/crosscancer/run_embed_crosscancer.py`(검증된 UNI 드라이버)를 재사용하되 3가지가 다르다:

  1. **모델** = Virchow2(2560-d). extract_virchow2.py. 스모크 실측 완료(raw token (B,261,1280)
     = CLS1+register4+patch256 → CLS+mean(patch) = 2560).
  2. **raw 삭제 안 함** (Leader 결정 2026-07-17: "프로젝트 끝나기 전까지는 조심"). 원 드라이버는
     임베딩 성공 후 .svs를 지웠다(LRU). 여기선 **보관**하고, 대신 디스크 가드가 여유<MIN_FREE_GB면
     **삭제가 아니라 정지+알림**한다. 판단은 사람이 한다.
     ⚠️ CLAUDE.md "Absolute Prohibitions"의 `raw WSI 전량 영구 보관 금지`와 충돌 — Leader 결정으로
     프로젝트 기간 한정 예외. 종료 시 정리 필요(RESUME.md 참조).
  3. **BRCA 포함**. BRCA raw는 이미 로컬(~/data/tcga_brca_wsi, 1010장)이라 다운로드 없이 타일부터.
     기존 UNI manifest에 coords 컬럼이 없어 **재타일링이 필요**하다.

순서 = 가치 우선(오늘 Yale 파이프라인의 anchor-first 교훈): BRCA(anchor, raw 로컬 → 네트워크 무의존)
→ HNSC(법칙의 유일한 powered CONFIRM) → COLORECTAL → GASTRIC → LUNG(최대·최후).

idempotent: 임베딩 .npy가 있고 (N,2560)·finite면 스킵 → 세션이 끊겨도 재실행하면 이어서 한다.

Usage:
  master: /opt/envs/spatialpatho/bin/python run_multifm.py
  resume: 같은 명령 재실행(완료분 자동 스킵)
"""
import argparse, json, os, sys, subprocess, time, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "experiments/crosscancer"))

PY = "/opt/envs/spatialpatho/bin/python"          # ⚠️ conda가 detached PATH에 없다(2026-07-17 사고). 절대경로 필수.
TILE = ROOT / "agents/embedding/scripts/tile_wsi.py"
EXTRACT = ROOT / "agents/embedding/scripts/extract_virchow2.py"
TILE_CFG = ROOT / "agents/embedding/configs/tile_config.yaml"

EMB_DIM = 2560
MIN_FREE_GB = 300                                  # 디스크 가드: 이하로 떨어지면 정지(삭제 아님)
RAW_BASE = Path.home() / "data/crosscancer_raw"    # HDD 15T. (원 드라이버는 SSD /workspace였으나 raw 보관 정책상 용량 필요)
BRCA_RAW = Path.home() / "data/tcga_brca_wsi"
OUT_BASE = Path("/workspace/data/cache/biop02")    # 공유 볼륨 — 팀 공유 데이터 규칙(CLAUDE.md)

COHORTS = [                                        # (name, gdc_projects | None=로컬)
    ("BRCA",          None),
    ("HEADNECK_HNSC", ["TCGA-HNSC"]),
    ("COLORECTAL",    ["TCGA-COAD", "TCGA-READ"]),
    ("GASTRIC_STAD",  ["TCGA-STAD"]),
    ("LUNG_NSCLC",    ["TCGA-LUAD", "TCGA-LUSC"]),
]
HB = HERE / "MULTIFM_HEARTBEAT.log"


def log(msg, fp=HB):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(fp, "a") as f:
        f.write(line + "\n")


def free_gb(path):
    # statvfs는 마운트(파티션) 여유를 본다. 아직 없는 raw 디렉토리면 존재하는 상위로 올라간다.
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    st = os.statvfs(p)
    return st.f_bavail * st.f_frsize / 1e9


def disk_guard(where, wlog):
    """여유<MIN_FREE_GB면 삭제하지 않고 정지+알림. 사람이 판단."""
    fg = free_gb(where)
    if fg >= MIN_FREE_GB:
        return True
    log(f"🛑 DISK GUARD: {where} 여유 {fg:.0f}GB < {MIN_FREE_GB}GB — raw 삭제하지 않고 **정지**한다. "
        f"사람이 판단할 것(RESUME.md).", wlog)
    (HERE / "DISK_GUARD_TRIPPED").write_text(f"{where} free={fg:.0f}GB at {time.strftime('%F %T')}\n")
    return False


def emb_ok(p):
    """부분/손상 파일을 성공으로 오인하지 않는다(원 드라이버 교훈)."""
    try:
        import numpy as np
        a = np.load(p)
        return a.ndim == 2 and a.shape[1] == EMB_DIM and np.isfinite(a).all()
    except Exception:
        return False


def dirs_for(cancer):
    out = OUT_BASE / cancer.lower() / "virchow2"
    co = OUT_BASE / cancer.lower() / "coords_v2"
    for d in (out, co):
        d.mkdir(parents=True, exist_ok=True)
    return {"emb": out, "coords": co, "raw": (BRCA_RAW if cancer == "BRCA" else RAW_BASE / cancer)}


def build_queue(cancer, projects):
    """BRCA=로컬 svs. 그 외=GDC REST(진단 -DX 슬라이드)."""
    if projects is None:
        return [{"file_name": p.name, "file_id": None, "size": p.stat().st_size}
                for p in sorted(BRCA_RAW.glob("*.svs"))]
    from run_embed_crosscancer import gdc_query
    recs, seen = [], set()
    for proj in projects:
        for h in gdc_query(proj):
            if h["file_id"] not in seen:
                seen.add(h["file_id"]); recs.append(h)
    recs.sort(key=lambda r: r["size"])             # 작은 것부터 = 초기 진척 빠름
    return recs


def process_slide(rec, d, wlog):
    name = rec["file_name"][:-4] if rec["file_name"].endswith(".svs") else rec["file_name"]
    emb = d["emb"] / f"{name}_virchow2_embeddings.npy"
    if emb.exists():
        if emb_ok(emb):
            return "skip"
        emb.unlink()                                # 손상 → 재처리

    raw = d["raw"] / rec["file_name"]
    if not raw.exists():
        if rec["file_id"] is None:
            log(f"  FAIL raw_missing {name} (로컬 BRCA인데 파일 없음)", wlog); return "fail_raw"
        d["raw"].mkdir(parents=True, exist_ok=True)
        if not disk_guard(d["raw"], wlog):
            return "halt_disk"
        from run_embed_crosscancer import download
        if download(rec, d["raw"]) is None:
            log(f"  FAIL download {name}", wlog); return "fail_dl"

    coords = d["coords"] / f"{name}_coords.npy"
    if not coords.exists():
        r = subprocess.run([PY, str(TILE), "--slide", str(raw), "--config", str(TILE_CFG),
                            "--out", str(coords)], capture_output=True, text=True, timeout=2400)
        if r.returncode != 0 or not coords.exists():
            log(f"  FAIL tile {name}: {r.stderr[-250:]}", wlog); return "fail_tile"

    r = subprocess.run([PY, str(EXTRACT), "--coords", str(coords), "--out_dir", str(d["emb"]),
                        "--device", "cuda"], capture_output=True, text=True, timeout=7200)
    if r.returncode != 0 or not emb.exists():
        log(f"  FAIL embed {name}: {r.stderr[-250:]}", wlog); return "fail_emb"
    if not emb_ok(emb):
        log(f"  FAIL verify {name}", wlog); emb.unlink(missing_ok=True); return "fail_verify"
    # ⚠️ raw 삭제하지 않는다 (Leader 결정 2026-07-17). 원 드라이버는 여기서 raw.unlink() 했다.
    log(f"  OK {name}", wlog)
    return "ok"


def run_worker(cancer, shard_path, gpu):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)
    d = dirs_for(cancer)
    recs = json.loads(Path(shard_path).read_text())
    wlog = HERE / f"worker_{cancer}_gpu{gpu}.log"
    tally = {}
    for i, rec in enumerate(recs):
        st = process_slide(rec, d, wlog)
        tally[st] = tally.get(st, 0) + 1
        if st == "halt_disk":
            log(f"[{cancer} gpu{gpu}] 디스크 가드로 중단 — {i}/{len(recs)}", wlog); break
        if i % 20 == 0:
            log(f"[{cancer} gpu{gpu}] {i}/{len(recs)} {tally}", wlog)
    log(f"[{cancer} gpu{gpu}] DONE {tally}", wlog)


def run_master():
    log(f"=== MULTIFM MASTER start — model=virchow2, raw 보관(삭제 안 함), guard={MIN_FREE_GB}GB ===")
    log(f"디스크 여유: ~/data={free_gb(Path.home()/'data'):.0f}GB /workspace={free_gb('/workspace'):.0f}GB")
    for cancer, projects in COHORTS:
        if (HERE / "DISK_GUARD_TRIPPED").exists():
            log("🛑 디스크 가드 발동 상태 — 남은 코호트 중단. 사람 판단 필요."); break
        done_flag = HERE / f"DONE_{cancer}"
        if done_flag.exists():
            log(f"{cancer}: 이미 완료 — 스킵"); continue
        d = dirs_for(cancer)
        try:
            recs = build_queue(cancer, projects)      # GDC 쿼리 일시 실패가 남은 코호트를 죽이지 않게 격리
        except Exception as e:
            log(f"⚠️ {cancer}: 큐 생성 실패({e}) — 이 코호트 건너뛰고 다음으로. 재실행하면 다시 시도(idempotent).")
            continue
        log(f"{cancer}: QUEUE={len(recs)} slides (raw={'로컬' if projects is None else 'GDC 다운로드'})")
        if not recs:
            log(f"{cancer}: 빈 큐 — 스킵"); continue
        (HERE / f"queue_{cancer}.json").write_text(json.dumps(recs))
        procs = []
        for s in range(3):                          # 3 shard → GPU 0/1/2
            shard = recs[s::3]
            if not shard:
                continue
            sp = HERE / f"shard_{cancer}_{s}.json"
            sp.write_text(json.dumps(shard))
            procs.append(subprocess.Popen(
                [PY, __file__, "--worker", "--cancer", cancer, "--shard", str(sp), "--gpu", str(s)]))
        for p in procs:
            p.wait()
        n_ok = len(list(d["emb"].glob("*_virchow2_embeddings.npy")))
        log(f"{cancer}: 완료 — 임베딩 {n_ok}/{len(recs)}")
        if n_ok >= len(recs):
            done_flag.write_text(f"{n_ok}/{len(recs)} at {time.strftime('%F %T')}\n")
        else:
            log(f"⚠️ {cancer}: {len(recs)-n_ok}장 미완 — 재실행하면 이어서 처리")
    log("=== MULTIFM MASTER end ===")
    (HERE / "MASTER_DONE").write_text(time.strftime("%F %T") + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--cancer"); ap.add_argument("--shard"); ap.add_argument("--gpu", type=int)
    a = ap.parse_args()
    if a.worker:
        run_worker(a.cancer, a.shard, a.gpu)
    else:
        run_master()

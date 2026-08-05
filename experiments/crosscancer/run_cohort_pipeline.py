#!/usr/bin/env python3
"""
run_cohort_pipeline.py — 신규 암종 코호트 1-command 자동화 드라이버 (BIOP02 cross-cancer 확장).

BIOP02 cross-cancer expansion / Week 19 "신규 공개 공공데이터로 확장" 과업의 자동화 축.
이건규(작성)가 자동화 파이프라인으로 구성하고, 김가경(kkkim)의 기존 검증 코드를 최대한 재사용한다.
새 코드로 분석을 재구현하지 않는다 — 아래 기존 스크립트를 순서대로 subprocess로 연결(chain)할 뿐이다.

체인하는 스테이지 (기존 스크립트 그대로 호출; GPU 여부 표기):
  0. (선행 데이터) <COHORT>/full/patient_labels.csv        ← 데이터 에이전트가 배치(분자 라벨: cBioPortal/GDC).
                                                            드라이버는 생성하지 않고 존재만 확인.
  1. site-disjoint split            [CPU]  reuse experiments/crosscancer/make_split.py :: run(cancer)
                                            → <COHORT>/full/split.csv + split_meta.json (split_policy_v0 로직, seed 42)
  2. tiling → UNI 임베딩            [GPU]  reuse agents/embedding/scripts/run_batch_embedding.py (main)
                                            → 내부에서 tile_wsi.py + extract_uni.py 체인, tile_config.yaml 사용
                                            → <COHORT>/full/embeddings/<slide>_uni_embeddings.npy (per-slide idempotent)
  3. per-endpoint MIL + cost        [GPU]  reuse run_mil_cost.py (LUNG_NSCLC·COLORECTAL) 또는
                                            sh_mil_cost.py (GASTRIC_STAD·HEADNECK_HNSC, frozen_map 없는 격리판)
                                            --cancer <C> --fm uni --device …  → <COHORT>/full/mil_cost_results.json
  4. 5-seed shuffle-null 강건성     [GPU]  reuse sh_robustness_5seed.py :: main (run_mil_cost.train_eval 재호출)
                                            --cancer <C> --fm uni  → <COHORT>/full/shuffle_null_robustness.json
  5. RESULTS_SUMMARY.md 재생성      [CPU]  reuse summarize_when_done.py :: build_summary(available)
                                            결과 있는 모든 코호트를 훑어 기존 포맷 그대로 재생성

멱등(idempotent) · 재기동 안전: 각 스테이지 출력이 이미 있으면 스킵 → 죽은 런이 이어서 재개된다.
--dry-run: 실제 실행 없이 계획(스킵/실행 커맨드)만 출력. GPU 스테이지는 [GPU]로 명시.

가정 / 규율(팀 discipline 준수):
  * 헤드라인 수치는 결과 파일에서만 읽는다(드라이버는 AUROC 등을 계산·주장하지 않음).
  * claim_level: hypothesis_only, critic_status: pending — 기존 러너가 결과 JSON에 그대로 기록한다.
  * split 정책은 기존 site-disjoint(make_split.py)를 재사용 — 새 split 정책을 발명하지 않는다.
  * 임베딩 헤드라인 = UNI. virchow2/uni2h(다중 FM 견고성)는 --fm 으로만 접근(신규 코호트 기본 경로 아님).
  * 분자 라벨(patient_labels.csv), 치료거리(frozen_map.json)는 도메인/데이터 입력 — 드라이버가 지어내지 않는다.

아직 사람/데이터·GPU가 필요한 것 (still needs):
  * <COHORT>/full/patient_labels.csv — 데이터 에이전트가 cBioPortal/GDC로 준비(라벨 컬럼 = endpoint 이름).
  * 슬라이드 manifest CSV(slide_path 컬럼) — 임베딩 대상. (GDC 자동수집은 run_embed_crosscancer.py 참조; 그쪽은
    코호트 하드코딩·kkkim env라 신규 코호트 기본 경로에서는 manifest 방식을 권장.)
  * 신규 코호트를 MIL 러너의 CANCER_CFG(endpoints·route_axis·positive_control)와
    sh_robustness_5seed.ENDPOINTS 에 1줄 등록 — 치료축/양성대조는 도메인 입력이므로 드라이버가 추정하지 않고,
    미등록 시 명확히 실패시킨다(라우팅 정책 발명 금지).
  * 스테이지 2·3·4 는 GPU 필요(임베딩/CLAM 학습). 스테이지 1·5 는 CPU.

Usage:
  # cohorts/<name>.yaml 에서 코호트 설정을 읽어 전체 체인 실행
  python run_cohort_pipeline.py --cohort GASTRIC_STAD
  python run_cohort_pipeline.py --cohort NEWCANCER --config experiments/crosscancer/cohorts/newcancer.yaml
  python run_cohort_pipeline.py --cohort NEWCANCER --dry-run        # 계획만 출력
  python run_cohort_pipeline.py --cohort NEWCANCER --only split,mil # 일부 스테이지만
"""
import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # experiments/crosscancer
ROOT = HERE.parents[1]                                  # repo root

# 기존 스크립트(재사용 대상) — 경로 고정
MAKE_SPLIT = HERE / "make_split.py"
BATCH_EMBED = ROOT / "agents/embedding/scripts/run_batch_embedding.py"
TILE_CFG = ROOT / "agents/embedding/configs/tile_config.yaml"
MIL_RUNNERS = {                                         # 코호트 CANCER_CFG 보유 러너
    "run_mil_cost.py": HERE / "run_mil_cost.py",        # frozen_map 있음(cost routing) — LUNG_NSCLC·COLORECTAL
    "sh_mil_cost.py":  HERE / "sh_mil_cost.py",         # frozen_map 없음(misroute lead) — GASTRIC_STAD·HEADNECK_HNSC
}
FIVESEED = HERE / "sh_robustness_5seed.py"
SUMMARIZE = HERE / "summarize_when_done.py"

# GPU 스테이지엔 GPU 있는 공유 env, CPU 스테이지도 동일 인터프리터로 충분.
DEFAULT_PYTHON = "/opt/envs/spatialpatho/bin/python"

# FM별 임베딩 파일 접미사(run_mil_cost.FM_SPEC 과 일치). 기본 UNI.
FM_SUFFIX = {"uni": "uni", "virchow2": "virchow2", "uni2h": "uni2h"}


def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #
def load_config(cohort, config_path):
    """cohorts/<name>.yaml (또는 --config)에서 코호트 설정 로드. YAML/JSON 지원."""
    if config_path:
        cfg_file = Path(config_path)
        if not cfg_file.is_absolute():
            cfg_file = (ROOT / cfg_file) if (ROOT / cfg_file).exists() else (Path.cwd() / cfg_file)
    else:
        # cohorts/<name>.yaml 대소문자 무관 탐색
        cdir = HERE / "cohorts"
        cand = [cdir / f"{cohort}.yaml", cdir / f"{cohort}.yml",
                cdir / f"{cohort.lower()}.yaml", cdir / f"{cohort.lower()}.yml",
                cdir / f"{cohort}.json"]
        cfg_file = next((c for c in cand if c.exists()), None)
        if cfg_file is None:
            raise SystemExit(f"[ERR] cohort config 없음: {cohort} — {cdir}/<name>.yaml 를 만들거나 --config 지정 "
                             f"(예시: {cdir}/EXAMPLE.yaml)")
    text = cfg_file.read_text(encoding="utf-8")
    if cfg_file.suffix == ".json":
        cfg = json.loads(text)
    else:
        import yaml
        cfg = yaml.safe_load(text)
    log(f"config: {cfg_file}")
    return cfg


def cohort_dir(cohort):
    return HERE / cohort / "full"


# --------------------------------------------------------------------------- #
# stage runner (idempotent + dry-run)
# --------------------------------------------------------------------------- #
def stage(name, gpu, output, cmd, dry_run, python=None, cwd=None, func=None):
    """스테이지 하나를 실행/스킵. output(Path 또는 Path 리스트)이 이미 있으면 스킵(멱등).
    cmd: subprocess argv(리스트). func: 대신 호출할 (callable, label) — 파이썬 인프로세스 재사용용.
    """
    tag = "[GPU]" if gpu else "[CPU]"
    outs = output if isinstance(output, (list, tuple)) else [output]
    if outs and all(o is not None and Path(o).exists() for o in outs):
        log(f"SKIP {tag} {name}: 출력 존재 ({', '.join(str(o) for o in outs)})")
        return "skip"
    if func is not None:
        callable_, label = func
        log(f"{'PLAN' if dry_run else 'RUN '} {tag} {name}: {label}")
        if dry_run:
            return "plan"
        t0 = time.time()
        callable_()
        log(f"DONE {tag} {name} ({time.time()-t0:.0f}s)")
        return "done"
    argv = ([python] if python else []) + [str(x) for x in cmd]
    log(f"{'PLAN' if dry_run else 'RUN '} {tag} {name}: {' '.join(argv)}")
    if dry_run:
        return "plan"
    t0 = time.time()
    r = subprocess.run(argv, cwd=str(cwd) if cwd else None)
    if r.returncode != 0:
        raise SystemExit(f"[ERR] {name} 실패 rc={r.returncode} — 여기서 중단(재실행하면 이어서 재개).")
    if outs and not all(o is None or Path(o).exists() for o in outs):
        raise SystemExit(f"[ERR] {name} 종료됐지만 기대 출력 없음: {[str(o) for o in outs]}")
    log(f"DONE {tag} {name} ({time.time()-t0:.0f}s)")
    return "done"


# --------------------------------------------------------------------------- #
# stage 1 — split (make_split.run 인프로세스 재사용; make_split 은 argparse 없음)
# --------------------------------------------------------------------------- #
def stage_split(cohort, dry_run):
    d = cohort_dir(cohort)
    labels = d / "patient_labels.csv"
    out = [d / "split.csv", d / "split_meta.json"]
    if not (out[0].exists() and out[1].exists()) and not labels.exists():
        raise SystemExit(f"[ERR] {labels} 없음 — 데이터 에이전트가 분자 라벨(patient_labels.csv)을 먼저 배치해야 함.")

    def _run():
        sys.path.insert(0, str(HERE))
        import make_split
        make_split.run(cohort)      # site-disjoint split_policy_v0 로직 그대로

    return stage("split(site-disjoint)", gpu=False, output=out, cmd=None,
                 dry_run=dry_run, func=(_run, f"make_split.run('{cohort}') → split.csv/split_meta.json"))


# --------------------------------------------------------------------------- #
# stage 2 — tiling + embedding (run_batch_embedding, per-slide idempotent)
# --------------------------------------------------------------------------- #
def stage_embed(cohort, cfg, python, dry_run):
    d = cohort_dir(cohort)
    emb_dir = d / "embeddings"
    fm = cfg.get("embedding_model", "uni")
    suffix = FM_SUFFIX.get(fm, "uni")
    manifest = cfg.get("slide_manifest")
    if not manifest:
        log(f"NOTE {cohort}: slide_manifest 미지정 — 임베딩 스테이지 스킵. "
            f"GDC 자동수집이 필요하면 run_embed_crosscancer.py(코호트 하드코딩 주의) 참조.")
        # 이미 임베딩이 배치돼 있으면 통과, 아니면 이후 MIL 에서 실패하도록 둔다.
        n = len(list(emb_dir.glob(f"*_{suffix}_embeddings.npy"))) if emb_dir.exists() else 0
        log(f"  현재 임베딩 {n}개 ({emb_dir})")
        return "skip"
    man_path = Path(manifest)
    if not man_path.is_absolute():
        man_path = ROOT / manifest
    # 멱등: manifest 행 수만큼 임베딩이 이미 있으면 스테이지 스킵
    try:
        n_slides = sum(1 for _ in csv.DictReader(man_path.open(encoding="utf-8-sig")))
    except FileNotFoundError:
        raise SystemExit(f"[ERR] slide_manifest 없음: {man_path}")
    n_have = len(list(emb_dir.glob(f"*_{suffix}_embeddings.npy"))) if emb_dir.exists() else 0
    run_manifest = d / "_embedding_run_manifest.csv"
    if n_have >= n_slides and n_slides > 0:
        log(f"SKIP [GPU] embed: 임베딩 {n_have}/{n_slides} 이미 존재 ({emb_dir})")
        _write_cc_manifest(cohort, emb_dir, suffix, fm, dry_run=False)
        return "skip"
    tile_cfg = cfg.get("tile_config", str(TILE_CFG))
    tile_dir = cfg.get("tile_dir", str(d / "coords"))
    device = cfg.get("device", "cuda")
    dev = device.split(":")[0] if fm == "uni" else device   # extract_uni: cuda/cpu
    cmd = [BATCH_EMBED,
           "--manifest", man_path,
           "--config", tile_cfg,
           "--tile_dir", tile_dir,
           "--embedding_dir", emb_dir,
           "--output_manifest", run_manifest,
           "--embedding_model", fm if fm in ("uni", "conch", "exaone", "dummy") else "uni",
           "--device", dev]
    st = stage("embed(tile→UNI, run_batch_embedding)", gpu=True, output=None, cmd=cmd,
               dry_run=dry_run, python=python)
    if not dry_run:
        _write_cc_manifest(cohort, emb_dir, suffix, fm, dry_run=False)
    return st


def _write_cc_manifest(cohort, emb_dir, suffix, fm, dry_run):
    """cross-cancer 관행 manifest(embedding_manifest_<cohort>_<fm>.csv) 생성 — glue(분석 아님).
    컬럼은 run_embed_crosscancer.build_manifest 와 동일. load_meta 는 이 파일을 읽지 않고
    embeddings/ 를 직접 glob 하므로 이 파일은 기록용."""
    if not emb_dir.exists():
        return
    rows = []
    for p in sorted(emb_dir.glob(f"*_{suffix}_embeddings.npy")):
        sid = p.name.replace(f"_{suffix}_embeddings.npy", "")
        rows.append({"case_id": sid[:12], "slide_id": sid, "embedding_path": str(p),
                     "embedding_model": fm, "file_id": ""})
    mp = cohort_dir(cohort) / f"embedding_manifest_{cohort.lower()}_{fm}.csv"
    with mp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "slide_id", "embedding_path", "embedding_model", "file_id"])
        w.writeheader()
        w.writerows(rows)
    log(f"  manifest: {len(rows)} rows → {mp}")


# --------------------------------------------------------------------------- #
# stage 3 — MIL + cost
# --------------------------------------------------------------------------- #
def _resolve_mil_runner(cohort, cfg):
    """cohort 를 CANCER_CFG 에 가진 러너 선택. cfg.mil_runner 우선, 없으면 두 러너에서 탐색."""
    want = cfg.get("mil_runner")
    if want:
        if want not in MIL_RUNNERS:
            raise SystemExit(f"[ERR] mil_runner 알 수 없음: {want} (택1: {list(MIL_RUNNERS)})")
        return want, MIL_RUNNERS[want]
    sys.path.insert(0, str(HERE))
    for name, path in MIL_RUNNERS.items():
        mod = __import__(name[:-3])
        if cohort in getattr(mod, "CANCER_CFG", {}):
            return name, path
    raise SystemExit(
        f"[ERR] {cohort} 이 어느 MIL 러너 CANCER_CFG 에도 없음. "
        f"run_mil_cost.py(frozen_map 필요) 또는 sh_mil_cost.py 의 CANCER_CFG 에 "
        f"endpoints·route_axis·positive_control 을 1줄 등록해야 함(도메인 입력, 드라이버가 추정 안 함). "
        f"또는 cohorts/<name>.yaml 에 mil_runner 를 지정.")


def stage_mil(cohort, cfg, python, dry_run):
    d = cohort_dir(cohort)
    fm = cfg.get("embedding_model", "uni")
    fm_tag = "" if fm == "uni" else f"_{fm}"
    out = d / f"mil_cost_results{fm_tag}.json"
    runner_name, runner_path = _resolve_mil_runner(cohort, cfg)
    device = cfg.get("device", "cuda:0")
    cmd = [runner_path, "--cancer", cohort, "--fm", fm, "--device", device]
    # cwd=HERE 이어야 러너의 `import run_mil_cost` 가 동작(같은 디렉터리).
    return stage(f"mil+cost ({runner_name})", gpu=True, output=out, cmd=cmd,
                 dry_run=dry_run, python=python, cwd=HERE)


# --------------------------------------------------------------------------- #
# stage 4 — 5-seed shuffle-null
# --------------------------------------------------------------------------- #
def stage_fiveseed(cohort, cfg, python, dry_run):
    d = cohort_dir(cohort)
    fm = cfg.get("embedding_model", "uni")
    out = d / ("shuffle_null_robustness.json" if fm == "uni" else f"shuffle_null_robustness_{fm}.json")
    # sh_robustness_5seed 는 ENDPOINTS 에 등록된 코호트만 받는다.
    sys.path.insert(0, str(HERE))
    mod = __import__("sh_robustness_5seed")
    if cohort not in getattr(mod, "ENDPOINTS", {}):
        raise SystemExit(
            f"[ERR] {cohort} 이 sh_robustness_5seed.ENDPOINTS 에 없음 — 5-seed 대상 endpoint 목록을 1줄 등록해야 함.")
    device = cfg.get("device", "cuda:0")
    cmd = [FIVESEED, "--cancer", cohort, "--fm", fm, "--device", device]
    return stage("5-seed shuffle-null", gpu=True, output=out, cmd=cmd,
                 dry_run=dry_run, python=python, cwd=HERE)


# --------------------------------------------------------------------------- #
# stage 5 — RESULTS_SUMMARY.md (summarize_when_done.build_summary 재사용)
# --------------------------------------------------------------------------- #
def stage_summary(dry_run):
    def _run():
        sys.path.insert(0, str(HERE))
        import summarize_when_done as s
        available = [c for c in sorted(p.parent.parent.name
                                       for p in HERE.glob("*/full/mil_cost_results.json"))]
        if not available:
            log("  결과(mil_cost_results.json) 있는 코호트 없음 — 요약 생략")
            return
        s.SUMMARY.write_text(s.build_summary(available))
        log(f"  RESULTS_SUMMARY.md 재생성 — 코호트: {available}")

    return stage("RESULTS_SUMMARY.md", gpu=False, output=None, cmd=None, dry_run=dry_run,
                 func=(_run, "summarize_when_done.build_summary(available)"))


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
STAGES = ["split", "embed", "mil", "fiveseed", "summary"]


def main():
    ap = argparse.ArgumentParser(description="신규 암종 코호트 cross-cancer 파이프라인 자동화 드라이버")
    ap.add_argument("--cohort", required=True, help="코호트 이름(=<COHORT>/full 디렉터리명, 예: GASTRIC_STAD)")
    ap.add_argument("--config", help="코호트 config(YAML/JSON). 생략 시 cohorts/<cohort>.yaml 탐색")
    ap.add_argument("--python", default=DEFAULT_PYTHON, help=f"GPU 스테이지 인터프리터(기본 {DEFAULT_PYTHON})")
    ap.add_argument("--dry-run", action="store_true", help="실행 없이 계획만 출력")
    ap.add_argument("--only", help="쉼표구분 스테이지만 실행(택: %s)" % ",".join(STAGES))
    a = ap.parse_args()

    cfg = load_config(a.cohort, a.config)
    # config 의 cancer/cohort 필드가 --cohort 와 다르면 경고(디렉터리명이 정본)
    cfg_name = cfg.get("cohort") or cfg.get("cancer")
    if cfg_name and cfg_name != a.cohort:
        log(f"NOTE config cohort='{cfg_name}' 가 --cohort '{a.cohort}' 와 다름 — 디렉터리명 '{a.cohort}' 기준으로 진행")

    d = cohort_dir(a.cohort)
    d.mkdir(parents=True, exist_ok=True)
    only = set(s.strip() for s in a.only.split(",")) if a.only else set(STAGES)

    log(f"=== cohort pipeline: {a.cohort} | fm={cfg.get('embedding_model','uni')} | "
        f"dry_run={a.dry_run} | stages={sorted(only)} ===")
    log("규율: 헤드라인=결과파일만 · claim_level=hypothesis_only · critic_status=pending · "
        "split=site-disjoint 재사용 · GPU=stage 2/3/4")

    results = {}
    if "split" in only:
        results["split"] = stage_split(a.cohort, a.dry_run)
    if "embed" in only:
        results["embed"] = stage_embed(a.cohort, cfg, a.python, a.dry_run)
    if "mil" in only:
        results["mil"] = stage_mil(a.cohort, cfg, a.python, a.dry_run)
    if "fiveseed" in only:
        results["fiveseed"] = stage_fiveseed(a.cohort, cfg, a.python, a.dry_run)
    if "summary" in only:
        results["summary"] = stage_summary(a.dry_run)

    log(f"=== 완료: {a.cohort} | {json.dumps(results, ensure_ascii=False)} ===")
    if not a.dry_run:
        log("⚠️ Owner != Reviewer: 결과 critic_status=pending. sjpark/braveji 크로스체크 필수.")


if __name__ == "__main__":
    main()

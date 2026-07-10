#!/usr/bin/env python3
"""
Cross-cancer cost-of-substitution runner (Phase 0 스캐폴드).

암종 config(YAML) 하나로 전 파이프라인을 오케스트레이션한다. 기존 BRCA 스크립트를 재사용하고
암종별 델타(코호트·엔드포인트·치료축맵·세포주 lineage)만 config에서 읽는다.

**Phase 0 = dry-run만.** 실제 실행(--execute)은 사인오프 + Paper A 완료 + GPU 슬롯 게이트 통과 후(Phase 1).
지금은 각 단계가 '무엇을, 어떤 명령으로' 돌릴지 계획만 출력한다(스코프 위반 없음, GPU 0).

사용:
  python experiments/crosscancer/run_crosscancer.py experiments/crosscancer/configs/lung_nsclc.yaml
  (--execute 는 Phase 1 전까지 차단)
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

STAGES = ["download_wsi", "tile", "embed", "fetch_labels", "train_mil",
          "build_frozen_map", "compute_cost", "make_figure"]


def load_cfg(path):
    text = Path(path).read_text()
    if yaml is None:
        print("[warn] pyyaml 미설치 — 계획 출력만(값 파싱 생략). `pip install pyyaml` 후 상세 계획.")
        return {"_raw": text, "cancer": "(config)", "out_dir": "experiments/crosscancer/OUT"}
    return yaml.safe_load(text)


def plan(cfg):
    """각 단계가 Phase 1에서 실행할 명령을 계획으로 출력(dry-run)."""
    c = cfg.get("cancer", "?"); out = cfg.get("out_dir", "experiments/crosscancer/OUT")
    R = cfg.get("reuse", {})
    print(f"\n=== Cross-cancer runner (DRY-RUN) : {c} ===")
    print(f"out_dir = {out}\n")
    steps = [
        ("download_wsi",
         f"GDC: gdc-client download -m <manifest for {cfg.get('tcga_cohorts')}> "
         f"(filter {cfg.get('gdc_filter')}); IDC: idc-index download {cfg.get('cptac_collections')}"),
        ("tile",
         f"{R.get('tile','tile_wsi.py')} --config tile_config.yaml (256^2@20x, Otsu, cap 5000) → {out}/coords"),
        ("embed",
         f"{R.get('embed',{})} → {out}/emb (UNI/CONCH; EXAONE 스모크 후). GPU 필요"),
        ("fetch_labels",
         f"cBioPortal {cfg.get('label_sources',{}).get('cbioportal')} → endpoints "
         f"{[e.get('name') for e in cfg.get('endpoints',[])]}"),
        ("train_mil",
         f"CLAM 학습(엔드포인트별) → {out}/predictions_ext (slide_id 인덱스). GPU 필요"),
        ("build_frozen_map",
         f"{R.get('frozen_map')} --depmap-lineage {cfg.get('depmap_lineage')} "
         f"--axes {cfg.get('map_axes')} → {out}/frozen_map.json (축별 세포주 >=5 게이트)"),
        ("compute_cost",
         f"{R.get('compute_cost')} : 치료거리 + 환자 라우팅(측정 vs 예측) → cost-of-substitution"),
        ("make_figure",
         f"{R.get('figure')} → {out}/fig_cost_of_substitution.png (2패널)"),
    ]
    for i, (name, cmd) in enumerate(steps, 1):
        gpu = " [GPU]" if name in ("embed", "train_mil") else ""
        print(f"  {i}. {name}{gpu}\n     → {cmd}")
    print("\n엔드포인트 → 치료축 (config):")
    for e in cfg.get("endpoints", []):
        print(f"   - {e.get('name'):20} axis={e.get('axis'):12} expect={e.get('expect')}")
    print(f"\n게이트: {cfg.get('gates', {})}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--execute", action="store_true", help="Phase 1 실행 (현재 차단)")
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    if a.execute:
        print("[BLOCKED] --execute 는 Phase 1 전용. 게이트 확인 필요:")
        print("  1) 사인오프 확정 + 팀 헤드업 (research/paperA-positioning/2026-07-10_crosscancer-signoff.md)")
        print("  2) Paper A receptor 라우팅·발표 완료 (또는 유휴 GPU 슬롯 예약)")
        print("  3) 각 단계 실 스크립트 wiring (Phase 1 작업)")
        sys.exit(2)
    plan(cfg)
    print("\n[Phase 0] dry-run 완료. 실행은 게이트 통과 후 --execute (Phase 1에서 wiring).")


if __name__ == "__main__":
    main()

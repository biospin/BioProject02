# Cross-cancer cost-of-substitution — 별도 트랙 (Phase 0 스캐폴드)

> **상태:** Phase 0(스캐폴드, GPU 0). 실행(Phase 1)은 게이트 통과 후.
> 사인오프: `research/paperA-positioning/2026-07-10_crosscancer-signoff.md` (Leader 승인 2026-07-10, 팀 헤드업 대기).
> 근거: `../../research/paperA-positioning/2026-07-10_future-crosscancer-{data,automation-plan}.md`.

## 무엇
BRCA cost-of-substitution 결정지도를 타암종으로 일반화. **암종 config(YAML) 하나로** 기존 BRCA 스크립트를 오케스트레이션.
- 재사용: tile_wsi·extract_uni/conch·build_frozen_map·compute_cost·make_fig (BRCA와 동일).
- 암종 델타: 코호트·엔드포인트·치료축맵·세포주 lineage = config에서만.

## 쓰기
```bash
# Phase 0 (dry-run, 지금): 계획만 출력, GPU 0, 스코프 위반 없음
python experiments/crosscancer/run_crosscancer.py experiments/crosscancer/configs/lung_nsclc.yaml
# Phase 1 (--execute): 게이트(사인오프+Paper A 완료+GPU) 통과 후, 실 스크립트 wiring
```

## Phase 게이트
- Phase 0 ✅ 지금 — config 스키마 + dry-run runner (준비/코드, 무해).
- Phase 1 ⏳ — 사인오프 확정 + 팀 헤드업 + Paper A receptor 라우팅·발표 후(또는 유휴 GPU). 폐 NSCLC 파일럿부터.
- Phase 2 대장 → Phase 3 cross-cancer decision map.

## configs
- `lung_nsclc.yaml` — 1순위 파일럿(EGFR/ALK/KRAS vs LUAD/LUSC). 값은 착수 전 GDC/DepMap 실측.
- (추가 예정) colorectal.yaml, gastric.yaml …

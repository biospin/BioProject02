# Future-work: 타암종 cost-of-substitution 자동화·실행 플랜 (2026-07-10)

> **계획만.** 착수 전제 = ① BRCA-only 룰 리더 사인오프 ② 발표/Paper A 코어 완료. 데이터·후보 = `2026-07-10_future-crosscancer-data.md`, 스쿱 = `2026-07-10_subtype-decision-map.md` §6.
> 결론: **파이프라인 모듈·암종 무관 → 대부분 자동화 가능. 자원(GPU·데이터)은 보유분으로 충분($0). 관문은 스코프 룰·마감.**

## 1. 자동화 가능성 (단계별)

| 단계 | 자동화 | 재사용 자산 | 사람 개입 |
|---|---|---|---|
| WSI 다운로드 | ✅ 완전 | gdc-client(manifest)·idc-index | 코호트 지정만 |
| 타일링 | ✅ | `tile_wsi.py` | — |
| 임베딩 추출 | ✅ | `extract_uni/conch/exaone.py`·run 러너 | GPU 슬롯 |
| 분자 라벨 수집 | ✅ | cBioPortal REST·GDC | 엔드포인트 지정 |
| 세포주 냉동지도 | ✅ | `build_frozen_map.py`(lineage 필터만 교체) | — |
| MIL 학습(H&E→아형/변이) | ✅ 파이프라인화 | CLAM(sjpark) | 검증·하이퍼 |
| cost-of-substitution·그림 | ✅ | `compute_cost.py`·`freeze_panel.py`·`make_fig_cost.py` | — |
| **아형→치료축 매핑** | ⚠️ config(암종당 1회) | — | **도메인 입력**(예: 폐 EGFR→osimertinib) |
| QC·Critic 7항목 | ⚠️ 부분 | Critic 체크리스트 | 사람 리뷰 |

→ **핵심: 암종당 config 하나만 채우면 나머지는 runner로.**

## 2. Config-driven runner 설계 (Phase 0 산출)

암종별 YAML 하나로 전 파이프라인 구동:
```yaml
cancer: LUNG_NSCLC
tcga_cohorts: [TCGA-LUAD, TCGA-LUSC]
cptac_collections: [cptac_luad, cptac_lscc]      # 외부검증
endpoints:                                        # H&E→예측 대상
  - {name: EGFR_mut, axis: anti-EGFR, drugs: [Osimertinib, Gefitinib]}
  - {name: ALK_fusion, axis: anti-ALK, drugs: [Crizotinib, Alectinib]}
  - {name: KRAS_G12C, axis: anti-KRAS, drugs: [Sotorasib]}
  - {name: histology_LUAD_LUSC, axis: histology, drugs: [Pemetrexed, ...]}  # 형태학 축
depmap_lineage: Lung                              # 냉동지도 세포주 필터
label_source: cbioportal:luad_tcga_pan_can_atlas_2018
```
러너 단계: download → tile → embed → label-join → MIL-train → frozen-map → compute-cost → figure. (기존 스크립트 오케스트레이션 = 신규 코드 최소.)

## 3. 시간·자원 (암종 1개 기준, 예: 폐 ~1,000슬라이드)

| 항목 | 추정 | 근거 |
|---|---|---|
| 컴퓨트 | **~2–4 GPU-day** | EXAONE 1010장 3-GPU ~8h·UNI ~95 tiles/s(세션 실측) + MIL 학습 |
| GPU 비용 | **$0** | A6000×3 Modulabs 무료 |
| 스토리지 | raw WSI ~0.5–1 TB(transient, LRU) + 임베딩 ~GB(영구) | 14.6TB HDD |
| 데이터 비용 | **$0** | TCGA/CPTAC/DepMap/GDSC open |
| wall-clock | **~1–2주/암종** | 다운로드+컴퓨트+QC |
| 사람 시간 | **~1–2주** 팀 분담 | 임베딩 kkkim·모델 sjpark·치료매핑 jhans·Critic braveji |
| **파일럿 쌍(폐+대장)** | **~1개월**(병렬) | |

## 4. 단계별 플랜

- **Phase 0 — 스캐폴드(저비용, 사인오프 전에도 설계 가능):** config 스키마 + runner 오케스트레이션 골격. 신규 코드 최소(기존 스크립트 wrapping).
- **Phase 1 — 폐 NSCLC 파일럿:** download→embed→MIL(EGFR/ALK/KRAS + LUAD/LUSC)→frozen-map(Lung)→cost. **기대: 표적축(EGFR/ALK) 붕괴 vs 형태학축(LUAD/LUSC) triage** = BRCA HER2 패턴 재현.
- **Phase 2 — 대장:** BRAF(붕괴) vs MSI(중간, 형태학적) → **metric calibration** 입증.
- **Phase 3 — 종합:** cross-cancer decision map(암종×치료축 cost 히트맵) + "표적변이=H&E-blind" 원리 정식화.

## 5. 진짜 관문 (기술·자원 아님)
1. **BRCA-only 룰** → 스코프 확장 **리더 사인오프 필수**(CLAUDE.md: pan-cancer 금지, Paper B까지).
2. **발표/Paper A 마감** → 지금 팀 포커스=BRCA. Paper A receptor 라우팅 완료 후.
3. **반복 사람 개입**(치료축 config·Critic 리뷰)은 작지만 0 아님 → 완전 무인 아님, "config만 사람"의 반자동.
4. Critic 제약 유지: hypothesis_only·비-DRP·per-experiment 가드.

## 6. 결론
- **가능하다:** 파이프라인 재사용 + config-driven runner → 암종당 반자동(사람=config·Critic만). 자원 $0(GPU·데이터 보유).
- **얼마나:** 암종당 ~2–4 GPU-day·~1–2주, 파일럿 쌍 ~1개월.
- **진행 조건:** 리더 사인오프 + Paper A 완료. 그 전엔 **Phase 0 스캐폴드 설계**까지만 저비용으로 선행 가능.

---
관련: `2026-07-10_future-crosscancer-data.md`(후보·다운로드) · `2026-07-10_subtype-decision-map.md` §6(스쿱·원리) · `experiments/kkkim/20260710_cost_of_substitution/`(재사용 스크립트).

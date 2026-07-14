# kkkim 실험 인덱스 — 2026-07 (Paper A 재정립 세션)

> 이 세션(2026-07-08~10)에 kkkim이 수행한 실험·분석의 마스터 인덱스. 각 항목 = 목적·경로·핵심결과·commit·상태·claim_level.
> 팀 실험(sjpark 등)은 §참조에만. 대용량 raw(세포주 omics·GDSC·IMPRESS WSI)는 gitignore.

## 1. 실험 (experiments/kkkim/)

### ① EXAONE Path 2.0 3-way 임베딩 비교 — `20260708_3way/`
- **목적:** UNI/CONCH/EXAONE 3 foundation model을 동일 슬라이드셋·동일 probe로 slide-level 비교(BIOP02-48).
- **핵심결과:** EXAONE_slide_global이 ER **0.923**/PR 0.845/HER2 0.697로 UNI·CONCH를 CI 비중첩 상회, PAM50만 UNI 0.736. **단 EXAONE_patch_mean(동일 mean-pool)은 UNI와 대등** → slide_global 이득은 EXAONE 자체 집계+내부 tiling 혼재.
- **산출:** `comparison.md`, `comparison_report.json`, `phenotype_auroc.png`. **commit `69fe4ce`.** claim=**sanity**(모델선택 QC, 예측주장 아님).

### ② CPTAC 공식 라벨 재조인 + 승격 — `20260709_cptac_official_join/`
- **목적:** jamie 공식 CPTAC 라벨(BIOP02-55, PR#24)로 CPTAC UNI 임베딩 매니페스트 재생성 → 공유 경로 승격.
- **핵심결과:** 653/653 매칭, 4종라벨 완비 395, task별 has_er 387/has_pr 375/**has_her2 294**/has_pam50 382. 임시본 대비 40슬라이드 값변경(HER2 equivocal 보존). 공유 매니페스트 승격 완료(백업 보존).
- **산출:** `REGEN.md`, `regen_join.py`, `embedding_manifest_cptac_uni_v1.csv`. sjpark BIOP02-53 외부검증 재실행에 사용됨.

### ③ 세포주 치료축 카운트 (C1 게이트) — `20260710_cellline_counts/`
- **목적:** cost-of-substitution 냉동 지도의 feasibility 게이트 — DepMap∩GDSC 유방 세포주를 치료축별 카운트.
- **핵심결과:** 교집합 **51라인**. 축별 **내분비 ER+ 15 · 항HER2 ERBB2-amp 14 · 화학 TNBC 23** — 전부 ≥5 → **GO**. 항HER2는 GDSC2 Lapatinib/Afatinib/Sapitinib Z-score로 독립 검증.
- **산출:** `counts.json`, `cellline_axis_table.csv`, `her2_drug_zscore_validation.csv`. (raw DepMap/GDSC = gitignore)

### ④ ★ Cost-of-substitution (C1, Paper A 플래그십) — `20260710_cost_of_substitution/`
- **목적:** 분자검사 대신 H&E-예측 아형으로 치료를 정하면 치료 랭킹을 얼마나 잃나(치료축별). 병목을 자산으로, "천장 못 넘음"을 논점으로 전환.
- **핵심결과(예비, PAM50 라우팅):**
  - 냉동 세포주→약물 지도 286약물. **치료거리:** antiHER2↔chemo **0.765**(최대)·endo↔chemo 0.695·endo↔antiHER2 0.395.
  - 환자 라우팅(n=382): **antiHER2 cost 0.718·mis-route 100%**(모델이 HER2 아예 예측 못 함) · chemo 0.105(최저) · endocrine 0.378.
  - **헤드라인:** cost(antiHER2)−cost(endocrine)=**0.340, 95%CI[0.276,0.402], 0 배제** → 반증 바 통과.
  - **사전등록 패널** positive control: antiHER2 3/3·chemo 7/7 완벽, **endocrine 1/8**(세포주가 내분비약 못 잡음).
  - **D1 흡수:** ER+ 박스 이중 한계(분류기 + 치료증거 인프라). `endocrine_limitation.md`.
- **산출:** `build_frozen_map.py`·`compute_cost.py`·`freeze_panel.py`·`make_fig_cost.py`, `frozen_map.*`·`therapeutic_distance.json`·`patient_routing_cost.json`·`preregistered_drug_panel.json`, **`fig_cost_of_substitution.png`**(2패널). **commits `dbf123f`·`70ae43d`·`d8eee4e`·`418888c`.** claim=**sanity/hypothesis**.
- **미완:** receptor-status 라우팅 = sjpark ER 예측(slide_id 인덱스) 대기, 골격은 자동실행 준비됨(`SJPARK_PRED_FORMAT.md`, JIRA BIOP02-53 #11006).

### ⑤ IMPRESS pCR 파이프라인 실증 (B 트랙) — `20260710_pcr_impress/`
- **목적:** pCR from pre-treatment H&E(IMPRESS) 파이프라인 호환성 실증 + 실행 준비.
- **핵심결과:** **GO** — 다운로드→tile→UNI 임베딩 무수정 동작, 조인 **126/126**(HER2+ 62·TNBC 64), tile min-bag 338, UNI ~95 tiles/s → HE-only 3모델 ~3–4 GPU-h. 외부검증 없음(단일기관). claim=사이드 트랙.
- **산출:** `RUN_PLAN.md`, `patient_slide_pcr.csv`, `DATA_MANIFEST.md`, `outputs/pilot/`. (raw WSI = gitignore)

## 2. 분석·포지셔닝 문서 (research/)

| 문서 | 내용 |
|---|---|
| `paperA-positioning/2026-07-10_novelty-scoop-analysis.md` | 레드오션 스쿱 확정(Fernandez-Romero 2026·Dawood 2024) + Tier A 재정립 + Tier B·D2/D3 스쿱 (2에이전트 원본+검증) |
| `paperA-positioning/2026-07-10_research-plan.md` | C1/C2 정식 연구계획(치료축 keying·누수가드·통계·게이트) |
| `paperA-positioning/2026-07-10_subtype-decision-map.md` | ★ 핵심 메시지: subtype 치료결정 지도 + 슬라이드 6장 골격 + 블로그 연계 |
| `paperA-positioning/2026-07-10_tierC-longterm-roadmap.md` | Tier C(공간/다중) NO-GO·add-on(§7.1, conditional-go)·B×C 접점(§7.2) |
| `program-narrative/2026-07-10_biop01-02-static-dynamic.md` | BIOP01↔02 연결(발표 서사, ER+ 저항에서 정적×동역학 수렴; Paper C NO-GO) |

## 3. 방향 판정 요약 (전수 탐색 결과)
- **A (cost-of-substitution)** = 유일 헤드라인. 진행 중(receptor 라우팅만 대기).
- **B (pCR/IMPRESS)** = GO, 사이드 논문(새 데이터).
- **C (공간 modality)** = NO-GO standalone(Path2Space Cell 2026 스쿱) → 검증 add-on DEFERRED(conditional-go).
- **D1(내분비 사각)** = A에 흡수. **D2(PRISM repurposing)** 얇음·**D3(CRISPR dependency)** red ocean → A 못 이김.
- **endpoint 전환**(HRD/PIK3CA/HER2-low 등) = 스쿱/불가.
- **BIOP01↔02** = 발표 서사만(생물학 파이프라인 Paper C 데이터-블록).

## 4. 참조 (팀 실험, main)
- sjpark: `experiments/sjpark/*` + `experiments/registry/cross_validation_registry.jsonl`(ER/PR/HER2/PAM50 외부검증 공식라벨) — cost-of-substitution 라우팅의 예측 소스.
- braveji: BIOP02-50 Critic·-57 registry.

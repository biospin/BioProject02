# IMPRESS pCR — RUN_PLAN

Tier B 트랙: **pCR from pre-treatment H&E** (IMPRESS, OSU NAC 코호트). Paper A(TCGA-BRCA)와 별개.
작성 2026-07-10 · kkkim (Embedding Agent) · 파이프라인 호환성 실증 완료 후 실행 계획.

> 이 문서의 모든 수치는 **실제 다운로드/실행 근거**만 인용한다. 추정치는 근거 n과 함께 "추정"으로 표기.

---

## 0. 실증 결과 요약 (go/no-go 근거)

| 항목 | 결과 | 근거 |
|---|---|---|
| Drive 다운로드 | ✅ 성공 (gdown, auth 불필요) | 5개 HE `.svs` 실제 다운로드 |
| openslide 열림 | ✅ 정상 | 061_HE: 32005×34355, 20×, mpp 0.4934, Aperio, 3 levels |
| 파일 ID 확보 | ✅ 254개 전체 열거 | `data/wsi_drive_listing/file_ids.txt` (id↔파일명) |
| tiling 호환 | ✅ 재사용 성공 | `tile_wsi.py` (256²@20×, Otsu) 5장 무수정 실행 |
| 임베딩 호환 | ✅ 재사용 성공 | `extract_uni.py` UNI v1 → (3501, 1024), 로컬 캐시 |
| 라벨 조인 | ✅ 126/126 매칭 | `patient_slide_pcr.csv` |

**결론: GO** — download→tile→embed→(label join) 전 구간이 IMPRESS `.svs`에서 무수정으로 동작함. 전체 추출 착수 가능.

---

## 1. 데이터 스케일 (실측 n=5 기반 추정)

### 파일 용량 (HE 5장 실측)
| slide | size(MB) | dims | tiles | tissue_frac |
|---|---|---|---|---|
| 062_HE | 34.7 | 22004×24323 | 338 | 0.042 |
| 901_HE | 75.5 | 38007×18286 | 1219 | 0.116 |
| 067_HE | 142.7 | 32005×26205 | 2583 | 0.203 |
| 061_HE | 169.9 | 32005×34355 | 3501 | 0.209 |
| 904_HE | 190.4 | 36006×29161 | 4257 | 0.269 |
| **평균** | **122.6** | — | **2380** | 0.168 |

- **HE-only 용량 추정:** 126 × 122.6MB ≈ **~15 GB** (n=5, 편차 큼: 34.7–190.4MB → 실제 15±수 GB).
- **전체 252 (HE+IHC) 용량 추정:** IHC도 유사 규모 가정 시 **~30 GB** (IHC 미측정 → 거친 추정).
- **주의:** 전처치 biopsy라 조직량 편차가 크다(tissue_frac 0.04–0.27). 단일 ×252 수치를 확정치로 인용 금지.

### 타일 수 분포 (MIL 설계 입력)
- 5장 tile 수: 338 / 1219 / 2583 / 3501 / 4257 (평균 2380, **min bag = 338**).
- **per_slide_cap 5000: 5장 모두 미도달** → 현 cap 유지 적정. 상향 불필요.
- **tissue_threshold 0.1**: min bag 338(062_HE, 34.7MB 초소형 biopsy)도 MIL 학습 가능한 수준 확보. 재검토 불필요 판정 — 단 062류(조직 극소) 슬라이드는 QC에서 육안 확인 권장.
- 전체 HE tile 총량 추정: 126 × 2380 ≈ **~300K tiles** (n=5).

---

## 2. 전체 추출 비용 (GPU, UNI 실측 스루풋 기반)

**실측 (061_HE, 3501 tiles, A6000 cuda:0, batch 64):**
- 총 47.3s (모델로드+슬라이드open 포함), compute 37s → **≈ 95 tiles/sec** (UNI v1).

**HE-only 126장 (~300K tiles) 추출 시간 추정:**
| 모델 | dim | 추정 compute | 비고 |
|---|---|---|---|
| UNI v1 | 1024 | ~300K/95 ≈ 53min + 슬라이드 오버헤드 ~20min ≈ **~1.2 GPU-h** | 실측 스루풋 근거 |
| CONCH | 512 | UNI와 동급 or 더 빠름(추정 ~1 GPU-h) | 미측정, 동일 배치 파이프라인 |
| EXAONE(tile) | 768 | batch 32, 동급 order (추정 ~1.5 GPU-h) | ⚠ §5 인터페이스 주의 |

- **HE-only 3모델 총합 추정: ~3–4 GPU-h.** IHC까지(252장) 포함 시 **~7–8 GPU-h**.
- A6000 3장 병렬 시 wall-clock ~1–3h. **Paper A(TCGA 1010장) GPU 경쟁 고려 → 야간/유휴 슬롯 예약** (`#biop02-alerts`).
- 우선순위: **HE-only UNI 먼저**(주 목표 재현) → CONCH → (EXAONE/IHC는 확장 옵션).

---

## 3. 모델링 계획 (patient-level MIL for pCR)

- **입력:** HE 슬라이드 tile 임베딩 bag (환자=슬라이드 1:1, multi-slide bag 아님).
- **모델:** CLAM(-SB) attention MIL (sjpark 담당, Paper A와 동일 스택 재사용). 슬라이드당 tile 임베딩 → attention pool → pCR 이진 분류.
- **baseline (Critic #2):**
  1. random / majority-class
  2. mean-embedding + logistic (슬라이드 임베딩 평균)
  3. **IMPRESS 저자 40-feature tabular** (`data/features/IMPRESS/`) + pCR → 즉시 재현 가능한 강 baseline
  4. 논문 발표 pCR AUC와 대조
- **정직성 테스트 (Critic 관점):** "FM 임베딩이 임상변수 baseline을 이기는가?"
  - ⚠ 임상변수 **비대칭**: HER2+ = age/HER2·CEP17/ER/ER%/PR/PR%, TNBC = age만.
  - → **subtype별 clinical baseline 따로** 구성하거나, FM 경로는 subtype pooled로만 비교. 전 코호트 단일 clinical baseline 금지.

---

## 4. 평가 설계 (n 작음 = 126, 보수적)

- **CV:** subtype(HER2+/TNBC) × pCR 층화 **5-fold**, 환자 단위(=슬라이드 단위, leakage 위험 낮음).
- **n:** HER2+ 62 (pCR 38), TNBC 64 (pCR 27), 합 126 (pCR 65) — subtype당 ~60, fold당 ~12 → **분산 큼**.
- **필수 CI:** bootstrap 또는 repeated-CV 신뢰구간 동반 (단일 AUC 점추정 인용 금지).
- **지표:** AUC, AUPRC, balanced accuracy (metrics.json 계약 준수).
- **claim:** `hypothesis_only`, 단일기관 한계 명시.

---

## 5. EXAONE 인터페이스 주의 (실행 전 확인 필수)

- `extract_exaone.py`는 **tile/coords 기반**(768-dim, batch 32)으로 UNI/CONCH와 동일 경로 — 코드상 호환.
- ⚠ **그러나** memory `project_exaone_path2_interface` + commit `69fe4ce`: **EXAONE Path 2.0 = slide-level 인터페이스**(model(svs), exaonepath 패키지)로 coords 파이프라인과 별개일 수 있음.
- `extract_exaone.py`의 `load_exaone`이 tile-level(구 Path)인지 Path 2.0인지 **실행 전 1장 스모크 확인** 후에만 3모델 추출에 포함. 미확인 시 **UNI+CONCH 2모델로 착수**, EXAONE는 별도 트랙.

---

## 6. 외부 검증

- IMPRESS = **단일기관(OSU)** → 내부 CV만으로는 일반화 주장 불가.
- TCGA-BRCA에는 **전처치 NAC biopsy 없음** → Paper A 코호트로 외부검증 불가.
- 후보(접근성·전처치 H&E·pCR 라벨 **확인 필요**, 현재 미확보): TransNEO(Sammut 2022), I-SPY2, BCNB.
- **현 시점 확보된 외부검증셋 = 없음.** 확보 전까지 "단일기관 한계"로 정직하게 기술.

---

## 7. 실행 체크리스트 (착수 순서)

1. [ ] EXAONE tile-level 호환 1장 스모크 (§5) → 2모델 vs 3모델 결정.
2. [ ] 전체 126 HE `.svs` 다운로드 (`file_ids.txt`, ~15GB) — GPU 슬롯 예약 후.
3. [ ] batch tiling 126 HE → coords (per-slide QC: min bag / tissue_frac 로그).
4. [ ] UNI (→CONCH) 임베딩 추출, A6000 유휴 슬롯.
5. [ ] 추출 후 raw `.svs` 삭제 (LRU 정책 — embeddings/coords만 영구 보존).
6. [ ] sjpark: CLAM MIL + 4 baseline + 층화 5-fold CV + bootstrap CI.
7. [ ] Critic(braveji 총괄): 7항목, 특히 #1 leakage(전처치 biopsy=OK)·#2 baseline·#7 claim_level.
8. [ ] Tier B 정식 트랙 승격 여부 팀 결정(Paper A 리소스 경쟁 고려).

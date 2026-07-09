# IMPRESS — DATA_MANIFEST

Tier B 트랙: **pCR from pre-treatment H&E** (Paper A와 별개).
확보일: 2026-07-10 · 담당: kkkim (Embedding Agent)

## 데이터셋 개요

- **이름:** IMPRESS (IMage-based Pathological REgistration and Segmentation Statistics)
- **논문:** Huang et al., *AI Predicts Features Associated with Breast Cancer Neoadjuvant
  Chemotherapy Response from Multi-stain Histopathologic Images*.
  - GitHub 초판 표기 "Huang et al. 2022"; 저널판 = npj Precision Oncology 7:14 (2023),
    DOI `10.1038/s41698-023-00352-5`.
- **GitHub:** https://github.com/huangzhii/IMPRESS (default branch `main`)
- **코호트:** 오하이오주립대(OSU) IRB 승인. 신보조요법(NAC) 대상 침윤성 유방암, NAC 후
  수술적 절제 시행. 2011-01 ~ 2016-12.
- **이미지 = 전처치(pretreatment) biopsy** — 논문 Methods 근거(PMC9883475):
  IHC는 "performed on freshly cut whole sections from **pretreatment biopsies**",
  RCB는 "comparing the **pre-treatment core needle biopsy** with the post-treatment
  resection specimen"로 산출. → **절제표본(post-NAC excision) 아님**. pCR을 전처치 H&E로
  예측하는 Tier B 프레이밍과 정합, **leakage 없음**(Critic #1 관점 중요).
- **염색:** H&E + IHC. IHC 마커(paper Methods + meta xlsx 정량 컬럼) = **PD-L1(SP263),
  CD8, CD163(SP57), PD-1**. 배율 = **20× (~0.5 µm/pixel), Hamamatsu 스캐너**
  (논문: "scanned into WSIs using Hamamatsu scanner with 20x magnification"). 모두 근거 있음.
- **라이선스:** 코드+GitHub feature/clinical CSV = **MIT** (© 2022 Zhi Huang).
  논문 = **CC BY** (© The Author(s) 2023). Drive WSI(deid)는 별도 라이선스 명시 없음
  (Drive README = svs-deidentifier 툴 고지만). 학술 연구용 사용은 안전.

## n / 라벨 분포 (다운로드한 clinical CSV로 직접 확인)

| Subtype | n | pCR (=1) | residual (=0) |
|---|---|---|---|
| HER2+ | 62 | 38 | 24 |
| TNBC | 64 | 27 | 37 |
| **합계** | **126** | **65** | **61** |

- 라벨 컬럼 = `pCR` (1=pathologic complete response, 0=residual disease).
- 부가 라벨: RCB value / RCB category, residual tumor size, ypT/ypN(TNBC), Response,
  ER/PR/HER2(HER2+ clinical), Nuclear grade 등 (meta xlsx `supp_2_cohort_meta.xlsx`).
- **환자 = 슬라이드 = 라벨 1:1** (multi-slide/bag 아님). Patient ID가 곧 파일명 prefix.

## 파일 형식 — 2계층으로 공개됨

### (A) GitHub repo 내부 = **엔지니어링 feature CSV + 임상 CSV** (이미 다운로드 완료, 총 160KB)

| 경로 | shape | 내용 |
|---|---|---|
| `data/clinical/HER2+.csv` | 62×8 | age, HER2/CEP17 ratio, ER, ER%, PR, PR%, **pCR** |
| `data/clinical/TNBC.csv` | 64×3 | age, **pCR** |
| `data/features/IMPRESS/HER2+.csv` | 62×40 | IMPRESS 파이프라인 정량 feature (stroma/tumor/... region별) |
| `data/features/IMPRESS/TNBC.csv` | 64×40 | 동일 |
| `data/features/pathologists/HER2+.csv` | 62×6 | 병리의 수기 평가 feature |
| `data/features/pathologists/TNBC.csv` | 64×7 | 동일 |
| `data/meta/supp_2_cohort_meta.xlsx` | HER2+ 62×33, TNBC 64×19 | 전체 임상+IHC 정량 메타 |
| `data/LICENSE` | — | MIT |

> ⚠️ 이 feature는 **딥러닝 임베딩이 아니라** IMPRESS 파이프라인(HE/IHC 정합→분할→통계)이 산출한
> **수작업 정의 정량 feature(40개)**. 우리 UNI/CONCH/EXAONE 임베딩과는 별개.

### (B) Google Drive = **raw WSI (.svs, deidentified)** — 다운로드 보류(용량 미확정)

- **링크:** `tinyurl.com/IMPRESS-DATA` → 301 →
  `https://drive.google.com/drive/folders/1fNf-F_aplm6ACJTWO1vGqbb-DdaP4K_r`
  (폴더명 `IMPRESS_DEID_IMAGES`).
- **구조** (public folder view로 파일명 열거, 목록 = `data/wsi_drive_listing/`):
  - `HER2+_deid/` — **124** `.svs` = 62×`{id}_HE.svs` + 62×`{id}_IHC.svs` (id 061–124)
  - `TNBC_deid/` — **128** `.svs` = 64×`{id}_HE.svs` + 64×`{id}_IHC.svs` (id 901–991)
  - `cohort_meta.xlsx`, `README.md` (Drive 루트)
  - **총 252개 `.svs`** = HE 126 + IHC 126.
- **형식:** `.svs` (openslide 호환; svs-deidentifier로 deid. 원 스캐너 Hamamatsu 20×).
  환자당 HE 1장 + IHC 1장.
- **용량:** ⚠️ **미확정.** public folder view가 per-file/합계 용량을 노출하지 않음.
  정확한 용량은 Drive API(auth) 또는 실제 다운로드 필요. `.svs` 20× WSI 통상 규모상
  수십~수백 GB대로 **추정만** 함(수치 확정 아님, 절대 인용 금지).

## 우리 파이프라인 적용 경로

1. **바로 MIL 가능한 경로 (즉시):** GitHub의 IMPRESS 40-feature CSV + pCR 라벨 →
   환자당 1 벡터이므로 MIL이 아니라 **단순 tabular classifier**(우리 baselines/mlp.py급)로
   즉시 재현/벤치마크 가능. 단 이건 저자 feature이지 우리 임베딩이 아님 → 논문 기여로는 약함.
2. **우리 임베딩 파이프라인 경로 (주 목표):** raw `.svs` = openslide 호환이므로
   기존 `agents/embedding/scripts/tile_wsi.py`(256×256 @20×, Otsu) →
   `extract_uni/conch/exaone.py` **재사용 가능**. HE 슬라이드로 tile→embed→
   patient-level MIL(sjpark, CLAM/attention) → pCR 예측. IHC 슬라이드는 옵션(멀티스테인 확장).
   - 전처치 biopsy라 조직량이 절제표본보다 작음 → per-slide tile 수 적을 수 있음(cap 재검토).
3. **라벨/split:** patient=slide 1:1이라 leakage 위험 낮음. subtype(HER2+/TNBC)별 층화 +
   pCR 층화 CV 권장(n 작음, 126). 외부 validation 없음(단일 기관) → claim 보수적으로.

## 다운로드 상태 / 다음 스텝

- ✅ 완료: feature CSV × 6, clinical CSV × 2, meta xlsx, LICENSE, WSI 파일목록(252개 이름).
- ⏸ 보류: raw `.svs` 252개 (용량 미확정, Drive). 다운로드는 tiling 착수 결정 후.
- **다음 스텝:**
  1. (kkkim) Drive `.svs` 1장 샘플 다운로드 → openslide 열림·배율·크기 확인 → 총 용량 추산.
  2. (kkkim) HE 슬라이드로 tile_wsi.py 파일럿 1장 → 파이프라인 호환 실증.
  3. (jamie/kkkim) patient↔svs↔pCR 라벨 조인 테이블 작성(id prefix 매칭).
  4. (팀 결정) Tier B를 정식 트랙으로 승격할지 — Paper A 리소스와 GPU 경쟁 고려.

## 출처 무결성 노트

- 위 n·라벨 분포·파일 개수·형식은 **실제 다운로드 파일 및 public folder listing 근거**.
- pretreatment biopsy 여부·20× 배율·IHC 마커·라이선스는 **논문 full text(PMC9883475, CC BY) Methods 근거**.
- WSI 총 용량은 folder view가 노출하지 않아 **미확정으로 표기**(추정치 인용 금지).
- Drive는 환자당 `_IHC.svs` 1장으로 번들 — 단일 슬라이드에 어느 마커가 담겼는지(멀티스테인/개별)는
  folder view만으로 확정 불가. 논문은 PD-L1/CD8/CD163/PD-1 IHC를 별도 섹션에서 수행했다고 기술 →
  실제 슬라이드 매핑은 샘플 다운로드로 확인 필요.

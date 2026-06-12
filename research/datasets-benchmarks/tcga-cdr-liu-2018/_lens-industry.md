# Industry / Access Lens — Getting and using TCGA-CDR

## 어디서 받나 / Where to get it
1. **Supplementary Table S1** of Liu et al. 2018 (*Cell*) — open the tab labeled
   **`TCGA-CDR`**. This is the single curated table: one row per patient
   (`bcr_patient_barcode`), columns for OS / OS.time, PFI / PFI.time, DFI / DFI.time,
   DSS / DSS.time plus demographics and stage. **11,160 rows / 33 types.**
2. **GDC PanCanAtlas** publications page
   (`gdc.cancer.gov/about-data/publications/pancanatlas`) re-hosts the same curated
   clinical TSV alongside the other Pan-Cancer Atlas freeze files — convenient for
   programmatic joins. 원본 cell.com 본문은 **HTTP 403**으로 직접 fetch가 막혀 있어,
   접근은 **Table S1 또는 GDC PanCanAtlas**가 사실상의 경로다.
3. **GDC harmonized clinical** (`portal.gdc.cancer.gov`) has live clinical data, but
   it is **not** the CDR-curated/endpoint-graded version — prefer Table S1/PanCanAtlas
   for the *curated* endpoints and usability flags.

## 라이선스·접근 등급 / License & access tier
- TCGA-CDR의 임상 outcome 필드는 **open-access** (controlled-access 체세포 변이와 달리
  dbGaP/PI 서명 불필요). BIOP02의 Paper A 범위(개방형 슬라이드 + 임상)와 정합.
- 데이터는 **research/publication use** 전제. 우리 프로젝트의 academic-only 산출물 정책과
  일치.

## 엔지니어링 통합 / Engineering integration
- 포맷: **TSV/XLSX** 단일 테이블. pandas로 즉시 로드 가능, 별도 ETL 불필요.
- 조인 키: `bcr_patient_barcode` (예: `TCGA-A1-A0SB`). WSI 파일명·매니페스트의 환자
  바코드와 substring 매칭/정규화 후 left-join.
- 권장 사용: BRCA 행만 필터 → **PFI/DFI 컬럼만** 모델 라벨로 채택, OS/DSS는 보조/민감도
  분석으로만 (이벤트 부족).

## 함정 / Gotchas
- **시간 단위**: `*.time` 컬럼은 **days**. 모델/플롯에서 month 변환 시 일관성 유지.
- **버전 드리프트**: GDC live clinical ≠ CDR. 두 소스를 섞으면 라벨 정의가 어긋남 →
  반드시 **CDR(Table S1/PanCanAtlas) 단일 소스**로 고정.
- BRCA OS 이벤트 ~151/1,097 → OS 기반 모델은 **underpowered**; 산업적 데모용으로도
  PFI/DFI를 기본값으로.

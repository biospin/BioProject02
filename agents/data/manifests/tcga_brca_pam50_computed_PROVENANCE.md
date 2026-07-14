# tcga_brca_pam50_computed.csv — provenance (BIOP02-49 후속 #1)

담당: kkkim (Embedding/Data) | 2026-07-10 | BIOP02-49 QC 후속(jamie 요청 #1: PAM50 소스 재확인·커밋)

## 무엇인가
`tcga_brca_manifest.csv`의 `pam50` 컬럼이 유래한 **원본 소스 파일**. 그동안 로컬(`~/data/clinical/`)에만 있어 레포에 미커밋 → `split_policy_v0.md`의 "라벨 정의 단일 소스 고정" 요구를 못 채우던 gap을 닫는다.

- 파일: `agents/data/manifests/tcga_brca_pam50_computed.csv`
- 컬럼: `case_id, pam50_subtype, pam50_confidence`
- 행수: 1218 case (TCGA barcode). 값: LumA/LumB/HER2/Basal/Normal.
- confidence: min 0.808 · max 0.925 · mean 0.867 (전부 고신뢰 구간).

## 소스 정체 (jamie의 57% 불일치 규명)
**cBioPortal의 curated study가 아니라, Parker 2009 PAM50 nearest-centroid classifier로 발현에서 계산한 라벨이다.**
- 근거 문헌: Parker et al. 2009, JCO, PAM50 (DOI `10.1200/JCO.2008.18.1370`). 요약 = `research/datasets-benchmarks/parker-2009-pam50/parker-2009-pam50_brief.md`.
- `pam50_confidence` 컬럼(centroid 상관 기반)이 계산본임을 방증.
- 그래서 jamie가 QC에서 본 **pan-can atlas 2018과 57.0% concordance**는 오류가 아니라 **다른 파생**(로컬 Parker 계산 vs curated atlas study)이라 나온 정상 현상이다. TCGA PAM50 재산정은 배치·구현 간 불일치가 문헌상 알려져 있다.

## 소스 확정 검증
- `tcga_brca_manifest.csv`의 pam50값 있는 case **1009개 전부(1009/1009 = 100%)** 이 파일과 일치. → manifest PAM50이 이 파일에서 왔음이 확정.
- 반례로 `~/data/clinical/tcga_brca_pam50.csv`(77행)는 pam50 컬럼에 'T_Other'·'Invasive Breast Carcinoma' 등 비-PAM50 값이 섞인 **깨진 파일** — 소스 아님(폐기 대상).

## 남은 gap (완전 재현용 후속)
- 이 CSV를 만든 **계산 스크립트 + 입력 발현 행렬(어느 study의 expression)** 은 아직 레포에 없다. 완전 재현을 위해 그 스크립트·입력 출처(study_id/버전)를 추후 커밋 권장. 현재로선 "Parker 2009 classifier로 계산, confidence 동반"까지 확정.
- PAM50은 Paper A에서 형태학이 이득을 보인 유일 엔드포인트(CLAM-MB 0.759)이므로, 라벨 정의 문서화 가치가 높다.

## 정책 정합
- Normal/Normal-like는 `build_manifest.py`의 `PAM50_MISSING`으로 다운스트림에서 제외(§4). manifest `has_pam50=882`(1009 raw 중 Normal 등 제외).
- split 불변: 이 소스는 `split_hash=5995f29d3978b831` 코호트 라벨의 출처일 뿐, split 배정과 무관.

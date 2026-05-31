# Therapeutic Evidence Agent — Skills & Work Log

**Author**: 서정한 (@jhans) | **Last updated**: 2026-06-01

---

## Sprint 0 (5/12 – 5/22)

### BIOP02-35 — 서버 환경 초기화
- 서버(61.109.239.220, 포트 2206) SSH 접속 확인
- `/workspace/agents/therapeutic_evidence/` 디렉토리 생성
- Therapeutic Evidence Agent 작업 공간 초기화 완료

### BIOP02-36 — DepMap PRISM + GDSC 데이터 소스 조사
- DepMap PRISM 24Q2 및 GDSC Release 8.5 두 데이터베이스의 전체 구조 파악
- 각 DB의 다운로드 경로, 핵심 파일 목록, 주요 컬럼 구조 정리
- BRCA 세포주 필터링 방법 (OncotreeLineage / TCGA_DESC) 코드 예시 작성
- 두 DB 통합 전략 정의: cell line 조인(SangerModelID 우선, COSMICID fallback), drug 조인(PubChem CID 우선)
- 라이선스 요약 (DepMap CC BY 4.0 / GDSC 학술 무료)
- 산출물: [`docs/BIOP02-36_depmap_gdsc_sources.md`](docs/BIOP02-36_depmap_gdsc_sources.md)

---

## Sprint 1 (5/22 – 6/05)

### BIOP02-45 — DepMap PRISM + GDSC 스키마 초안 (컬럼 확정)
- `schemas/hypothesis.schema.json` 역추적: `hypothesis[].confidence`, `drug_class`, `rationale`, `data_source` 필드 요구사항 분석
- 프로젝트에서 실제로 사용할 최소 컬럼 4개 카테고리로 확정:
  1. **Cell line 식별 / BRCA 필터링**: `ModelID`, `OncotreeLineage`, `SangerModelID`, `COSMIC_ID` 등
  2. **감수성 지표** (`confidence` 계산): PRISM `AUC`, GDSC `LN_IC50`, `Z_SCORE`
  3. **약물 어노테이션** (`drug_class` / `rationale`): `MOA`, `target`, `PATHWAY_NAME`, `PUTATIVE_TARGET`
  4. **Drug cross-link**: `pubchem_cid` ↔ `PUBCHEM`
- Python 최소 로드 컬럼 코드(`DEPMAP_MODEL_COLS`, `PRISM_COMPOUND_COLS` 등) 확정
- BIOP02-36 문서 v0.2로 업데이트 (§3.4 추가)
- 산출물: [`docs/BIOP02-36_depmap_gdsc_sources.md`](docs/BIOP02-36_depmap_gdsc_sources.md) §3.4

### BIOP02-52 — PRISM vs GDSC Consistency 검증 방법 문서화
- PRISM과 GDSC의 IC50/AUC 직접 비교가 부적절한 이유 분석 (Haibe-Kains et al. Nature 2013 기반)
  - 스크리닝 방식, dose 범위, viability assay, 정규화 방법이 모두 다름
- 5단계 일관성 검증 절차 정의:
  1. SangerModelID 기준 BRCA cell line 교집합 추출
  2. PubChem CID 기준 drug 교집합 추출
  3. 각 DB 내 drug별 z-score 변환 (절댓값 비교 금지)
  4. 공통 (cell line × drug) 쌍에 대해 Spearman 상관계수 계산
  5. ρ ≥ 0.3 && p < 0.05 기준으로 `data_source: "both"` 태깅
- 출력물 형식 정의 (`consistency_scores.csv`): BIOP02-60에서 `hypothesis[].data_source` 직접 매핑
- 산출물: [`docs/BIOP02-52_prism_gdsc_consistency.md`](docs/BIOP02-52_prism_gdsc_consistency.md)

---

## 다음 예정 작업

| 티켓 | 내용 | 선행 조건 | 예정 스프린트 |
|---|---|---|---|
| BIOP02-52 v0.2 | 실측: BRCA cell line/drug 교집합 count, Spearman ρ 분포 | PRISM·GDSC 데이터 다운로드 | S2 (6/05~) |
| BIOP02-60 | Endocrine rule sample (DepMap transfer 초안) | sjpark MLP 결과 (6/05~) | S4 |
| BIOP02-67 | Anti-shortcut sanity 검증 지원 | gglee Critic 작업 시작 | S5 |
| BIOP02-80 | Paper B 기획 착수 | Paper A 완성도 70%+ | S8 |

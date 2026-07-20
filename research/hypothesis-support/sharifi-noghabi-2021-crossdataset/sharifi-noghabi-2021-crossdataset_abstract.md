# Sharifi-Noghabi 2021 — Guidelines for ML drug-sensitivity predictors (cross-dataset generalization)

## 서지
- **Title:** Drug sensitivity prediction from cell line-based pharmacogenomics data: guidelines for developing machine learning models
- **Authors:** Hossein Sharifi-Noghabi, Soheil Jahangiri-Tazehkand, Petr Smirnov, Casey Hon, Anthony Mammoliti, Sisira Kadambat Nair, Arvind Singh Mer, Martin Ester, Benjamin Haibe-Kains
- **Venue:** Briefings in Bioinformatics, Vol. 22, Issue 6 (Nov 2021), article bbab294
- **DOI:** 10.1093/bib/bbab294
- **Source status:** verified via WebFetch (OUP) — abstract + full author list confirmed.

> ⚠️ **출처 정정(검증됨):** 상위 태스크는 이 논문을 "Sharifi-Noghabi 2024, PMC11043358,
> cross-dataset Spearman ≈ 0.2–0.25"로 지목했으나, 이는 서로 다른 두 문헌의 혼동이다.
> (1) 실제 논문은 **2021년** Briefings in Bioinformatics(bbab294). (2) **PMC11043358**은
> 전혀 다른 논문 — Ovchinnikova et al. 2024, *npj Precision Oncology* 8:95(약물반응
> z-scoring), Sharifi-Noghabi는 저자 아님. (3) "Spearman ≈ 0.2–0.25" 수치는 이 논문
> **초록에 명시돼 있지 않다**(아래 참조) — **미검증**으로 남긴다.

## 초록 요약 (faithful)
정밀종양학의 목표는 종양 유전체 프로파일로 환자별 치료를 맞추는 것이다. 세포주 같은
파마코지노믹스 데이터셋은 약물 민감도 예측(정밀종양학의 핵심 과제)에 가장 값진 자원이며,
대규모 세포주 패널의 다중 오믹스로 ML 모델이 학습돼 왔다. 그러나 **약물 민감도 예측
모델을 어떻게 제대로 학습·검증할지에 대한 종합 가이드라인이 없었다.** 이 논문은 세포주
데이터로 발현 기반 예측기를 학습할 때의 여러 측면에 대한 가이드라인을 제시한다. 이
가이드라인은 약물 민감도 예측기의 **일반화(generalization)를 광범위하게 분석**하며,
**학습 데이터셋 선택과 약물 민감도 측정치(measure) 선택** 등 현재 관행 상당수에
문제를 제기한다. 향후 연구에 이를 적용하면 더 견고한 전임상 바이오마커 개발이 가능하다.

**검증된 본문 수치(교차-도메인 일반화, 초록 밖 발췌):**
- CTRPv2로 학습 → gCSI 테스트: **Pearson 0.4 ± 0.21**
- GDSCv1로 학습 → gCSI 테스트: **Pearson 0.26 ± 0.16**
- 즉 데이터셋을 넘나들면 예측 상관이 낮고 **학습 데이터셋/측정치에 따라 결과가 크게 바뀐다.**
- (상위 태스크가 말한 "Spearman ≈ 0.2–0.25"는 이 논문 초록에서 확인되지 않음 — 위 Pearson
  ~0.26이 가장 근접한 검증값. 정확한 Spearman 값이 필요하면 본문/원출처 수동 확인 필요.)

## 우리 논문에서의 역할
- **축 독립성(axis-independence) 근거.** 보류된 치료-근거 엔진(Paper B)은 기전적으로
  독립인 축들 — 약물-생존(PRISM/GDSC/CTRP), CRISPR 의존성(DepMap Chronos), 전사체 역전
  (LINCS L1000) — 의 **수렴(convergence)** 으로 가설을 세운다. 이 논문은 **약물-생존
  데이터셋들끼리도 교차-데이터셋 일관성이 낮고 측정치/데이터셋 선택에 민감**함을 보여,
  **PRISM·GDSC·CTRP를 3개의 독립 축으로 삼분(triple-count)하면 안 된다**는 핵심 논거를
  제공한다. 이들은 동일 readout(생존)을 공유하므로 하나의 축으로 취급하고, 진짜 독립
  축은 서로 다른 readout(생존 vs 유전자 의존성 vs 전사체 역전)에서 나온다.
- **인용 위치:** 치료-근거 축 설계의 Methods/Rationale에서, "convergence는 readout이
  다른 축들 사이에서만 의미가 있다"는 문장의 anchor로 사용. Haibe-Kains 계열의
  파마코지노믹스 비일관성 문헌 계보(교차-데이터셋 discordance)에 연결.
- **주의:** 이 논문 자체는 형태(morphology)·전사체 역전 타당성에 대한 문헌이 **아니다**.
  오직 **약물-생존 축 내부의 비일관성**(→ 삼분 금지)만 뒷받침한다.

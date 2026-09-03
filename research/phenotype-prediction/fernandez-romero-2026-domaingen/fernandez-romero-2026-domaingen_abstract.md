# Fernandez-Romero et al., 2026 — Domain generalisation in BC molecular classification — Abstract 분석

> 근거 자료: `sources/fernandez-romero-2026-domaingen_pmc.xml`(Europe PMC JATS 전문) + `sources/fernandez-romero-2026-domaingen.pdf`(본문 11p). 2026-09-02 전문 재분석으로 갱신했고, 그 전 판본은 초록만 보고 작성된 것이라 수치가 비어 있었다.
>
> 표기: `해석:` / `계산값:` / `원문 미확인:`(본문·표에서 찾지 못함, 대개 Supplementary PDF 소재).

## 서지

- **Title**: Domain generalisation challenges in breast cancer molecular classification using foundation models: a cross-cohort exploratory study
- **Authors**: Jesus Fernandez-Romero, Pablo Ramos-Berciano, Manuel Perez-Perez, David Benavides, Antonio Robles-Frias, Jorge Garcia-Gutierrez, Laura Macias-Garcia
- **Venue**: *Medical & Biological Engineering & Computing* **64(6):2321–2331** (2026)
- **DOI**: [10.1007/s11517-026-03590-4](https://doi.org/10.1007/s11517-026-03590-4) · PMC13269319 · PMID 42113320 · CC-BY 4.0
- **소속**: Universidad de Sevilla, Hospital Universitario Virgen de Valme (스페인 세비야)
- **Citation key**: `fernandez-romero-2026-domaingen`
- **Funding**: MICIU/AEI PID2023-147688OA-I00, Data-pl(PID2022-138486OB-I00), SENSOLIVE(PLSQ_00162). 이해상충 없음 선언.

## Abstract 요약

- **한 문장 요약**: 병리 foundation model(FM) 13종과 MIL 아키텍처 3종을 PAM50 아형과 ER/PR/HER2 예측에 붙여 TCGA-BRCA(n=1,079)에서 교차검증하고 CPTAC-BRCA(n=120)로 외부검증한 뒤, 코호트 간 성능 열화(RPD)를 네 가지 도메인 시프트 요인으로 회귀해 원인을 나눈 탐색적 연구.
- **문제의식**: 대부분의 선행연구가 같은 기관 내부 검증만 보고하고 외부 코호트를 시험하지 않아, 도메인 일반화가 검증되지 않은 채로 남아 있다.
- **핵심 방법**: 13 FM(SOTA 12종 + ResNet-50 baseline)을 baseline CLAM으로 먼저 선별하고, 최고 FM 하나(Virchow v2)에 Optuna로 최적화한 CLAM, TransMIL, DSMIL 3종을 붙여 열화 패턴이 아키텍처 의존인지 확인한다. 지표는 PAM50 macro-F1, ER/PR/HER2 PR-AUC.
- **주요 결과**: Virchow v2가 종합 1위(mean rank 2.00)지만 외부검증에서 심한 열화를 보이고, 그 열화는 3개 MIL 전부에서 같은 방향으로 나타난다. HER2-enriched와 Normal-like 아형, HER2-양성 IHC에서 특히 크다.
- **요인분해**: 네 요인 중 염색 변이(Δn), 특징공간 발산(d), 형태 분리도(B̃)가 단변량에서 유의하고 유병률 시프트(Δp)는 유의하지 않다(q=0.615). 최종 다변량 모형 `RPD ~ Δn + d`가 RPD 분산의 80.0%를 설명한다(R²=0.800, R²adj=0.750, F=16.03, q=0.005).
- **저자 스스로의 한정**: 클래스 수준 관측치가 11개뿐이라 회귀는 탐색적이고 가설 생성 수준이라고 본문에 명시한다.

## 우리 논문(BIOP02 Paper C)에서의 역할

- **최근접 스쿱**: 우리가 유방 단독 예측 논문(구 Paper A)으로 하려던 설계, 곧 H&E FM+MIL로 PAM50과 ER/PR/HER2를 예측하고 TCGA에서 학습해 CPTAC로 외부검증하는 구성이 같은 코호트, 같은 동기로 이미 출판되었다. 유방을 flagship Paper C(치환비용 결정지도)로 흡수하게 만든 직접 원인이 이 논문이다.
- **인용 방식**: 예측 정확도를 헤드라인으로 삼지 않는다. "H&E에서 분자 아형을 예측하는 일과 그 외부 열화는 이미 보고되었다[Fernandez-Romero 2026]"로 한 줄 양보한 뒤 곧바로 결정가치(치환비용) 프레임으로 넘어간다.
- **동시에 우리 전제의 근거**: 이 논문의 외부 붕괴는 "예측만으로는 취약하므로 치환에는 계량 가능한 비용이 따르고 보정과 기권이 필요하다"는 SUBSTITUTABILITY_LAW의 외부 근거로 쓸 수 있다.
- **분할 설계 차이가 새로 확보된 대조축**: 전문에서 확인한 바로는 이 논문의 내부 검증이 환자 층화만 하고 기관(tissue source site)을 통제하지 않는다. 우리는 사전 고정된 site-disjoint 분할을 쓴다. 상세 대조는 `_comparison-with-biop02.md`.

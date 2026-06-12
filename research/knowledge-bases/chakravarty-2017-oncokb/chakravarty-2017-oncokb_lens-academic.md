# chakravarty-2017-oncokb — Lens: Academic

## 학술적 위상 (Academic standing)
OncoKB는 변이 임상해석(clinical variant interpretation) 분야의 표준 레퍼런스 중 하나로, **FDA가 인정한 최초의 종양 변이 데이터베이스**(Public Human Genetic Variant Database 등재)다. 이 FDA recognition은 단순 학술 인용을 넘어 **규제적 신뢰성**을 부여하며, npj Precision Oncology 같은 타깃 저널 리뷰어가 actionability 주장의 근거로 기대하는 자원이다.
OncoKB is a standard reference for clinical variant interpretation and the first FDA-recognized tumor-mutation database. This gives its level assignments regulatory credibility that reviewers at precision-oncology venues treat as the actionability gold standard.

## 방법론적 강점 (Methodological strengths)
- **이중 축 분리:** oncogenicity(변이가 driver인가)와 actionability(약물 함의가 있는가)를 분리 — 우리 파이프라인의 "phenotype 예측"과 "therapeutic hypothesis"를 명확히 구분하는 데 직접 대응.
- **종양형 특이성:** 동일 변이도 종양형에 따라 레벨이 달라짐(예: 다른 적응증 → Level 3B). BRCA-only scope에서 cross-tumor 일반화를 경계하라는 강한 신호.
- **위계적 evidence tier:** Level 1(FDA) → 4(생물학적 근거) → R(내성)의 순서가 우리 Critic #5 plausibility 점수를 **연속값이 아닌 서열척도(ordinal)** 로 다루게 해준다.

## 학술적 한계 (Limitations for our use)
- **큐레이션 시점 의존:** 빈번한 업데이트로 published 수치(418 genes / >3,000 alterations)는 스냅샷일 뿐 — 인용 시 접근 날짜 명시 필요.
- **재배포 불가:** 전체 주석 다운로드를 정책적으로 막음(아래 industry lens) → 논문 부록에 OncoKB 테이블 전체를 싣는 식의 재현은 불가, **API 조회 결과만** 보고 가능.
- **BRCA-targeted-therapy 편향:** Level 1 actionable 비율(7.5%)은 pan-cancer 평균이며 유방암·종양형별로 다름 — 우리 결과를 이 숫자에 직접 비교 금지.

## 우리 논문에서의 인용 전략 (Citation strategy)
Exp4/Exp5에서 OncoKB를 **gold actionability tier 정의**로 인용하되, 우리가 실제 매칭에 쓰는 것은 오픈 KB(CIViC/Open Targets/DGIdb)임을 명시하고 "OncoKB 레벨에 대한 근사 + 잔여 gap"으로 정직하게 프레이밍한다.

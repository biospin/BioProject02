# tsherniak-2017-depmap — brief

Tsherniak 등(2017, Cell)은 **Cancer Dependency Map(DepMap)**을 정의한 논문으로, 대규모 cell line 패널에서 RNAi(및 후속 CRISPR) 유전자 녹다운/녹아웃이 생존에 미치는 효과를 측정해 암세포가 의존하는 유전자(genetic dependency)를 체계적으로 지도화했다. 핵심 기여는 분자특징과 유전자 의존성의 연관을 통해 cell line별 취약점(vulnerability)을 예측 가능하게 한 dependency framing이다. BIOP02 관련성(DRUG=약물민감도 전이 자원): PRISM(약물 viability)이 BIOP02의 1차 약물 축이라면, DepMap의 **유전자 의존성**은 이를 보완하는 직교 신호다 — 예측된 BRCA 표현형이 특정 경로/유전자 의존성을 시사할 때, 그 유전자를 표적하는 약물 가설을 dependency 근거로 지지·교차검증할 수 있다(Critic #5 생물학적 타당성 보강). 약물 구조 입력이 없는 표현형-매개 조회이므로 DRP가 아니며, 출력은 hypothesis-only 랭킹임에 유의. *DOI unverified — 인용 전 CrossRef 재확인 필요.*

In short: DepMap defines genetic dependencies (RNAi/CRISPR) that complement PRISM's drug-viability axis, letting BIOP02 cross-support phenotype-implied target/drug hypotheses with dependency evidence (Critic #5) — a phenotype-mediated, hypothesis-only use, not DRP. (unverified)

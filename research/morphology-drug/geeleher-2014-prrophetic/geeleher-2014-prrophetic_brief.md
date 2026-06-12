# geeleher-2014-prrophetic — brief

Geeleher 등(2014, PLOS ONE)의 **pRRophetic**은 종양 유전자 발현으로부터 임상 화학요법 반응을 예측하는 표준 R 패키지로, 동일 저자의 전이 방법론(geeleher-2014-transfer)을 재현 가능한 소프트웨어로 구현한 것이다. cell line(GDSC) 발현→약물 민감도 모델을 ridge 회귀로 학습하고, 배치효과 보정·동질 유전자 매핑을 거쳐 환자 종양 발현에 적용해 약물별 예측 민감도를 imputation한다. 핵심 기여는 발현→민감도 전이를 누구나 재현할 수 있는 파이프라인으로 패키징해 사실상 표준 도구로 만든 점이다. BIOP02 관련성(DRUG=약물민감도 전이 자원): BIOP02가 예측한 분자표현형(발현 proxy)을 cell-line 민감도로 변환하는 단계의 **참조 구현/베이스라인**으로, 전처리(배치보정·유전자 정합) 관례를 차용하거나 대조군으로 인용한다. 단 BIOP02는 약물 구조를 입력하지 않고 출력이 hypothesis-only 랭킹이라 mainstream DRP와 구분되며, pRRophetic은 "기존 표준 도구" 위치다. *DOI unverified — 인용 전 CrossRef 재확인 필요.*

In short: pRRophetic packages the expression→cell-line sensitivity transfer into a standard, reproducible R tool that BIOP02 cites as the reference implementation/baseline for its phenotype→drug imputation step — while BIOP02 stays hypothesis-only and drug-structure-free, not DRP. (unverified)

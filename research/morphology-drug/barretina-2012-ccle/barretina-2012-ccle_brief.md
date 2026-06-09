# barretina-2012-ccle — brief

Barretina 등(2012, Nature)의 **CCLE(Cancer Cell Line Encyclopedia)**는 약 947개 cell line의 멀티오믹스(발현·변이·CNA)와 약리 프로파일을 결합해, 분자특징으로 항암제 민감도를 예측 모델링할 수 있음을 보인 기반 자원 논문이다. 핵심 기여는 대규모 cell line의 유전체-약리 매핑을 표준화해 이후 DepMap·GDSC 분석의 공통 분자 참조층을 제공한 것이다(*수치 reading_list/csv 기반, DOI unverified*). BIOP02 관련성(DRUG=약물민감도 전이 자원): CCLE는 DepMap의 기반을 이루며, BIOP02가 예측한 BRCA 분자표현형을 cell-line 공간에 정렬할 때 사용하는 **cell-line 발현/유전체 참조층**이다. PRISM·GDSC 민감도 값을 동일 cell-line 식별자로 연결·교차검증(Critic #4)하는 공통 좌표계 역할을 한다. 약물 구조 입력이 없는 표현형-매개 조회이므로 DRP가 아님에 유의. *DOI/수치 unverified — 인용 전 CrossRef 재확인 필요.*

In short: CCLE provides the standardized cell-line multi-omics reference layer underlying DepMap, serving as BIOP02's common coordinate system for aligning predicted BRCA phenotypes to cell lines and linking PRISM/GDSC sensitivity for cross-DB checks — a phenotype-mediated lookup, not DRP. (unverified)

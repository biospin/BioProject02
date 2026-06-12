# corsello-2020-prism — brief

PRISM(Profiling Relative Inhibition Simultaneously in Mixtures)은 분자 바코드로 수백 개 cell line을 동시에 풀링해 viability를 측정함으로써 **4,518개 약물 × 578개 cell line** 규모의 약물 민감도 프로파일을 구축한 자원 논문이다(*수치 reading_list/csv 기반, DOI unverified*). 핵심 기여는 비종양(non-oncology) 약물에서 선택적 항암 활성을 대규모로 스크리닝하고, cell line의 분자특징(발현·변이)으로 그 선택적 민감도를 예측할 수 있음을 보인 것이다. PRISM은 DepMap의 약물 축을 구성한다. BIOP02 관련성(DRUG=약물민감도 전이 자원): H&E→분자표현형으로 예측된 BRCA 표현형을 cell-line 발현 공간에 매핑한 뒤, PRISM viability 프로파일을 조회해 **랭킹된 hypothesis-only 치료 후보**를 산출하는 1차 약물 전이 소스다. GDSC와 교차해 PRISM↔GDSC 일관성(Critic checklist #4)을 검증하는 한 축으로 쓰인다. 본 프로젝트는 약물 구조를 입력하지 않으므로 이는 DRP가 아닌 표현형-매개 자원 조회임에 유의. *DOI/수치 unverified — 인용 전 CrossRef 재확인 필요.*

In short: PRISM defines the large-scale drug × cell-line viability resource underlying DepMap's drug axis, serving as BIOP02's primary sensitivity-transfer lookup for ranked, hypothesis-only therapeutic candidates and as one arm of PRISM↔GDSC consistency checking — not a DRP input. (unverified)

# seashore-2015-ctrp — brief

Seashore-Ludlow 등(2015, Cancer Discovery)은 **CTRP(Cancer Therapeutics Response Portal)**의 대규모 small-molecule 민감도 데이터셋(약 860 cell line × 481 compound)을 구축하고, 민감도-분자특징 간 연결성(connectivity)을 활용해 작용기전·취약점을 추론한 자원 논문이다(*수치 reading_list/csv 기반, DOI unverified*). 핵심 기여는 GDSC·PRISM과 부분적으로 겹치되 독립적으로 생성된 cell-line 약물 민감도 매트릭스를 제공한 것이다. BIOP02 관련성(HYPO=직교검증): CTRP는 BIOP02 약물 랭킹의 **GDSC/PRISM와 독립인 세 번째 일관성 DB**다. 예측 표현형→cell-line 전이로 도출한 약물 후보가 PRISM·GDSC뿐 아니라 CTRP에서도 일관되게 민감하게 나오면, cross-dataset 일관성(Critic checklist #4)이 한층 강화되어 단일 DB 아티팩트에 의한 거짓 양성을 완화한다. 약물 구조 입력이 없는 표현형-매개 조회이며 출력은 hypothesis-only 랭킹임에 유의. *DOI/수치 unverified — 인용 전 CrossRef 재확인 필요.*

In short: CTRP provides an independently generated cell-line × compound sensitivity matrix that serves as BIOP02's third consistency DB beyond GDSC/PRISM, reinforcing cross-dataset agreement (Critic #4) and reducing single-DB false positives in hypothesis-only rankings. (unverified)

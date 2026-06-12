# wang-2025-truecam — brief

핵심 기여(core contribution): 병리 파운데이션 모델(UNI·CONCH) 기반 WSI 분석에 OOD 탐지와 conformal prediction을 결합한 **신뢰성 프레임워크(TRUECAM)**를 제안한다. The preprint integrates foundation-model WSI embeddings with out-of-distribution detection and conformal prediction to deliver trustworthy, uncertainty-aware predictions with finite-sample coverage guarantees, abstaining on unreliable or OOD slides.

방법 요지(method): FM 타일/슬라이드 임베딩 위에 OOD 게이트와 conformal 보정을 얹어, 신뢰할 수 없는 예측을 flag하고 coverage를 보장하는 예측 집합을 출력한다. arXiv preprint(2501.00053) — DOI **unverified**, 인용 전 확인 필요.

BIOP02 관련성(UQ — 불확실성 게이팅/해석성): SpatialPathoAgent와 동일하게 UNI/CONCH 임베딩 + conformal 불확실성을 사용하는 **가장 가까운 blueprint**다. 따라서 본 논문은 반드시 인용하되, BIOP02의 차별점(표현형-매개 framing, DepMap/GDSC 치료가설 전이, 독립 Scientific Critic 게이트, hypothesis-only 출력)을 delta로 명확히 구분해야 한다.

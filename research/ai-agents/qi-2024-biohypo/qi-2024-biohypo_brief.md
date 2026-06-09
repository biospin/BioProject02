# qi-2024-biohypo — brief

핵심 기여(core contribution): LLM을 **생의학 가설 생성기(biomedical hypothesis generator)**로 평가하여, 문헌 기반으로 새롭고 검증 가능한 가설을 만들 수 있는지와 그 한계를 종합적으로 분석한다. The study assesses LLMs' ability to produce novel, valid biomedical hypotheses, examining how retrieval, prompting, and uncertainty affect the quality and testability of generated hypotheses.

방법 요지(method): 문헌 코퍼스를 기반으로 가설 생성 과제를 구성하고, novelty·plausibility·검증가능성을 평가 프로토콜로 측정한다. COLM 2024 — DOI **unverified**(arXiv URL로 인용, AGENT 영역 다수 preprint).

BIOP02 관련성(AGENT — 시스템 framing): SpatialPathoAgent의 치료가설 생성은 이미 활발히 연구되는 영역(crowded)이므로, "LLM 가설 생성 자체"를 novelty로 내세우기 어렵다. 본 논문은 그 포화를 보여주며, BIOP02가 기여를 **method가 아니라 도메인 거버넌스·검증(Critic 게이트·cross-DB 일관성·hypothesis-only)**으로 재포지셔닝해야 함을 뒷받침한다.

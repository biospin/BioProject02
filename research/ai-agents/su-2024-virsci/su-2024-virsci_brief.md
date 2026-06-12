# su-2024-virsci — brief

핵심 기여(core contribution): 서로 다른 역할의 LLM 에이전트가 협업·토론하는 **멀티에이전트 과학 아이디어 생성 시스템(VirSci)**이 단일 에이전트보다 더 새롭고 가치 있는 연구 아이디어를 만든다는 점을 보인다. The paper demonstrates that a team of role-specialized LLM agents that collaborate and critique each other ("many heads") produces ideas with higher novelty and quality than a single agent acting alone.

방법 요지(method): 다수 에이전트에 역할을 부여하고 idea 제안·토론·선택 루프를 돌려, 생성 아이디어의 novelty·diversity를 baseline 대비 평가한다. ACL 2025 — DOI **unverified**(arXiv URL로 인용, AGENT 영역 다수 preprint).

BIOP02 관련성(AGENT — 시스템 framing): SpatialPathoAgent의 멀티에이전트 구조(Data·Embedding·Modeling·Therapeutic Evidence·Critic·Orchestrator)는 본 논문 등으로 이미 선행된 패러다임이다. 따라서 "멀티에이전트 = novelty"는 주장하기 어렵고(crowded), BIOP02의 delta는 협업 자체가 아니라 **도메인 거버넌스·독립 Critic 게이트·재현성 산출물**에 있음을 보여주는 근거다.

# lu-2024-aiscientist — brief

핵심 기여(core contribution): 아이디어 생성→실험 수행→결과 분석→논문 작성→자동 리뷰까지 전 과정을 LLM이 수행하는 **완전 자율 연구 파이프라인(The AI Scientist, Sakana)**을 제안한다. The paper presents an end-to-end framework where LLM agents autonomously generate research ideas, write and run code, produce manuscripts, and even peer-review them, demonstrating open-ended discovery at low cost on ML toy domains.

방법 요지(method): 코드 템플릿 위에서 idea proposal·실험 iteration·LaTeX 작성·LLM 자동 리뷰 루프를 연결하고, 생성 논문을 LLM-judge로 점수화한다. arXiv preprint(2408.06292) — DOI **unverified**(AGENT 영역 다수 preprint).

BIOP02 관련성(AGENT — 시스템 framing): SpatialPathoAgent는 **의도적으로 자율성을 제한**하여 hypothesis-only 출력과 인간 거버넌스를 둔다. 본 논문은 그 반대 극단(완전 자율)으로서 **대조군(autonomy contrast)** 역할을 하며, BIOP02가 "fully automated discovery"가 아니라 거버넌스·검증 중심 시스템임을 positioning하는 근거다. eval-2025-sakana의 비판적 평가와 함께 읽어야 한다.

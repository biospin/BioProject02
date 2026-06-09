# zheng-2023-llmjudge — brief

핵심 기여(core contribution): 강력한 LLM을 인간 평가의 확장 가능한 대리자로 쓰는 **LLM-as-a-judge** 패러다임의 타당성을 MT-Bench·Chatbot Arena로 검증하면서, 동시에 그 한계인 **position bias·verbosity bias·self-enhancement bias**를 정량화한다. The paper shows strong LLM judges agree well with human preferences yet exhibit systematic biases, providing both validation and caveats for automated evaluation.

방법 요지(method): pairwise·single-answer 채점에서 LLM judge와 인간 선호의 일치율을 측정하고, 답변 순서·길이·자기 모델 출력 선호로 인한 편향을 통제 실험으로 드러낸다. NeurIPS 2023 — DOI **unverified**(arXiv URL로 인용).

BIOP02 관련성(AGENT — LLM-judge 편향): SpatialPathoAgent의 Scientific Critic은 본질적으로 LLM-as-judge다. 본 논문은 (1) Critic을 자동 평가자로 두는 것의 **타당성 근거**이자, (2) position/verbosity/self-enhancement 편향을 인지해 완화해야 한다는 경고이며, (3) self-enhancement 편향이 BIOP02의 **owner≠reviewer(anti-self-reference)** 규칙을 직접 뒷받침한다.

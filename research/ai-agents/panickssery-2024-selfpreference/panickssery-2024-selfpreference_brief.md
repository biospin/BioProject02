# panickssery-2024-selfpreference — brief

핵심 기여(core contribution): LLM 평가자가 **자기 자신이 생성한 출력을 인식(self-recognition)**하고 그것을 더 높게 평가(self-preference)한다는 점을, 단순 상관을 넘어 **인과 관계**로 입증한다. The paper shows that an LLM's ability to recognize its own generations causally drives a self-preference bias when it acts as an evaluator, with self-recognition strength predicting the magnitude of inflated self-scoring.

방법 요지(method): self-recognition 능력을 fine-tuning으로 조절했을 때 self-preference가 함께 변하는지를 측정하는 개입(intervention) 실험으로 인과성을 확립한다. NeurIPS 2024 — DOI **unverified**(proceedings URL로 인용).

BIOP02 관련성(AGENT — LLM-judge 편향): SpatialPathoAgent의 Critic 교차검토(cross-review) 규칙(owner≠reviewer)이 왜 반드시 필요한지에 대한 **가장 강한 단일 근거**다. 같은 에이전트가 자신의 가설·결과를 평가하면 self-preference로 인해 게이트가 무력화되므로, BIOP02는 작성자와 Critic 담당을 분리하고 anti-self-reference를 절대 금지사항으로 둔다.

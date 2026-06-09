# gottweis-2025-coscientist — Academic Lens (FRAMING SCOOP)

## 정직한 진단: 이건 우리에 대한 scoop이다 (Honest scoop verdict)
"multi-agent AI가 분화된 에이전트와 비평으로 검증 가능한 과학 가설을 만든다"는 **상위 프레이밍은 이 논문이 이미 선점**했다. 우리는 그 패러다임을 **발명한 것이 아니라 적용**한다. 리뷰어가 "AI co-scientist와 무엇이 다른가?"를 반드시 물을 것이므로, 우리 포지셔닝은 **paradigm-inventing이 아니라 applied / governed / domain-specific**으로 못 박아야 한다.

## 정확히 겹치는 부분 (Exact overlap — 굵게)
- **분화된 전문 에이전트 구성** — 그들의 Generation/Reflection/Ranking/Evolution/Meta-review/Proximity ↔ 우리 Data/Embedding/Modeling/TE + Scientific Critic. **구조 동형.**
- **명시적 critic 에이전트** — 그들의 **Reflection 에이전트(가설 리뷰/비평)** ↔ 우리 **Scientific Critic**. *비평을 별도 에이전트로 분리*한다는 발상이 동일.
- **가설을 산출물로** — 둘 다 **hypothesis-as-output**, 모델 점수가 아니라 검증 가능한 연구가설을 낸다.
- **자동 평가/랭킹** — 그들의 **Elo 토너먼트**로 가설을 순위화 ↔ 우리 ranked therapeutic hypothesis. 자동 우선순위화 동일.
- **wet-lab 검증된 생의학 적용** — drug repurposing·target discovery까지 닿는 적용 범위가 우리 npj Precision Oncology 타깃과 겹침.

## 우리의 정직한 delta (Defensible delta — 좁지만 진짜)
overlap이 큰 만큼 delta는 **방법이 아니라 거버넌스/도메인 한정**에 둔다:
- **Anti-DRP 프레이밍 락** — drug feature(SMILES/fingerprint) 입력 **금지**, "drug response prediction"·"personalized therapy" 표현 금지. co-scientist에는 이런 도메인 안전장치가 없다.
- **`hypothesis_only` claim-level 강제** — 모든 산출물에 claim_level 필드, 과대주장 차단. 그들의 자유로운 가설 생성과 대비되는 **제약된(constrained) 생성**.
- **owner≠reviewer anti-self-reference** — 우리 cross-review 규칙(작성자≠Critic). co-scientist의 Reflection은 같은 시스템 내부라 self-preference 편향 위험(cf. panickssery-2024)이 구조적으로 존재; 우리는 이를 **규칙으로 차단**.
- **단일 구체 파이프라인 결속** — 추상적 discovery가 아니라 **H&E WSI → molecular phenotype → DepMap/GDSC** 한 경로에 고정. 일반성은 잃지만 재현성·평가 가능성을 얻음.

## 인용·주의
- **preprint (peer-review 전, DOI 미확정)** — "검증된 발견 도구"가 아니라 **proof-of-concept**로 인용. 우리가 더 엄격한(governed) 변형이라는 논거 가능.
- 인용형식: Gottweis J, Weng W-H, Daryin A, et al. *Towards an AI co-scientist.* arXiv:2502.18864. 2025.
- 관련: lu-2024-aiscientist(자율 ML 논문작성), zheng-2023-llmjudge(LLM-judge), panickssery-2024-selfpreference(self-preference 편향).

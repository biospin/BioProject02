# gottweis-2025-coscientist — Core Summary

**"Towards an AI co-scientist"** · Gottweis J, Weng W-H, Daryin A, Tu T, et al. (Google / Google DeepMind, ~34인) · 2025 · arXiv:2502.18864 (preprint, non-peer-reviewed; DOI 미확정) · 공개 코드 없음(trusted-tester 프로그램만).

## 한 줄 요지 (One-line)
Gemini 2.0 위에 **여러 전문 에이전트 + 명시적 비평(critic) + 토너먼트 랭킹**을 올려, 자연어 연구목표로부터 **검증 가능한 새 연구가설**을 만들고, 그 일부를 **습식 실험(wet-lab)으로 실제 검증**한 multi-agent 프레임워크.

## 시스템 구조 (Architecture)
- **비동기 task-execution 프레임워크** + **test-time compute scaling**: 계산을 더 쓸수록 가설 품질이 계속 향상.
- **전문 에이전트 (specialized agents):**
  - **Generation** — 문헌 grounding·simulated debate로 가설 제안
  - **Reflection** — 가설 리뷰/비평 (full, deep-verification, observation, tournament review). *우리 Scientific Critic의 직접 대응물.*
  - **Ranking** — 쌍대(pairwise) 과학적 토론으로 **Elo 토너먼트** 등급화
  - **Evolution** — 상위 가설을 단순화·확장·결합해 개선
  - **Proximity** — 가설 유사도 그래프/중복 제거
  - **Meta-review** — 토너먼트 피드백을 research overview로 종합
- **핵심 방법론:** *generate–debate–evolve* (과학적 방법 모사).
- **자동 평가:** **Elo 등급**이 자기개선 루프를 구동하며, Elo가 산출물 품질과 상관.
- **도구 접근:** web search + 특화 AI 모델 + 데이터베이스 호출.
- **scientist-in-the-loop:** 연구자가 목표 제시, 자기 가설/리뷰 추가, 방향 재설정 가능.

## 검증 (Validation) — 핵심 차별점
세 개 생의학 도메인에서 **실제 실험 검증**:
1. **Drug repurposing** — AML 후보, in vitro 임상 적용 농도에서 종양 억제.
2. **Novel target discovery** — 간섬유화 epigenetic 표적, 인간 hepatic organoid에서 항섬유화 활성.
3. **AMR** — **미발표** 박테리아 유전자 전달 기전을 독립적으로 재현.

## BIOP02 관점 (Why it matters here)
이 논문은 "multi-agent + critic 가설 생성"의 **패러다임 정의 논문(paradigm-setter)**이다. 우리는 이를 **발명할 수 없고**, 단지 **적용·도메인 한정·거버넌스 부가**할 수 있다. 자세한 overlap/delta는 `_lens-academic.md`, 우리가 주장하지 않는 것은 `_methodology-brief.md` 참조.

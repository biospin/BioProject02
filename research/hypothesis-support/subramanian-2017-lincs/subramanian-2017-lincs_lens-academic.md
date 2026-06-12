# Lens — Academic / Scientific

## Contribution claim
L1000은 transcriptomics를 **압축 측정 + 추론** 문제로 재정의했다. "유전자 발현은
저차원 구조를 가진다 → landmark만 측정해도 전체를 복원할 수 있다"는 가정을
130만 profile 규모로 실증했다. 학술적으로는 (1) reduced-representation 측정의
정당화, (2) tau 기반 cross-context connectivity 정규화, (3) perturbation biology를
hypothesis-generation 인프라로 만든 점이 핵심 기여다.

## Strengths
- **Scale + openness**: GSE92742 / GSE70138 Level 1–5 데이터, clue.io API, Docker
  컨테이너까지 공개 → 재현성·재사용성이 매우 높음.
- **Tau normalization**: connectivity를 database-wide percentile로 변환해 서로 다른
  cell line·plate 간 비교 가능. 이것이 외부 signature query를 가능하게 한다.
- **Mechanism-agnostic**: 약물 구조나 표적 정보 없이 발현 결과만으로 MoA 가설을 세움
  — 우리의 "drug structure 입력 금지" 제약과 철학적으로 일치.

## Limitations (우리가 critic 관점에서 반드시 명시)
- **Inference error**: 19% inferred 유전자는 R_gene < 0.95. 추론된 유전자에 크게
  의존하는 signature는 약화될 수 있음 → query는 가급적 landmark-weighted로.
- **Cell-line context**: 참조 signature는 cell line(주로 9개 core) 기반. **BRCA tumor
  morphology와 cell line context 간 도메인 차**가 reversal 해석을 제한 → claim_level
  hypothesis_only 유지의 근거.
- **Batch / dose / time**: connectivity는 dose·time에 민감. 단일 hit를 과해석 금지.
- **Reversal ≠ efficacy**: signature reversal은 *기전적 가설*이지 치료 효능 증거가
  아님. DRP framing 금지 규칙과 직결.

## Citing in our paper
배경(Methods/Intro)에서 route 2의 근거 문헌으로 인용. Lamb-2006(원조 CMap) →
Subramanian-2017(L1000 scale-up)로 계보를 제시하고, route 1(PRISM, Corsello-2020)과의
**독립성**을 강조하는 문장에서 anchor로 사용.

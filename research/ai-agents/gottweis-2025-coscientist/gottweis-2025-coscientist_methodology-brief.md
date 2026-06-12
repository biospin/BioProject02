# gottweis-2025-coscientist — Methodology Brief (what we do NOT claim + Exp5)

## 우리가 **주장하지 않는 것** (Explicit non-claims)
이 논문이 선점했으므로, BIOP02 논문/문서에서 아래는 **절대 주장하지 않는다**:
- ❌ multi-agent 가설 생성을 **발명/창안**했다.
- ❌ *generate–debate–evolve* 또는 토너먼트 **Elo 자기평가**를 도입했다.
- ❌ "agentic scientific discovery" **패러다임**을 제시했다.
- ❌ critic을 별도 에이전트로 분리한다는 **아이디어 자체**가 새롭다.
- ❌ wet-lab까지 닿는 **범용 발견 엔진**이다.

→ 이 모두 Gottweis 2025의 선행이다. 우리 논문은 서론에서 **명시적으로 이를 prior art로 인용**하고, "우리는 패러다임이 아니라 **도메인 한정 거버넌스**를 기여한다"고 선언해야 리뷰어 scoop 공격을 무력화한다.

## 우리가 **유일하게 publishable**하게 주장할 수 있는 method angle = Critic-gate
co-scientist의 Reflection/Elo는 **시스템 내부 자기평가**라 self-preference 편향(panickssery-2024)·LLM-judge 신뢰성(zheng-2023) 문제가 구조적으로 잔존한다. 우리의 **참신한 method 주장은 단 하나**:

> **owner≠reviewer를 강제하는 도메인 Critic-gate** — 작성 에이전트와 비평 에이전트를 분리하고, `hypothesis_only` claim-level과 anti-DRP 규칙을 *통과 조건*으로 박아, 가설이 게이트를 통과해야만 공유·등록되게 한다.

이는 "더 똑똑한 생성"이 아니라 **"검증 가능하게 제약된 생성"**이라는, co-scientist와 직교하는 기여다.

## Exp5 — Critic-gate ablation (제안 실험)
**가설:** owner≠reviewer + claim-level gate가 *과대주장/누수/DRP-프레이밍 위반*을 측정 가능하게 줄인다.

**Arms (동일 H&E→phenotype→DepMap/GDSC 가설 세트):**
1. **No-critic** — 생성 가설을 그대로 통과.
2. **Self-critic** — 작성 에이전트가 자기 비평 (co-scientist Reflection 모사, owner=reviewer).
3. **Cross Critic-gate (ours)** — owner≠reviewer + `hypothesis_only` + anti-DRP 규칙 게이트.

**측정 지표:**
- DRP-금지 표현 위반율 (CLAUDE.md 금칙어 자동 스캔).
- claim-level 과대주장률 (hypothesis_only 이탈 빈도).
- biological-plausibility / pathway-drug 링크 타당성 (7-point checklist 항목 5).
- self-preference 편향: arm 2가 자기 가설을 통과시키는 비율 vs arm 3.

**예상 결과:** arm 3가 위반율·과대주장률 최저, self-preference 0 (구조적으로 차단). 이로써 **"governance가 측정 가능한 효과를 낸다"**는 *유일하게 새로운* 정량 주장 확보.

**Critic 연계(7-point):** 항목 6(DRP framing 금지)·7(claim-level)이 본 실험의 직접 출력. 항목 1(leakage)·5(plausibility)는 게이트 통과 조건. 단, **Critic은 자기 임계치를 설정하지 않는다**(anti-self-reference) — 임계는 사전 고정.

# Methodology Brief — Signature-Reversal Scoring & Exp4 Convergence

## 1. Signature-reversal scoring (이 논문의 방법)
주어진 query signature S = (S_up, S_down)에 대해, 각 reference perturbagen
profile r에 대해 **weighted Kolmogorov–Smirnov enrichment statistic**으로
S_up·S_down이 r의 순위 리스트에서 어디에 enrich되는지를 측정한다.

- raw connectivity score(WTCS-유사): S_up이 r의 **아래쪽(억제)**, S_down이 r의
  **위쪽(유도)** 에 몰리면 → 강한 **음의** score → r이 S를 **역전(reverse)** 한다.
- 정규화: **Tau (τ)** = 관측 enrichment를 database 전체 분포에 대한 percentile로 환산.
  τ ∈ [-100, 100]; τ ≤ -90 이면 "이 perturbagen은 거의 모든 비교 대상보다 강하게
  이 signature를 역전한다"로 해석.
- 신뢰도: nominal p-value + FDR로 보강.

핵심 직관: **질병/표현형 signature를 거꾸로 뒤집는 약물 = 후보**. 약물 구조·표적
정보가 전혀 필요 없다(우리 제약과 합치).

## 2. BIOP02 route 2 적용
1. 모델이 BRCA molecular phenotype(ER/PR/HER2/PAM50)을 예측.
2. 그 phenotype과 연관된 **expression signature**(up/down DEG)를 도출
   (TCGA/CPTAC 발현으로부터, 또는 phenotype-conditioned DEG).
3. 이 signature를 clue.io에 query → perturbagen별 τ.
4. τ가 강한 음(reversal) 약물을 **route-2 후보 랭킹**으로 채택.

route 1과 달리 **viability label을 전혀 쓰지 않으므로** 두 route는 독립.

## 3. Exp4 — Route Convergence (novelty)
```
route1: phenotype → PRISM/GDSC viability transfer → drug rank R1
route2: phenotype → L1000 reversal (this paper)   → drug rank R2
convergence = rank-overlap / RBO(R1, R2) at top-k
```
- **Convergence 가설**: 두 독립 readout(viability vs expression-reversal)에서 모두
  상위인 약물은 단일 route hit보다 가설로서 훨씬 신뢰도 높음.
- **비-순환성**: route 2는 발현 역전, route 1은 생존 억제 — 공유 label 없음.
  같은 Broad 생태계지만 readout이 달라 convergence가 진짜 신호.
- **Critic 체크 연계**:
  - #4 cross-dataset: PRISM vs GDSC 일관성에 더해 vs L1000까지 3-way 가능.
  - #5 biological plausibility: reversal된 pathway가 phenotype과 정합하는지.
  - #6 DRP framing 금지: "signature reversal hypothesis"로만 기술, "drug response
    prediction" 표현 금지.
  - #7 claim-level: 출력 `hypothesis_only` 고정.

## 4. 주의 (over-claim 방지)
- inferred 유전자(19% R<0.95) 의존 signature 약화 가능 → landmark 우선.
- cell-line context ≠ tumor morphology → reversal은 *기전 가설*, 효능 주장 아님.
- dose/time/build 버전 민감 → 결과에 build id·query set 고정 기록.

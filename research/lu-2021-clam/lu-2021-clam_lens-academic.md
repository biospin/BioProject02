# CLAM — Academic Lens (baseline role & honest framing)

## Positioning: CLAM은 우리 novelty가 아니라 building block
BIOP02의 modeling 축은 **MLP baseline → attention MIL**이다. 이 progression에서:
- **ABMIL (Ilse 2018)** = primary *minimal* attention-MIL baseline (gated-attention pooling 그 자체).
- **CLAM (Lu 2021)** = *pathology-grade* standard comparator. ABMIL에 instance-level clustering
  constraint와 multi-branch multi-class head를 더한 확장판.

두 모델 모두 **검증된 기성 aggregator**다. 우리가 논문에서 주장할 contribution은 "더 나은
attention-MIL 구조"가 아니라 **FM tile embedding → slide-level BRCA phenotype (ER/PR/HER2/PAM50)
예측 + therapeutic-evidence transfer + Critic-validated hypothesis**다. 따라서 CLAM은 *공정한
비교를 위한 강한 baseline*으로만 쓴다. "우리가 MIL을 발명했다" 식 framing은 명백한 anti-pattern.

## Why CLAM is the right comparator (not just ABMIL)
1. **Multi-class subtyping**: PAM50은 5-class 문제다. CLAM-MB의 class별 attention branch는
   multi-class WSI 분류의 정석 reference로, PAM50 baseline 비교에 직접 들어맞는다.
2. **Data efficiency**: TCGA-BRCA Paper A scope가 ~150 slide subset으로 작다. CLAM의 핵심
   selling point가 "data-efficient, slide-label-only"라서, small-N 환경의 현실적 상한선 baseline.
3. **Generalization**: CLAM은 independent cohort·cell-phone·biopsy 일반화를 보였다. 우리
   cross-dataset 계획 (TCGA train → CPTAC test, Sprint 3)과 같은 평가 철학.

## Honest framing checklist (Critic 7-point 대비)
- **Baseline comparison (#2)**: random / subtype-only / pixel-mean 외에 CLAM-SB·CLAM-MB와
  ABMIL을 *동일 FM embedding* 위에서 비교해야 aggregator의 marginal 효과를 분리할 수 있다.
- **DRP framing (#6)**: CLAM은 subtyping/metastasis 모델일 뿐 drug-response 모델이 아니다.
  인용 시 "drug response prediction" 어휘를 CLAM에 갖다 붙이지 말 것.
- **Claim-level (#7)**: CLAM 비교 결과도 `hypothesis_only` 수준 유지 — "임상 사용 가능" 주장 금지.
- **No self-reference**: CLAM의 threshold/clustering 설정을 그대로 우리 Critic 기준으로 쓰지 말 것.

## Net academic verdict
CLAM은 **인용·재현·비교가 필수인 표준 baseline**이지만, 그 자체로 우리 기여를 깎지 않는다.
정직한 서술은 "ABMIL/CLAM은 검증된 aggregator이고, 우리는 그 위에서 BRCA phenotype→therapeutic
hypothesis 파이프라인을 구축한다"이다. MIL 구조 개선을 novelty로 포장하는 순간 reviewer에게
정확히 이 논문으로 반격당한다.

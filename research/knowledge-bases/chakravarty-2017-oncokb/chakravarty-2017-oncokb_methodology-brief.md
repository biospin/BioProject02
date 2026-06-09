# chakravarty-2017-oncokb — Methodology Brief (Exp4 / Exp5 적용)

OncoKB를 BIOP02 파이프라인의 **actionability 오라클**로 삽입하는 방법. 핵심 원칙: OncoKB Tx 레벨(1–4, R1/R2)은 **게이트된 ceiling**, 오픈 KB는 재현 가능한 **floor** — 둘의 차이를 정량화하고 라벨링한다.
Insert OncoKB as the actionability oracle; treat its FDA-recognized Tx levels as a gated ceiling and open KBs as a reproducible floor, then quantify the gap.

## Exp4 — Multi-source convergence (수렴)
- **목적:** H&E→phenotype 후 도출된 BRCA 변이→약물 가설 edge가 **여러 독립 KB에서 동시에 지지**되는지 측정.
- **소스:** OncoKB(Tx level, 게이트) · CIViC(evidence level A–E, CC0) · Open Targets(association score) · DGIdb(interaction).
- **수렴 지표:** edge별 **convergence count / 가중 합의 점수**. OncoKB Level 1–2가 있으면 high-confidence anchor; 오픈 KB만 지지하면 mid; 단일 소스면 weak.
- **레벨 정렬(level alignment):** OncoKB Level 1≈FDA, 3A≈well-powered trial, 4≈biological → CIViC A–E와 ordinal 매핑 테이블을 만들어 cross-KB 비교를 동일 척도로.

## Exp5 — Critic-gate precision label (정밀도 라벨)
- **목적:** Critic #5(pathway–drug link plausibility) 게이트가 거른/통과시킨 가설의 정밀도를 OncoKB 레벨을 ground-truth로 평가.
- **라벨 규칙(ordinal):**
  - `actionable_L1_2` — OncoKB Level 1/2 매칭(표준치료 actionable).
  - `investigational_L3_4` — Level 3A/3B/4.
  - `resistance_R` — R1/R2 (방향성 주의: 민감↔내성 혼동 방지).
  - `open_only` — 오픈 KB만 지지, OncoKB 무근거 → **잔여 gap** 후보.
  - `unsupported` — 어떤 KB도 미지지 → Critic가 차단해야 할 false hypothesis.
- **게이트 정밀도:** Critic가 pass시킨 edge 중 `actionable_L1_2`+`investigational_L3_4` 비율 = precision; `unsupported`를 pass시키면 false-positive penalty.

## Open-route gap (정직성 핵심)
- **floor(오픈):** CIViC+OpenTargets+DGIdb로 도달 가능 — 누구나 재현.
- **ceiling(OncoKB):** FDA-recognized, tumor-type-specific Tx level — 게이트(토큰/라이선스), 벌크 다운로드 불가.
- **residual gap = ceiling − floor:** 오픈 KB에 없거나 레벨이 불명확한 edge 집합. Exp5에서 `open_only`/`unsupported`로 명시 카운트하고, "오픈 라우트가 OncoKB 레벨의 X%만 커버, 나머지는 게이트된 잔여"로 보고. **오픈 floor를 ceiling으로 포장 금지.**

## 주의 (Anti-patterns 회피)
- OncoKB 레벨을 우리 모델 입력 feature로 쓰지 않음(actionability는 사후 grounding, 학습 신호 아님 — anti-leakage).
- 종양형 특이성 준수: BRCA 외 적응증 레벨(3B 등)을 BRCA에 무비판 전이 금지(Critic #4 cross-dataset 정신).
- 내성(R) 레벨을 민감도로 오독 금지.

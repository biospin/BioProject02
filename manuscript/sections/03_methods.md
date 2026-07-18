# Methods (집필 골격 — 지금 바로 쓸 수 있음)

> 타일링부터 검정까지 전부 코드·결과 파일이 있어 월요일에 병행 집필 가능. 파라미터는 실제 config/코드에서만 인용(파일:줄 명시), 지어내지 않는다.

## M1. 코호트와 라벨
- 유방(anchor) TCGA-BRCA ~1010 DX-slide. 5암종: 유방·폐·대장·위·두경부. 각 `n_slides`는 결과 JSON에 실측(대장 523, 폐 1026, 위 439, 두경부 468).
- 라벨 출처·split은 [../../agents/data/](../../agents/data/), 사전등록 경계는 [../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md](../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md).

## M2. 타일링 · 임베딩
- 256×256 @ 20×, Otsu mask, per-patient cap 5000 — [../../agents/embedding/configs/tile_config.yaml](../../agents/embedding/configs/tile_config.yaml).
- 헤드라인 임베딩 = **UNI v1 (1024-d)**. 견고성용 다중 FM(Virchow2 2560-d, UNI2-h 1536-d)은 Supplement.

## M3. 모델 · 학습
- CLAM-SB attention MIL. feature_dim=임베딩차원, hidden 512, att 256, epochs 40–50, seed 42(결정론). 코드 [../../experiments/crosscancer/run_mil_cost.py](../../experiments/crosscancer/run_mil_cost.py).

## M4. 평가 설계
- **site-disjoint holdout(val+test pooled)** — leakage 차단. 각 결과 JSON `eval` 필드에 명시.
- 대조군 3종: shuffle-null, prevalence baseline(0.5), (해당 시) subtype-only/pixel-mean.
- 신뢰구간: bootstrap 95% CI(결과 JSON `ci95`).

## M5. cost-of-substitution 프레임
- confusion matrix × therapeutic distance → 라우팅 오분류 비용. 정의·계산 [../../experiments/kkkim/20260710_cost_of_substitution/](../../experiments/kkkim/20260710_cost_of_substitution/).

## M6. 사전등록 · claim 규율
- 법칙 임계는 봉인 문서에서만 인용(발표자료 숫자 금지). 모든 산출 `hypothesis_only`, 후향적, 전향 검증 필요.

## M7. Yale 앵커 방법 — <FILL: A3/A4 확정 후>
## M8. 다중 FM 견고성 방법 — <FILL: 재학습 확정 후>

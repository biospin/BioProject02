# Fernandez-Romero et al., 2026 (MBEC domain generalisation) — methodology-brief

> 근거: `sources/` 전문. 2026-09-02 전문 기반 재작성. 분할, 지표, 통계 절차를 우리 원고에서 인용·대조할 수 있는 수준까지 옮긴다.

## A. 실험 파이프라인 4단계

원문 Figure S1이 정리하는 순서는 다음과 같다.

1. 패치 추출
2. TCGA에서 baseline CLAM으로 Monte Carlo 교차검증
3. CPTAC에서 baseline MIL로 외부검증
4. 최고 FM과 최적화 MIL 3종의 결과를 받아 도메인 시프트 분석

즉 FM 선별과 도메인 시프트 분석의 모형 구성이 다르다. 선별은 baseline CLAM 하나로, 시프트 분석은 Optuna로 튜닝한 CLAM·TransMIL·DSMIL 셋으로 한다. Table 1과 Table 2의 숫자가 같은 모형에서 나온 것이 아니라는 점이 인용할 때 중요하다.

## B. 분할 설계 (원문 확정)

### 내부 검증

> "We performed patient-stratified MCCV with 10 random splits on TCGA as internal validation. In each iteration, patients were randomly partitioned into 80% training, 10% validation (for early stopping) and 10% test. Patient-level stratification ensured that all slides from the same patient remained in the same fold, preventing data leakage."

- 반복: Monte Carlo 교차검증 10회, 매회 무작위 재분할.
- 비율: 학습 80% / 검증 10% / 시험 10%, 환자 단위.
- 통제: 환자 하나. 같은 환자의 슬라이드가 fold를 넘지 않게 한다.
- **미통제**: 제출 기관, 스캐너, 배치. 전문에 `tissue source site` 0회, `submitter` 0회, `batch` 0회, `scanner` 0회. `site`는 논의 문단의 "cross-site generalisation" 한 번뿐이다.
- 클래스 불균형은 분할이 아니라 손실 가중(빈도 역수 cross-entropy)으로 다룬다.

### MIL 비교 단계

- 10-fold 교차검증(MCCV 아님)으로 TCGA에서 학습하고 CPTAC을 독립 hold-out으로 평가한다.
- 하이퍼파라미터는 아키텍처마다 따로 최적화한다. PathBench-MIL + Optuna, 50 trial, pruning, validation(학습셋의 10%)에서 mean average precision 최대화. 탐색 변수는 z_dim(32~512)과 bag size(8~256).
- 타일은 256×256 px / 128 µm @ 20×로 고정. 염색 정규화는 이 단계에서 적용하지 않는다.

### 외부 검증

> "each FM-CLAM model was trained on the entire TCGA cohort (85% training, 15% validation) and tested on CPTAC"

- 내부 검증과 하이퍼파라미터를 같게 두고, 학습 데이터만 전체 TCGA로 바꿔 다시 학습한다. 조기 종료는 validation loss, 최고 체크포인트로 CPTAC 평가.
- 외부 코호트는 CPTAC 하나뿐이고 반복이 없다. Table 1의 HO 열에 표준편차가 없는 이유가 이것이다.

## C. 지표

| 과제 | 지표 | 비고 |
|---|---|---|
| PAM50 5-class | macro F1-score | scikit-learn |
| ER / PR / HER2 | PR-AUC | 클래스 불균형 인식 지표로 선택 |
| 열화 | RPD | 아래 정의 |

- AUROC는 논문 어디에도 없다. 우리 registry가 AUROC이므로 숫자를 직접 겹칠 수 없다.

```
RPD(Q, c) = (Q_c^CV − Q_c^HO) / Q_c^CV     (Q_c^CV > 0)
          = n.d.                            (그 외)
```

- Q는 클래스 c의 지표(PAM50이면 F1, IHC면 PR-AUC), CV는 내부 10-fold 평균, HO는 외부.
- 원문 예시: 내부 0.60, 외부 0.42면 RPD = 0.30, 곧 30% 상대 낙폭.
- 회귀에 들어가는 RPD는 최적화 MIL 3종의 평균값이다.

## D. 네 요인의 조작적 정의

### 1. 염색 변이 이득 Δn

- Macenko 정규화를 패치 단위로, 특징 추출 직전에 적용한다. SlideFlow population-level preset v3, stain matrix는 3×2(H·E 벡터 × RGB), 기준 최대 농도 [1.766, 1.280], TCGA 450 슬라이드 약 50,000 패치의 Macenko 분해 평균에서 추정.
- 정규화 TCGA로 학습, 정규화 CPTAC으로 평가.
- `n_c = Perf_c(normalised) − Perf_c(original)`, 외부 성능 기준, 3개 MIL 평균.

### 2. 유병률 시프트 Δp

- `Δp_c = p_c(CPTAC) − p_c(TCGA)`. 단순 비율 차이.

### 3. 특징공간 발산 d

- 각 WSI에서 attention 상위 K=8 패치를 고른다. CLAM은 정답 클래스에 해당하는 attention 열, DSMIL·TransMIL은 단일 attention 벡터를 쓴다.
- 정답 라벨과 코호트로 묶어 클래스 중심점(임베딩 산술 평균)을 구한다.
- `d_c = 1 − cos(μ_c^TCGA, μ_c^CPTAC)`. 3개 MIL에서 따로 구해 평균.

### 4. 형태 분리도 B̃

- baseline CLAM이 고른 패치 중 클래스 중심점에 가장 가까운 25장을 뽑는다. PAM50 125장(5×25), IHC 150장(3 마커 × 2 상태 × 25장)씩 코호트마다.
- 병리 두 명이 라벨과 예측에 눈가림된 채 독립 주석. 특징 여섯 가지: 튜불 형성(1~3), 핵 다형성(1~3), 유사분열 수(개수), 종양 괴사(유무), 림프구 침윤(유무), 다형핵구 침윤(유무). 합의 절차 없이 두 사람 점수의 산술 평균을 최종값으로 쓴다.
- 일치도는 순서형에 선형 가중 κw, 이분형에 Cohen's κ. 결과는 κw 0.152~0.289, κ 0.177~0.321(Landis-Koch 기준 slight~fair).
- 코호트 간 특징 분포를 Mann-Whitney U로 비교하고 효과크기는 rank-biserial r_rb. 클래스 쌍마다 BH 보정(α=0.05).
- `B(c,c') = Σ_{i=1..6} |r_rb,i^(c,c')|`, 유의한 특징만(BH q<0.05) 더한다. 대각 B(c,c)는 코호트 사이 같은 클래스의 형태 이질성, 비대각은 클래스를 가로지른 유사도.
- `B̃_c = min_{d≠c} B(c,d) − B(c,c)`. 양수면 자기 자신과의 코호트 간 일관성이 다른 클래스와의 유사도보다 크다는 뜻이고, 음수면 외부 코호트의 그 클래스가 자기보다 다른 클래스와 더 닮았다는 뜻이다.

## E. 통계 절차

- 관측 단위는 클래스이고 n=11(PAM50 5 + ER 2 + PR 2 + HER2 2).
- **과제 통합의 근거 세 가지**(저자 제시): RPD가 무차원 비율이라 지표 척도와 무관하게 비교 가능하다는 것, 요인이 클래스 수준에서 정의되어 생물학적 과제와 독립적으로 작동한다고 가정한 것, 관측치를 5개에서 11개로 늘려 검정력을 얻는다는 것. 세 번째는 저자 스스로 실용적 이유로 적는다.
- 다중비교 보정은 BH를 네 묶음(단변량 Spearman, 단변량 OLS 기울기, 다변량, 공선성) 안에서 각각 따로 적용하고 보정된 값을 q로 표기한다. 단변량에서 q<0.05인 요인만 다변량 후보가 된다.
- 단변량은 단순 OLS로 Pearson r, R², 기울기 β와 q를 보고하고, n=11의 비정규 가능성 때문에 Spearman ρ도 함께 낸다.
- 다변량은 유의 요인의 가장 간결한 조합으로 OLS를 적합한다. 공선성은 Pearson r, Spearman ρ, VIF(=1/(1−R²), 이변량 회귀에서)로 본다.
- 일반형: `RPD_c = β0 + β1·Δn_c + β2·Δp_c + β3·d_c + β4·B̃_c + ε`. 실제로는 단변량 유의 요인만 후보로 넣는다.

## F. 결과 요약 (수치는 `_core.md` 표 참조)

- 단변량 유의: d(R²=0.577, q(β)=0.027), Δn(R²=0.479, q(β)=0.037), B̃(R²=0.424, q(β)=0.040). 비유의: Δp(R²=0.029, q=0.615).
- 최종 다변량 `RPD ~ Δn + d`: R²=0.800, adj R²=0.750, F=16.03, q=0.005. 고유 기여는 d가 ΔR²=0.322, Δn이 0.224.
- B̃는 두 항이 들어오면 ΔR²<0.001, q=0.881로 기여가 사라진다. Δn과 B̃의 Spearman ρ=−0.691(q=0.056)이 그 이유로 제시된다.

## G. 우리 원고에서 쓸 방식

### 즉시 반영

1. **참고문헌 추가**: Fernandez-Romero J, Ramos-Berciano P, Perez-Perez M, Benavides D, Robles-Frias A, Garcia-Gutierrez J, Macias-Garcia L. Domain generalisation challenges in breast cancer molecular classification using foundation models: a cross-cohort exploratory study. *Med Biol Eng Comput* 64(6):2321–2331 (2026). doi:10.1007/s11517-026-03590-4.
2. **Related work 한 줄 양보**: H&E FM+MIL로 PAM50과 ER/PR/HER2를 예측하는 실험과 TCGA→CPTAC 외부 열화는 이미 보고되었다는 사실을 먼저 인정하고, 그 다음 문장에서 결정 층위로 넘어간다.
3. **분할 설명 각주**: 두 연구의 내부 수치가 서로 다른 성격이라는 점을 밝힌다. 그들은 환자 층화 랜덤 MCCV, 우리는 기관 분리를 강제한 사전 고정 분할. 지표도 macro-F1·PR-AUC 대 AUROC로 다르다.
4. **HER2 수렴 문장**: 그들 HER2-enriched RPD=1.000과 우리 HER2 외부 AUROC 0.530을 나란히 두되, 지표가 달라 수치 비교가 아니라 결론 방향의 일치임을 명시한다.

### 하지 말 것

- 예측 정확도 표로 정면 대결하지 않는다. figure로 방어하지 않는다. 인용은 본문 한두 줄까지.
- 그들의 PR-AUC·macro-F1을 우리 AUROC와 같은 축에 올리지 않는다.
- 그들이 기관을 통제하지 않았다는 사실에서 "그래서 그들 내부 수치가 부풀려졌다"로 곧장 결론 내지 않는다. 사실과 추론을 문장에서 갈라 놓는다.
- 예측 충실도(표1)와 라우팅 비용(표2)을 하나의 비용 숫자로 합치지 않는다. 층위 융합은 그들 지표를 치료 가치로 승격하는 오류다.

### 열린 항목

- `원문 미확인:` 아키텍처별 클래스별 원값(Table S4)이 없으므로, 그들 클래스별 내부·외부 절대 성능을 인용하려면 Supplementary PDF를 따로 받아야 한다. 지금 인용 가능한 클래스 단위 값은 Table 2의 RPD와 네 요인뿐이다.
- 우리 쪽 macro-F1·PR-AUC 재계산 여부는 미결정. 재계산하면 그들 표와 같은 자에 올릴 수 있으나, 헤드라인을 예측 정확도로 되돌릴 위험이 있어 보조 표로만 검토한다.

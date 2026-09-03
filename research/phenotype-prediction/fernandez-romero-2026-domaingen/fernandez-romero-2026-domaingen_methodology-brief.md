# Fernandez-Romero et al., 2026 (MBEC domain generalisation) — methodology-brief

> 근거: `sources/` 전문. 2026-09-02 전문 기반 재작성. 분할, 지표, 통계 절차를 우리 원고에서 인용·대조할 수 있는 수준까지 옮긴다.
>
> **2026-09-02 보강**: Supplementary PDF(10p)를 확보해 학습 하이퍼파라미터(Table S2), Optuna 최적 구성(Table S3), 염색 정규화 원값(Table S5)을 채웠다. 클래스별 원값 표는 `_core.md`에 옮겨 두었다.

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

### baseline CLAM 학습 설정 (Table S2)

FM 13종 선별 단계에서 쓴 고정 설정이다. 조기 종료는 patience 20 epoch, min delta 0.001이다.

| Parameter | MCCV(내부) | HO(외부) |
|---|---|---|
| seed | 42 | 42 |
| dropout | 0.7 | 0.7 |
| learning rate | 0.0001 | 0.0001 |
| weight decay | 0.0001 | 0.0001 |
| bag loss | cross-entropy | cross-entropy |
| instance loss | cross-entropy | cross-entropy |
| patches per bag | 64 | 64 |
| model size | big | big |
| training fraction | 0.8 | 0.85 |
| validation fraction | 0.1 | 0.15 |
| test fraction | 0.1 | 0 |

- seed가 42 하나로 고정되어 있다. MCCV 10회의 무작위성은 분할 재추출에서 나오고 초기화에서는 나오지 않는다.
- HO 열의 test fraction이 0이라는 것은 TCGA를 전량 학습·검증에 쓰고 시험은 CPTAC에서만 한다는 뜻이다. 본문의 "85% training, 15% validation" 서술과 맞는다.
- patches per bag 64는 baseline 값이고, Optuna 단계에서는 bag size를 8~256에서 다시 찾는다.

### Optuna 최적 구성 (Table S3)

검증셋에서 mean average precision을 최대화해 고른 값이다. `z_dim`은 MIL 쪽 투영 차원이지 FM 출력 차원이 아니다.

| Task | Model | z_dim | dropout |
|---|---|---|---|
| ER | CLAM | 233 | 0.737 |
| ER | DSMIL | 57 | 0.747 |
| ER | TransMIL | 499 | 0.565 |
| HER2 | CLAM | 317 | 0.756 |
| HER2 | DSMIL | 121 | 0.514 |
| HER2 | TransMIL | 325 | 0.534 |
| PR | CLAM | 33 | 0.543 |
| PR | DSMIL | 329 | 0.475 |
| PR | TransMIL | 439 | 0.652 |
| PAM50 | CLAM | 255 | 0.549 |
| PAM50 | DSMIL | 311 | 0.631 |
| PAM50 | TransMIL | 472 | 0.597 |

- z_dim이 33에서 499까지 흩어져 있고 과제·모델 사이에 규칙이 보이지 않는다. PR-CLAM의 33과 ER-TransMIL의 499가 양 끝이다. 탐색 범위(32~512)의 경계에 붙은 값이 여럿이라, 50 trial이 수렴할 만큼 충분했는지는 원문만으로 판단할 수 없다.
- dropout은 0.475~0.756으로 baseline의 0.7보다 대체로 낮다.
- **표에 없는 것**: bag size의 최적값은 Table S3에 실리지 않는다. 본문이 탐색 변수로 명시했으나 결과는 공개되지 않아 `원문 미확인:`으로 남는다.

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
- **기준 슬라이드는 없다.** 흔히 쓰는 단일 참조 슬라이드 방식이 아니라 모집단 평균을 목표로 삼는 방식이다. 우리가 "그들이 어떤 슬라이드를 기준으로 삼았나"를 묻는다면 답은 "특정 슬라이드가 아니라 TCGA 450장의 평균"이다. 3×2 행렬의 성분값 자체는 공개되지 않아 `원문 미확인:`으로 남는다.
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
- 일치도는 순서형에 선형 가중 κw, 이분형에 Cohen's κ. 패치 275장을 이미지 식별자로 맞춰 계산했다. Table S9 실측값은 튜불 형성 κw=0.289(fair), 핵 다형성 κw=0.285(fair), 유사분열 κw=0.152(slight), 괴사 κ=0.177(slight), 림프구 침윤 κ=0.185(slight), 다형핵구 침윤 κ=0.321(fair)이다. 여섯 가지 모두 moderate(0.41)에 닿지 못한다.
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

- ~~아키텍처별 클래스별 원값(Table S4) 미확보~~ → **해소됨**. Supplementary를 확보해 `_core.md`에 33행 전부 옮겼다. 그들 클래스별 내부·외부 절대 성능을 이제 정확히 인용할 수 있다.
- 다만 인용 범위에 한 가지 제약이 남는다. **Table S4는 Virchow v2 하나 위에서만 계산되었다.** FM 13종을 클래스 단위로 가로지르는 표는 논문에 없으므로, "FM별 클래스별 성능"을 인용하려는 계획은 성립하지 않는다.
- `원문 미확인:`으로 남는 방법론 항목은 넷이다. FM 임베딩 차원, FM 가중치 버전 식별자, bag size 최적값, stain matrix 성분값.
- 우리 쪽 macro-F1·PR-AUC 재계산 여부는 미결정. 재계산하면 그들 표와 같은 자에 올릴 수 있으나, 헤드라인을 예측 정확도로 되돌릴 위험이 있어 보조 표로만 검토한다.

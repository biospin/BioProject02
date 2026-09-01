# Fernandez-Romero et al., 2026 — Domain generalisation in BC molecular classification — core 분석

> 근거 자료: `sources/fernandez-romero-2026-domaingen_pmc.xml`(Europe PMC JATS 전문, Table 1·2·3 원문 파싱) + `sources/fernandez-romero-2026-domaingen.pdf`(본문 11p). 2026-09-02 전문 기반 재작성.
>
> 본문과 Table 1~3에 숫자로 적힌 값만 단정한다. Supplementary(Table S1~S9, Figure S1~S3)는 별도 PDF(1.76 MB)로 이 폴더에 없으므로 그 소재 값은 `원문 미확인:`으로 표시한다. 우리가 원문 값에서 나눗셈으로 만든 값은 `계산값:`으로 구분한다.
>
> 표기: `해석:` / `계산값:` / `원문 미확인:` / `외부 맥락:`

## Executive Summary

- **무엇**: 새 예측기를 내놓는 논문이 아니라, H&E 기반 유방암 분자분류가 코호트를 넘으면 왜 무너지는지를 계량하는 진단 논문이다. 저자들 스스로 "to our knowledge, this is the first study to systematically characterise the sources of domain-induced performance degradation"이라고 위치를 잡는다.
- **설계 2단**: (1단) 13개 FM을 baseline CLAM 하나로 붙여 8개 평가(PAM50/ER/PR/HER2 × 내부/외부)로 순위를 매기고 최고 FM을 고른다. (2단) 고른 FM(Virchow v2)에 Optuna로 최적화한 CLAM, TransMIL, DSMIL을 붙여 열화가 aggregator 설계 탓인지 확인하고, 클래스별 RPD를 네 요인으로 회귀한다.
- **핵심 수치**: Virchow v2 mean rank 2.00으로 1위. 그 Virchow v2조차 baseline CLAM 기준 PAM50 macro-F1 0.542 → 0.358, HER2 PR-AUC 0.399 → 0.219로 떨어진다. 클래스 단위로는 HER2-enriched가 RPD=1.000, 곧 외부에서 완전 붕괴한다.
- **원인 분해**: `RPD ~ Δn + d`가 R²=0.800(adj 0.750, F=16.03, q=0.005). 특징공간 발산 d가 더 큰 고유 기여(ΔR²=0.322), 염색 변이 Δn이 0.224. 유병률 시프트 Δp는 유의하지 않다(q=0.615). 즉 공변량 시프트가 주범이고 사전 시프트는 아니라는 결론.
- **우리 관점 요지**: 예측 정확도 축에서는 정면 스쿱이지만, 분할 설계(기관 미통제)와 결정 층위(치료 라우팅 없음)에서 우리 여지가 남는다. 자세한 대조는 `_comparison-with-biop02.md`.

## Identity

| 항목 | 값 |
|---|---|
| Venue | Med Biol Eng Comput 64(6):2321–2331 (2026) |
| DOI | 10.1007/s11517-026-03590-4 |
| 라이선스 | CC-BY 4.0, PMC13269319 |
| 코드 | CLAM fork(`BIGS-investigacion/CLAiMem-ALL`) + PathBench-MIL fork(`BIGS-Investigacion/PathBench-MIL`) |
| 논문 성격 | exploratory benchmark / diagnostic (저자 자기규정) |

## 데이터

| 코호트 | 역할 | 슬라이드 | 환자 | 조직 처리 | 라벨 출처 |
|---|---|---|---|---|---|
| TCGA-BRCA | 내부(MCCV·CV) | 1,522 | 1,079 | **flash-frozen만**(FFPE 제외) | Thennavan et al. supplementary |
| CPTAC-BRCA | 외부(HO) | 387 | 120 | flash-frozen | Krug et al. |

- TCGA 라벨 가용 슬라이드: ER 1,455, PR 1,452, HER2 1,482. PAM50은 1,522 전체.
- CPTAC 라벨 가용 슬라이드: ER 379, PR 367, HER2 387.
- **중요 정정**: 이전 판본 분석은 TCGA를 FFPE로 적었으나 원문은 반대다. "To ensure consistency with CPTAC (which comprises flash-frozen samples), we excluded formalin-fixed paraffin-embedded specimens." 곧 양쪽 코호트 모두 냉동 조직이며, FFPE와 냉동의 차이는 이 논문의 시프트 축이 **아니다**. 저자들도 Limitations에서 FFPE 일반화가 안 된다는 점을 한계로 든다.

## 검증 설계 (Paper C 대조에 가장 중요한 절)

### 내부 검증

원문 그대로:

> "We performed patient-stratified MCCV with 10 random splits on TCGA as internal validation. In each iteration, patients were randomly partitioned into 80% training, 10% validation (for early stopping) and 10% test. Patient-level stratification ensured that all slides from the same patient remained in the same fold, preventing data leakage."

- 통제 단위는 **환자 하나뿐**이다. 슬라이드가 환자를 넘지 않게 막을 뿐, 제출 기관을 fold 사이에서 분리하지 않는다.
- 전문 문자열 확인: `tissue source site` 0회, `submitter` 0회, `batch` 0회, `scanner` 0회. `site`는 딱 1회 나오는데 그마저 "cross-site generalisation"이라는 논의 문장이지 분할 설명이 아니다. `institution`은 서론과 논의에서 남의 연구를 비판하는 맥락으로만 쓰인다.
- **해석**: 기관 서명(Howard 2021)이 내부 fold를 가로질러 남아 있을 수 있고, 그렇다면 내부 성능은 위로 편향된다. 저자들은 이 가능성을 다루지 않는다. 그들이 보고하는 "심각한 열화"의 분모가 부풀려졌을 여지가 여기서 생긴다. 다만 이는 우리 추론이지 저자들이 인정한 결함이 아니다.
- 2단계 MIL 비교에서는 MCCV 대신 10-fold CV를 쓰고 CPTAC을 hold-out으로 둔다.

### 외부 검증

- 각 FM-CLAM 모형을 TCGA 전체(train 85% / val 15%)로 다시 학습해 CPTAC에서 시험한다. 조기 종료는 validation loss 기준이고 최고 체크포인트를 쓴다.
- 외부 코호트는 CPTAC 하나뿐이다.

### 지표

- PAM50 = macro F1-score, ER/PR/HER2 = PR-AUC. **AUROC는 논문 전체에서 한 번도 쓰지 않는다**(`AUROC` 0회). 우리 registry의 AUROC와 직접 비교되지 않는 이유가 여기 있다.
- 학습 시 클래스 불균형은 빈도 역수 가중 cross-entropy로 처리한다.

### RPD 정의

```
RPD(Q,c) = (Q_c^CV − Q_c^HO) / Q_c^CV      (Q_c^CV > 0일 때)
         = n.d.                             (그 외)
```

RPD=0은 무열화, 1.0은 완전 붕괴, 음수는 외부에서 오히려 개선. 회귀에 쓰인 클래스별 RPD는 최적화 MIL 3종의 평균값이다.

## 결과 1: FM 13종 벤치 (Table 1, baseline CLAM)

PAM50은 macro-F1, ER/PR/HER2는 PR-AUC. MCCV=내부, HO=외부. 괄호 안은 우리가 계산한 상대 낙폭이다.

| Model | PAM50 MCCV | PAM50 HO | ER MCCV | ER HO | PR MCCV | PR HO | HER2 MCCV | HER2 HO | Mean Rank |
|---|---|---|---|---|---|---|---|---|---|
| ResNet-50 | 0.342 | 0.218 | 0.933 | 0.722 | 0.822 | 0.595 | 0.326 | 0.104 | 12.75 |
| CTransPath | 0.446 | 0.342 | 0.962 | 0.870 | 0.845 | 0.757 | 0.395 | 0.156 | 7.00 |
| RetCCL | 0.414 | 0.272 | 0.956 | 0.804 | 0.837 | 0.736 | 0.368 | 0.130 | 9.63 |
| CONCH | 0.493 | 0.335 | 0.957 | 0.885 | 0.853 | 0.777 | 0.306 | 0.190 | 7.13 |
| UNI | 0.527 | 0.365 | 0.967 | 0.885 | 0.870 | 0.833 | 0.396 | 0.148 | 4.38 |
| Prov-GigaPath | 0.504 | 0.379 | 0.967 | 0.900 | 0.875 | 0.822 | 0.368 | 0.160 | 4.13 |
| Hibou-B | 0.457 | 0.289 | 0.964 | 0.803 | 0.835 | 0.696 | 0.354 | 0.133 | 9.63 |
| Hibou-L | 0.399 | 0.297 | 0.952 | 0.858 | 0.826 | 0.697 | 0.246 | 0.107 | 11.38 |
| H-optimus-0 | 0.565 | 0.304 | 0.973 | 0.897 | 0.883 | 0.803 | 0.377 | 0.153 | 4.25 |
| **Virchow v2** | 0.542 | 0.358 | 0.972 | 0.916 | 0.874 | 0.862 | 0.399 | 0.219 | **2.00** |
| Phikon v2 | 0.508 | 0.345 | 0.971 | 0.906 | 0.861 | 0.802 | 0.359 | 0.191 | 4.63 |
| Musk | 0.450 | 0.305 | 0.955 | 0.774 | 0.832 | 0.700 | 0.364 | 0.126 | 9.88 |
| UNI-2 | 0.575 | 0.325 | 0.969 | 0.917 | 0.868 | 0.858 | 0.353 | 0.164 | 4.25 |

- 순위: Virchow v2 2.00 < Prov-GigaPath 4.13 < H-optimus-0 4.25 = UNI-2 4.25 < UNI 4.38 < Phikon v2 4.63. 구세대 CTransPath 7.00, RetCCL 9.63, ResNet-50 12.75.
- `계산값:` Virchow v2 상대 낙폭 PAM50 0.339, ER 0.058, PR 0.014, HER2 0.451. UNI는 PAM50 0.307, ER 0.085, PR 0.043, HER2 0.626. UNI-2는 PAM50 0.435, ER 0.054, PR 0.012, HER2 0.535. **우리가 쓰는 UNI 계열이 HER2에서 Virchow v2보다 더 크게 떨어진다**는 점은 기록해 둘 만하다.
- 표준편차는 MCCV에만 붙는다(예: Virchow v2 PAM50 ±0.041, HER2 ±0.115). 외부 HO는 단일 학습 단일 평가라 산포가 없다.
- `해석:` 어느 FM을 쓰든 HER2 PR-AUC는 내부에서도 0.25~0.40 수준에 그친다. 외부에서 무너지기 전에 이미 내부에서 약한 축이다.

## 결과 2: MIL 3종과 클래스별 열화

- Optuna로 최적화한 CLAM, TransMIL, DSMIL은 대부분의 클래스에서 baseline CLAM을 앞선다. 그럼에도 CPTAC 열화 패턴은 세 아키텍처에서 거의 같다.
- HER2-enriched는 세 모델 모두 **RPD = 1.000**. Normal-like는 TransMIL이 내부 최고 성능을 낸 뒤에도 외부에서 심하게 떨어진다. Luminal B도 세 아키텍처 모두 RPD가 높다. Luminal A와 Basal-like는 상대적으로 안정적이다.
- IHC 쪽은 ER과 PR이 중간 정도 열화, HER2-양성이 큰 낙폭.
- `원문 미확인:` 아키텍처별 클래스별 내부/외부 원값은 Table S4에 있고 본 폴더에 그 파일이 없다. 본문에는 방향과 패턴만 서술된다. Figure 1도 그림이라 수치를 읽을 수 없다.
- 저자 결론: 열화가 aggregator 설계가 아니라 FM이 만든 특징 표현과 과제 자체에 뿌리를 둔다.

## 결과 3: 도메인 시프트 네 요인 (Table 2)

네 요인의 정의는 다음과 같다.

| 기호 | 이름 | 정의 |
|---|---|---|
| Δn | 염색 정규화 이득 | Macenko 정규화 학습·평가 후 외부 클래스 성능에서 원본 성능을 뺀 값. 3개 MIL 평균 |
| Δp | 유병률 시프트 | p_c(CPTAC) − p_c(TCGA) |
| d | 특징공간 발산 | 클래스별 상위 K=8 attention 패치 임베딩 중심점 사이 코사인 거리. 3개 MIL 평균 |
| B̃ | 형태 분리도 | min_{d≠c} B(c,d) − B(c,c). 병리의 두 명이 매긴 형태 특징의 유의한 효과크기 합에서 유도 |

| Task | Class | Δn | Δp | d | B̃ | RPD |
|---|---|---|---|---|---|---|
| PAM50 | Basal-like | +0.015 | +0.132 | 0.139 | −0.125 | +0.219 |
| PAM50 | **HER2-enriched** | +0.000 | +0.025 | **0.197** | −0.904 | **+1.000** |
| PAM50 | Luminal A | −0.020 | −0.075 | 0.123 | +0.574 | +0.166 |
| PAM50 | Luminal B | +0.067 | −0.066 | 0.149 | +0.693 | +0.644 |
| PAM50 | Normal-like | +0.061 | −0.016 | 0.147 | **−1.232** | +0.906 |
| ER | ER-negative | −0.053 | +0.220 | 0.136 | +1.445 | +0.063 |
| ER | ER-positive | −0.038 | −0.220 | **0.105** | **+2.642** | +0.093 |
| PR | PR-negative | −0.028 | +0.143 | 0.112 | +1.080 | +0.163 |
| PR | PR-positive | −0.032 | −0.143 | 0.118 | +1.558 | +0.161 |
| HER2 | HER2-negative | +0.006 | +0.099 | 0.106 | −0.296 | **+0.021** |
| HER2 | HER2-positive | +0.035 | −0.099 | 0.115 | +0.419 | +0.643 |

- 특징공간 발산은 HER2-enriched에서 최대(0.197), ER-양성에서 최소(0.105)다. DSMIL이 CLAM·TransMIL보다 일관되게 큰 거리를 낸다.
- 형태 분리도는 Normal-like −1.232에서 ER-양성 +2.642까지 퍼져 있다. 음수는 외부 코호트의 그 클래스가 자기 자신보다 다른 클래스와 더 닮았다는 뜻이다.
- 병리의 두 명 사이 일치도는 낮은 편이다: 순서형 특징 가중 κw 0.152~0.289, 이분형 κ 0.177~0.321. 저자들도 이를 B̃ 추정의 불확실성으로 인정한다.

## 결과 4: 요인 회귀 (Table 3, n=11 클래스)

BH 보정은 단변량 Spearman, 단변량 OLS 기울기, 다변량, 공선성의 네 묶음 안에서 각각 따로 적용했다.

**단변량**

| 요인 | Pearson r | Spearman ρ | q(ρ) | R² | β | q(β) |
|---|---|---|---|---|---|---|
| d | +0.759 | +0.755 | 0.029 * | 0.577 | +10.110 | 0.027 * |
| Δn | +0.692 | +0.673 | 0.047 * | 0.479 | +6.160 | 0.037 * |
| B̃ | −0.651 | −0.573 | 0.087 † | 0.424 | −0.204 | 0.040 * |
| Δp | −0.171 | −0.109 | 0.750 | 0.029 | −0.449 | 0.615 |

**다변량 `RPD ~ Δn + d`**: R²=0.800, adj R²=0.750, F=16.03, q=0.005 *

| 항 | β | Std Error | t | q | ΔR² |
|---|---|---|---|---|---|
| d | +7.9728 | 2.2215 | +3.589 | 0.011 * | 0.322 |
| Δn | +4.4456 | 1.4857 | +2.992 | 0.017 * | 0.224 |
| B̃ | +0.0125 | 0.0805 | +0.156 | 0.881 | 0.001 |

**공선성**

| 쌍 | Pearson r | Spearman ρ | q(ρ) | VIF |
|---|---|---|---|---|
| d ~ B̃ | −0.583 | −0.482 | 0.160 | 1.515 |
| Δn ~ d | +0.321 | +0.455 | 0.160 | 1.115 |
| Δn ~ B̃ | −0.639 | −0.691 | 0.056 † | 1.691 |

- 80.0%라는 숫자의 정체는 `Δn`과 `d` 두 항만 넣은 최소 모형의 R²다. B̃는 단변량에서는 유의했지만 두 항이 들어오면 고유 기여가 사실상 0(ΔR²<0.001, q=0.881)이라 최종 모형에서 빠진다. 저자 설명은 B̃가 Δn·d와 겹치는 정보를 담고 있다는 것이다(Δn~B̃ ρ=−0.691).
- 결론 문장: 공변량 시프트(염색·특징공간)가 주범이고 사전 시프트(유병률)는 아니다.

## 염색 정규화 견고성

- 방법: 모든 패치에 Macenko 정규화를 적용한 뒤 특징을 뽑는다. PathBench-MIL이 SlideFlow 정규화 파이프라인의 population-level preset(v3)을 쓴다. 이 preset은 H와 E 염색 벡터를 RGB 공간에 담은 3×2 stain matrix와 기준 최대 농도 **[1.766, 1.280]**을 정의하며, 이 값은 TCGA 슬라이드 450장에서 뽑은 약 50,000개 패치의 Macenko 분해 파라미터 평균으로 추정한 것이다.
- 정규화는 feature bag 생성 시 패치 단위로, Virchow v2 특징 추출 직전에 적용한다. TCGA 모집단 기준으로 CPTAC까지 맞춘다.
- 정규화 TCGA로 학습해 정규화 CPTAC에서 평가하고, 클래스별 차이를 `n_c = Perf(normalised) − Perf(original)`로 정의한다(3개 MIL 평균).
- 결과: 효과가 클래스·아키텍처마다 제각각이다(Table S5). **HER2-enriched는 어떤 아키텍처에서도 변화가 없다(Δn=0.000).** ER·PR 계열은 음수(정규화가 오히려 손해), Luminal B(+0.067)와 Normal-like(+0.061)는 양수.
- `해석:` Δn이 RPD와 양의 상관을 갖는다는 것은, 정규화로 회복되는 클래스일수록 원래 낙폭이 컸다는 뜻이다. 저자들은 이를 Virchow v2가 형태 정보와 색 의존 정보를 모든 클래스에서 분리해 내지는 못했다는 근거로 읽는다.
- `원문 미확인:` 아키텍처별 Δn 원값은 Table S5.

## 한계 (원문 Limitations 절 전체)

저자들이 든 항목은 넷이다.

1. **냉동 조직 한정**. TCGA·CPTAC 모두 flash-frozen으로 제한해 임상에서 흔한 FFPE로 일반화되지 않는다. 확인한 공변량 요인이 FFPE 코호트의 시프트 원인을 다 담지 못할 수 있다.
2. **FM 목록의 시점 한계와 선택 절차**. 2025년 초 공개된 FM(H-optimus-1 등)은 가중치를 구할 수 없어 빠졌다. 또한 FM 선택을 baseline CLAM 하나로 했으므로, 최적화된 MIL 구성에서는 순위가 달라질 수 있다. Ma et al.이 독립적으로 Virchow v2 우위를 보고한 점이 이 우려를 부분적으로 덜어 준다고 적는다.
3. **회귀의 표본 크기**. 클래스 11개뿐이라 탐색적이다. PAM50과 IHC를 과제 유형 공변량 없이 합쳤고, 요인이 과제와 무관한 클래스 수준 기전으로 작동한다는 가정은 검증되지 않았다. 결과는 가설 생성으로 읽어야 한다.
4. **병리 주석의 불확실성**. 두 병리 사이 일치도가 낮고(κw 0.152~0.289, κ 0.177~0.321) 클래스당 패치가 25개뿐이라 B̃의 견고성이 떨어진다. 저자들은 통상 조직학적 등급 매기기보다 이 주석 과제가 훨씬 주관적이라고 변호하면서도, B̃와 RPD의 단변량 연관을 해석할 때 고려할 불확실성이라고 인정한다.

## 이 논문이 하지 않은 것 (전문 확인)

Paper C 방어에 바로 쓰는 목록이다. 각 항목은 전문 문자열 검색과 정독으로 확인했다.

| 항목 | 판정 | 근거 |
|---|---|---|
| 기관(tissue source site) 통제 분할 | **없음** | `tissue source site`·`submitter`·`batch`·`scanner` 각 0회. 분할은 환자 층화만 |
| 사전등록 | **없음** | `preregist`·`pre-regist`·`registered` 0회 |
| 치료 라우팅 / 치료 배정 | **없음** | `decision` 0회, `trastuzumab` 본문 0회, `therap`은 서론의 "therapeutic responses" 1회뿐 |
| 의사결정 비용·효용 분석 | **없음** | `cost`는 전부 "분자검사가 비싸다"는 동기 문장(초록·서론 3회). `utility`·`net benefit` 0회 |
| 확률 보정(calibration)·기권 | **없음** | `calibrat` 0회 |
| 임상 효용·전향 검증 | **없음** | `clinical deployment` 0회. 저자 스스로 exploratory·hypothesis-generating으로 한정 |
| 다암종 | **없음** | 유방 단일. `pan-cancer` 0회 |
| AUROC 보고 | **없음** | `AUROC`·`AUC-ROC` 0회. macro-F1과 PR-AUC만 |
| 다중 외부 코호트 | **없음** | CPTAC 하나 |
| FFPE | **없음** | 명시적으로 제외하고 한계로 인정 |

- `해석:` 그들이 남긴 공백은 두 갈래다. 하나는 **분할 엄밀성**(기관 통제·사전등록)이고, 다른 하나는 **결정 층위**(예측 정확도 위에 올라가는 라우팅 비용·보정·기권)다. 우리 Paper C는 뒤쪽을 헤드라인으로 삼고, 앞쪽은 내부 수치의 성격 차이를 설명하는 데 쓴다.

## 우리 적용 (BIOP02)

1. **인용 필수**. 같은 코호트, 같은 과제, 같은 동기로 이미 출판되었으므로 미인용은 리뷰어의 첫 지적이 된다.
2. **한 줄 양보 후 전환**. 예측 정확도 표로 맞서지 않는다. 이 논문의 외부 붕괴를 SUBSTITUTABILITY_LAW의 외부 근거로 재배치한다.
3. **HER2 수렴을 명시**. 그들 HER2-enriched RPD=1.000, HER2-양성 RPD=0.643. 우리 HER2 내부 AUROC 0.599, 외부 0.530. 지표가 달라 수치는 못 겹치지만 결론 방향은 같다. 독립 재현으로 서술한다.
4. **분할 대조는 가설로만**. 그들이 기관을 통제하지 않았다는 것은 사실이고, 그것이 내부 수치를 부풀렸다는 것은 우리 추론이다. 원인 단정 금지.
5. **UNI 계열 주의**. Table 1에서 UNI의 HER2 낙폭(계산값 0.626)이 Virchow v2(0.451)보다 크다. 우리 파이프라인이 UNI v1 기반이므로 "FM을 바꾸면 해결된다"는 반론에 대비해 이 숫자를 들고 있어야 한다.

## 심층

한계 평가, 산업·재현 관점, 방법론 상세, Paper C 정면 대조는 각각 `_lens-academic.md`, `_lens-industry.md`, `_methodology-brief.md`, `_comparison-with-biop02.md` 참고.

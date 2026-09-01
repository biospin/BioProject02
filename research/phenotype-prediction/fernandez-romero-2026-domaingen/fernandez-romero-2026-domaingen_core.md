# Fernandez-Romero et al., 2026 — Domain generalisation in BC molecular classification — core 분석

> 근거 자료: `sources/fernandez-romero-2026-domaingen_pmc.xml`(Europe PMC JATS 전문, Table 1·2·3 원문 파싱) + `sources/fernandez-romero-2026-domaingen.pdf`(본문 11p). 2026-09-02 전문 기반 재작성.
>
> **2026-09-02 보강**: Supplementary PDF(`sources/..._supplementary.pdf`, 10p)를 확보해 Table S1~S9와 Figure S1~S3을 전부 옮겼다. 이전 판본에서 `원문 미확인:`으로 남겼던 아키텍처별 클래스별 원값(S4), 염색 정규화 세부(S5), 유병률(S6), 코사인 거리(S7), 형태 특징(S8), 일치도(S9)는 실측값으로 교체했다. 추출은 `pdftotext -layout`(poppler)으로 했고, S4·S5·S6·S7은 표에 적힌 값끼리 산술 검산해 33/33, 33/33, 11/11, 11/11 모두 일치함을 확인했다.
>
> 본문과 Table 1~3, Supplementary Table S1~S9에 숫자로 적힌 값만 단정한다. 우리가 원문 값에서 나눗셈으로 만든 값은 `계산값:`으로 구분한다.
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

## FM 13종의 정확한 구성 (Table S1)

Supplementary Table S1은 FM을 **12종만** 싣는다. 본문이 말하는 13종은 여기에 ImageNet 사전학습 ResNet-50 baseline을 더한 수다. 표의 출처는 Wölflein & Myles의 공개 목록([11], `github.com/georg-wolflein/pathology-foundation-models`)이다.

| # | Name | Release | WSIs | Tiles | Architecture | Training Data |
|---|---|---|---|---|---|---|
| 1 | CTransPath | Dec 2021 | 32K | 16M | Swin-T | TCGA, PAIP |
| 2 | RetCCL | Dec 2021 | 32K | 16M | ResNet-50 | TCGA, PAIP |
| 3 | CONCH | Jul 2023 | 21K | 16M | ViT-B | in-house |
| 4 | UNI | Aug 2023 | 100K | 100M | ViT-L | in-house |
| 5 | Prov-GigaPath | May 2024 | 170K | 1.4B | ViT | in-house |
| 6 | Hibou-B | Jun 2024 | 1.1M | 510M | ViT-B | in-house |
| 7 | Hibou-L | Jun 2024 | 1.1M | 1.2B | ViT-L | in-house |
| 8 | H-optimus-0 | Jul 2024 | 500K | >100M | ViT-G | in-house |
| 9 | Virchow v2 | Aug 2024 | 3.1M | 2B | ViT-H | in-house |
| 10 | Phikon v2 | Sep 2024 | 58.4K | 456M | ViT-L | PANCAN-XL |
| 11 | Musk | Jan 2025 | 33K | 50M | BEiT3 | TCGA |
| 12 | UNI-2 | Jan 2025 | 350K | 200M | ViT-H | in-house |
| 13 | ResNet-50 (baseline) | ImageNet 사전학습 | 해당 없음 | 해당 없음 | ResNet-50 | ImageNet |

- **임베딩 차원은 표에 없다.** Table S1은 아키텍처 계열(ViT-B/L/H/G, Swin-T, BEiT3)까지만 적고 출력 차원(`embed_dim`)을 싣지 않으며, 본문에도 없다. 우리가 인용하려면 각 모델 카드에서 따로 확인해야 한다. 여기서 추정해 채우지 않는다.
- **버전 표기**는 릴리스 월까지가 전부다. 가중치 커밋 해시나 체크포인트 태그는 원문에 없다.
- **본문과 표가 어긋나는 지점**: 본문은 "12 state-of-the-art FMs (July 2023–January 2025)"라고 적지만, Table S1의 CTransPath와 RetCCL은 둘 다 Dec 2021이다. 12종 중 10종만 본문이 말한 기간에 들어간다. 인용할 때는 본문의 기간 표현 대신 Table S1의 개별 릴리스 월을 쓰는 편이 안전하다.
- Optuna 탐색이 건드린 `z_dim`은 FM의 출력 차원이 아니라 MIL 쪽 투영 차원이다(Table S3). 둘을 섞지 않는다.

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

### Table S4 원값 (아키텍처 3종 x 클래스 11개, 염색 정규화 없음)

Supplementary Table S4가 실은 값을 그대로 옮긴다. 모두 Virchow v2 임베딩 위에서 얻은 값이고, PAM50은 F1, IHC는 PR-AUC다. RPD는 표에 적힌 대로이며, `(TCGA − CPTAC) / TCGA`로 33행 전부 검산해 어긋나는 행이 없었다.

| MIL | Task | Class | 지표 | TCGA | CPTAC | RPD |
|---|---|---|---|---|---|---|
| CLAM | PAM50 | Basal-like | F1 | 0.852 | 0.693 | +0.187 |
| CLAM | PAM50 | HER2-enriched | F1 | 0.598 | 0.000 | **+1.000** |
| CLAM | PAM50 | Luminal A | F1 | 0.865 | 0.732 | +0.154 |
| CLAM | PAM50 | Luminal B | F1 | 0.629 | 0.200 | +0.682 |
| CLAM | PAM50 | Normal-like | F1 | 0.179 | 0.000 | **+1.000** |
| CLAM | ER | ER-negative | PR-AUC | 0.670 | 0.698 | **−0.042** |
| CLAM | ER | ER-positive | PR-AUC | 0.955 | 0.881 | +0.077 |
| CLAM | PR | PR-negative | PR-AUC | 0.901 | 0.764 | +0.152 |
| CLAM | PR | PR-positive | PR-AUC | 0.962 | 0.822 | +0.145 |
| CLAM | HER2 | HER2-negative | PR-AUC | 0.983 | 0.925 | +0.059 |
| CLAM | HER2 | HER2-positive | PR-AUC | 0.728 | 0.176 | +0.758 |
| DSMIL | PAM50 | Basal-like | F1 | 0.824 | 0.633 | +0.232 |
| DSMIL | PAM50 | HER2-enriched | F1 | 0.538 | 0.000 | **+1.000** |
| DSMIL | PAM50 | Luminal A | F1 | 0.862 | 0.745 | +0.136 |
| DSMIL | PAM50 | Luminal B | F1 | 0.607 | 0.242 | +0.601 |
| DSMIL | PAM50 | Normal-like | F1 | 0.353 | 0.062 | +0.824 |
| DSMIL | ER | ER-negative | PR-AUC | 0.810 | 0.713 | +0.120 |
| DSMIL | ER | ER-positive | PR-AUC | 0.978 | 0.854 | +0.127 |
| DSMIL | PR | PR-negative | PR-AUC | 0.876 | 0.788 | +0.101 |
| DSMIL | PR | PR-positive | PR-AUC | 0.959 | 0.811 | +0.154 |
| DSMIL | HER2 | HER2-negative | PR-AUC | 0.930 | 0.925 | +0.005 |
| DSMIL | HER2 | HER2-positive | PR-AUC | 0.329 | 0.123 | +0.626 |
| TransMIL | PAM50 | Basal-like | F1 | 0.969 | 0.739 | +0.237 |
| TransMIL | PAM50 | HER2-enriched | F1 | 0.912 | 0.000 | **+1.000** |
| TransMIL | PAM50 | Luminal A | F1 | 0.966 | 0.765 | +0.208 |
| TransMIL | PAM50 | Luminal B | F1 | 0.902 | 0.317 | +0.649 |
| TransMIL | PAM50 | Normal-like | F1 | 0.915 | 0.098 | +0.893 |
| TransMIL | ER | ER-negative | PR-AUC | 0.859 | 0.763 | +0.112 |
| TransMIL | ER | ER-positive | PR-AUC | 0.986 | 0.913 | +0.074 |
| TransMIL | PR | PR-negative | PR-AUC | 0.969 | 0.741 | +0.235 |
| TransMIL | PR | PR-positive | PR-AUC | 0.985 | 0.805 | +0.183 |
| TransMIL | HER2 | HER2-negative | PR-AUC | 0.904 | 0.904 | 0.000 |
| TransMIL | HER2 | HER2-positive | PR-AUC | 0.244 | 0.111 | +0.545 |

원값이 들어오면서 본문 서술만으로는 보이지 않던 것들이 드러난다.

- **HER2-enriched의 RPD=1.000은 세 아키텍처에서 모두 CPTAC F1이 정확히 0.000이기 때문이다.** 성능이 낮아진 것이 아니라 해당 클래스를 단 한 건도 맞히지 못했다는 뜻이다. 내부 F1은 CLAM 0.598, DSMIL 0.538, TransMIL 0.912로 서로 크게 다른데도 외부는 모두 0이다.
- **TransMIL의 내부 성능이 유독 높다.** 11개 클래스 중 Normal-like 0.915, HER2-enriched 0.912처럼 CLAM·DSMIL보다 0.3~0.7 높은 값이 여럿이다. 그런데 CPTAC 값은 세 모델이 비슷하게 낮아서, 결과적으로 TransMIL의 RPD가 가장 커진다. 내부 적합을 잘할수록 낙폭이 커 보이는 구조이므로, RPD를 아키텍처 간 우열 지표로 읽으면 안 된다.
- **유일한 음수 RPD는 CLAM의 ER-negative 하나뿐이다**(0.670 → 0.698, −0.042). 곧 외부에서 개선된 사례가 33개 중 1개다.
- HER2-양성은 내부부터 이미 약하다. TransMIL 0.244, DSMIL 0.329로 내부 PR-AUC가 0.35를 넘지 못한다. 외부 붕괴 이전에 과제 자체가 어렵다는 신호다.
- `해석:` 세 아키텍처가 서로 다른 내부 성능에서 출발해 같은 외부 바닥으로 수렴한다는 점이 저자 결론을 뒷받침한다. 열화는 aggregator 설계가 아니라 FM이 만든 특징 표현과 과제 자체에 뿌리를 둔다.
- **표기 불일치 하나**: Table S4 캡션은 TCGA 열을 "hold-out test score"라고 적지만, 본문은 이 단계의 내부 성능을 10-fold CV 평균으로 정의한다. 어느 쪽이 맞는지는 원문만으로 가릴 수 없어 `판독 불확실`로 남긴다. 다만 이 열의 값으로 계산한 RPD가 본문 Table 2의 RPD와 11/11 일치하므로, RPD 계산에 쓰인 내부값이 이 열이라는 사실은 확실하다.

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
- 병리학자 두 명 사이의 일치도는 낮은 편이다: 순서형 특징 가중 κw 0.152~0.289, 이분형 κ 0.177~0.321. 저자들도 이를 B̃ 추정의 불확실성으로 인정한다.

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

### Supplementary Figure S2·S3이 더해 주는 것

Figure S2는 네 요인 각각을 RPD에 회귀한 산점도 네 장이고, Figure S3은 B̃와 나머지 두 유의 요인의 공선성 산점도 두 장이다. 패널에 적힌 통계량은 본문 Table 3과 어긋나지 않는다.

| 그림 | 관계 | R² | ρ | q |
|---|---|---|---|---|
| S2 | RPD ~ Δn | 0.479 | +0.673 | q(OLS) 0.037, q(ρ) 0.047 |
| S2 | RPD ~ Δp | 0.029 | −0.109 | q(OLS) 0.615, q(ρ) 0.750 |
| S2 | RPD ~ d | 0.577 | +0.755 | q(OLS) 0.027, q(ρ) 0.029 |
| S2 | RPD ~ B̃ | 0.424 | −0.573 | q(OLS) 0.040, q(ρ) 0.087 |
| S3 | Δn ~ B̃ | 0.409 | −0.691 | q 0.056 (비유의) |
| S3 | d ~ B̃ | 0.340 | −0.482 | q 0.160 (비유의) |

- Figure S3의 R²(0.409, 0.340)는 본문 Table 3 공선성 절에 없는 값이다. 본문은 같은 쌍을 Pearson r(−0.639, −0.583)과 VIF(1.691, 1.515)로만 적는다. 부호와 크기는 서로 모순되지 않는다.
- 점 배치를 보면 네 패널 모두 HER2-enriched와 Normal-like가 RPD 1.0 부근 오른쪽 위에 따로 떨어져 있다. n=11에서 이 두 점이 적합을 상당 부분 끌고 간다. 영향점 진단(Cook's distance 등)은 원문에 없다.
- 축 라벨 일부가 PDF 폰트 인코딩 문제로 깨져 나온다(예: `Δp (p0e4a+e−ce 1()f2)`). 라벨 문자열은 `판독 불확실`로 두되, 패널의 통계량 수치는 깨지지 않았고 본문 Table 3과 일치해 신뢰할 수 있다.

## Supplementary 확보로 바뀐 것과 남은 공백

**본문 서술과 충돌하거나 어긋나는 지점 (3건)**

1. **FM 릴리스 기간**. 본문은 12종을 "July 2023–January 2025"로 묶지만 Table S1의 CTransPath와 RetCCL은 Dec 2021이다. 12종 중 10종만 그 기간에 든다.
2. **Table S4 캡션의 TCGA 열 정의**. 캡션은 "hold-out test score"라 적고 본문은 10-fold CV 평균이라 적는다. 어느 쪽이 맞는지 원문만으로 가릴 수 없다.
3. **Table S9의 n=275 귀속**. 코호트 하나당 패치 수(125+150)와 맞아떨어지지만 어느 코호트인지는 밝히지 않는다.

셋 다 값 자체의 모순이 아니라 표기와 서술의 어긋남이다. Table S4·S5·S6·S7의 수치는 본문 Table 2와 11/11 일치하므로, 본문과 supplementary의 **숫자가 서로 다른 사례는 발견되지 않았다**.

**여전히 `원문 미확인:`으로 남는 것 (4건)**

1. FM 13종의 임베딩 차원. Table S1은 아키텍처 계열까지만 싣는다.
2. FM 가중치 버전 식별자(커밋 해시, 체크포인트 태그).
3. 형태 유사도 행렬 B(c,c')의 원소값과 rank-biserial 효과크기.
4. SlideFlow v3 preset의 3×2 stain matrix 성분값. 기준 최대 농도 [1.766, 1.280]만 공개되어 있다.

**FM별 클래스별 원값은 애초에 존재하지 않는다.** 이것이 이번 확보로 확정된 가장 중요한 사실이다. 논문의 설계상 클래스 단위 성능은 최고 FM 하나(Virchow v2) 위에서 MIL 3종에 대해서만 계산했다(Table S4). FM 13종을 가로지르는 값은 본문 Table 1의 과제 단위 요약(macro-F1, PR-AUC) 하나뿐이며, 13 x 3 x 클래스 격자는 논문에 없다. 그 격자를 인용하려는 계획은 접어야 한다.

## 염색 정규화 견고성

- 방법: 모든 패치에 Macenko 정규화를 적용한 뒤 특징을 뽑는다. PathBench-MIL이 SlideFlow 정규화 파이프라인의 population-level preset(v3)을 쓴다. 이 preset은 H와 E 염색 벡터를 RGB 공간에 담은 3×2 stain matrix와 기준 최대 농도 **[1.766, 1.280]**을 정의하며, 이 값은 TCGA 슬라이드 450장에서 뽑은 약 50,000개 패치의 Macenko 분해 파라미터 평균으로 추정한 것이다.
- 정규화는 feature bag 생성 시 패치 단위로, Virchow v2 특징 추출 직전에 적용한다. TCGA 모집단 기준으로 CPTAC까지 맞춘다.
- 정규화 TCGA로 학습해 정규화 CPTAC에서 평가하고, 클래스별 차이를 `n_c = Perf(normalised) − Perf(original)`로 정의한다(3개 MIL 평균).
### 기준 슬라이드에 관한 정정

찾던 "기준 슬라이드"는 **존재하지 않는다**. SlideFlow v3 preset은 단일 참조 슬라이드를 지정하는 방식이 아니라, TCGA 450장에서 뽑은 약 50,000 패치의 Macenko 분해 파라미터를 평균 낸 **모집단 수준 목표값**을 쓴다. 목표는 두 덩어리로 이뤄진다. 하나는 H와 E 염색 벡터를 RGB에 담은 3×2 stain matrix이고, 다른 하나는 기준 최대 농도 [1.766, 1.280]이다. 행렬 자체의 여섯 개 성분값은 원문에 적혀 있지 않으므로 `원문 미확인:`으로 남긴다. 우리가 같은 설정을 재현하려면 SlideFlow v3 preset을 직접 읽어야 한다.

### Table S5 원값 (정규화 전후, 모두 CPTAC 외부 평가)

`None`은 정규화 없이, `Macenko`는 정규화 후의 외부 성능이고 `Δn = Macenko − None`이다. 33행 전부 검산해 어긋나는 행이 없었다.

| MIL | Task | Class | None | Macenko | Δn |
|---|---|---|---|---|---|
| CLAM | PAM50 | Basal-like | 0.693 | 0.682 | −0.011 |
| CLAM | PAM50 | HER2-enriched | 0.000 | 0.000 | +0.000 |
| CLAM | PAM50 | Luminal A | 0.732 | 0.740 | +0.008 |
| CLAM | PAM50 | Luminal B | 0.200 | 0.386 | **+0.186** |
| CLAM | PAM50 | Normal-like | 0.000 | 0.103 | +0.103 |
| CLAM | ER | ER-negative | 0.698 | 0.733 | +0.035 |
| CLAM | ER | ER-positive | 0.881 | 0.911 | +0.030 |
| CLAM | PR | PR-negative | 0.764 | 0.733 | −0.031 |
| CLAM | PR | PR-positive | 0.822 | 0.758 | −0.064 |
| CLAM | HER2 | HER2-negative | 0.925 | 0.933 | +0.008 |
| CLAM | HER2 | HER2-positive | 0.176 | 0.234 | +0.058 |
| DSMIL | PAM50 | Basal-like | 0.633 | 0.694 | +0.061 |
| DSMIL | PAM50 | HER2-enriched | 0.000 | 0.000 | +0.000 |
| DSMIL | PAM50 | Luminal A | 0.745 | 0.732 | −0.013 |
| DSMIL | PAM50 | Luminal B | 0.242 | 0.246 | +0.004 |
| DSMIL | PAM50 | Normal-like | 0.062 | 0.160 | +0.098 |
| DSMIL | ER | ER-negative | 0.713 | 0.685 | −0.028 |
| DSMIL | ER | ER-positive | 0.854 | 0.873 | +0.019 |
| DSMIL | PR | PR-negative | 0.788 | 0.771 | −0.017 |
| DSMIL | PR | PR-positive | 0.811 | 0.828 | +0.017 |
| DSMIL | HER2 | HER2-negative | 0.925 | 0.917 | −0.008 |
| DSMIL | HER2 | HER2-positive | 0.123 | 0.140 | +0.017 |
| TransMIL | PAM50 | Basal-like | 0.739 | 0.735 | −0.004 |
| TransMIL | PAM50 | HER2-enriched | 0.000 | 0.000 | +0.000 |
| TransMIL | PAM50 | Luminal A | 0.765 | 0.710 | −0.055 |
| TransMIL | PAM50 | Luminal B | 0.317 | 0.329 | +0.012 |
| TransMIL | PAM50 | Normal-like | 0.098 | 0.080 | −0.018 |
| TransMIL | ER | ER-negative | 0.763 | 0.598 | **−0.165** |
| TransMIL | ER | ER-positive | 0.913 | 0.751 | **−0.162** |
| TransMIL | PR | PR-negative | 0.741 | 0.705 | −0.036 |
| TransMIL | PR | PR-positive | 0.805 | 0.757 | −0.048 |
| TransMIL | HER2 | HER2-negative | 0.904 | 0.923 | +0.019 |
| TransMIL | HER2 | HER2-positive | 0.111 | 0.141 | +0.030 |

- **HER2-enriched는 세 아키텍처 모두 정규화 전후가 0.000이다.** 정규화가 효과 없다기보다, 이미 바닥이라 움직일 자리가 없다고 읽는 편이 정확하다. Δn=0.000이라는 값을 "염색이 원인이 아니다"의 근거로 인용하면 오독이 된다.
- **정규화가 손해인 경우가 33건 중 13건이다.** 특히 TransMIL의 ER에서 −0.165, −0.162로 크게 떨어진다. Macenko를 일괄 적용하는 것이 안전한 기본값이 아니라는 실측 근거다.
- 가장 크게 회복된 것은 CLAM의 Luminal B(+0.186)와 Normal-like(+0.103)다.
- 부호가 아키텍처마다 뒤집히는 클래스가 있다. Basal-like는 CLAM −0.011, DSMIL +0.061, TransMIL −0.004이고, Luminal A는 CLAM +0.008, DSMIL −0.013, TransMIL −0.055다. 본문 Table 2가 쓰는 Δn은 이 셋의 평균이라 이런 상쇄가 가려진다.
- `해석:` Δn이 RPD와 양의 상관을 갖는다는 것은, 정규화로 회복되는 클래스일수록 원래 낙폭이 컸다는 뜻이다. 저자들은 이를 Virchow v2가 형태 정보와 색 의존 정보를 모든 클래스에서 분리해 내지는 못했다는 근거로 읽는다.

## 클래스 유병률 (Table S6)

p는 각 코호트 안에서 그 클래스가 차지하는 비율이고, Δp = p(CPTAC) − p(TCGA)다. 11행 전부 검산해 일치했고, PAM50 다섯 아형의 합은 TCGA 0.999, CPTAC 1.001로 반올림 오차 범위 안이다.

| Task | Class | p(TCGA) | p(CPTAC) | Δp |
|---|---|---|---|---|
| PAM50 | Basal-like | 0.170 | 0.302 | **+0.132** |
| PAM50 | HER2-enriched | 0.076 | 0.101 | +0.025 |
| PAM50 | Luminal A | 0.525 | 0.450 | −0.075 |
| PAM50 | Luminal B | 0.179 | 0.114 | −0.066 |
| PAM50 | Normal-like | 0.049 | 0.034 | −0.016 |
| ER | ER-negative | 0.160 | 0.380 | **+0.220** |
| ER | ER-positive | 0.840 | 0.620 | **−0.220** |
| PR | PR-negative | 0.312 | 0.455 | +0.143 |
| PR | PR-positive | 0.688 | 0.545 | −0.143 |
| HER2 | HER2-negative | 0.793 | 0.891 | +0.099 |
| HER2 | HER2-positive | 0.207 | 0.108 | −0.099 |

- **가장 중요한 용어 정리**: 이 논문에서 `Δn`은 유병률과 아무 관계가 없다. Δn은 Macenko 정규화 이득이고, 유병률 차이는 `Δp`다. 두 기호를 바꿔 인용하면 결론이 뒤집힌다. Δn은 유의하고(q=0.037) Δp는 유의하지 않기(q=0.615) 때문이다.
- CPTAC이 TCGA보다 훨씬 공격적인 구성이다. Basal-like가 0.170에서 0.302로 늘고 ER-음성이 0.160에서 0.380으로 두 배 넘게 는다. HER2-양성은 반대로 0.207에서 0.108로 줄어든다.
- `해석:` 방향이 흥미롭다. 외부에서 **더 흔해진** ER-음성(Δp=+0.220)은 RPD가 0.063으로 가장 안정적인 축에 들고, 외부에서 **더 드물어진** HER2-양성(Δp=−0.099)은 RPD 0.643이다. 유병률이 낮아지는 쪽이 무너진다는 그림이 눈에는 보이지만, 회귀에서는 Δp의 설명력이 R²=0.029에 그쳐 통계적으로 지지되지 않는다. 저자들이 사전 시프트를 기각한 근거가 이 대비다.
- Δn 계산 근거로 오해할 여지가 있어 못 박아 둔다. Δn은 Table S5의 정규화 전후 차이에서 나오고, Table S6은 Δp의 근거일 뿐이다.

## 코사인 중심점 거리 (Table S7)

Virchow v2 임베딩 공간에서 클래스별 TCGA 중심점과 CPTAC 중심점 사이의 코사인 거리다. 각 WSI에서 attention 상위 K=8 패치를 골라 계산했고, `d`는 세 아키텍처의 산술 평균이다. 11행 모두 평균이 맞는지 검산해 일치했다.

| Task | Class | CLAM | DSMIL | TransMIL | d (평균) |
|---|---|---|---|---|---|
| PAM50 | Basal-like | 0.099 | 0.222 | 0.096 | 0.139 |
| PAM50 | HER2-enriched | 0.118 | 0.365 | 0.109 | **0.197** |
| PAM50 | Luminal A | 0.096 | 0.184 | 0.087 | 0.123 |
| PAM50 | Luminal B | 0.123 | 0.204 | 0.121 | 0.149 |
| PAM50 | Normal-like | 0.103 | 0.232 | 0.106 | 0.147 |
| ER | ER-negative | 0.096 | 0.208 | 0.102 | 0.136 |
| ER | ER-positive | 0.098 | 0.125 | 0.093 | **0.105** |
| PR | PR-negative | 0.093 | 0.133 | 0.111 | 0.112 |
| PR | PR-positive | 0.100 | 0.139 | 0.114 | 0.118 |
| HER2 | HER2-negative | 0.091 | 0.145 | 0.082 | 0.106 |
| HER2 | HER2-positive | 0.098 | 0.153 | 0.096 | 0.115 |

- 평균 d 열은 본문 Table 2의 d와 11개 값이 모두 같다. 본문과 supplementary가 어긋나지 않는다.
- **DSMIL이 다른 둘보다 일관되게 큰 거리를 낸다.** CLAM은 0.091~0.123, TransMIL은 0.082~0.121로 좁은 범위에 모여 있는데 DSMIL만 0.125~0.365로 넓다. 곧 평균 d의 클래스 간 변이는 상당 부분 DSMIL이 만든다. HER2-enriched가 최대값 0.197을 받은 것도 DSMIL의 0.365 덕이 크고, CLAM(0.118)과 TransMIL(0.109)만 보면 다른 클래스와 크게 다르지 않다.
- `해석:` d가 RPD를 가장 잘 설명하는 요인(R²=0.577)인데 그 d의 분산이 한 아키텍처의 attention 분포에 크게 기대고 있다. 저자들이 세 모델 평균을 쓴 것은 합리적이나, "특징공간 발산이 주범"이라는 결론의 견고성은 DSMIL 의존도만큼 약해진다. 원문이 이 점을 짚지 않으므로 우리 추론으로 표시해 둔다.

## 형태 특징 실측값 (Table S8)

병리학자 두 명의 점수를 평균한 값이고, 클래스마다 코호트별 25개 패치의 평균이다. 튜불 형성과 핵 다형성은 1~3 순서형, 유사분열은 개수, 나머지 셋은 유무(0/1)를 평균한 값이라 0~1 사이에 놓인다.

| Task | Class | Cohort | 튜불형성 | 핵다형성 | 유사분열 | 종양괴사 | 림프구침윤 | 다형핵구침윤 |
|---|---|---|---|---|---|---|---|---|
| PAM50 | Basal-like | CPTAC | 2.76 | 2.14 | 0.48 | 0.46 | 0.98 | 0.60 |
| PAM50 | Basal-like | TCGA | 2.72 | 2.88 | 0.58 | 0.56 | 0.54 | 0.78 |
| PAM50 | HER2-enriched | CPTAC | 2.76 | 1.96 | 0.60 | 0.48 | 0.76 | 0.52 |
| PAM50 | HER2-enriched | TCGA | 2.82 | 2.78 | 0.38 | 0.48 | 0.96 | 0.72 |
| PAM50 | Luminal A | CPTAC | 2.14 | 1.42 | 0.02 | 0.36 | 0.50 | 0.06 |
| PAM50 | Luminal A | TCGA | 1.64 | 1.52 | 0.12 | 0.00 | 0.56 | 0.12 |
| PAM50 | Luminal B | CPTAC | 2.38 | 1.76 | 0.26 | 0.12 | 0.88 | 0.32 |
| PAM50 | Luminal B | TCGA | 2.20 | 2.26 | 0.28 | 0.10 | 0.80 | 0.22 |
| PAM50 | Normal-like | CPTAC | 2.62 | 1.96 | 0.28 | 0.26 | 0.80 | 0.32 |
| PAM50 | Normal-like | TCGA | 1.36 | 1.34 | 0.00 | 0.00 | 0.80 | 0.04 |
| ER | ER-negative | CPTAC | 2.80 | 2.66 | 0.68 | 0.44 | 0.86 | 0.54 |
| ER | ER-negative | TCGA | 2.72 | 2.60 | 0.30 | 0.54 | 0.62 | 0.76 |
| ER | ER-positive | CPTAC | 2.44 | 1.94 | 0.26 | 0.24 | 0.90 | 0.24 |
| ER | ER-positive | TCGA | 2.40 | 2.20 | 0.12 | 0.06 | 0.94 | 0.26 |
| PR | PR-negative | CPTAC | 2.68 | 2.10 | 0.44 | 0.44 | 0.84 | 0.56 |
| PR | PR-negative | TCGA | 2.72 | 2.50 | 0.36 | 0.72 | 0.66 | 0.78 |
| PR | PR-positive | CPTAC | 2.42 | 1.72 | 0.16 | 0.22 | 0.84 | 0.38 |
| PR | PR-positive | TCGA | 2.34 | 1.90 | 0.08 | 0.12 | 0.64 | 0.32 |
| HER2 | HER2-negative | CPTAC | 2.58 | 1.86 | 0.30 | 0.26 | 0.94 | 0.48 |
| HER2 | HER2-negative | TCGA | 2.50 | 2.36 | 0.24 | 0.16 | 0.48 | 0.34 |
| HER2 | HER2-positive | CPTAC | 2.62 | 2.22 | 0.38 | 0.34 | 0.82 | 0.46 |
| HER2 | HER2-positive | TCGA | 2.62 | 2.78 | 0.28 | 0.36 | 0.56 | 0.44 |

- **핵 다형성이 11개 클래스 가운데 10개에서 CPTAC 쪽이 낮다.** 유일한 예외는 ER-음성(CPTAC 2.66 대 TCGA 2.60)이다. 계통적인 방향성이므로 클래스 고유의 생물학이 아니라 코호트 사이 주석 기준이나 슬라이드 품질 차이일 가능성이 있다. 원문은 이 패턴을 따로 언급하지 않는다.
- **Normal-like의 코호트 간 격차가 가장 크다.** 튜불 형성이 TCGA 1.36에서 CPTAC 2.62로, 핵 다형성이 1.34에서 1.96으로 벌어진다. B̃가 −1.232로 최저인 것과 방향이 맞는다.
- 림프구 침윤은 반대로 CPTAC이 대체로 높다. HER2-음성은 TCGA 0.48에서 CPTAC 0.94로 거의 두 배다.
- **`원문 미확인:` 형태 유사도 행렬 B(c,c') 자체는 어디에도 실려 있지 않다.** Table S8이 싣는 것은 B를 만들기 전 단계의 원자료(특징별 평균값)이고, Mann-Whitney 검정의 rank-biserial 효과크기와 그것을 합산한 11×11 행렬은 본문에도 supplementary에도 없다. 클래스별 요약값인 B̃만 본문 Table 2에 있다(Normal-like −1.232에서 ER-양성 +2.642). 우리가 이 행렬을 인용하려면 저자에게 요청해야 한다.

## 병리학자 일치도 (Table S9)

패치 275개를 이미지 식별자로 맞춘 뒤 계산했다. 순서형 세 가지는 선형 가중 κw, 이분형 세 가지는 Cohen's κ이며, 해석 구간은 Landis & Koch(1977)를 따른다.

| 구분 | Feature | 통계량 | n | 값 | 해석 |
|---|---|---|---|---|---|
| 순서형 | Tubule Formation | κw | 275 | 0.289 | fair |
| 순서형 | Nuclear Pleomorphism | κw | 275 | 0.285 | fair |
| 순서형 | Mitotic Activity | κw | 275 | **0.152** | slight |
| 이분형 | Necrosis | κ | 275 | 0.177 | slight |
| 이분형 | Lymphocytic Infiltrate | κ | 275 | 0.185 | slight |
| 이분형 | PMN Infiltrate | κ | 275 | **0.321** | fair |

- 여섯 가지 모두 slight 또는 fair에 머물고 moderate(0.41 이상)에 닿는 항목이 하나도 없다. 최고가 PMN 침윤 0.321, 최저가 유사분열 0.152다.
- n=275는 코호트 하나당 패치 수다. PAM50 125장과 IHC 150장을 더한 값이며, 두 코호트를 합친 550장이 아니다. 원문은 "the same set of 275 representative patches"라고만 적어 어느 코호트인지 밝히지 않으므로, 코호트 귀속은 `판독 불확실`로 남긴다.
- `해석:` B̃는 이 여섯 특징에서 유도되는데 그 여섯이 전부 낮은 일치도 위에 서 있다. B̃가 다변량에서 탈락한 것(ΔR²<0.001)을 두고 "형태 분리도는 중요하지 않다"고 읽으면 위험하다. 측정 잡음이 커서 신호가 희석된 경우와 구분되지 않기 때문이다. 저자들도 한계 절에서 같은 취지를 인정한다.

## 한계 (원문 Limitations 절 전체)

저자들이 든 항목은 넷이다.

1. **냉동 조직 한정**. TCGA·CPTAC 모두 flash-frozen으로 제한해 임상에서 흔한 FFPE로 일반화되지 않는다. 확인한 공변량 요인이 FFPE 코호트의 시프트 원인을 다 담지 못할 수 있다.
2. **FM 목록의 시점 한계와 선택 절차**. 2025년 초 공개된 FM(H-optimus-1 등)은 가중치를 구할 수 없어 빠졌다. 또한 FM 선택을 baseline CLAM 하나로 했으므로, 최적화된 MIL 구성에서는 순위가 달라질 수 있다. Ma et al.이 독립적으로 Virchow v2 우위를 보고한 점이 이 우려를 부분적으로 덜어 준다고 적는다.
3. **회귀의 표본 크기**. 클래스 11개뿐이라 탐색적이다. PAM50과 IHC를 과제 유형 공변량 없이 합쳤고, 요인이 과제와 무관한 클래스 수준 기전으로 작동한다는 가정은 검증되지 않았다. 결과는 가설 생성으로 읽어야 한다.
4. **병리 주석의 불확실성**. 병리학자 두 명 사이의 일치도가 낮고(κw 0.152~0.289, κ 0.177~0.321) 클래스당 패치가 25개뿐이라 B̃의 견고성이 떨어진다. 저자들은 통상 조직학적 등급 매기기보다 이 주석 과제가 훨씬 주관적이라고 변호하면서도, B̃와 RPD의 단변량 연관을 해석할 때 고려할 불확실성이라고 인정한다.

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

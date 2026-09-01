# Fernandez-Romero 2026 vs BIOP02 Paper C — 정면 대조

> 작성 2026-09-02. 그들 쪽 수치는 `sources/fernandez-romero-2026-domaingen_pmc.xml`(Table 1·2·3)에서, 우리 쪽 수치는 아래 명시한 결과 파일에서 그대로 옮겼다. 추정한 값은 없고, 나눗셈으로 만든 값은 `계산값:`으로 표시한다.
>
> **출처 (우리 쪽)**
> - `experiments/sjpark/{er,pr,her2}_status_clam_uni_v2/{metrics.json, ext_eval_summary.json}`
> - `experiments/sjpark/pam50_clam_mb_uni_v1/{metrics.json, ext_eval_summary.json}`
> - `experiments/sjpark/pam50_clam_mb_uni_v1_4class/{metrics.json, ext_eval_summary.json}`
> - 분할 정의: `agents/data/split_policy_v0.md`(LOCKED 2026-07-11, Critic cross-sign 2026-07-13), `agents/data/manifests/split_manifest_meta.json`(split_hash `5995f29d3978b831`)
> - 라우팅·보정 붕괴: `experiments/crosscancer/PROGRESS_DECISIONS.md`

## 1. 설계 대조표

| 축 | Fernandez-Romero 2026 | BIOP02 Paper C |
|---|---|---|
| 내부 코호트 | TCGA-BRCA 냉동만, 1,522 슬라이드 / 1,079 환자 | TCGA-BRCA 진단 슬라이드, 1,010 환자 |
| 외부 코호트 | CPTAC-BRCA 387 슬라이드 / 120 환자 | CPTAC-BRCA(전량 hold-out) |
| 내부 분할 | 환자 층화 Monte Carlo CV, 무작위 10회, 80/10/10 | 환자 + **기관(TSS) disjoint**, 사전 고정 1회, 707/152/151 환자 (16/10/11 사이트) |
| 기관 통제 | 없음(`tissue source site`·`submitter`·`batch`·`scanner` 각 0회) | Howard PreservedSiteCV(QP 클래스 균형), fallback은 site-grouped greedy |
| 분할 잠금 | 없음(매 반복 무작위 재분할) | split_hash를 모든 `metrics.json`에 각인, sign-off 후 동결 |
| FM | 13종 비교, 최종 Virchow v2 | UNI v1 |
| MIL | CLAM, TransMIL, DSMIL(Optuna 튜닝) | CLAM-SB(ER/PR/HER2), CLAM-MB(PAM50) |
| 지표 | PAM50 macro-F1, IHC PR-AUC (AUROC 0회) | AUROC 주 지표, AUPRC·balanced accuracy 병기 |
| 열화 지표 | RPD = (CV − HO)/CV | 상대 낙폭을 별도 정의하지 않음(아래는 우리가 계산한 참고치) |
| 결정 층위 | 없음 | 라우팅 비용, 보정, 기권 |

## 2. 수치 대조

### 2-1. 그들 (Table 1, baseline CLAM, Virchow v2)

| 엔드포인트 | 지표 | 내부(MCCV) | 외부(HO) | 계산값: 상대 낙폭 |
|---|---|---|---|---|
| PAM50 5-class | macro-F1 | 0.542 | 0.358 | 0.339 |
| ER | PR-AUC | 0.972 | 0.916 | 0.058 |
| PR | PR-AUC | 0.874 | 0.862 | 0.014 |
| HER2 | PR-AUC | 0.399 | 0.219 | 0.451 |

참고로 우리가 쓰는 encoder 계열: UNI는 HER2 0.396 → 0.148(계산값 0.626), UNI-2는 0.353 → 0.164(계산값 0.535). 13종 중 최고 모형이 Virchow v2라는 것이지, 어느 것도 외부 HER2를 지키지 못한다.

### 2-2. 그들 (Table 2, 최적화 MIL 3종 평균의 클래스별 RPD)

| 클래스 | RPD |
|---|---|
| HER2-enriched | **1.000** |
| Normal-like | 0.906 |
| Luminal B | 0.644 |
| HER2-positive (IHC) | 0.643 |
| Basal-like | 0.219 |
| Luminal A | 0.166 |
| PR-negative | 0.163 |
| PR-positive | 0.161 |
| ER-positive | 0.093 |
| ER-negative | 0.063 |
| HER2-negative | 0.021 |

### 2-3. 우리 (UNI v1 + CLAM, 사전등록 site-disjoint 분할, AUROC)

| 엔드포인트 | 내부 홀드아웃 | CPTAC 외부 | n(외부) | 계산값: 상대 낙폭 |
|---|---|---|---|---|
| ER | 0.9013 | 0.894 | 387 | +0.008 |
| PR | 0.7765 | 0.7776 | 375 | −0.001 |
| HER2 | 0.5992 | 0.5297 | 294 | +0.116 |
| PAM50 5-class | 0.7589 | 0.7216 | 395 | +0.049 |
| PAM50 4-class | 0.8053 | 0.8181 | 382 | −0.016 |

- 95% CI(외부): ER 0.861–0.926, PR 0.729–0.825, HER2 0.440–0.619, PAM50 5-class 0.678–0.767, PAM50 4-class 0.788–0.854.
- PAM50 4-class는 split_policy_v0 §4에 따라 Normal-like 13건을 제외한 평가다.
- **경고**: 이 상대 낙폭은 AUROC 기반이라 그들의 RPD(macro-F1·PR-AUC 기반)와 같은 양이 아니다. 나란히 두는 것은 방향 비교까지이고, 크기 비교로 쓰면 안 된다.

## 3. 다뤄야 할 논점 네 가지

### 3-1. 내부 수치의 성격이 다르다

그들의 내부 성능은 환자만 층화한 무작위 분할에서 나온다. 원문 문장이 통제 범위를 명확히 한다.

> "Patient-level stratification ensured that all slides from the same patient remained in the same fold, preventing data leakage."

우리 내부 성능은 기관을 fold 사이에서 분리한 사전 고정 분할에서 나온다. 근거는 Howard 2021이 보고한 기관 서명이고, 분할은 2026-07-11에 잠근 뒤 모든 실행의 `metrics.json`에 해시로 각인했다.

따라서 두 논문의 "내부 숫자"는 같은 이름이 붙었을 뿐 서로 다른 조건에서 얻은 값이다. 우리 원고는 이 차이를 먼저 밝히고 나서 비교를 시작해야 한다.

### 3-2. 외부에서 판별력이 보존되는 정도가 다르다 (원인은 가설)

- **사실**: 그들은 CPTAC에서 심각한 열화를 보고한다. HER2-enriched는 RPD=1.000으로 완전히 무너지고 Normal-like 0.906, Luminal B 0.644다.
- **사실**: 우리 CPTAC 결과에서 판별력은 대체로 보존된다. ER 0.9013 → 0.894, PR 0.7765 → 0.7776, PAM50 5-class 0.7589 → 0.7216, 4-class 0.8053 → 0.8181.
- **사실**: 그들은 내부 분할에서 기관을 통제하지 않았다.
- **가설(우리 추론이며 검증되지 않음)**: 기관을 통제하지 않은 내부 분할은 기관 서명을 fold를 가로질러 남겨 내부 성능을 위로 밀어 올릴 수 있고, RPD의 분모가 커진 만큼 낙폭이 커 보일 수 있다. 우리 쪽 낙폭이 작은 것은 내부 성능이 이미 기관을 넘은 조건에서 측정되었기 때문일 수 있다.
- **가설을 단정으로 바꾸지 않기 위한 조건**: 그들이 기관 분리 분할로 내부 성능을 다시 재는 실험을 하지 않았으므로, 위 설명은 검정되지 않은 후보다. 지표(macro-F1·PR-AUC 대 AUROC), FM(Virchow v2 대 UNI v1), 슬라이드 포함 기준도 함께 다르다. 원고에는 "설계 차이가 낙폭 차이의 한 가지 설명이 될 수 있다"는 수준으로 적고, 원인 규명은 후속 과제로 남긴다.

### 3-3. 판별력 보존과 결정 안전성 붕괴의 해리 (우리 프레임의 핵심)

우리 쪽 판별력이 보존된다는 사실이 "CPTAC에서 잘 돌아간다"를 뜻하지 않는다. 라우팅과 보정 층은 무너졌다.

`experiments/crosscancer/PROGRESS_DECISIONS.md` 기록:

- CPTAC에서 예측이 다수 클래스로 붕괴한다. 항HER2 예측이 0%이고 ER은 과다 호출된다.
- 그 결과로 나온 endocrine 5% / chemo 73%라는 "반전"은 모델의 실력이 아니라 붕괴의 산물이다.
- 원문 기록 그대로: "raw AUROC(0.9)가 숨긴 miscalibration을 cost가 축별로 드러냄(방법론 기여)".

여기서 나오는 것이 cost-of-substitution 프레임의 근거다. 판별력(순위를 매기는 능력)과 결정 안전성(그 순위를 임계값 위에 올려 치료를 배정하는 능력)은 같이 움직이지 않는다. AUROC가 0.9여도 배치된 분류기가 한 클래스로 쏠리면 라우팅은 전량 오배정이 된다. 정확도 한 축만 재는 논문은 이 실패 양식을 볼 수 없고, 그들의 지표 체계(macro-F1·PR-AUC)도 마찬가지다.

곧 우리 기여는 "우리 예측이 더 잘 버틴다"가 아니라 **"예측 충실도와 결정 가치는 분리해서 재야 한다"**이다. 두 층을 하나의 비용 숫자로 합치지 않는 규율이 여기서 나온다.

### 3-4. HER2는 양쪽 다 실패한다 (수렴 증거)

| | 그들 | 우리 |
|---|---|---|
| HER2-enriched(PAM50) | RPD = 1.000 | 별도 클래스 지표 미산출 |
| HER2 수용체 상태 | 내부 PR-AUC 0.399 → 외부 0.219, RPD(클래스 평균) 0.643 | 내부 AUROC 0.5992 → 외부 0.5297 |
| 외부 CI | 원문 미제공 | 0.440–0.619 (우연 수준 0.5를 포함) |
| 외부 balanced accuracy | 원문 미확인 | 0.500 (정확히 우연) |

- 분할 설계가 다르고, FM이 다르고(Virchow v2 대 UNI v1), 지표가 다른데도 HER2 축은 양쪽 모두에서 쓸 수 없는 수준이다.
- 우리 쪽은 **내부에서 이미 0.599**다. 곧 이것은 도메인 시프트만의 문제가 아니라 H&E 형태에서 HER2를 읽어 내는 일 자체의 한계로 보는 편이 자연스럽다. 그들 Table 1에서도 13개 FM 전부 내부 HER2 PR-AUC가 0.25~0.40에 머문다는 사실이 같은 방향을 가리킨다.
- 원고에서는 이를 독립 재현으로 서술한다. 서로 다른 방법 선택에서 같은 실패가 나왔으므로 방법 의존적 결함이 아니다.
- 다만 구분해 두어야 할 것이 있다. **전량 붕괴(도메인·보정 문제, 고칠 수 있음)와 HER2 내재적 형태 blind(0.599, 고쳐지지 않음)는 다른 현상**이다. `PROGRESS_DECISIONS.md`도 이 구분을 명시한다.

## 4. 원고 문장으로 옮길 때의 규율

- 우리 내부 수치가 그들보다 "낮다/높다"로 말하지 않는다. 지표와 분할이 달라 비교 대상이 아니다.
- 우리 낙폭이 작다는 사실을 우리 방법의 우월성 주장으로 쓰지 않는다. 분할 설계가 후보 설명이라는 가설까지만 적는다.
- 그들의 열화 결과는 우리 논지를 지지하는 외부 근거로 인용한다. 예측만으로는 배치가 취약하므로 치환에는 계량 가능한 비용이 따르고 보정과 기권이 필요하다는 SUBSTITUTABILITY_LAW의 근거다.
- 우리 쪽 라우팅 붕괴를 숨기지 않는다. 판별력 보존과 결정 안전성 붕괴가 함께 있다는 것이 우리 프레임의 존재 이유이므로, 붕괴 사실이 결과인 동시에 caveat다.
- 모든 우리 산출물은 `hypothesis_only`를 유지하고 Critic 통과 전에는 공유하지 않는다.

## 5. 열린 항목

- `원문 미확인:` 그들의 아키텍처별 클래스별 내부·외부 절대 성능(Table S4)은 Supplementary PDF에 있고 이 폴더에 없다. 클래스 단위 절대값 비교가 필요하면 따로 받아야 한다.
- 우리 쪽 클래스별(PAM50 아형별) 내부·외부 성능과 macro-F1·PR-AUC 재계산은 아직 하지 않았다. 하면 그들 Table 2와 같은 자에 올릴 수 있으나, 헤드라인이 예측 정확도로 되돌아갈 위험이 있어 보조 표로만 검토한다.
- 그들이 통제하지 않은 기관 효과의 크기를 우리 데이터에서 역으로 추정하는 실험(기관 통제 분할과 무작위 분할의 내부 성능 차이 측정)은 아직 계획 단계다. 이것이 3-2의 가설을 사실로 바꿀 수 있는 가장 값싼 경로다.

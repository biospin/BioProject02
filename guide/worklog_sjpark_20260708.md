# 작업일지 — sjpark (박세진) | 2026-07-08

Sprint 3 (BIOP02-53) | Self-critic 2회차 — 방법론 오류 발견 및 정정

---

## 배경

전날(7/7) BIOP02-53의 self-critic 1회차를 수행하고 4개 항목(HER2/PAM50 baseline, CLAM bootstrap CI, counterfactual 실험, HER2 CPTAC 분포)을 처리했다. 오늘은 그 결과물 자체를 다시 검증하는 2회차 self-critic을 수행했다.

**핵심 질문:** "어제 고친 것들 자체에 새로운 공백은 없는가?"

---

## 2회차 self-critic에서 발견한 4개 문제

### 1. Patient-level leakage — 검증 없이 인용만 함

지금까지 "site-disjoint split"이라는 kkkim의 주장을 그대로 인용만 했지, train/val/test 간 환자(case_id) 중복 여부를 직접 확인한 적이 없었다.

### 2. "우위/유의성" 판정이 통계적 근거 없이 눈짐작이었음

CLAM vs subtype_only baseline을 비교할 때 두 모델의 95% CI가 겹치는지 눈으로만 보고 "subtype_only 우위"라고 판정했다. 두 모델이 **같은 val set**에서 나온 예측이므로 paired test가 필요한데 이를 하지 않았다.

### 3. Counterfactual 실험이 PAM50에 적용되지 않음

`counterfactual_attention.py`가 이진분류 CLAM-SB 전용이라 CLAM-MB(PAM50, 5-class)는 검증에서 빠져 있었다.

### 4. CPTAC 외부검증 원본 예측값 미저장

전날 "개선 필요"로만 기록해두고 실제로 고치지 않았던 항목. CPTAC AUC에 CI가 전혀 없는 상태가 그대로였다.

---

## 처리 내역

### ① Patient-level leakage 직접 검증

train/val/test 각 split의 고유 `case_id` 집합을 만들어 교집합을 계산했다.

```
test ∩ val:   0명
test ∩ train: 0명
val ∩ train:  0명
```

전체 1010명 = 1010슬라이드로 1인 1슬라이드 구조임도 함께 확인했다. 5분짜리 검증이었지만, 지금까지 인용만 하던 주장에 처음으로 직접 근거를 붙인 작업이었다.

---

### ② CPTAC 외부검증 원본 예측값 저장 + bootstrap CI

`eval_external.py`를 새로 작성해 재학습 없이 기존 `model.pt`로 CPTAC 전체를 재추론하고, 원본 proba/pred/label을 `predictions_ext.npy`로 저장한 뒤 bootstrap CI를 계산했다.

| 태스크 | CPTAC AUC | CI 95% |
|---|---|---|
| ER | 0.894 | [0.861, 0.926] |
| PR | 0.778 | [0.729, 0.825] |
| HER2 | 0.530 | [0.440, 0.619] — **0.5 포함, 유의성 없음** |

HER2의 CPTAC CI가 0.5를 포함한다는 것은 TCGA 결과([0.483, 0.711])와 일관되게, CLAM-SB HER2 모델이 random과 통계적으로 구별되지 않는다는 뜻이다.

---

### ③ PAM50 CLAM-MB counterfactual 실험

`counterfactual_attention_mb.py`를 새로 작성했다. CLAM-MB는 클래스별로 독립된 attention branch를 가지므로, 각 슬라이드의 **예측 클래스에 해당하는 branch**의 top-attention 타일을 기준으로 제거 실험을 설계했다.

```
Mean |Δproba| top    = 0.0248
Mean |Δproba| random = 0.0017   (약 15배 차이)
Faithfulness confirmed: True
```

ER(20배)·PR(20배)·HER2(10배)와 같은 방향의 결과로, PAM50에서도 attention이 장식적이지 않음을 확인했다.

---

### ④ CLAM vs subtype_only paired bootstrap 유의성 검정 — 가장 중요한 정정

`paired_significance_test.py`를 작성해 같은 val set 인덱스로 CLAM과 subtype_only를 동시에 리샘플링하고, AUC 차이(`CLAM − subtype_only`)의 분포로 직접 검정했다.

**결과:**

| 태스크 | 차이 | 95% CI | p-value(근사) | 결론 |
|---|---|---|---|---|
| ER | -0.0177 | [-0.088, 0.045] | 0.613 | **유의한 차이 없음** |
| PR | -0.0331 | [-0.106, 0.038] | 0.358 | **유의한 차이 없음** |
| HER2 | -0.1232 | [-0.230, -0.015] | 0.024 | subtype_only 유의하게 우수 |

### 정정한 내용

7/7 self-critic 1회차 JIRA 댓글에서 "ER/PR/HER2 모두 subtype_only가 CLAM보다 우위"라고 판정했었다. 이는 각 모델의 CI를 따로 구해서 겹치는지 눈으로 비교한 것이었는데, **paired 상황에서는 이 방법이 부정확하다.** 개별 CI가 겹쳐 보여도 paired 차이의 CI는 0을 포함하지 않을 수 있고(반대로 개별 CI가 안 겹쳐 보여도 paired 차이는 유의하지 않을 수 있다), 실제로 ER과 PR에서 그런 경우였다.

**정정 후 결론:** ER과 PR은 CLAM이 subtype_only에 뒤진다고 말할 통계적 근거가 없다. HER2만 subtype_only가 진짜로 유의하게 우수하다.

이 정정을 BIOP02-53 JIRA에 명시적으로 남기고 이전 판정을 철회했다.

---

## 커밋 이력

| 커밋 | 내용 |
|---|---|
| `7b23b67` | leakage 직접검증 + CPTAC CI + PAM50 counterfactual + paired 유의성검정 |

새로 작성한 스크립트 3개:
- `eval_external.py` — 학습된 모델을 재학습 없이 외부 데이터셋에 재추론 + CI
- `counterfactual_attention_mb.py` — CLAM-MB(multiclass) counterfactual 실험
- `paired_significance_test.py` — paired bootstrap 유의성 검정

---

## Lesson Learned

### CI 겹침 눈짐작은 방법론적 오류다

두 모델이 **동일한 데이터셋**에서 나온 예측일 때는 각자의 CI를 따로 구해 겹치는지 보는 방식(unpaired 비교)이 부정확하다. 같은 리샘플 인덱스로 두 모델을 동시에 평가해 차이의 분포를 직접 구하는 paired test를 써야 한다. 이 오류를 스스로 저지르고 스스로 잡아낸 경험 자체가, 왜 이 절차가 필요한지에 대한 가장 설득력 있는 근거가 됐다.

### self-critic도 반복해야 한다

1회차 self-critic에서 발견한 공백을 메웠다고 끝난 게 아니었다. 그 메운 결과물 자체를 다시 의심하는 2회차가 실제로 유의미한 오류(paired test 부재)를 찾아냈다. "고쳤다"와 "제대로 고쳤는지 다시 확인했다"는 다른 단계다.

### 재학습 없이도 검증을 확장할 수 있다

CPTAC 재추론이나 counterfactual 실험은 기존 `model.pt`를 그대로 불러와 추론만 다시 하는 방식으로 구현했다. 학습을 다시 돌리지 않고도 검증 커버리지를 넓힐 수 있다는 것을 실감했다.

---

## 다음 단계

| 항목 | 상태 |
|---|---|
| Patient-level leakage | ✅ 완료 |
| CPTAC bootstrap CI | ✅ 완료 |
| PAM50 counterfactual | ✅ 완료 |
| Paired 유의성 검정 | ✅ 완료 (판정 정정 포함) |
| jamie 공식 CPTAC 라벨 (BIOP02-55) | ⏳ 대기 중 |
| Biological plausibility (#5, jhans 이관) | ⏳ 대기 중 |
| Paper A Methods 서술 방향 수정 | 필요 — "H&E가 subtype 상관관계를 넘어선다"고 과장하지 않되 "뒤진다"고도 말하지 않는 중립적 서술 |

critic_status는 여전히 `caution`이지만, 남은 블로커가 명확해졌다: 공식 CPTAC 라벨과 jhans 생물학적 타당성 검토 두 가지뿐이다.

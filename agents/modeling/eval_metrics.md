# Evaluation Metrics — SpatialPathoAgent Modeling

> 적용 범위: 모든 이진 phenotype 예측 태스크 (ER / PR / HER2 status)  
> 기준 버전: v0.1 (2026-05-29, sjpark)

---

## 1. AUC (Area Under the ROC Curve)

**정의:** 임계값(threshold)과 무관하게 모델이 양성(positive)을 음성(negative)보다 높게 랭킹할 확률.

$$\text{AUC} = P(\hat{p}_{\text{pos}} > \hat{p}_{\text{neg}})$$

- **범위:** 0.5 (random) ~ 1.0 (perfect)
- **사용 이유:** 클래스 불균형에 강건하며, 임계값 선택과 독립적
- **구현:** `sklearn.metrics.roc_auc_score(y_true, y_score)`
- **보고 기준:** val set 기준, 소수점 4자리

---

## 2. AUPRC (Area Under the Precision-Recall Curve)

**정의:** Precision-Recall 곡선 아래 면적. 양성 클래스 예측 성능에 집중.

$$\text{AUPRC} = \sum_k (R_k - R_{k-1}) \cdot P_k$$

- **범위:** 양성 비율(baseline) ~ 1.0 (perfect)
- **사용 이유:** 양성 클래스가 희소한 경우(HER2+, BRCA mutation 등) AUC보다 민감
- **구현:** `sklearn.metrics.average_precision_score(y_true, y_score)`
- **보고 기준:** val set 기준, 소수점 4자리

---

## 3. Balanced Accuracy

**정의:** 클래스별 recall의 평균. 클래스 불균형 시 accuracy 대신 사용.

$$\text{Balanced Accuracy} = \frac{\text{Sensitivity} + \text{Specificity}}{2} = \frac{1}{2}\left(\frac{TP}{TP+FN} + \frac{TN}{TN+FP}\right)$$

- **범위:** 0.5 (random) ~ 1.0 (perfect)
- **사용 이유:** ER+ 비율이 ~70%인 TCGA-BRCA에서 단순 accuracy는 항상 양성 예측으로 편향됨
- **구현:** `sklearn.metrics.balanced_accuracy_score(y_true, y_pred)`
- **보고 기준:** threshold=0.5 적용 후 val set 기준, 소수점 4자리

---

## 4. metrics.json 필수 필드 요약

```json
{
  "auc": 0.0000,
  "auprc": 0.0000,
  "balanced_accuracy": 0.0000,
  "n_train": 0,
  "n_val": 0,
  "model": "SlideMLP",
  "embedding_model": "dummy | UNI | CONCH | ...",
  "commit_hash": "abc1234"
}
```

> `auc`, `auprc`, `balanced_accuracy`가 `null`인 경우 smoke test 결과로 간주.  
> 실험 결과 공유(`#biop02-experiments`)는 세 값이 모두 채워진 경우에만 가능.

---

## 5. Trivial Baseline 기준선 (ER status 기준)

| Baseline | 예상 AUC | 예상 AUPRC | 예상 Balanced Acc |
|---|---|---|---|
| Random | ~0.50 | ~pos_rate | ~0.50 |
| Majority (항상 ER+) | 0.50 | ~0.70 | ~0.50 |
| Mean Embed (LR) | 0.55–0.65 | — | — |

> MLP 모델은 반드시 Mean Embed baseline을 상회해야 실험 결과로 인정.

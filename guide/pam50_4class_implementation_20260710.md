# PAM50 4-class 구현 및 결과 정리 (§4 준수)

> 작성 sjpark · 2026-07-10
> 배경: braveji Critic 지적(BIOP02-56) — PAM50가 split_policy §4 위반(Normal 포함 5-class 학습)
> 조치: §4 준수 4-class(Normal 제외) 재실행, 기존 5-class는 덮어쓰지 않고 별도 보존

---

## 1. 4-class로 만든 방식

### 정책 근거
`split_policy_v0.md` §4: **PAM50 = 4-class (LumA / LumB / Basal / HER2)**, Normal-like는 제외
(형태학 신호 빈약, Tafavvoghi 정렬). 기존 5-class(Normal 포함)는 정책 위반.

### 구현 — 라벨 매핑에서 Normal을 제외
핵심은 별도 필터링 코드가 아니라 **라벨 매핑 딕셔너리에서 Normal을 빼는 것**이다.
로더는 `label not in map`이면 스킵하므로, 4-class 맵을 쓰면 Normal/Normal-like 슬라이드가
자동으로 제외된다.

```python
# agents/modeling/scripts/train_mil.py
PAM50_MAP_5 = {"luma":0, "lumb":1, "basal":2, "her2":3, "normal":4, "normal-like":4}
PAM50_MAP_4 = {"luma":0, "lumb":1, "basal":2, "her2":3}   # §4 준수: Normal 제외
def pam50_map(num_classes):     return PAM50_MAP_4 if num_classes == 4 else PAM50_MAP_5
def pam50_classes(num_classes): return PAM50_CLASSES_4 if num_classes == 4 else PAM50_CLASSES_5
```

- **스위칭 단일 소스 = config의 `num_classes`.** `baseline_pam50_clam_4class.yaml`에 `num_classes: 4`만
  지정하면 4-class 맵·클래스명(LumA/LumB/Basal/HER2)이 자동 선택된다.
- **기본 5-class 동작 불변**(기본값 5). 같은 스크립트로 두 버전이 공존 → 재현성 보존.
- 동일 방식을 `run_baselines_pam50.py`(`--num_classes`), `counterfactual_attention_mb.py`에도 적용.

### 제외 검증 (정합 확인)
| split | 5-class | Normal 제외 | 4-class |
|---|---|---|---|
| train | 707 | −79 | **628** |
| val | 151 | −28 | **123** |
| CPTAC 외부 | 395 | −13 | **382** |

train Normal 79 / val 28 / test 20, CPTAC 13건 제외 — `n_train`·`n_val`·`ext_n_test`와 모두 정합.

---

## 2. 결과 정리 방식

기존 5-class(`experiments/sjpark/pam50_clam_mb_uni_v1/`)를 **덮어쓰지 않고**,
4-class를 별도 디렉토리 `experiments/sjpark/pam50_clam_mb_uni_v1_4class/`로 병렬 산출.

### 4-class 핵심 수치
| 지표 | 값 |
|---|---|
| num_classes / class_names | 4 / LumA·LumB·Basal·HER2 |
| n_train / n_val | 628 / 123 |
| 내부 macro-AUC | 0.805 [0.750, 0.862] |
| 외부(CPTAC) macro-AUC | 0.818 [0.788, 0.854], n_test=382 |
| mean_embed 외부 | 0.653 |
| paired diff (CLAM − mean_embed, 외부) | +0.165, CI [0.122, 0.206], p≈0 |
| label-shuffle null (외부, 5-seed) | [0.43, 0.57] → real 0.818 훨씬 위 |
| 판정 | **GENUINE** (null 위 + baseline 유의 상회) |

### 산출 아티팩트
| 파일 | 내용 |
|---|---|
| metrics.json | 4-class 지표 + auc_ci_95 / ext_auc_ci_95 / ext_n_test / ext_normal_like_excluded |
| ext_eval_summary.json | 외부검증 요약 |
| critic_report.json | 5-artifact 규칙 충족(판정 status는 pending, 최종 sign-off는 braveji) |
| paired_significance_internal/external.json | CLAM-MB vs mean_embed 유의성 |
| label_shuffle_null.json | 5-seed shuffle null (GENUINE 판정 근거) |
| counterfactual/ | attention faithfulness |
| predictions.npz / predictions_ext.npz | 내부/외부 예측 |
| `pam50_uni_v1_4class_baselines/trivial_baselines.json` | random·majority·mean_embed 4-class |
| `pam50_4class_vs_5class.json` | 4 vs 5-class 대조 + 비교 무효 주장 철회 기록 |
| Fig4 PAM50 패널 | 4-class로 갱신(정책 준수본) |

---

## 3. 중요 — 비교 주장 정정 (Critic 기각 수용)

처음 비교표 결론은 "4-class가 5-class보다 더 강하다(0.722→0.818 상승)"였으나,
braveji가 **기각**: 4-class와 5-class macro-AUC는 라벨 공간·표본이 달라 직접 비교 불가.
가장 어려운 Normal을 macro 평균에서 빼면 모델 개선 없이도 AUC가 기계적으로 상승.

→ 해당 주장을 모두 철회하고 `pam50_4class_vs_5class.json`의 `critic_correction` 필드에 명시.
**현재 유효한 주장**: 4-class는 §4 준수본이며, *자기 라벨 공간 안에서* CLAM-MB가 trivial baseline을
유의하게 상회 + shuffle null 위 = GENUINE. **버전 간 우열 비교는 하지 않는다.**

---

## 4. 남은 것 (sign-off 블로커, 전부 kkkim)

- split_policy_v0 lock (Critic #1)
- PAM50 라벨 소스 study_id 확정 (BIOP02-38, §139 단일소스)
- 이후 braveji가 registry(BIOP02-57)에 append: 5-class caution→reject+superseded, 4-class 신규 cv-20260710

---

*관련: BIOP02-56(Critic §4), BIOP02-57(registry), BIOP02-53(외부검증). 커밋 c938ff4·33d0629·fc07e5c.*

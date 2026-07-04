# SpatialPathoAgent Scientific Critic Checklist v1

> Critic 총괄: braveji (ykji) | 바이오 sub-check (#4/#5): sjpark / jhans  
> 모든 실험 결과는 이 체크리스트를 통과한 후에만 `#biop02-experiments`에 공유 가능.  
> Owner ≠ Reviewer 원칙 필수 준수.

---

## 사용 방법

1. `experiments/<username>/<date>/critic_report.json` 파일을 `schemas/critic_report.schema.json`에 맞게 작성
2. 아래 7개 항목을 순서대로 검토
3. 각 항목 결과를 `pass` / `caution` / `reject`로 기재
4. 하나라도 `reject`면 전체 `critic_status: reject`
5. `caution`이 있으면 `required_followups`에 구체적 후속 조치 명시 후 `caution` 가능

---

## 체크리스트 7항목

---

### #1 Data Leakage Check

**목적:** 환자 정보가 train/val/test 경계를 넘는지 확인

**확인 항목:**

- [ ] `split_policy_v0.md` 기준: train ∩ val ∩ test (by `case_id`) == 0
- [ ] 타일/슬라이드 단위가 아닌 **환자(`case_id`) 단위**로 분리됐는지 확인
  ```python
  # 필수 assert — build_manifest.py 또는 학습 직전 실행
  assert len(set(train_ids) & set(val_ids)) == 0
  assert len(set(train_ids) & set(test_ids)) == 0
  ```
- [ ] TCGA TSS site-disjoint split 적용 여부 (Howard 2021 기준)
  - train site ∩ val/test site == 0 (권장) 또는 site leakage 정량화 필수
  - `site_classifier_probe.py` 실행 결과 AUC < 0.65면 pass, ≥ 0.65면 caution/reject
- [ ] CPTAC-BRCA는 학습/튜닝에 일절 미노출 (external hold-out only)
- [ ] 라벨(ER/PR/HER2/PAM50)이 split 이전에 표준화됐는지 확인

**필수 근거 (evidence):**

- `split_policy_v0.md`의 lock 해시 또는 서명 여부
- patient-overlap assert 통과 로그
- site_classifier_probe.py 출력 AUC 수치

**판정 기준:**

| 결과 | 판정 |
|---|---|
| patient overlap == 0 + site AUC < 0.65 | pass |
| patient overlap == 0 + site AUC 0.65–0.75 | caution (사이트 보정 검토) |
| patient overlap > 0 OR site AUC ≥ 0.75 | reject |

---

### #2 Baseline Comparison

**목적:** 모델이 의미 없는 trivial baseline을 충분히 이기는지 확인

**필수 baseline 3종 (BIOP02-40 기준):**

| Baseline | 설명 | 참고 AUC |
|---|---|---|
| Random | 레이블 분포에 따른 무작위 예측 | ~0.50 |
| Subtype-only | IHC 서브타입 one-hot 피처만 사용 | 태스크별 상이 |
| Pixel-mean | 슬라이드 픽셀 평균값만 사용 | ~0.50–0.60 |

**확인 항목:**

- [ ] 위 3종 baseline AUC/AUPRC가 `experiments/sjpark/*/metrics.json`에 존재
- [ ] 제출 모델이 **모든 baseline을 AUC 기준 +0.03 이상** 상회
- [ ] AUPRC도 subtype-only baseline 이상 (불균형 데이터 필수)
- [ ] bootstrap 95% CI가 baseline과 겹치지 않는지 확인
  ```python
  # bootstrap CI 확인
  assert model_auc_lower > max_baseline_auc_upper, "CI overlap → caution"
  ```

**판정 기준:**

| 결과 | 판정 |
|---|---|
| 모든 baseline +0.03↑ + CI 비겹침 | pass |
| baseline +0.01~0.03 OR CI 겹침 | caution |
| baseline 미달 OR baseline 수치 누락 | reject |

---

### #3 Counterfactual Check

**목적:** 모델이 실제 형태학적 피처를 사용하는지, 아니면 confound에 의존하는지 확인

**확인 항목:**

- [ ] **주요 피처 ablation**: 임베딩 top-k attention patch 제거 시 AUC 유의미하게 하락하는지
  - CLAM-SB: attention score 상위 10% 타일 마스킹 → AUC 변화 확인
  - MLP: PCA top-k 차원 0으로 설정 → AUC 변화 확인
- [ ] **라벨 셔플 테스트**: 학습 라벨을 무작위 셔플 후 재학습 → AUC ≈ 0.5 확인
  - 셔플 후 AUC가 0.5보다 유의미하게 높으면 데이터 누수 의심
- [ ] **예측 순위 변화**: 주요 피처 제거 시 top-ranked 샘플이 달라지는지

**판정 기준:**

| 결과 | 판정 |
|---|---|
| ablation AUC ↓ + 셔플 AUC ≈ 0.5 | pass |
| ablation 결과 없으나 셔플 pass | caution (ablation 추가 권고) |
| 셔플 후 AUC > 0.55 | reject (누수 의심) |

---

### #4 Cross-Dataset Check

**목적:** DepMap PRISM ↔ GDSC 결과 일관성 확인 (Therapeutic Evidence Agent 산출물에 적용)  
**담당:** braveji 총괄, 생물학적 일관성 sub-check → sjpark

> Paper A (표현형 예측) 단계에서는 해당 없음 → `not_applicable` 가능.  
> Paper B (DepMap/GDSC 전이) 단계부터 필수.

**확인 항목 (Paper B 적용 시):**

- [ ] 동일 약물에 대해 PRISM sensitivity ranking ↔ GDSC IC50 ranking 스피어만 상관 ≥ 0.4
- [ ] PRISM에만 있거나 GDSC에만 있는 약물 처리 방식 명시
- [ ] 세포주 ↔ 환자 전이 시 분포 shift 정량화 (UMAP 또는 domain distance)
- [ ] 결과가 한 데이터셋에서만 유효하면 `caution` 이상

---

### #5 Biological Plausibility

**목적:** 예측된 표현형-약물 연결이 알려진 생물학적 메커니즘과 일치하는지 확인  
**담당:** braveji 총괄, sub-check → sjpark (pathway 분석) / jhans (DepMap/GDSC 연결)

**확인 항목:**

- [ ] ER+ 예측 → Tamoxifen/Fulvestrant 감수성 높음 (문헌 일치)
- [ ] HER2+ 예측 → Trastuzumab/Lapatinib 감수성 높음 (문헌 일치)
- [ ] PAM50 Basal-like → PARP inhibitor 감수성 (BRCA1/2 pathway)
- [ ] **절대 금지**: ICI (Pembrolizumab 등) cell-line transfer 추천 → `reject`
- [ ] pathway-drug 연결 출처 명시 (OncoKB / ReactomeDB / DGIdb 중 하나 이상)
- [ ] 생물학적으로 설명 불가능한 연결이 top-5 안에 포함되면 `caution`

**판정 기준:**

| 결과 | 판정 |
|---|---|
| 주요 표현형-약물 연결 문헌 일치 + 출처 명시 | pass |
| 일부 연결 불분명하나 top-3은 타당 | caution |
| 상위 연결이 문헌과 불일치 OR ICI 추천 포함 | reject |

---

### #6 DRP Framing Check

**목적:** "Drug Response Prediction" 표현이 산출물에 포함됐는지 확인

**확인 항목 (자동 grep 가능):**

```bash
# 실험 디렉토리에서 금지 표현 검색
grep -ri "drug response prediction\|personalized therapy\|patient-specific.*treatment\|optimal treatment" \
  experiments/ schemas/ agents/ --include="*.json" --include="*.md" --include="*.yaml"
```

- [ ] 위 grep 결과 == 0건
- [ ] `metrics.json`, `critic_report.json`의 `task` 필드가 `er_status` / `pr_status` / `her2_status` / `pam50` 중 하나
- [ ] `claim_level` 필드가 `hypothesis_only` (다른 값이면 즉시 `reject`)
- [ ] 보고서/슬라이드에 "예측"이 아닌 "가설 생성(hypothesis generation)" 표현 사용 확인

**판정 기준:**

| 결과 | 판정 |
|---|---|
| grep 0건 + claim_level == hypothesis_only | pass |
| 금지 표현 1건 이상 | reject (수정 후 재제출) |

---

### #7 Claim-Level Check

**목적:** 결과의 주장 수준이 근거에 비해 과도하지 않은지 확인

**확인 항목:**

- [ ] `claim_level: hypothesis_only` 명시
- [ ] 결과 해석이 "예측한다(predicts)"가 아닌 "시사한다(suggests)" / "가설을 제시한다" 수준
- [ ] 단일 코호트(TCGA-only) 결과를 일반화하지 않음
- [ ] 세포주 전이 결과는 "전임상 가설(preclinical hypothesis)"로만 표현
- [ ] 외부 검증(CPTAC) 없이 임상 연관성 주장 금지

**판정 기준:**

| 결과 | 판정 |
|---|---|
| hypothesis_only 명시 + 표현 수준 적절 | pass |
| 표현이 약간 과장됐으나 데이터 범위 내 | caution (표현 수정 후 caution) |
| "predicts clinical outcome" 류 표현 | reject |

---

## 최종 판정 규칙

```
모든 항목 pass                    → critic_status: pass
pass + caution(1개 이상), reject 없음 → critic_status: caution
reject 1개 이상                   → critic_status: reject
```

**`critic_status: pass` 또는 `caution`만 `#biop02-experiments` 공유 허용.**  
`reject`는 owner에게 피드백 후 수정·재실험·재제출.

---

## 서명란

```
Critic 총괄: braveji (ykji)   서명: _______________  날짜: ___________
바이오 sub-check (#4/#5):
  - sjpark (박세진)             서명: _______________  날짜: ___________
  - jhans (서정한)              서명: _______________  날짜: ___________
```

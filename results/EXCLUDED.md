# 원고 미반영 산출물 대장

> 실험 산출물 중 **원고에 싣지 않기로 한 것**과 그 사유를 남기는 파일임. 결과가 조용히 사라지는 것을 막는 것이 목적임.
> 배경 = `docs/PITFALLS_REGISTRY.md` A9·C11. CPTAC 외부검증 5종이 분석 완료 상태로 원고에 한 번도 반영되지 않은 채 두 달이 지났고, 어떤 게이트에도 걸리지 않았음.
> 검사기 = `agents/critic/scripts/check_result_coverage.py`. **`[제외확정]` 태그가 붙은 줄에 경로가 적힌 것만** 제외로 인정함. 태그 없이 적으면 게이트가 계속 잡음.

## 기재 규칙

- 한 항목에 **산출물 경로 · 제외 사유 · 근거 등급 · 재검토 조건 · 판정자**를 적음.
- 근거 등급: **E1** 전문·원자료 확인 / **E2** 요약·초록만 / **E3** 2차 인용. **E2 이하로는 제외를 확정하지 않음**(A9 재발 방지).
- 판정이 안 끝난 것은 §2에 두고 `[제외확정]`을 붙이지 않음. 게이트에서 계속 미분류로 뜨는 것이 정상임.

---

## 1. 제외 확정

| 산출물 | 사유 | 등급 | 재검토 조건 |
|---|---|---|---|
| `[제외확정]` `experiments/template/metrics.json` | 신규 실험용 빈 템플릿이며 실측 결과가 아님 | E1 | 없음 |
| `[제외확정]` `experiments/sjpark/immune_signature_dummy_v1/metrics.json` | 배선 점검용 더미 실행임. 파일명이 `dummy`이고 성능 지표 키가 없음 | E1 | 없음 |
| `[제외확정]` `experiments/crosscancer/LUNG_NSCLC/pilot/tiling_summary.json` | 타일링 전처리 집계이며 모델 성능이 아님. Methods 서술로 충분함 | E1 | 타일링 파라미터를 결과로 주장할 경우 |
| `[제외확정]` `experiments/crosscancer/LUNG_NSCLC/pilot/embedding_summary.json` | 임베딩 추출 집계이며 모델 성능이 아님. 위와 같음 | E1 | 위와 같음 |

---

## 2. 판정 대기 (제외 아님, 게이트에 계속 뜸)

### 2-1. 원고에 실어야 한다고 보는 것 — kkkim 의견

| 산출물 | 왜 실어야 하나 | 판정 필요 |
|---|---|---|
| `sjpark/{er,pr,her2}_status_clam_uni_v2/ext_eval_summary.json`, `sjpark/pam50_clam_mb_uni_v1{,_4class}/ext_eval_summary.json` | CPTAC 외부검증 5종. 원고 전체에 `ext_` 수치가 **하나도 없음**. 판별력은 보존되는데(ER 0.9013→0.894, PAM50 4-class 0.8053→0.8181) 라우팅·보정 층은 붕괴한다는 해리가 cost-of-substitution 프레임의 직접 근거임 | braveji (critic_status caution→pass), BIOP02-70 |
| `sjpark/{er,pr,her2}_status_clam_uni_v2_labelshuffle/metrics.json`, `sjpark/pam50_clam_mb_uni_v1_labelshuffle/metrics.json` | 라벨셔플 음성대조 4종. 라벨을 섞으면 우연 수준으로 내려감(ER ext 0.3501, PR ext 0.3664, HER2 0.4829, PAM50 ext 0.5393). 우리 양성 결과가 배선 산물이 아님을 보이는 방어 근거인데 원고에 없음 | 박세진 (결과 오너) |

### 2-2. 구버전으로 대체됐는지 확인이 필요한 것

| 산출물 | 잠정 판단 | 판정 필요 |
|---|---|---|
| `sjpark/er_status_uni_v1/metrics.json` (auc 0.8209) | Sprint 1 MLP 베이스라인이며 Sprint 3 CLAM(`er_status_clam_uni_v2`, auc 0.9013)으로 대체된 것으로 보임 | 박세진 |
| `sjpark/pr_status_uni_v1/metrics.json` (auc 0.7125) | 위와 같음 | 박세진 |
| `sjpark/pam50_uni_v1/metrics.json`, `pam50_uni_v2/metrics.json` (auc 0.7113) | 위와 같음 | 박세진 |
| `sjpark/her2_status_uni_v1/metrics.json` (auc 0.5509) | 위와 같음. 다만 HER2는 v1·v2 모두 우연 수준이라 방법 비의존성 근거로 쓸 여지가 있음 | 박세진 |

베이스라인을 비교 대상으로 본문에 남길지, Methods 한 줄로 줄일지가 갈림. **대체됐다는 이유만으로 지우면 "왜 CLAM을 썼나"의 근거가 사라짐.**

### 2-3. 아직 이른 것

| 산출물 | 상태 |
|---|---|
| `experiments/kkkim/20260830_encoder_ablation/metrics.json` (auc 0.8918) | BIOP02-149. PR #150이 2026-08-31 병합됨. `critic_status` v2 재검토 대기 중이라 원고 반영은 그 뒤 |
| `braveji/BIOP02-56_counterfactual_recompute/{pam50_4class,pr}/counterfactual_summary.json` | Critic #3 counterfactual 재계산. 원고 반영 범위를 braveji 판정에 맞춰야 함 |
| `experiments/kkkim/20260804_operating_point/label_quality_results.json` | 성능 지표 키가 없어 자동 판정 불가. 내용 확인 후 분류 |

---

## 3. 갱신 규칙

- 결과를 원고에서 빼기로 하면 **그 자리에서** 여기에 적음. 나중에 몰아 쓰면 사유가 날아감.
- 제외 확정으로 올릴 때는 근거 등급을 함께 적고, **E2 이하면 전문 확보 티켓을 먼저 만듦**.
- 판정이 끝난 항목은 §2에서 §1로 옮기거나 원고에 반영하고 이 표에서 지움.

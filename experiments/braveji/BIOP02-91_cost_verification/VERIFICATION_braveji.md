# Critic 검증 — cost-of-substitution receptor 라우팅 (BIOP02-91 / Fig 2·3 서명 근거)

**검증자:** braveji (Critic 총괄) · 2026-07-23 · owner=kkkim → **Owner≠Reviewer 충족**
**대상:** `experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost_receptor.json` (`critic_status: pending`) 및 이를 근거로 하는 **Fig 2·Fig 3**
**방법:** 원자료(`experiments/sjpark/cptac_ext_predictions_indexed.csv` + `/workspace/.../embedding_manifest_cptac_uni.csv`)에서 라우팅·비용·CI를 **독립 재계산**. env: spatialpatho(numpy 2.4.4).

---

## 1. 원자료 재현 — 전부 일치 ✅

라우팅 규칙(`HER2+>antiHER2; ER+>endocrine; else chemo`), 임계 0.5, HER2·ER 라벨 보유 슬라이드로 재계산:

| 항목 | 커밋본 | braveji 재계산 | 일치 |
|---|---|---|---|
| n | 294 | 294 | ✅ |
| confusion endocrine→ | {endo 171, chemo 9} | 동일 | ✅ |
| confusion antiHER2→ | {endo 33, chemo 2} | 동일 | ✅ |
| confusion chemo→ | {endo 58, chemo 21} | 동일 | ✅ |
| base rate (actual) | .612/.119/.269 | 동일 | ✅ |
| base rate (predicted) | .891/0/.109 | 동일 | ✅ |
| misroute | .05 / 1.0 / .734 | 동일 | ✅ |
| mean_cost | .035/.416/.510 | .0347/.4161/.5103 | ✅ |
| headline contrast | 0.381 | 0.3814 | ✅ |

비용 정의(`cost = therapeutic_distance(true, pred)`)도 손검산 일치: endocrine `(171×0+9×0.695)/180=0.0347`, antiHER2 `(33×0.395+2×0.765)/35=0.4161`, chemo `(58×0.695)/79=0.5103`.

## 2. 🔴 신규 발견 — pseudo-replication (CI 과소추정)

**n=294는 슬라이드 수이고, 고유 환자는 95명이다** (평균 3.09 슬라이드/환자, 최대 9장, 2장 이상 환자 88명). 같은 환자의 슬라이드는 true 라벨이 동일하고 예측도 상관되므로 **독립 표본이 아니다.**

재계산 부트스트랩 (B=5000, seed=42):

| 리샘플 단위 | headline contrast 95% CI | 폭 | 0 배제 |
|---|---|---|---|
| 슬라이드 (커밋본 방식) | [0.347, 0.420] | 0.073 | ✅ |
| **환자 클러스터 (올바른 단위)** | **[0.331, 0.427]** | **0.096** | ✅ |

- 슬라이드 단위 재현치가 기록 CI `[0.348, 0.420]`와 일치 → **커밋본 CI는 슬라이드 단위 부트스트랩**임이 확인됨.
- 환자 단위로 바꾸면 **CI가 1.32× 넓어진다** → 기록 CI는 정밀도를 과대 표시.
- **단, 결론은 불변:** 환자 단위에서도 CI가 0을 배제 → **헤드라인(antiHER2 축 대체비용이 endocrine보다 크다)은 유지**.

## 3. 정성 판단

- ✅ `honest_reading`이 모범적이다. endocrine 5% mis-route를 "진짜 H&E 스킬이 아니라 다수클래스 붕괴의 산물"로 **스스로 부정**하고, robust 결론을 HER2축 + headline contrast로만 한정했다. 과대주장 없음.
- ✅ `claim_level: hypothesis_only`, 두 라우팅(PAM50 0.340 / receptor 0.381) 모두 0 배제 → 스킴 비의존.
- ✅ HER2 100% mis-route가 외부 AUROC 0.53(random)과 정합 — Critic #2/#4의 HER2 reject와 일관.

## 4. 판정: **`critic_status: caution`** (결론 유지, 보고 수정 4건 후 pass)

핵심 결론은 원자료 재현 + 환자 단위 재검정으로 **버팀**. 다만 제출 전 아래 수정 필요:

1. 🔴 **CI를 환자 단위로 교체** — `headline_contrast.ci95`를 `[0.331, 0.427]`(또는 재산출값)로. 슬라이드 단위 CI는 pseudo-replication으로 과소. **per_axis mean_cost의 불확실성도 동일 이슈** → 환자 단위로 재보고 권장.
2. ⚠️ `pred_source`가 **개인 홈 절대경로**(`/home/kkkim/project/...`) — CLAUDE.md 공유경로 규칙 위반, 타인 재현 불가. repo-relative `experiments/sjpark/cptac_ext_predictions_indexed.csv`로 정정(내용 동일 확인함).
3. ⚠️ **라우팅 임계 0.5가 JSON에 미기재** — 재현으로 확인했으나 명시 필요(임계는 사전등록/코드 근거로 고정).
4. ⚠️ **CI 산출 메타 미기재** — 부트스트랩 반복수·seed·리샘플 단위를 JSON에 기록.

→ 위 4건 반영 시 **pass 상신 가능**. 그 전까지 **Fig 2·Fig 3은 headline 승격 금지**(FIGURES_INDEX 규율 유지).

## 5. 재현 방법

`experiments/braveji/BIOP02-91_cost_verification/verify_cost_routing.py` — 라우팅 재계산 + 슬라이드/환자 부트스트랩 비교. `/workspace` CPTAC manifest 필요(GPU 머신).

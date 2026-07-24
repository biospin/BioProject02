# Critic 7-point 최종 게이트 — 상태 트래커 (BIOP02-75)

**작성:** braveji (Critic 총괄) · 2026-07-23 · 근거 = origin/main + 진행 PR
**목적:** 7항목 판정이 여러 JIRA 코멘트에 흩어져 있어, **엔드포인트 × 7항목** 단일 매트릭스로 통합. 최종 서명(-75)을 기계적으로 만들기 위한 사전작업.
**규율:** 판정 근거는 **봉인 문서·실물 코드·재계산 결과**만. 발표자료·메모 수치는 근거로 쓰지 않는다.

---

## 1. 엔드포인트별 7항목 매트릭스

| # | 항목 | ER | PR | HER2 | **PAM50-4c** |
|---|---|---|---|---|---|
| 1 | data_leakage | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| 2 | baseline_comparison | ⚠️ caution | ⚠️ caution | ❌ reject | **✅ PASS** |
| 3 | counterfactual | ⚠️ caution | ⚠️ caution | ⚠️ caution | ⚠️ caution |
| 4 | cross_dataset | ⚠️ caution | ⚠️ caution | ❌ reject | **✅ PASS** |
| 5 | bio_plausibility | ⚠️ caution | ⚠️ caution | ⚠️ caution | ⚠️ caution |
| 6 | drp_framing | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| 7 | claim_level | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| — | **종합** | SIGNAL, NOT ADDITIVE | SIGNAL, NOT ADDITIVE | **REJECT** | **caution (pass 후보 1순위)** |

### 근거 요약
- **#1** split_policy_v0 lock(BIOP02-41) + braveji 독립 검증 `split_integrity_verification.json`: site/case_id overlap **0**, `site_disjoint=true`·`patient_disjoint=true`. 4-class는 동일 split의 부분집합이라 disjoint 유지.
- **#2** 최종표 lock(BIOP02-69, `FINAL_baseline_comparison.md`). ER/PR은 mean_embed는 유의하게 이기나(ext +0.128/+0.223) subtype_only에 외부 역전 → **비가산**. HER2는 mean_embed조차 못 이김. PAM50-4c만 유효 기준선(mean_embed)을 내부·외부 **CI 비중첩**으로 상회(+0.089/+0.165).
- **#3** braveji GPU 독립 재실행(BIOP02-56, 4엔드포인트 diff 0). proba-level faithful(10~23×)이나 **AUC-level 비유의**(ER drop 0.0009 / PAM50 p=0.061).
- **#4** registry 5엔트리 + braveji 재계산 일치. PAM50-4c만 ext(0.8181) ≥ int(0.8053).
- **#5** PAM50 라벨소스 = Parker 2009 계산본 확정, manifest **1009/1009 100% 추적**(braveji 검증). 잔여 = 발현행렬 study_id·계산 스크립트 미커밋 + jhans sub-check 미배정.
- **#6/#7** DRP 표현 없음, `hypothesis_only` 전면 적용, 4-class vs 5-class 비교주장 철회(`fc07e5c`), Fig 1 서명 pass.

---

## 2. 🔴 Orchestrator 판단 — "7항목 전부 pass"는 달성 불가

**-75의 문구("Critic 7항목 전부 pass 확인")를 문자 그대로 달성할 수 없습니다.** #3 counterfactual이 그 이유입니다:

- AUC-level 효과가 **본질적으로 비유의**(PAM50 p=0.061, ER drop 0.0009). 이는 **결함이 아니라 MIL 신호 중복성**의 결과다 — top-attention 타일을 지워도 다른 타일이 같은 신호를 담고 있어 슬라이드 순위가 안 흔들린다.
- 추가 작업으로 pass가 되지 않는다. 데이터를 더 본 뒤 기준을 낮추는 것은 **금지**(사후 골대 이동).

**권고:** -75의 성공 기준을 **"7항목 전부 pass"** → **"7항목 전부 *판정 완료* + caution은 Limitation으로 명시 서술"** 로 재정의. 이건 기준 완화가 아니라 **처음부터 정직한 기준**이다. Leader(kkkim) 승인 필요.

---

## 3. 최종 서명(-75) 잔여 블로커

| 블로커 | 담당 | 상태 |
|---|---|---|
| Fig 2·3 pass 승격 4건 (CI 환자 단위 교체 등) | kkkim | ⏳ BIOP02-91 comment 11395 / PR #70 |
| PAM50 발현 study_id + 계산 스크립트 커밋 (#5) | kkkim | ⏳ 미해소 (PROVENANCE "남은 gap") |
| #5 bio sub-check 재배정 (Owner≠Reviewer) | jhans | ⏳ 미배정 |
| 원고 draft 완성 (Methods/Results 리뷰 대상) | 집필 담당 | ⏳ |
| 저자·소속·순서·corresponding·GPU 제공처 확정 | 팀/사람 게이트 | ⏳ (-76/-79 공통 선행) |

**해소된 항목 (이번 주):** ✅ sjpark `commit_hash` 회귀 수정(`f5d0d9a…`) · ✅ `faithfulness_scope: "proba-level only"` + note 명기 — 둘 다 braveji 지적(BIOP02-56 comment 11160) 반영 확인.

---

## 4. cost-of-substitution (Paper C 유방 anchor headline)

| 항목 | 상태 |
|---|---|
| 수치 무결성 | ✅ 원자료 재현 전부 일치 (braveji, PR #70) |
| headline contrast | 0.3814, 환자 단위 CI **[0.331, 0.427]** — 0 배제 ✅ |
| critic_status | ⚠️ **caution** — 표시 CI가 슬라이드 단위(1.32× 과소), 수정 4건 후 pass |
| claim_level | `hypothesis_only` ✅ |

---

## 5. 갱신 규칙
이 문서는 **-75 서명 시점의 단일 근거**다. 항목 상태가 바뀌면 근거(파일:줄 또는 JIRA comment id)와 함께 이 표를 갱신한다. 판정 변경은 braveji(Critic 총괄)만 수행한다.

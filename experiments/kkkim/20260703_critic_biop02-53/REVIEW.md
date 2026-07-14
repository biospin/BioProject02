# Critic Cross-Review — BIOP02-53 Attention MIL (sjpark)

- **Reviewer:** kkkim  **Owner:** sjpark  **Date:** 2026-07-03
- **Target:** CLAM-SB attention MIL, UNI embeddings, ER/PR/HER2, TCGA(train) → CPTAC(external test)
- **Verdict:** `caution` — 모델링 교차리뷰만. **최종 pass는 braveji(총괄) 몫**, 아직 #done 아님.

## 결과 요약 (v2 = attention-init, 최종본)

| task | val AUC | CPTAC ext AUC | random | mean_embed | subtype_only* |
|---|---|---|---|---|---|
| ER  | 0.901 | **0.894** | 0.526 | 0.816 | 0.918* |
| PR  | 0.777 | **0.778** | 0.557 | 0.686 | 0.808* |
| HER2| 0.599 | **0.530** ⚠ | — | — | — |

\* `subtype_only`은 PAM50 분자라벨을 **입력으로** 쓰는 ceiling reference (`--aux_col pam50`) — 모델이 넘어야 할 floor가 아님.

## 7-point 판정

1. **Data leakage — PASS.** TSS 37개 사이트, train/val/test 어디에도 중복 없음(site-disjoint 실검증). val↔CPTAC gap 미미(ER/PR)로 재확인. site-probe 0.9977은 "morphology가 site를 인코딩"하나 split이 disjoint라 누수 아님.
2. **Baseline — PASS.** ER 0.901 > random 0.526, > mean_embed 0.816. attention MIL이 mean-pooling도 이김 = 집계 아키텍처 값어치 있음. subtype_only(ceiling)만 못 넘음 = "H&E가 분자서브타입 prior에 근접하나 초과 못함" = limitation, FAIL 아님.
3. **Counterfactual — N/A.** 치료가설 랭킹(Paper B) 단계 항목. attention map이 부분 해석성 제공.
4. **Cross-dataset — CAUTION.** 여기선 TCGA→CPTAC(문자 그대로의 PRISM/GDSC는 N/A). ER/PR 외부 유지, **HER2 외부 near-random(ext_auc 0.53, auprc 0.12) = 실제 실패**. CPTAC 라벨이 kkkim 임시본(395/653) → 리뷰어 self-reference 부분충돌.
5. **Biological plausibility — N/A(defer).** owner(sjpark) 자기리뷰 불가, braveji 지정 non-owner sub-reviewer로 이관.
6. **DRP framing — PASS.** 금지표현 0건.
7. **Claim-level — PASS.** 전 산출물 `hypothesis_only`.

## 필수 후속 (required_followups)

1. jamie 공식 CPTAC 라벨로 교체 → 외부평가 재실행(self-reference 제거).
2. braveji: 최종 `critic_status` + #5 생물학 sub-reviewer(non-owner) 지정.
3. sjpark: **PAM50 attention-MIL 추가**(현재 MLP만 존재) — BIOP02-53 scope 미완.
4. HER2 외부 near-random 명시, "검증됨"으로 제시 금지.
5. 대표값은 v1 아닌 **v2** 사용(ER/PR 외부에서 v2 우위).

산출: `critic_report.json`(schema v0.1 valid).

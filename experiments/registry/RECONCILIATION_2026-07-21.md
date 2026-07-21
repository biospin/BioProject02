# Registry reconciliation — Critic 검증 라운드 (BIOP02-71)

**작성:** braveji (Orchestrator, registry owner) · 2026-07-21 · main 병합분 기준
**목적:** Sprint 5·6 Critic 검증(BIOP02-50 재판정 · BIOP02-56 counterfactual · BIOP02-69 baseline 최종표)을 `cross_validation_registry.jsonl`와 대조·연결. **append-only 원칙상 기존 엔트리는 수정하지 않고**, 이 노트로 검증 이력과 신규 증거 위치를 기록한다.

## 1. Registry ↔ 재계산 일치 확인 (무결성)

병합된 Critic 재계산의 external AUC가 registry 엔트리와 **전부 일치**함을 확인:

| entry_id | endpoint | registry ext AUC | 재계산 ext AUC | critic_status |
|---|---|---|---|---|
| cv-20260703-er-uni-clam | er | 0.894 | 0.894 ✓ | caution |
| cv-20260703-pr-uni-clam | pr | 0.7776 | 0.7776 ✓ | caution |
| cv-20260703-her2-uni-clam | her2 | 0.5297 | 0.5297 ✓ | reject |
| cv-20260707-pam50-uni-clammb | pam50 (5-class) | 0.7216 | — | reject (SUPERSEDED) |
| cv-20260710-pam50-uni-clammb | pam50_4class | 0.8181 | 0.8181 ✓ | caution |

→ registry 수치는 원자료 재계산으로 검증됨. critic_status도 재판정 결과(BIOP02-50/56)와 정합. **새 CV 실험은 없음**(동일 5 실험의 Critic 검증) → 신규 엔트리 append 불필요.

## 2. 이번 라운드 신규 증거 (엔트리 밖, 아래 경로)

registry 스키마(`schemas/cv_registry.schema.json`, `additionalProperties:false`)에는 아직 필드가 없어 엔트리에 넣지 않고 여기서 연결한다:

- **mean_embed paired 유의성 (BIOP02-69, Critic #2 핵심):** `baselines.mean_embed_auc`는 AUC만 있고 **paired diff/CI/p가 없었다**. 신규 산출 →
  `experiments/braveji/BIOP02-69_meanembed_paired/paired_meanembed_{er,pr,her2}_{val,cptac_external}.json`
  - ext: ER +0.1283 (p≈0) ✅ · PR +0.2230 (p≈0) ✅ · HER2 −0.054 (ns) ❌ · PAM50-4c +0.165 (CI배제) ✅
  - 결론: ER/PR = **SIGNAL, NOT ADDITIVE**(mean_embed는 이기나 subtype_only에 외부 역전), HER2 = reject, PAM50-4c = **#2 PASS(유일)**. 최종표 = `.../FINAL_baseline_comparison.md`.
- **counterfactual #3 독립 재실행 (BIOP02-56):** 4엔드포인트 원자료 재현 일치(diff 0) →
  `experiments/braveji/BIOP02-56_counterfactual_recompute/VERIFICATION_braveji.json`
- **수치 무결성 재계산 (BIOP02-50):** `experiments/braveji/BIOP02-50_critic_recompute_braveji.json`

## 3. 후속 (registry 개선)

- **스키마 확장 권장:** 엔트리에 `mean_embed_paired`(diff·ci·p)·`counterfactual`(auc_drop·proba_delta·auc_drop_significant) 필드 추가 → 증거가 엔트리에 인라인되게. (schema owner=braveji, 별도 PR)
- **근본 원인(sjpark):** `run_baselines.py`가 mean_embed **proba를 저장**하면 이 라운드의 재생성이 불필요. BIOP02-69 후속으로 요청됨.
- PAM50-4c pass 승격 잔여 = commit_hash 회귀·faithfulness 플래그(sjpark), #5 bio(jhans) — BIOP02-56 참조.

## 4. 상태

Sprint 5·6 registry = **엔트리 5건 최신·검증 완료**. -71 "정리"의 잔여는 (a) 스키마 확장으로 신규 증거 인라인, (b) Fig 2/3 확정 후 cost-of-substitution 관련 엔트리 필요 여부 판단(BIOP02-91 종속).

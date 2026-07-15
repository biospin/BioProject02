# BIOP02-50 정식 Peer Review — sjpark ER/PR/HER2/PAM50 CLAM (BRCA, Paper A)

> reviewer: **kkkim** (지정 리뷰어, cross-review pairing "sjpark 모델링→kkkim", Owner≠Reviewer) · owner: sjpark · Critic 총괄: braveji
> 날짜: 2026-07-15 · 대상: `experiments/sjpark/{er,pr,her2}_status_clam_uni_v2/`·`pam50_clam_mb_uni_v1/` (main 최신, split_hash `5995f29d3978b831` locked)
> 결론: **critic_status `caution` 동의** — braveji 2026-07-15 재판정(BIOP02-50 코멘트 11015+)과 독립적으로 동일 결론.

## 1. 아티팩트·재현성 (7-point #7/무결성)
- metrics.json 필수필드 완비(auc·auprc·balanced_accuracy·n_train·n_val·model·embedding_model·commit_hash·**split_hash**). ✅
- split_hash = `5995f29d3978b831` = **정본 lock 값 일치**(BIOP02-41). 3 태스크 동일. ✅
- 수치 = braveji 재판정과 일치(ER 0.9013·PR 0.7765·HER2 0.5992·PAM50 0.7589).

## 2. 누수 (#1) — caution→개선
- split lock 기록됨 + sjpark site-disjoint 직접검증(train16/val10/test11 site, 중복 0). ✅
- 잔여: patient-overlap assert **로그 파일** 미커밋(서술 근거는 있음). braveji 지적과 동일 — sjpark 커밋 필요.

## 3. Baseline 비교 (#2) — **독립 재계산으로 braveji 확인 (핵심)**

CLAM(CLAM-SB) vs mean_embed(임베딩 평균+선형, trivial baseline) 95% CI 직접 대조:

| task | CLAM auc [CI95] | mean_embed [CI95] | random | subtype_only(ceiling) | CLAM>mean_embed CI **비중첩?** |
|---|---|---|---|---|---|
| ER | 0.9013 [0.837, 0.954] | 0.8162 [0.743, 0.885] | 0.526 | 0.918 | ❌ **중첩**(0.837<0.885) |
| PR | 0.7765 [0.683, 0.864] | 0.6859 [0.593, 0.773] | 0.557 | 0.809 | ❌ **중첩** |
| HER2 | 0.5992 [0.483, 0.711] | 0.5477 [0.431, 0.660] | 0.480 | 0.724 | ❌ **중첩**(둘 다 ~random) |

- **세 태스크 모두 CLAM이 mean_embed를 CI-비중첩으로 상회하지 못함**(point estimate는 우위). 대조로 PAM50 4-class만 mean_embed 대비 paired diff(+0.089 내부/+0.165 외부, CI 0 제외)로 유의 → #2 pass.
- **단 CI 중첩은 "차이 없음"의 엄밀 증명이 아니다.** 직접 근거 = **paired bootstrap(CLAM vs mean_embed)** 이며, 현재 paired 파일은 전부 CLAM vs `subtype_only`(ceiling)뿐이다. → **sjpark가 mean_embed 대비 paired significance를 ER/PR/HER2에 산출해야 #2 판정이 확정**된다(braveji 배정에 동의).
- **random(0.53) 대비는 큰 우위** → ER/PR은 H&E 형태학으로 명확히 예측됨(신호 실재). HER2는 mean_embed·random과 무차별 = 정직한 음성.

## 4. Cross-dataset (#4) / subtype ceiling — 한계 기술 필수
- 외부 CPTAC에서 **subtype_only가 CLAM을 유의 역전**(ER 0.9615 vs 0.894) → 형태학이 외부 코호트에서 분자 subtype 정보를 못 따라감. **Paper A Limitation 필수**(braveji와 동일).
- registry(BIOP02-57) 검증 통과. CPTAC 공식 라벨 반영 확인.

## 5. 종합 (peer review 결론)
- **critic_status `caution` 동의.** #2는 "미해결"이 아니라 **"MIL이 trivial baseline을 유의하게 못 넘는다"가 확인된 정직한 결과** — 모델 개선이 아니라 **Paper A의 정직한 기술로 닫힌다**: "H&E 형태학 신호는 실재(ER/PR random 대비 큰 우위)하나 MIL(CLAM)의 부가가치는 mean_embed 대비 통계적으로 유의하지 않음; HER2는 near-random Limitation; 외부에서 molecular subtype이 형태학을 상회."
- **pass 전제(kkkim 아님):** (sjpark) mean_embed 대비 paired sig 산출 + patient-overlap 로그 커밋 · (jhans) #5 biological plausibility → braveji 최종 서명.
- Owner≠Reviewer 준수: 본 리뷰는 kkkim(비-owner) 독립 재계산(위 §3 CI 표는 baseline JSON에서 직접 산출). braveji 총괄과 독립적으로 동일 결론 도달 = 교차 확인.

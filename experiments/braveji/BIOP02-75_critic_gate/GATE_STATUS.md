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
| 5 | bio_plausibility | ✅ **PASS** | ✅ **PASS** | ✅ **PASS** | ✅ **PASS** |
| 6 | drp_framing | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| 7 | claim_level | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| — | **종합** | SIGNAL, NOT ADDITIVE | SIGNAL, NOT ADDITIVE | **REJECT** | **caution (pass 후보 1순위)** |

### 근거 요약
- **#1** split_policy_v0 lock(BIOP02-41) + braveji 독립 검증 `split_integrity_verification.json`: site/case_id overlap **0**, `site_disjoint=true`·`patient_disjoint=true`. 4-class는 동일 split의 부분집합이라 disjoint 유지.
- **#2** 최종표 lock(BIOP02-69, `FINAL_baseline_comparison.md`). ER/PR은 mean_embed는 유의하게 이기나(ext +0.128/+0.223) subtype_only에 외부 역전 → **비가산**. HER2는 mean_embed조차 못 이김. PAM50-4c만 유효 기준선(mean_embed)을 내부·외부 **CI 비중첩**으로 상회(+0.089/+0.165).
- **#3** braveji GPU 독립 재실행(BIOP02-56, 4엔드포인트 diff 0). proba-level faithful(10~23×)이나 **AUC-level 비유의**(ER drop 0.0009 / PAM50 p=0.061).
- **#4** registry 5엔트리 + braveji 재계산 일치. PAM50-4c만 ext(0.8181) ≥ int(0.8053).
- **#5** ✅ **PASS(2026-08-04)** — jhans 재실행 산출물을 braveji가 **원자료에서 독립 재계산해 3/3 일치**(`0.5927 / 0.3448 / 0.5682`). PAM50 라벨소스 = Parker 2009 계산본, manifest **1009/1009 100% 추적**. ⚠️ 잔여 재현성 gap(발현행렬 study_id·계산 스크립트 미커밋)은 **원고 한계에 명시 서술됨**(`04_discussion.md:25`)이라 판정을 막지 않는다. 별건 스키마 결함 = §6.
- **#6/#7** DRP 표현 없음, `hypothesis_only` 전면 적용, 4-class vs 5-class 비교주장 철회(`fc07e5c`), Fig 1 서명 pass.

---

## 2. 🔴 Orchestrator 판단 — "7항목 전부 pass"는 달성 불가

**-75의 문구("Critic 7항목 전부 pass 확인")를 문자 그대로 달성할 수 없습니다.** #3 counterfactual이 그 이유입니다:

- AUC-level 효과가 **본질적으로 비유의**(PAM50 p=0.061, ER drop 0.0009). 이는 **결함이 아니라 MIL 신호 중복성**의 결과다 — top-attention 타일을 지워도 다른 타일이 같은 신호를 담고 있어 슬라이드 순위가 안 흔들린다.
- 추가 작업으로 pass가 되지 않는다. 데이터를 더 본 뒤 기준을 낮추는 것은 **금지**(사후 골대 이동).

**권고:** -75의 성공 기준을 **"7항목 전부 pass"** → **"7항목 전부 *판정 완료* + caution은 Limitation으로 명시 서술"** 로 재정의. 이건 기준 완화가 아니라 **처음부터 정직한 기준**이다.

### ✅ Leader 승인 완료 — 2026-07-24 (JIRA 11402, 재확인 11512)

kkkim이 근거 수치를 원자료에서 독립 확인한 뒤 승인. **승인 조건 3건**(이 문서의 판정을 인용할 때 함께 인용한다):

1. caution 항목(#3 counterfactual · #5 bio_plausibility · ER/PR·HER2의 #2)은 원고 **Results/Limitation에 명시 서술**. 판정 완료로 닫되 caution을 본문에서 감추지 않는다.
2. HER2는 #2·#4에서 reject다. **"대체 불가(H&E로 안 보임)"라는 정직한 음성**으로 서술하고 pass인 척하지 않는다.
3. faithfulness는 **proba-level only** 스코프 유지(슬라이드 순위 AUC-level은 비유의). `claim_level: hypothesis_only` 유지. 이 재정의는 **-75에만 적용**하며 사전등록 법칙 기준(ρ≥0.50 등)엔 손대지 않는다.

⚠️ **승인 ≠ 서명.** 조건 1이 **원고 Limitation 실물**을 요구하므로, 그 서술이 없는 상태에서는 최종 서명 불가(없는 문서를 근거로 pass 선언 금지). 서명은 2단 분리 — 1단 = 게이트 판정 확정(이 문서), 2단 = Limitation 서술·Fig 2·3·저자정보 확정 후 `critic_status: pass`. 근거 = JIRA 11515 → **11521로 사유 정정**.

### ✍️ 1단 서명 완료 — 2026-07-28 (JIRA 11560)

**확정한 것:** 7항목 × 4엔드포인트 **판정 완료**(§1 매트릭스 28칸, 미판정 0건) + 각 판정이 원자료 재현으로 버팀.
**확정하지 않은 것:** `critic_status: pass`. 승인조건 1 미충족 → **2단 보류.**

서명 직전 실물 재확인(기억·SESSION_LOG 아님):

| 항목 | 근거 파일 | 결과 |
|---|---|---|
| #1 | `experiments/braveji/split_integrity_verification.json` | 존재 · overlap 0 |
| #2 | `experiments/braveji/BIOP02-69_meanembed_paired/FINAL_baseline_comparison.md` | 존재(최종표 lock) |
| #3 | `experiments/braveji/BIOP02-56_counterfactual_recompute/VERIFICATION_braveji.json` | 4엔드포인트 `max_abs_diff=0.0` · `all_reproduced=true` · pam50 `auc_drop_significant=false` |
| #4 | `experiments/registry/cross_validation_registry.jsonl` | 존재 |
| Fig 2 | `experiments/braveji/BIOP02-91_cost_verification/reverify_4fixes.py` · `0a31c62` | 스크립트 존재 · 커밋 main 포함 |

**집필에 넘긴 확정 Limitation 목록(승인조건 1 이행 명세)** — 상세 문안은 JIRA 11560 §3:
1. **#3 counterfactual** — faithfulness는 proba-level 한정(무작위 대비 10~23×), AUC-level은 비유의(ER 0.0009 · PAM50 p=0.061) = MIL 신호 중복성. 슬라이드 순위 faithfulness 주장 금지.
2. **#5 bio_plausibility** — PAM50 라벨소스 Parker 2009 계산본·manifest 1009/1009 추적 확인, 단 발현행렬 study_id·계산 스크립트 미커밋 + 산출물 재실행 진행(BIOP02-111) → caution 유지.
3. **#2/#4** — ER/PR = SIGNAL, NOT ADDITIVE(subtype_only에 외부 역전) · **HER2 = reject → "H&E로 안 보임 = 대체 불가" 정직한 음성** · PAM50-4c만 CI 비중첩 상회.

⚠️ **문안 집필은 집필 담당(현 `manuscript/` 커밋 이력상 kkkim)이 한다.** Critic이 Limitation을 직접 쓰고 그 충족을 자기가 서명하면 Owner≠Reviewer 위반(자기검수). Critic은 "무엇을 써야 하는가"만 명세하고, **위 3종의 사실관계가 담기면 충족으로 판정**한다.

📌 `manuscript/README.md` L1 기준 이 폴더 = **Paper C 플래그십**이고 유방(前 Paper A)은 **anchor 챕터로 흡수**됨 → caution 3종은 **플래그십 원고 한계 절**에 들어간다(별도 Paper A 원고 신설 불요).

> 🔴 **정정(2026-07-27, JIRA 11521):** 11515에서 이 블로커를 **"원고 draft 미존재"**로 적었으나 **사실이 아니다.** `manuscript/sections/`에 5개 섹션이 main에 존재한다(abstract 9줄·intro 14·results 37·methods 28·discussion 13). **열어보지 않고 단정한 오류** — 같은 날 11511("kkkim 승인 대기", 실제 승인은 07-24)과 같은 종류를 두 번 저질렀다.
> **결론은 유지되나 사유가 다르다:** `04_discussion.md`가 **13줄 자리표시자**(L3이 "exemplar 정독 후 확정"이라 자칭)이고 한계는 L11 한 줄뿐이며, **승인조건 1이 요구한 caution 3종이 없다**(전 섹션 검색: `counterfactual` 0회 · `bio_plausibility`/`pathway` 0회). 즉 블로커의 실체는 **"원고를 새로 써야 함"이 아니라 "Discussion 한계 절에 caution 3종 추가"**다.

---

### ✅✅ 2단 최종 서명 완료 — 2026-08-27 (`critic_status: pass`, JIRA 12053)

**확정:** Critic 7-point **과학 게이트 통과**. 재정의된 성공 기준(*"7항목 전부 판정 완료 + caution은 Limitation 명시"*, kkkim 승인 11402·11512)을 충족.

**⚠️ 이 서명이 열지 않는 것:** **외부 공개(preprint·투고)는 그대로 닫혀 있다.** 저자·소속·순서·corresponding·Funding 확정은 **별도 공개 게이트**이며 미해소다(BIOP02-114).

**게이트 분리 결정 (braveji, #12051 → 승인 A안):** 저자 메타데이터는 어떤 과학적 주장의 타당성에도 영향을 주지 않는다. 7-point는 과학 게이트, 저자정보는 공개 게이트다. 두 게이트를 한 조건에 묶은 것은 **braveji 자신의 2단 정의(#11515)**였고 그 때문에 Critic 게이트가 과학과 무관한 사유로 닫히지 못했다. 범위를 과학 게이트로 한정해 서명하되 **공개 차단은 유지**한다. kkkim 이의 시 되돌릴 수 있다.

**서명 직전 실물 재확인**(기억·SESSION_LOG 아님, origin/main `6390f9b`):

| 조건 | 근거 |
|---|---|
| 7항목 × 4엔드포인트 판정 완료 | §1 매트릭스 28칸, **미판정 0** |
| #2 baseline (ER/PR 비가산) | `04_discussion.md:19` |
| #3 counterfactual (proba-level 한정) | `04_discussion.md:21` |
| #2/#4 HER2 정직한 음성(reject) | `04_discussion.md:23` |
| #5 bio_plausibility | `04_discussion.md:25` |
| DRP 금지표현 스캔 | 전 섹션 + 전체초안 **실히트 0** |
| Fig 1 / 2 / 3 | pass(07-21) / pass(07-27, 19/19) / **pass(08-19, 25/25)** |

> 🔎 **자기정정:** 1차 스캔에서 caution 3종이 **0히트**로 나왔으나 원인은 원고가 아니라 **내 grep 문법 오류**였다(`-E`에서 `\|`는 리터럴 파이프 → 검색어 자체가 존재하지 않는 문자열). **도구가 "못 찾겠다"고 한 것을 사실로 처리하지 않고 조사해 확인**했다 — CLAUDE.md 금지항목 그대로.

**비블로커 잔여 2건(판정에 영향 없음):** PAM50 발현 study_id·계산 스크립트 미커밋(원고 한계에 서술, kkkim #11967 확인) · `04_discussion.md:10`의 stale `<FILL: A3/A4 후>`(Yale 0.533은 전체 초안 R6에 실재 — 집필 담당 정리 대상).

**산출물:** `critic_report.json`(이 폴더) + 재현물 4종(`BIOP02-59_bioplausibility_recompute` · `BIOP02-75_fig3_pam50_verification` · `BIOP02-91_cost_verification` · `BIOP02-56_counterfactual_recompute`).

---

## 3. 최종 서명(-75) 잔여 블로커

**갱신 2026-08-19 (Fig 3 PAM50 CI 25/25 검증·서명 완료).** 잔여 = **저자·소속·순서·corresponding 확정(팀 게이트) · PAM50 발현 study_id 커밋(kkkim)** — **braveji 몫의 기술 잔여는 없다.**
판정 자체는 §2의 1단 서명으로 확정됐고, **Discussion caution 3종 해소 + #5 caution→PASS**.

> ✍️ **#5 PASS 서명 2026-08-04.** GPU 머신 원자료(`/workspace/…/consistency_scores.csv`, md5 `52547edc…`)에서 **`endocrine_rule.py`를 import하지 않고 규칙을 재구현해** 독립 산출 → 커밋값과 **3/3 일치(차이 0.00e+00)**.
> `Anti-HER2 0.5927`(ρ=0.4927, n_both=2) · `Endocrine±CDK4/6i 0.3448`(ET ρ=0.1129 + CDK ρ=0.4768 → 결합 0.2949, n_both=1) · `Cytotoxic chemo 0.5682`(ρ=0.4682, n_both=3).
> 재현 스크립트·원자료 스냅샷·결과 = `experiments/braveji/BIOP02-59_bioplausibility_recompute/`.
> ⚠️ **별건 결함 2종은 #5와 분리해 남긴다**(아래 §6).

| 블로커 | 담당 | 상태 |
|---|---|---|
| 성공기준 재정의 승인 | kkkim | ✅ **해소** — 11402(07-24) + 11512(07-27) |
| **Fig 2** pass 승격 4건 | braveji | ✅ **서명 완료 2026-07-27** — 원자료 **19/19 재계산 일치**(`reverify_4fixes.py`). PR #75 병합(`0a31c62`) |
| **Fig 3** pass | braveji | ✅ **서명 완료 2026-08-19** — kkkim이 `83da89d`로 PAM50 라우팅 CI를 **환자 클러스터 부트스트랩**으로 교체(`[0.2508, 0.4254]`, 슬라이드 단위 `[0.2765,0.4004]`는 `_deprecated` 보존)하고 독립검증용 인덱스 CSV를 함께 커밋. braveji가 생산 스크립트를 호출하지 않고 규칙을 재구현해 **25/25 완전일치**(비용 컬럼도 규칙에서 재생성, 최대차 0.00e+00). headline 0.3396 · **0 배제 유지**. 재현물 = `experiments/braveji/BIOP02-75_fig3_pam50_verification/`. ⚠️ 재현 함정 2건(예측 파일 v1/4class 혼동 · 무치료 페널티=전역최대 0.765)은 그 폴더에 기록 |
| PAM50 발현 study_id + 계산 스크립트 커밋 (#5) | kkkim | ⏳ 미해소 (PROVENANCE "남은 gap") |
| **#5 bio sub-check** | jamie(리뷰, 완료) → **jhans(실행+산출물 owner, BIOP02-111)** | 🟡 **sub-check 실질 완료** — jamie가 코드·서버 실측으로 검증(BIOP02-59 #11501·#11518), braveji가 repo에서 4건 독립 재확인 일치(#11528). **잔여 = 재실행 1건 → `BIOP02-111`**(assignee 서정한, 2026-07-27 신설). 커밋 산출물 `confidence` 0.5/0.5/0.0·0.3 = **fallback 값 그대로**, `critic_status: pending`; jamie 재실행값 0.3448과 달라 숫자가 바뀜 → 현 산출물로 pass 불가. **산출물 owner도 sjpark→jhans 이관**(#11535), 경로 `experiments/sjpark/…` → `experiments/jhans/biological_plausibility/`(실행코드 참조 0건 확인, docstring 사용예 1곳만 정정). ⚠️ **소유 집중**: jhans가 rule·입력데이터·실행·산출물 전부를 가짐 → Owner≠Reviewer 위반은 아니나(검토자 jamie·braveji는 owner 아님) 남는 외부점검이 **braveji 독립 재계산 하나**뿐 → **그 재계산은 서명의 전제 조건**. ← **11531·11532·11535 정정**(구 문구 "담당 미확정·불일치"는 오류). **갱신 2026-08-04(JIRA 11587):** jhans 재실행 완료·main 병합(`07a32ee`), BIOP02-111 **Done**. braveji **구조 검증 통과** — 커밋 실측 `0.5927 / 0.3448 / 0.5682`이 보고값과 일치, 요건 5종(`confidence_source: measured_rho`·`generated_by`·`commit_hash` 갱신·`critic_status: pending` 유지·구 sjpark 경로 삭제) 전부 반영, **fallback 값 소멸**. ⛔ **단 서명 불가** — 원자료 `consistency_scores.csv`가 리포에 없고 `/workspace` 미마운트라 **독립 재계산 미수행**. 구조·형식 검증 ≠ 수치 검증. **갱신 2026-08-04: 재계산 완료 → ✅ PASS 서명**(§3 상단 인용). GPU 원자료에서 규칙 재구현으로 독립 산출, 커밋값과 **3/3 일치(0.00e+00)**. 재현물 = `experiments/braveji/BIOP02-59_bioplausibility_recompute/`. 산출물 `critic_status: pending → pass`, `critic_report_path` 연결. ⚠️ 별건 스키마 결함 2종은 §6으로 분리 |
| ~~Discussion 한계에 caution 3종 명시~~ | 집필 | ✅ **해소 2026-08-04**(JIRA 11586) — `04_discussion.md` §한계(커밋 `926fdc4`)에 3종 + HER2 전용 문단 실물 반영. **승인조건 1·2·3 모두 충족.** 수치를 **1차 근거와 대조해 전부 일치**: ER +0.1283 / PR +0.2230 / subtype-only 역전 −0.067·−0.1343 / HER2 mean-embed **−0.054** p=.368 / PAM50-4c +0.0889·+0.165 CI 비중첩(`FINAL_baseline_comparison.md:14-17`) · 10~23배·ER 0.0009·PAM50 p=0.061(`VERIFICATION_braveji.json:85`) · 1009/1009 및 "남은 gap"(`agents/data/manifests/tcga_brca_pam50_computed_PROVENANCE.md:20,23-24`). 하드룰 스캔 **실히트 0건**. ⚠️ 문안은 braveji가 쓰지 않았으므로 이 판정은 자기검수가 아니다(명세=11560, 집필=타인) |
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

---

## 6. 별건 결함 — #5 서명과 분리해 기록 (2026-08-04, braveji)

#5 재계산 중 발견. **수치와 무관하고 #5 판정에 영향을 주지 않으나**, 아티팩트 계약 위반이라 별도로 처리한다.

### (a) hypothesis 산출물이 `schemas/hypothesis.schema.json`을 만족하지 않는다

| 위반 | 내용 |
|---|---|
| 필수 필드 누락 | **`embedding`** — 스키마 `required`에 있으나 산출물에 없음 |
| `additionalProperties: false` 위반 | `critic_5_biological_plausibility` · `confidence_source` · `generated_by` |

**귀책 구분(중요):**
- `embedding` 누락과 `critic_5_biological_plausibility`는 **구 placeholder(`802ef9b`, 2026-07-08)에도 이미 있었다** → jhans가 만든 문제가 **아니다**.
- `confidence_source`·`generated_by`는 **braveji가 BIOP02-111에서 신설을 요청**한 필드다. **스키마의 `additionalProperties: false`를 확인하지 않고 요청한 내 실수다.** 두 필드 자체는 유용하므로(fallback↔실측 구분) **스키마를 확장하는 쪽**을 권고하나, 그 결정은 Leader 승인 사안이다.

### (b) 더 근본적 — 이 스키마를 **실제로 검증하는 코드가 리포에 없다**

`biological_plausibility_check.py:5`·`run_hypothesis_pipeline.py:3`은 docstring에서 *"hypothesis.schema.json 형식 출력"* 이라고 **말할 뿐** 검증하지 않는다. 리포 전체에서 `jsonschema` 사용처는 `evals/critic_pilot/`(픽스처)와 `experiments/registry/`(다른 스키마)뿐이다.

→ **"스키마 형식"이라는 주장이 한 번도 검증된 적이 없고**, 그래서 위 (a)가 최소 4주간 드러나지 않았다.
이는 이 프로젝트가 반복해 만난 실패와 **같은 모양**이다: *검증 게이트 ①의 실행 명령 부재* · *CI가 없어 만들어 둔 검증이 안 돌던 것*. **문서에만 있는 보장은 보장이 아니다.**

**권고:** ① 스키마에 3필드 추가 여부 결정(Leader) ② `embedding` 채우기(생성자만 값을 안다) ③ **산출 시 스키마 검증을 강제**하고 CI blocking에 편입. → 별도 티켓 권장.

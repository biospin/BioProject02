# Critic #4 (cross-dataset PRISM vs GDSC) — 판정불가 근본원인

> owner(kkkim) 실행 기록, 2026-07-16. 대상: jhans `crosscancer_subcheck.py` (PR #44) #4 로직.
> **결론: 제공된 데이터로는 #4가 구조적으로 계산 불가. "fail"이 아니라 "데이터 provisioning 문제".**

## 증상
`crosscancer_subcheck.py --gdsc ... --prism_bowel ... --prism_lung ...` 실행 시:
- 대장(Bowel): PRISM∩GDSC 최종 교집합 **1개** cell line → 상관 계산 불가(전부 n<5 skip).
- 폐(Lung): 교집합 **14개** → median Spearman ρ 낮음(Osimertinib −0.09, Gefitinib 0.10, Afatinib −0.48…) → status=fail.

## 근본원인 (실측)
ID 조인은 **정상**이다 — PRISM index와 GDSC(Sanger→ModelID 매핑) 모두 `ACH-xxxx` DepMap ModelID로 정확히 정규화됨. 문제는 **두 패널의 세포주 커버리지가 상보적**이라는 것:

| Bowel | 수 |
|---|---|
| Model.csv Bowel 총 | 99 (SangerModelID 有 70) |
| PRISM Bowel | 38 |
| GDSC Bowel | 49 |
| **PRISM ∩ GDSC** | **1** |
| PRISM ∪ GDSC | 86 |
| PRISM only | 37 |
| GDSC only | 48 |

교집합 1 / 합집합 86 → PRISM "subsetted" 파일(`PRISM_Repurposing_Secondary_(AUC)_subsetted_Bowel.csv`)이 사실상 **GDSC의 여집합**으로 구성돼 있음. PRISM-vs-GDSC 상관(#4의 전제)은 **공통 cell line이 있어야** 계산되는데 그게 1개뿐 → 구조적 불가.

## jhans에게 (수정 방향)
1. `subsetted` PRISM 파일이 왜 GDSC와 안 겹치는지 확인 — DepMap Custom Downloads 필터 조건 재점검(특정 context/subset 필터가 GDSC 세포주를 배제했을 가능성).
2. **GDSC와 겹치는 cell line을 포함한 PRISM AUC**를 다시 받거나(비-subset 전량 PRISM Secondary에서 lineage 필터), 또는
3. #4를 PRISM-vs-GDSC 대신 **다른 일관성 근거**로 재설계(예: 동일 플랫폼 내 replicate, 또는 positive-control drug의 방향성만).

## 판정
- #5 생물학적 타당성: **PASS** (독립적, 영향 없음).
- #4 cross-dataset: **pending_data (구조적)** — critic_upgrade 불가는 유지되나 사유는 "일치성 실패"가 아니라 "PRISM subset이 GDSC와 비중첩".
- Owner≠Reviewer: 본 노트는 owner(kkkim) 관찰. Critic 판정은 jhans(#4/#5)·braveji(총괄) 몫.

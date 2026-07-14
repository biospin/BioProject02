# docs/BIOP02-53 → main 정리 병합 체크리스트 (게이트 봉인)

> 목적: 이 장수 브랜치(`docs/BIOP02-53-kkkim-critic-review`, 2026-07-13 기준 main 대비 **앞 98·뒤 0**)를 **게이트 통과 후에만** 기계적으로 main에 병합. 즉흥·조기 병합 방지.
> 결정자: kkkim(Leader). Critic 서명: braveji. **모든 게이트가 ✅ 되기 전에는 병합 금지.**

## 🚦 병합 게이트 (전부 충족해야 실행)

- [x] **G1 — Paper C 결과 확정.** ✅ **kkkim Leader 승인(2026-07-14).** held-out 4암종+anchor firm, 대장 회고적 명시, 5암종 통합 = `LAW_HELDOUT_SCOREBOARD.md`. 결론 "방향 일관·이분법 미확립"으로 동결(승격 금지).
- [ ] **G2 — Critic 서명(braveji).** split lock ✅ 완료 / **Paper C held-out ❌ REJECT — remediation 필요.**
  - ✅ **split lock(BIOP02-41): braveji Critic cross-sign PASS**(2026-07-13, commit 6ffdeb9 + critic_report/registry a6d2f55). §6 lock criteria 전항 통과.
  - [ ] ❌ **Paper C held-out: braveji Critic REJECT**(2026-07-14). 산출물 `critic_report.json`·`CRITIC_REVIEW_G2_braveji.md`·`CRITIC_REVIEW_G2_ADDENDUM.md`(브랜치 `docs/BIOP02-96-braveji-critic-crosscancer-g2` / PR#33 · BIOP02-96 코멘트). 블로커 5건: ①단일시드 null→우연배제 미확립(두경부 HPV 0.9594 포함) ②폐 stale doc(정본 histology 0.939 vs 문서 0.9247) ③baseline(pixel-mean·subtype-only) 전 암종 부재 ④대장 5-seed 실패검정(cms1·cms4 FAIL)이 문서서 소실 ⑤embedding_path 2,588건 전부 /home/kkkim=재현 불가(구조적 루트, **착수함→/workspace 이관 중**). **서명조건 6개 해소 후 재검토(braveji: "통과 가능성 높음").**
- [x] **G3 — claim 규율.** ✅ 검증(2026-07-14): crosscancer 산출물 전부 `claim_level: hypothesis_only`·`critic_status: pending`, DRP 금지표현 0(유일 히트=준수 문장 "약물반응예측 아니다").
- [ ] **G4 — 브랜치 동기화.** `git fetch && git merge origin/main` → **뒤처짐 0**. (2026-07-13 충족, 병합 직전 재확인.)
- [x] **G5 — split lock focused PR(#32) 선처리.** ✅ **braveji가 PR #32 main 머지 완료**(2026-07-13, merge e6ffc45). split lock provenance가 main에 안착 → 대형 병합 diff·리스크 축소됨.

## 🔧 병합 절차 (게이트 통과 후, 사전 결정)

1. `git checkout docs/BIOP02-53-kkkim-critic-review && git fetch origin && git merge origin/main` — 뒤처짐 0 재확인(충돌 시 해결).
2. **PR #21 재정비**(현재 제목이 stale = "Critic 교차리뷰"): 제목·본문을 실제 스코프(Paper C 교차암종 + 블로그 + cost-of-substitution + split lock 잔여)로 갱신. 게이트 체크 결과를 본문에 첨부.
3. **머지 방식 = merge commit(히스토리 보존).** squash 금지 — 98커밋은 분석 provenance(법칙 검정·정정 이력)라 per-commit 기록 유지. `gh pr merge 21 --merge`.
4. 병합 후 `origin/main`에서 검증: 헤드라인 산출물 존재·`split_hash` 정본 일치·claim 라벨 보존.
5. 병합 완료 후 브랜치 삭제, 후속 작업은 새 티켓 브랜치에서 시작([[feedback-branch-hygiene]]).

## 📌 상태 (갱신)
- 2026-07-13: 게이트 전부 미충족(G2 pending). 브랜치는 동기화(G4 ✅). PR #32(split lock focused) 리뷰 대기.
- 2026-07-14: HNSC 472/472 → 5암종 held-out + 스코어보드, G1 ✅. **BUT G2 Paper C = braveji Critic REJECT**(블로커 5건, PR#33). ⚠️ **병합 중단.** (kkkim이 올린 BIOP02-93 Critic요청 코멘트는 reject와 교차되어 삭제됨.)
- 다음(remediation 순서): 블로커5 경로→/workspace 재현성(**착수**) → 문서동기화(폐 정본·대장 5-seed) → 전 endpoint 5-seed null + baseline(pixel-mean·subtype-only) → sjpark/jhans #4·#5 → braveji 재검토 → G2 통과 후에만 §16 병합.

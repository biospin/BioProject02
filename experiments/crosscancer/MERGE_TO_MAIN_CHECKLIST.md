# docs/BIOP02-53 → main 정리 병합 체크리스트 (게이트 봉인)

> 목적: 이 장수 브랜치(`docs/BIOP02-53-kkkim-critic-review`, 2026-07-13 기준 main 대비 **앞 98·뒤 0**)를 **게이트 통과 후에만** 기계적으로 main에 병합. 즉흥·조기 병합 방지.
> 결정자: kkkim(Leader). Critic 서명: braveji. **모든 게이트가 ✅ 되기 전에는 병합 금지.**

## 🚦 병합 게이트 (전부 충족해야 실행)

- [x] **G1 — Paper C 결과 확정.** ✅ **kkkim Leader 승인(2026-07-14).** held-out 4암종+anchor firm, 대장 회고적 명시, 5암종 통합 = `LAW_HELDOUT_SCOREBOARD.md`. 결론 "방향 일관·이분법 미확립"으로 동결(승격 금지).
- [~] **G2 — Critic 서명(braveji).** 2갈래 중 **split lock ✅ 완료**, Paper C 대기.
  - ✅ **split lock(BIOP02-41): braveji Critic cross-sign PASS**(2026-07-13, commit 6ffdeb9 + critic_report/registry a6d2f55). §6 lock criteria 전항 통과.
  - [ ] **Paper C held-out 산출물**: 5암종 held-out 완료(HNSC 472/472 포함)·G1 승인(07-14) → **braveji Critic 정식 요청됨**(2026-07-14, BIOP02-93 코멘트 11157). `critic_status: pass` 서명 대기.
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
- 2026-07-14: HNSC 임베딩 472/472 완료 → **5암종 held-out 전부 완료 + 스코어보드**. G1 ✅ 승인. **G2 Paper C Critic을 braveji께 정식 요청**(BIOP02-93 코멘트 11157). 남은 게이트 = G2-PaperC(braveji 서명) + G4 최종 재확인.
- 다음: braveji `critic_status: pass` → G4 뒤처짐 0 재확인 → 병합 절차(§16) 실행.

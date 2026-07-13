# docs/BIOP02-53 → main 정리 병합 체크리스트 (게이트 봉인)

> 목적: 이 장수 브랜치(`docs/BIOP02-53-kkkim-critic-review`, 2026-07-13 기준 main 대비 **앞 98·뒤 0**)를 **게이트 통과 후에만** 기계적으로 main에 병합. 즉흥·조기 병합 방지.
> 결정자: kkkim(Leader). Critic 서명: braveji. **모든 게이트가 ✅ 되기 전에는 병합 금지.**

## 🚦 병합 게이트 (전부 충족해야 실행)

- [ ] **G1 — Paper C 결과 확정.** held-out 법칙 검정이 firm(HNSC ✅ / STAD 442 ✅ / 폐 MIL held-out 완료 / 대장 증분 D13 정리). 미완 endpoint는 exploratory로 명시, provisional headline을 확립으로 승격하지 않음.
- [ ] **G2 — Critic 서명(braveji).** split lock(BIOP02-41) + Paper C 산출물 `critic_status: pass`. Owner≠Reviewer(kkkim self-sign 금지). 현재 = **pending**.
- [ ] **G3 — claim 규율.** 전 산출물 `claim_level: hypothesis_only`(+ provisional 표기) 유지, DRP 프레이밍 0.
- [ ] **G4 — 브랜치 동기화.** `git fetch && git merge origin/main` → **뒤처짐 0**. (2026-07-13 충족, 병합 직전 재확인.)
- [ ] **G5 — split lock focused PR(#32) 선처리.** 가능하면 PR #32(split lock만)를 먼저 main에 머지해 provenance를 분리 이관 → 이 대형 병합의 diff·리스크 축소.

## 🔧 병합 절차 (게이트 통과 후, 사전 결정)

1. `git checkout docs/BIOP02-53-kkkim-critic-review && git fetch origin && git merge origin/main` — 뒤처짐 0 재확인(충돌 시 해결).
2. **PR #21 재정비**(현재 제목이 stale = "Critic 교차리뷰"): 제목·본문을 실제 스코프(Paper C 교차암종 + 블로그 + cost-of-substitution + split lock 잔여)로 갱신. 게이트 체크 결과를 본문에 첨부.
3. **머지 방식 = merge commit(히스토리 보존).** squash 금지 — 98커밋은 분석 provenance(법칙 검정·정정 이력)라 per-commit 기록 유지. `gh pr merge 21 --merge`.
4. 병합 후 `origin/main`에서 검증: 헤드라인 산출물 존재·`split_hash` 정본 일치·claim 라벨 보존.
5. 병합 완료 후 브랜치 삭제, 후속 작업은 새 티켓 브랜치에서 시작([[feedback-branch-hygiene]]).

## 📌 상태 (갱신)
- 2026-07-13: 게이트 전부 미충족(G2 pending). 브랜치는 동기화(G4 ✅). PR #32(split lock focused) 리뷰 대기.
- 다음: 폐 MIL held-out 완료 → G1 근접. braveji Critic 요청(STAD·HNSC·split lock 묶어) → G2.

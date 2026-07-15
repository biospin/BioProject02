# docs/BIOP02-53 → main 정리 병합 체크리스트 (게이트 봉인)

> 목적: 이 장수 브랜치(`docs/BIOP02-53-kkkim-critic-review`, 2026-07-13 기준 main 대비 **앞 98·뒤 0**)를 **게이트 통과 후에만** 기계적으로 main에 병합. 즉흥·조기 병합 방지.
> 결정자: kkkim(Leader). Critic 서명: braveji. **모든 게이트가 ✅ 되기 전에는 병합 금지.**

## 🚦 병합 게이트 (전부 충족해야 실행)

- [x] **G1 — Paper C 결과 확정.** ✅ **kkkim Leader 승인(2026-07-14).** held-out 4암종+anchor firm, 대장 회고적 명시, 5암종 통합 = `LAW_HELDOUT_SCOREBOARD.md`. 결론 "방향 일관·이분법 미확립"으로 동결(승격 금지).
- [ ] **G2 — Critic 서명(braveji).** split lock ✅ / **Paper C held-out = `caution`**(1차 reject→2차 reject→**caution**; kkkim remediation 완료, 잔여 = sjpark #4·jhans #5 sub-check → braveji 3차 재검토·서명).
  - ✅ **split lock(BIOP02-41): braveji Critic cross-sign PASS**(2026-07-13, commit 6ffdeb9 + critic_report/registry a6d2f55). §6 lock criteria 전항 통과.
  - [ ] ❌ **Paper C held-out: braveji Critic 2차 재검토 REJECT**(2026-07-14, commit ab77cce, 브랜치 `docs/BIOP02-96-braveji-critic-g2-reverify`). 1차 5건 중 3건 해소, **잔여 2건 + 신규 HPV 표 모순:**
    - ✅ BLOCKER-2 해소: 폐 정본 재동기화(9b42d37, histology 0.9247→0.939)
    - ✅ BLOCKER-4 해소: 대장 5-seed 실패(cms1·cms4 FAIL) 스코어보드 §6 반영
    - ✅ BLOCKER-5 해소: embedding_path 43G → `/workspace` 이관 완료(재현성 복원)
    - ✅ **BLOCKER-3 해소(2026-07-14)**: pixel-mean baseline 3암종(`baseline_pixelmean.json`) + subtype-only 폐 EGFR/KRAS(`baseline_subtype.json`; cross-cancer subtype는 대부분 순환). random(shuffle)·pixel·subtype 3종 완비.
    - ✅ **BLOCKER-4-2 해소(2026-07-14)**: 폐·위·두경부 5-seed shuffle-null 실행 = `<암종>/full/shuffle_null_robustness.json`(sh_robustness_5seed.py — braveji가 찾던 `critic_robustness.json`이 아니라 이 파일명). **두경부 HPV 0.9594 5-seed PASS(thr 0.790)** → braveji 확인해 HPV CONFIRM 복원(11f8782).
    - ✅ **HPV 표 모순 해소**: braveji caution 달성(ad6ac2e) + 5-seed PASS 확인으로 CONFIRM 복원(11f8782). 자기모순 해소.
    - ✅ **위암 lauren 원인 진단 완료(14a181d)**: `GASTRIC_STAD/full/LAUREN_POSCONTROL_DIAGNOSIS.md` — Lauren-특이 site-교란(파이프라인 고장·데이터희소 아님, MSI 일반화 정상).
    - **현재 critic_status = `caution`. `pass` 잔여 = sjpark #4(cross-dataset)·jhans #5(biological plausibility) sub-check → braveji 3차 재검토·서명.** (kkkim 몫 remediation 전부 완료.)
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
- 2026-07-14 #1: HNSC 472/472 → 5암종 held-out + 스코어보드, G1 ✅. **BUT G2 Paper C = braveji Critic 1차 REJECT**(블로커 5건, PR#33 / BIOP02-96). ⚠️ 병합 중단.
- 2026-07-14 #2: **braveji 2차 재검토 — REJECT 유지**(commit ab77cce). 5→2 블로커 축소. HPV 표 모순 신규 지적.
- 2026-07-14 #3: **braveji Critic — HPV 표 provisional 수정 완료 → critic_status: caution 달성.** `LAW_HELDOUT_SCOREBOARD.md` HPV 행 "✅ CONFIRM" → "⚠️ provisional (5-seed 대기)" 및 결론 §1 consistent 수정(자기모순 해소). **G2 pass 잔여 = `critic_robustness_probe.py` 폐·위·두경부 실행 + 위암 lauren 원인 진단 + sjpark/jhans sub-check (#4/#5) → braveji 3차 재검토.**
- **2026-07-15 재구성(스테일 정정):** 위 "kkkim probe 실행"·"lauren 진단"은 **이미 완료**(5-seed=`shuffle_null_robustness.json`, pixel-mean, subtype-only, lauren 진단 전부 커밋됨: 50bb7c9·14a181d·bfa03f8). critic_status=**caution**.
- **다음(잔여 = kkkim 아님):** sjpark #4(cross-dataset) · jhans #5(biological plausibility) sub-check → braveji 3차 재검토·서명 → G2 pass → main 병합. remediation 데이터는 **PR #36 open**(docs/BIOP02-96-kkkim-5seed-remediation→main).

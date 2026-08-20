# 기계화 가능하나 7종 CI 게이트가 미커버 (MISSED) — A2 · G1 · G5

이 세 건은 **결정론적·오프라인으로 커밋 산출물/이력만 보고 잡을 수 있는** 결함이다
(의미 판단 불필요). 그러나 `.github/workflows/critic-validators.yml`에 배선된 **7종 중 어느
것도** 이를 검사하지 않는다. 픽스처를 만들어 "돌릴 게이트"가 없으므로, MISSED 근거는
**7종 소스 전수 확인**(git 이력·카운트 미검사)으로 확정한다.

## 근거: 7종 중 git 이력/카운트를 보는 검증기 없음
```
grep -cE "git |commit|ahead|behind|fetch|merge|diff-filter"  (각 스크립트)
  0  check_number_drift.py
  0  manuscript_parity_ko_en.py
  0  test_gate_vacuous_pass.py
  0  verify_split_integrity.py
  4  citation_verifier/mutation_check.py   (주석의 'commit/merge' 단어 매칭 — git 조작 아님, import 확인)
  0  critic_pilot/mutation_check.py
  0  validation_harness/run_validation.py
```
7종은 모두 파일(MD/CSV/JSON) 내용만 읽는다. 커밋 시각·브랜치 ahead/behind·임베딩 개수는
아무도 안 본다.

## A2 — 회고적 사전등록
- 결함: 예측 커밋(77c0633 05:06)이 결과 커밋(afedc6a 04:45)보다 **늦음** → "sealed-forward"가 거짓.
- 기계화 방법(가능): 예측 파일 vs 결과 파일의 `git log --format=%ct` 시각 비교 → 예측이 늦으면 실패.
- 결과: **MISSED** — 7종 중 커밋 시각을 비교하는 게이트 없음. (미래 게이트 후보로 가치 큼: 분석-무결성 직결.)

## G1 — fetch만 하고 merge 안 함 (브랜치 드리프트)
- 결함: main 대비 97앞/13뒤 드리프트.
- 기계화 방법(가능): `git rev-list --count main...HEAD` ahead/behind.
- 결과: **MISSED by the 7.** 단, 프로젝트에는 SessionStart 훅 `git_drift_check.sh`가 별도로 존재해
  이 결함을 실제로는 잡는다 — 그러나 그것은 **PR 게이트 7종 밖**이라 본 실험 범위에서는 미커버.

## G5 — 임베딩 이동 → master가 0개로 읽고 1010장 재큐잉
- 결함: 파일 이동 후 개수 검증이 "0개"를 "미추출"로 오해 → GPU/디스크 낭비 직전.
- 기계화 방법(가능): 개수 실측 vs manifest 기대치, 또는 `ARCHIVED_<코호트>` 마커 확인.
- 결과: **MISSED by the 7.** 재발방지 장치(`ARCHIVED` 마커)는 **운영 파이프라인**에 있지 PR 게이트가 아님.

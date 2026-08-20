# seal_manifests — 회고적 사전등록 탐지

Registry-Replay(2026-08-20, `experiments/kkkim/20260820_registry_replay/`)가 드러낸 구멍 **A2**를 메우는 게이트의 입력.

- **게이트**: `agents/critic/scripts/check_seal_timeline.py`
- **자기검증**: `agents/critic/tests/test_seal_timeline.py` (비공허 mutation 테스트 — 정상 통과 + 회고적 검출 둘 다 확인)
- **판정**: "sealed-forward"라 주장한 예측이 결과보다 **먼저** 커밋됐는지 git 시각으로 검증. 늦었으면(회고적) FAIL.

## 왜
7종 CI 중 git 이력을 보는 게이트가 없어 A2("봉인의 진위는 시각이 가른다")를 못 잡았다. 결정론 게이트로 기계화 가능한 3건 중 분석-무결성 직결 최우선 구멍.

## CI 배선 전 필수 (공허 게이트 방지)
빈 매니페스트는 seal 0건이라 무조건 통과한다 = **공허 게이트**(우리가 금지한 anti-pattern). 따라서:
1. 먼저 실제 봉인 주장을 매니페스트에 채운다(SHA 또는 path). 근거 = `LAW_HELDOUT_SCOREBOARD.md`.
2. 채운 뒤에 `critic-validators.yml`에 8번째 스텝으로 배선(Critic=braveji 판단).
빈 채로 CI에 넣으면 "통과만 하는 게이트"라 이 게이트의 존재 이유와 모순된다.

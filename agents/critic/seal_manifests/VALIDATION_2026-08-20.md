# A2 게이트 실데이터 검증 (2026-08-20)

Registry-Replay가 MISSED로 지목한 A2(회고적 사전등록)를 게이트로 만든 뒤, **실제 교차암 커밋에 돌려** 검증했다. 근거 타임라인 = `experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md` §인식론 구분.

## 결과 — 게이트가 sealed-forward와 retrospective를 git 시각만으로 정확히 구분

| 코호트 | 예측(봉인) 커밋 | 결과 커밋 | 게이트 판정 | 스코어보드 라벨 |
|---|---|---|---|---|
| 폐 | 77c0633 (07-12 05:06) | 994b187 (07-12 15:35) | ✅ SEALED-FORWARD | sealed ✓일치 |
| 위 | b5b0088 (07-12 05:18) | 2760fb8 (07-12 16:22) | ✅ SEALED-FORWARD | sealed ✓일치 |
| 두경부 | b5b0088 (07-12 05:18) | 28eb0af (07-13 20:36) | ✅ SEALED-FORWARD | sealed ✓일치 |
| **대장(데모)** | 77c0633 (07-12 05:06) | **afedc6a (07-12 04:45)** | ❌ **RETROSPECTIVE** | **retrospective ✓일치** |

**핵심**: 게이트가 사람이 손으로 붙인 라벨(스코어보드의 정직한 sealed/retrospective 구분)을 **git 커밋 시각만으로 독립 재현**했다. 폐·위·두경부 봉인 주장은 실증됐고, 대장은 정확히 회고적으로 걸린다(스코어보드가 이미 정직하게 회고적이라 라벨한 것과 일치).

- 적용(enforcement) 매니페스트 = `crosscancer_seals.json`(폐·위·두경부 3건 = sealed-forward 주장 → 전부 PASS).
- 대장은 sealed-forward로 **주장하지 않으므로** enforcement에 넣지 않는다(정직 라벨 그대로). 위 표의 대장은 게이트가 회고적을 잡는지 보이는 **데모**.
- 규율: 게이트 튜닝 없음, 커밋 시각은 불변(결정론). incident(A2)→gate→실데이터 검증 루프 완결.

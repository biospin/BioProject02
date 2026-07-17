# 인용 오류 정정 목록 (2026-07-17)

> 참고문헌 초록분석(에이전트 3인, 실제 초록 fetch + Crossref 대조) 중 **적대적 검증으로 발견된 우리 포지셔닝 문서의 인용 오류.** 논문 집필 전 반드시 정정. 지금은 발견만 기록(자동 수정 안 함) — 각 정정은 원 문서 소유·맥락 확인 후.
> ⚠️ 에이전트 경고: 제공된 식별자 다수가 틀렸으므로 **포지셔닝 문서 전반의 인용을 한 번 검증**할 것.

| # | 위치 | 틀린 인용 | 실제(검증) | 조치 |
|---|---|---|---|---|
| 1 | `therapeutic_layer_strengthening.md` §B | "Sharifi-Noghabi **2024**, PMC11043358" | Sharifi-Noghabi **2021**, *Brief Bioinform* 22(6) **bbab294** (10.1093/bib/bbab294). PMC11043358은 **다른 논문**(Ovchinnikova 2024) | 연도·ID 정정 |
| 2 | 〃 | "cross-dataset **Spearman ≈0.2–0.25**" | 그 초록에 **없음**. 검증된 값은 Pearson: CTRPv2→gCSI 0.4±0.21 · GDSCv1→gCSI 0.26±0.16 | 수치 출처 재확인 or 삭제 |
| 3 | 〃 §B 축3 | "**Williams 2022** LINCS reversal" | **실존 확인 안 됨(NOT FOUND).** 근접 Koudijs 2023(bbac490)은 **반대 결론**(reversal 예측력 과대평가) | 정확한 서지 확인 or 삭제(Lamb2006+Subramanian2017이 이미 reversal축 근거) |
| 4 | `paperC-positioning/2026-07-12_CRC-LUNG-ST-scoop-and-data.md` | Path2Space "**Kaminski** et al." | 1저자 **Eldad D. Shulman**, 교신 **Eytan Ruppin**, *Cell* 189 (2026) 10.1016/j.cell.2026.04.023 | 저자명 정정 |
| 5 | (내 프레이밍/일부 문서) | MAKO = "H&E→ER/PR/HER2/PAM50 벤치마크" | 실제 = **ROR-P(재발위험 점수) 예측**(Kaczmarzyk, *npj Digital Medicine* 9:149). subtype 분류 아님 | "재발위험/ROR-P"로 프레이밍 수정("예측 포화" 논지는 유지) |

## 함의
- #1·#2·#3은 **B엔진(보류) 근거축**이라 당장 급하진 않으나, B 되살릴 때 정정 필수. 특히 #2(0.2–0.25)는 우리가 "viability 3중계산 금지"의 정량 근거로 반복 인용했으므로 **대체 출처 확보 필요**.
- #4·#5는 **C flagship 포지셔닝**에 직접 인용될 논문이라 우선 정정.
- Koudijs 2023은 오히려 **"reversal 단독은 generic 항증식 신호 → 독립축 수렴 필요"**의 근거로 인용 가치 있음(에이전트 제안) — B 되살릴 때 검토.

## 정정 안 한 이유
자동 수정하지 않고 기록만 함 — 원 문서(therapeutic_layer_strengthening 등)는 설계 맥락이 있어 Leader 확인 후 정정하는 게 안전. "말이 아닌 행동" 원칙상 발견 즉시 기록은 완료.

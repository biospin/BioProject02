# 치환가능성 법칙 — 5암종 통합 스코어보드 (G1 결과 확정용)

> 사전등록 `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`(봉인) 대비 held-out 관측 통합. claim_level: **hypothesis_only** · critic_status: **pending**(braveji 서명 대기). 2026-07-13.
> 목적: Paper C 브랜치→main 병합 게이트 **G1(결과 확정)**의 단일 인계 문서. 정본 수치는 각 암종 `full/LAW_TEST.md` / `routing_cost.json`에서 직접 인용.
> **핵심 규율: "확정"=결과셋 동결+정직 라벨링이지 "법칙 확증"이 아니다.** 검정력 있는 봉인 확증은 아래 굵게 표시된 소수뿐.

## 인식론 구분 (읽기 전 필수)
- **Sealed-forward(진짜 held-out):** 폐·위·두경부 — 예측을 결과 전 커밋으로 봉인 후 MIL. (폐 예측 07-12 05:06 < 결과 15:35 등)
- **Retrospective(회고적):** 대장 — 결과(07-12 04:45) 먼저, 예측(05:06) 뒤. **held-out 확증 아님, 방향 일관까지만.** (`COLORECTAL/full/LAW_TEST.md` 상단 배너)
- **Anchor(내부 holdout):** 유방 — 기존 내부 site-disjoint holdout(외부 아님).
- **검정력 규칙(사전등록, 사후 이동 금지):** n_pos<25 → exploratory → **INCONCLUSIVE**(확증·반증 대칭 불가, 점추정은 "consistent with"까지).

## 통합 표

| 암종 | endpoint | 축 분류 | 관측 AUROC (CI) | n_pos | 검정력 | 지위 | 판정 |
|---|---|---|---|---|---|---|---|
| 두경부 | **HPV** | 대체가능(바이러스축 형태) | **0.9594 (0.921–0.986)** | **26** | **충분** | sealed | **✅ CONFIRM (≥0.80)** |
| 두경부 | grade_high | 양성대조(분화도) | 0.8152 (0.742–0.882) | 41 | 충분 | sealed | ✅ 양성대조 PASS(≥0.75) |
| 두경부 | egfr_amp | 필수/등급적 | 0.6039 (0.443–0.760) | 17 | 부족 | sealed | INCONCLUSIVE(≤0.70 점추정 부합) |
| 폐 | **histology LUSC** | 대체가능(양성대조) | **0.9247 (0.889–0.957)** | **152** | **충분** | sealed | **✅ 양성대조 CONFIRM(≥0.93)** |
| 폐 | egfr_activating | 등급적 | 0.8133 (0.670–0.934) | 15 | 부족 | sealed | INCONCLUSIVE(0.75–0.89 점추정 부합) |
| 폐 | kras_g12c | 필수 | 0.6549 (0.563–0.743) | 14 | 부족 | sealed | INCONCLUSIVE(≤0.65 경계, EGFR>KRAS 점추정만) |
| 위 | lauren_diffuse | 양성대조(강한 형태) | 0.5364 (0.379–0.694) | 31 | 충분 | sealed | ⚠️ **양성대조 FAIL(예측 ≥0.85, 관측 0.54)** |
| 위 | msi_h | 대체가능 | 0.8599 (0.759–0.941) | 24 | 부족 | sealed | INCONCLUSIVE(≥0.82 점추정 부합) |
| 위 | erbb2_amp | 필수 | 0.6444 (0.523–0.771) | 14 | 부족 | sealed | INCONCLUSIVE(유방 HER2 0.599와 consistent) |
| 위 | ebv | 대체가능(부분) | 0.9477 (0.861–1.0) | 7 | 부족 | sealed | exploratory only |
| 대장 | msi_high | 대체가능 | 0.9184 (0.850–0.969) | 21 | 부족 | **retro** | 회고·consistent(held-out 아님) |
| 대장 | anti_egfr | 필수 | 0.7053 (0.620–0.783) | 84 | 충분 | **retro** | 회고·방향 consistent(misroute 0.416 최고) |
| 대장 | braf_v600 | 등급적/partial | 0.8817 (0.817–0.938) | 15 | 부족 | **retro** | 회고·consistent |
| 유방(anchor) | ER | 대체가능 | 0.901 | — | 내부 | anchor | 대체가능축 高 |
| 유방(anchor) | HER2 | 필수 | 0.599 | — | 내부 | anchor | 필수축 near-random(법칙 앵커) |
| 유방(anchor) | PAM50 | 아형 | 0.759 | — | 내부 | anchor | 아형 회복 中 |

## 결론 (정직한 bottom line — 이게 "확정")

1. **검정력 있는 sealed-forward 확증은 소수:** 양성대조(폐 histology 0.925 · 두경부 grade 0.815) + **두경부 HPV 0.959(n_pos=26)**. HPV가 "형태 상관물 有 → 대체가능(≥0.80)" 축의 **유일한 검정력 있는 확증**이며, 변이가 아닌 **바이러스축**이라 법칙을 새 종류로 확장.
2. **모든 변이/증폭축은 exploratory(n_pos<25) → INCONCLUSIVE.** 폐 EGFR/KRAS, 위 HER2-amp/MSI, 방향은 법칙과 일관하나 검정력 부족으로 확증·반증 불가. 유방 HER2(0.599)와 위 ERBB2-amp(0.644)가 "증폭≠형태" 방향으로 일치하나 위는 exploratory.
3. **위암 양성대조(Lauren) FAIL(0.54):** 위암 파이프라인 sanity가 서지 않음 → **위암 endpoint 전체는 저신뢰로 취급.** (파이프라인 문제 vs 데이터 희소 구분 필요.)
4. **대장은 회고적** → 검정력 있는 held-out 확증 집계에서 제외. 방향 일관까지만.
5. **법칙 = 방향적으로 일관(directionally consistent), 이분법 미확립(dichotomy NOT established).** 확립엔 검정력 있는 필수/변이축 확증(n_pos≥25) 축적 필요 — 현 코호트 크기론 대부분 도달 불가(구조적 한계).

## G1 상태 — ✅ **확정 (kkkim Leader 승인, 2026-07-14)**
- [x] held-out 4암종 + anchor 결과 산출·정본 수치 확정.
- [x] 대장 회고적 지위 명시(sealed-forward와 구분).
- [x] 정직 라벨링(검정력·지위·판정, 위암 양성대조 FAIL 명시).
- [x] **kkkim(Leader) 최종 "결과 확정" 승인(2026-07-14).** 결과셋 동결 = 이 스코어보드 + 각 `LAW_TEST.md` + DECISION_MAP. **이후 변경은 새 버전.**
- → **다음: braveji Critic(G2 나머지) 인계.** claim은 "법칙 방향 일관·이분법 미확립"으로 동결(승격 금지).

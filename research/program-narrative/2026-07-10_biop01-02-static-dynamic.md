# BIOP01 ↔ BIOP02 연결 서사 — 정적 + 동역학 → 치료효과 예측 (2026-07-10)

> 프로그램/그랜트/논문 Discussion용 서사. **새 데이터 불필요(서사 수준).** 실제 생물학 파이프라인은 향후(Paper C, 데이터 스쿱 별도).
> 근거: BIOP01 `blog/CONTENT_MAP.md`·FINDINGS(velocity 벤치), BIOP02 `research/paperA-positioning/*`(cost-of-substitution). 억지 직접 이식 금지 — ER+ 접점에서만 연결.

---

## 0. 한 문장
> **치료효과 예측은 두 축이 필요하다 — 정적 phenotype(BIOP02, 값싼 H&E→아형)와 조절 동역학(BIOP01, velocity·전사율 α). 둘은 ER+ 내분비 저항에서 정확히 만난다.**

## 1. 두 프로젝트 (사실)
- **BIOP02 (정적/공간):** H&E → foundation embedding → BRCA 분자아형 → 치료축 라우팅. 결과 = **cost-of-substitution 지도**(basal→H&E triage 안전 · HER2→분자검사 필수 · **ER+→불확실**).
- **BIOP01 (동역학/단세포):** RNA velocity 벤치(HSPC/BMMC, GSE209878). 결과 = **lag는 비robust(❌), 전사율 α는 robust(0.88)·예측 가능(+0.31, ✅)**. "무엇이 신뢰성 있게 예측되는가"의 엄밀한 경계 긋기 + 음성대조 + cross-dataset.

## 2. 공통 DNA (억지 아님)
둘 다 **"신뢰할 수 있는 신호 vs 없는 신호를 정직하게 가른다"**:
- BIOP01: lag ❌ / α ✅
- BIOP02: H&E로 HER2 ❌ / basal ✅ / ER+ 유보
→ 랩 시그니처 = **"무엇이 정말 예측 가능한지를 엄밀·정직하게 가른다"**(과잉주장 회피·음성대조·cross-dataset). 프로그램 서사의 축.

## 3. 치료효과 접점 = ER+ 내분비 저항 (구체적)
BIOP02 지도에서 **가장 불확실한 칸이 ER+/endocrine.** 그 불확실성은 **이중**(D1 흡수):
1. H&E 정적 스냅샷이 내분비 상태를 못 가름
2. 세포주 치료증거가 내분비를 체계적으로 못 잡음(positive control 1/8)

그런데 **내분비 저항은 본질적으로 동역학** — 세포가 시간에 걸쳐 저항 상태로 전이(state transition). **정적으론 원리적으로 못 잡고, velocity/kinetics로 잡는 문제.** BIOP01이 "**α(전사율/kinetics)는 robust·예측 가능**"을 보였다는 게 바로 이 handoff의 근거 — 신뢰 가능한 동역학 신호가 존재한다.

```
BIOP02 (정적):  H&E → subtype → 치료축
                     └─ ER+ 박스 = 이중 불확실(정적+세포주 한계) ──┐
                                                              ▼
BIOP01 (동역학): velocity·전사율 α(robust✅) → 상태 전이 예측
                     └─ 내분비 저항 궤적 = 동역학 문제 ◄──────────┘
```

**연결 명제:** "정적 병리(02)가 원리적으로 못 푸는 하드 문제(내분비 저항)를, 신뢰 가능한 동역학 신호(01의 α)로 넘긴다. 두 프로젝트는 ER+ 저항에서 만난다."

## 4. 세 수준 (정직: 서사 vs 실행)
| 수준 | 지금 가능? | 비고 |
|---|---|---|
| **프로그램/그랜트/Discussion 서사** | ✅ 지금 | 새 데이터 불필요. 두 논문 = 하나의 프로그램 |
| **실제 생물학 파이프라인**(BRCA 단세포 velocity로 내분비 저항 예측) | ⚠️ 향후 | BRCA scRNA/multiome + 내분비 저항 라벨 필요 → 공개데이터 스쿱 진행 중(별도) |
| 억지 직접 이식(HSPC 결과를 BRCA에 붙이기) | ❌ | 도메인 갭 — 안 함 |

## 5. 활용처 — **발표가 주 용도, 단독 논문 아님(결정 2026-07-10)**

⛔ **한 논문으로 묶지 않는다(억지).** BIOP01(velocity·HSPC·조혈)과 BIOP02(H&E·BRCA·병리)는 데이터·생물학·방법·질문이 달라, 한 논문이면 심사자가 "두 얘기를 스테이플로 찍었다"고 본다. 연결은 생물학적 파이프라인이 아니라 **프레이밍/서사**다.

**주 용도(우선):**
- ⭐ **발표 슬라이드(로드맵):** "우리가 못 푸는 칸(ER+)을 어떻게 풀 것인가" — 정적(02)이 남긴 하드 문제를 동역학(01)으로 넘김. 발표 마지막 "future/vision" 슬라이드.

**부차(선택):**
- **BIOP02 Paper A Discussion 한 문장:** ER+ 저항은 정적 한계 → 동역학 후속이 자연스럽다(단독 주장 아닌 future work 한 줄).
- **그랜트/프로그램 소개:** 랩의 두 축(정적 공간 × 동역학 단세포)이 치료효과 예측에서 수렴.

→ **논문 본체 X, 발표·그랜트 서사 O.**

## 6. 상태
기록 완료. **실행(Paper C)은 BRCA 내분비저항 단세포 공개데이터 존재 여부에 달림 → 스쿱 진행 중**(결과 오면 §4 중간행 go/no-go 갱신).
관련: `../paperA-positioning/2026-07-10_subtype-decision-map.md`, `../../experiments/kkkim/20260710_cost_of_substitution/endocrine_limitation.md`, BIOP01 `blog/CONTENT_MAP.md`.

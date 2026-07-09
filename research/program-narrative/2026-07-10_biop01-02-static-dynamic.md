# BIOP01 ↔ BIOP02 연결 서사 — 정적 + 동역학 → 치료효과 예측 (2026-07-10)

> 프로그램/그랜트/논문 Discussion용 서사. **새 데이터 불필요(서사 수준).** 실제 생물학 파이프라인은 향후(Paper C, 데이터 스쿱 별도).
> 근거: BIOP01 `blog/CONTENT_MAP.md`·FINDINGS(velocity 벤치), BIOP02 `research/paperA-positioning/*`(cost-of-substitution). 억지 직접 이식 금지 — ER+ 접점에서만 연결.

---

## 0. 한 문장
> **치료효과 예측은 두 축이 필요하다 — 정적 phenotype(BIOP02, 값싼 H&E→아형)와 조절 동역학(BIOP01, chromatin-lag은 비재현임을 반증하고 세운 robust·예측 가능한 전사율 α). 둘은 ER+ 내분비 저항에서 정확히 만난다.**

## 1. 두 프로젝트 (사실)
- **BIOP02 (정적/공간):** H&E → foundation embedding → BRCA 분자아형 → 치료축 라우팅. 결과 = **cost-of-substitution 지도**(basal→H&E triage 안전 · HER2→분자검사 필수 · **ER+→불확실**).
- **BIOP01 (동역학/단세포):** RNA velocity 다방법 대질(HSPC 10x Multiome, GSE209878). **벤치마크가 아니라 반증형 결론:** ① **chromatin→transcription lag은 method-robust하지 않다**(4방법 크기 |ρ|≤0.08·방향 48%≈우연·permutation-FDR 공집합) — "chromatin이 transcription을 prime한다"는 분야 가정 반증. ② **음성대조**: chromatin 셔플해도 lag 불변 → 모델 구조 아티팩트. ③ **건설적 대안**: 전사율 **α는 robust(ρ=0.88)·예측 가능(+0.31)**. ④ **메커니즘**: profile-likelihood로 lag은 목적함수가 데이터로 식별 못 함(α가 3.53× 민감, 94.57% 유전자) — 관찰을 메커니즘으로 설명. ⑤ **4개 외부 데이터셋 보존**. → 결론 = **"chromatin-lag은 식별 불가·비재현, α가 신뢰 가능한 예측 신호"**(cautionary+건설적 독립 논문감).

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
| **실제 생물학 파이프라인**(BRCA 단세포 velocity로 내분비 저항 예측) | ❌ **공개 데이터로는 불가**(2026-07-10 스쿱 확정) | 아래 §6.1 참조 — 예측 no-go, 특성화만 conditional, **새 paired-multiome 데이터 필요** |
| 억지 직접 이식(HSPC 결과를 BRCA에 붙이기) | ❌ | 도메인 갭 — 안 함 |

## 5. 활용처 — **발표가 주 용도, 단독 논문 아님(결정 2026-07-10)**

⛔ **한 논문으로 묶지 않는다(억지).** BIOP01(velocity·HSPC·조혈)과 BIOP02(H&E·BRCA·병리)는 데이터·생물학·방법·질문이 달라, 한 논문이면 심사자가 "두 얘기를 스테이플로 찍었다"고 본다. 연결은 생물학적 파이프라인이 아니라 **프레이밍/서사**다.

**주 용도(우선):**
- ⭐ **발표 슬라이드(로드맵):** "우리가 못 푸는 칸(ER+)을 어떻게 풀 것인가" — 정적(02)이 남긴 하드 문제를 동역학(01)으로 넘김. 발표 마지막 "future/vision" 슬라이드.

**부차(선택):**
- **BIOP02 Paper A Discussion 한 문장:** ER+ 저항은 정적 한계 → 동역학 후속이 자연스럽다(단독 주장 아닌 future work 한 줄).

→ **논문 본체 X, 발표 서사 O.**

> ⚠️ **"그랜트" 언급 철회(2026-07-10):** 이 서사는 그랜트 근거가 아니다. 현 상태(예비 결과+발표+오픈repo)는 그랜트 패키지가 아니고, PI/기관 자격·공모 매칭·강화된 예비데이터가 필요하다. **발표 서사에만 사용.**

## 6. 상태
기록 완료. **결론: 발표 서사로만 사용. 생물학 파이프라인(Paper C)은 공개 데이터로 실행 불가.**

### 6.1 Paper C 실행가능성 스쿱 결과 (2026-07-10, literature-scout)
- **near-scooped + 데이터 부족.** 최적 데이터셋 **GSE240112**(Genome Medicine 2024)가 **이미 tamoxifen-저항 환자 종양에 scVelo 적용** + 저항 환자 **n=3**(예측엔 태부족). 저항 라벨 있는 **paired same-cell multiome 없음** → chromatin-informed velocity(MultiVelo) 불가.
- **go/no-go:** 예측 주장 = **NO-GO(공개 데이터)**. α-특성화(GSE240112↔GSE122743 cross, BIOP01 α-robust 인용)만 **conditional-go**이나 scoop-adjacent("Genome Med 2024와 뭐가 다르냐"에 α-as-feature가 유일한 답).
- **결론: BIOP01↔02 생물학 연결은 공개 데이터로 설득력 있게 실행 못 함 → 새 paired-multiome(내분비요법하) 데이터 생성이 전제.** **공개 데이터만으론 결과가 아니라 서사.**
- 위협 논문: Zhou Genome Med 2024(GSE240112, 직격 스쿱) · Hong Nat Commun 2019(GSE122743, pseudotime) · bioRxiv 2026(저항 궤적, velocity 미사용). EstroGene2.0 등으로 단세포 저항 특성화는 crowded.
관련: `../paperA-positioning/2026-07-10_subtype-decision-map.md`, `../../experiments/kkkim/20260710_cost_of_substitution/endocrine_limitation.md`, BIOP01 `blog/CONTENT_MAP.md`.

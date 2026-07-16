# 논문 구조 결정 기록 — A/B/C 정리 (2026-07-17)

> **Leader(kkkim) 결정.** 이 문서는 Paper A·B·C의 관계를 확정하고, "무엇을 한 편으로 묶고 무엇을 보류하는가"를 한 곳에 못 박는다. 이후 이 문서가 정본이며, 흩어진 "Paper A" 라벨은 여기로 수렴한다.
> 선행 결정: `FLAGSHIP_PLAN.md`(D11/D12, 2026-07-12, A→C 흡수) · `PAPER_DIRECTION.md`(C 확정본) · `../therapeutic_layer_strengthening.md`(치료층 설계) · `../paperA-positioning/2026-07-10_subtype-decision-map.md`(前 Paper A).

---

## 0. 한 문장

**논문은 C 플래그십 하나로 수렴한다.** 유방(前 Paper A)은 이미 C의 anchor로 흡수됐고(D11/D12), C의 유일한 약점인 "후향적-only"를 메우기 위해 **B의 실제-결과 앵커(Yale)만 C에 흡수**한다. B의 무거운 약물-발견 엔진은 **조건부 보류(→ 가능한 별도 P2)** 한다.

---

## 1. 배경 — A와 C는 "겹침"이 아니라 이미 통합됨

### 1.1 A = C의 유방 슬라이스 (사실 확인)
前 Paper A(subtype 치료결정 지도)와 Paper C(다암종 치환가능성 지도)는 프레임·표·데이터·그림이 동일하다.

| | 前 Paper A | Paper C |
|---|---|---|
| 핵심 메시지 | "H&E-예측 아형으로 치료 시 HER2축은 항상 실패 = 분자검사 대체불가를 비용으로 증명" | "H&E가 분자검사를 언제 값싸게 대신하나 = 치환가능성 결정지도" |
| 프레임 | cost-of-substitution (예측 ≠ 대체) | cost-of-substitution (예측 ≠ 대체) — **동일** |
| 표 | subtype 지도(유방 수용체축) | 표2 라우팅 치환비용의 **"유방 수용체" 한 행** |
| 데이터·그림 | `experiments/kkkim/20260710_cost_of_substitution/` (Fig2 confusion×distance) | C의 유방 anchor 그림 = **바로 그것** |

前 Paper A 문서 스스로 §6에서 "cross-cancer 일반화 = Paper C 후보"라 명시한다. 즉 A는 자기가 C의 유방 사례임을 인정한다.

### 1.2 이미 내려진 결정 (D11/D12, 2026-07-12)
`FLAGSHIP_PLAN.md`: **"유방(Paper A)을 별도로 두지 않고 cross-cancer 결정지도 논문의 anchor 암종으로 흡수. 유방 단독 Paper A의 서명된 정체성은 flagship의 anchor 챕터로 대체된다."** (사유: breast-only 예측은 Fernandez-Romero 2026에 스쿱.)

→ **A는 독립 논문이 아니다. C의 anchor 챕터다.**

### 1.3 드리프트 (정리 대상 = 결정 4-A)
D11/D12 이후에도 실무 라벨이 안 따라왔다: HANDOFF "Paper A + Paper C 두 트랙", FIGURES_INDEX.md 제목 "Paper A", Fig2(BIOP02-91) "Paper A" 라벨. 이 드리프트가 "A라는 독립 논문이 있다"는 착각·중복작업을 유발한다 → 본 문서 기준으로 통일.

---

## 2. 진짜 남은 결정 — B의 운명

A가 C에 있으므로, 실제 결정은 **B(치료증거 트랙)를 어떻게 하느냐** 하나다. B를 두 부분으로 분리해서 본다.

- **B-① 실제-결과 앵커:** Yale HER2+/trastuzumab pCR로 "H&E-유래 항HER2 축이 실제 치료결과를 층화하나" 검정(개방 데이터, `../therapeutic_layer_strengthening.md` Exp-OUTCOME).
- **B-② 무거운 엔진:** DepMap/GDSC 약물가설 + 3축 수렴(CRISPR·LINCS) + TNBC repurposing(`endocrine_rule.py`, PR #44 파이프라인).

### 결정 1 — Yale 실제-결과 앵커를 C에 넣나 → **[선택: 1-A] 본문 포함, 지금 추진**

| 선택지 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **★A. 본문 포함(선택)** | frozen 파이프라인→Yale H&E→항HER2 축→pCR 층화, C 유방 anchor에 삽입 | C의 유일 약점(후향적) 해소·킬러질문 방어·IF 상향 조건 충족·개방데이터+임베딩1회로 저비용 | C가 mid-flight라 지연 위험·HER2 blind면 음성결과(확인적)·검증 축 설계검토 필요 |
| B. revision용 준비 | 분석만 해두고 코어 블로커 아님 | 코어 일정 무손상·위험 최저 | 초기 제출 임팩트 기여 못함 |
| C. 안 넣음 | 순수 후향적 지도 | 가장 빠름 | "so what·전향검증 필요" 취약점 그대로 |

### 결정 2 — B 무거운 엔진 처리 → **[선택: 2-B] 조건부 보류**

| 선택지 | 내용 | 장점 | 단점 |
|---|---|---|---|
| A. 지금 별도 2편 | 약물가설+수렴+repurposing 독립 논문 | 성공 시 추가 출판·jhans 트랙 활용 | Dawood 2024 스쿱 인접·무겁고 불확실·C 지연 |
| **★B. 조건부 보류(선택)** | 지금 멈추고, TNBC KB-novel 수렴 히트가 실제로 나오면 P2 | 스쿱·무게 리스크 회피·C 집중·옵션 유지 | jhans 할 일 재배치 필요·엔진 코드 유휴 |
| C. 완전 폐기 | 트랙 종료 | 가장 단순 | 기투입(BIOP02-52/60/89) 매몰 |

### 결정 3 — jhans 재지정 → **[자동 확정: 3-A] Yale 앵커로 전환**
1-A(Yale 활성) + 2-B(엔진 보류)이면 3은 논리적으로 3-A만 남는다(3-C는 2-B와 모순, 3-B는 어정쩡). jhans = Therapeutic Evidence Agent이므로 "치료축이 실제결과를 예측하나"(Yale)는 그 역할의 정중앙이다.

### 결정 4 — 라벨 드리프트 정리 → **[선택: 4-A] 지금 통일**
"Paper A" → "C 유방 anchor"로 문서 통일. 정본 = 본 문서.

---

## 3. 확정 구조 + 흐름도

```
            H&E → 분자 예측  (분야 포화·스쿱: Fernandez-Romero 2026, Dawood 2024)
                    │
                    ▼
        cost-of-substitution 프레임   ("예측된다" ≠ "임상적으로 대체 가능하다")
                    │
   ┌────────────────┴─────────────────────────────────────────────┐
   │                                                               │
   ▼  [플래그십 — 논문 1편으로 수렴]                                  ▼  [B 무거운 엔진]
 Paper C                                                      약물가설·repurposing
 다암종 치환가능성 결정지도                                     ·CRISPR·LINCS 수렴
 · 형태학적 상관물 법칙(사전등록)                                     │
 · 5암종: 유방(anchor)·폐·대장·위·두경부                              │ [결정 2-B] 보류
 · AI 기권/보정 레이어                                                ▼
   │                                                          조건부 별도 P2
   │   ▲ [D11/D12] 흡수                                       (repurposing 실측 나오면)
   │   └── 유방 = 前 Paper A (anchor 챕터)                     아니면 폐기
   │
   ▼  [결정 1-A] 실증 이빨 추가
 Yale 실제 pCR 앵커
 (항HER2 축 → 실제 trastuzumab 결과 층화)
   │
   ▼
 후향적 결정지도  →  실제-결과로 검증된 결정지도
```

**핵심 논리 사슬:** C의 최대 약점은 "후향적-only"(자기 문서에 명시) → 리뷰어 킬러질문("골드스탠다드 이미 있는데?")에 취약 → **Yale 앵커가 C anchor의 헤드라인 주장(HER2 대체불가)에 실제-결과 검증을 달아 지도를 실증으로 격상** → IF 스트레치 조건 충족.

---

## 4. 액션 아이템 (누가 · 무엇)

| # | 담당 | 할 일 | 상태 |
|---|---|---|---|
| A1 | kkkim | 본 결정 문서 = 정본. 라벨 드리프트 정리(FIGURES_INDEX 등) | 이 PR |
| A2 | kkkim | Yale 코호트(TCIA HER2-TUMOR-ROIS, 개방 ~40GB) 확보·타일·UNI 임베딩 | 대기 |
| A3 | sjpark | frozen phenotype 모델을 Yale 임베딩에 적용(항HER2 축 점수 산출) | 대기 |
| A4 | jhans | **[전환]** Yale 앵커 소유 — 항HER2 축 점수 → pCR 층화(AUROC+bootstrap CI, DeLong vs HER2-prob baseline), 반증조건 보고 | 재지정 |
| A5 | jhans | PR #44(약물가설 파이프라인) **park**(엔진 보류, 병합 안 함). BIOP02-52/60 산출은 P2용 보존 | 보류 |
| A6 | sjpark | 앞서 요청한 TCGA 4-endpoint CSV(BIOP02-80 c.11216)는 **엔진용이었으므로 hold**(급하지 않음) | 재조율 |
| A7 | braveji | Yale 앵커 = 새 결과주장 → Critic 대상(사전등록 반증조건 봉인 후) | 이후 |

---

## 5. 정직한 전제 · 리스크 (원고/검토에 명시)

1. **Yale 앵커의 과학적 적합성은 설계 검토 필요.** HER2가 진짜 blind면 H&E-유래 항HER2 축이 pCR을 **못 층화**할 수 있고, 이는 "분자검사 필수"를 **강화하는 정직한 음성**이라 C 논지와 일관되나 화려한 양성은 아니다. 어느 축(항HER2 vs 대체가능축)을 결과검증할지가 설계 핵심.
2. **C는 mid-flight**(법칙 held-out 진행 중) — Yale 추가는 지연 리스크. 1-A는 "코어 블로커"가 아니라 "본문 add / 안 되면 revision 강화"로 운용.
3. **B 엔진 보류는 매몰이 아님** — BIOP02-52(consistency)·60(endocrine rule)·89(pipeline)은 P2 착수 시 재사용. repurposing 실측(KB-novel 수렴 히트)이 나올 때만 P2 승격.
4. **모든 산출 hypothesis_only, 후향적, 전향적 검증 필요**(Yale pCR도 코호트 수준 층화지 개인 benefit 아님).

---

## 6. 관련 문서
- 흡수 결정: `FLAGSHIP_PLAN.md`(D11/D12) · C 확정본: `PAPER_DIRECTION.md`
- Yale 앵커 설계: `../therapeutic_layer_strengthening.md`(Exp-OUTCOME, §A) · 데이터: TCIA HER2-TUMOR-ROIS(개방)
- 前 Paper A: `../paperA-positioning/2026-07-10_subtype-decision-map.md` (= C 유방 anchor) · Fig2: `../../experiments/kkkim/20260710_cost_of_substitution/`
- 사전등록 법칙: `../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md`

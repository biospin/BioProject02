# 통합 Flagship 논문 계획 — Cross-cancer H&E 치환비용 결정지도

> **리더 결정(kkkim, 2026-07-12): 옵션 1 통합 flagship 확정.** 유방(Paper A)을 별도로 두지 않고 cross-cancer 결정지도 논문의 anchor 암종으로 흡수. 아래 거버넌스 주의 참조.
> 근거: breast-only 예측은 스쿱(Fernandez-Romero 2026이 CPTAC HER2 열화까지 이미 출판, IF 4-6). cross-cancer 치환비용 결정지도가 구별되는 기여. "오래 끌지 않고 하나의 강한 논문으로 수렴"(사용자).

## 거버넌스 주의 (기록)
CLAUDE.md는 A/B를 Paper B까지 BRCA-only, pan-cancer=Paper C 별도 트랙(리더 승인)으로 명시. 이 통합은 그 계획을 재편하며, **리더(kkkim)가 통합을 승인**함으로써 성립한다. 유방 단독 Paper A의 서명된 정체성은 flagship의 anchor 챕터로 대체된다. 팀 공유·저자 확정은 사람 승인 게이트 유지.

## 기여 문장 (이게 곧 논문의 정체성 — 파이프라인 아님)
> H&E→분자 예측이 포화된 상황에서, 이 분야는 "예측된다"를 "임상적으로 대체 가능하다"와 혼동해 왔다. 우리는 치료 결정 경로에서 **H&E가 분자검사를 언제 값싸게 대신할 수 있는지의 다암종 결정지도**를 제시하고, 그 경계가 **형태학적 상관물의 유무**라는 사전등록 법칙으로 예측됨을 보인다. 멀티에이전트 파이프라인은 인프라이며 기여가 아니다.

## 스토리 아크
1. 갭: 예측 포화 ≠ 치환 가능. 아무도 치환 경계를 지도화하지 않음.
2. 틀: cost-of-substitution — 예측충실도(표1)와 라우팅 치환비용(표2) 분리, 절대 융합 안 함.
3. 법칙: 형태학적 상관물 유무가 치환가능성을 결정(사전등록 `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`).
4. 다암종 증거: 유방(HER2 예측되나 치료축 blind)·대장(MSI 저 vs RAS 고)·폐(EGFR 등급적, held-out 법칙 검정).
5. 메커니즘: ST(유방 ERBB2 floor, 대장 MSI-면역 공존 / RAS-조용).
6. 도메인 취약성: CPTAC 붕괴(염색·특징공간 시프트) → 치환은 도메인 조건부.
7. 결정 시스템 레이어(AI 기여): 치환가능성 스코어 + 보정/기권 + (stretch) VoI 검사주문 정책.
8. 함의: 검사 주문 결정지원 지도. hypothesis-only, 전향적 검증 필요.

## AI 레이어 (사용자 확정 방향)
- ✅ **치환가능성 스코어 지수**: (cancer, marker)별 = f(예측 AUROC, 라우팅 오배정비용, 형태상관물 강도, 도메인강건성). 지도를 정량 산출물로.
- ✅ **보정 + 기권(selective prediction/conformal)**: OOD·불확실 시 기권→분자검사. CPTAC 붕괴에 대한 직접 답. repo olsson-2022 conformal 렌즈 활용.
- ⏳ **VoI 비용민감 결정정책(stretch)**: 환자별 "H&E 믿기 vs 검사 주문"을 기대비용 최소화로. 시간 되면.
- ❌ **RL 제외**: 단일스텝·후향적이라 미스매치, gimmick 감점 위험. VoI/결정이론으로 환원.
- ⚠️ DRP 경계: VoI는 "분자검사 주문 여부"에만. "어떤 약"에 걸면 금지선.

## 저널 (상향)
- 모달 IF ~6-12: npj Precision Oncology, Genome Medicine, EBioMedicine, Cell Reports Medicine.
- 스트레치 ~12-16: Nature Communications, npj Digital Medicine, Med. (법칙이 예측적으로 서고 3암종 깨끗할 때, + AI 결정레이어가 "새 능력"으로 읽힐 때.)
- 비현실(20+): 전향적 검증/새 능력 필요 — 제외.

## 성공 조건부
- **폐 안착**: 임베딩 완료(844/1053) + subtype 라벨(SUBTYPE 공란 → SSP 계산). 깨끗한 3암종 = 한 티어 위. 폐 subtype 실패 시 유방+대장 2암종으로도 성립하게 설계(폐는 변이축만이라도).
- **법칙이 held-out(폐)에서 확증**되어야 discovery 급.

## 다음 작업 (의존성)
1. [진행] 대장 ST 두 반쪽 / mean_cost 사전등록 / shuffle-null 5-seed / 폐 임베딩.
2. [대기] 폐 subtype SSP 계산 → 폐 라벨→split→MIL(법칙 held-out 검정).
3. [결과 안착 후] AI 레이어: 스코어 지수 + 보정/기권 구현.
4. [후] Critic 7항목 → figure → 통합 원고(manuscript-writer) → paper-critic.

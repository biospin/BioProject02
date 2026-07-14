# 통합 Flagship 논문 계획 — Cross-cancer H&E 치환비용 결정지도

> **리더 결정(kkkim, 2026-07-12): 옵션 1 통합 flagship 확정.** 유방(Paper A)을 별도로 두지 않고 cross-cancer 결정지도 논문의 anchor 암종으로 흡수. 아래 거버넌스 주의 참조.
> 근거: breast-only 예측은 스쿱(Fernandez-Romero 2026이 CPTAC HER2 열화까지 이미 출판, IF 4-6). cross-cancer 치환비용 결정지도가 구별되는 기여. "오래 끌지 않고 하나의 강한 논문으로 수렴"(사용자).

## 거버넌스 주의 (기록)
CLAUDE.md는 A/B를 Paper B까지 BRCA-only, pan-cancer=Paper C 별도 트랙(리더 승인)으로 명시. 이 통합은 그 계획을 재편하며, **리더(kkkim)가 통합을 승인**함으로써 성립한다. 유방 단독 Paper A의 서명된 정체성은 flagship의 anchor 챕터로 대체된다. 팀 공유·저자 확정은 사람 승인 게이트 유지.

## 암종 선정 근거 (리뷰어 필수 질문 — 근거는 `research/paperA-positioning/2026-07-10_future-crosscancer-data.md`)
선정 기준: 후보 암종은 **표적/H&E-blind 축**과 **형태학/H&E-triageable 축**을 **둘 다** 가져야 한다(치환비용의 전 범위를 stress-test하기 위해). 6개 후보를 랭킹했다.

| 순위 | 암종 | 표적축(blind) | 형태학축(가시) | 판정 | 채택? |
|---|---|---|---|---|---|
| 1 | 폐 NSCLC | EGFR/ALK/KRAS | LUAD/LUSC 조직형 | Excellent | ✅ anchor |
| 2 | 대장 CRC | BRAF/RAS | MSI-H(부분 형태) | Excellent | ✅ (중간비용 calibration) |
| 3 | 위 STAD | HER2-amp(유방 직접 평행)·MSI | Lauren·signet-ring·EBV | Strong, **CPTAC ~20슬라이드 빈약** | ⏳ 미채택(외부검증 약) |
| 4 | Glioma | 1p19q·MGMT·EGFRvIII | IDH·grade | Strong, 약리 얇음·표적 아닌 진단축 | ❌ |
| 5 | 자궁내막 UCEC | POLE·HER2 | serous/endometrioid | CPTAC 우수하나 세포주 얇음 | ❌(검증용만) |
| 경계 | 흑색종 SKCM | BRAF-V600 | (형태 아형 약함) | WSI ~107·CPTAC 없음 | ❌ |

**왜 폐+대장:** 폐=가장 깨끗한 이중축(EGFR blind vs LUAD/LUSC 가시, ~1053슬라이드, CPTAC 페어). 대장=MSI 뉘앙스가 **중간비용**을 줘 metric calibration 가능(BRAF 고 vs MSI 중 vs 조직형 저). 둘이 치환비용 전 범위를 커버. ALK는 세포주 게이트 NO-GO(n=2)로 드롭(D1).

**미채택 사유(정직):** 위암은 서사 최강(HER2-amp→trastuzumab = 유방 HER2 문자 그대로 복제)이나 외부검증 CPTAC-STAD ~20슬라이드로 빈약. Glioma는 마커가 진단/예후성이라 치료라우팅 프레이밍에 부적합. 자궁내막·흑색종은 데이터/축 결함.

**flagship 확정(D12, 2026-07-12): 5개 암종 = 유방(anchor) + 폐 + 대장 + 위 + 두경부.** 위암=법칙 최강 교차장기 검정(HER2-amp가 다른 장기서도 blind면 유방 HER2 복제, TCGA-STAD 내부 split), 두경부=바이러스(HPV)라는 새 종류의 형태-가시 축. 이 선까지가 "넓히되 pan-cancer 아틀라스로 안 흩는" 경계. 위 STAD ~440·HNSC ~523 슬라이드. HPV(HNSC)·EBV(STAD)·아형 라벨은 마커논문/유도로 조달(폐 SSP 패턴). 법칙 예측은 결과 전 봉인됨(`SUBSTITUTABILITY_LAW_PREREGISTRATION.md`).

## 기여 문장 (이게 곧 논문의 정체성 — 파이프라인 아님)
> H&E→분자 예측이 포화된 상황에서, 이 분야는 "예측된다"를 "임상적으로 대체 가능하다"와 혼동해 왔다. 우리는 치료 결정 경로에서 **H&E가 분자검사를 언제 값싸게 대신할 수 있는지의 다암종 결정지도**를 제시하고, 그 경계가 **형태학적 상관물의 유무**라는 사전등록 법칙으로 예측됨을 보인다. 멀티에이전트 파이프라인은 인프라이며 기여가 아니다.

## 스토리 아크
1. 갭: 예측 포화 ≠ 치환 가능. 아무도 치환 경계를 지도화하지 않음.
2. 틀: cost-of-substitution — 예측충실도(표1)와 라우팅 치환비용(표2) 분리, 절대 융합 안 함.
3. 법칙: 형태학적 상관물 유무가 치환가능성을 결정(사전등록 `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`).
4. 다암종 증거: 유방(HER2 예측되나 치료축 blind)·대장(MSI 저 vs RAS 고)·폐(EGFR 등급적, held-out 법칙 검정).
5. 메커니즘: ST(유방 ERBB2 floor, 대장 MSI-면역 공존 / RAS 상관물 부재).
6. 도메인 취약성: CPTAC 붕괴(염색·특징공간 시프트) → 치환은 도메인 조건부.
7. 결정 시스템 레이어(AI 기여): 치환가능성 스코어 + 보정/기권 + (stretch) VoI 검사주문 정책.
8. 함의: 검사 주문 결정지원 지도. hypothesis-only, 전향적 검증 필요.

## AI 레이어 (사용자 확정 방향)
- ✅ **치환가능성 스코어 지수**: (cancer, marker)별 = f(예측 AUROC, 라우팅 오배정비용, 형태상관물 강도, 도메인강건성). 지도를 정량 산출물로.
- ✅ **보정 + 기권(selective prediction/conformal)**: OOD·불확실 시 기권→분자검사. CPTAC 붕괴에 대한 직접 답. repo olsson-2022 conformal 렌즈 활용.
- ⏳ **VoI 비용민감 결정정책(stretch)**: 환자별 "H&E 믿기 vs 검사 주문"을 기대비용 최소화로. 시간 되면.
- ❌ **RL 제외**: 단일스텝·후향적이라 미스매치, gimmick 감점 위험. VoI/결정이론으로 환원.
- ⚠️ DRP 경계: VoI는 "분자검사 주문 여부"에만. "어떤 약"에 걸면 금지선.

## SOTA 다중 FM 견고성 (법칙의 모델 비의존성 — 최대 IF 레버)
목적: "HER2/RAS 형태학적 상관물 부재"에 대한 "더 센 FM이면 보일 것" 반박을 선제 차단. 핵심 마커(HER2·MSI·all-RAS)를 여러 프런티어 FM으로 재임베딩해 패턴(HER2 near-random, MSI 높음)이 **모델 비의존**임을 입증.
- **현재 SOTA(검색 2026-06)**: Virchow2(0.82) > UNI2(0.79) > Prov-GigaPath(0.787). Virchow2·UNI2가 표현공간 가장 이질적(상보). Virchow2는 stain-norm 후 slide-특이성 최저 → CPTAC 도메인/기권 서사와 직결.
- **접근권(BIOP02-24, 2026-05-17 승인 / 2026-07-12 서버 토큰 재확인)**: **Virchow2·UNI2-h·Prov-GigaPath·UNI·CONCH 전부 접근 OK**(HF 계정 irobii/kkkim@cytogenlab.com, 기관 이메일). **신청 불필요.** 로컬 미다운로드일 뿐 → 필요 시 weights 다운로드만 하면 됨. EXAONE=coords 비호환(블로커).
- **구현**: coords 영구저장(LUNG 941·STAD 187·COLORECTAL 622) → 재다운로드+재추출(재타일 불필요). **폐 임베딩 완료 후** 착수(다운로드 병목이라 폐 우선 침해 금지). 핵심 마커 서브셋만.
- **FM 앙상블도 blind(blind 마커 천장 방어)**: HER2/RAS에 SOTA FM 여러 개(UNI+Virchow2+Prov-GigaPath) + 좋은 MIL을 **앙상블해도 여전히 ≈chance**임을 보임 → "약한 모델 아티팩트" 반박 차단. **blind 축 한정·방어용**(성능 경쟁 아님, 과적합 주의: 얇은 양성엔 스태킹 금지). 가시 축엔 불필요.
- 스코프: 성능 자랑 아님. 법칙 견고성만. hypothesis_only.

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

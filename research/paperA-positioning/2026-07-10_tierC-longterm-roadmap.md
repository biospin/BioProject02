# Tier C 장기 로드맵 — 다른 병리 이미지 modality (2026-07-10)

> 작성: kkkim (Leader). **이번 발표(PseudoCon 2026)에는 미포함** — 장기 트랙(Paper B 이후 or 별도).
> 목적: H&E 너머 modality(공간/다중)로 **진짜 novelty 천장**을 여는 계획. A(치료 cost-map)·B(endpoint 전환)는 별도 문서.
> 원칙: 기존 자산(타일링·임베딩·MIL·Critic) 재사용 최대화, 신규 데이터 획득은 **공개 코호트 우선**(생성 회피).

---

## 0. 왜 Tier C인가 (한 줄)
H&E는 "분자 아형을 되맞히는" 데선 crowded·천장 비김. **bulk 분자검사가 못 보는 공간 정보**(단세포 위치·면역 아키텍처·세포-세포 상호작용)는 다중/공간 이미지가 직접 봄 → 최고 novelty. 단 **새 데이터 + 새 파이프라인 = 고비용**이라 장기.

## 1. 후보 modality (novelty × 비용)

| Modality | 무엇을 봄 | novelty | 진입 비용 | 공개 유방 데이터(검증 필요) |
|---|---|---|---|---|
| **mIF / IMC**(다중면역형광·질량세포) | 단세포 공간 단백질(30–40 마커), 면역 아키텍처 | 높음 | 중–고 | METABRIC-연계 IMC(Ali 2020 / Danenberg 2022), Jackson 2020 Nature |
| **공간 전사체**(Visium/Xenium) | 공간 유전자발현(spot/단세포) | 매우 높음 | 고 | 10x Xenium Breast, HTAN breast, 일부 GEO |
| **H&E→분자 공간 예측**(bridge) | H&E에서 공간 오믹스 *추정* | 높음(방법론) | **낮음**(H&E만, 라벨=공간오믹스) | 위 코호트에 H&E 페어 있으면 |

→ **주목: 세 번째(H&E→공간오믹스 예측)** 는 우리 기존 H&E 파이프라인을 그대로 쓰면서 라벨만 공간오믹스로 바꾸는 것 → **Tier C 중 유일하게 저비용**. 단 H&E-공간오믹스 페어 코호트 필요.

## 2. 단계별 계획 (phased, 각 단계에 go/no-go)

**Phase 0 — 데이터 정찰 (저비용, 수 주):**
- 공개 유방 mIF/IMC/공간전사체 코호트의 **가용성·규모·H&E 페어·라이선스** 실측(literature-scout/general-purpose). 
- go/no-go: H&E 페어 + 사용가능 라벨이 n≥수십 규모로 존재하는가.

**Phase 1 — 저비용 bridge 파일럿 (H&E→공간오믹스 예측):**
- 기존 임베딩 파이프라인 재사용, 라벨=공간오믹스(예: 면역 셀 밀도·특정 유전자 공간패턴).
- 우리 강점(Critic 거버넌스·외부검증 엄밀성)을 그대로 이식.
- go/no-go: H&E가 공간 신호를 bulk보다 잘 예측하는가(orthogonal 입증).

**Phase 2 — 신규 modality 직접 분석 (고비용):**
- IMC/공간전사체 자체를 입력으로(새 파이프라인·전처리·정규화). GPU·학습곡선 큼.
- 협업(데이터 보유 랩) 또는 대형 공개셋 전제.

**Phase 3 — 통합(H&E + 공간)·치료 연결:**
- Tier A(치료 cost-map)를 공간 맥락으로 확장(면역 아키텍처 → 면역치료 가설, 단 ICI 세포주 전이 금지 규칙 유의 → 세포주 아닌 다른 근거 필요).

## 3. 자산 재사용 지도
- **재사용:** 타일링·foundation embedding·attention MIL·Critic 7항목·registry 스키마·외부검증 프로토콜.
- **신규 필요:** 데이터(공개 코호트), modality별 전처리(IMC 채널 정규화/공간전사체 정렬), 평가지표(공간 상관·셀-이웃 통계).

## 4. 리스크 / 전제
- **데이터가 병목**(H&E와 달리 우리 코호트에 없음). Phase 0에서 실패하면 협업 없이는 진행 불가.
- BRCA-only·hypothesis_only·DRP 금지 규칙 유지. ICI/pembro 세포주 전이 금지 → 면역치료 연결은 세포주 아닌 근거 설계 필요.
- GPU·인력: 활동멤버 3인·마감(~9월) 고려 시 Phase 2+는 현 스프린트 밖.

## 5. 타임라인 제안 (장기)
- **지금~발표:** Tier C는 **Phase 0 정찰만**(저비용) 병행 가능, 실행은 발표 후.
- **발표 후(Paper A 제출 뒤):** Phase 1 bridge 파일럿 착수 검토 → Paper B/C 트랙.
- Tier A(치료 cost-map)·Tier B(endpoint 전환)가 발표·Paper A 우선, Tier C는 그 위 장기 확장.

## 6. 다음 액션 (사용자 결정 시)
- [ ] Phase 0 데이터 정찰 발행(공개 유방 mIF/IMC/공간 코호트 + H&E 페어 실측) — 저비용, 발표와 병행 가능
- [ ] H&E→공간오믹스 bridge의 스쿱 확인(이미 하는 그룹?)
- [ ] 협업 가능 랩(공간 데이터 보유) 탐색 여부 결정

> 이 문서는 계획만. 실행은 발표/Paper A 이후 별도 착수. 관련: `2026-07-10_novelty-scoop-analysis.md`(A·B 근거), `2026-07-10_research-plan.md`(Tier A 실험).

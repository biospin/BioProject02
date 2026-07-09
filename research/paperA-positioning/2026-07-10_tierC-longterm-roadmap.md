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

---

## 7. Phase 0 정찰 결과 (2026-07-10 실측) — **NO-GO (standalone 트랙)**

**핵심: 저비용 H&E→공간 bridge는 데이터가 막혔거나 이미 스쿱됨.**
- **공개 유방 IMC 대코호트에 paired H&E 없음(검증):** Danenberg 2022(693환자, 37마커 IMC)·Jackson 2020(352환자)은 **TMA 코어**라 H&E는 병리사 영역선택용일 뿐 co-registered H&E 미공개. → bridge 불가, direct-IMC(신규 파이프라인·H&E 재사용 0)만 가능.
- **paired H&E+단세포공간이 공개된 곳(10x Xenium / HEST-1k breast)은 n≈4 환자** — 코호트 학습 불가.
- **정확한 play가 이미 출판:** **Path2Space (Cell 2026-04)** — H&E→공간전사체, **976 TCGA-BRCA에 추론**, TME 아형+생존, **화학·trastuzumab 반응 예측**. 우리가 노린 "외부 paired 학습→TCGA 추론→치료 연결"의 직격 스쿱. (bioRxiv 2024.10.16.618609 / DOI 10.1016/j.cell.2026.04.023)
- 인접 스쿱: HEST-1k 벤치(NeurIPS 2024, Mahmood), HistoPlexer(H&E→IMC, 단 melanoma), BC immune-phenotype from H&E(arXiv 2404.16397).

**Phase 1 판정: NO-GO** (standalone 신규 modality 트랙). 남은 whitespace = 얇음(비-ICI·비-response 순수 기술적 spatial-immune→pathway-drug 연관, hypothesis_only) → Path2Space 뒤에서 방어 가능한지 불확실.

**대안(권고):** Tier C를 **검증 add-on**으로 격하 — 발표/Paper A의 **보조 그림**으로만 사용(예: 공개 H&E→ST 모델로 우리 TCGA-BRCA 임베딩을 주석해 subtype 지도를 공간적으로 뒷받침). 헤드라인 트랙 아님.
- 데이터 진입점(최소): **HEST-1k breast**(HF, CC-BY-NC-SA, UNI/CONCH 동일 랩 → 도구 호환) — 벤치 규모지만 add-on엔 충분.
- 착수 전 확인: Zenodo 레코드별 라이선스, Path2Space 코드/가중치 공개 여부(공개면 우리 add-on 비용 급감).

**결론:** A(발표)·B(pCR)에 이어 **C도 standalone으론 막힘** — 스쿱/데이터. C는 "발표 후 보조 검증"으로만 살려둔다. 3개 트랙 전수 확인 결과 **Paper A(cost-of-substitution)가 유일한 헤드라인**.

### 7.1 C 검증 add-on 실행안 (기록 — **DEFERRED, Paper A 코어 후 착수**)

**목적:** Paper A의 subtype 치료결정 지도를 **공간적으로 뒷받침하는 보조 그림**. 헤드라인 아님, hypothesis_only, 순수 기술적(비-ICI·비-response — Path2Space 재현 회피).

**가설(검증용):** H&E-예측 아형/치료축이 **공간 TME 구조와 일관**되면, cost 지도의 "형태학이 보는 것/못 보는 것"이 생물학적으로 뒷받침됨. 특히 **HER2 축이 형태학적으로 안 보이는 것**이 공간 데이터에서도 확인되는가.

**접근(택1, 비용순):**
1. **HEST-1k breast(외부 sanity, 최소비용):** HF `MahmoodLab/hest`(CC-BY-NC-SA, UNI/CONCH 동일 랩→도구 호환). breast Visium/Xenium 소수 샘플에 우리 임베딩 파이프라인 적용 → H&E 임베딩 vs 공간 셀타입 조성 상관. n 작음(≈4~20) → **sanity/보조만**.
2. **공개 H&E→ST 모델로 TCGA-BRCA 주석(add-on 그림):** Path2Space 등 **가중치 공개 시** 우리 TCGA-BRCA WSI에 추론 → 아형별 공간 TME 특징 → cost 지도와 대조(예: chemo-안전 축=면역-hot? HER2-무용 축=특정 공간패턴?). **주의: response 예측은 안 함**(스쿱·DRP 금지).

**데이터/도구:** 기존 TCGA-BRCA WSI+임베딩(재사용), HEST-1k(HF), Path2Space 코드/가중치(공개 여부 미확인).

**Go 조건:** (i) Path2Space(또는 대안 H&E→ST)의 **가중치·코드 공개** 확인 → 있으면 접근 2, 없으면 접근 1만. (ii) Paper A 코어(receptor 라우팅 완성) 후 착수.

**산출:** Paper A supplementary 1개 그림(공간 뒷받침) + 1문단. 별도 논문 아님.

**스코프 가드:** hypothesis_only·BRCA-only·DRP 금지·ICI/pembro 금지. 기술적 상관·조성만, 반응/추천 금지.

**상태:** 기록 완료, **미착수.** 재개 트리거 = Paper A receptor 라우팅 확정 + Path2Space 가중치 공개 확인.

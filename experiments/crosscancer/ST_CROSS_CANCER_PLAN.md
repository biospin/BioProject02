# Cross-cancer ST(공간전사체) 추가 분석 — 결정·시퀀스 추적

> 2026-07-12, 사용자 결정. 세션이 바뀌어도 이 순서대로 이어서 진행할 것.
> 관련: `PROGRESS_DECISIONS.md` D9(ST 트랙 지금 개설 X)·D10(유방 Angle A 착수) · `experiments/kkkim/angle_A_spatial_erbb2/`(유방 ERBB2 floor) · `research/paperA-positioning/2026-07-11_HE-ST-scoop-and-angles.md`.

## 배경 — 유방 ST의 위치
유방 ST(Angle A)는 **ST 트랙이 아니라 전용 방어 그림**이다. HER2가 왜 H&E-blind인지를 메커니즘으로 grounding: HER2+ 유방 ST(Andersson 2021)에서 종양 spot ERBB2가 배경 수준까지 겹치는 공간 floor(Θ 중앙 0.158, CI 0배제 8/8). D9에서 "cost-of-substitution은 ST 불필요"를 이미 확정했고, Angle A는 그럼에도 값싼 헤드라인 강화용으로만 착수했다.

## 대장·폐 ST — 필요성 판단
- **핵심 cross-cancer 주장(치환비용 비대칭)에는 ST 불필요.** 증거는 H&E→마커 MIL AUROC 비대칭(진행 중, `mil_cms_fidelity.json`·`routing_cost.json`).
- **높은 가치의 단 하나 = 대장 MSI-가시 / RAS 상관물-부재 공간 대조**(Angle A의 대장 격):
  - RAS/EGFR-경로 발현이 공간적으로 존재하나 형태학적 상관물이 없음 → ERBB2 floor 대칭, 항EGFR 축 고비용의 메커니즘 근거.
  - MSI-면역 시그니처가 형태학적 TIL과 공간 공존 → 형태 상관물 존재, 저비용의 메커니즘 근거.
  - 효과: 비대칭이 상관관계가 아니라 **메커니즘**이 됨(유방 ERBB2 floor와 완전 대칭).
- **폐는 낮은 우선순위** — EGFR 부분 가시(lepidic/acinar)라 그림이 덜 깔끔. MIL이 graded 스토리를 이미 설명.

## 확정된 시퀀스 (사용자 지시 2026-07-12)
1. **[진행 중] 스쿱 + 데이터 가용성 조사** — literature-scout. 대장 우선·폐 부차. 산출 `research/paperC-positioning/2026-07-12_CRC-LUNG-ST-scoop-and-data.md`. 게이팅: scooped면 중단, adjacent/clear면 진행. 공개 대장 ST(Visium 등)에 MSI/RAS 라벨 + 타깃유전자 존재 확인.
2. **대장 ST 그림** — 위 조사가 Go일 때만. Angle A식 threshold-free 지표로 (a)RAS/EGFR 형태학적 상관물-부재 (b)MSI-면역 형태-공존 대조. 전면 ST 트랙(D9 위반) 아님 — 타깃 방어 그림 1건.
3. **폐 ST** — **대장 ST 결과를 보고 결정**(사용자 명시: "폐암은 완료 후 대장에서 결과 보고 진행"). 대장이 메커니즘으로 단단하면 폐도 시도, 아니면 생략.

## 가드레일
- 예측 프레이밍 금지(imCMS·Kather2019·Coudray2018가 예측은 이미 함) → 우리는 치환비용/결정경계 메커니즘.
- 아형↔변이 1:1 비교 금지(사례: `docs/ai-collaboration-cautions.md` 사례1).
- MSI(가시)와 RAS(조용)는 **같은 변이/마커 층위**에서 대조 — 층위 정합.
- 8/15 GPU 마감·논문 집필 부담 → MIL 결과가 그림 보강을 요구할 때 착수. 스쿱·데이터가 막으면 즉시 중단.

## 조사 결과 (2026-07-12 완료, literature-scout)
전체: `research/paperC-positioning/2026-07-12_CRC-LUNG-ST-scoop-and-data.md`.
- **판정: 대장 ST = adjacent(인접·미스쿱, 스쿱 위험 낮음) · 데이터 conditional-Go.** 정확히 우리 프레이밍(MSI-면역 형태공존 vs RAS/EGFR 형태학적 상관물-부재 decoupling을 치환비용으로 시연)을 한 선행 없음. 최근접 5건(Path2Space 유방전용·반대방향, Valdeolivas CMS이질성 기술, Yang KRAS niche 기술, Pelka MMRd 면역hub 주로 scRNA, arXiv MSI예측)은 전부 결이 다름.
- **⚠️ 중대 caveat(유방과 구조적 차이):** ERBB2는 증폭→과발현이라 ST가 치료축을 직접 읽지만(Angle A가 깨끗한 이유), **KRAS/NRAS/BRAF는 점변이라 발현량이 안 변한다** → "RAS 상관물-부재"은 하류 프록시(MAPK/RAS 전사 시그니처·EGFR 리간드 EREG/AREG) 경유. 본질적으로 유방 ERBB2 floor보다 덜 깨끗. 숨길 결함이 아니라 "대장이 유방보다 어렵다"는 정직한 포지셔닝. **아형↔변이가 아니라 변이↔변이지만, 증폭↔점변이라 ST 가독성 층위가 다름 — 그림에서 대칭인 척 금지.**
- **데이터 병목:** MSI-H + MSS(+RAS)를 라벨과 함께 H&E-정합 Visium으로 담은 단일 공개셋 부재.
  - RAS 상관물-부재 반쪽 = 즉시 가능: **Valdeolivas(Zenodo 7551712, 7pt/14 Visium+H&E+annot)=1순위**, **Yang(GSA HRA011642, 2 KRAS-mut+2 WT)=RAS 페어 보강**.
  - MSI-가시 반쪽 = 게이트: Pelka(SCP1162)/HTAN에 H&E-정합 MSI-H Visium 오픈 존재 여부 **미확인**(PMC 네트워크 거부로 확인 실패) → 확인 필요, 없으면 공개 MSI-H Visium 1건 조달 or MLH1↓+IFN 프록시 유도.
- **비용:** 유방 Angle A는 반나절이었으나 대장은 MSI substrate 조달+RAS 프록시 정의로 1-2일 추정.

## MSI substrate 확인 결과 (2026-07-12, 사용자 지시로 게이트 해소)
부록: 조사 문서 하단 `## 부록: MSI-H Visium substrate 확인`. **판정: "MSI substrate 부재" 기각 → 프록시-Go~조건부 완전-Go.** 오픈 MSI-H CRC ST substrate 존재.
- **GSE285505**(Visium FFPE, PMID 41276505, 2025 오픈): 한 시리즈에 **CMS1/MSI 1건(GSM8703565) + MSS 3건** — 유일한 오픈 MSI+MSS 짝 Visium. 전장이라 KRAS·AREG/EREG·CD8A·GZMB·MLH1·IFN 커버. RAW.tar 41GB FTP. **한계: MSI n=1(대조 검정력 얇음), H&E 실재 미확인(tar 미열람), invasive-front 초점.**
- **Su et al. 2025**(npj Prec Oncol, Zenodo 13901180, CC-BY): **IMC(전사체 아님)**이나 MSI-H 9/MSS 33 + H&E 확정 + 오픈 → MSI-가시(면역 단백질↔H&E 림프구 공존) 반쪽에 적합. GSE285505(전장·MSI 얇음)와 상보.
- 기각: Pelka SCP1162(오픈분 scRNA, 공간 아님), HTAN(controlled), GSE226997(MSI/H&E 없음).
- **남은 확정 2건(완전-Go 조건):** (1) GSE285505 RAW.tar 다운로드로 H&E tissue image 실재 확인, (2) MSI n=1 얇음 → 2번째 오픈 MSI-H Visium 추가 or Su IMC로 면역축 보강.
- **RAS 상관물-부재 반쪽**(Valdeolivas Zenodo 7551712 · Yang HRA011642)과 합치면 양쪽 substrate 오픈 확보.

## 대장 ST 실행 결과 (2026-07-12) — ⚠️ 정직한 NULL
GSE285505 4샘플(CMS1/MSI + MSS + CMS4×2) 다운로드·분석 완료. 산출 `COLORECTAL/ST/`(json 2·그림 2·스크립트·README).
- **가설한 MSI-가시/RAS 상관물-부재 공간 비대칭이 관측되지 않음.** MSI 면역 시그니처↔H&E 세포밀도 공존 ρ=−0.007(CI 0 포함), RAS MAPK 프록시 ρ=+0.075~0.172("조용 아님"), 대조 Δρ 부호 비일관·프록시 간 뒤집힘.
- **유일한 견고한 양성 = 발현 수준(공간 아님)**: CMS1 IFN-hot vs CMS2 cold(IRF1 0.85 vs 0.23 등, housekeeping 대조로 아티팩트 배제).
- **원인 = 생물학적 반증 아니라 기질 한계**: (1) Visium 55µm spot이 hires에서 14px = 핵 텍스처 해상도 미만(imCMS/Kather의 세포단위 신호 접근 불가), (2) IFN 시그니처가 림프구 위치 아닌 경로활성을 읽음, (3) MSI n=1. 전부 exploratory.
- **함의**: 대장 ST를 메커니즘 그림으로 강제하지 않는다. **MIL AUROC 비대칭(CMS1 0.912·MSI 0.918 vs all-RAS 0.705)이 핵심 증거로 독립적으로 성립**(D9: cost-of-sub는 ST 불필요). 메커니즘 grounding은 유방 ERBB2 floor(작동함)가 담당.
- **선택지(사람 결정)**: (a) 대장 ST를 mechanism 그림에서 빼고 MIL로만 간다(권장, 마감·정직성), (b) 해상도 적합 substrate **Su et al. 2025 IMC**(Zenodo 13901180, 단백/세포수준)로 재시도 — 단 IMC는 세포분할 별도 파이프라인(추가 작업).

## 상태 (2026-07-12)
- 스쿱·데이터 조사: ✅ adjacent + conditional-Go.
- MSI substrate 확인: ✅ 존재(GSE285505 + Su IMC).
- 대장 ST 그림: ✅ **실행 완료 = NULL(exploratory)**. Visium 해상도 한계. **권장: mechanism 그림에서 제외, MIL이 핵심 증거.** Su IMC 재시도는 옵션.
- 폐 ST: ❌ 착수 안 함 — 대장 Visium이 null이라 폐도 동일 해상도 문제 예상. Su IMC류 아니면 우선순위 없음.

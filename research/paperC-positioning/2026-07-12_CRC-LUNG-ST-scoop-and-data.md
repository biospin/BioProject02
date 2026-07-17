# 대장(우선)·폐(부차) 공간전사체(ST) — 스쿱 판정 + 공개 데이터 가용성 (2026-07-12)

> literature-scout. 목적: 유방 **Angle A**(HER2+ ST에서 ERBB2 종양 spot의 배경 겹침 = 치환비용의 공간 floor, threshold-free Θ=P(tumor≤ref)=1−AUC)의 **대장 격 = MSI-가시 / RAS 상관물-부재 공간 대조**가 (a) 스쿱되었는가 (b) 공개 ST로 실행 가능한가 판정.
> 참조: `research/paperA-positioning/2026-07-11_HE-ST-scoop-and-angles.md`(유방 Angle A·D9/D10) · `experiments/crosscancer/CRC_SUBTYPE_INVESTIGATION.md`(CMS/MSI 라벨 층위) · `PROGRESS_DECISIONS.md`.

---

## ⭐ 한 줄 판정

**대장 ST: `adjacent`(인접·미스쿱 — 정확히 우리 프레이밍을 한 선행 없음, 유방 Angle A와 대칭) · 데이터 확보 = `conditional-Go`(부분 Y).**
공개 대장 ST-with-H&E 중 **MSI-H + MSS(+ RAS 상태)를 라벨과 함께 한 데이터셋에 담은 것은 없다.** RAS 상관물-부재 축은 Visium(Valdeolivas / Yang KRAS-pair)으로 즉시 가능하나, **MSI-가시 대조군은 별도 MSI-H 공개 Visium을 붙이거나 발현 프록시(MLH1↓·면역 시그니처)로 유도**해야 한다. → **조건부 Go**(아래 §5 지목).

**중대 caveat (유방과 다른 점):** ERBB2는 **증폭→mRNA 과발현**이라 ST가 치료축을 직접 읽는다(Angle A가 깨끗한 이유). **KRAS/NRAS는 점돌연변이라 발현량이 안 변한다** — "RAS 상관물-부재"은 KRAS 발현이 아니라 **하류 프록시(MAPK/RAS 전사 시그니처, EGFR 리간드 EREG/AREG)**를 경유해야 하며 본질적으로 유방 ERBB2보다 덜 깨끗하다. 이건 숨길 결함이 아니라 **정직한 포지셔닝**(대장이 유방보다 어려운 이유)이고, "형태학적 상관물-부재" 서사와도 정합적이다.

---

## 1. 스쿱 판정 (대장 우선)

### 우리가 하려는 것 ≠ 이미 포화된 것
- **H&E→CMS / H&E→MSI 예측은 이미 확립(레드오션):** imCMS(Sirinukunwattana, *Gut* 2021), Kather MSI(*Nat Med* 2019), 최근 FM 기반 cross-site MSI 일반화(arXiv 2605.02660, 2026). **우리는 예측 논문을 하지 않는다.**
- **우리가 하려는 것:** ST로 (a) **RAS/EGFR-경로 발현이 종양 조직에 공간적으로 존재하나 형태학적 상관물이 없음**(=ERBB2 floor 대칭, 항EGFR 축 고비용의 메커니즘 근거)과 (b) **MSI-H의 면역 시그니처(TIL/IFN)가 형태로 보이는 림프구 침윤과 공간 공존**(=형태 상관물 존재 → 저비용 근거)을 **치환비용(cost-of-substitution) 결정경계의 공간 메커니즘으로 시연**. 예측 아님.

### 스쿱 표 (최근접 선행 × 우리와의 차이)

| # | 선행 | 인용 | 무엇을 했나 | 우리와 같은 점 / **다른 점** |
|---|---|---|---|---|
| S1 | **Path2Space** (유방 전용) | Shulman et al. (교신 Ruppin), *Cell* 189 (2026), 10.1016/j.cell.2026.04.023; bioRxiv 2024.10.16.618609  [인용정정 2026-07-17: 종전 "Kaminski" 오기] | H&E→예측ST→SPAND 공간지표→trastuzumab/chemo 반응 **advocacy** | 같음: H&E×ST×치료축, ~976 TCGA. **다름: (1) 유방 전용 — 대장/범암종 버전 미존재(2026-07 확인). (2) 방향 반대 = 예측지표 옹호 vs 우리는 치환실패 지점 감사.** 유방에서 이미 인접·미스쿱 확정(D9). |
| S2 | 대장 CMS 공간 이질성 | Valdeolivas et al., *npj Precis Oncol* 2024, 8:10 (10.1038/s41698-023-00488-4) | 7환자 14 Visium으로 종양 내 CMS 이질성·다초점성 매핑 | 같음: 대장 ST에서 분자아형 공간분포. **다름: 순수 이질성 기술(descriptive) — 치환비용/결정손실·H&E 형태학적 상관물-부재 대비 없음.** 우리 데이터 substrate이자 인접선행. |
| S3 | KRAS-mut 면역억제 공간 niche | Yang, Gu, Miao et al., *J Immunother Cancer* 2025, 13:e013763 (10.1136/jitc-2025-013763; PMID 41475845) | 2 KRAS-mut + 2 WT Visium — KRAS-mut 종양의 면역억제 spatial niche | 같음: **RAS mut/WT ST 페어**(우리 RAS축에 최근접). **다름: 면역微환경 기술 — 형태학적 상관물-부재 decoupling·치환비용 프레이밍 없음.** 최근접 RAS-pair substrate 겸 인접선행. |
| S4 | MMRd/MMRp 공간 면역 hub | Pelka et al., *Cell* 2021, 184:4734 (S0092-8674(21)00945-4; PMID 34450029) | 62환자(28 MMRp/34 MMRd) — MMRd-enriched 면역 hub, 종양-내 활성T·chemokine | 같음: **MSI(=MMRd) 면역 시그니처의 공간 조직화**(우리 MSI-가시 축의 생물학 앵커). **다름: 주로 scRNA-seq(371k cells); 형태 상관물 공존/치환비용 렌즈 없음.** ⚠️ H&E-정합 Visium 여부 미확인(§2 주). |
| S5 | H&E→MSI FM 일반화 | (arXiv 2605.02660, 2026) | 생물학적 공간 prior로 cross-site MSI 예측 정규화 | 다름: **예측 논문**(우리가 하는 게 아님). MSI가 형태로 보인다는 방증(우리 (b) 저비용 논거 지지)이나 프레이밍 상이. |

**판정 근거:** 위 5건 중 **정확히 "ST로 MSI-면역 형태공존 vs RAS/EGFR 형태학적 상관물-부재 decoupling을 치환비용으로 시연"한 것은 없다.** S2/S3/S4는 공간 이질성·면역微환경의 *기술(descriptive)*이고, S1/S5는 *예측/advocacy*다. 우리 결정손실(cost-of-substitution) 렌즈는 그 위에 앉는 직교 축 → **adjacent(인접·미스쿱), 유방 Angle A와 동일 지형.** 스쿱 위험 낮음. 단 서사 충돌 관리 필요: S3(KRAS-mut niche가 "존재")를 우리는 "형태학적 상관물-부재이라 H&E로 라우팅 불가"로 다르게 프레이밍 — Path2Space 이질성 논쟁(D9-확인)과 같은 방어 필요.

---

## 2. 공개 ST 데이터 가용성 (대장)

플랫폼이 **Visium(전사체 전장)**이면 KRAS·NRAS·BRAF·EGFR·AREG·EREG·CD8A·GZMB·IFN 시그니처·MLH1 커버는 원리상 보장(패널형 Xenium만 확인 필요). **관건은 "다운로드 가능 + H&E 정합 + MSI/RAS 라벨"의 동시 충족.**

| 데이터셋 | Accession | 플랫폼 | N | H&E 정합 | MSI 라벨 | RAS 라벨 | 타깃유전자 커버 | 다운로드 |
|---|---|---|---|---|---|---|---|---|
| **Valdeolivas 2024** (CMS 이질성) | Zenodo **10.5281/zenodo.7551712** (Space Ranger out + 병리annot); scRNA GSE132465/GSE144735; GitHub `alberto-valdeolivas/ST_CRC_CMS` | Visium (fresh-frozen) | 7환자 / **14 슬라이드**(환자당 2 serial) | ✅ (Zenodo에 H&E + 병리 spot annot) | ❌ **미보고**(Table1) | 부분(S2/S4 "no mut", S1 BRAF-V600E) | ✅ 전장(웹확인, Visium) | ✅ 오픈 |
| **Yang 2025** (KRAS niche) | GSA **HRA011642** (ngdc.cncb.ac.cn/gsa-human); scRNA 다수 GSE | Visium | **2 KRAS-mut + 2 WT** | ✅(추정, Visium) | ❌ 미보고 | ✅ **mut/WT 페어** | ✅ 전장(Visium) | ✅ 오픈(GSA) |
| **Pelka 2021** (MMRd/MMRp 면역 hub) | Single Cell Portal **SCP1162**; HTAN raw = dbGaP **phs002371**(controlled) | 주로 scRNA(371k); 공간 검증 소수 | 62환자(28 MMRp/34 MMRd) | ⚠️ **미확인**(H&E-정합 Visium 여부) | ✅ **MMRd/MMRp 둘 다** | 미확인 | scRNA 전장 | 처리본 오픈 / raw controlled |
| **10x Visium HD CRC (FFPE)** | Zenodo **11402686**(병리 annot) + 10x datasets | Visium HD (FFPE) | 단일 샘플(demo) | ✅ | ❌ | ❌ | ✅ 전장 | ✅ 오픈 |
| **10x Visium CytAssist/11mm CRC (FFPE)** | 10x datasets (CytAssist post-Xenium colon; 11mm capture FFPE) | Visium (FFPE) | 단일 샘플(demo) | ✅ | ❌ | ❌ | ✅ 전장 | ✅ 오픈(등록) |
| **HTAN CRC 아틀라스** (일반) | HTAN Portal / phs002371 | Visium 포함 다모달 | 다수 | 부분 | 부분(MMR) | 미확인 | 전장 | Level3-4 raw = **dbGaP controlled** |

**데이터 현실(정직):**
- **RAS 상관물-부재 축**은 즉시 가능: Valdeolivas(CMS/RAS 프록시) + **Yang HRA011642(진짜 KRAS mut/WT Visium 페어)**. 단 RAS는 발현 아닌 변이라 MAPK/EREG/AREG 프록시 경유(위 caveat).
- **MSI-가시 대조군이 병목:** MSI-H + MSS를 **라벨과 함께 H&E-정합 Visium**으로 담은 단일 공개셋 부재. 옵션 (i) Pelka MMRd/MMRp를 생물학 앵커로 쓰되 H&E-정합 공간 여부 확인 후 substrate 여부 판정, (ii) 공개 MSI-H Visium 1건 + MSS Visium 1건을 붙여 대조, (iii) Visium 발현에서 **MLH1↓ + IFN/CD8A 시그니처**로 MSI 상태를 프록시 유도.
- Valdeolivas는 **CMS2-우세(canonical/MSS-계)**라 그 자체로는 MSI 대조가 약함(S1만 BRAF-V600E → CMS1/MSI 계열 후보).

---

## 3. 폐 (부차 — 낮은 우선순위)

- **공개 폐 ST:** LUAD/LUSC Visium/Xenium 공개셋 존재(10x 폐암 Visium demo, GEO 다수 NSCLC ST). **정밀 accession은 이번 스캔에서 미확정 — 대장 결정 후 확인 예정으로 보류.**
- **EGFR 스쿱:** H&E→EGFR/조직형 예측 다수(포화). EGFR은 **부분 가시(lepidic/acinar 패턴 상관)**라 유방 ERBB2·대장 MSI만큼 "형태학적 상관물-부재 vs 가시" 대비가 깔끔하지 않음. 게다가 EGFR도 대개 **활성화 돌연변이**(발현 불변)라 RAS와 같은 프록시 문제.
- **결론:** 폐 ST 그림은 **대장 결과를 본 뒤 결정**(D8 폐 cost 프레이밍 보류와 정합). 지금은 착수 대상 아님.

---

## 4. 유방 Angle A 대비 대장의 구조적 차이 (정직한 한계)

| 축 | 유방(Angle A, 실행됨) | 대장(제안) |
|---|---|---|
| 치료축의 ST 가독성 | ERBB2 **증폭→과발현** → ST 직접 읽음(깨끗) | KRAS/NRAS/BRAF **점변이→발현 불변** → 프록시 경유(덜 깨끗) |
| "형태학적 상관물-부재" 대상 | HER2(ERBB2 floor) | RAS/EGFR 경로(MAPK·EREG/AREG 프록시) |
| "형태-가시" 대조 | (유방엔 명시적 대조 없음) | **MSI-H 면역침윤 = 새 대칭축**(유방보다 서사 강점) |
| 라벨 완비 공개셋 | HER2+ ST 확보(Andersson) | **MSI-H+MSS+RAS 동시 라벨 부재**(병목) |

→ 대장은 **"MSI-가시 vs RAS 상관물-부재" 이중 대조**라는 유방에 없는 서사 이점이 있으나, **깨끗한 단일 라벨 데이터가 없다**는 실행 리스크가 그 대가.

---

## 5. 권고

**Verdict: 조건부 Go (conditional-Go). 스쿱 위험 낮음(adjacent), 데이터는 부분 확보 — MSI-H 대조 substrate 확정이 유일 게이트.**

**실행 타당성:**
- ✅ **RAS 상관물-부재 반쪽은 지금 실행 가능** — 방법 학습 0, 그림 1장(Angle A와 동형). substrate 지목:
  1. **Yang 2025 / GSA HRA011642** (2 KRAS-mut + 2 WT Visium) — **RAS mut/WT 페어로 최적**. MAPK/EREG 프록시를 종양 spot에 오버레이 → "치료축 발현이 형태학적 상관물-부재" Θ 지표.
  2. **Valdeolivas / Zenodo 7551712** (7pt/14 Visium + H&E + 병리 annot) — CMS/RAS 상관물-부재 축, H&E 정합 완비로 오버레이 그림에 가장 깨끗한 substrate.
- ⚠️ **MSI-가시 반쪽은 게이트** — 먼저 확인: (a) Pelka(SCP1162) 또는 HTAN에 **H&E-정합 MSI-H Visium**이 오픈으로 있는가, 없으면 (b) 공개 MSI-H Visium 1건 확보 or (c) MLH1↓+IFN 프록시로 MSI 유도. 이 하나가 풀리면 **완전 Go**.
- **지목 1-2개:** **Valdeolivas(Zenodo 7551712) = 1순위 substrate**(H&E+annot 완비), **Yang(HRA011642) = RAS-pair 보강**. MSI 대조는 별도 공개 MSI-H Visium 또는 프록시로 조달.

**리스크:** 스쿱보다 **데이터 라벨 병목**이 실질 리스크. 유방 Angle A가 "반나절 방어탄약"이었던 것과 달리, 대장은 **MSI-H substrate 조달 + RAS 프록시 정의**로 반나절보다 큼(1-2일 추정). D9/D10 결정("C는 Paper B 후 bank")과 정합적으로, **본 그림도 Paper A 사전제출 필수가 아니라 cross-cancer 확장(Paper C)용 banked 후보**로 두고, RAS 상관물-부재 반쪽만 값싼 예비 그림으로 먼저 시연 가능.

---

## Sources
- Path2Space: [Cell 2026](https://www.cell.com/cell/abstract/S0092-8674(26)00458-7) · [bioRxiv 2024.10.16.618609](https://www.biorxiv.org/content/10.1101/2024.10.16.618609.full.pdf)
- Valdeolivas et al., npj Precis Oncol 2024: [10.1038/s41698-023-00488-4](https://www.nature.com/articles/s41698-023-00488-4) · [Zenodo 7551712](https://zenodo.org/records/7551713) · [GitHub ST_CRC_CMS](https://github.com/alberto-valdeolivas/ST_CRC_CMS)
- Yang, Gu, Miao et al., J Immunother Cancer 2025 (KRAS niche): [10.1136/jitc-2025-013763](https://pmc.ncbi.nlm.nih.gov/articles/PMC12766835/) · GSA HRA011642 (https://ngdc.cncb.ac.cn/gsa-human)
- Pelka et al., Cell 2021 (MMRd/MMRp immune hubs): [PMID 34450029](https://pubmed.ncbi.nlm.nih.gov/34450029/) · [SCP1162](https://singlecell.broadinstitute.org/single_cell/study/SCP1162/human-colon-cancer-atlas-c295)
- HTAN data access (dbGaP phs002371): [Nat Methods 2025](https://www.nature.com/articles/s41592-025-02643-0) · [humantumoratlas.org/standard/spatial_transcriptomics](https://humantumoratlas.org/standard/spatial_transcriptomics)
- 10x public CRC: [Visium HD CRC FFPE Zenodo 11402686](https://zenodo.org/records/11402686) · [10x datasets](https://www.10xgenomics.com/datasets)
- imCMS: Sirinukunwattana et al., Gut 2021 · Kather MSI, Nat Med 2019 · H&E→MSI FM: arXiv 2605.02660 (2026)
- 미확인 표기: Pelka H&E-정합 Visium 여부 / 폐 ST 정밀 accession / HTAN CRC 오픈 Visium MSI 라벨 — 웹 직접 확인 못함(PMC IPv6 간헐 거부).

---

## 부록: MSI-H Visium substrate 확인 (2026-07-12, 후속 단독 조사)

> 코디네이터 후속 지시: §2에서 "미확인"으로 남긴 **MSI-가시 반쪽 substrate 게이트**만 집중 해소. 목표 = **오픈(비-controlled) 대장 ST 중 (a) MSI-H/MMRd 샘플을 (b) H&E 정합으로 담고 (c) 실제 다운로드 가능**한 것이 존재하는가. MSS 짝 포함이면 최상.

### 확인 표 (데이터셋 × MSI-H 유무 × H&E정합 × 오픈 × 다운로드 실검증)

| 데이터셋 | Accession | 플랫폼 | MSI-H 유무 | MSS 짝 | H&E 정합 | 오픈 여부 | 다운로드 실검증 |
|---|---|---|---|---|---|---|---|
| **GSE285505** (TSP2 invasive front) | GEO **GSE285505** (PMID 41276505) | Visium (FFPE, NovaSeq6000) | ✅ **CMS1/MSI ×1** (GSM8703565) | ✅ MSS ×3 (CMS4×2·CMS2) | ⚠️ **미확인**(RAW.tar 내부 미열람; Visium이라 tissue image 동봉 가능성 높음) | ✅ 오픈(Public 2025-10-28) | ✅ **RAW.tar 41GB FTP 경로 확인**(내부 H&E 파일 실재는 미확인) |
| **Su et al. 2025** (stage III CRC 공간 landscape) | Zenodo **10.5281/zenodo.13901180** (PMC11973205, PMID 40189697) | **IMC**(Hyperion 단백 패널, 전사체 아님) | ✅ **MSI-H 9** | ✅ **MSS 33** (+미정 10) | ✅ H&E 포함(병리검수; H&E는 Stanford dna-discovery 공개 URL) | ✅ 오픈(CC-BY 4.0) | ✅ Zenodo + GitHub(BiomedicalMachineLearning/CRC_Spatial_Landscape) |
| Valdeolivas 2024 | Zenodo 7551712 | Visium (fresh-frozen)+H&E | ❌ 미보고(S1 BRAF-V600E만 MSI-계열 후보) | CMS2-우세(MSS-계) | ✅ | ✅ | ✅(§2) |
| Yang 2025 | GSA HRA011642 | Visium | ❌ 미보고 | (RAS mut/WT 축) | ✅(추정) | ✅ | ✅(§2) |
| Pelka 2021 | SCP1162 / HTAN phs002371 | **scRNA**(dissociated) | ✅ 라벨(MMRd 34) | ✅ MMRp 28 | ❌ **H&E-정합 공간 아님** | 처리본 오픈 / raw controlled | 공간 substrate 아님(생물학 앵커) |
| GSE226997 | GEO GSE226997 | Visium | ❌ 미보고 | — | ❌ 미기재 | ✅ | ✅(단 MSI/H&E 없음) |
| Glycolysis MSI-H CRC (OTT.S538018) | 미확인(본문 403) | scRNA+ST(재사용 추정) | ✅(MSI-H 초점) | — | 미확인 | 저널 오픈 | ST accession **미확인** |

### 항목별 결론
1. **Pelka(SCP1162/HTAN):** 공개된 것은 **scRNA-seq(371k cells, dissociated)** — H&E-정합 Visium이 오픈으로 받아지지 않음. HTAN CRC raw(공간 포함)는 **dbGaP phs002371 = controlled**. → **MSI 생물학 앵커 인용용이지 figure substrate 아님**(advisor 지적대로 확인 완료: 공간 modality가 H&E-정합 오픈 Visium이 아님).
2. **HTAN CRC 일반:** 오픈 Level에서 MSI-라벨 H&E-정합 CRC Visium을 특정 accession으로 확정하지 못함(raw = phs002371 controlled). → **오픈 substrate로 부적합**.
3. **GEO/Zenodo 직접 검색 → 결정적 1건 확보: GSE285505.** 오픈 Visium(FFPE) 4슬라이드에 **CMS1/MSI 1건 + MSS 3건**을 한 시리즈로 담음(bulk-RNA-seq로 subtyping). 전장 Visium이라 KRAS·AREG/EREG·CD8A·GZMB·MLH1·IFN 시그니처 모두 커버. **유일한 실질 오픈 MSI+MSS 짝 Visium.** ⚠️ 한계: (i) **MSI 샘플 n=1**(대조 검정력 얇음), (ii) H&E 파일 실재는 RAW.tar 미열람으로 **미확인**(Visium FFPE 표준상 tissue_hires_image 동봉이 일반적이나 확인 필요), (iii) invasive-front/fibrotic 초점이라 종양 코어 커버 편향 가능.
4. **프록시 경로:** GSE285505는 MSI 샘플이 **이미 라벨링**돼 프록시 불필요(직접). Valdeolivas/Yang는 MSS-편향이라 MLH1↓+IFN 프록시로 MSI-유사 spot 유도는 **약함**(진짜 MSI-H 환자 미포함 가능성). → 프록시는 GSE285505 보강용이 아니라 대체 불가.
5. **보강 substrate = Su 2025 IMC(Zenodo 13901180).** 전사체는 아니나 **MSI-H 9 / MSS 33 + H&E + 오픈**으로, **MSI-가시(면역 단백질 CD8/면역세포가 H&E 림프구 침윤과 공간 공존)** 반쪽을 직접 시연하기에 오히려 적합(단백 패널이라 임의 유전자 mRNA는 없음). Visium(GSE285505)과 상보: GSE285505=전장 발현·MSI n 얇음 / Su=MSI n 두꺼움·전사체 아님.

### ⭐ 한 줄 판정
**프록시-Go → 사실상 완전-Go(조건부).**
오픈 MSI-H CRC ST substrate는 존재한다: **전사체 축 = GSE285505**(오픈 Visium, MSI(CMS1)+MSS 3, 전장; 단 MSI n=1·H&E 파일 실재 미확인), **면역-가시 축 = Su 2025 IMC**(오픈, MSI-H 9/MSS 33, H&E 확정). **RAS 상관물-부재 반쪽(Valdeolivas·Yang)과 합치면 대장 Angle A 양쪽 substrate가 모두 오픈으로 확보됨** — 남은 확정 작업 단 2건: **(1) GSE285505 RAW.tar 다운로드로 H&E tissue image 실재 확인, (2) MSI n=1 얇음 → 두 번째 오픈 MSI-H Visium 추가 탐색 or Su IMC로 면역축 보강.** 이 둘이 풀리면 완전-Go. → "MSI substrate 부재(RAS-반쪽만)"는 **기각**.

### 부록 Sources
- GSE285505 (Visium, MSI+MSS): [GEO acc](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE285505) · PMID 41276505
- Su et al. 2025, npj Precis Oncol (IMC, MSI-H 9/MSS 33): [PMC11973205](https://pmc.ncbi.nlm.nih.gov/articles/PMC11973205/) · DOI 10.1038/s41698-025-00853-5 · [Zenodo 13901180](https://zenodo.org/records/13901180) · H&E: dna-discovery.stanford.edu/publicmaterial/datasets/spatial_CRC
- Pelka SCP1162 (scRNA, MMRd/MMRp): [Single Cell Portal](https://singlecell.broadinstitute.org/single_cell/study/SCP1162) · HTAN raw dbGaP phs002371
- GSE226997 (Visium CRC, MSI 없음): [OmicsDI](https://www.omicsdi.org/dataset/geo/GSE226997)
- MSS good-prognosis 공간(Karlsen 2025, MSS-초점): bioRxiv 10.1101/2025.03.31.646286
- 미확인: GSE285505 H&E 파일 실재 · Glycolysis MSI-H ST(OTT.S538018) accession · 두 번째 오픈 MSI-H Visium 존재 여부.

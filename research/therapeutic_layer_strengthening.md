# BIOP02 — 치료-가설 층 보강 설계 (falsifiable therapeutic layer)

작성 2026-06-10. Leader(kkkim) 결정 #1("치료층 유지 + 강화")의 실행 설계.
Ground = research-methodologist(웹검증) + [`critique_and_revised_direction.md`](critique_and_revised_direction.md) 구멍 #1~#3.
타겟 = npj Precision Oncology. Scope 준수: **NOT DRP, 약물구조 입력 없음, BRCA-only, hypothesis-only, single A100.**

> **목표:** 리뷰어 평결("치료층 = 검증불가·collinear·trivial")을 *강등이 아니라 반박*으로 해소.
> 모든 데이터셋 주장은 웹검증(인라인 인용), 모든 테스트는 **반증 조건(falsification condition)**을 명시한다.
> "관심 있으니 유지"가 rigor 면제가 아님 — 아래 (A)실제 결과 앵커 + (B)비-collinear 독립 readout + 셔플 null + (D)비순환 Critic을 충족해야 헤드라인 자격 인정.

---

## A. 실제 치료-결과 앵커 (구멍 #1 "검증불가·순환" 해소)

문제: 현재 치료가설의 유일한 검증이 phenotype 정확도(CPTAC) + KB enrichment(순환 — SoC가 KB에 인코딩됨). → **사전치료 H&E + 실제 치료-결과 라벨**을 가진, 파이프라인이 학습한 적 없는 코호트 1개 이상 필요.

### 검증된 후보 데이터셋 (사전치료 유방 H&E + 결과)

| 데이터셋 | n / modality | 결과 라벨 | H&E 가용? | 접근 | 평가 |
|---|---|---|---|---|---|
| **Yale HER2 + Trastuzumab (TCIA "HER2-TUMOR-ROIS")** | 사전치료 HER2+ biopsy 85례(responder 36 / non 49) + HER2 status 188 | **trastuzumab pCR** | **Yes — 사전치료 WSI + tumor-ROI 주석** | **OPEN, CC-BY 4.0, 등록 불필요, ~40 GB TCIA 직접 다운로드** | **★PRIMARY ANCHOR.** 개방·사전치료·실제 anti-HER2 결과. Farahmand *Mod Pathol* 2022; [TCIA HER2-TUMOR-ROIS](https://www.cancerimagingarchive.net/collection/her2-tumor-rois/) |
| **TransNEO (Sammut 2022)** | 168례 neoadjuvant chemo; FF H&E WSI | **pCR / RCB** | Yes (WSI=Zenodo; 라벨+RNA-seq=EGA) | **이미지 Zenodo 개방([6337925](https://zenodo.org/records/6337925)); 라벨 EGA [EGAS00001004582](https://ega-archive.org/studies/EGAS00001004582)(controlled, ~수주)** | **SECONDARY.** gold-standard NAC. 라벨 gated. [Nature 601:623](https://www.nature.com/articles/s41586-021-04278-5) |
| **IMPRESS (Huang 2023, npj Prec Onc=타겟저널)** | 126 WSI (HER2+ 62, TNBC 64), 전원 NAC | **NAC response** | Yes (H&E + 정합 IHC) | GitHub [huangzhii/IMPRESS](https://github.com/huangzhii/IMPRESS) (WSI 가용성 repo 확인 요) | **TERTIARY.** *동일 저널이 n~126 H&E→NAC-response 논문을 게재한 선례.* [npj PO 7:14](https://www.nature.com/articles/s41698-023-00352-5) |
| **BCNB (Xu 2021)** | 1058 core-needle WSI | ALN 전이 + ER/PR/HER2/subtype (치료결과 없음) | Yes | OPEN ([BCNB](https://bupt-ai-cz.github.io/BCNB/)) | **phenotype 외부검증 코호트**(앵커 아님) — TCGA와 site-orthogonal(Asian) 대규모 ER/PR/HER2/PAM50 test |
| Post-NAT-BRCA (TCIA) | 96 WSI/54례 | **치료후** RCB/cellularity | Yes | OPEN | **앵커 기각** — 사후 절제, 사전치료 아님. cellularity sanity만 |
| HEROHE(509)·ACROBAT(4212 WSI/1152례)·BreastPathQ | 대규모 | HER2 status/정합/cellularity — **치료결과 없음** | Yes | OPEN/challenge | phenotype·robustness 용도만 |
| I-SPY1/2 | 대규모 | pCR | **공개본은 MRI, H&E 아님**(TCIA 확인) | — | **기각** — 병리 WSI 미공개 |

### 내부 생존 앵커 (추가 다운로드 0)
TCGA-CDR([Liu *Cell* 2018](https://www.cell.com/cell/fulltext/S0092-8674(18)30229-0)) — **PFI**(BRCA 권장 고신뢰 endpoint) + 치료 필드(이미 보유, 1010 슬라이드). **기록된 치료 하 PFI**를 leave-one-cohort-out 내부 생존 앵커로. ⚠️ TCGA 치료주석 희소·이질 → **보조용**(primary 아님).

### 단일 반증 테스트 — **Exp-OUTCOME**
**H_A:** 형태학에서만 도출된 anti-HER2 치료축 점수(H&E→예측phenotype→dependency 수렴)가 Yale 코호트(미학습)의 **실제 trastuzumab pCR**을 층화한다.
- **코호트:** Yale 85 사전치료 HER2+. 파이프라인 frozen(TCGA만 학습) → Yale은 embedding→예측phenotype→치료축 점수만. **Yale 미세조정 금지.**
- **Primary:** 치료축 점수의 pCR 예측 **AUROC + bootstrap 95% CI**(2000, 환자단위).
- **Baselines (바닥 아닌 진짜 bar):** (1) 예측 HER2 확률 단독(*치료축이 phenotype 위에 무엇을 더하나?*), (2) cellularity/TIL proxy, (3) **published Yale 모델 AUC ~0.8**(Farahmand 2022) = head-to-head 외부 SOTA bar.
- **통계:** 축 vs phenotype AUC차 = DeLong; n=85라 대부분 비유의 — *그대로 보고*.
- **★FALSIFICATION:** 치료축 AUC의 95% CI가 0.5를 포함하거나, 예측-HER2-확률 baseline을 넘지 못하면 → **치료층은 phenotype 이상의 결과정보를 주지 않음** → 음성결과로 보고하고 수렴주장 강등. *이것이 리뷰어가 요구한 정직한 falsifiability.*
- **확장(병행):** TransNEO EGA 접근 지금 신청(~수주) → chemo축 pCR/RCB 반복(HER2축과 독립).

---

## B. 진짜로 독립인 readout 축 (구멍 #2 collinearity 환상 + 공유 H&E 오류)

검증된 사실: **PRISM↔GDSC/CTRP cross-dataset Spearman ≈ 0.2–0.25**([Sharifi-Noghabi 2024, PMC11043358](https://pmc.ncbi.nlm.nih.gov/articles/PMC11043358/)) — 완전 중복은 아니나 **같은 evidence type(cell-line viability)**·method 교란 공유. 3표로 세면 독립성 과장. → viability를 **1축**으로 접고, **기전적으로 다른** 축 추가.

### 재설계된 축

| 축 | 소스 | evidence type | viability와 직교? |
|---|---|---|---|
| **축1 — 약물 viability (1축)** | PRISM+GDSC+CTRP 통합; 내부일치 보고하되 **3중계산 금지** | 화합물 하 세포생존 | n/a (기준축) |
| **축2 — CRISPR 유전자 의존성** | DepMap **Chronos** gene-effect (Achilles) | **인과 loss-of-function** — 약물 없음, *타깃* 필수성 측정 | **YES.** 약물스크린 무관, CRISPR knockout 기반 ([DepMap Chronos](https://depmap.org/portal/achilles/)) |
| **축3 — 전사체 reversal** | **LINCS L1000 / CMap** connectivity | 후보약물 시그니처가 예측 dysregulated 시그니처를 *역전*시키나? | **YES.** viability 아닌 약물유도 전사섭동; 종양 repurposing 검증됨 ([Williams 2022](https://academic.oup.com/bib/article/24/1/bbac490/6850563)) |
| **축4 (보조, 독립표 아님)** | OncoKB/CIViC/Open Targets | 큐레이션 임상 actionability | NO — grounding 전용, 수렴 투표서 제외(Part D) |

**비-collinear 근거:** 축2=유전적 섭동(축1=화학적과 다른 modality), 축3=전사체 층(viability와 다른 분자층). 세 축 모두 상위인 약물 = **독립 3선 지지**(1신호 3중계산 아님).

### 수렴 정량 + 의무 null 2종
1. **cross-axis 수렴점수:** 약물/타깃별 각 축 rank-normalize[0,1], 방향 일치 요구; 수렴=통과 축 수(0–3) 또는 rank-aggregation(RRA/Stuart).
2. **collinearity 표 (의무 figure):** 축간 **3×3 + viability 내부 3×3 Spearman 행렬**. 측정된 PRISM/GDSC/CTRP 내부 r과 *훨씬 낮은* 축1↔2↔3 cross-type r을 보여 **독립성을 주장 아닌 증명**.
3. **★phenotype-shuffle null (공유 H&E 오류 sub-hole):** 예측 phenotype을 환자간 1000회 셔플 후 수렴 재계산. **FALSIFICATION:** 셔플 수렴이 참 phenotype과 통계적 구분 불가(perm p>0.05)면 → 수렴은 H&E-phenotype이 아닌 KB/스크린 구조의 산물 → 수렴주장 반증.
4. **공유오류 바닥:** 모든 축이 *같은* 예측 phenotype 소비 → 수렴은 phenotype 품질 한계 초과 불가. 수렴을 phenotype **calibrated 신뢰도**로 층화 — 고신뢰에서만 나오고 저신뢰서 붕괴하면 그 의존구조를 명시. random-phenotype 바닥 추가.

---

## C. 가설을 비-trivial·기전적으로 (scoop/trivial 격상)

**scoop 확인:** Dawood 2024([npj PO](https://www.nature.com/articles/s41698-023-00491-9))가 이미 H&E→다약물 민감도(cell-line imputed) on TCGA-BRCA — *타겟저널*. "H&E→약물민감도 랭킹" 프레임은 scoop됨. **재진입 금지.**

### 재정의된 기여 진술 (정밀)
> end-to-end image→drug-sensitivity 회귀(Dawood 2024)와 달리, 모든 치료가설을 **검사가능한 분자-phenotype 병목**으로 라우팅하고, **기전적으로 독립인 3축(약물-viability·CRISPR 의존성·전사체 reversal)이 수렴할 때만** 지지하는 **auditable phenotype→pathway-dependency→target 가설 생성기**. 기여를 **Basal/TNBC repurposing**(SoC 희소 → KB-SoC로 enrichment 설명 불가)에 집중하고, **실제 anti-HER2 치료결과(Yale)에 대한 사전등록 반증 테스트**를 보고. 기여 = 더 나은 민감도 숫자가 아니라 재현·반증 *프로토콜*.

### 비-trivial·저비용 아이디어 3
1. **TNBC/Basal repurposing 집중(순환 탈출).** HER2+/ER+는 KB=SoC라 enrichment 순환. **TNBC/Basal은 actionable SoC 희소** → 수렴 지지 repurposing 후보(아직 SoC 아닌 CRISPR-essential·시그니처-역전 타깃)는 진짜 가설. 가장 반박 어려운 곳에 기여 배치. 비용 0.
2. **의존성-축을 헤드라인, 약물은 귀결.** "Basal 형태 → 예측 Basal → PARP/replication-stress 축 수렴 의존성" 같은 **타깃/pathway-의존성 가설**을 출력, 그 *다음* 해당 약물 나열. Dawood(직접 민감도 예측, 의존성 중간 없음)와 다름. 약물구조 미진입 — 준수.
3. **KB 대비 "surprise" 필터(KB를 oracle→null로).** 각 가설을 해당 subtype의 OncoKB/CIViC가 *설명 못하는 정도*로 점수화. **KB-novel 수렴 가설**을 별도 보고 — 이것이 falsifiable·비-trivial 출력. (Part D 운영화.)

---

## D. Critic 비순환화 (구멍 #3)

순환: OncoKB로 생성 + OncoKB-enrichment를 "성공"으로 채점 → Critic이 known-knowledge 필터.

### KB 분리 (비중첩)
| 기능 | 자원 | 규칙 |
|---|---|---|
| **가설 생성** (pathway→target→drug 링크) | **DGIdb + Reactome/MSigDB** (drug–gene, gene–pathway) | 생성은 이 기전 링크 DB만; 임상 actionability 점수 아님 |
| **독립 ground-truth 채점** (Critic) | **OncoKB + CIViC** (임상 actionability) | 채점 전용, 생성 금지. 생성 도운 KB가 가설을 "보상" 불가 |
| **양쪽서 투표 제외** | Open Targets | narrative grounding만 |

### 비-KB falsifiability 신호 (진짜 해법)
KB-vs-KB는 여전히 knowledge-recovery. **진짜 비순환 신호 = Part A 실제결과 앵커:** Critic의 *primary* gate = "anti-HER2 치료축이 held-out Yale 실제 pCR을 층화하나?" — *어떤 KB에도 없는* 신호. 보조 비-KB = phenotype-shuffle null(B) + PFI 층화(TCGA-CDR). Critic의 operating characteristic(기각률·held-out 결과 대비 precision)을 method의 측정가능 행동으로 보고 — 멀티에이전트 Critic의 유일한 출판 각도(novelty doc: 오케스트레이션 자체는 novelty 아님).

---

## E. LLM / RAG 활용 — 한정 도입 (auditability 강화, 정량경로 불가침)

> 결론: LLM/RAG는 **off-topic 아님 — 이미 절반 들어와 있음**(멀티에이전트 Critic = LLM-judge, 치료가설 KB grounding). 핵심은 *어디 쓰고 어디 절대 안 쓰는가*.

**쓰는 곳 (권장).**
1. **증거-결합 레이어 = RAG.** 수렴 가설 각 edge를 DGIdb/Reactome/PubMed/ClinicalTrials.gov에서 **검색→인용 의무화** → 출력 단위 = *근거 인용이 박힌 hypothesis card*. **논문 auditability thesis와 동일 방향**, Dawood엔 없는 차별점.
2. **Critic claim 검증.** Critic이 "이 pathway-drug 링크가 문헌상 지지되나?"를 retrieved evidence에 대조 → 7-point #5(plausibility)를 *주관*이 아니라 *검색근거*로 채점. (채점 KB = OncoKB/CIViC, 생성 KB와 분리 — Part D 준수.)
3. **기전 narrative 생성.** phenotype+수렴축 → 가설 서술. 단 retrieval-grounded + 인용 강제, 인용 없는 출력은 자동 기각.

**절대 안 쓰는 곳 (rigor 보호).**
- **정량 백본**(phenotype 예측, viability/CRISPR/LINCS 수렴, enrichment 통계)에 **LLM 금지.** 신호는 숫자에서 — LLM이 "그럴듯한 기전 스토리"를 만들면 리뷰어 지적 *"두 번째 블랙박스 / plausible-but-wrong"* 함정.
- RAG hallucination 감소는 **검색근거 없는 주장 금지**가 전제.

**novelty/scoop 경고.** "LLM 에이전트 썼어요"는 기여 아님(novelty doc: "에이전트 있어요'가 아니라 기각률로"). **Google "AI co-scientist"가 최대 scoop 위험.** → LLM/RAG는 **Exp5/Exp-CRITIC의 측정된 operating characteristic + Part D 비순환**으로만 정당화. GPU ~0(추론 API/경량).

---

## F. Feasibility & 정직한 한계

**GPU/데이터 (single A100 80GB).** 임베딩 1회 추출(GPU 유일 비용): TCGA 1010 + Yale ~273 + BCNB 1058 + (승인시)TransNEO 168 + IMPRESS 126 ≈ **~2600 WSI** → UNI/CONCH frozen tile+extract, 수일 내 여유. 하류(MLP/MIL + 3축)는 **CPU-cheap**(DepMap/LINCS=행렬). 저장: Yale 40 GB; 임베딩 영구·소형 → 2 TB/200 GB cache 내.

**접근 blocker/타임라인.** *개방 즉시:* Yale(primary), BCNB, Post-NAT, HEROHE, ACROBAT, BreastPathQ, TransNEO *이미지*(Zenodo), DepMap, LINCS, GDSC/CTRP, DGIdb/CIViC/Open Targets. *controlled(지금 신청, ~수주):* TransNEO **라벨** EGA — **block 금지**(Yale가 primary, 완전개방). *token-gated:* OncoKB API → open KB로 도달범위 정량화 + residual gap. *FM:* UNI/CONCH HF 승인 진행중.

**★반증 불가로 남는 것 (over-claim 금지).**
1. **환자 개별 인과검증 불가.** Yale pCR도 *코호트 수준 층화*지 개인 benefit 아님 → hypothesis-only가 정직한 천장.
2. **cell-line/CRISPR/LINCS 전부 in-vitro proxy.** 수렴은 단일스크린 artifact 위험만 줄임, 환자 efficacy 미입증. organoid/PDX = 다음 단계(공급 불가).
3. **결과앵커 단일맥락(anti-HER2, n=85).** Yale pCR이 **TNBC/Basal repurposing(novel 부분)을 검증 안 함** — 그건 전향 데이터 전까지 기전가설로 잔존. *명시.*
4. **phenotype 오류가 상류.** 모든 축이 H&E→phenotype 오류 상속 — 정량(calibration·신뢰도층화)하되 제거 불가.
5. **TCGA PFI**는 치료주석 희소로 교란 — 보조용만.

---

## 추가 실험 목록 (기존 Exp1–5에 추가)

| ID | 실험 | 해소 | 반증 조건 |
|---|---|---|---|
| **Exp-OUTCOME** | frozen 파이프라인 → anti-HER2 축 → Yale 실제 pCR AUROC; DeLong vs HER2-prob; bootstrap CI | #1 | 축 AUC CI가 0.5 포함 OR ≤ phenotype baseline |
| **Exp-AXES** | PRISM/GDSC/CTRP→1축; +Chronos+LINCS; 3×3 상관행렬; rank-aggregate 수렴 | #2 | cross-axis r이 viability 내부만큼 높음 → 독립 아님 |
| **Exp-SHUFFLE** | phenotype-shuffle null(1000×); 신뢰도-층화 수렴 | #2 | 셔플 수렴 = 참(perm p>0.05) |
| **Exp-TNBC** | 수렴지지·KB-novel Basal/TNBC repurposing 후보; OncoKB/CIViC 대비 "surprise" | trivial/scoop(C) | KB-novel 수렴후보 0 → SoC 재현뿐 |
| **Exp-CRITIC** | Critic을 분리 KB(OncoKB/CIViC) + primary 비-KB gate=Yale 결과로 채점; 기각률/precision | #3 | 기각률≈0 OR 생성-KB 필터와 동일 → Critic 장식 |

---

## 연관 파일
- [`novelty_positioning.md`](novelty_positioning.md) — 본 설계가 "근거 축 확장" 표·Exp4/5 확장
- [`experiment_plan.md`](experiment_plan.md) — Exp-OUTCOME/AXES/SHUFFLE/TNBC/CRITIC 통합 대상
- [`../agents/data/split_policy_v0.md`](../agents/data/split_policy_v0.md) — Yale/BCNB/TransNEO = 외부 test, **never-train**·site-stratified 선언 필요

## Sources
Sammut Nature 601:623 (2022) · TCIA HER2-TUMOR-ROIS(Yale, open, trastuzumab pCR)/Farahmand PMC10221954 · Huang npj PO 7:14 (2023) IMPRESS · BCNB · Post-NAT-BRCA · HEROHE · ACROBAT · BreastPathQ · I-SPY2(MRI only) · Dawood npj PO (2024, scoop) · DepMap/Chronos · LINCS L1000 reversion(Williams 2022) · PRISM/GDSC/CTRP r~0.2–0.25 (PMC11043358) · Liu Cell (2018) TCGA-CDR PFI/DFI

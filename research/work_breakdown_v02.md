# BIOP02 v0.2 — 작업분해 & 일 배분 핸드오프 (→ Orchestrator braveji)

작성 2026-06-10, Leader=kkkim. 대상 독자 = **braveji(Orchestrator)** — 본 문서를 읽고 JIRA(BIOP02) 이슈 생성·담당 배분에 사용.
근거 = [`therapeutic_layer_strengthening.md`](therapeutic_layer_strengthening.md) + [`experiment_plan.md`](experiment_plan.md) + [`critique_and_revised_direction.md`](critique_and_revised_direction.md).

> **신규 등록 범위:** 치료층 유지+강화 결정에 따라 추가된 외부 코호트·5개 신규 실험(Exp-OUTCOME/AXES/SHUFFLE/TNBC/CRITIC) + Exp3 보류해제 + Exp7 포함. 기존 Exp1/Exp2는 진행 중(여기선 의존성으로만 언급).

---

## 0. PR 요청 (braveji 처리)

| 브랜치 | 내용 | 요청 |
|---|---|---|
| `docs/BIOP02-kkkim-literature-survey` | v0.2 결정 + 치료층 보강안 + 본 작업분해 (신규 3문서/갱신) | **PR 리뷰→main 머지** (Critic: 자기검토 금지 → kkkim 외 검토자, 권장 jamie/sjpark) |
| `docs/BIOP02-kkkim-roles-update` | Leader=kkkim·Critic=braveji 역할표 갱신 (푸시됨, **미머지**) | **선(先) 머지 필요** — 본 문서의 담당 배분 전제 |

JIRA: 신규 작업을 **Epic "BIOP02 v0.2 치료층 강화"** 아래 T1–T12 이슈로 생성 권장. 브랜치 네이밍 = `<type>/<BIOP02-번호>-<owner>-<설명>`.

---

## 1. 작업분해 (T1–T12)

표기: 🟢개방즉시 / 🟡controlled·신청 / 🔴token·승인대기. GPU 없으면 CPU.

### 데이터 층 — owner: **jamie(Data)** + kkkim 보조

| ID | 작업 | 입력/데이터 | 방법 | 산출물 | 자원 | 의존 | 완료기준 |
|---|---|---|---|---|---|---|---|
| **T1** | 외부 코호트 확보·manifest | 🟢Yale HER2-TUMOR-ROIS(TCIA, ~40GB, CC-BY) · 🟢BCNB(1058) · 🟢TransNEO 이미지(Zenodo 6337925) · 🟡TransNEO 라벨(EGA EGAS00001004582, **지금 신청**) · IMPRESS(repo 확인) | TCIA/Zenodo 다운로드, S3/캐시 적재, `manifest.csv`(slide_id·cohort·경로·체크섬) | cohort별 manifest + 무결성 로그 | CPU, 저장 ~수백 GB | — | 4 코호트 manifest + 다운로드 검증; EGA 신청 접수번호 |
| **T2** | 라벨 정리 | Yale pCR(resp/non) · BCNB ER/PR/HER2/subtype · TCGA-CDR PFI+치료필드(보유) | 라벨 파싱·정규화·결측표, PAM50 소스(cBioPortal 1순위) | `labels.csv` per cohort + 결측 리포트 | CPU | T1 | 각 코호트 라벨 완전성 표; Yale 85·BCNB 1058 라벨 매칭 |
| **T3** | split 정책 갱신 | manifest+labels | 외부 코호트 = **never-train**·site-stratified 선언, `split_policy_v0.md §갱신`, `split_hash` 재발급 | 갱신 split_policy + hash | CPU | T1,T2 | **Critic(braveji) 검토** — Yale/BCNB/TransNEO가 train에 절대 미포함 보증 |

### 임베딩 층 — owner: **kkkim(Embedding)**

| ID | 작업 | 입력 | 방법 | 산출물 | 자원 | 의존 | 완료기준 |
|---|---|---|---|---|---|---|---|
| **T4** | 신규 코호트 임베딩 추출 | T1 WSI(Yale 273+IMPRESS 126[+TransNEO 168][+BCNB 1058]) | tile(256²@20×, Otsu) → **UNI frozen** 추출(외부=primary만; CONCH/CNN은 TCGA 한정) | tile feature(.h5/.npy) 영구저장 | 🔴**GPU ~14–57 GPU-h**(외부분, §2-1): 코어 Yale+IMPRESS ~13, +TransNEO 6, +BCNB 37 | T1, 🔴HF 승인 | 임베딩 완료 + 차원/카운트 검증 |

### 모델링 층 — owner: **sjpark(Modeling)** (+ kkkim 임베딩 연계)

| ID | 작업 | 입력 | 방법 | 산출물 | 자원 | 의존 | 완료/반증 |
|---|---|---|---|---|---|---|---|
| **T5** | **Exp-OUTCOME** (치료층 primary 반증) | Yale 임베딩 + pCR | frozen 파이프라인→anti-HER2 치료축 점수→pCR **AUROC+bootstrap CI**; baseline=예측HER2확률·cellularity·**Farahmand AUC~0.8(bar)**; DeLong | metrics.json + ROC | CPU(임베딩 재사용) | T4,T2 | **반증: 축 AUC CI가 0.5 포함 OR ≤ HER2확률 baseline → 치료층 음성 보고** |
| **T6** | **Exp3** (보류해제, 최대 GPU) | TCGA 임베딩 + ShuffleNet 512² 패스 + CTRP route | Arm B(병목 phenotype→ranking) vs Arm E(**SlideGraph∞ end-to-end** 재현); **TOST 동등정확도 + FAS 감사성**(rater 2인 κ) | 두 arm metrics + FAS | 🔴**GPU 최대 ~48–120 GPU-h(~2–5 GPU-day)**: Arm E GNN 학습/튜닝, 80GB에 sampling 적합 | T4(TCGA), Exp1 | TOST 동등 + FAS(B)−FAS(E)>0 (CI) |
| **T7** | **Exp7** (전이연료) | TCGA 임베딩 + 발현 | frozen UNI+회귀head로 proliferation/immune/ESR1/ERBB2/Hallmark 예측; **ssGSEA train-only**; per-sig Spearman+BH-FDR | 시그니처 예측 r 표 | CPU/경량GPU | T4, 발현데이터 | per-sig Spearman CI; **병목 승격 금지(categorical 유지)** |

### 치료근거 층 — owner: **jhans(Therapeutic Evidence)**

| ID | 작업 | 입력/데이터 | 방법 | 산출물 | 자원 | 의존 | 완료/반증 |
|---|---|---|---|---|---|---|---|
| **T8** | **Exp-AXES** (비-collinear 독립축) | 🟢PRISM/GDSC/CTRP · 🟢DepMap Chronos · 🟢LINCS L1000 | viability=**1축 통합**(3중계산 금지) + Chronos 의존성 + LINCS reversal; **3×3 Spearman 행렬**; rank-aggregate(RRA) 수렴 | 상관행렬 figure + 수렴점수 | CPU | T7(시그니처=route2 연료) | cross-axis r이 viability 내부만큼 높으면 독립 실패 보고 |
| **T9** | **Exp-SHUFFLE** (null) | T8 수렴 + 예측 phenotype(신뢰도) | **phenotype-shuffle 1000×** 수렴 재계산; 신뢰도 층화; random-phenotype 바닥 | perm p + 층화 곡선 | CPU | T8, T5/sjpark 신뢰도 | **반증: 셔플 수렴=참(perm p>0.05) → 수렴 artifact** |
| **T10** | **Exp-TNBC** (비-trivial showcase) | T8 수렴 + OncoKB/CIViC | KB-novel Basal/TNBC repurposing 후보 + **surprise score**; enrichment(Fisher/hypergeom +CI) | 후보 표 + enrichment | CPU, 🔴OncoKB token | T8 | **subgroup AUROC 금지**; KB-novel 수렴후보 0이면 SoC 재현뿐 |

### Critic / 거버넌스 층 — owner: **braveji(Critic 총괄)** + bio sub-check(sjpark/jhans)

| ID | 작업 | 입력 | 방법 | 산출물 | 자원 | 의존 | 완료/반증 |
|---|---|---|---|---|---|---|---|
| **T11** | **Exp-CRITIC** (비순환) | 후보가설 + KB | **생성KB(DGIdb/Reactome) ↔ 채점KB(OncoKB/CIViC) 분리**; primary 비-KB gate = **Yale 결과(T5)**; 기각률·precision·ROC | operating characteristic | CPU, 🔴OncoKB | T5,T8,T10 | **반증: 기각률≈0 OR 생성-KB 필터와 동일 → Critic 장식** |
| **T12** | **LLM/RAG 증거-결합** | DGIdb/Reactome/PubMed/ClinicalTrials.gov | **인용 강제 hypothesis card**(retrieval-grounded) + Critic claim 검증; **정량백본 미사용** | RAG 파이프라인 + card 스키마 | CPU, API(~0 GPU) | T11 | 인용 없는 출력 자동기각; Exp-CRITIC operating char로만 정당화(scoop=co-scientist 주의) |

---

## 2. 자원 소요 종합 (v0.2 재측정, 2026-06-10)

> 단가 = 프로젝트 실측 **1010 TCGA → UNI ~34 GPU-h ≈ 0.035 GPU-h/슬라이드**(추론) 기준. v0.1 최소셋 대비 변화: **Exp3 포함(최대 항목 신규)** + 외부 코호트 4개 임베딩 + Exp7/신규 치료실험(GPU≈0).

### 2-1. 임베딩 추출 (T4, 1회·스트리밍)

| 모델 | 대상 코호트 | 슬라이드 | GPU-h |
|---|---|---|---|
| **UNI (primary)** | TCGA 1010 + Yale 273 + IMPRESS 126 | 1409 | ~49 |
| UNI (조건부) | + TransNEO 168 (EGA 라벨 도착 후) | +168 | +6 |
| UNI (swing/선택) | + BCNB 1058 (대규모 phenotype 외부검증) | +1058 | **+37** |
| **CONCH (Exp1 ablation)** | TCGA 1010 only | 1010 | ~35 |
| ImageNet/ShuffleNet | TCGA only (Exp1c + Exp3 ArmE 512² 패스) | 1010 | ~20 |

→ **임베딩 코어 ≈ 104 GPU-h(~4.5 GPU-day)**; BCNB 포함 시 ~141; TransNEO 포함 시 +6.

### 2-2. 실험별 GPU

| 항목 | GPU | 비고 |
|---|---|---|
| **T6 Exp3 — SlideGraph∞ GNN 학습(Arm E)** | **~48–120 GPU-h (~2–5 GPU-day)** | ★**단일 최대·불확실 항목.** 1010 patch-graph EdgeConv + pairwise ranking 학습/튜닝. 80GB에 sampling으로 적합 |
| T5 Exp-OUTCOME / T7 Exp7 | ~0 (경량 head) | 임베딩 재사용, CPU/경량GPU |
| Exp1/Exp2 head·probe | <12 GPU-h | 임베딩 재사용 |
| **T8–T12** (AXES/SHUFFLE/TNBC/CRITIC/RAG) | **0 (CPU)** | DepMap/LINCS=행렬, KB/RAG=API |
| Exp6 LoRA (선택) | +24–48 GPU-h, **VRAM ≥24GB** | 최후순위 |

### 2-3. 총계 & 스펙

| 구분 | 값 |
|---|---|
| **코어 GPU 총량(Exp6 제외)** | **임베딩 ~104 + Exp3 ~48–120 + 기타 <12 ≈ 165–235 GPU-h ≈ 7–10 A100-day** |
| BCNB 포함 시 | +37 GPU-h (~1.5 GPU-day) — swing 요인 |
| **VRAM** | 추론 <16GB · GNN 학습 80GB에 적합 · LoRA 24GB → **A100 80GB 단일로 충분**(다중 GPU 불필요) |
| **병목** | VRAM 아닌 **시간/슬롯**. T6(Exp3)·T4는 **연속 다일(multi-day) 슬롯 전용 예약** 필요 |
| **저장** | Yale 40GB + BCNB/TransNEO raw 수백 GB; 임베딩 영구·소형 → 200GB cache/2TB root 내 |
| **GPU 슬롯** | T4·T6 = `#biop02-alerts` 예약 필수 (09–13/13–17/17–21/21–01 중 다일 확보) |

### 2-4. GPU 요청 한 줄 (모임/braveji용)
> **A100 80GB 단일이면 충분**(다중 GPU·≥40GB full-FT 불필요). 코어 ~7–10 GPU-day 소요, 그중 **Exp3 GNN(~2–5일)과 1회 임베딩(~4.5일)이 지배** → 두 항목에 연속 다일 슬롯 배정. 선택 Exp6 LoRA 시 VRAM ≥24GB(80GB에 포함). BCNB 외부검증 포함은 +1.5일(swing).

## 3. 접근 blocker (병행 처리, T6/T8 등 block 금지)

| 자원 | 상태 | 조치 |
|---|---|---|
| Yale/BCNB/DepMap/LINCS/GDSC/CTRP/DGIdb/CIViC/Open Targets/Reactome | 🟢 개방 | 즉시 |
| TransNEO **라벨** (EGA) | 🟡 controlled ~수주 | T1에서 **지금 신청**; Yale가 primary라 block 아님 |
| OncoKB API | 🔴 token | open KB로 floor 도달범위 + residual gap (T10/T11) |
| UNI/CONCH (HF) | 🔴 승인대기 | 진행중; 미승인 시 dummy 임베딩으로 T5/T8 파이프라인 선개발 |

## 4. 의존성 체인 (배분 순서)

```
T1(데이터)─T2(라벨)─T3(split)        ← jamie, 먼저
        └→ T4(임베딩, kkkim) ─┬→ T5(Exp-OUTCOME, sjpark) ─┐
                              ├→ T6(Exp3, sjpark) [GPU 최대]│
                              └→ T7(Exp7, sjpark/kkkim) ─→ T8(Exp-AXES, jhans)
                                                            └→ T9(SHUFFLE)·T10(TNBC, jhans)
                                                                    └→ T11(Exp-CRITIC, braveji)─T12(RAG)
```

## 5. Cross-review 배분 (owner≠reviewer)

| 작성자(작업) | Critic 담당 |
|---|---|
| jamie (T1–T3 데이터/split) | braveji |
| kkkim (T4 임베딩) | jamie |
| sjpark (T5–T7 모델링) | kkkim |
| jhans (T8–T10 TE) | braveji 총괄(+ bio sub-check sjpark) |
| braveji (T11–T12, 본인 산출물) | **타인 검토 필수**(sjpark/jhans 분담) — anti-self-reference |

---

신규 작업 = **T1–T12**. braveji는 §1 표로 JIRA 이슈 생성, §4 순서로 배분, §3 blocker 병행 착수, §2로 GPU 슬롯 예약 조율.

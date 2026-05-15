# SpatialPathoAgent — 운영 계획서 (v0.1)

> 한 곳에서 다 본다. **다음 1주 행동 + 매주 운영 방식 + 16주 milestone + 기획 필요 항목**.
> 작성: 2026-05-15 (gglee). 차주 회의 후 ykji에게 인계 → v0.2로 갈아엎음.

---

## 0. 한 줄 요약 + 현재 위치

> **목표:** H&E WSI → morphology embedding → molecular phenotype 예측 → DepMap/GDSC transfer 기반 **ranked therapeutic hypothesis** + Scientific Critic 검증.
> **이건 DRP 모델이 아님** (drug structure 입력 없음, BRCA-only, hypothesis-only).

| | |
|---|---|
| **Kickoff** | 2026-05-12 (화, 완료) |
| **오늘** | 2026-05-15 (금, Kickoff D+3) — **첫 정기 미팅 날** |
| **정기 미팅** | **매주 금요일.** 매주 진행상황(progress) + 다음 주 분배 |
| **다음 미팅** | 2026-05-22 (금, D+10) — Sprint 0 closeout |
| **공식 일정** | Paper A 16주 / Paper B 후속 16–20주 |
| **12주 압축안** | stretch goal, 공식 plan 아님 |

### 리더십
- **리더:** gglee (이건규) — 회의 진행 · 의사결정 · 외부 커뮤니케이션 · 일정 관리
- **Orchestrator (실무 운영 메인):** ykji (지용기) — pipeline 조정, AGENTS.md, schema 폴더, 인프라(Jira/Confluence/GitHub/agent) 실무 owner, 실험 registry 관리
- 분담 원칙: **결정은 gglee, 실행 인프라는 ykji.** ykji가 들고 오는 옵션 비교안을 gglee가 최종 sign-off.

**현재 Sprint:** Sprint 0 (Kickoff ~ 2주차, 데이터 access · repo · storage · governance · 협업 인프라 정리).

---

## 1. 🔥 2026-05-15 (금) 첫 정기 미팅 안건 (60분)

> Kickoff(5/12) D+3. **포커스: Kickoff 진행상황 점검 + 협업 인프라(Jira·Confluence·GitHub·Agent) 셋업 방향을 다음주(5/22)까지 끝내자.**
> 리더 진행: gglee. 실무 owner: ykji. 서기: ykji (회의록 작성).

### Slot 1 — Kickoff D+3 progress 점검 (10')
한 사람당 1분, 입으로 짧게:
- **HF UNI/CONCH 신청** — gglee · gkkim 둘 다 신청 완료? 승인 도착 여부.
- **SSH 5명 접속** — 5/12 회의 후 안정 접속? 아직 막힌 사람?
- **컨테이너 / CLI 셋업** — 본인 어디까지 (CLI 1개 선택, `/workspace/agents/<role>/` 폴더 생성)
- **Embedding 분담 협의** — gglee ↔ gkkim 결과 (제안: gglee=tiling/setup, gkkim=feature extraction)

**진행 룰:** "아직 못 함"이면 1줄로. 디테일은 회의 후 1:1. 10분 넘기지 말 것.

### Slot 2 — 협업 인프라 셋업 방향 (25', 안건당 5–7분)

> **이번 미팅의 메인.** "다음주(5/22)까지 셋업한다"를 합의하고, **어떻게 할지**를 정한다.
> 4개 안건 모두 ykji가 "다음주까지 옵션 비교안 1쪽" 들고 오기로 결정해도 됨 — 단 오늘 **방향성**은 박는다.

#### 2-1. Jira (5')
- **용도:** Sprint 보드, 이슈/태스크 트래킹, 5명 진행상황 한눈에
- **결정할 것:**
  - 워크스페이스: 회사 Atlassian 사용 가능? 별도 무료 plan? (Free tier = 10 user OK)
  - 프로젝트 키 (예: `SPA` — SpatialPathoAgent)
  - 보드 타입: Scrum (2주 sprint) vs Kanban
  - 이슈 타입: Epic(=Sprint 0~8) / Story / Task / Bug
- **owner:** ykji가 1쪽 셋업 가이드 + 5/22까지 워크스페이스 생성
- **합의 안:** ☐ Atlassian Free + Scrum + `SPA` 키 / ☐ 다른 안

#### 2-2. Confluence (5')
- **용도:** AGENTS.md / 회의록 / Sprint review / 논문 draft / Risk log 보관
- **결정할 것:**
  - 별도 도구 vs Notion vs GitHub Wiki vs Jira와 함께 Atlassian
  - 회의록은 어디? Sprint retro는 어디?
- **owner:** ykji가 5/22까지 공간 + 페이지 트리 초안
- **합의 안:** ☐ Confluence (Jira와 같은 워크스페이스) / ☐ Notion / ☐ GitHub Wiki

#### 2-3. GitHub (7')
- **용도:** 코드 repo (모든 agent 폴더) + PR review + Issue tracker (Jira와 연동 또는 단독)
- **결정할 것:**
  - GitHub Org 이름 + private repo
  - **mono-repo (`spatial-pathoagent` 하나) vs multi-repo (agent별)** — 추천: mono
  - Branch protection: `main` 보호, PR + 1 reviewer 필수
  - PR template / Issue template / CODEOWNERS (agent별 owner)
  - Jira ↔ GitHub 연동 (Smart Commits, branch 자동 link)
- **owner:** ykji가 5/22까지 org + repo + 기본 구조 push
- **합의 안:** ☐ mono-repo + main 보호 + CODEOWNERS + Jira 연동 / ☐ 다른 안

#### 2-4. Agent 셋업 (8')
- **용도:** 각자 본인 agent 작업 공간 + prompt + schema 통일 (PDF 14장 패턴)
- **결정할 것:**
  - 폴더 표준: `agents/<role>/` + `prompts/<role>_prompt.md` + `schemas/*.json` (PDF 14장 그대로)
  - 5명 컨테이너 분리 → **git repo로 동기화 필수** → 매번 본인 컨테이너에서 `git pull/push`
  - CLI 선택: Claude Code / Codex CLI / OpenCode (출력 schema만 통일이라 본인 자유)
  - 첫 prompt 5개 (data / embedding / modeling / therapeutic_evidence / scientific_critic) — 5/22까지 본인이 자기 prompt 1쪽 draft
- **owner:** ykji = AGENTS.md v0.2 작성 (폴더 규약 + cross-review 룰). 본인 prompt = 각자.
- **합의 안:** ☐ PDF 14장 폴더 구조 그대로 + CLI 본인 선택 + 5/22까지 prompt 본인 draft

### Slot 3 — 다음 주(5/22)까지 실행 분배 (15')

| 사람 | 5/22까지 들고 올 것 |
|---|---|
| **gglee** (리더) | Kickoff 회의록 정리분 + Critic checklist v1 + critic_report.schema.json v0.1 + Embedding tiling 셋업 |
| **ykji** (Orchestrator) | Jira 워크스페이스 + Confluence 공간 + GitHub org/repo + AGENTS.md v0.2 + S3/NAS/MinIO 비교안 1쪽 |
| **jmryu** | TCGA-BRCA manifest CSV v0.1 + CPTAC-BRCA 메모 1쪽 + clinical 메타데이터 추출 검증 |
| **gkkim** | HF 승인 즉시 1 slide UNI pilot + Embedding feature extraction 분담 + hypothesis.schema.json v0.1 |
| **sjpark** | dummy embedding 기반 MLP baseline 1회 학습 성공 + 3 trivial baseline 스켈레톤 + eval_metrics.md 1쪽 |

**진행 룰:** 본인 입으로 "OK 가능 / 못 함" 표명 받기. 침묵 = 통과 금지.

### Slot 4 — 다음 회의(5/22) 안건 + 마지막 점검 (10')
- 5/22 안건 prelock:
  1. Sprint 0 walk-through (5명 × 5분)
  2. Jira/Confluence/GitHub/Agent 셋업 결과 점검 (작동하나)
  3. S3 / NAS / MinIO 최종 결정 (ykji 비교안)
  4. AGENTS.md v0.2 sign-off
  5. Sprint 1 분배 (Embedding pipeline + 첫 endpoint)
- 마지막 점검:
  - [ ] 다음 회의 5/22 (금) 시간·장소 확정 (온/오프라인?)
  - [ ] 회의록 ykji가 작성 → 슬랙 공유
  - [ ] 5명 모두 본인 5/22 산출물 OK 표명?

---

## 1B. 🗓️ 5/15 ~ 5/22 Daily (회의 후 1주)

> 본업 병행. 실작업 1–2h/일 기준.

| 날짜 | 누가 / 뭐 |
|---|---|
| **5/15 (금) — 회의 후** | gglee: 회의록 정리 + 5명 슬랙 공유 · ykji: Jira/Confluence workspace 신청 시작 · 전원: HF 신청 미완료자 마무리 |
| **5/16 (토)** | (선택) ykji: GitHub org + private repo 생성 · gglee: critic_report.schema.json draft 시작 |
| **5/17 (일)** | (선택) jmryu: TCGA GDC manifest 다운로드 시도 · gkkim/gglee: 환경 셋업 (openslide, libvips, pyvips, timm) |
| **5/18 (월)** | ykji: AGENTS.md v0.2 폴더 규약 + schema 위치 · sjpark: `/workspace/agents/modeling/` + dummy MLP 스켈레톤 |
| **5/19 (화)** | gglee: Critic checklist 7항목 중 5개 자세히 · jmryu: manifest CSV v0.1 · gkkim: HF 승인 오면 1 slide pilot |
| **5/20 (수)** | ykji: S3/NAS/MinIO 비교안 1쪽 + AGENTS.md v0.2 마무리 · sjpark: 3 trivial baseline 스켈레톤 + eval_metrics.md |
| **5/21 (목)** | 전원: 5/22 walk-through 5분 발표 준비 · gkkim: hypothesis.schema.json v0.1 (gglee critic draft 받은 후) |
| **5/22 (금)** | **정기 미팅 #2 — Sprint 0 closeout** |

### 1주 합격선 (5/22 가져갈 것)
**필수 (못 들고 오면 Sprint 1 시작 못 함):**
- ykji: Jira + Confluence + GitHub repo **작동** + AGENTS.md v0.2
- gglee: Critic checklist v1 + critic schema v0.1
- jmryu: manifest CSV v0.1 + label 후보 표
- gkkim + gglee: HF 신청 완료 + 환경 셋업 (pilot은 가중치 승인 시)

**Nice to have:** sjpark dummy MLP / gkkim Therapeutic Evidence draft / gpu.lock wrapper / rclone

---

## 2. 📅 매주 운영 방식 (cadence)

### 정례 미팅 — 매주 금요일 60분 (고정)
- **목적:** 이번 주 progress 점검 + 다음 주 분배 + blocker 해결 + 안건 결정
- **표준 순서 (60분):**
  - Slot 1 (10'): 지난 주 progress 점검 — 5명 × 1–2분 (입으로 짧게)
  - Slot 2 (25'): 결정 안건 (5분 컷) — 사전 ykji가 안건지 1쪽 / 옵션 비교안
  - Slot 3 (15'): 다음 주 분배 — 각자 OK 표명
  - Slot 4 (10'): 다음 미팅 안건 prelock + 마지막 점검
- **리더 (진행 · 의사결정):** gglee (고정)
- **Orchestrator (실무 owner · 안건지 준비 · 운영):** ykji (고정)
- **서기 (회의록 작성):** ykji — 진행과 서기 분리
- **2주 sprint 경계:** 격주 금요일 미팅 = Sprint review + Sprint planning 통합 (Sprint 0 closeout = 5/22)

### Daily 슬랙 standup (텍스트)
- 매일 1줄: "어제 한 것 / 오늘 할 것 / blocker". 공통 채널.
- 본업 병행이라 강제 X, **blocker만은 그날 안에 표명**이 룰.
- 셋업 후 Jira board 카드 본인이 In Progress / Done 이동.

### Sprint 회고 (2주에 1회, sprint 끝 금요일 미팅 안에 흡수)
- 잘된 것 / 막힌 것 / 다음 sprint 개선점 — 5–7분 간단히
- Confluence에 매 sprint retro 1쪽 누적

### Critic cross-review 룰 (PDF 5장)
- owner ≠ reviewer. 자기 결과 자기 critic 금지.
- 모든 hypothesis 출력 = `claim_level` + `critic_status` 필드 필수.
- 결과 공유는 Critic pass 후.

### 산출물 표준 (PDF 6·8장)
- 모든 실험: `experiments/<user>/<date>/{config.yaml, model.pt, metrics.json, predictions.npy, critic_report.json}` + git commit hash
- Raw data = S3 read-only. Processed/embedding = version 명시.
- 결과 공유 = 표준 JSON schema. CLI(Claude/Codex/OpenCode) 무관.

---

## 3. 🗺️ 16주 Roadmap (Paper A 기준)

> PDF 12장 Sprint 구조 + 매주 금요일 cadence. **각 sprint = 2주, sprint 경계 = 격주 금요일 미팅.**
> 총 8 sprint × 2주 = 16주. Paper A target = 9월 초.

| Sprint | 기간 (금→금) | 목표 | 핵심 산출물 | Sprint close 미팅 |
|---|---|---|---|---|
| **Sprint 0** | 5/12 (화 Kickoff) → **5/22** | 인프라 + governance + 협업 셋업 | Manifest CSV v0.1 · AGENTS.md v0.2 · schemas/ · S3 결정 · 1 slide pilot · Jira+Confluence+GitHub 작동 · Critic checklist v1 | 5/22 |
| **Sprint 1** | 5/22 → **6/05** | Embedding pipeline + 첫 phenotype | TCGA-BRCA 전체 embedding · ER status MLP · 3 trivial baseline 비교 · 첫 critic_report.json | 6/05 |
| **Sprint 2** | 6/05 → **6/19** | Multi-endpoint phenotype | ER + PR + HER2 + PAM50 × {MLP / attention MIL} 매트릭스 | 6/19 |
| **Sprint 3** | 6/19 → **7/03** | Attention MIL + cross-dataset | TCGA train → CPTAC test 외부 검증 · counterfactual check | 7/03 |
| **Sprint 4** | 7/03 → **7/17** | TIL/immune phenotype + endocrine rule | Immune phenotype score · endocrine rule sample | 7/17 |
| **Sprint 5** | 7/17 → **7/31** | Paper A Figure 1·2 draft | Pipeline figure · embedding UMAP sanity · 1차 결과 narrative | 7/31 |
| **Sprint 6** | 7/31 → **8/14** | Paper A Figure 3·4 + external validation lock | Phenotype baseline 비교 · anti-shortcut sanity · 외부 검증 lock | 8/14 |
| **Sprint 7** | 8/14 → **8/28** | Paper A draft + Critic 전 항목 pass | Methods · Results · Discussion draft · Critic 7항목 pass | 8/28 |
| **Sprint 8** | 8/28 → **9/11** (16주차) | Paper A submission | 내부 → 외부 review → 제출 · target journal 결정 | 9/11 |

### Paper B Follow-up (~16–20주, 9/11 → ~2027-02-01)
- Therapeutic Evidence Agent 본격 개발 (DepMap PRISM + GDSC pathway-drug linking)
- Patient ↔ cell line similarity mapping
- Ranked hypothesis 출력 + Critic 검증 (Paper B 5 figures)
- Paper B 제출

### 매 sprint review에서 점검 (매 격주 금요일)
- Critic 7항목 중 현재 sprint에서 어디까지 pass 받았나
- 산출물 표준 (config / metrics / predictions / critic_report) 모두 저장됐나
- 다음 sprint 분배 OK 표명

---

## 4. 🧠 기획해야 할 것 (지금 답 없음 / 다음 회의 안건 후보)

> 회의 1번에 안 들어간 결정들. **Sprint 0~1 끝나기 전에 확정 필요.**

### 다음 정기 미팅 (5/22 금) 안건 — Sprint 0 closeout
1. **Sprint 0 walk-through** — 5명 × 5분 (manifest / Jira·Confluence·GitHub 작동 / Critic checklist v1 / dummy MLP)
2. **S3 / NAS / MinIO 최종 결정** — ykji 비교안 보고
3. **AGENTS.md v0.2 sign-off** — gglee가 ykji draft 확정
4. **잠정 GPU 사용 룰** — gpu.lock wrapper 나오기 전까지 캘린더+슬랙 알림 (PDF 7장: 09–13 / 13–17 / 17–21 슬롯)
5. **TCGA controlled access dbGaP — PI 누구로?** (학생 단독 X, 지도교수 사인 필요)
6. **Cross-review 페어링 확정** — gglee embedding을 sjpark/jmryu 중 누가 critic
7. **Sprint 1 분배** — Embedding pipeline + 첫 endpoint (ER status)

### Sprint 1 시작 전 (~5/22) 결정
8. **첫 endpoint 확정** — ER status binary 우선이지만 1·2·3순위 ranking
9. **Patient-level split 정책 lock** — jmryu split_policy_v0 → 5명 OK → 변경 금지
10. **실험 추적 도구** — wandb / MLflow / DVC / git만? AGENTS.md 안에 박을지

### Sprint 2~3 결정
11. **MIG 파티션 재검토** — Embedding wall-clock 측정 후 (Sprint 1 결과 보고)
12. **Attention MIL 구체 구조** — DSMIL / TransMIL / CLAM 중 선택
13. **Target journal 후보** — Paper A 제출 최소 8주 전엔 정해야

### 미정 (장기)
14. **TCGA controlled access 승인 후 활용 범위** — somatic mutation 어디까지
15. **Paper B Therapeutic Evidence 개발 본격 착수 시점** — Paper A submission 직후? 또는 병행?
16. **외부 패널/멘토 review 시점** — Paper A draft Sprint 7 즈음
17. **Pan-cancer 확장 여부** — Paper B 이후. BRCA-only 원칙 유지.

---

## 5. ⚠️ Risk 리스트 (현재 living)

| Risk | 영향 | 대응 |
|---|---|---|
| HF UNI/CONCH 승인 지연 | Embedding pilot 못 함 → Sprint 1 시작 지연 | dummy embedding (`torch.randn(1,1024)`)으로 코드 흐름 검증, 승인 즉시 swap |
| dbGaP controlled access 몇 주 | somatic mutation 못 씀 | open access slides + clinical만으로 v0, Paper A scope에서 controlled 제외 |
| GPU 1대 5명 충돌 | 학습 wall-clock 폭주 | 잠정 캘린더 룰 → Sprint 0 끝나면 gpu.lock wrapper |
| 2 TB 디스크 부족 | raw WSI 못 들어감 | raw = S3 only, `/data/cache/` LRU 200 GB, embedding만 영구 |
| gglee 1인 2역 + 회의 리딩 | Critic 작업 누락 | Sprint 0은 checklist v1까지만, 본격 critic은 Sprint 1부터 |
| sjpark 의존성 묶임 | dummy 대기로 1주 날림 | dummy embedding으로 코드 흐름부터 잡기 (강제) |
| 회의 5분 컷 불가 | Sprint 0 안건 10분 빨려들어감 | co-facilitator 1명 지정 (ykji가 노트+타이머) |
| 공유 인프라 미정 (repo/slack) | AGENTS.md 만들어도 5명 동기화 못함 | Sprint 0 안에 git repo + Slack 채널 확정 |
| Critic = 자기 결과 검증 위험 | claim_level 오용 | owner ≠ reviewer 페어링 확정 |
| WSI tiling 처리량 병목 | Embedding wall-clock 폭주 | gkkim+gglee 1 slide pilot으로 측정 → MIG 결정 input |

---

## 6. 📚 Appendix

### 역할 매핑 (Kickoff 확정)
| 사람 | username | 포트 | 역할 |
|---|---|---|---|
| jmryu | jmryu | 2201 | Data Agent |
| gkkim | gkkim | 2202 | Embedding + Therapeutic Evidence |
| gglee | gklee | 2203 | Embedding + Scientific Critic + **리더 (회의 진행 · 결정)** |
| sjpark | sjpark | 2204 | Modeling Agent |
| ykji | ykji | 2205 | **Orchestrator (실무 운영 메인 · 안건지 · 서기 · Jira/Confluence/GitHub/Agent 셋업)** |

### 인프라 (Kickoff 확정)
- 서버: A100 80GB × 1, 24 CPU, 188 GiB RAM, 2 TB root
- IP: `61.109.239.220`, SSH key only
- 데이터 저장 정책: raw=S3 only / cache LRU 200 GB / embedding 영구

### 데이터
- TCGA-BRCA (~1.5K slides, open access slides + clinical 우선)
- CPTAC-BRCA (IDC gs:// bucket)
- DepMap PRISM + GDSC (cell line × drug sensitivity)
- **BRCA-only. Pan-cancer 안 함.**

### Critic 7항목 (PDF 11장)
1. Data leakage check
2. Baseline comparison (random, subtype-only, pixel-mean)
3. Counterfactual check (핵심 feature 제거 시 ranking 변화)
4. Cross-dataset check (DepMap PRISM vs GDSC 일관성)
5. Biological plausibility (pathway-drug 연결 타당성)
6. DRP framing check ("drug response prediction" 표현 금지)
7. Claim-level check (`hypothesis_only` 외 사용 시 사유)

### Paper A Figure 계획 (PDF 13장)
- Fig 1: Pipeline (H&E → embedding → phenotype)
- Fig 2: Embedding sanity (UMAP by subtype/quality)
- Fig 3: Phenotype prediction baseline 비교
- Fig 4: External validation + anti-shortcut sanity

### Paper B Figure 계획
- Fig 1: Therapeutic Evidence + Critic pipeline
- Fig 2: Drug ranking (NDCG@10, Hit@K)
- Fig 3: Track-separated hypothesis 예시
- Fig 4: Critic 결과 (pass/caution/reject)
- Fig 5: Anti-shortcut validation

### 실패 방지 7원칙 (PDF 15장)
1. 데이터 욕심 금지 (BRCA부터)
2. 모델 욕심 금지 (MLP → attention MIL 순서)
3. Virtual spatial proteomics 욕심 금지
4. "drug response prediction" 표현 금지
5. Critic 없이 결과 공유 금지
6. 구조 없이 Claude/Codex/OpenCode 쓰면 망함
7. 실험 기록 안 하면 망함

---

## 7. 변경 이력
- 2026-05-15 v0.1 — gglee 작성. 회의 결정 + PDF v3.1 roadmap 통합.
- 2026-05-15 v0.2 — 리더십 정정 (gglee 리더 유지, ykji는 Orchestrator로 실무 운영 메인). 정기 미팅 cadence 화 → **금**. 5/15 첫 정기 미팅 안건 (Jira/Confluence/GitHub/Agent 셋업) 추가. Sprint 0~8 날짜를 금요일 경계로 재정렬.
- (다음) v0.3 — 5/22 미팅 후 AGENTS.md v0.2 + S3 결정 반영.

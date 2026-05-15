# 차주(2026-05-19)까지 팀원별 숙제 — 공유용

> 이 문서는 팀 전체에게 공유 가능. 본인 섹션만 잘라서 슬랙 DM으로 보내도 OK.

---

## ⚠️ 공통 함정 (전원 숙지)

1. **UNI / CONCH 가중치는 HF gated.** Mahmood Lab 승인 며칠 걸림. 신청 안 하면 embedding 파일럿 못 함 → **오늘/내일 안에 신청부터.** (gkkim, gklee)
2. **TCGA controlled access (somatic mutation 등)는 dbGaP 신청.** 몇 주 걸림. 일단 **open access slides + clinical만으로 v0 시작**, controlled는 병행 신청만. (jmryu)
3. **SSH 키 등록은 오늘 회의에서 끝낸다.** 미완료자는 회의 후 1:1.
4. **CLI 1개 본인 선택.** Claude Code / OpenAI Codex CLI / OpenCode 중. 출력 schema는 통일이라 무관.

---

## 1. 류재면 (jmryu) — Data Agent

**워크로드 추정:** 5–7시간 분산 (본업 병행 가정)

### Day 1–2 — 컨테이너 접속
- [ ] SSH 접속 (`ssh -p 2201 jmryu@61.109.239.220`)
- [ ] CLI 1개 셋업 (Claude Code / Codex / OpenCode 중 택1)
- [ ] `/workspace/agents/data/` 폴더 생성

### Day 3–5 — 데이터 수집 메인
- [ ] **TCGA-BRCA manifest 다운로드** — GDC Portal에서 `TCGA-BRCA` filter + `Slide Image` (.svs) + `open access`. JSON manifest → CSV 변환.
- [ ] **CPTAC-BRCA 어디서 받을지 결정** — IDC (Imaging Data Commons) gs:// bucket 가장 편함. PDC도 옵션. 1쪽 메모.
- [ ] **manifest CSV v0.1** — columns: `slide_id, patient_id, source, file_size_mb, download_url`. 환자당 slide 수 분포 같이.
- [ ] **clinical 메타데이터 추출 검증** — 1명 환자 sample로 ER/PR/HER2 IHC, PAM50, BRCA1/2 mutation, OS/DFS — TCGA-CDR 또는 cBioPortal에서 뭐가 바로 나오고 뭐가 안 나오는지 표로.

### Day 6–7 — 정리
- [ ] **`split_policy_v0.md` 1쪽** — patient-level split (no leakage), 외부 validation 설계 (TCGA train → CPTAC test 또는 site-stratified)
- [ ] 차주 walk-through 5분 발표 준비

**합격선:** manifest CSV v0.1 + label 후보 1쪽이면 OK. controlled access는 차주 안건.

---

## 2. 김가경 (gkkim) — Embedding Agent + Therapeutic Evidence Agent

**워크로드 추정:** 8–10시간 (1인 2역)
**우선순위:** Embedding이 critical path. Therapeutic Evidence는 week 2–3로 미뤄도 OK.

### Day 1 — 가중치 신청 (오늘 안에)
- [ ] SSH 접속 (`ssh -p 2202 gkkim@61.109.239.220`)
- [ ] **UNI 가중치 HF 신청** — https://huggingface.co/MahmoodLab/UNI
- [ ] **CONCH 가중치 HF 신청** — https://huggingface.co/MahmoodLab/CONCH

### Day 2–4 — Embedding (gklee와 분담)
- [ ] **gklee와 분담 합의** — 누가 tiling, 누가 feature 추출? (gklee가 먼저 DM 줄 예정)
- [ ] `agents/embedding/setup.sh` — openslide-tools, libvips, pyvips, openslide-python, timm, huggingface_hub
- [ ] `tile_config.yaml` — tile_size, magnification (20x or 40x), background filter, stride
- [ ] **가중치 승인 즉시:** 1 slide pilot — UNI feature 추출. 출력 shape / 시간 / 디스크 측정
- [ ] pilot 결과 1쪽: "1 slide 처리 X분, feature N개, M MB"

### Day 5–7 — Therapeutic Evidence (가볍게)
- [ ] `agents/therapeutic_evidence/depmap_schema.md` — DepMap PRISM + GDSC 테이블 구조 1쪽 (cell line, drug, sensitivity 컬럼)
- [ ] `schemas/hypothesis.schema.json` v0.1 — gklee의 `critic_report.schema.json` draft 받은 뒤 시작 (필드 호환 위해)

**합격선:** HF 신청 완료 + 환경 셋업 + (가능하면) 1 slide pilot. Therapeutic Evidence 2개 중 1개만 와도 OK.

---

## 3. 이건규 (gklee) — Embedding Agent + Scientific Critic Agent

**워크로드 추정:** 9–11시간 (1인 2역 + 오늘 회의 리딩)

### 오늘 (회의 리딩)
- [x] 회의 진행
- [ ] 회의록 작성 → ykji 인수인계

### Day 1–2 — 가중치 신청 + 셋업
- [ ] SSH 접속 (`ssh -p 2203 gklee@61.109.239.220`)
- [ ] **UNI/CONCH HF 신청** — gkkim과 둘 다 신청

### Day 3–5 — Embedding (gkkim과 분담)
- [ ] gkkim과 합의한 분담대로 실행 (gklee 추천: gklee=tiling/setup, gkkim=feature extraction)

### Day 5–7 — Critic
- [ ] **`agents/critic/checklist_v1.md`** — PDF 7개 항목 expansion (Data leakage / Baseline / Counterfactual / Cross-dataset / Biological plausibility / DRP framing / Claim-level). 각 항목: 입력 / 검사 방법 / pass·caution·reject 기준.
- [ ] **`agents/critic/anti_patterns.md`** — "DRP로 보이게 쓰는 표현" 사례 + 교정
- [ ] **`schemas/critic_report.schema.json` v0.1** — gkkim에게 먼저 draft 보낼 것
- [ ] **Cross-review 페어링 제안 1쪽** — gklee 본인 embedding 결과 critic을 누가 맡을지 (sjpark? jmryu?)

**합격선:** Critic checklist v1 (7개 중 5개 자세히 + 2개 outline). HF pilot은 가중치 승인 안 오면 환경 셋업까지만.

---

## 4. 박세진 (sjpark) — Modeling Agent

**워크로드 추정:** 4–6시간 (가장 여유)

### Day 1–2 — 접속
- [ ] SSH 접속 (`ssh -p 2204 sjpark@61.109.239.220`)
- [ ] CLI 1개 셋업
- [ ] `/workspace/agents/modeling/` 폴더 생성

### Day 3–5 — 코드 스켈레톤 (dummy 기반)
- [ ] **`baselines/mlp.py`** — input `(N, 1024)`, output phenotype logit. 1-layer + sigmoid. `torch.randn`으로 dummy embedding 만들어 학습 1회 돌아가는 것까지.
- [ ] **3 trivial baselines** — `random_baseline.py`, `subtype_only.py`, `pixel_mean.py` 코드 스켈레톤만
- [ ] **`configs/baseline_er_status.yaml`** — 첫 endpoint(ER status binary) config 양식: `dataset, split, embedding_path, model, lr, epochs, batch, metric, output_dir`

### Day 6–7 — 메트릭/리포팅
- [ ] **`eval_metrics.md` 1쪽** — AUROC, balanced accuracy, calibration, confusion matrix. Reporting 표 양식 1개.

**합격선:** dummy embedding으로 end-to-end 흐름 1회 성공 + config/메트릭 양식. **embedding 안 와도 dummy로 진행** — 의존성 묶이지 말 것.

---

## 5. 지용기 (ykji) — Orchestrator

**워크로드 추정:** 10–12시간 (셋업 + 의사결정 대부분)

### Day 1–3 — AGENTS.md + schemas 폴더
- [ ] **AGENTS.md v0.1** (`/workspace/AGENTS.md`) — 폴더 규약, schema 위치, CLI-agnostic 프롬프트 원칙, Critic cross-review 룰. **다른 사람 숙제의 채점 기준.**
- [ ] **`/workspace/schemas/` 폴더** — gkkim의 `hypothesis.schema.json` + gklee의 `critic_report.schema.json` 통합 위치 미리 만들어두기

### Day 4–5 — 인프라
- [ ] **`/data/gpu.lock` wrapper 스크립트** — `gpu-run <cmd>` 형태. lock + timeout + 강제 해제 옵션.
- [ ] **베이스 이미지에 rclone 추가** — `~/docker/Dockerfile` 1줄 + 재빌드 + 5명 컨테이너 재시작 영향 평가
- [ ] **S3 / NAS / MinIO 옵션 비교 1쪽** — 차주 회의에서 결정용

### Day 6–7 — 운영 도구
- [ ] **`run_experiment.sh` 스켈레톤** — config 받아 `experiments/<user>/<date>/{config.yaml, model.pt, metrics.json, predictions.npy, critic_report.json}` 자동 생성 + git commit hash
- [ ] **차주 회의 리딩 인수** — gklee에게서 회의록 + Sprint 0 결정사항 받기

**합격선:** AGENTS.md v0.1 + schemas 폴더 + S3 옵션 비교. gpu.lock wrapper / rclone 추가는 차주로 미뤄도 OK. **v0.1은 거칠어도 OK, 차주에 다 같이 v0.2.**

---

## 📅 우선순위 컷오프 (다 못 하면 이 순서로)

**필수:**
- jmryu: manifest CSV v0.1 + label 후보 1쪽
- gkkim+gklee: HF 신청 완료 + 환경 셋업 + (가능하면) 1 slide pilot
- gklee: Critic checklist v1
- ykji: AGENTS.md v0.1 + schema 폴더

**Nice to have:**
- sjpark: dummy MLP 돌아가는 것까지
- gkkim: Therapeutic Evidence 2개 중 1개만 와도 OK
- ykji: gpu.lock wrapper / rclone 추가는 차주 가능

**완전히 차주로 미뤄도 됨:**
- TCGA controlled access 신청
- MIG 파티션 결정 (Sprint 1)
- S3 최종 결정 (옵션 비교만)

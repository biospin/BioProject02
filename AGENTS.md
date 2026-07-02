# AGENTS.md — SpatialPathoAgent 협업 규약 v0.2

> 버전: v0.6 | 작성: 2026-05-16 braveji (ykji) | 최종 수정: 2026-06-12

---

## 1. 팀 구성 및 역할

| Username | 이름 | 역할 | SSH 포트 | Workspace 경로 |
|---|---|---|---|---|
| kkkim   | 김가경 | **Project Leader** + Embedding Agent (Data manifest/다운로드 역할 흡수) | 2202 | `/workspace/agents/embedding/` |
| braveji | 지용기 | Orchestrator + **Scientific Critic (총괄)** | 2205 | `/workspace/agents/orchestrator/` |
| jamie   | 류재면 | Data Agent | 2201 | `/workspace/agents/data/` |
| sjpark  | 박세진 | Modeling Agent; Critic 바이오 sub-check 분담 | 2204 | `/workspace/agents/modeling/` |
| jhans   | 서정한 | Therapeutic Evidence Agent | 2206 | `/workspace/agents/therapeutic_evidence/` |
| ~~gglee~~   | ~~이건규~~ | (이탈 2026-06-09) | 2203 | — |

**분담 원칙:** kkkim이 Project Leader 겸임 (2026-06-09 확정). braveji = Orchestrator + Scientific Critic 총괄. gglee 이탈로 5인 체제.

> **서버 안내(현행):** 작업 서버는 `121.126.38.195`(RTX A6000 49GB × 3). 기존 `61.109.239.220`은 사용 불가. 위 SSH 포트는 기존 서버 기준으로, 현행 서버에선 kkkim=2205만 확인됨 — 나머지는 재확인 필요.

---

## 2. 레포지토리 폴더 구조

```
agents/
  data/                    # jamie — TCGA/CPTAC manifest, label, split
  embedding/               # kkkim — WSI tiling, feature extraction
    setup.sh
    configs/tile_config.yaml
    scripts/tile_wsi.py
    scripts/extract_<model>.py
    scripts/extract_dummy.py
  modeling/                # sjpark — MLP/MIL baselines, training configs
    baselines/mlp.py
    configs/baseline_er_status.yaml
  therapeutic_evidence/    # jhans — DepMap/GDSC schema, drug linking
  critic/                  # braveji — checklist, anti-patterns, validation
    checklist_v1.md
    anti_patterns.md
schemas/
  critic_report.schema.json
  hypothesis.schema.json
experiments/<username>/<date>/
  config.yaml
  model.pt
  metrics.json
  predictions.npy
  critic_report.json
guide/
  plan-v1.0.md
  start-project.md
```

**실험 디렉토리 필수 5개 아티팩트 + git commit hash:**
모든 실험 디렉토리에 `config.yaml / model.pt / metrics.json / predictions.npy / critic_report.json` 및 실행 시점 git commit hash를 함께 기록해야 합니다.

---

## 3. 브랜치 및 커밋 규칙

### 브랜치 명명
```
<type>/<BIOP02-이슈번호>-<username>-<짧은설명>
```
예시:
```
feat/BIOP02-27-kkkim-tile-wsi
docs/BIOP02-13-braveji-agents-md
fix/BIOP02-32-sjpark-mlp-baseline
infra/BIOP02-12-braveji-github-setup
```

| prefix | 용도 |
|---|---|
| `feat/` | 새 기능 (코드/스크립트) |
| `docs/` | 문서, schema, checklist |
| `fix/` | 버그 수정 |
| `infra/` | setup.sh, Dockerfile, gpu.lock 등 |

### JIRA Smart Commits
커밋 메시지에 JIRA 이슈 번호 포함 → JIRA 이슈 자동 업데이트:
```bash
git commit -m "BIOP02-27 #in-progress tile_wsi.py 256x256 tiling 구현"
git commit -m "BIOP02-27 #done tile_wsi.py Otsu mask + per-patient cap 5000 완성"
```

---

## 4. Critic Cross-review 규칙

**owner ≠ reviewer — 자기 결과 자기 critic 금지.**

### 기본 페어링 (2026-06-09 갱신 — gglee 이탈, Critic=braveji 총괄)

**Scientific Critic = braveji (총괄).** 7-point/critic_status owns. 바이오 판단(#4/#5)은 sjpark/jhans에 분담. sub-reviewer는 해당 산출물 owner가 아니어야 함(Owner≠Reviewer).

| 작성자 | Critic 담당 |
|---|---|
| sjpark (모델링 결과) | kkkim |
| kkkim (임베딩 결과) | jamie |
| jamie (데이터/split) | braveji |
| jhans (TE 결과) | braveji 총괄 (생물학적 타당성 sub-check: sjpark) |

### Critic 통과 조건
모든 hypothesis 출력은 다음 두 필드가 **필수**:
- `claim_level`: 반드시 `"hypothesis_only"` (예외 시 사유 기재)
- `critic_status`: `"pass"` / `"caution"` / `"reject"`

**결과 공유는 `critic_status: pass` 후에만 가능.**

### Critic 7항목 체크리스트 (매 실험 적용)
1. Data leakage check
2. Baseline comparison (random, subtype-only, pixel-mean)
3. Counterfactual check (핵심 feature 제거 시 ranking 변화)
4. Cross-dataset check (DepMap PRISM vs GDSC 일관성)
5. Biological plausibility (pathway-drug 연결 타당성)
6. DRP framing check (`"drug response prediction"` 표현 금지)
7. Claim-level check (`hypothesis_only` 외 사용 시 사유)

---

## 5. 실험 추적 규칙

### 도구 역할 분담 (2026-06-03 확정)

| 도구 | 역할 | 설정 |
|---|---|---|
| **git** | 아티팩트 버전 관리 — 실험 디렉토리 전체 commit 필수 | 별도 설정 불필요 |
| **wandb** | 학습 중 실시간 loss/metric 시각화 | `WANDB_PROJECT=spatialpathoagent` |
| **MLflow** | 실험 레지스트리 + 모델 비교 UI (셀프호스팅) | `MLFLOW_TRACKING_URI=http://<현행서버>:5000` (서버 이전으로 호스트 재확인 필요; 기존 `61.109.239.220`은 불가) |

- wandb API key는 `~/.netrc` 또는 환경변수 `WANDB_API_KEY`로 관리 — git commit 금지
- MLflow UI: 서버에서 `mlflow server --host 0.0.0.0 --port 5000` 실행 후 접근

### 디렉토리 구조 및 필수 아티팩트

- 실험 디렉토리: `experiments/<username>/<YYYYMMDD_설명>/`
- 5개 아티팩트 모두 저장 후 `git commit`
- `metrics.json` 최소 포함 필드: `auc`, `auprc`, `balanced_accuracy`, `n_train`, `n_val`, `model`, `embedding_model`, `commit_hash`
- `commit_hash`는 학습 스크립트에서 `git rev-parse HEAD`로 자동 기록
- 실험 결과 공유 = Critic pass + Slack `#biop02-experiments` 채널

---

## 6. GPU 사용 규칙 (gpu.lock wrapper 배포 전 잠정)

| 슬롯 | 시간 |
|---|---|
| 슬롯 A | 09:00–13:00 |
| 슬롯 B | 13:00–17:00 |
| 슬롯 C | 17:00–21:00 |
| 슬롯 D | 21:00–01:00 |

- 사용 전 Slack `#biop02-alerts`에 슬롯 예약 메시지 필수
- 장시간 학습 시 타 팀원 슬롯 침범 금지
- embedding 연속 작업: 최대 3 슬롯(12시간) 연속 예약 허용, 24시간 전 사전 공지 필수
- gpu.lock wrapper 배포 후 캘린더 룰 → 자동 관리로 전환

### MIG 파티션 정책 (2026-06-03 확정, BIOP02-51)

**Sprint 1–2 (~ 2026-06-19): MIG 없이 full GPU(80GB) 유지**  
근거: 1 slide UNI v1 embedding = 125.6s. 300장 ≈ 10.5시간. MIG 적용 시 속도 저하로 Sprint 마감에 영향.

**Sprint 3+ (2026-07-03~): 2× 3g.40gb 전환 재검토**  
조건: embedding 완료 후, 동시 GPU 사용 수요가 주 2회 이상 발생할 때.

MIG 전환/해제는 braveji가 서버에서 실행 후 `#biop02-general` 공지.  
상세 분석: `guide/gpu_mig_policy.md` 참조.

---

## 7. 절대 금지 사항

- `❌` HF 토큰 / AWS 키 git commit
- `❌` drug feature (SMILES, fingerprint, learnable embedding) 모델 입력
- `❌` `"patient-specific optimal treatment prediction"` / `"personalized therapy"` 표현
- `❌` ICI / Pembrolizumab cell-line transfer 추천
- `❌` Critic agent 자기 임계값/control 결정 (anti-self-reference)
- `❌` raw WSI 전량 영구 보관 — 스트리밍 다운로드 → 임베딩 추출 후 raw `.svs` 삭제(LRU). 영구 보존은 manifest·coords·embeddings·logs (Paper A = ~1010 DX-slide BRCA cohort, 2026-06-10 확정)
- `❌` Pan-cancer 확장 — Paper B까지 BRCA-only

---

## 8. 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| v0.1 | 2026-05-12 | Kickoff 초안 |
| v0.2 | 2026-05-16 | 1인 1역할 확정, 브랜치 규칙 구체화, cross-review 페어링 초안, GPU 슬롯 룰 추가 |
| v0.3 | 2026-06-03 | 실험 추적 도구 결정 (git+wandb+MLflow), experiments/ 디렉토리 표준 적용 |
| v0.4 | 2026-06-03 | MIG 파티션 정책 확정 (Sprint 1–2: MIG 없음, Sprint 3+: 2×3g.40gb 검토) |
| v0.5 | 2026-06-12 | braveji Orchestrator + Scientific Critic 총괄 겸임으로 변경 |
| v0.6 | 2026-06-12 | kkkim Project Leader 확정, gglee 이탈(2026-06-09) 반영, Paper A scope ~1010, raw WSI 삭제 정책, Critic sub-check 분담 기술 |

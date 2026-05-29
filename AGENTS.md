# AGENTS.md — SpatialPathoAgent 협업 규약 v0.2

> 버전: v0.2 | 작성: 2026-05-16 braveji (ykji) | 승인: gglee sign-off 후 확정

---

## 1. 팀 구성 및 역할

| Username | 이름 | 역할 | SSH 포트 | Workspace 경로 |
|---|---|---|---|---|
| gglee   | 이건규 | Scientific Critic + 리더 | 2203 | `/workspace/agents/critic/` |
| braveji | 지용기 | Orchestrator | 2205 | `/workspace/agents/orchestrator/` |
| jamie   | 류재면 | Data Agent | 2201 | `/workspace/agents/data/` |
| kkkim   | 김가경 | Embedding Agent | 2202 | `/workspace/agents/embedding/` |
| sjpark  | 박세진 | Modeling Agent | 2204 | `/workspace/agents/modeling/` |
| jhans   | 서정한 | Therapeutic Evidence Agent | 2206 | `/workspace/agents/therapeutic_evidence/` |

**분담 원칙:** 1인 1역할. 겸임 없음 (2026-05-15 확정).

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
  critic/                  # gglee — checklist, anti-patterns, validation
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

### 기본 페어링 (Week 10 / 5/22 미팅 최종 확정)

| 작성자 | Critic 담당 |
|---|---|
| sjpark (모델링 결과) | kkkim |
| kkkim (임베딩 결과) | jamie |
| jamie (데이터/split) | braveji |
| jhans (TE 결과) | gglee |

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

- 실험 디렉토리: `experiments/<username>/<YYYYMMDD_설명>/`
- 5개 아티팩트 모두 저장 후 `git commit`
- `metrics.json` 최소 포함 필드: `auc`, `auprc`, `balanced_accuracy`, `n_train`, `n_val`, `model`, `embedding_model`, `commit_hash`
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
- gpu.lock wrapper 배포 후 캘린더 룰 → 자동 관리로 전환

---

## 7. 절대 금지 사항

- `❌` HF 토큰 / AWS 키 git commit
- `❌` drug feature (SMILES, fingerprint, learnable embedding) 모델 입력
- `❌` `"patient-specific optimal treatment prediction"` / `"personalized therapy"` 표현
- `❌` ICI / Pembrolizumab cell-line transfer 추천
- `❌` Critic agent 자기 임계값/control 결정 (anti-self-reference)
- `❌` TCGA WSI 전체 다운로드 (Paper A = ~150장 subset)
- `❌` Pan-cancer 확장 — Paper B까지 BRCA-only

---

## 8. 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| v0.1 | 2026-05-12 | Kickoff 초안 |
| v0.2 | 2026-05-16 | 1인 1역할 확정, 브랜치 규칙 구체화, cross-review 페어링 초안, GPU 슬롯 룰 추가 |

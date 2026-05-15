# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SpatialPathoAgent** (BioProject02) is a multi-agent AI research pipeline predicting molecular phenotypes from H&E whole-slide images (WSI) and generating ranked therapeutic hypotheses.

Goal: H&E WSI → morphology embedding → molecular phenotype prediction → DepMap/GDSC transfer → ranked therapeutic hypothesis + Scientific Critic validation.

**This is NOT a drug response prediction (DRP) model.** No drug structure input, BRCA-only, hypothesis-only output.


## Project 진행사항 공유 
###  Confluence 정보
  - Space key: VC
  - 작업위치 : 프로젝트 진행-AI전용 > 프로젝트#02
### JIRA 정보
  - Space key : BIOP02


## Team & Roles

| Username | github id | atlassian id | slack id  | slack app name for openclaw | SSH Port | Role |
|---|---|---|---|---|---|---|
| jamie (jmryu) | JamieLyu | jamie.orangecounty@gmail.com | jamie.orangecounty@gmail.com | jamie-openclaw-bot |2201 | Data Agent — TCGA/CPTAC manifests, labels, splits |
| kkkim (gkkim) | kakyungkim | kakyung.kim@gmail.com | kakyung.kim@gmail.com | kakyung.kim-openclaw-bot | 2202 | Embedding Agent — WSI tiling, foundation model extraction |
| gglee (gklee) | Geongyu | rjsrb365@gmail.com | rjsrb365@gmail.com | ggyu-claw | 2203 | Scientific Critic + Project Leader |
| sjpark | sezinie000 | sezinie000@gmail.com | sezinie000@gmail.com | sezinie-openclaw-bot | 2204 | Modeling Agent — phenotype prediction (MLP, attention MIL) |
| braveji (ykji) | braveji18 | biospinleader@gmail.com  | biospinleader@gmail.com | yong-openclaw-bot |  2205 | Orchestrator — pipeline coordination, infra, schemas |
| jhans | JeonghanSeo | phoenicx16@gmail.com | phoenicx16@gmail.com |  | 2206 |  Therapeutic Evidence Agent — DepMap/GDSC drug linking |

## Infrastructure

- **Server:** A100 80GB × 1, 24 CPU, 188 GiB RAM, 2 TB root — `61.109.239.220`, SSH key only
- **Data layout:** raw WSI = S3 read-only | `/data/cache/` = LRU 200 GB (processed/tiled) | embeddings = permanent
- **GPU slots:** 09–13 / 13–17 / 17–21 / 21–01 (calendar + Slack reservation until `gpu.lock` wrapper is ready)
- **Workspace:** `/workspace/agents/<role>/` per person

## Repository Structure (target)

```
agents/
  data/           # jmryu — manifests, clinical metadata, split policy
  embedding/      # kkkim — tiling scripts, feature extraction
    setup.sh
    configs/tile_config.yaml   # 256×256 @ 20×, Otsu mask, per-patient cap 5000
    scripts/tile_wsi.py
    scripts/extract_<model>.py
  modeling/       # sjpark — MLP/MIL baselines, training configs
    baselines/mlp.py
    configs/baseline_er_status.yaml
  therapeutic_evidence/   # jhans — DepMap/GDSC schema, drug linking
  critic/         # gglee — checklist, anti-patterns, validation
    checklist_v1.md
    anti_patterns.md
schemas/
  critic_report.schema.json
  hypothesis.schema.json
experiments/<user>/<date>/
  config.yaml  model.pt  metrics.json  predictions.npy  critic_report.json
```

Every experiment directory must include all five artifacts above plus a git commit hash.

## Foundation Models (embedding)

Apply to HuggingFace with institutional email (not `@gmail`/`@naver`). All gated. Apply to 5 simultaneously; use first approved for Sprint 1 pilot.

| Priority | Model | Dim | License |
|---|---|---|---|
| 1 | UNI v1 (`MahmoodLab/UNI`) | 1024 | CC-BY-NC-ND 4.0 |
| 2 | CONCH (`MahmoodLab/CONCH`) | 512 | CC-BY-NC-ND 4.0 |
| 3 | EXAONE Path 2.0 (`LGAI-EXAONE/EXAONE-Path-2.0`) | 768 | EXAONEPath NC |
| 4 | Virchow v1 (`paige-ai/Virchow`) | 1280 | Apache 2.0 |
| 5 | UNI2-h (`MahmoodLab/UNI2-h`) | 1536 | CC-BY-NC-ND 4.0 |

All licenses are academic non-commercial — project is **academic research only, publication-only output**.

Fallback while awaiting approval: `torch.randn(N, 1024)` dummy embeddings to unblock Modeling Agent.

## Key Commands (Sprint 0 skeleton)

```bash
# SSH access
ssh -p <port> <username>@61.109.239.220

# WSI tiling pilot
time python scripts/tile_wsi.py --slide /data/raw/tcga/sample.svs \
    --config configs/tile_config.yaml --out outputs/pilot/coords.npy

# Feature extraction (after HF approval)
time python scripts/extract_uni.py --slide /data/raw/tcga/sample.svs \
    --coords outputs/pilot/coords.npy --out_dir outputs/pilot/

# GPU monitoring
watch -n 1 nvidia-smi

# Dummy embedding (unblocks Modeling Agent)
python scripts/extract_dummy.py  # outputs torch.randn(N, 1024)
```

## Critic Cross-Review Rules

- **Owner ≠ Reviewer.** Never self-review your own results.
- All hypothesis outputs require `claim_level` + `critic_status` fields.
- Results may not be shared without Critic pass.

**7-point Critic checklist:**
1. Data leakage check
2. Baseline comparison (random, subtype-only, pixel-mean)
3. Counterfactual check (ranking change when key features removed)
4. Cross-dataset check (DepMap PRISM vs GDSC consistency)
5. Biological plausibility (pathway-drug link validity)
6. DRP framing check — "drug response prediction" expression prohibited
7. Claim-level check (`hypothesis_only` required; deviation needs justification)

## Absolute Prohibitions

- `❌` Commit HF tokens / AWS keys to git
- `❌` Drug features (SMILES, fingerprints, learnable embeddings) as model input
- `❌` Expressions: "patient-specific optimal treatment prediction", "personalized therapy"
- `❌` Recommending ICI / Pembrolizumab via cell-line transfer
- `❌` Critic agent setting its own thresholds / controls (anti-self-reference)
- `❌` TCGA WSI full download (Paper A scope = ~150 slide subset)
- `❌` Pan-cancer expansion — BRCA-only through Paper B

## Sprint Schedule

| Sprint | Dates | Key Deliverables |
|---|---|---|
| Sprint 0 | 5/12 – 5/22 | Manifest CSV, AGENTS.md v0.2, schemas/, S3 decision, 1-slide pilot, Jira+GitHub |
| Sprint 1 | 5/22 – 6/05 | Full TCGA-BRCA embedding, ER status MLP, 3 trivial baselines, first critic_report.json |
| Sprint 2 | 6/05 – 6/19 | ER + PR + HER2 + PAM50 × {MLP / attention MIL} |
| Sprint 3 | 6/19 – 7/03 | Attention MIL + cross-dataset (TCGA train → CPTAC test) |
| Sprint 5 | 7/17 – 7/31 | Paper A Figures 1–2 draft |
| Sprint 7 | 8/14 – 8/28 | Paper A draft + all 7 Critic items passed |
| Sprint 8 | 8/28 – 9/11 | Paper A submission |

Weekly sync: **every Friday**, 60 min. Leader: gglee. Orchestrator/minutes: braveji.

## Data Sources

- **TCGA-BRCA** — ~150 slides (open access slides + clinical, Paper A scope). Controlled access (somatic mutations) requires dbGaP with PI signature.
- **CPTAC-BRCA** — IDC `gs://` bucket, ~120 paired samples for external validation.
- **DepMap PRISM + GDSC** — cell line × drug sensitivity (Paper B / Therapeutic Evidence).

Labels: ER/PR/HER2 IHC, PAM50, BRCA1/2 mutation, OS/DFS from TCGA-CDR or cBioPortal.

Patient-level splits are locked after `split_policy_v0` is signed off — no changes after lock.

## Workflow: OpenClaw → Slack → Claude Code / Codex

실제 작업 흐름은 아래와 같습니다.

```
JIRA (BIOP02)
  └─ 담당자에게 이슈 할당
        │
        ▼
  OpenClaw bot (담당자별, 자동 모니터링)
  - JIRA BIOP02에서 본인 할당 이슈를 주기적으로 확인
  - 새 할당 / 기한 임박 / 상태 변경 감지 시 Slack으로 알림
        │
        ▼  Slack DM 또는 #biop02-dev 채널 알림
  팀원 (담당자)
  - 알림 내용 확인 후 Claude Code 또는 Codex로 실제 작업 수행
  - 작업 완료 후 git commit (BIOP02-번호 포함) → PR
        │
        ▼
  JIRA Smart Commits 자동 연동 (이슈 상태 업데이트)
```

**역할 구분:**
- **OpenClaw bot** — JIRA 모니터링 + Slack 알림 전용. 코드를 직접 작성하지 않음.
- **Claude Code / Codex** — 팀원이 직접 구동하는 코딩 도구. 실제 구현 담당.

팀원별 OpenClaw bot (Slack app):

| Username | OpenClaw Slack App |
|---|---|
| jamie | jamie-openclaw-bot |
| kkkim | kakyung.kim-openclaw-bot |
| gglee | ggyu-claw |
| sjpark | sezinie-openclaw-bot |
| braveji | yong-openclaw-bot |
| jhans | (미설정 — Sprint 1 전 braveji 생성 예정) |

## Governance

- `v3.1` master plan (goals/principles) takes precedence over `PROJECT_PLAN.md` (operational schedule) on conflicts.
- CLI choice (Claude Code / Codex / OpenCode) is each person's own — output schemas are unified.
- Modeling progression: MLP baseline → attention MIL. No skipping ahead.

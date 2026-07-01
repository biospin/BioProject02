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
| jamie (jmryu) | JamieLyu | jamie.orangecounty@gmail.com | jamie.orangecounty@gmail.com | jamie-openclaw-bot |2203 | Data Agent — TCGA/CPTAC manifests, labels, splits |
| kkkim | kakyungkim | kakyung.kim@gmail.com | kakyung.kim@gmail.com | kakyung.kim-openclaw-bot | 2205 | **Project Leader** + Embedding Agent — WSI tiling, foundation model extraction (Data manifest/다운로드 역할 흡수) |
| ~~gglee (gklee)~~ | Geongyu | rjsrb365@gmail.com | rjsrb365@gmail.com | ggyu-claw | 2202 | (이탈 2026-06-09 — Leader→kkkim, Critic→braveji 재배정) |
| sjpark | sezinie000 | sezinie000@gmail.com | sezinie000@gmail.com | sezinie-openclaw-bot | 2206 | Modeling Agent — phenotype prediction (MLP, attention MIL); Critic 바이오 sub-check 분담 |
| braveji (ykji) | braveji18 | biospinleader@gmail.com  | biospinleader@gmail.com | yong-openclaw-bot |  2201 | Orchestrator + **Scientific Critic (총괄)** — pipeline coordination, infra, schemas; 7-point/critic_status owns, 바이오 sub-check(#4/#5)는 sjpark/jhans에 분담 |
| jhans | JeonghanSeo | phoenicx16@gmail.com | phoenicx16@gmail.com |  | 2204 |  Therapeutic Evidence Agent — DepMap/GDSC drug linking |

## Infrastructure

- **Server:** A100 80GB × 1, 24 CPU, 188 GiB RAM, 2 TB root — `61.109.239.220`, SSH key only
- **Data layout:** raw WSI = S3 read-only | `/data/cache/` = LRU 200 GB (processed/tiled) | embeddings = permanent
- **GPU slots:** 09–13 / 13–17 / 17–21 / 21–01 — reserve in `#biop02-alerts` before use (until `gpu.lock` wrapper is ready)
- **Workspace:** `/workspace/agents/<role>/` per person

### 팀 공유 데이터 경로 규칙 (중요)

각 팀원 SSH 계정은 **별도 Docker 컨테이너**다(브리지망 `172.18.0.x`, hostname=본인 계정명). `/home/<user>/`는 해당 컨테이너 로컬 디스크(`/dev/sdb1`)라 **다른 계정에서는 보이지 않는다**(권한을 열어도 마운트 자체가 없음). `/workspace`(`/dev/sda2`)만 컨테이너 간 공유되는 볼륨이다.

- **공유 대상 데이터(임베딩·manifest·split·label)는 반드시 `/workspace/data/cache/biop02/`에 실파일로 둔다.** 모든 계정에서 읽기 검증된 경로는 `/workspace`뿐이다. (과거엔 공유 볼륨 용량 등으로 활용이 어려워 `/home/<user>/shared` 심링크를 차선으로 썼으나, 이제 `/workspace`가 표준이다.)
- manifest의 `embedding_path`는 **`/workspace/...` 절대경로**로 작성한다(개인 홈 경로 금지).
- 폴더 네이밍: 임베딩 `<model>_<version>/`(예 `uni_v1/`, `conch_v1/`, `exaone_v2/`), manifest `embedding_manifest_<model>.csv`, split `split_policy_v<n>.csv`.
- 새 공유 폴더는 `chmod 2775`(setgid) + `chgrp project` → 하위 파일이 group `project`를 자동 상속. 파일은 `g+r` 유지.
- 영구 공유 = manifest·coords·embeddings·logs·split/label만. raw `.svs`는 각자 스트리밍→추출→삭제(개인 LRU)이므로 컨테이너 로컬에 둬도 무방(팀 공유·영구보관 금지).

**Slack channels:**

| 채널 | 용도 |
|---|---|
| `#biop02-general` | 공지, 전체 공유 |
| `#biop02-dev` | OpenClaw 알림 수신 + 작업 진행 공유 |
| `#biop02-experiments` | 실험 결과 공유 (Critic pass 후만) |
| `#biop02-alerts` | GPU 슬롯 예약, 서버 장애 알림 |

**Atlassian MCP (Claude Code에서 Confluence·JIRA 직접 조작):** `guide/start-project.md` §7 참조. API token은 `~/.claude/settings.json` 또는 개인 shell 환경변수에만 저장 — 절대 git commit 금지.

**Atlassian DNS 오류 대응:** Confluence/JIRA API 호출 중 `curl: (6) Could not resolve host: biospin-ai.atlassian.net`가 발생하면 재시도만 반복하지 말고 아래 우회 절차를 따른다.

```bash
# 1. 로컬 DNS 확인
getent hosts biospin-ai.atlassian.net

# 2. 실패하면 Cloudflare DNS-over-HTTPS로 IP 조회
curl -sS -H "accept: application/dns-json" \
  "https://1.1.1.1/dns-query?name=biospin-ai.atlassian.net&type=A"

# 3. 반환된 IP로 curl --resolve 사용
curl --resolve biospin-ai.atlassian.net:443:<IP> \
  -u "$ATLASSIAN_EMAIL:$ATLASSIAN_TOKEN" \
  ...
```

성공 후에는 응답의 `id`, `type`, `status`, `_links.webui`를 확인한다. 실제 성공 사례: `13.227.180.4`로 `--resolve` 지정 후 Confluence comment 등록 HTTP 200, comment id `34275356`.

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
  critic/         # braveji — checklist, anti-patterns, validation
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

## Key Commands

```bash
# SSH access
ssh -p <port> <username>@61.109.239.220

# Environment setup (embedding agent)
bash agents/embedding/setup.sh   # installs openslide-tools, libvips, pyvips, timm, huggingface_hub

# WSI tiling pilot
time python agents/embedding/scripts/tile_wsi.py --slide /data/raw/tcga/sample.svs \
    --config agents/embedding/configs/tile_config.yaml --out outputs/pilot/coords.npy

# Feature extraction (after HF approval)
time python agents/embedding/scripts/extract_uni.py --slide /data/raw/tcga/sample.svs \
    --coords outputs/pilot/coords.npy --out_dir outputs/pilot/

# GPU monitoring
watch -n 1 nvidia-smi

# Dummy embedding (unblocks Modeling Agent)
python agents/embedding/scripts/extract_dummy.py  # outputs torch.randn(N, 1024)
```

## Git & JIRA Workflow

### Branch Naming

```
<type>/<BIOP02-이슈번호>-<username>-<짧은설명>
```

| prefix | 용도 |
|---|---|
| `feat/` | 새 기능 (코드/스크립트) |
| `docs/` | 문서, schema, checklist |
| `fix/` | 버그 수정 |
| `infra/` | setup.sh, Dockerfile, gpu.lock 등 |

예: `feat/BIOP02-27-kkkim-tile-wsi`

### JIRA Smart Commits

커밋 메시지에 이슈 번호를 포함하면 JIRA 상태가 자동 업데이트됩니다.

```bash
git commit -m "BIOP02-27 #in-progress tile_wsi.py 256×256 tiling 구현"
git commit -m "BIOP02-27 #done tile_wsi.py Otsu mask + per-patient cap 5000 완성"
git commit -m "BIOP02-27 #comment 1 slide pilot: 8.3min, 4821 patches, 19MB"
```

## Experiment Tracking

Every experiment directory `experiments/<username>/<YYYYMMDD_설명>/` must contain:
- `config.yaml`, `model.pt`, `metrics.json`, `predictions.npy`, `critic_report.json`
- git commit hash recorded inside `metrics.json`

`metrics.json` required fields: `auc`, `auprc`, `balanced_accuracy`, `n_train`, `n_val`, `model`, `embedding_model`, `commit_hash`

Experiment results may only be shared in `#biop02-experiments` after `critic_status: pass`.

## Agent Dependency Chain

```
jamie (manifest + split_policy_v0)
  └→ kkkim (어떤 슬라이드 tiling할지 결정)
  └→ sjpark (MLP 학습 시작 조건)

kkkim (임베딩 완료)
  └→ sjpark (dummy → 실제 임베딩 교체)

sjpark (MLP 결과)
  └→ Critic (braveji 총괄, 바이오 sub-check = sjpark/jhans 분담) → critic_report.json

critic_status: pass
  └→ braveji (Orchestrator: 결과 공유 + experiments registry 등록)
```

## Critic Cross-Review Rules

- **Owner ≠ Reviewer.** Never self-review your own results.
- All hypothesis outputs require `claim_level` + `critic_status` fields.
- Results may not be shared without Critic pass.
- **Scientific Critic = braveji (총괄).** braveji가 7-point 체크리스트와 최종 `critic_status`를 owns하되, 바이오 판단(#4 cross-dataset, #5 biological plausibility)을 sjpark/jhans에 분담한다. sub-reviewer는 해당 산출물 owner가 아니어야 한다(Owner≠Reviewer).

**Cross-review pairings (2026-06-09 갱신 — gglee 이탈, Critic=braveji 총괄):**

| 작성자 | Critic 담당 |
|---|---|
| sjpark (모델링 결과) | kkkim |
| kkkim (임베딩 결과) | jamie |
| jamie (데이터/split) | braveji |
| jhans (TE 결과) | braveji 총괄 (생물학적 타당성 sub-check: sjpark) |

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
- `❌` raw WSI 전량 영구 보관 — 스트리밍 다운로드 → 임베딩 추출 후 raw `.svs` 삭제(LRU). 영구 보존은 manifest·coords·embeddings·logs (Paper A scope = manifest 기반 **~1010 DX-slide BRCA cohort**, 2026-06-10 Leader 확정)
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

Weekly sync: **every Friday**, 60 min. Leader: kkkim. Orchestrator/minutes: braveji.

## Data Sources

- **TCGA-BRCA** — **~1010 slides** (manifest 기반 DX-slide BRCA cohort, open access slides + clinical, Paper A scope; NAS 원본 1133장 중 DX+임상 결합 subset, 2026-06-10 Leader 확정). Controlled access (somatic mutations) requires dbGaP with PI signature.
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

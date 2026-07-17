# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SpatialPathoAgent** (BioProject02) is a multi-agent AI research pipeline predicting molecular phenotypes from H&E whole-slide images (WSI) and generating ranked therapeutic hypotheses.

Goal: H&E WSI → morphology embedding → molecular phenotype prediction → DepMap/GDSC transfer → ranked therapeutic hypothesis + Scientific Critic validation.

**This is NOT a drug response prediction (DRP) model.** No drug structure input, hypothesis-only output.

### 현재 스코프 (2026-07-12) — 반드시 먼저 읽는다
프로젝트는 논문 두 갈래로 진행 중이다. "BRCA-only"는 **Paper A/B에만** 적용되며, **Paper C는 의도적으로 5개 암종**을 다룬다 — 아래 "Absolute Prohibitions"의 pan-cancer 항목을 Paper C 작업과 충돌하는 것으로 오해하지 말 것.

- **Paper A/B (SpatialPathoAgent, BRCA-only)** — H&E→분자 표현형→치료 가설. 이 CLAUDE.md 대부분이 이 파이프라인을 기술한다.
- **Paper C (통합 flagship, cross-cancer 결정지도)** — "H&E가 분자검사를 언제 값싸게 대신할 수 있나"의 **사전등록 결정지도**. 유방(anchor) + 폐·대장·위·두경부 **5개 암종**. 이는 열린 pan-cancer 아틀라스 확장이 **아니라** 법칙 검정을 위한 의도된 경계다(`research/paperC-positioning/PAPER_DIRECTION.md`가 "pan-cancer 아틀라스로 안 흩는 경계"로 봉인). 단일 컨텍스트 = **`research/paperC-positioning/PAPER_DIRECTION.md`**, 계획=`FLAGSHIP_PLAN.md`, 사전등록 법칙=`experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md`, 결정지도=`experiments/crosscancer/CROSS_CANCER_DECISION_MAP.md`. Paper C 작업(분석·집필·검수) 전 이 문서들을 읽는다.
- 현재 진행: Sprint 3 종결 → Paper A(cost-of-substitution) + Paper C(cross-cancer). 상태 상세 = `HANDOFF.md`.


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
| kkkim (gkkim) | kakyungkim | kakyung.kim@gmail.com | kakyung.kim@gmail.com | kakyung.kim-openclaw-bot | 2205 | **Project Leader** + Embedding Agent — WSI tiling, foundation model extraction (Data manifest/다운로드 역할 흡수) |
| gglee (gklee) | Geongyu | rjsrb365@gmail.com | rjsrb365@gmail.com | ggyu-claw | 2202 | **재편입 2026-07-07** (일정으로 2026-06-09 이탈 → 재합류). 역할 재배정 별도 협의(현재 Leader=kkkim·Critic=braveji 유지). Atlassian 계정 active·배정 가능(accountId 712020:bff61238-cf1c-4ca7-a971-4411a06ccf42); GitHub org 접근만 확인 필요 |
| sjpark | sezinie000 | sezinie000@gmail.com | sezinie000@gmail.com | sezinie-openclaw-bot | 2206 | Modeling Agent — phenotype prediction (MLP, attention MIL); Critic 바이오 sub-check 분담 |
| braveji (ykji) | braveji18 | biospinleader@gmail.com  | biospinleader@gmail.com | yong-openclaw-bot |  2201 | Orchestrator + **Scientific Critic (총괄)** — pipeline coordination, infra, schemas; 7-point/critic_status owns, 바이오 sub-check(#4/#5)는 sjpark/jhans에 분담 |
| jhans | JeonghanSeo | phoenicx16@gmail.com | phoenicx16@gmail.com |  | 2204 |  Therapeutic Evidence Agent — DepMap/GDSC drug linking |

## Infrastructure

- **Server (현행):** RTX A6000 49GB × 3, 32 vCPU, 503 GiB RAM — `121.126.38.195` (내부망 `192.168.0.85`), SSH key only (컨테이너/overlay 환경).
- **접속(정본, 2026-07-11 — bastion 폐기):** **직접접속** `ssh -p <본인포트> <계정>@121.126.38.195`. 구 방식(bastion `61.109.239.220` 경유 `-J`)은 A100 서버 시절 방식으로 **폐기** — 쓰지 않는다. 정본 = BIOP01 `docs/SHARED-INFRA-GUIDE.md` §1.
- **SSH 포트:** 팀원별 포트는 위 Team & Roles 표 기준 (2026-06-30 현행 서버로 정정: braveji 2201 / jamie 2203 / kkkim 2205 / jhans 2204 / sjpark 2206).
- **Data layout:** raw WSI(NAS/로컬 캐시) → 타일·임베딩 처리. 공용 `/workspace/data/cache/biop02/`, 개인 대용량 `~/data/`(15 TB, LRU). embeddings = permanent.
- **GPU:** A6000 3장(`cuda:0/1/2`). 사용 전 `#biop02-alerts`에 GPU 인덱스 예약(until `gpu.lock` wrapper is ready).
- **스토리지:** `/workspace`·`/data` = SATA SSD 447 GB(공용, ext4) | `~/data` = **HDD 14.6 TB**(개인, ext4, 회전식). raw WSI·임베딩이 HDD에 있어 타일 읽기 I/O가 병목.
- **소프트웨어:** Ubuntu 22.04.4(Docker), NVIDIA 드라이버 535.309.01, CUDA 12.4, torch 2.6.0+cu124. 외부 IP=SSH IP(NAT 없음), 리전=한국(IP 121.126.x).
- **제공처/비용:** **모두의연구소(Modulabs) 제공(추정), 비용 무료.** 조건: **논문 Acknowledgments에 GPU 자원 제공처로 명시.** 계약기간·연장·idle 정책은 미확인(담당자 확인 권장).
- **공동 JupyterLab (협업):** 실시간 동시편집 + 채팅. jupyter는 **kkkim 컨테이너**에서 1개 기동, 팀 전원이 터널로 공유. 각자 본인 계정 접속(kkkim 계정 공유 X). 접속(정본, 2026-07-11 — bastion 폐기, **직접접속**): `ssh -p <본인포트> -L 8899:<kkkim 컨테이너 IP>:8899 <계정>@121.126.38.195` → `http://localhost:8899`(웹 비밀번호는 Slack 공유). **목적지는 `localhost`가 아니라 kkkim 컨테이너 IP**(예 `172.18.0.5`, 기동 로그의 "★ kkkim 컨테이너 IP"; 재시작 시 바뀜) — `localhost`로 쓰면 자기 컨테이너로 해석돼 접속 불가. kkkim 본인만 `-L 8899:localhost:8899` 가능. 공용 작업폴더 `~/collab_workspace`. SSH 세션 종료 시 터널도 끊기므로 사용 중 터미널 유지. 정본 = BIOP01 `docs/SHARED-INFRA-GUIDE.md` §2.
- **GPU env (BIOP02 전용):** **`spatialpatho`** — Python 3.13, torch 2.6.0+cu124(3 devices). 활성화 `conda activate /opt/envs/spatialpatho`(**full-path 권장**; 이름만 쓰면 개인 원본 `~/miniconda3/envs/spatialpatho`가 우선순위상 먼저 잡힘). canonical = `guide/gpu_env_biop02.md`. ⚠️ **BIOP01 velocity env(`velo-*`)와 통합·rename 금지 — BIOP02 전용 격리 env.**
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

HF 게이팅 접근은 **BIOP02-24(2026-05-17)에서 5종 전종 승인 완료** — HF 계정 `irobii`, 기관 이메일 `kkkim@cytogenlab.com`(신규 신청 시에도 기관 이메일; `@gmail`/`@naver` 거부 사례). Prov-GigaPath는 **2026-07-12 추가 승인**(BIOP02-24 댓글). **UNI v1이 헤드라인 임베딩(1024-d)**이고, Virchow2·UNI2-h·Prov-GigaPath는 **SOTA 다중 FM 견고성 검증용**(치환가능성 법칙의 모델 비의존성, Paper C).

| Priority | Model | Dim | License | 접근 |
|---|---|---|---|---|
| 1 | UNI v1 (`MahmoodLab/UNI`) | 1024 | CC-BY-NC-ND 4.0 | ✅ 승인 — **헤드라인 임베딩** |
| 2 | CONCH (`MahmoodLab/CONCH`) | 512 | CC-BY-NC-ND 4.0 | ✅ 승인 |
| 3 | EXAONE Path 2.0 (`LGAI-EXAONE/EXAONE-Path-2.0`) | 768 | EXAONEPath NC | ✅ 공개(신청 불필요) — 단 slide-단위라 현 coords 파이프라인 비호환(블로커) |
| 4 | **Virchow2** (`paige-ai/Virchow2`) | 2560 (CLS+mean-patch; token 1280) | CC-BY-NC-ND 4.0 | ✅ 승인 — **Virchow v1 대체**(2026-05 신청 시 최신판으로), 현 SOTA |
| 5 | UNI2-h (`MahmoodLab/UNI2-h`) | 1536 | CC-BY-NC-ND 4.0 | ✅ 승인 |
| 6 | Prov-GigaPath (`prov-gigapath/prov-gigapath`) | 1536 (tile enc.) | 비상업 학술(모델 페이지 조건) | ✅ 승인(2026-07-12 추가) |

All licenses are academic non-commercial — project is **academic research only, publication-only output**.

임베딩은 UNI로 실제 추출 중(cross-cancer 포함). 모델링 언블록용 더미(`torch.randn(N, 1024)`, `extract_dummy.py`)는 초기 부트스트랩 잔재로, 현재는 실임베딩 사용.

## Key Commands

```bash
# SSH access (직접접속 정본; kkkim 포트=2205. bastion 경유는 폐기)
ssh -p <port> <username>@121.126.38.195

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
- `❌` **발표자료·슬라이드·메모·배정표의 숫자를 합격 기준으로 쓰는 것** (2026-07-17 실사고)
  - **발표자료엔 "관측값"이 실리지 "기준값"이 안 실린다.** 슬라이드 12의 `α 0.88`은 *측정 결과*인데, 하네스 점검 메모가 이를 eval 임계로 옮겨 적었다. **봉인된 사전등록의 실제 기준은 `ρ ≥ 0.50`**(BIOP01 `manuscript/PREREGISTRATION_gse205117.md` L15; 0.88은 비고란 관측치). 0.88을 게이트로 박으면 **데이터를 본 뒤 골대를 옮기는 것** = 그 문서 L26이 금지한 행위.
  - **규칙:** eval 임계·합격 기준의 근거는 **봉인 문서(사전등록)와 실물 코드**뿐이다. 기준을 인용할 땐 **`파일:줄`을 명시**한다. 발표자료를 근거로 쓰지 않는다.
  - **같은 사고의 다른 얼굴:** 배정표의 *"앞으로 할 일"*(지용기님 `ref/compact/reset diff 자동화`)이 몇 줄 아래서 *"이미 있는 씨앗"*으로 승격됐다 — **실물이 없었다.** **계획을 자산으로 쓰지 않는다. 있다고 적혀 있으면 열어서 확인한다.**
- `❌` **도구가 "못 찾겠다"고 한 것을 통과로 처리하는 것** (2026-07-17 실측)
  - `medsci verify-refs`는 **DOI 조회 실패 시 약한 제목 검색으로 내려가 `OK`를 준다** → **엉터리 DOI(`10.9999/fake...`)가 통과**했다. DOI를 안 쓰는 것보다 **가짜 DOI가 더 잘 뚫린다.**
  - **규칙:** DOI 부재 · **DOI 조회 실패** · `actual_authors=0` → **전부 사람/적대적 검증으로 에스컬레이션.** 도구의 `submission_safe`를 믿지 않는다(날조가 있는데도 `True`였다).
- `❌` raw WSI 전량 영구 보관 — 스트리밍 다운로드 → 임베딩 추출 후 raw `.svs` 삭제(LRU). 영구 보존은 manifest·coords·embeddings·logs (Paper A scope = manifest 기반 **~1010 DX-slide BRCA cohort**, 2026-06-10 Leader 확정)
  - ⚠️ **예외 (Leader 결정 2026-07-17, 프로젝트 기간 한정): raw 자동 삭제 중단.** LRU 삭제 때문에 cross-cancer raw 2,588장이 전부 사라져 **재다운로드가 필요해졌다**(다중 FM 견고성 작업이 실제로 이 비용을 치름). 논문이 끝날 때까지는 raw를 **보관**하고, 디스크가 부족하면 **자동 삭제가 아니라 정지+사람 판단**(디스크 가드). 신규 파이프라인은 이 정책을 따른다 — 근거·운용 = `experiments/kkkim/20260717_multifm_robustness/RESUME.md` §3. 프로젝트 종료 시 위 원칙(삭제)으로 복귀.
- `❌` **Paper A/B는 BRCA-only** — Paper A/B에서 다른 암종으로 확장 금지. **단 Paper C는 예외**: 사전등록된 **5개 암종**(유방 anchor + 폐·대장·위·두경부) cross-cancer 결정지도다("현재 스코프" 참조). Paper C가 금지하는 것은 **열린 pan-cancer 아틀라스로의 무경계 확장**(6번째 암종 즉흥 추가 등) — 사전등록 5종 경계를 넘으려면 Leader(kkkim) 승인.

## Sprint Schedule

**현재 위치 (2026-07-12): Sprint 3 종결 → Paper A(cost-of-substitution) + Paper C(cross-cancer) 병행.** 원래 sprint 계획은 단일 Paper A 로드맵이었으나 실제 작업은 Paper C 통합 flagship으로 확장됨(위 "현재 스코프"·`HANDOFF.md`). 아래 표는 원 계획 기준이며, **Sprint 4(7/03–7/17)·Sprint 6(7/31–8/14)는 원 문서에 누락** — 실제 진행 정본은 항상 `HANDOFF.md`를 본다(sprint 표는 큰 그림만).

| Sprint | Dates | Key Deliverables | 상태 |
|---|---|---|---|
| Sprint 0 | 5/12 – 5/22 | Manifest CSV, AGENTS.md v0.2, schemas/, S3 decision, 1-slide pilot, Jira+GitHub | ✅ 완료 |
| Sprint 1 | 5/22 – 6/05 | Full TCGA-BRCA embedding, ER status MLP, 3 trivial baselines, first critic_report.json | ✅ 완료 |
| Sprint 2 | 6/05 – 6/19 | ER + PR + HER2 + PAM50 × {MLP / attention MIL} | ✅ 완료 |
| Sprint 3 | 6/19 – 7/03 | Attention MIL + cross-dataset (TCGA train → CPTAC test) | ✅ 종결 |
| Sprint 4 | 7/03 – 7/17 | *(원 문서 누락 — HANDOFF 참조: Paper A/C 분석 진행 중)* | 🔄 진행 |
| Sprint 5 | 7/17 – 7/31 | Paper A Figures 1–2 draft | ⏳ |
| Sprint 6 | 7/31 – 8/14 | *(원 문서 누락)* | ⏳ |
| Sprint 7 | 8/14 – 8/28 | Paper A draft + all 7 Critic items passed | ⏳ |
| Sprint 8 | 8/28 – 9/11 | Paper A submission | ⏳ |

Weekly sync: **every Friday**, 60 min. Leader: kkkim. Orchestrator/minutes: braveji.

## Data Sources

- **TCGA-BRCA** — **~1010 slides** (manifest 기반 DX-slide BRCA cohort, open access slides + clinical, Paper A scope; NAS 원본 1133장 중 DX+임상 결합 subset, 2026-06-10 Leader 확정). Paper A의 BRCA1/2 gene-level mutation label은 open-access MC3 기반 cBioPortal API로 충분하므로 dbGaP 신청은 하지 않는다(BIOP02-61, 2026-07-16). Raw/unmasked genome-wide somatic data가 새로 필요할 때만 PI 서명을 포함한 controlled-access 신청을 별도 검토한다.
- **CPTAC-BRCA** — IDC `gs://` bucket, ~120 paired samples for external validation.
- **DepMap PRISM + GDSC** — cell line × drug sensitivity (Paper B / Therapeutic Evidence).

Labels: ER/PR/HER2 IHC, PAM50, BRCA1/2 gene-level mutation(open-access MC3/cBioPortal), OS/DFS from TCGA-CDR or cBioPortal.

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

---

## Agent routing & artifact contract (논문 생산 하네스)

> 논문 집필·발표 단계용 재사용 스캐폴드(Designed by Ka-Kyung Kim, CC BY 4.0) 설치본. 전체 랩 지도·멤버 JD = **`docs/HARNESS.md`**. 도메인 분석 슬롯 = **`spatialpatho-analyst`**(기존 `agents/<role>/` 파이프라인 대표). 브랜치에 project-scope 설치.
> ⚠️ 이건 **논문 *생산* 레이어**로, 기존 **분석 파이프라인**(`agents/data|embedding|modeling|therapeutic_evidence|critic/`)을 대체하지 않고 그 위에 얹힌다. BioProject02는 분석 진행 단계 → 집필-단계 산출물(FINDINGS/manuscript/figures) 미존재, 관련 FILL은 팀 확정 대기. **headline 숫자·주장은 지어내지 않는다(가정 금지).**

### 자연어 라우팅
요청에 agent 이름이 없어도 배정. 프로젝트 agent는 `.claude/agents/`. 여러 단계를 엮는 요청("풀 파이프라인 / 프리프린트 업데이트해 제출 준비 / 분석→집필→그림→검수 / 그림만 다시 / 리뷰만 / critic 지적 반영")은 **`paper-production-orchestrator`** Skill(메인 루프 실행).

| 요청 (자연어) | 첫 agent |
| --- | --- |
| "분석 돌려줘 / 재실행 / eval·통계 / 임베딩·모델 성능 / 오류 분석" | `spatialpatho-analyst` |
| "프리프린트/저널/블로그 초안·섹션 써줘" | `manuscript-writer` |
| "그림 만들어줘 / 그림 번호 정리" | `manuscript-writer` (runs figure script) |
| "선행연구 / related work / 스쿱 확인" | `literature-scout` |
| "차별화 각도 / 뭘 새로 해야 하나" | `novelty-strategist` |
| "가설·실험설계·분석계획 점검·감사" | `research-methodologist` |
| "제출 전 적대적 자체검토 / 그림 QA" | `paper-critic` (+ `agents/critic/` 체크리스트 병행) |
| "정식 venue 리뷰 시뮬레이션" | `reviewer` (전역, 선택) |
| "발표자료/슬라이드/발제" | `presenter` |
| "로고·아이콘·브랜드·그림 미감" | `design` |
| "여러 단계를 어떤 순서로 엮을지 계획만" | `paper-orchestrator` (계획만; 실행은 메인 루프) |

### 산출물 계약
| 단계 | Writer | 산출물 | 다음이 읽음 |
| --- | --- | --- | --- |
| 분석·eval | `spatialpatho-analyst` | `<FILL: eval outputs>` + `<FILL: consolidated results summary (미존재)>` | 집필·검수 |
| 집필+그림 | manuscript-writer | `<FILL: manuscript (미존재)>`, `<FILL: figures dir>` | 검수·리뷰·발표 |
| 검증 게이트 | (커밋/공개 전) | `<FILL: headline AUC/AUPRC 재계산 → summary 대조>` | 사람 |
| 리뷰 | paper-critic / reviewer | `<FILL: peer review note path>` | 집필(수정) |
| 발표 | presenter | 슬라이드/발제 | 사람 |
| 상태 핸드오프 | (전원) | `HANDOFF.md`, `TODO.md`, `SESSION_LOG.md` | 다음 세션 |

**사람 승인 게이트:** 공개는 **저자·소속·저자순서·corresponding email·IP·GPU 제공처(Modulabs) 확정** 전까지 보류; 커밋/푸시는 사람이 한다; **팀 프로젝트라 저자-대면 내용은 팀 합의 필요.**

---

## 에이전트 발행 · 프롬프트 규칙 (구 CLAUDE.local.md에서 이관)

에이전트가 Bash를 못 쓰는 것처럼 보이는 건 대개 **권한이 아니라 프롬프트 문제**다. 서브에이전트 발행 시:
- 프롬프트 첫 줄에 명시: `슬래시 커맨드나 스킬(/xxx)을 쓰지 말고, Bash로 Python 코드를 직접 실행하라.`
- 실행할 코드를 프롬프트에 **copy-paste 가능한 형태로 직접 포함**한다(추상 지시 금지).
- **python/env 경로를 명시**한다. GPU·임베딩·MIL 작업은 `conda run -p /opt/envs/spatialpatho python ...`(또는 활성화 후 실행). 순수 스크립트는 base `python3`도 되지만 torch/openslide는 spatialpatho env 필요.
- 에러 발생 시 수정 후 재시도하도록 명시.
- 피할 표현: "스캔해서 설정 파일 업데이트"(→ `fewer-permission-prompts` 스킬 트리거), "설정을 등록"(→ `update-config` 트리거). 구체적 코드·명령으로 대체.

**Critic Agent 발행 전 필수 확인**(하나라도 미충족이면 발행 금지):
1. 리뷰 대상의 upstream 의존성이 **모두 완료**됐는가.
2. dummy/smoke test가 아닌 **실제 데이터 기반** 결과물인가.
3. 결과 파일(`metrics.json` 등)이 실제로 존재하고 **수치가 채워져** 있는가.

---

## 완료의 정의 (Definition of Done) — 공유/커밋 전 체크리스트

**"done"은 코드를 다 짰을 때가 아니라 end-to-end로 검증했을 때만이다.** 결과를 `#biop02-experiments`에 공유하거나 커밋하기 전에 아래를 통과한다:

1. **experiment 아티팩트 완비.** `experiments/<user>/<YYYYMMDD_설명>/`에 5종(`config.yaml`·`model.pt`·`metrics.json`·`predictions.npy`·`critic_report.json`) + `metrics.json` 내부에 `commit_hash`. `metrics.json` 필수필드(`auc`·`auprc`·`balanced_accuracy`·`n_train`·`n_val`·`model`·`embedding_model`·`commit_hash`) 채움.
2. **Critic 통과.** `critic_status: pass`(7-point 체크리스트). Owner≠Reviewer. **pass 전에는 `#biop02-experiments` 공유 금지.**
3. **검증 게이트(헤드라인 숫자).** 공개 전 헤드라인 AUC/AUPRC를 **다시 계산**해 결과 요약과 대조 일치. 캐시·이전 세션 출력을 그대로 믿지 않는다.
4. **claim 규율.** 모든 가설 산출물에 `claim_level`(+`hypothesis_only`)·`critic_status` 필드. DRP 프레이밍 표현 금지(7-point #6). Paper C headline claim은 사전등록 법칙·held-out 검정 전까지 provisional — 본문 승격 금지.
5. **registry 등재.** 완료 experiment는 `experiments/registry/`에 등록.
6. **숫자·저자·경로를 지어내지 않았는가.** 근거 없는 헤드라인 수치·저자 정보 금지 — `<FILL>`로 남기고 팀/kkkim 확인.
7. **상태 기록 + 정직 보고.** 그 턴에 `HANDOFF.md`·`TODO.md`·`SESSION_LOG.md` 갱신. 검증한 것/미검증인 것 명시, 실패는 출력과 함께 그대로 보고.

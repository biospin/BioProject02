# BioProject02 — SpatialPathoAgent

H&E 전체 슬라이드 이미지(WSI)에서 분자 표현형을 예측하고 치료 가설을 순위화하는 멀티에이전트 AI 연구 파이프라인.

**목표:** H&E WSI → 형태학적 임베딩 → 분자 표현형 예측 → DepMap/GDSC 전이 → 순위화된 치료 가설 + Scientific Critic 검증

> **이 프로젝트는 약물 반응 예측(DRP) 모델이 아닙니다.** 약물 구조 입력 없음, BRCA 단일 암종, 가설 출력 전용. 학술 연구 목적 — 논문 출판 전용.

---

## 팀 구성 및 역할

| 사용자명 | GitHub | 역할 | SSH 포트 |
|---|---|---|---|
| jamie (jmryu) | [JamieLyu](https://github.com/JamieLyu) | Data Agent — TCGA/CPTAC 매니페스트, 레이블, 분할 | 2201 |
| kkkim | [kakyungkim](https://github.com/kakyungkim) | Embedding Agent — WSI 타일링, 파운데이션 모델 특징 추출 | 2202 |
| gglee | [Geongyu](https://github.com/Geongyu) | Scientific Critic + 프로젝트 리더 | 2203 |
| sjpark | [sezinie000](https://github.com/sezinie000) | Modeling Agent — 표현형 예측 (MLP, attention MIL) | 2204 |
| braveji (ykji) | [braveji18](https://github.com/braveji18) | Orchestrator — 파이프라인 조율, 인프라, 스키마 | 2205 |
| jhans | [JeonghanSeo](https://github.com/JeonghanSeo) | Therapeutic Evidence Agent — DepMap/GDSC 약물 연결 | 2206 |

주간 동기화: **매주 금요일** 60분. 리더: gglee. 오케스트레이터/회의록: braveji.

---

## 인프라

- **서버(현행):** RTX A6000 49GB × 3, 32 vCPU, RAM 503 GiB — `121.126.38.195` (내부망 `192.168.0.85`), SSH 키 전용 (컨테이너 환경). (kkkim 포트=2205, 나머지 재확인 필요)
- **Bastion(점프 호스트):** `61.109.239.220` (구 A100 서버 주소) — 본서버 접속 경유지
- **데이터 레이아웃:** 원본 WSI(NAS/로컬 캐시) → 타일·임베딩 처리 | 공용 `/workspace/data/cache/biop02/`, 개인 대용량 `~/data/`(15 TB, LRU) | 임베딩 = 영구 보존
- **GPU:** A6000 3장(`cuda:0/1/2`) — 사용 전 Slack `#biop02-alerts`에 GPU 인덱스 예약
- **제공처:** 모두의연구소(Modulabs) 제공(추정), 비용 무료. **논문 Acknowledgments에 GPU 자원 제공처 명시 필요.**
- **공동 JupyterLab (협업):** 실시간 동시편집 + 채팅 — `ssh -L 8899:localhost:8899 -J bastion@61.109.239.220 -p <포트> <사용자명>@192.168.0.85` → `http://localhost:8899` (비밀번호 Slack 공유). 공용 작업폴더 `/home/kkkim/collab_workspace`
- **작업 공간:** `/workspace/agents/<role>/` (팀원별)

```bash
# 본서버 접속 (bastion 경유)
ssh -J bastion@61.109.239.220 -p <포트> <사용자명>@192.168.0.85
```

---

## 저장소 구조

```
agents/
  data/                    # jamie — 매니페스트, 임상 메타데이터, 분할 정책
  embedding/               # kkkim — 타일링 스크립트, 특징 추출
    setup.sh
    configs/tile_config.yaml
    scripts/tile_wsi.py
    scripts/extract_<model>.py
  modeling/                # sjpark — MLP/MIL 베이스라인, 학습 설정
    baselines/mlp.py
    configs/baseline_er_status.yaml
  therapeutic_evidence/    # jhans — DepMap/GDSC 스키마, 약물 연결
  critic/                  # gglee — 체크리스트, 안티패턴, 검증
    checklist_v1.md
    anti_patterns.md
schemas/
  critic_report.schema.json
  hypothesis.schema.json
experiments/<user>/<date>/
  config.yaml  model.pt  metrics.json  predictions.npy  critic_report.json
```

모든 실험 디렉토리에는 위 5개 아티팩트와 git 커밋 해시가 포함되어야 합니다.

---

## 시작하기

Git 클론, 브랜치 명명 규칙, JIRA Smart Commits 커밋 형식은 [guide/start-project.md](guide/start-project.md) §1~3, §5 참조.

### 주요 스크립트

```bash
# WSI 타일링 파일럿
time python scripts/tile_wsi.py --slide /data/raw/tcga/sample.svs \
    --config configs/tile_config.yaml --out outputs/pilot/coords.npy

# 특징 추출 (HuggingFace 승인 후)
time python scripts/extract_uni.py --slide /data/raw/tcga/sample.svs \
    --coords outputs/pilot/coords.npy --out_dir outputs/pilot/

# 더미 임베딩 (HF 승인 대기 중 Modeling Agent 언블록용)
python scripts/extract_dummy.py  # torch.randn(N, 1024) 출력

# GPU 모니터링
watch -n 1 nvidia-smi
```

---

## 파운데이션 모델

HuggingFace에 기관 이메일로 신청 (`@gmail`/`@naver` 불가). 모두 게이트 모델 — 5종 동시 신청 후 가장 먼저 승인된 모델로 파일럿 진행.

| 우선순위 | 모델 | HF ID | 차원 | 라이선스 |
|---|---|---|---|---|
| 1 | UNI v1 | `MahmoodLab/UNI` | 1024 | CC-BY-NC-ND 4.0 |
| 2 | CONCH | `MahmoodLab/CONCH` | 512 | CC-BY-NC-ND 4.0 |
| 3 | EXAONE Path 2.0 | `LGAI-EXAONE/EXAONE-Path-2.0` | 768 | EXAONEPath NC |
| 4 | Virchow v1 | `paige-ai/Virchow` | 1280 | Apache 2.0 |
| 5 | UNI2-h | `MahmoodLab/UNI2-h` | 1536 | CC-BY-NC-ND 4.0 |

---

## 데이터 소스

- **TCGA-BRCA** — 약 150장 슬라이드 (공개 접근). 체세포 변이 데이터는 dbGaP + PI 서명 필요.
- **CPTAC-BRCA** — IDC `gs://` 버킷, 약 120 쌍 샘플 (외부 검증용).
- **DepMap PRISM + GDSC** — 세포주 × 약물 감수성 (Paper B).

레이블: ER/PR/HER2 IHC, PAM50, BRCA1/2 변이, TCGA-CDR 또는 cBioPortal의 OS/DFS.

---

## 스프린트 일정

| 스프린트 | 기간 | 주요 산출물 |
|---|---|---|
| Sprint 0 | 5/12 – 5/22 | Manifest CSV, AGENTS.md v0.2, schemas/, S3 결정, 1슬라이드 파일럿, Jira+GitHub |
| Sprint 1 | 5/22 – 6/05 | TCGA-BRCA 전체 임베딩, ER status MLP, 3종 기본 베이스라인, 첫 critic_report.json |
| Sprint 2 | 6/05 – 6/19 | ER + PR + HER2 + PAM50 × {MLP / attention MIL} |
| Sprint 3 | 6/19 – 7/03 | Attention MIL + 교차 데이터셋 (TCGA 학습 → CPTAC 테스트) |
| Sprint 5 | 7/17 – 7/31 | Paper A Figure 1–2 초안 |
| Sprint 7 | 8/14 – 8/28 | Paper A 초안 + Critic 7개 항목 전부 통과 |
| Sprint 8 | 8/28 – 9/11 | Paper A 제출 |

---

## Critic 교차 검토 규칙

- **작성자 ≠ 검토자.** 자기 결과를 직접 검토하지 않습니다.
- 모든 가설 출력에 `claim_level` + `critic_status` 필드 필수.
- Critic 통과 없이 결과 공유 불가.

7점 체크리스트: 데이터 누수 · 베이스라인 비교 · 반사실 검증 · 교차 데이터셋 · 생물학적 타당성 · DRP 표현 · 주장 수준 확인.

---

## 작업 흐름

```
JIRA (BIOP02) → OpenClaw bot → Slack DM → Claude Code / Codex → git commit → PR → JIRA Smart Commits
```

Confluence: Space key `VC` · 작업 위치: 프로젝트 진행-AI전용 > 프로젝트#02

OpenClaw 설정, Confluence/JIRA 연동, Atlassian MCP 설정은 [guide/start-project.md](guide/start-project.md) §5~8 참조.

---

## 절대 금지 사항

- `❌` HF 토큰 / AWS 키 git 커밋
- `❌` 약물 피처(SMILES, 핑거프린트, 학습 가능한 임베딩)를 모델 입력으로 사용
- `❌` "환자 맞춤 최적 치료 예측", "개인화 치료" 표현
- `❌` 세포주 전이로 ICI / Pembrolizumab 추천
- `❌` TCGA WSI 전체 다운로드 (Paper A = 약 150장 서브셋만)
- `❌` 범암종 확장 — Paper B까지 BRCA 단일 유지

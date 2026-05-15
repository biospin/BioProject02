# SpatialPathoAgent — 담당자 업무 분담 계획 (v1.0)

> 기준일: 2026-05-16 | 현재 위치: Sprint 0 (5/12–5/22) 진행 중  
> 작성: braveji (ykji). 선행 정본: `PROJECT_PLAN.md` (v0.2), `CLAUDE.md`, `0515_kkkim_onboarding_action_plan.md`

---

## 역할 한 줄 요약

| 담당자 | Username | 역할 | 핵심 산출물 |
|---|---|---|---|
| 이건규 | gglee | Scientific Critic + 리더 | critic checklist, critic_report, 회의 진행, 최종 sign-off |
| 지용기 | braveji (ykji) | Orchestrator | 인프라 셋업, AGENTS.md, 스키마 관리, 회의록 |
| 류재면 | jamie (jmryu) | Data Agent | manifest CSV, 레이블, patient-split |
| 김가경 | kkkim (gkkim) | Embedding Agent | WSI tiling, foundation model 특징 추출 |
| 박세진 | sjpark | Modeling Agent | MLP baseline → attention MIL |
| 서정한 | jhans | Therapeutic Evidence Agent | DepMap/GDSC 약물 연결 (Paper B) |

**분담 원칙:** 결정은 gglee, 실행 인프라는 ykji. 1인 1역할 — 겸임 없음 (5/15 미팅 확정).

---

## Sprint 0 — 인프라 + Governance (5/12–5/22) ← 현재

### braveji (ykji) — Orchestrator

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| Jira workspace + BIOP02 프로젝트 생성 | 5/17 | Scrum 보드 작동, 팀원 6명 초대 |
| Confluence 공간 + 페이지 트리 초안 | 5/17 | `VC` space, 프로젝트#02 페이지 생성 |
| GitHub org + private mono-repo + main 브랜치 보호 | 5/18 | CODEOWNERS, PR template push 완료 |
| AGENTS.md v0.2 작성 | 5/20 | 폴더 규약 + cross-review 룰 포함 |
| S3 / NAS / MinIO 비교안 1쪽 | 5/20 | 5/22 미팅 전 Slack 공유 |
| 5/22 미팅 안건지 1쪽 준비 | 5/21 | Sprint 0 closeout 안건 정리 |
| 회의록 작성 + Confluence 업로드 | 5/22 당일 | Slack 공유 포함 |

### gglee — Scientific Critic + 리더

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| Critic checklist v1 (`agents/critic/checklist_v1.md`) | 5/19 | 7항목 상세 기술 |
| `schemas/critic_report.schema.json` v0.1 | 5/19 | JSON Schema 형식 |
| Embedding tiling 환경 셋업 확인 | 5/19 | openslide/pyvips/timm 설치 확인 |
| kkkim의 `hypothesis.schema.json` draft 검토 | 5/21 | 의견 Slack 전달 |

### jamie (jmryu) — Data Agent

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| TCGA-BRCA manifest CSV v0.1 | 5/19 | GDC manifest 다운로드 + 레이블 후보 표 (ER/PR/HER2/PAM50) |
| CPTAC-BRCA 메모 1쪽 | 5/19 | IDC gs:// 버킷 접근 방법 확인 |
| kkkim에게 TCGA 샘플 WSI 1장 경로 공유 | 5/19 | `/data/raw/tcga/sample.svs` 접근 가능 확인 |

### kkkim (gkkim) — Embedding Agent

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| HF UNI/CONCH/EXAONE/Virchow/UNI2-h 5종 동시 신청 | 즉시 | 신청 완료 확인 메시지 스크린샷 |
| SSH 접속 + `/workspace/agents/embedding/` 폴더 생성 | 5/17 | `nvidia-smi`, `df -h` 정상 확인 |
| 환경 셋업 (`setup.sh`) | 5/18 | openslide, libvips, timm, huggingface_hub 설치 |
| `configs/tile_config.yaml` + `scripts/tile_wsi.py` 작성 | 5/19 | 256×256 @ 20×, Otsu mask, cap 5000 |
| `scripts/extract_dummy.py` 작성 | 5/19 | `torch.randn(N, 1024)` 출력 → sjpark unblock |
| `schemas/hypothesis.schema.json` v0.1 | 5/21 | gglee draft 받은 후 작성 |
| HF 승인 즉시: 1 slide pilot + wall-clock 측정 | 5/21 (조건부) | `outputs/pilot/PILOT_REPORT.md` |

### sjpark — Modeling Agent

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| `/workspace/agents/modeling/` 셋업 | 5/17 | 폴더 + conda/pip 환경 생성 |
| dummy embedding 기반 MLP 스켈레톤 | 5/18 | `torch.randn(N, 1024)` 입력으로 1회 학습 성공 |
| 3 trivial baseline 스켈레톤 | 5/20 | random / subtype-only / pixel-mean 구조 |
| `eval_metrics.md` 1쪽 | 5/20 | AUC, AUPRC, balanced accuracy 정의 |

### jhans — Therapeutic Evidence Agent

| 태스크 | 기한 | 완료 기준 |
|---|---|---|
| SSH 접속 + `/workspace/agents/therapeutic_evidence/` 생성 | 5/19 | 접속 확인 |
| DepMap PRISM + GDSC 데이터 소스 조사 1쪽 | 5/21 | 다운로드 경로 + 칼럼 구조 파악 |

### Sprint 0 합격선 (5/22 미충족 시 Sprint 1 시작 불가)

- **ykji**: Jira + Confluence + GitHub **작동** + AGENTS.md v0.2
- **gglee**: Critic checklist v1 + `critic_report.schema.json` v0.1
- **jamie**: manifest CSV v0.1 + label 후보 표
- **kkkim**: HF 5종 신청 완료 + 환경 셋업 (pilot은 가중치 승인 시)

---

## Sprint 1 — Embedding Pipeline + 첫 Phenotype (5/22–6/05)

| 담당자 | 태스크 | 완료 기준 |
|---|---|---|
| **kkkim** | TCGA-BRCA ~150 slides 전체 tiling | coords.npy 전체 생성 완료 |
| **kkkim** | UNI/CONCH 특징 추출 → `/data/cache/` 저장 | HF 승인 즉시 시작. 임베딩 `.npy` 저장 |
| **sjpark** | ER status binary MLP 학습 | kkkim 임베딩 받는 즉시 시작. AUC 수치 |
| **sjpark** | 3 trivial baseline 비교 완료 | random / subtype-only / pixel-mean vs MLP 표 |
| **jamie** | patient-level split `split_policy_v0` | 5명 OK 서명 후 lock — 이후 변경 금지 |
| **gglee** | 첫 `critic_report.json` | ER status MLP 결과 대상 7항목 체크 완료 |
| **ykji** | 실험 추적 도구 결정 | wandb / MLflow / DVC / git 중 선택 + AGENTS.md 반영 |
| **ykji** | `experiments/` 디렉토리 표준 적용 | config.yaml / model.pt / metrics.json / predictions.npy / critic_report.json + commit hash |
| **jhans** | DepMap PRISM + GDSC 스키마 초안 | `agents/therapeutic_evidence/` 에 칼럼 정의 문서 |

**Sprint 1 종료 기준 (6/05):** `critic_report.json` 1건 + ER status AUC 베이스라인 비교 수치 공유

---

## Sprint 2 — Multi-endpoint Phenotype (6/05–6/19)

| 담당자 | 태스크 |
|---|---|
| **sjpark** | ER / PR / HER2 / PAM50 × MLP 4종 학습 |
| **sjpark** | Attention MIL 구조 선택 (DSMIL / TransMIL / CLAM) → gglee sign-off |
| **kkkim** | 임베딩 추가 모델 실험 지원 (CONCH 또는 EXAONE Path 비교) |
| **jamie** | HER2/PAM50 레이블 추출 + QC |
| **gglee** | ER/PR/HER2/PAM50 MLP 결과 각 Critic 7항목 체크 |
| **ykji** | MIG 파티션 재검토 (Sprint 1 wall-clock 측정 결과 기반) |
| **jhans** | DepMap PRISM vs GDSC consistency 검증 방법 문서화 |

---

## Sprint 3 — Attention MIL + Cross-dataset (6/19–7/03)

| 담당자 | 태스크 |
|---|---|
| **sjpark** | Attention MIL 학습 (TCGA train → CPTAC test) |
| **kkkim** | CPTAC-BRCA 임베딩 추출 (IDC gs:// 버킷) |
| **jamie** | CPTAC 임상 메타데이터 매핑 + split 검증 |
| **gglee** | Counterfactual check + Cross-dataset check (Critic 3·4번 항목) |
| **ykji** | 교차검증 실험 registry 관리 |

---

## Sprint 4 — TIL/Immune Phenotype + Endocrine Rule (7/03–7/17)

| 담당자 | 태스크 |
|---|---|
| **sjpark** | Immune phenotype score 모델 |
| **gglee** | Biological plausibility check (Critic 5번: pathway-drug 연결) |
| **jhans** | Endocrine rule sample (DepMap transfer 초안) |
| **ykji** | dbGaP controlled access 신청 상태 확인 + PI 서명 조율 |

---

## Sprint 5–6 — Paper A Figure 초안 (7/17–8/14)

| 담당자 | 태스크 |
|---|---|
| **gglee** | Fig 1: Pipeline figure (H&E → embedding → phenotype) 초안 |
| **kkkim** | Fig 2: Embedding UMAP sanity (subtype/quality 색상) |
| **sjpark** | Fig 3: Phenotype prediction baseline 비교 |
| **jamie** | Fig 4: External validation (TCGA train → CPTAC test) 수치 정리 |
| **ykji** | Figure 버전 관리 + Confluence 업로드 |
| **jhans** | Anti-shortcut sanity 검증 지원 |

---

## Sprint 7–8 — Paper A 초안 + 제출 (8/14–9/11)

| 담당자 | 태스크 |
|---|---|
| **gglee** | Critic 7항목 전부 pass 확인 + Methods/Results 리뷰 |
| **sjpark** | Methods 섹션 (모델 구조, 학습 설정) |
| **kkkim** | Methods 섹션 (tiling, 임베딩 파이프라인) |
| **jamie** | Methods 섹션 (데이터 출처, split 정책) |
| **ykji** | Supplementary 관리 + 제출 플랫폼 준비 |
| **jhans** | Paper B 기획 착수 (DepMap/GDSC therapeutic evidence 상세 설계) |

---

## Cross-review 페어링

```
작성자              Critic 담당
sjpark (모델링)  →  gglee
kkkim (임베딩)   →  jamie 또는 sjpark
jamie (데이터)   →  ykji 또는 gglee
jhans (TE)      →  gglee
```

> 5/22 미팅에서 페어링 확정 필요. owner ≠ reviewer 원칙 — 자기 결과 자기 critic 금지.

---

## 주요 의존 관계

```
jamie (manifest + split)
    └→ sjpark (MLP 학습 시작 조건)
    └→ kkkim (어떤 슬라이드 tiling할지 결정)

kkkim (임베딩 완료)
    └→ sjpark (dummy → 실제 임베딩으로 교체)

sjpark (MLP 결과)
    └→ gglee (critic_report.json 작성 시작)

gglee (critic_report pass)
    └→ ykji (결과 공유 + registry 등록)
```

---

## Risk 요약

| Risk | 대응 |
|---|---|
| HF 승인 5/22 전 미도착 | dummy embedding(`torch.randn`)으로 sjpark MLP 흐름 unblock, pilot 5/22 발표 보류 |
| GPU 충돌 (5명 1대) | 잠정 캘린더 슬롯 룰 (09–13 / 13–17 / 17–21 / 21–01) → Sprint 0 끝나면 gpu.lock wrapper |
| 2 TB 디스크 부족 | raw = S3 only, `/data/cache/` LRU 200 GB, embedding만 영구 보존 |
| dbGaP controlled access 지연 | open access slides + clinical만으로 v0 진행, Paper A scope에서 controlled 제외 |
| split_policy_v0 lock 지연 | jamie가 5/29 이전 lock — 이후 변경 금지 (실험 재현성 보호) |

---

## 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| v1.0 | 2026-05-16 | 최초 작성. PROJECT_PLAN.md v0.2 + kkkim onboarding plan 통합. 담당자별 Sprint 0–8 태스크 분해. |

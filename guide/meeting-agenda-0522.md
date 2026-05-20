# Sprint 0 Closeout 미팅 안건지

> **일시:** 2026-05-22 (금) | **진행:** gglee | **서기:** braveji (ykji)  
> **준비:** braveji (BIOP02-15) | 참고: `guide/plan-v1.0.md`, `AGENTS.md v0.2`, `guide/storage-comparison.md`

---

## Sprint 0 합격선 사전 점검

> 미팅 전 각자 Slack `#biop02-dev`에 ✅ / ❌ 표명 (5/22 09:00 전)

| 담당자 | 산출물 | 기한 | 상태 |
|---|---|---|---|
| **braveji** | Jira + Confluence + GitHub 작동 | 5/22 | ✅ 완료 |
| **braveji** | AGENTS.md v0.2 | 5/20 | ✅ 완료 |
| **braveji** | S3/NAS/MinIO 비교안 1쪽 (`guide/storage-comparison.md`) | 5/20 | ✅ 완료 |
| **gglee** | Critic checklist v1 (`agents/critic/checklist_v1.md`) | 5/19 | ❓ 확인 |
| **gglee** | `schemas/critic_report.schema.json` v0.1 | 5/19 | ❓ 확인 |
| **jamie** | TCGA-BRCA manifest CSV v0.1 + 레이블 후보 표 | 5/19 | ❓ 확인 |
| **kkkim** | HF 5종 신청 완료 + 환경 셋업 (`setup.sh`) | 5/21 | ✅ 완료 |
| **kkkim** | `scripts/tile_wsi.py` + `extract_dummy.py` | 5/21 | ✅ 완료 |
| **sjpark** | dummy embedding 기반 MLP 스켈레톤 | 5/18 | ❓ 확인 |

---

## 안건 (총 60분)

### Slot 1 — Sprint 0 Walk-through (25분, 5명 × 5분)

각자 5분, 산출물 스크린 공유 또는 터미널 데모. 발표 순서: jamie → kkkim → sjpark → gglee → braveji

| 발표자 | 보여줄 것 |
|---|---|
| **jamie** | manifest CSV 행 수 · 레이블 후보 표 (ER/PR/HER2/PAM50) · CPTAC 접근 메모 |
| **kkkim** | `setup.sh` 실행 결과 · `tile_wsi.py` 1-slide pilot coords.npy (또는 실행 명령) · `extract_dummy.py` output shape |
| **sjpark** | dummy MLP 1회 학습 성공 로그 · 3 trivial baseline 스켈레톤 · `eval_metrics.md` |
| **gglee** | `checklist_v1.md` 7항목 · `critic_report.schema.json` 필드 설명 |
| **braveji** | Jira 보드 · Confluence 페이지 트리 · GitHub main 브랜치 보호 · AGENTS.md v0.2 diff · NCP storage-comparison 요약 |

> **룰:** "아직 못 함"은 1줄로 — 디테일은 회의 후 1:1.

---

### Slot 2 — 결정 안건 (30분, 안건당 5분 컷)

#### 안건 2-1. 스토리지 최종 결정 (5분)
- **보고:** braveji — `guide/storage-comparison.md` v0.2 요약
- **결정할 것:** 3-tier 권장안 lock

```
Raw WSI     → NCP biospin 버킷 (read-only, rclone pull)
Tile cache  → /data/cache/  (LRU 200 GB)
Embedding   → /data/embeddings/ (영구 보존)
MinIO       → Sprint 1 결과 후 재검토 (현재 보류)
```

- **표명 필요:** 전원 ☐ OK / ☐ 이의

#### 안건 2-2. AGENTS.md v0.2 sign-off (5분)
- **보고:** braveji — 주요 변경점: 1인 1역할 · 브랜치 규칙 · Cross-review 페어링 초안 · GPU 슬롯 룰
- **결정할 것:** gglee 최종 sign-off → AGENTS.md v0.2 확정 (`main` push)
- **표명 필요:** gglee ☐ sign-off / ☐ 수정 요청

#### 안건 2-3. Cross-review 페어링 확정 (5분)
- **현재 초안:**

| 작성자 | Critic 담당 |
|---|---|
| sjpark (모델링 결과) | gglee |
| kkkim (임베딩 결과) | jamie 또는 sjpark |
| jamie (데이터/split) | braveji 또는 gglee |
| jhans (TE 결과) | gglee |

- **결정할 것:** kkkim/jamie 담당자 최종 확정
- **표명 필요:** 전원 ☐ 페어링 OK

#### 안건 2-4. TCGA controlled access — dbGaP PI 지정 (5분)
- **현안:** somatic mutation 사용 시 PI 서명 필요. 학생 단독 신청 불가.
- **결정할 것:** PI 누구? 신청 일정은? (Paper A open access 범위로 선진행 후 controlled 추가 방안)
- **표명 필요:** PI 후보 ☐ 확정 / ☐ Sprint 1 중 별도 논의

#### 안건 2-5. GPU 슬롯 룰 확인 + gpu.lock 방향 (5분)
- **현재 잠정 룰:**

| 슬롯 | 시간 |
|---|---|
| A | 09:00–13:00 |
| B | 13:00–17:00 |
| C | 17:00–21:00 |
| D | 21:00–01:00 |

- **결정할 것:** 슬롯 룰 그대로 유지? Sprint 1 중 gpu.lock wrapper 개발 여부(ykji)?
- **표명 필요:** ☐ 현행 유지 / ☐ 변경안

#### 안건 2-6. 실험 추적 도구 결정 (5분)
- **후보:** wandb / MLflow / DVC / git-only
- **결정할 것:** 1종 선택 → AGENTS.md §5에 반영 (BIOP02-43)
- **표명 필요:** ☐ 선택 완료

---

### Slot 3 — Sprint 1 분배 (5분)

> Sprint 1 기간: 5/22–6/05

| 담당자 | Sprint 1 핵심 태스크 | 의존 |
|---|---|---|
| **kkkim** | TCGA-BRCA ~150 slides 전체 tiling → 임베딩 추출 | HF 승인 즉시 시작 |
| **sjpark** | ER status binary MLP 학습 + 3 baseline 비교 | kkkim 임베딩 수령 즉시 |
| **jamie** | `split_policy_v0` patient-level split → 5명 OK → lock | 5/29 이전 lock 필수 |
| **gglee** | 첫 `critic_report.json` (ER status MLP 결과 대상) | sjpark 결과 후 |
| **braveji** | 실험 추적 도구 적용 + `experiments/` 표준 구축 (BIOP02-43, 44) | 오늘 도구 결정 후 |
| **jhans** | DepMap PRISM + GDSC 스키마 초안 | 독립 진행 |

**Sprint 1 종료 기준 (6/05):** `critic_report.json` 1건 + ER status AUC 베이스라인 비교 수치 공유

> **표명 필요:** 각자 Sprint 1 태스크 ☐ OK 표명. 침묵 = 통과 금지.

---

### Slot 4 — 마무리 (없음 / 초과 방지)

- 다음 정기 미팅: **2026-06-05 (금)** — Sprint 1 closeout
- 회의록: braveji 작성 → 당일 Slack `#biop02-dev` 공유 + Confluence 업로드 (BIOP02-16)

---

## 사전 읽기 자료

| 자료 | 위치 | 담당 |
|---|---|---|
| 스토리지 비교안 | `guide/storage-comparison.md` | braveji |
| AGENTS.md v0.2 | `AGENTS.md` | braveji |
| 담당자 업무 분담 | `guide/plan-v1.0.md` | braveji |
| Hypothesis schema | `schemas/hypothesis.schema.json` | kkkim |

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1.0 | 2026-05-20 | BIOP02-15 산출물. Sprint 0 합격선 점검 + 6개 결정 안건 + Sprint 1 분배 포함. |

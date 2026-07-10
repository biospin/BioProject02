# 작업일지 — sjpark (박세진) | 2026-06-03

Sprint 1 (5/22–6/05) 진행 중 | 주요 작업: BIOP02-39, 40 파이프라인 연결

---

## 1. 현황 파악

Confluence [진행현황] Sprint 1 중간 점검(2026-05-29) 확인.

- Sprint 0 완료 (BIOP02-31~34) — JIRA 기준 완료 상태 재확인
- Sprint 1 현재 블로커:
  - kkkim: TCGA-BRCA 전수 다운로드 + tiling + UNI 임베딩 (GPU 타인 점유로 대기)
  - jamie: split_policy_v0 lock (5명 서명 대기)

---

## 2. BIOP02-32, 33 재검토

### 비평 검토

"smoke test가 kkkim의 실제 파일을 쓰지 않았다"는 비평에 따라 pilot 파일로 파이프라인 연결 테스트를 추가 수행했으나, 이후 Sprint 0 완료 기준을 재확인한 결과:

- Sprint 0 스켈레톤 완료 기준: dummy 데이터로 1회 실행 → 처음부터 충족
- 실제 `.npy` 로딩 파이프라인 검증은 Sprint 1(BIOP02-39, 40) 영역

**결론: 재작업은 불필요했으며 Sprint 1 사전 준비에 해당.** JIRA 댓글로 명시.

### 추가 수행 내용 (Sprint 1 사전 준비)

- pilot manifest(2장)로 `load_manifest_dataset()` 실제 실행 확인
- `MeanEmbedBaseline` 단일 클래스 예외 처리 버그 수정 (commit `3749293`)

---

## 3. BIOP02-41 split_policy_v0 서명 요청

jamie의 split_policy 파일이 GitHub에 push되지 않아 검토 불가.
BIOP02-41에 브랜치 push 요청 댓글 등록.

---

## 4. kkkim 대안 기반 BIOP02-39, 40 착수

### 배경

GPU 타인 점유로 UNI 실제 임베딩 추출 대기 중.\
kkkim이 BIOP02-39 댓글로 dummy manifest를 준비해 파이프라인 먼저 연결하도록 안내.

### kkkim 준비 파일

| 항목 | 경로 |
|---|---|
| Manifest (최종 1010장) | `/workspace/data/cache/biop02/embedding_manifest_dummy.csv` |
| Dummy embeddings | `/workspace/data/cache/biop02/dummy_embeddings/<slide_id>_dummy_embeddings.npy` |
| Split v1 | train 706 / val 151 / test 153 (ER stratified) |

### 발견된 이슈: split 미할당 510장

초기 manifest 확인 시 1010장 중 500장만 split 할당(train 350/val 75/test 75), 510장 미할당 발견.
kkkim 확인 결과: 500장 candidate에서 split 생성 후 1010장으로 확장 시 split 재생성 누락.
→ kkkim이 1010장 전체 기준으로 split 재할당 후 manifest 업데이트.

### 코드 수정: manifest 형식 불일치 해소

**원인:** embedding manifest CSV 레이블 인코딩 스펙이 Sprint 0에서 사전 정의되지 않음.
- sjpark `train.py`: 숫자 레이블(0/1) 가정
- kkkim manifest: TCGA 원본 형식 `"Positive"/"Negative"` 텍스트 사용

**수정 내용 (commit `515720f`):**

`agents/modeling/scripts/train.py`, `agents/modeling/scripts/run_baselines.py`
- `LABEL_MAP = {"positive": 1.0, "negative": 0.0}` 추가
- `Equivocal` / `Indeterminate` / `[Not Available]` / `[Not Evaluated]` 자동 제외
- 80/20 랜덤 split → manifest `split` 컬럼 기반 분리로 변경

`agents/modeling/configs/baseline_er_status.yaml`
- `embedding_manifest`: kkkim manifest 경로 적용
- `label_col`: `er_status` → `er`

---

## 5. 실행 결과

### BIOP02-39: ER status binary MLP (dummy, 1010장)

```
manifest: /workspace/data/cache/biop02/embedding_manifest_dummy.csv
Slides: train=706 / val=151
epochs: 10 / wall-clock: 57.7s (CUDA)
val_acc: 0.775 (Epoch 1) → 0.656 (Epoch 10)
```

overfitting 패턴은 dummy 데이터 특성 (랜덤 노이즈엔 패턴 없음). 파이프라인 정상 동작 확인.

### BIOP02-40: 3 trivial baseline (dummy, 1010장)

| Baseline | AUC | AUPRC | Balanced Acc |
|---|---|---|---|
| random | 0.568 | 0.790 | 0.590 |
| majority | 0.500 | 0.775 | 0.500 |
| mean_embed | 0.607 | 0.826 | 0.500 |

dummy 데이터 기준 수치이므로 UNI 임베딩 교체 후 재측정 필요.

---

## 6. kkkim Critic 리뷰 및 schemas 미준수 수정

### Critic 리뷰 결과 (BIOP02-39)

kkkim이 `er_status_dummy_v1` Critic 리뷰를 수행했고 **2건 FAIL + 2건 PASS + N/A**로 조건부 통과.

| 항목 | 결과 |
|---|---|
| data_leakage | ✅ PASS — split 컬럼 기반 분리 확인 |
| drp_framing | ✅ PASS — 금지 표현 없음 |
| baseline_comparison | ❌ FAIL — AUC/AUPRC/balanced_accuracy null |
| claim_level | ❌ FAIL — metrics.json에 claim_level, critic_status 필드 없음 |
| counterfactual, cross_dataset, biological_plausibility | ⚪ N/A — dummy embedding 조건 |

### schemas 미준수 원인

BIOP02-32 작성 시 `schemas/` 디렉토리를 참조하지 않고 AGENTS.md 필수 필드 목록만 참고.  
`hypothesis.schema.json`에 required로 정의된 필드들이 누락된 채 구현됨.

**원칙 추가:** 새 코드 작성 전 `schemas/`를 먼저 확인하고, 출력 형식을 schema에 맞춰 설계한 뒤 구현.

### 수정 내역 (train.py / run_baselines.py)

| 커밋 | 수정 내용 |
|---|---|
| `4cd2b9f` | AUC/AUPRC/balanced_accuracy 계산 추가, claim_level/critic_status 추가 |
| `c3357cb` | schema_version, created_at 추가 / predictions.npy 저장 / 실험 디렉토리 구조 수정 / config.yaml 복사 |
| `c10f890` | run_baselines.py 동일 수정 (schema_version, created_at, claim_level, critic_status, 디렉토리 구조) |
| `ba04e77` | 실험 디렉토리 날짜 기반 → `--tag` 명시 방식으로 변경 |

### --tag 방식 도입 이유

날짜 기반(`20260603_er_status`) 방식은 UNI 임베딩으로 재실행 시 여러 디렉토리가 생겨 최신 결과 구분이 어려웠음.

```bash
# dummy 실행
python train.py --config ... --tag dummy_v1
→ experiments/sjpark/er_status_dummy_v1/

# UNI 실제 임베딩 실행
python train.py --config ... --tag uni_v1
→ experiments/sjpark/er_status_uni_v1/
```

### 레이블 형식 불일치 최종 확인

초기 발견: sjpark `train.py`는 숫자(0/1) 가정, kkkim manifest는 텍스트(`"Positive"/"Negative"`).  
수정 후 최종 실행(`er_status_dummy_v1`)에서 `train=706 val=151` 정상 로딩, AUC `0.6036` 산출 — 레이블 변환 정상 작동 확인.

---

## 7. 최종 실험 결과 (er_status_dummy_v1)

### BIOP02-39: ER status binary MLP

```
경로: experiments/sjpark/er_status_dummy_v1/
아티팩트: model.pt / metrics.json / predictions.npy / config.yaml

n_train=706 / n_val=151 / epochs=10 / 54.5s (CUDA)
AUC: 0.6036 / AUPRC: 0.8407 / balanced_accuracy: 0.517
claim_level: hypothesis_only / critic_status: pending
```

### BIOP02-40: 3 trivial baseline

```
경로: experiments/sjpark/er_status_dummy_v1_baselines/
아티팩트: trivial_baselines.json
```

| Baseline | AUC | AUPRC | Balanced Acc |
|---|---|---|---|
| random | 0.568 | 0.790 | 0.590 |
| majority | 0.500 | 0.775 | 0.500 |
| mean_embed | 0.607 | 0.826 | 0.500 |

모든 수치는 dummy embedding 기준 (파이프라인 검증 목적).

---

## 8. JIRA 업데이트

| 티켓 | 상태 변경 | 내용 |
|---|---|---|
| BIOP02-39 | 해야 할 일 → **진행 중** | Critic FAIL 수정, 최종 결과, 수정 이력 전체 |
| BIOP02-40 | 해야 할 일 → **진행 중** | 최종 결과, 수정 이력 |
| BIOP02-32, 33 | 완료 유지 | schemas 미참조 회고 댓글 추가 |
| BIOP02-41 | 진행 중 유지 | 브랜치 push 요청 댓글 |
| BIOP02-44 | 완료 유지 | template에 4개 필드 추가 요청 댓글 + 이유 설명 |

---

## 9. 인사이트

### schemas 미참조 문제

`hypothesis.schema.json`이 BIOP02-29(kkkim)에서 완성됐고 sjpark BIOP02-32는 그 이후 작업임에도 schemas를 참조하지 않아 5건의 미준수 사항 발생. Critic FAIL로 뒤늦게 발견됨.  
**원칙: 새 코드 작성 전 schemas/ 먼저 확인.**

### embedding manifest 인터페이스 스펙 누락

`hypothesis.schema.json`은 출력 포맷을 정의했으나, 에이전트 간 중간 데이터(manifest CSV 레이블 인코딩)가 정의되지 않아 불일치 발생.  
Sprint 2 전에 `schemas/embedding_manifest.schema.json` 정의 필요.

### split 생성과 manifest 확장의 순서 문제

500장 split → 1010장 확장 시 split 재생성 누락. 대규모 manifest 확장 시 split 미할당 행 사전 검증 절차 필요.

### GPU 점유 상황에서의 대응

dummy embedding으로 파이프라인을 먼저 연결해두는 방식이 효과적. UNI 임베딩 완료 시 `--tag uni_v1`만 바꿔서 즉시 재실행 가능.

---

## 10. 다음 단계

| 조건 | 액션 |
|---|---|
| kkkim GPU 슬롯 확보 + tiling + UNI 임베딩 완료 | `--tag uni_v1`으로 BIOP02-39, 40 재실행 → 실제 AUC 산출 |
| jamie split_policy_v0 브랜치 push | 검토 후 서명 (BIOP02-41) |
| 위 두 가지 완료 | BIOP02-39, 40 완료 → kkkim Critic 최종 리뷰 착수 |

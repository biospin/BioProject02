# 작업일지 — sjpark (박세진) | 2026-06-05

Sprint 1 (5/22–6/05) 마감일 | BIOP02-39, 40 Critic 피드백 마무리

---

## 1. commit_hash "unknown" 수정 (BIOP02-39)

### 원인

kkkim Critic에서 `metrics.json`의 `commit_hash: "unknown"` 지적.

서버(`/workspace`)는 `scp`로 파일만 복사한 디렉토리라 `.git`이 없음.  
`git rev-parse HEAD` 실패 → fallback `"unknown"` 저장.

### 수정 (커밋: `93f4ae6`)

`--commit_hash` 인자 추가. 로컬에서 hash를 명시적으로 전달하는 방식.

```bash
python train.py --config ... --tag dummy_v1 \
  --commit_hash $(git rev-parse HEAD)
```

미전달 시 git 자동 감지 fallback 유지.  
`run_baselines.py`에도 동일하게 적용.

**재실행 결과:** `commit_hash: "ba04e7793a62faf6540b86ed1bef8719f88c3dbf"` 정상 기록 확인.

---

## 2. braveji BIOP02-44 template 업데이트 확인

6/3에 요청한 `experiments/template/metrics.json` 4개 필드 추가를  
braveji가 반영 완료한 것을 pull 시 확인.

```json
"schema_version": "0.1",
"created_at": "<ISO 8601 UTC e.g. 2026-06-03T12:00:00Z>",
"claim_level": "hypothesis_only",
"critic_status": "pending"
```

BIOP02-44에 확인 댓글 등록.

---

## 3. BIOP02-40 kkkim Critic 권고 반영

### Critic 리뷰 결과 (2026-06-04)

**conditional_pass** — PASS 항목 전부 충족, 권고 사항 1건.

| 항목 | 결과 |
|---|---|
| 3종 baseline 구현 | ✅ PASS |
| 1010장 기준 실행 | ✅ PASS |
| claim_level, critic_status, schema_version, created_at | ✅ PASS |
| run_command 필드 | ❗ 권고 (재현성) |

### 권고 분석

`trivial_baselines.json`에 실행 명령이 기록되어 있지 않아 재현 시 어떤 인자로 실행했는지 알 수 없는 문제.  
`run_command` 또는 `script` 필드로 재현 가능하도록 기록 권장.

### 영향 범위 확인

| 코드 | 영향 |
|---|---|
| `run_baselines.py` | ✅ 수정 대상 — 출력 JSON에 필드 추가 |
| `train.py` / `mlp.py` / `trivial.py` | ❌ 영향 없음 |
| kkkim Critic 다운스트림 | ❌ non-breaking (필드 추가) |
| braveji template | ❌ trivial_baselines.json 템플릿 없음 |

### 수정 (커밋: `97b3592`)

`run_baselines.py`에 `sys.argv` 전체를 `run_command` 필드로 기록.

```json
"run_command": "agents/modeling/scripts/run_baselines.py --manifest ... --tag dummy_v1 --commit_hash ..."
```

---

## 4. 커밋 이력

| 커밋 | 내용 |
|---|---|
| `93f4ae6` | commit_hash unknown 수정 — --commit_hash 인자 추가 (train.py, run_baselines.py) |
| `97b3592` | trivial_baselines.json에 run_command 필드 추가 |

---

## 5. JIRA 업데이트

| 티켓 | 내용 |
|---|---|
| BIOP02-39 | commit_hash 수정 원인 분석 + 재실행 결과 댓글 |
| BIOP02-40 | Critic 권고 반영(run_command) 댓글 |
| BIOP02-44 | braveji template 업데이트 확인 댓글 |

---

## 6. 현재 상태

| 항목 | 상태 |
|---|---|
| BIOP02-39 (MLP) | 진행 중 — dummy_v1 파이프라인 완료, UNI 임베딩 대기 |
| BIOP02-40 (baseline) | 진행 중 — dummy_v1 완료, UNI 임베딩 대기 |
| kkkim GPU + 임베딩 | 대기 중 |
| jamie split_policy_v0 | 브랜치 push 대기 중 |

## 7. 다음 단계

UNI 임베딩 완료 시 실행 명령:

```bash
# MLP
python agents/modeling/scripts/train.py \
  --config agents/modeling/configs/baseline_er_status.yaml \
  --tag uni_v1 \
  --commit_hash $(git rev-parse HEAD)

# Baselines
python agents/modeling/scripts/run_baselines.py \
  --manifest /workspace/data/cache/biop02/embedding_manifest_uni.csv \
  --label_col er --task er_status \
  --tag uni_v1 \
  --commit_hash $(git rev-parse HEAD)
```

완료 후 kkkim 최종 Critic 리뷰 → critic_status: pass → BIOP02-39, 40 완료 처리.

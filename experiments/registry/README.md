# 교차검증 실험 registry (BIOP02-57)

> 담당: braveji (Orchestrator) | Sprint 3 | 관련: BIOP02-44(experiments/ 표준), BIOP02-53(Attention MIL 교차학습), BIOP02-56(Critic #3·#4), BIOP02-54(CPTAC 임베딩)

**교차 데이터셋 검증**(TCGA-BRCA 학습 → **CPTAC-BRCA** 외부 테스트) 실험을 한 곳에서 추적하는 append-only registry.
in-domain(TCGA val) 대비 out-of-domain(CPTAC test) 성능 하락(generalization gap)을 표준 포맷으로 기록해, Fig 4(외부검증)와 Critic #4(cross-dataset)의 근거로 쓴다.

## 왜 필요한가

개별 실험 디렉토리(`experiments/<user>/<date>/`)는 실험 하나의 아티팩트를 담지만, "어떤 endpoint × 임베딩 × 모델 조합이 외부 코호트에서 얼마나 견디는가"를 **가로질러 비교**할 인덱스가 없다. 이 registry가 그 인덱스다.

## 디렉토리 / 파일 구조

```
experiments/
  registry/
    README.md                          # (이 문서)
    cross_validation_registry.jsonl    # append-only, 1줄 = 1 실험 (JSON object)
    entry.example.json                 # 스키마 예시 1건 (실제 결과 아님)
    validate_registry.py               # 스키마 검증 스크립트
  <owner>/<YYYYMMDD_설명>/             # 실제 아티팩트 5종 (BIOP02-44 표준)
    config.yaml  model.pt  metrics.json  predictions.npy  critic_report.json
schemas/
  cv_registry.schema.json              # registry 엔트리 JSON Schema v0.1
```

- **registry 엔트리는 아티팩트를 복제하지 않는다.** `experiment_dir`/`commit_hash`로 실제 산출물을 가리키기만 한다(single source of truth = 실험 디렉토리).
- 엔트리 스키마: [`schemas/cv_registry.schema.json`](../../schemas/cv_registry.schema.json).

## 엔트리 필드 요약

| 필드 | 의미 |
|---|---|
| `entry_id` | `cv-<YYYYMMDD>-<endpoint>-<embedding>-<model>` (예: `cv-20260703-er-uni-mlp`) |
| `endpoint` | `er_status` / `pr_status` / `her2_status` / `pam50` |
| `model` / `embedding_model` | 모델 구조 / 임베딩(uni_v1·conch·…) |
| `split_policy` | lock된 split 참조 (site-disjoint 707/152/151) |
| `internal_metrics` | TCGA held-out val (in-domain) AUC/AUPRC/balanced_acc |
| `external_metrics` | **CPTAC test (out-of-domain)** AUC/AUPRC/balanced_acc |
| `generalization_gap` | internal − external (양수 = 외부에서 성능 하락) |
| `baselines` | 외부 코호트 trivial baseline (Critic #2) — 외부 AUC가 이를 넘어야 신호 주장 |
| `experiment_dir` / `commit_hash` | 아티팩트 5종 위치 + 재현용 커밋 |
| `critic_status` | `pending`/`pass`/`caution`/`reject` — **pass 후에만 공유** |
| `claim_level` | 항상 `hypothesis_only` |

## 사용법

```bash
# 1) 엔트리 1건 추가 (append) — entry.example.json을 복사해 값 채운 뒤 한 줄로 append
python -c "import json,sys; print(json.dumps(json.load(open('my_entry.json'))))" \
  >> experiments/registry/cross_validation_registry.jsonl

# 2) 스키마 검증 (커밋 전 필수)
python experiments/registry/validate_registry.py \
  --registry experiments/registry/cross_validation_registry.jsonl \
  --schema schemas/cv_registry.schema.json
```

## 규칙 (거버넌스)

- **Owner ≠ Reviewer.** `owner`(실험자)와 `reviewer`(Critic)는 달라야 한다.
- **`critic_status: pass` 전에는 `#biop02-experiments` 공유 금지.** registry 등록은 되지만 공유 불가 상태(`pending`/`caution`)로만 남는다.
- Critic 총괄 = **braveji**. 바이오 sub-check는 **#4 cross-dataset → jhans, #5 biological plausibility → sjpark** 분담.
- 모든 엔트리 `claim_level`은 `hypothesis_only`. "drug response prediction"·"개인 맞춤 치료" 표현 금지(Critic #6).
- 외부검증 결과 lock은 BIOP02-70에서 최종 확정한다.

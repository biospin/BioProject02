# [스터디 공유] sjpark Sprint 1 진행 현황 — 2026-06-05

> 담당: 박세진 (sjpark) | Modeling Agent — phenotype prediction (MLP, attention MIL)  
> 기간: 2026-06-03 ~ 06-05 | Sprint 1 (5/22–6/05)

---

## Sprint 1 소개

Sprint 1 (5/22–6/05)은 **"파이프라인의 첫 번째 숫자를 만드는 단계"** 입니다.

Sprint 0에서 인프라, 데이터 확인, 임베딩 도구, 모델 골격을 만들었다면, Sprint 1은 실제 TCGA-BRCA 슬라이드를 처음부터 끝까지 돌려서 **ER status 예측 AUC 수치를 처음으로 산출하는 것**이 목표입니다.

```
jamie     → TCGA-BRCA 150~1010장 환자 분리 (split_policy_v0 lock)
kkkim     → 전체 슬라이드 tiling + UNI 임베딩 추출
sjpark    → ER status MLP 학습 + 3 trivial baseline 비교 → AUC 산출
kkkim     → sjpark 결과 Critic 리뷰 (7항목 체크리스트)  ← Week 10 변경
braveji   → 실험 추적 도구 확정(wandb/MLflow) + experiments/ 디렉토리 표준 수립
jhans     → DepMap/GDSC 스키마 초안 (치료 가설 연결 준비)
```

> Critic 페어링 (Week 10 확정): sjpark 결과 → **kkkim** 리뷰 / kkkim 결과 → jamie 리뷰

팀 전체가 처음으로 "H&E 이미지로 분자 아형 예측이 되는가?"에 대한 첫 번째 숫자를 보는 스프린트입니다.

---

## sjpark의 역할

저는 **Modeling Agent**로, kkkim이 만든 임베딩을 입력받아 ER status를 예측하는 모델을 학습하고 평가합니다.

구체적으로:
- **BIOP02-39**: ER status binary MLP 학습 → AUC/AUPRC/Balanced Accuracy 산출
- **BIOP02-40**: Random / Majority / Mean Embed 3종 trivial baseline 비교

MLP가 trivial baseline을 넘지 못하면 "H&E 이미지가 ER 예측에 유효하지 않다"는 의미이고, 넘으면 "비선형 패턴이 존재한다"는 첫 번째 증거가 됩니다. 이 비교가 Sprint 1의 핵심입니다.

현재는 kkkim의 UNI 임베딩이 준비되기를 기다리면서, **dummy embedding(랜덤 노이즈)으로 파이프라인을 먼저 완성**해두는 작업을 진행했습니다.

---

## 이 작업이 왜 필요한가

프로젝트의 핵심 가설은 하나입니다.

> **H&E 슬라이드 이미지만 보고 유방암의 분자 특성(ER/HER2 양성 여부)을 예측할 수 있는가?**

IHC 검사 없이 이미지만으로 분자 아형을 추론할 수 있다면 임상적 가치가 큽니다. 제 역할은 이 가설을 수치로 검증하는 **예측 모델(MLP)**과 **비교 기준선(Trivial Baseline)** 을 구현하는 것입니다.

지금 단계는 아직 가설 검증이 아닙니다. **"실제 데이터가 도착했을 때 즉시 실험할 수 있는 파이프라인을 완성하는 것"** 이 목표였습니다.

---

## 무엇을 했나

### 1. 파이프라인 연결 (GPU 없이 선행 진행)

kkkim님이 UNI 임베딩 추출을 위한 GPU 슬롯을 기다리는 동안, dummy embedding(랜덤 노이즈)으로 먼저 파이프라인을 연결했습니다.

```
H&E 슬라이드
  → kkkim: 타일링 + UNI 임베딩 추출       ← 현재 GPU 대기 중
  → sjpark: MLP 학습 + baseline 비교      ← 파이프라인 완성, 실제 데이터 대기 중
  → kkkim: Critic 리뷰
```

kkkim이 TCGA-BRCA 1010장 전체의 dummy manifest를 준비해줬고, 이것으로 코드가 실제 데이터 형식을 처리할 수 있는지 먼저 검증했습니다.

---

## Sprint 0 작업 재검토 — 재작업이 필요했나?

### 배경

Sprint 0에서 완료한 BIOP02-32, 33(MLP 스켈레톤, trivial baseline)에 대해 "smoke test가 kkkim의 실제 파일을 사용하지 않았다"는 비평이 있었습니다. 이에 따라 pilot 임베딩 파일(2장)로 실제 파이프라인을 돌리는 재작업을 수행했습니다.

### 재작업 내용

- kkkim pilot 파일 경로로 mini manifest 생성 (dummy + UNI 각 1장)
- `load_manifest_dataset()` 실제 실행 확인
- 레이블이 모두 같아 `MeanEmbedBaseline`(LogReg) 실패 → 단일 클래스 예외 처리 버그 수정 (commit `3749293`)

### 재검토 결과: 재작업은 불필요했다

Sprint 0 스켈레톤 완료 기준을 다시 확인한 결과:

| 완료 기준 | 상태 |
|---|---|
| dummy 데이터로 코드가 1회 실행되는가? | ✅ 처음부터 충족 |
| 실제 .npy 파일 로딩 파이프라인 검증 | ❌ Sprint 1(BIOP02-39, 40) 영역 |

실제 파일로 파이프라인을 연결하는 것은 Sprint 1의 작업입니다. Sprint 0는 "코드가 돌아가는가"를 확인하는 단계였고, 이 기준은 처음부터 충족되어 있었습니다.

재작업의 긍정적 결과물은 `MeanEmbedBaseline` 버그 수정 하나였으며, 파이프라인 연결 테스트 자체는 Sprint 1 사전 준비로 의미를 재정의했습니다.

### Lesson Learned

> **Sprint 완료 기준을 JIRA 티켓에 명시적으로 기록해야 한다**

스켈레톤 태스크의 완료 기준이 "dummy 데이터 1회 실행"인지, "실제 파일로 파이프라인 연결"인지가 문서화되어 있지 않았기 때문에 비평과 불필요한 재작업이 발생했습니다. 각 Sprint의 Done Definition을 티켓 description에 명확히 적어두면 이런 혼선을 방지할 수 있습니다.

---

## 시행착오와 해결 과정

### 시행착오 1: 레이블 형식 불일치

sjpark 코드는 숫자 레이블(0/1)을 가정하고 작성됐는데, kkkim의 manifest는 TCGA 원본 형식인 텍스트(`"Positive"/"Negative"`)를 사용했습니다.

**근본 원인:** Sprint 0에서 두 agent 사이의 중간 데이터(manifest CSV) 형식을 사전에 합의하지 않았습니다.

```python
# 수정 전: float("Positive") → ValueError
label = torch.tensor(float(label_val))

# 수정 후
LABEL_MAP = {"positive": 1.0, "negative": 0.0}
label = torch.tensor(LABEL_MAP[label_raw])
# + Equivocal/Indeterminate 등 불명확 레이블 자동 제외
```

**교훈:** 에이전트 간 인터페이스 스펙(manifest CSV 레이블 인코딩)을 `schemas/`에 사전 정의해야 합니다.

---

### 시행착오 2: split 미할당 510장

처음 실행 시 1010장 중 500장만 split이 할당되어 있고 510장은 미할당이었습니다.

```
초기: train 350 / val 75 / test 75 (500장) + 미할당 510장
최종: train 706 / val 151 / test 153 (1010장 전체)
```

**원인:** kkkim이 처음 500장 기준으로 split을 생성한 뒤 1010장으로 manifest를 확장할 때 split 재생성을 누락했습니다.

**해결:** kkkim이 1010장 전체 기준으로 split을 재생성하고 manifest를 업데이트했습니다.

**교훈:** manifest 규모 확장 시 split 재생성 여부를 반드시 검증하는 절차 필요합니다.

---

### 시행착오 3: schemas를 참조하지 않은 코드

`train.py` 최초 작성 시(BIOP02-32) `schemas/` 디렉토리를 확인하지 않고, **AGENTS.md의 `metrics.json` 필수 필드 목록만 참고**하여 구현했습니다. 그 결과 Critic 리뷰에서 5건의 미준수 사항이 발견됐습니다.

**schemas 위치 (참조했어야 할 파일):**
- `schemas/hypothesis.schema.json` — 파이프라인 출력 형식 (BIOP02-29에서 kkkim 작성)
- `schemas/critic_report.schema.json` — Critic 리포트 형식

**kkkim Critic FAIL 2건:**

| 항목 | 문제 | 해결 |
|---|---|---|
| baseline_comparison | val set AUC/AUPRC/BalAcc를 계산하지 않고 `null` 저장 | sklearn 지표 계산 추가 |
| claim_level | `claim_level`, `critic_status` 필드 없음 | `hypothesis_only`, `pending` 추가 |

**추가 발견 미준수 (5건):**

| 항목 | 문제 | 해결 |
|---|---|---|
| schema_version / created_at | `hypothesis.schema.json` required 필드 누락 | 추가 |
| predictions.npy | 실험 디렉토리 필수 아티팩트 미저장 | val set 예측값 저장 |
| config.yaml | 실험 디렉토리에 복사되지 않음 | 자동 복사 추가 |
| 실험 디렉토리 구조 | `experiments/er_status/` (규칙 위반) | `experiments/sjpark/<task>_<tag>/` 적용 |
| commit_hash | 서버에서 `"unknown"` 저장 | `--commit_hash` 인자로 명시 전달 |

**근본 원인:** `hypothesis.schema.json`은 BIOP02-29에서 kkkim이 이미 완성했는데, sjpark BIOP02-32 작성 시 이를 참조하지 않고 AGENTS.md 목록만 확인했습니다. schemas와 AGENTS.md가 정의하는 범위가 달랐고, 이 차이가 Critic 리뷰에서 뒤늦게 발견됐습니다.

**원칙으로 추가:** 새 코드 작성 전 `schemas/`를 먼저 확인하고, 출력 형식을 schema에 맞춰 설계한 뒤 구현.

---

### 시행착오 4: commit_hash "unknown"

서버에서 실행하면 `metrics.json`의 `commit_hash`가 `"unknown"`으로 저장됐습니다.

**원인:** 서버의 `/workspace`는 `scp`로 파일만 복사한 디렉토리라 `.git`이 없어 `git rev-parse HEAD`가 실패합니다.

```bash
# 해결: 로컬에서 hash를 명시적으로 전달
python train.py --config ... --tag uni_v1 \
  --commit_hash $(git rev-parse HEAD)
```

---

### 실험 디렉토리 구조: 날짜 → tag 방식

처음에는 날짜 기반(`20260603_er_status`)으로 디렉토리를 생성했으나, UNI 임베딩으로 재실행 시 `20260603_`, `20260605_` 두 디렉토리가 생겨 최신 결과 구분이 어려웠습니다.

```bash
# 변경 후: 의미 있는 tag로 명시
--tag dummy_v1  → experiments/sjpark/er_status_dummy_v1/
--tag uni_v1    → experiments/sjpark/er_status_uni_v1/
```

---

## 현재 결과 (dummy embedding 기준)

> **중요:** 아래 수치는 랜덤 노이즈(dummy) 데이터 기준이므로 과학적 의미가 없습니다. 파이프라인이 정상 동작하는지를 검증한 것입니다.

### MLP (BIOP02-39)

```
train=706 / val=151 / 10 epochs / 54.5s (CUDA)
AUC: 0.6036 / AUPRC: 0.8407 / BalAcc: 0.517
```

train_loss가 급감하는데 val_loss가 급증하는 overfitting 패턴 → dummy 데이터에 패턴이 없으니 당연합니다. UNI 임베딩으로 교체하면 이 패턴이 사라지고 의미 있는 수렴이 나타나야 합니다.

### 3 Trivial Baseline (BIOP02-40)

| Baseline | AUC | 의미 |
|---|---|---|
| random | 0.568 | 아무 정보 없이 찍었을 때 |
| majority | 0.500 | 항상 ER+ 예측 |
| mean_embed | 0.607 | 선형 분류기 최소 성능 |

**MLP가 이 수치를 넘지 못하면 H&E 이미지가 ER 예측에 도움이 되지 않는다는 의미입니다.**

---

## Critic 리뷰 결과 요약

| 티켓 | Critic | 결과 | 내용 |
|---|---|---|---|
| BIOP02-39 | kkkim | conditional_pass | FAIL 2건 수정 완료, dummy 조건 N/A 3건 |
| BIOP02-40 | kkkim | conditional_pass | PASS 전항목, 권고 1건(run_command) 반영 |

---

## braveji님께 template 업데이트 제안 (BIOP02-44)

### 제안 배경

kkkim Critic FAIL을 수정하면서 `hypothesis.schema.json`에 required로 정의된 필드 4개가 `experiments/template/metrics.json`에 빠져 있다는 것을 발견했습니다.

template은 팀 전체가 참조하는 기준 파일이기 때문에, 여기에 없으면 다른 팀원들도 같은 실수를 반복할 수 있습니다.

### 제안 내용

```json
// 추가 요청 필드
"schema_version": "0.1",
"created_at": "<ISO 8601 UTC e.g. 2026-06-03T12:00:00Z>",
"claim_level": "hypothesis_only",
"critic_status": "pending"
```

### 각 필드가 필요한 이유

| 필드 | 이유 |
|---|---|
| `schema_version` | 출력이 어느 버전 스키마를 따르는지 명시 → 스키마 변경 시 하위 호환성 추적 |
| `created_at` | 실험 실행 시점 기록 → 같은 task의 여러 실험 구분 |
| `claim_level: "hypothesis_only"` | DRP 금지 원칙의 코드 레벨 강제 장치, Critic 7번 체크리스트에서 직접 확인 |
| `critic_status: "pending"` | 결과 공유 전 Critic pass 여부 추적, 초기값 pending → Critic 후 pass/caution/reject |

### 결과

braveji님이 바로 반영해주셨습니다. ✅  
이제 template을 참고하면 schemas 미준수 문제가 예방됩니다.

---

## 팀 협업 측면의 배움

**인터페이스 스펙 없이는 통합이 안 된다**

6명이 역할을 나눠 개발하는 구조에서 각 agent의 출력 형식이 다른 agent의 입력이 됩니다. `schemas/`에 출력 형식은 정의했지만 **agent 간 중간 데이터(manifest CSV)의 레이블 인코딩 방식이 누락**되어 통합 시 불일치가 발생했습니다. Sprint 2 전에 `schemas/embedding_manifest.schema.json` 정의가 필요합니다.

**GPU 없이도 파이프라인을 먼저 연결하는 전략이 효과적**

UNI 임베딩이 준비되기 전에 dummy embedding으로 파이프라인을 완성해두면, 실제 데이터가 도착하는 순간 명령어 하나만 바꿔서 바로 실험할 수 있습니다.

---

## 회고 기반 제안 — 하네스 / 스킬

오늘 경험한 pain point들을 자동화로 해소할 수 있는 제안입니다.

---

### 제안 1. `/validate-experiment` 스킬 (우선순위 최고)

**배경:** BIOP02-32 작성 시 `schemas/`를 참조하지 않아 Critic FAIL 5건이 뒤늦게 발견됐습니다. Critic 리뷰 전에 사전 검증할 수 있었다면 수정 커밋을 4번 반복하지 않아도 됐습니다.

**기능:** 실험 디렉토리의 아티팩트가 `hypothesis.schema.json`을 준수하는지 자동 점검합니다.

```
/validate-experiment experiments/sjpark/er_status_uni_v1/
```

점검 항목:
- `metrics.json`: `schema_version`, `created_at`, `claim_level`, `critic_status`, `commit_hash` 형식 (`[0-9a-f]{7,40}`)
- `predictions.npy` 존재 여부
- `config.yaml` 존재 여부
- 실험 디렉토리 구조 (`experiments/<username>/<task>_<tag>/`)

**기대 효과:** Critic 리뷰 전에 sjpark 스스로 사전 검증 → 팀 전체의 Critic 리뷰 효율 향상

---

### 제안 2. `/run-experiment` 스킬

**배경:** 서버 실행 시 `--commit_hash $(git rev-parse HEAD)`를 매번 수동으로 추가해야 했고, scp 업로드 → ssh 실행 순서도 반복됩니다.

**기능:** 로컬에서 한 번에 처리합니다.

```
/run-experiment --script train.py --config baseline_er_status.yaml --tag uni_v1
```

내부 동작:
1. `git rev-parse HEAD`로 commit_hash 자동 추출
2. 변경된 스크립트 scp 업로드
3. 서버에서 실행 (`--commit_hash` 자동 포함)
4. 완료 후 결과 요약 출력

---

### 제안 3. 하네스 — `agents/modeling/` 새 파일 생성 시 schemas 리마인더

**배경:** 새 Python 파일 작성 시 schemas를 참조하지 않아 발생한 문제입니다.

**기능:** `agents/modeling/` 아래에 `.py` 파일이 새로 생성될 때 자동으로 관련 schemas를 안내합니다.

```
[schemas 리마인더]
새 파일 감지: agents/modeling/baselines/attention_mil.py
참조 필요: schemas/hypothesis.schema.json, schemas/critic_report.schema.json
출력 형식을 schema에 맞춰 설계한 뒤 구현하세요.
```

---

### 우선순위 요약

| 순위 | 제안 | 팀 적용 범위 | 즉시 효과 |
|---|---|---|---|
| 1 | `/validate-experiment` | 모든 팀원 (Critic 전 필수 단계) | Critic FAIL 사전 차단 |
| 2 | `/run-experiment` | sjpark (서버 실행 반복 감소) | 실행 오류 방지 |
| 3 | 하네스 (schemas 리마인더) | 모든 팀원 | 장기 예방 |

---

## 다음 단계

1. **kkkim GPU 슬롯 확보 → UNI 임베딩 완료 (~37시간)** — 완료되면 즉시 아래 명령 실행
2. **jamie split_policy_v0 서명** — 브랜치 push 대기 중
3. **실제 AUC 측정** — dummy `0.60` vs UNI `>?` 비교로 가설 첫 검증

```bash
python train.py --config ... --tag uni_v1 --commit_hash $(git rev-parse HEAD)
```

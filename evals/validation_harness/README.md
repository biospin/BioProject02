# BIOP02 검수 하네스 (validation_harness) — BIOP02-129

BIOP01 `evals/reproducibility_pilot` 골격을 **벤치마킹 이식**한 것이다. 복사가 아니다: 골격(러너·control-vs-mutated 델타·음성대조·정직 보고)만 재사용하고, **mutation 과 detector 는 BIOP02 도메인**으로 다시 정의했다.

재는 것은 하나다 — **"BIOP02 실무자가 저지를 법한 실수를 심었을 때 우리 게이트가 실제로 잡는가?"**

```
python3 evals/validation_harness/run_validation.py             # 전체
python3 evals/validation_harness/run_validation.py --case split_leak_patient
python3 evals/validation_harness/run_validation.py --strict    # 구멍 있으면 exit 1
```

## 1. 집안 스타일과의 차이 (의도적)

| | critic_pilot / citation_verifier | 이 하네스 |
|---|---|---|
| mutation 대상 | **scorer 함수**(레지스트리 몽키패치) | **데이터·산출물**(split.csv, critic_report, 스코어보드) |
| 재는 것 | 케이스가 스코어러를 구속하는가 | 게이트가 실무 실수를 구속하는가 |
| detector 호출 | in-process import | **CLI 서브프로세스**(종료코드·보고서가 계약이므로) |

split 누수·수치 드리프트·critic 위조는 코드가 아니라 **데이터에서** 발생하는 실패다. 따라서 데이터 mutation 이라야 그 게이트를 실제로 시험한다.

## 2. 판정 어휘

| 판정 | 뜻 |
|---|---|
| `CAUGHT` | control 통과 + mutated 거부 = 게이트가 이 실수를 구속함 |
| `SURVIVED` | mutated 를 통과시킴 = **게이트 구멍** (이 하네스의 실패 조건) |
| `VACUOUS` | control 에서도 아무것도 검사하지 않음 = 통과가 무의미 |
| `BROKEN` | control(무결)에서 실패 = 오탐 |
| `NOT_TESTED` | 실행 못 함 — 정직 기록(방법론 §10). 없는 척하지 않는다 |

## 3. 수행 기록 (2026-08-06, 이건규)

**적발 3 / 게이트 구멍 3 / 미검사 2 (총 8)**

| 케이스 | detector | 판정 | 내용 |
|---|---|---|---|
| `split_leak_patient` | verify_split_integrity.py | ✅ CAUGHT | test 환자를 train 에도 삽입 → `patient-level leakage 발견` assert 로 차단 |
| `split_leak_site` | verify_split_integrity.py | ✅ CAUGHT | test 기관 환자를 train 에 삽입 → `site-level leakage 발견` assert 로 차단 |
| `manuscript_number_drift` | check_number_drift.py --strict | ✅ CAUGHT | 스코어보드 0.939→0.9233(정본 부재값) → `--strict` 차단 |
| `split_drop_column` | verify_split_integrity.py | ❌ **SURVIVED** | `split` 컬럼을 지우면 전 행 스킵 → **검사행 0 으로 통과** |
| `real_manifest_contract` | verify_split_integrity.py | ⚠️ **VACUOUS** | 실물 `embedding_manifest_*.csv` 에 `split` 컬럼이 없어 **아무것도 검사하지 않고 통과** |
| `critic_report_forgery` | auto_review_gate.py | ❌ **SURVIVED** | 7항목을 증거 없이 전부 `pass` 로 위조해도 통과 |
| `operating_point_tamper` | — | `NOT_TESTED` | operating-point 산출물(BIOP02-124) 미생성 |
| `citation_fabrication` | — | `NOT_TESTED` | `evals/citation_verifier` 가 이미 커버(중복 방지) |

### 3-1. 발견된 게이트 구멍 (실행 결과, 추정 아님)

1. **★ `verify_split_integrity.py` 의 공허한 통과** — 입력 CSV 에 `split` 컬럼이 없으면 모든 행을 `continue` 로 건너뛰고 "무결"로 통과한다. 그런데 **도구 헤더가 사용법으로 제시하는 `embedding_manifest_*.csv` 에 정확히 그 컬럼이 없다**(실측: `case_id, slide_id, embedding_path, embedding_model, file_id`). 즉 문서대로 실행하면 누수 검사가 **작동하지 않는데 통과처럼 보인다**. 실무자가 이 통과를 근거로 삼으면 위험하다.
   - 권고: 필수 컬럼 부재 시 **명시적 실패**(0행 검사 시 error), 또는 `split.csv` 를 정본 입력으로 고정.
2. **`auto_review_gate.py` 는 증거 없는 pass 를 막지 않는다** — 7항목 `status: pass` + `evidence: []` 를 통과시킨다. 보고서의 주장과 증거파일을 대조하는 게이트가 커밋돼 있지 않다.
   - 권고: `evidence` 가 비었거나 참조 경로가 없으면 `needs_human` 이상으로 강등.

### 3-2. 어댑터가 필요했던 detector 계약 차이 (실측)

- `verify_split_integrity.py` 는 실패를 **bare `assert`** 로 알린다 → `AssertionError`·exit 1 이고 **보고서 JSON 이 기록되지 않는다**. 또한 `python -O` 에서는 assert 가 제거되어 조용히 통과하므로 이 하네스는 `-O` 를 쓰지 않는다.
- `auto_review_gate.py` 는 **verdict 와 무관하게 항상 exit 0** 이다 → 종료코드가 아니라 `gate_report.json` 을 읽어 판정한다.

### 3-3. 정직 메모 — 처음 돌렸을 때 틀렸던 것

`manuscript_number_drift` 는 최초 실행에서 `SURVIVED` 로 나왔으나 **하네스 쪽 결함**이었다. (a) 위조값 0.988 이 정본 JSON 에 실재해 도구가 "알려진 값"으로 통과시킨 것이 정상 동작이었고, (b) 변조 위치가 prose 여서 도구가 문서화한 v1 범위(endpoint 1:1 행 표) 밖이었다. 위조값을 정본 부재값(0.9233)으로, 위치를 스코어보드 표 행으로 바꾸자 `CAUGHT` 가 되었다. **게이트를 탓하기 전에 mutation 이 공정한지 먼저 확인해야 한다**는 사례로 남긴다.

## 4. 안전장치

- 모든 mutation 은 **임시 디렉터리**에서 수행한다. 정본을 건드리는 유일한 케이스(`manuscript_number_drift`)는 `try/finally` 로 원본을 복원하며, 실행 후 `git status` 가 깨끗함을 확인했다.
- 실행에 GPU·대용량 데이터가 필요 없다(수 초).

## 5. 남은 것

- `operating_point_tamper`: BIOP02-124 산출물이 나오면 케이스 추가.
- 위 3-1 의 두 구멍은 **도구 수정 사안**이므로 별도 티켓/PR로 분리한다(이 하네스는 진단까지).
- 참고: 티켓이 인용한 BIOP01 경로(`pipeline/hspc-velocity-benchmark/evals/validation_harness/`, `cases.yaml`, `run_validation.py`, `check_claims_ledger.py`)는 실재하지 않아, 실제 참조본 `BioProject01/evals/reproducibility_pilot/`(JSON 케이스 + `run_pilot.py`/`mutation_check.py`)을 기준으로 이식했다.

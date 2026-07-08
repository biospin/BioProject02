# sjpark — Sprint 1 진행 공유
### 2026-06-05 스터디 발표

> 박세진 (sjpark) | Modeling Agent

---

## 🎯 우리가 증명하려는 것

> **H&E 슬라이드 이미지만 보고**  
> **유방암의 분자 특성(ER 양성 여부)을 예측할 수 있는가?**

- IHC 검사 없이 이미지만으로 분자 아형 추론
- 가능하다면 → 임상적으로 큰 가치

**지금 단계:** 가설 검증 전. "실제 데이터 도착 즉시 실험할 수 있는 파이프라인 완성"이 목표

---

## 📦 Sprint 0 회고 — 무엇을 준비했나

**Sprint 0 (5/12–5/22)의 의미:** 실험을 시작하기 위한 기반 구축. 가설 검증이 아닌 "측정 도구 제작" 단계.

| 역할 | 완료한 것 |
|---|---|
| braveji | JIRA/GitHub/Confluence 연결, AGENTS.md v0.2, 스토리지 비교안 |
| jamie | TCGA-BRCA manifest CSV, 샘플 WSI 1장 경로 공유 |
| kkkim | setup.sh, tile_wsi.py (Otsu + MPP 보정), extract_uni.py, extract_dummy.py, 1-slide pilot |
| sjpark | modeling 환경 셋업, SlideMLP 스켈레톤, 3 trivial baseline, eval_metrics.md |
| gglee | Critic checklist v1 (7항목), critic_report.schema.json |
| kkkim | hypothesis.schema.json v0.1 |

**1-slide pilot 결과 (kkkim):**
```
TCGA-3C-AALI (Aperio 40×, 1.6GB)
  타일링: 5.6초 / 5,000 tiles (14,198 중 cap)
  UNI 임베딩: 125.6초 / 20MB
  → 300장 전체 추산: 약 10시간
```

**Sprint 1 준비 완료 여부:**

| 항목 | 상태 |
|---|---|
| HF 모델 5종 승인 (UNI/CONCH 등) | ✅ 완료 |
| 배치 임베딩 파이프라인 (`run_batch_embedding.py`) | ✅ 완료 |
| MLP + baseline 코드 | ✅ 완료 |
| kkkim manifest 형식 지원 | ✅ 완료 |
| GPU 슬롯 확보 | ⏳ 대기 중 |
| jamie split_policy_v0 lock | ⏳ 대기 중 |

→ 코드는 모두 준비됐고, **두 가지 외부 조건**이 충족되면 즉시 실제 AUC 산출 가능

---

## 🏃 Sprint 1 — 팀 전체 분담

```
jamie    → 환자 분리 (split_policy_v0 lock)
kkkim    → TCGA-BRCA 1010장 tiling + UNI 임베딩 추출
sjpark   → ER status MLP + 3 trivial baseline → AUC 산출   ← 여기
kkkim    → sjpark 결과 Critic 리뷰                          ← Week 10 변경
braveji  → 실험 추적 도구 + experiments/ 표준 수립
jhans    → DepMap/GDSC 스키마 초안 (치료 가설 연결 준비)
```

> **sjpark 역할 요약:** kkkim의 tile 임베딩(5000×1024)을 입력받아 슬라이드 단위 mean-pooling 후 MLP로 ER 이진분류.  
> 3종 trivial baseline(random / majority / mean_embed)과 AUC를 비교해 "H&E morphology가 ER 예측에 실제 유효한가"를 수치로 판단.  
> MLP > mean_embed baseline → 비선형 패턴 존재 증거. 이후 Attention MIL로 "어떤 타일이 예측에 중요한가"까지 확장.

> **jhans 역할 요약:** sjpark의 phenotype 예측 결과를 치료 가설로 변환하는 단계.  
> ER+/- 예측 → DepMap/GDSC 세포주 약물 감수성 데이터와 연결 → "CDK4/6 inhibitor 유효 가능성" 같은 ranked hypothesis 생성.  
> 단, 세포주 기반 데이터이므로 `claim_level: hypothesis_only` 필수.

**Sprint 1 핵심 deliverables:**

| 담당 | 목표 | 상태 |
|---|---|---|
| kkkim | TCGA-BRCA 전체 tiling + UNI 임베딩 추출 | 🔄 GPU 슬롯 대기 중 |
| sjpark | ER status MLP + 3 baseline 비교 (AUC) | 🔄 dummy_v1 완료, UNI 대기 |
| jamie | split_policy_v0 patient-level lock | 🔄 브랜치 push 대기 |
| braveji | 실험 추적 도구(wandb/MLflow) + experiments/ 표준 | ✅ 완료 |
| jhans | DepMap/GDSC 스키마 초안 | ✅ 완료 |

**Sprint 1 목표:** "H&E 이미지로 ER 예측이 되는가?" 첫 번째 숫자 산출

---

## 🧑‍💻 sjpark 역할

| 티켓 | 내용 |
|---|---|
| BIOP02-39 | ER status binary MLP 학습 → AUC 산출 |
| BIOP02-40 | Random / Majority / MeanEmbed 3종 baseline 비교 |

**핵심 판단 기준:**

```
MLP AUC > MeanEmbed baseline?
  YES → H&E에서 비선형 패턴 존재 (가설 지지)
  NO  → 선형 분류와 다를 바 없음 (모델 개선 필요)
```

---

## ⚡ 현황 — GPU 없이 선행 진행

kkkim이 GPU 슬롯 대기 중 → dummy embedding으로 파이프라인 먼저 연결

```
[지금]
  kkkim: 1010장 다운로드 완료, GPU 슬롯 확보 후 임베딩 시작 예정
  sjpark: dummy_v1 파이프라인 완성 대기 중

[UNI 완료 후]
  python train.py --tag uni_v1 --commit_hash $(git rev-parse HEAD)
```

kkkim이 dummy manifest(1010장)를 준비해줘서 파이프라인 검증 선행 가능

---

## 🔄 시행착오 ① — Sprint 0 재작업 논란

**비평:** "smoke test가 kkkim 실제 파일을 쓰지 않았다"

**재작업 후 결론:** 불필요했다

| 완료 기준 | 상태 |
|---|---|
| dummy 데이터로 코드 1회 실행 | ✅ 처음부터 충족 |
| 실제 .npy 파일 로딩 검증 | Sprint 1 영역 (BIOP02-39) |

**긍정적 부산물:** MeanEmbedBaseline 단일 클래스 버그 발견·수정

> 💡 **Lesson:** Sprint Done Definition을 JIRA 티켓에 명시해야 한다

---

## 🔄 시행착오 ② — 레이블 형식 불일치

| | sjpark 코드 | kkkim manifest |
|---|---|---|
| 가정 | 숫자 `0` / `1` | TCGA 원본 `"Positive"` / `"Negative"` |
| 결과 | `float("Positive")` → ValueError | — |

```python
# 수정
LABEL_MAP = {"positive": 1.0, "negative": 0.0}
# + Equivocal / Indeterminate 자동 제외
```

> 💡 **Lesson:** agent 간 중간 데이터 형식을 `schemas/`에 사전 정의해야 한다  
> → Sprint 2 전 `schemas/embedding_manifest.schema.json` 필요

---

## 🔄 시행착오 ③ — split 미할당 510장

```
초기: 1010장 중 train 350 / val 75 / test 75 (500장) + 미할당 510장
원인: 500장 split 생성 후 1010장으로 확장할 때 split 재생성 누락
해결: kkkim이 1010장 전체 재생성

최종: train 706 / val 151 / test 153
```

> 💡 **Lesson:** manifest 규모 확장 시 split 미할당 행 사전 검증 필요

---

## 🔄 시행착오 ④ — schemas 미참조 (핵심)

**BIOP02-32 작성 시 AGENTS.md만 참조, schemas/ 미확인**

**결과:** kkkim Critic 리뷰에서 7건 발견

| 구분 | 항목 | 처리 |
|---|---|---|
| FAIL | AUC/AUPRC/BalAcc null 저장 | val set 계산 추가 |
| FAIL | claim_level, critic_status 없음 | hypothesis_only, pending 추가 |
| 추가 | schema_version, created_at 없음 | 추가 |
| 추가 | predictions.npy 미저장 | val 예측값 저장 |
| 추가 | config.yaml 미복사 | 자동 복사 추가 |
| 추가 | 실험 디렉토리 구조 위반 | `experiments/sjpark/<task>_<tag>/` |
| 추가 | commit_hash "unknown" | `--commit_hash` 인자 추가 |

> 💡 **Lesson:** 새 코드 작성 전 `schemas/`를 먼저 확인하고 설계할 것

---

## 📊 현재 결과 (dummy 기준)

> ⚠️ 랜덤 노이즈 데이터 — 수치 자체는 의미 없음, **파이프라인 검증 목적**

**MLP (BIOP02-39)**

```
train=706 / val=151 / 10 epochs / 54.5s
AUC: 0.6036 / AUPRC: 0.8407 / BalAcc: 0.517
→ overfitting 패턴 (dummy 특성, 예상대로)
```

**3 Trivial Baseline (BIOP02-40)**

| Baseline | AUC | 의미 |
|---|---|---|
| random | 0.568 | 무작위 예측 |
| majority | 0.500 | 항상 ER+ |
| mean_embed | 0.607 | 선형 분류기 최솟값 |

**UNI 임베딩 후 기대:** MLP AUC > 0.7, mean_embed 상회 여부로 가설 첫 검증

---

## ✅ Critic 리뷰 결과

| 티켓 | Critic | 결과 |
|---|---|---|
| BIOP02-39 | kkkim | conditional_pass |
| BIOP02-40 | kkkim | conditional_pass |

**BIOP02-39:** FAIL 2건 수정 완료 / dummy 조건 N/A 3건 → UNI 후 재리뷰  
**BIOP02-40:** PASS 전항목 / 권고(run_command 재현성) 반영 완료

---

## 🤝 braveji님 template 업데이트 제안

**발견:** `experiments/template/metrics.json`에 schema required 필드 4개 누락

```json
"schema_version": "0.1",
"created_at": "<ISO 8601 UTC>",
"claim_level": "hypothesis_only",   ← DRP 금지 원칙 코드 강제
"critic_status": "pending"           ← Critic pass 전 공유 차단
```

**braveji님 즉시 반영** ✅ → 이후 다른 팀원들은 template 참고만 해도 schemas 준수 가능

---

## 💡 회고 기반 제안

### `/validate-experiment` 스킬 (우선순위 1)

Critic 리뷰 전에 사전 검증 → FAIL 예방

```
/validate-experiment experiments/sjpark/er_status_uni_v1/
→ schema_version ✅ / claim_level ✅ / predictions.npy ✅ / ...
```

### `/run-experiment` 스킬 (우선순위 2)

서버 실행 자동화 — commit_hash, scp, ssh 한 번에

```
/run-experiment --script train.py --config ... --tag uni_v1
```

### 하네스 — schemas 리마인더 (우선순위 3)

새 `.py` 파일 생성 시 `schemas/` 참조 안내 자동 출력

---

## 🚀 다음 단계

```
현재                      다음
─────────────────────────────────────────
kkkim GPU 슬롯 대기    →  UNI 임베딩 완료 (~37h)
jamie split 미서명     →  brancch push 후 서명
dummy AUC: 0.60        →  uni_v1 실행 → 실제 AUC
                           MLP > baseline?
                           → 가설 첫 검증 ✓
```

**실행 명령 (UNI 완료 후 즉시):**
```bash
python train.py --config baseline_er_status.yaml \
  --tag uni_v1 --commit_hash $(git rev-parse HEAD)
```

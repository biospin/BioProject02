# SpatialPathoAgent Anti-Patterns v1

> 이 파일은 과거 리뷰·디버깅에서 반복적으로 발견된 오류 패턴을 기록합니다.  
> Critic 리뷰 시 이 패턴을 먼저 확인하면 reject 사유의 80%를 사전에 차단할 수 있습니다.

---

## AP-01 | Slide/Tile 단위 Split (Data Leakage)

**패턴:** 환자가 아닌 슬라이드·타일 단위로 train/val/test를 나눔  
**결과:** AUC가 5–30% 부풀림 (Yagis 2021: 29–55% 과대평가)  
**감지:**
```python
# train/val에 동일 case_id가 존재하면 즉시 reject
overlap = set(train['case_id']) & set(val['case_id'])
assert len(overlap) == 0, f"Leakage detected: {overlap}"
```
**수정:** `split_policy_v0.md` §1 기준 patient-level split 재실행  

---

## AP-02 | Baseline 누락 (Baseline Missing)

**패턴:** trivial baseline(random/subtype-only/pixel-mean) 없이 모델 AUC만 보고  
**결과:** 모델이 실제로 유용한지 알 수 없음  
**감지:** `metrics.json`에 `baseline_random_auc`, `baseline_subtype_auc`, `baseline_pixelmean_auc` 필드 누락  
**수정:** `agents/modeling/baselines/mlp.py`의 trivial baseline 3종 실행 후 `metrics.json`에 추가  

---

## AP-03 | DRP 프레이밍 (Drug Response Prediction Framing)

**패턴:** 결과를 "drug response prediction" / "personalized therapy" 로 표현  
**결과:** 프로젝트 절대 금지 위반 → 자동 reject  
**감지:**
```bash
grep -ri "drug response prediction\|personalized therapy\|patient-specific.*treatment" .
```
**수정:** "hypothesis-only therapeutic candidate generation"으로 교체  

---

## AP-04 | ICI 추천 (ICI / Pembrolizumab Recommendation)

**패턴:** TCGA 세포주 전이에서 PD-1/PD-L1 억제제(Pembrolizumab 등) 추천  
**결과:** cell-line → patient transfer가 ICI에서는 극히 부정확 (tumor microenvironment 무시) → reject  
**감지:** `critic_report.json`의 `biological_plausibility.notes`에서 ICI 언급 확인  
**수정:** ICI는 전임상 가설 목록에서 제외  

---

## AP-05 | Self-Reference (Critic 자기 검토)

**패턴:** 실험 owner가 자신의 critic_report.json을 작성  
**결과:** Owner ≠ Reviewer 원칙 위반 → 해당 report 무효  
**감지:** `critic_report.json`의 `reviewer == owner`  
**수정:** AGENTS.md §4 cross-review pairing 표에 따라 지정 Critic에게 요청  

---

## AP-06 | Raw WSI 영구 보관

**패턴:** 임베딩 추출 후 raw `.svs` 파일을 삭제하지 않고 HDD에 계속 보관  
**결과:** 14.6 TB HDD 소진 → 다른 팀원 작업 불가  
**감지:** `~/data/` 용량 점검, `.svs` 파일 존재 확인  
**수정:** `stream_download_embed.py`의 `--delete-raw` 옵션 사용. 영구 보존 대상: `manifest / coords.npy / embeddings / logs`만  

---

## AP-07 | Claim 과장 (Over-claiming)

**패턴:** 단일 코호트 결과를 "predicts clinical outcome in BRCA patients"로 표현  
**결과:** Claim-level check (#7) reject  
**감지:** `summary` 또는 metrics 해석 텍스트에서 "predicts", "diagnoses", "identifies" 동사 사용  
**수정:** "suggests", "is associated with", "provides hypothesis" 수준으로 완화  

---

## AP-08 | CPTAC 학습 노출

**패턴:** CPTAC-BRCA 데이터를 val/튜닝에 사용  
**결과:** 외부 검증 오염 → Sprint 3 cross-dataset 결과 무효화  
**감지:** config.yaml의 `val_cohort` 또는 `dataset` 필드에 "cptac" 포함  
**수정:** CPTAC는 `test_external`로만 사용, 학습/튜닝 파이프라인에서 완전 분리  

---

## AP-09 | commit_hash 누락

**패턴:** `metrics.json`에 `commit_hash: null` 또는 `"unknown"`  
**결과:** 실험 재현 불가 → experiments registry 등록 거부  
**감지:**
```bash
python -c "import json; d=json.load(open('metrics.json')); assert d['commit_hash'] not in [None,'unknown','']"
```
**수정:** 학습 스크립트에 아래 코드 추가:
```python
import subprocess
commit = subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
metrics['commit_hash'] = commit
```

---

## AP-10 | 임베딩 모델 미기재

**패턴:** `metrics.json`의 `embedding_model`이 `null` 또는 `"uni"` (버전 불명)  
**결과:** 어떤 임베딩으로 학습했는지 추적 불가  
**감지:** `embedding_model` 필드 확인  
**수정:** `"uni_v1"` / `"conch_v1"` / `"exaone_path_v2"` 형식으로 버전까지 명시  

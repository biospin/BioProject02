# 인코더 ablation — 파운데이션 모델 선택이 표현형 예측을 얼마나 좌우하는가

- 실행일: 2026-08-30 (v1), 2026-08-31 재실행 (v2)
- 실행자: kkkim
- JIRA: BIOP02-149
- 상태: **v1은 reject(폐기), v2가 정본.** v2는 Critic 재검토 대기.

---

## ⚠️ v1은 폐기한다 (2026-08-31)

v1(`bp02_encoder_ablation.json`, `bp02_encoder_ablation_ci.json`)은 적대적 Critic 리뷰에서
**reject** 판정을 받았다(`critic_report.json`). 사유 네 가지 중 결정적인 것은 분할이다.

- **v1은 잠긴 분할을 쓰지 않았다.** 정본은 `agents/data/manifests/split_policy_v0_folds.json`
  (train 707 / val 152 / test 151, `split_hash=5995f29d3978b831`)인데, v1은 서버의
  `split_policy_v1.csv`를 써서 test 153을 냈다. 선행 결과와 비교가 불가능하다.
- `metrics.json`의 `split_hash` 칸에 해시가 아니라 파일명을 적어 넣어, 자동 게이트가 이
  불일치를 잡지 못했다.
- trivial baseline이 하나도 없었다.
- PAM50이 Normal-like를 포함한 5-class로 돌았다(정책 §92는 4-class).
- 다중비교 보정이 없었다.

**v1의 헤드라인이었던 "염색 정규화가 ER에서 이득을 준다"는 v2에서 재현되지 않는다.**
분할을 바로잡자 uni_v1 0.809 → 0.774, uni_stainnorm_v1 0.892 → 0.796으로 내려갔고
차이도 유의하지 않다. v1 수치를 어디에도 인용하지 않는다.

---

## v2: 잠긴 분할로 재실행

### 방법

- **분할**: `split_policy_v0_folds.json` 정본 그대로. hash `5995f29d3978b831`.
  train 707 / val 152 / test 151 (라벨 결측으로 과제별 유효 수는 아래 표).
- **인코더**: uni_v1(1024), uni_stainnorm_v1(1024), conch_v1(512), exaone_v2(768).
  case 단위 평균 임베딩(`_cache/*_casemean.npz`).
- **라벨**: ER/PR/HER2는 biotab IHC(positive/negative만), PAM50은 **4-class**
  (LumA, LumB, HER2, Basal. Normal-like 제외 — 정책 §92).
- **프로브**: StandardScaler → LogisticRegression(class_weight=balanced, max_iter=5000).
- **기준선**: random_uniform, prevalence(stratified), majority, embedding_mean_1d.
- **불확실성**: test 환자 2,000회 부트스트랩. 쌍대 차이는 같은 재표집 인덱스로 계산(paired).
- **다중비교**: 24개 비교에 Benjamini-Hochberg 보정.

재현: `python rerun_locked.py` (레포 안에서 실행, 서버 불필요)

### 결과 (test AUROC)

| 인코더 | dim | ER (n=151) | PR (n=149) | HER2 (n=90) | PAM50 4c (n=131) |
|---|---|---|---|---|---|
| uni_v1 | 1024 | 0.774 | 0.732 | 0.552 | 0.719 |
| uni_stainnorm_v1 | 1024 | 0.796 | 0.707 | 0.498 | 0.737 |
| conch_v1 | 512 | 0.746 | 0.745 | 0.564 | **0.783** |
| exaone_v2 | 768 | **0.828** | **0.761** | **0.562** | 0.747 |
| *random/majority* | — | *0.500* | *0.500* | *0.500* | *0.500* |
| *embedding_mean_1d* | 1 | *0.406* | *0.435* | *0.305* | *0.435* |

### 쌍대 비교: **24건 중 BH 보정 후 유의 0건**

가장 작은 q값 셋은 이렇다.

| 비교 | Δ | 95% CI | p | q(BH) |
|---|---|---|---|---|
| PAM50: conch_v1 > uni_v1 | +0.063 | [0.017, 0.113] | 0.004 | 0.096 |
| ER: exaone_v2 > conch_v1 | +0.082 | [0.009, 0.164] | 0.026 | 0.312 |
| ER: exaone_v2 > uni_v1 | +0.054 | [−0.026, 0.141] | 0.198 | 0.679 |

## 읽는 법

**1. 인코더 선택은 이 표본에서 결론을 바꾸지 않는다.** 보정 후 유의한 차이가 없다.
Paper C에서 UNI를 주모델로 쓰는 선택은 성능 우위가 아니라 다른 근거(가용성, 선행 사용,
문서화)로 정당화해야 하며, 결론이 인코더에 의존하지 않는다고 말할 수 있다.
이것이 리뷰어의 "왜 이 인코더인가"에 대한 정직한 답이다.

**2. 염색 정규화의 이득은 확인되지 않았다.** ER에서 +0.022로 방향은 같으나 CI가 0을
포함한다. 원고 methods의 "염색 정규화 미적용" 서술과 충돌하지 않는다.

**3. HER2는 네 인코더 모두 우연 수준이다**(0.498~0.564, n=90). 형태에서 HER2를 읽어내지
못한다는 뜻이고, Paper C의 음성 앵커 서사와 방향이 같다.

**4. 임베딩이 밝기·크기 대리 변수가 아니다.** embedding_mean_1d 기준선이 모두 0.5 미만이라,
표현이 단순 강도 정보로 환원되지 않는다.

## 한계

- 평균 풀링에 선형 프로브까지만 본 값이다. attention MIL의 순위와 다를 수 있다.
- **exaone_v2는 인코더만 다른 것이 아니다.** 내부 타일링과 Macenko 정규화를 거친 별도
  파이프라인이라 차이를 인코더 단독으로 귀속하면 안 된다.
- `uni_stainnorm_v1`의 추출 스크립트가 레포에 없어 정규화 방법과 기준 이미지, 타일 좌표
  동일성을 확인하지 못했다.
- PAM50 라벨 소스(`tcga_brca_pam50_computed.csv`)가 무엇으로 계산되었는지 확인하지 못했다.
  정책 §220은 cBioPortal PAM50을 1순위로 지정하므로 소스 대조가 필요하다.
- 단일 test fold다. val fold나 교차검증 반복은 하지 않았다.
- `predictions.npy`와 `config.yaml`을 남기지 않았다(리포 아티팩트 계약 미충족).

## 다음

1. `uni_stainnorm_v1` 추출 스크립트 확보 후 정규화 조건 확인
2. PAM50 라벨 소스를 cBioPortal 정본으로 교체해 재계산
3. attention MIL로 같은 비교 반복
4. Critic 재검토(담당: jamie 또는 braveji) → 통과 시 Paper C ablation 절 반영

## 파일

- `rerun_locked.py`, `results_locked_v2.json` — **v2 정본**
- `_cache/` — case 평균 임베딩과 라벨(서버 반납 대비 회수본). **미커밋·로컬 보관**(TCGA 임상 원본 포함, 저장소 공개). 무결성은 `_cache_manifest.sha256` 으로 대조한다.
- `_cache_manifest.sha256` — `_cache/` 6파일 sha256
- `critic_report.json` — v1에 대한 적대적 리뷰(reject)
- `bp02_*.py`, `bp02_*.json`, `metrics.json`, `gate_report.json` — v1 기록(폐기, 이력 보존용)

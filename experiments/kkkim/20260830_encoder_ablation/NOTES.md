# 인코더 ablation — 파운데이션 모델 선택과 염색 정규화가 표현형 예측을 얼마나 좌우하는가

- 실행일: 2026-08-30
- 실행자: kkkim
- 상태: **critic_status: pending** — Critic 검토 전이며 공유·발표·원고 반영 전 게이트를 거쳐야 한다.
- JIRA: 미배정 (기존 BIOP02-48 `20260701_uni_vs_conch`의 확장에 해당)

## 왜 했나

기존 BIOP02-48은 UNI와 CONCH를 ER·PR에서 `StratifiedGroupKFold(5)`로 비교한 sanity 수준이었다.
Paper C 리뷰에서 "왜 이 인코더인가", "염색 정규화는 왜 하는가"가 나올 것이 확실하므로,
보유한 인코더 4종을 **프로젝트 분할 정책의 고정 test 분할**로, **PAM50까지 포함해** 한 프로토콜에
놓고 비교했다.

## 방법

- 인코더: `uni_v1`(1024), `uni_stainnorm_v1`(1024), `conch_v1`(512), `exaone_v2`(768)
  - 경로: `~/data/embeddings/biop02/tcga/<encoder>/`
  - exaone_v2는 npz의 `patch_mean`을 사용(사전 계산). 나머지는 타일 임베딩 평균.
- 집계: 타일 평균 → 슬라이드 → case 평균 (다중 슬라이드 환자는 슬라이드 평균의 평균)
- 라벨: `clinical_patient_brca.txt`의 `er/pr/her2_status_by_ihc`(positive/negative만),
  `tcga_brca_pam50_computed.csv`의 `pam50_subtype`(test 20건 미만 클래스 제외)
- 분할: `split_policy_v1.csv` (case 단위, train 706 / val 151 / test 153). 학습 train, 보고 test.
- 프로브: `StandardScaler` → `LogisticRegression(class_weight="balanced", max_iter=5000)`
- 불확실성: test 환자를 1,000회 재표집한 부트스트랩. 인코더 쌍 차이는 **같은 재표집 인덱스**로
  계산(paired)해 차이의 95% 구간을 냈다. 인코더별 test 환자 집합이 동일한지 코드에서 검증한다.

재현: `bp02_encoder_ablation.py` → `bp02_bootstrap.py` (환경 `spatialpatho`)

## 결과 (test 분할, AUROC. 이진은 양성확률, PAM50은 OvR macro)

| 인코더 | dim | ER | PR | HER2 | PAM50 |
|---|---|---|---|---|---|
| uni_v1 | 1024 | 0.809 [0.725, 0.882] | 0.787 [0.710, 0.858] | 0.685 [0.529, 0.824] | 0.710 [0.660, 0.753] |
| uni_stainnorm_v1 | 1024 | **0.892** [0.825, 0.946] | 0.790 [0.709, 0.865] | 0.692 [0.546, 0.824] | 0.721 [0.667, 0.767] |
| conch_v1 | 512 | 0.874 [0.793, 0.942] | **0.798** [0.716, 0.876] | 0.606 [0.446, 0.750] | 0.722 [0.665, 0.770] |
| exaone_v2 | 768 | 0.828 [0.732, 0.909] | 0.730 [0.629, 0.826] | **0.749** [0.588, 0.888] | **0.746** [0.691, 0.800] |

n_test = 153 (HER2는 라벨 결측으로 102)

### 차이의 95% 구간이 0을 포함하지 않는 쌍

- **ER**: `uni_stainnorm_v1 > uni_v1`, `uni_stainnorm_v1 > exaone_v2`
- **HER2**: `exaone_v2 > conch_v1`
- **PR·PAM50**: 없음

## 읽는 법

1. **염색 정규화의 이득이 ER에서 실재한다.** 같은 UNI 인코더인데 정규화판이 0.083 높고
   차이의 구간이 0을 넘지 않는다. 전처리 선택을 근거로 방어할 수 있다.
2. **인코더 선택은 대체로 이 표본에서 판정 불가다.** PR과 PAM50은 네 인코더가 모두 겹친다.
   "가장 좋은 인코더"를 주장하지 말고, 표본 크기의 한계를 명시하는 편이 정확하다.
3. HER2는 n=102에 구간이 넓어(±0.15) 어떤 결론도 탐색적이다.

## 한계 (원고에 반드시 함께 적을 것)

- 평균 풀링 + 선형 프로브까지만 본 값이다. attention MIL의 순위와 다를 수 있다.
- exaone_v2만 사전 계산된 `patch_mean`을 써서 집계 경로가 완전히 동일하지 않다.
- 단일 test 분할이다. 분할을 바꾼 반복은 하지 않았다.
- 부트스트랩은 test 환자 재표집만 반영하며, 학습 변동은 포함하지 않는다.
- **Critic 미통과.** 이 수치는 팀 내부 검토 전이므로 외부(발표·면접·공개 저장소) 인용 금지.

## 다음

- attention MIL로 같은 비교를 반복해 순위가 유지되는지 확인
- val 분할에서도 같은 방향인지 대조(현재 test만 보고)
- Critic 게이트 → JIRA 이슈 배정 → Paper C ablation 절 반영

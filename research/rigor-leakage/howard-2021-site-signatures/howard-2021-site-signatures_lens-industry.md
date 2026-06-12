# Lens: Industry / Engineering — QP site-preserved splitting & reproducibility

## The reusable artifact: PreservedSiteCV
Howard 2021의 실질 산출물은 논문 본문이 아니라 **재사용 가능한 분할 엔진**이다: `github.com/fmhoward/PreservedSiteCV`. 우리에게 중요한 건 결과 숫자가 아니라 이 **fold-assignment 알고리즘을 그대로 들여올 수 있다**는 점.

### 알고리즘 (engineering view)
- **입력**: 각 환자의 `(site, outcome label)`. BIOP02에서는 `(tss_code, ER/PR/HER2/PAM50)`.
- **제약(hard)**: 한 site의 모든 슬라이드는 **정확히 하나의 fold** 에만 — train·val 동시 출현 0건. → tile-level이든 slide-level이든 institutional leakage가 구조적으로 불가능.
- **목적(soft, QP)**: fold별 outcome 분포가 perfect stratification에서 벗어난 편차의 **제곱합(MSE)을 최소화**. 이를 convex/quadratic program으로 풀어 site를 fold에 정수 배정.
- **검증된 성능**: 58개 outcome 중 32개(55%)에서 perfect stratification, 12%만 의미있는 imbalance. 즉 site 격리라는 강한 제약을 걸고도 **class balance를 거의 잃지 않는다** — 단순 무작위 site 배정 대비 명확한 이점.

## Reproducibility / stack 정합성
- 원 논문 stack: **Xception + TensorFlow 2.3.0**, tile 299×299 px @ ~×10. 우리는 FM embedding(UNI/CONCH 등) 기반이라 backbone은 다르지만, **분할 로직은 모델-agnostic** — embedding 단계 앞단(jamie의 manifest/split)에 그대로 끼워 넣으면 된다.
- **Slideflow 주의**: 우리 CLAUDE.md/주변 문헌이 Slideflow를 언급하지만, *이 2021 논문 본문에는 Slideflow가 없다*. Slideflow는 동일 연구진(Dolezal/Pearson)이 **이후에** 만든 별도 파이프라인 패키지이며, preserved-site CV 로직이 거기에 통합되어 있다. 즉 "Howard 2021 = 방법·증명 + PreservedSiteCV repo", "Slideflow = 그 방법을 production화한 후속 툴". 인용 시 둘을 혼동하지 말 것.

## BIOP02 integration plan (engineering)
1. jamie의 manifest에 **`tss_code` 컬럼** 추가 (barcode `TCGA-XX-####`의 `XX` 파싱; 한 줄).
2. PreservedSiteCV의 QP fold-assignment를 `agents/data/`의 split 생성 단계에 포팅 — 입력 `(tss_code, label)`, 출력 `fold_id`. 외부 의존성은 QP solver 하나뿐(cvxpy/quadprog 등).
3. 생성된 fold를 **split_policy_v0에 동결**, `metrics.json`에 fold 정의 해시 기록 → 실험 재현성/감사 추적.
4. CI sanity check: 어떤 site도 train·val에 동시 등장하지 않음을 assert (leakage 회귀 방지).

**요약**: 비용은 작고(컬럼 1개 + QP 1회), 얻는 것은 reviewer-proof한 leakage 방어 + 검증된 class balance. 가성비가 가장 높은 rigor 투자.

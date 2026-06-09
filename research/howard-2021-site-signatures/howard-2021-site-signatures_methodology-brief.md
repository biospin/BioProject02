# Methodology Brief — Split protocol we adopt + site-classifier probe (Exp2)

Derived from Howard et al. 2021 (Nat Commun 12:4423). 이 문서는 BIOP02가 **그대로 채택**하는 분할 프로토콜과 Exp2 probe 설계를 규정한다.

## 1. Split protocol we adopt (split_policy_v0, locked)
**Grouping key**: TCGA barcode의 Tissue Source Site = `tss_code` (`TCGA-XX-####`의 `XX`). 환자 disjoint는 전제, 그 위에 **site disjoint** 추가.

| 단계 | 규칙 |
|---|---|
| 1 | 환자 단위로 슬라이드 묶기 (patient-level, Bussola 2020 전제) |
| 2 | 각 환자를 `tss_code`로 그룹화 |
| 3 | **Default**: site-disjoint folds — 한 site는 한 fold에만. 한 site가 train·val에 동시 등장 시 빌드 실패(hard assert) |
| 4 | **Preferred**: PreservedSiteCV QP로 fold별 ER/PR/HER2/PAM50 class balance 최대화 (MSE 최소화) |
| 5 | fold 정의를 동결, 정의 해시를 모든 `metrics.json`의 `commit_hash` 옆에 기록 |

- Tiling/embedding 파라미터는 우리 기존 설정 유지 (256×256 @ 20×, per-patient cap 5000) — 분할 로직만 site-aware로 교체. (참고: Howard 원본은 299×299 @ ~×10이나 분할은 magnification-agnostic.)
- **Stain normalization은 계속하되 단독 방어로 의존 금지** (Howard 권고 #4: 외부 타당성엔 도움, 그러나 site signature는 못 지움 → 분할이 진짜 방어).

## 2. Site-classifier probe = Exp2
**목적**: 우리 데이터·임베딩에 site signature가 실제로 얼마나 남아 있는지 *정량화*하고, site-aware split이 그것을 무력화함을 *증명*.

**Exp2-A — Site detectability probe**
- FM embedding(UNI/CONCH 등)을 입력으로 **submitting-site 분류기**(softmax/logistic) 학습.
- 지표: one-vs-rest AUROC. Howard 기준선(0.964–0.998)과 비교해 우리 임베딩의 site leakage 강도 보고.
- 해석: 높을수록 embedding이 site를 강하게 인코딩 → site-aware split의 필요성 입증.

**Exp2-B — Random vs site-stratified split 대조 (핵심 reviewer shield)**
- 동일 ER status MLP를 (i) **random/patient-only split** 과 (ii) **site-disjoint(QP) split** 두 방식으로 학습.
- ΔAUROC = random − site-disjoint 를 보고. Howard처럼 **양의 Δ(= random이 부풀려짐)** 가 나오면, site-disjoint 숫자가 우리의 *정직한* 성능임을 입증.
- 추가: ancestry/race를 site-disjoint vs random에서 예측 시도 → site-disjoint에서 chance(≈0.5)로 떨어지는지 확인(Howard BRCA 0.798→0.507 재현 여부) = equity 방어.

**Pass 기준 (Critic #1)**: ER/PR/HER2/PAM50 주요 결과가 **site-disjoint split 하에서** 보고되고, Exp2-B의 Δ가 명시되며, Exp2-A의 residual site-AUROC가 함께 리포트될 것. (Owner≠Reviewer: kkkim 임베딩 결과의 Critic은 jamie 또는 sjpark.)

## 3. Tooling
- Fold 생성: `github.com/fmhoward/PreservedSiteCV` 포팅 (QP solver: cvxpy/quadprog).
- Leakage 회귀 테스트: "no site in both train & val" assert를 split 빌드 + CI에 고정.

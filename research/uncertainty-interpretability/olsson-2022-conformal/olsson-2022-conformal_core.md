# Olsson 2022 — Conformal Prediction for Diagnostic Uncertainty in AI Pathology (Core)

**Citation.** Olsson H, Kartasalo K, Mulliqi N, et al. *Estimating diagnostic uncertainty in artificial intelligence assisted pathology using conformal prediction.* Nature Communications 2022;13:7761. DOI 10.1038/s41467-022-34945-8. PMC9755280. Code: github.com/heolss/Conformal_analyses (Zenodo 10.5281/zenodo.7147740).

## 한 줄 요약 / One-line
**KR.** 병리 AI 예측에 Mondrian inductive conformal prediction(ICP)을 씌워, 분포-무관·유한표본 커버리지 보장 하에 "신뢰할 수 없는" 예측을 자동으로 기권(abstain)시키는 첫 본격 병리 사례.
**EN.** First substantive pathology application of Mondrian inductive conformal prediction (ICP) that, under a distribution-free finite-sample coverage guarantee, automatically *abstains* on untrustworthy predictions instead of forcing a label.

## 무엇을 했나 / What
- **Task & data.** 전립선 생검(STHLM3): 이진 암 검출 + ISUP grading 1–5. 학습 7,788 biopsies(1,192명) — 6,951 train + **837 calibration**(123명). 테스트 3,059 biopsies(676명), 6개 테스트셋(동일 lab → 외부 scanner/lab → 전향 코호트 → 희귀 형태).
- **Model.** 2개 앙상블 × 30 Inception-V3(ImageNet pretrain) → slide-level gradient-boosted trees. CP는 이 베이스 모델 *위에* 후처리로 얹힘 (모델 재학습 불필요).
- **Conformal.** Mondrian(class-conditional) ICP. Nonconformity score = `1 − p(class)`. Calibration 집합의 score 분포로 새 샘플의 p-value를 계산, 유의수준 ε에서 **prediction set**(0·1·다중 라벨)을 산출.

## 핵심 수치 / Key numbers (anchor-verified)
- **암 검출, 동일 lab (Test set 1, n=794), 99.9% 신뢰(ε=0.001):** CP 적용 시 오류 **1/794 = 0.1%** vs 미적용 **14/794 = 2%**. 대신 **175/794 = 22%**를 다중-라벨(=불확실)로 플래그. → *오류 20배↓를 22% 기권으로 교환.*
- **ISUP grading (67% 신뢰):** CP 28% err + 20% 다중 라벨 vs 미적용 33% err.
- **희귀 형태 (Test set 6, n=179):** CP 오류 **2%** vs **25%**, 단 **80%** 플래그 — 분포 밖 입력에서 기권율이 자동으로 치솟음(원하던 행동).
- **외부 scanner drift:** CP가 **49개** 관측만으로 체계적 분포 이동을 검출.

## 왜 작동하나 / Why it works
Coverage 보장은 **exchangeability**만 가정 — 모델·데이터 분포 가정 없음. 따라서 어떤 베이스 분류기에도 부착 가능하고, 보장은 marginal하게 유한표본에서 성립. 분포 이동(외부 scanner)이 발생하면 exchangeability가 깨져 prediction set이 비거나 커지면서 **자동 경보** 역할을 한다.

## BIOP02 함의 / Implication
H&E→BRCA phenotype head 위에 동일 레시피를 얹으면, "확신할 때만 hypothesis 발화"라는 게이트를 **분포-무관 보장**으로 정당화할 수 있다. 특히 HER2-E의 F1 천장 문제를 *틀린 예측을 줄이는* 대신 *불확실한 케이스를 기권*으로 전환해 우회. 단, marginal coverage이므로 subgroup(예: HER2-E)별 conditional validity는 별도 검증 필요. 자세한 레시피는 `_methodology-brief.md`.

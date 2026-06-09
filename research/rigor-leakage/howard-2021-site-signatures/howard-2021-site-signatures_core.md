# Howard et al. 2021 — Site-Specific Digital Histology Signatures (Core)

**Howard FM, Dolezal J, Kochanny S, … Grossman RL, Pearson AT. _Nat Commun_ 12:4423 (2021). doi:10.1038/s41467-021-24698-1**

## One-line claim
TCGA H&E 슬라이드에는 **제출 기관(submitting site)별 디지털 서명(site signature)** 이 각인되어 있고, 이를 deep learning이 거의 완벽하게 읽어내며, 이 신호가 stain normalization·augmentation 후에도 살아남아 생존·돌연변이·병기 예측의 정확도를 **과대평가(leakage)** 하고 환자 **인종/조상(ancestry)** 까지 누설한다.

## Scope (grounded)
- **6개 TCGA 코호트**: BRCA, LUAD, LUSC, COAD/READ, KIRC, HNSC. **>3,000 patients**, 코호트당 약 888–1,006 slides.
- 모델: **Xception** (ImageNet pretrained) + FC(width 500) + softmax. **TensorFlow 2.3.0 / Python 3.8**. Tile = **299×299 px ≈ 302×302 μm (~×10)**.

## Key results (grounded numbers)
1. **Site is trivially detectable from histology alone.** One-vs-rest AUROC **0.964 (LUSC) → 0.998 (KIRC)**. 같은 site를 임상변수만으로 맞히면 평균 0.623 — 즉 이미지가 임상정보보다 훨씬 강하게 site를 누설.
2. **Stain normalization은 site signature를 지우지 못한다.** 모든 정규화 적용 후에도 평균 OVR AUROC **>0.850**. 2차 Haralick texture(특히 **angular second moment**)가 site 간 가장 강하게 다른 채로 남음 — 색 보정으로 못 지우는 구조적 텍스처 batch effect.
3. **표준 CV는 정확도를 인위적으로 부풀린다.** Preserved-site CV로 바꾸면 예측 가능한 feature의 **91.1%** 가 AUROC 하락; 처음 "유의"했던 feature의 **35.7%** 가 site 격리 후 검출 불가로 무너짐. 평균 AUROC 하락 폭 −0.042 ~ 0.291.
   - 예: LUSC **PIK3R1** 변이 0.614 → 0.386. 폐암 3-year PFS도 유의하게 하락.
4. **Ancestry leakage (equity 경고).** BRCA ancestry 예측이 표준 CV 0.798 → preserved-site **0.507** (≈ chance, p<0.001). UChicago(African-ancestry 다수) 샘플에서 표준 CV가 African ancestry false-positive를 site-staining 패턴만으로 유의하게 부풀림 — 생물학이 아니라 **기관 배치 효과**가 인종을 맞히던 것.

## Proposed fix — Preserved-site CV (quadratic programming)
각 site를 **단 하나의 fold에만** 배치(train·val에 동시 등장 금지)하면서, fold 간 outcome 분포 불균형(완벽 stratification에서의 편차 제곱합)을 **convex/QP 최적화**로 최소화. 결과: 58개 outcome 중 32개(55%)에서 perfect stratification, 12%만 유의미한 불균형. 코드: `github.com/fmhoward/PreservedSiteCV`.

## Why this is BIOP02's defense anchor
우리 파이프라인(H&E WSI → FM embedding → BRCA ER/PR/HER2/PAM50)은 동일한 TCGA-BRCA를 쓰므로 **동일한 site-confounding 위험**에 노출된다. Howard는 (a) 무엇이 새는지, (b) 색 정규화로 안 지워진다는 점, (c) 정량적 보정폭, (d) 검증된 분할 해법까지 한 논문에 담아 **Critic checklist #1 (data leakage)** 의 근거 문헌이자 Exp2 설계의 직접 출처가 된다.

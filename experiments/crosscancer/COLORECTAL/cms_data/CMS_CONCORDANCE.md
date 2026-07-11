# CMS 라벨 일치도 — 권위(Synapse) vs 자가계산(CMScaller)

> TCGA-COADREAD. 권위 라벨 = Guinney consensus(`cms_labels_public_all.txt`, syn4978511, TCGA 573환자).
> 자가계산 = CMScaller NTP(cBioPortal RNA-seq, 템플릿 유전자). 대조 가능(권위 최종콜 CMS1-4) = 484환자.

## 전체 일치율 (핵심)
**398/484 = 82.2%.** 이것이 서로 다른 도구(자가계산 CMScaller vs Guinney CMSclassifier-consensus)의 교차 일치율이며,
문헌 보고 CMScaller-consensus concordance(~0.83) 및 사용자가 겪은 "CMScaller와 CMSclassifier가 완전히 같지는 않다"(≈18% 불일치)와 정합한다.

## Confusion matrix (행=권위 consensus, 열=자가계산 CMScaller)

| 권위 \ 계산 | CMS1 | CMS2 | CMS3 | CMS4 | 합 | class recall |
|---|---|---|---|---|---|---|
| **CMS1** | 67 | 0 | 2 | 2 | 71 | 94% |
| **CMS2** | 3 | 157 | 14 | 29 | 209 | 75% |
| **CMS3** | 13 | 0 | 56 | 0 | 69 | 81% |
| **CMS4** | 3 | 3 | 7 | 118 | 135 | 87% |

## 정정 노트 — "23% 불일치"의 정확한 정체
권위 파일 안의 두 하위방법(**CMS_network vs CMS_RFclassifier**, 둘 다 Guinney CMSclassifier 내부)은 **둘 다 확정 CMS1-4를 낸 441샘플에서 0개만 불일치(라벨 자체는 100% 일치)**한다.
한쪽만 확정하고 다른 쪽은 미분류(UNK/NOLBL)인 경우가 71/573(12%)이며, 앞서 "23% 불일치"라고 한 것은 **라벨 차이가 아니라 '어느 샘플을 분류하느냐(분류가능성)'의 차이**였다. 정정한다.
- 즉 라벨 자체가 갈리는 것은 **서로 다른 도구 간**(CMScaller vs CMSclassifier)이며, 그 값이 위 **18% 불일치**다.

## 해석
- CMS1(67/71)·CMS4(118/135) recall이 높다 — H&E로 형태 상관물이 뚜렷한 아형과 정합(imCMS와 일치).
- 주된 교차-도구 불일치는 CMS2↔CMS4 경계이며, 자가계산이 템플릿 유전자만으로 정규화되어 기질 신호(CMS4)를 다소 과대호출한 것으로 보인다.
- 파이프라인 검증 목적 달성. **최종 분석에는 권위 consensus 라벨을 사용**하고, 자가계산은 검증·재현용으로 보존한다.

# CMS 라벨 3자 일치도 — Synapse vs CMScaller vs CMSclassifier

> TCGA-COADREAD. 세 라벨 소스: **Synapse**=Guinney 최종 consensus(`cms_labels_public_all.txt`, syn4978511) · **CMSclassifier(RF)**=동 파일의 RF 분류기 컬럼 · **CMScaller**=자가계산(NTP, cBioPortal RNA-seq). 확정 콜(CMS1-4) 공통 샘플 기준.

## 쌍별 일치율

| 비교 | 일치 | 일치율 |
|---|---|---|
| Synapse(consensus) vs CMScaller | 398/474 | **84.0%** |
| Synapse(consensus) vs CMSclassifier(RF) | 494/494 | **100.0%** |
| CMSclassifier(RF) vs CMScaller | 388/460 | **84.3%** |
| 3자 만장일치 | 388/460 | 84.3% |

## 읽는 법
- **Synapse consensus 와 CMSclassifier(RF)가 100% 일치하는 이유는 둘이 독립이 아니기 때문이다** — Synapse 최종 라벨이 RF 분류기 출력으로 구성된다. 사실상 같은 값이다.
- 따라서 **실제 도구 간 불일치는 CMScaller vs 나머지 ≈ 16%** 다. 이것이 문헌 concordance(~0.83) 및 "CMScaller와 CMSclassifier가 완전히 같지는 않다"는 경험과 정합한다.

## Confusion matrices (권위 기준, 두 방법)

### 권위(Synapse) × CMSclassifier(RF)  (일치 494/494 = 100.0%)

| Synapse \ CMSclassifier(RF) | CMS1 | CMS2 | CMS3 | CMS4 | 합 | recall |
|---|---|---|---|---|---|---|
| **CMS1** | 76 | 0 | 0 | 0 | 76 | 100% |
| **CMS2** | 0 | 208 | 0 | 0 | 208 | 100% |
| **CMS3** | 0 | 0 | 71 | 0 | 71 | 100% |
| **CMS4** | 0 | 0 | 0 | 139 | 139 | 100% |

### 권위(Synapse) × CMScaller  (일치 398/474 = 84.0%)

| Synapse \ CMScaller | CMS1 | CMS2 | CMS3 | CMS4 | 합 | recall |
|---|---|---|---|---|---|---|
| **CMS1** | 67 | 0 | 2 | 2 | 71 | 94% |
| **CMS2** | 3 | 157 | 14 | 29 | 203 | 77% |
| **CMS3** | 13 | 0 | 56 | 0 | 69 | 81% |
| **CMS4** | 3 | 3 | 7 | 118 | 131 | 90% |

> Synapse×CMSclassifier(RF)가 완전 대각선(100%)인 것은 **RF(CMSclassifier)가 network consensus로 학습되어 이를 재현하기 때문**이다(동어반복적, 독립 검증 아님). 권위 최종 라벨은 network 확정이면 network(80%, 459/573), network가 UNK면 RF로 보충(20%, 114/573)한다 — 즉 주로 network consensus이며 RF는 보조다. **독립적인 다른 그룹의 도구는 CMScaller(Eide 2017)뿐이므로, 유일하게 의미 있는 교차검증은 Synapse×CMScaller(≈84%)다.**

## 결론
- 최종 분석에는 **Synapse consensus 라벨**을 사용한다(권위, CMSclassifier와 동치).
- CMScaller 자가계산은 파이프라인 검증·재현용으로 보존한다(consensus와 84% 일치).
- CMS1·CMS4(H&E 형태 상관물 뚜렷)의 recall이 높고, 주된 불일치는 CMS2↔CMS4 경계다.

## 권위 라벨의 구성 (검증)
- 최종 라벨 = **network 확정이면 network consensus(459/573=80%)**, network가 UNK면 **RF(CMSclassifier)로 보충(114/573=20%)**.
- 즉 권위 표준은 **컨소시엄 network consensus**(Guinney 2015 Nat Med)이고, RF는 그 consensus로 학습된 공식 적용 도구다. Synapse≠CMSclassifier 단독 출력.

# D1 (A에 흡수): 세포주 약물감수성은 내분비요법을 체계적으로 못 잡는다

> A(cost-of-substitution)의 정식 층. 근거: `preregistered_drug_panel.json`(positive-control), `frozen_map.json`.
> claim_level=sanity, hypothesis_only. BRCA-only·DRP 금지 준수.

## 발견 (정량)
사전등록 external-anchor 패널(임상 확립 표적약)이 냉동 세포주→약물 지도에서 **의도한 치료축으로 라우팅되는 비율(positive control):**

| 축 | 앵커약물 지도 라우팅 | positive control |
|---|---|---|
| **antiHER2** | Lapatinib·Afatinib·Sapitinib 전부 → antiHER2 | **3/3 ✅** |
| **chemo/basal** | 세포독성 7종 → chemo | **7/7 ✅** |
| **endocrine** | **Fulvestrant만** → endocrine. Tamoxifen→chemo, Palbociclib·Alpelisib·Taselisib·Pictilisib→antiHER2, AZD8186→chemo | **1/8 ❌** |

즉 2D 세포주 viability 지도는 **표적(HER2)·세포독성(chemo) 결정엔 신뢰성 있지만, 내분비/cytostatic 결정엔 사실상 눈이 멀어 있다.** (알려진 이유: 내분비약은 ER 의존 cytostatic이라 단기 2D viability 스크린이 못 잡음.)

## A에 대한 함의 (ER+ 박스의 이중 한계)
subtype 지도에서 **ER+/endocrine 칸이 불확실**한 이유가 하나가 아니라 **둘**:
1. **H&E 분류기 쪽** — Normal-like 과예측으로 luminal 30% 무치료 이탈(예비 라우팅).
2. **치료증거(세포주 지도) 쪽** — endocrine 축 지도 자체가 약함(1/8). **완벽한 ER 분류기라도** cost-of-substitution의 endocrine 값은 신뢰 못 함.

→ 그래서 지도에서 **단단한 결론은 양 극단(HER2 무용·basal 안전)**이고, endocrine은 물렁하다는 게 **분류기 탓만이 아니라 치료증거 인프라의 구조적 한계**임.

## 일반화된 정직한 기여 (A를 강화)
이건 우리 지도만의 quirk가 아니라 **DepMap/GDSC→치료전이 패러다임 전체의 한계**:
> 세포주 약물감수성은 targeted·cytotoxic 축엔 유효한 치료증거지만, **BRCA의 ~70%를 차지하는 ER+ 내분비 backbone엔 체계적으로 부적합**하다.

- Dawood류 H&E→약물 직접예측이나 세포주 전이 연구가 대개 이걸 명시 안 함 → 우리 cost-of-substitution 프레임이 **정량적으로 노출**.
- Paper A 서술: "cheap H&E가 어디까지 충분한가" 지도에 **"그리고 세포주 치료증거 자체도 어디까지 유효한가"** 층을 겹침 → 두 축의 한계를 함께 그린 정직한 지도.

## 후속(선택)
- endocrine 축 보강 대안: PRISM secondary(8-point)·장기 assay·ER+ 특이 지표가 GDSC/PRISM에 있는지(jhans BIOP02-52) — 있으면 endocrine 지도 재구성, 없으면 "세포주 증거로는 판정 불가"로 정직 기술.

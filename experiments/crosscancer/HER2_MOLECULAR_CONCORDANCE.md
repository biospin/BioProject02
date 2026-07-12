# HER2 분자 다중검사 일치 + decoupling 증거 (2026-07-12)

> 사용자 질의("CNV·IHC/FISH 매칭")에서 출발. HER2가 **여러 분자검사에서 명확히 실재**하는데도 H&E는 못 본다(decoupling)를 굳히고, 라벨 정의 이슈를 드러낸다. claim_level: hypothesis_only.

## 1. CNV — 증폭이 high-level(라벨 깨끗)
cBioPortal `*_pan_can_atlas_2018` ERBB2 copy number(log2CNA):
- **유방**: GISTIC=2(high-amp) 123/1070(11.5%), 증폭군 log2 중앙 **3.66**(≈12배), 비증폭군 ~0.00.
- **위**: GISTIC=2 58/438(13.2%), 증폭군 log2 중앙 **3.66**, 비증폭군 0.01.
→ 증폭군은 애매하지 않은 **명확한 high-level 증폭**. 라벨 노이즈 아님 → H&E 실패는 진짜 형태학적 침묵.

## 2. 세 분자검사 상호 일치 (유방, 같은 TCGA 환자, `brca_tcga` 임상)
FISH+ 78 · IHC 3+ 90 · CNV-amp(GISTIC=2) 123.
| 비교 | 일치율 |
|---|---|
| FISH ↔ CNV증폭 | 88.9% (n=397) |
| IHC 3+ ↔ CNV증폭 | 91.2% (n=411) |
| FISH ↔ IHC 3+ | 93.6% (n=125) |
→ 세 assay가 대체로 같은 종양을 HER2+로 지목 → **"HER2+가 분자적으로 실재"가 3중으로 airtight.**
+ CPTAC proteomics(단백질 d≈4.0, p≈1.6e-7)까지 하면 **4개 직교 분자층(DNA copy·FISH·IHC 단백질·MS 단백질)이 모두 HER2+를 확인**하는데 H&E만 못 본다(≈chance 0.59).

## 3. ⚠️ 드러난 라벨 정의 이슈 (정직히)
- **유방 라벨 = IHC status(`her2_status_by_ihc`)**, **위 라벨 = CNV(GISTIC=2)** — **서로 다른 assay**로 정의됨.
- 일치율이 높으나 완전치 않다(GISTIC=2는 stringent → FISH+/IHC3+ 일부가 저수준 증폭이라 GISTIC 미달: FISH+ 78 중 41이 CNV-정상).
- **함의/액션**: 논문에서 HER2 정의를 **암종 간 harmonize**(예: 임상 표준 = IHC 3+ 또는 FISH+, CNV는 보조)하거나, assay 차이를 명시. 추가 견고성: **H&E-blindness가 정의(IHC/FISH/CNV) 무관하게 성립하는지** 재검(같은 유방 코호트를 세 정의로 각각 H&E 예측 → 모두 ≈chance면 강력).

## 결론
- "HER2 증폭 실재 증명이 더 필요한가?" → **분자적 실재는 이미 4중 확인.** 우리 기여는 "HER2가 실재한다"가 아니라 "**여러 분자검사가 명확히 잡는 것을 H&E는 못 잡는다(치환 불가)**"이고, 이 대비가 decoupling의 핵심.
- CNV·IHC·FISH 매칭은 (a) 라벨이 high-level·다중검사 일치로 **깨끗함을 입증**해 "H&E 실패=노이즈" 반박을 막고, (b) **breast(IHC)/gastric(CNV) 정의 불일치**를 드러냄 → harmonize 필요.
- 산출 재현: cBioPortal API(ERBB2 gistic·log2CNA / brca_tcga HER2_FISH_STATUS·HER2_IHC_SCORE, PATIENT-level).

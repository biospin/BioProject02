# chakravarty-2017-oncokb — Core 요약 (Core summary)

**OncoKB: A Precision Oncology Knowledge Base**
Chakravarty D, Gao J, Phillips SM, Kundra R, Zhang H, ... Schultz N.
*JCO Precision Oncology* 2017. DOI 10.1200/PO.17.00011. PMC5586540.

## 핵심 기여 (Core contribution)
개별 체세포 변이(somatic mutation)에 대해 **(1) 생물학적/발암 효과(oncogenic effect)** 와 **(2) 치료적 함의(therapeutic implication)** 를 전문가 큐레이션으로 부여하는 정밀종양학 지식베이스. 출판 시점 기준 **418개 암 관련 유전자**, **>3,000개의 고유 변이(돌연변이·융합·copy-number)** 를 주석화. cBioPortal에 통합되어 변이를 임상적으로 해석 가능하게 만든다.
An expert-curated precision-oncology KB that annotates each somatic variant with its oncogenic effect and its therapeutic implication. At publication: 418 cancer genes, >3,000 unique alterations; embedded in cBioPortal.

## 두 축의 주석 체계 (Two annotation axes)
- **Oncogenic effect:** Oncogenic / Likely Oncogenic / Likely Neutral / Inconclusive / Unknown — 변이가 발암 동인인지 판정.
- **Therapeutic (Tx) Levels of Evidence — 종양형(tumor-type)별:**
  - **Level 1** — FDA가 해당 적응증에서 승인약 반응 예측 바이오마커로 인정.
  - **Level 2** — 승인약에 대한 standard-care 바이오마커로 널리 인정.
  - **Level 3A** — well-powered 임상연구에서 약물 반응 예측(해당 종양형).
  - **Level 3B** — 다른 적응증에서 인정된 standard/investigational 바이오마커.
  - **Level 4** — compelling biological evidence 기반 예측.
  - **R1 / R2** — 표준치료/임상적 근거 기반 **내성(resistance)** 바이오마커.

## 근거 출처 (Evidence sources)
FDA 라벨 · NCCN 가이드라인 · 질환별 전문가그룹 권고 · 임상시험 · 과학 문헌. 의사·암생물학자 패널이 감독.

## 검증 규모 (Validated numbers)
- 19개 암종 **5,983 원발성 종양** 분석.
- **41%** 가 최소 1개의 잠재적 actionable 변이 보유; 그중 **7.5%** 가 표준치료 임상 이익을 예측(Level 1/2).

## BIOP02 역할 (Role)
가설화된 BRCA 변이→약물 edge를 **인정된 evidence tier(Level 1–4)** 로 환산하는 actionability **오라클**. 단, Tx 레벨은 토큰/라이선스 게이트(아래 lens 참조) → 오픈 경로로의 근사 + 잔여 gap 라벨링이 필수.

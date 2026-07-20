# farahmand-2022-modpathol — Lens: Academic

## Novelty 평가
H&E에서 HER2 상태를 예측한 연구는 선행(Bychkov·Rawat·Naik)이 있었으나, 본 연구의 진짜 신규성은 **(1) invasive-carcinoma tumor ROI로 입력을 국한**해 정확도를 0.90/0.81로 끌어올린 점과 **(2) 같은 modality를 trastuzumab 반응(pCR) 예측으로 확장**해 H&E→HER2→치료반응을 한 파이프라인으로 연결한 점. 백본(Inception v3)·집계(확률 평균+0.5 cutoff)는 표준 재사용 → 방법론적 신규성은 **중간**, 임상 질문 설정(반응 예측)의 신규성이 큼.

## Rigor 평가
- **강점:** 독립 TCGA 외부테스트(HER2 상태), 1000회 bootstrap CI, 2-class/3-class 주석 비교, 선행 3개 방법과 정량 대조, blinded ROI-예측 일치 분석.
- **약점:**
  - **Trastuzumab 반응은 외부검증 전무** — single-institution Yale n=85, **5-fold CV만**. HER2 상태처럼 독립 코호트 재현이 없다.
  - **검정력:** n=85(36/49), AUC 0.80의 **95% CI 0.69–0.88**로 폭이 넓다. 0.80은 point estimate일 뿐 하한 0.69까지 열려 있어, 이 벤치마크는 "고정된 천장"이 아니라 **넓은 신뢰구간을 가진 in-cohort CV 값**으로 읽어야 한다.
  - ROI **수기 주석 의존** → 관찰자 변이·확장성 한계.
  - 코드·데이터 비공개("upon request") → 독립 재현 곤란.

## BIOP02와의 관계 (head-to-head anchor)
- **동일 modality**: H&E tumor ROI. **동일 target**: trastuzumab 반응(pCR). **동일 데이터 계보**: Yale 코호트 = 공개된 **TCIA HER2-TUMOR-ROIS**(status ROI + 85 response cohort/pCR 라벨 포함, 검증됨).
- 따라서 이 논문은 Paper C real-outcome anchor의 **직접 벤치마크**다.

## 차별점 (우리의 방어선)
- 이들: **in-cohort로 학습한 black-box Inception v3**. 우리: **Yale에 학습하지 않은 frozen out-of-cohort phenotype 모델**에서 유도한 **해석 가능한 anti-HER2 axis score** → 더 어려운(핸디캡 있는) 설정.
- 코호트가 **전부 HER2+**라 코호트 내부에서 HER2 상태는 반응에 거의 비정보적 → 우리 검정의 핵심은 axis score가 **HER2 양성 여부를 넘어서는** 반응 신호를 잡는가(= HER2-probability baseline 대비 DeLong 우위).
- 이들: **단일 태스크**. 우리: cross-cancer **substitution decision map**의 한 anchor + cost-of-substitution 프레이밍.

## 인용 포인트
- "H&E tumor-ROI → HER2/trastuzumab-response" **직접 벤치마크**로 인용, trastuzumab CV AUC 0.80(CI 0.69–0.88)을 우리 bar로 명시.
- 외부검증 부재·수기 주석·비공개 코드를 우리 설계 동기(공개 TCIA + frozen public FM + 외부 적용)로 인용.

## 검증 플래그
수치 전부 WebFetch(PMC10221954)로 확인: 188(93/95)·CV 0.90(0.79–0.97)·TCGA 187(92/95) 0.81(0.73–0.84)·85(36/49) 반응 5-fold 0.80(0.69–0.88)·Inception v3·512px@20×·확률평균+0.5. **[미확인]** trastuzumab 모델이 HER2 Inception 가중치를 transfer했는지 vs 새로 학습했는지는 본문 미명시.

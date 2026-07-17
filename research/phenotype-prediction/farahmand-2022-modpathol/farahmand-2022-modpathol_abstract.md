# Farahmand 2022 (Modern Pathology) — Abstract-level analysis

## 서지
- **제목:** Deep learning trained on hematoxylin and eosin tumor region of interest predicts HER2 status and trastuzumab treatment response in HER2+ breast cancer
- **저자:** Saman Farahmand, Aileen I. Fernandez, Fahad Shabbir Ahmed, David L. Rimm, Jeffrey H. Chuang, Emily Reisenbichler, Kourosh Zarringhalam
- **출처:** Modern Pathology 2022; 35(1): 44–51
- **DOI:** 10.1038/s41379-021-00911-w
- **원문 확인:** PMC10221954 + Europe PMC (verbatim abstract 확보)

## 초록 요약
HER2+ 유방암의 표준 치료는 HER2 증폭(ISH 또는 IHC 판정)에 근거한 neoadjuvant 항암 + 항-HER2 병용이다. 그러나 H&E 슬라이드가 훨씬 흔하게 확보되므로, H&E에서 HER2 상태와 항-HER2 치료 반응을 정확히 예측하면 비용을 줄이고 치료 선택 속도를 높일 수 있다. 저자들은 기존 방법보다 정확도를 높인 CNN 분류기를 제시한다.

- **HER2 상태 예측:** 병리팀이 tumor ROI를 수기 주석한 **188개 H&E WSI**(93 HER2+, 95 HER2−)로 학습. slide-level HER2 상태에 대해 **교차검증 AUC 0.90**, **독립 TCGA 테스트셋(187 slides)에서 AUC 0.81**. 슬라이드 내부에서 병리의가 주석한 ROI와 blinded 계산 예측(tumor region / HER2 status)이 강하게 일치.
- **Trastuzumab 치료 반응 예측:** 이후 trastuzumab 치료를 받은 **HER2+ 환자 187명의 치료 전(pre-treatment) 샘플**(36 responders, 49 non-responders)로 학습. **5-fold 교차검증 AUC 0.80**.

## 우리 논문에서의 역할
- **역할: head-to-head 벤치마크 (핵심 baseline).** Paper C의 real treatment-outcome anchor — Yale HER2 코호트(TCIA HER2-TUMOR-ROIS)에서 H&E 유도 anti-HER2 axis score가 실제 trastuzumab 반응(pCR)을 층화하는지 — 와 **동일 modality(H&E tumor ROI) · 동일 target(trastuzumab 반응) · 겹치는 코호트 계보**를 공유한다.
- **AUC bar:** 이들의 trastuzumab-response **5-fold CV AUC = 0.80**이 우리 axis score가 넘어야(또는 최소한 도달해야) 하는 정량 기준이다. HER2 상태 예측 쪽 기준은 CV AUC 0.90 / TCGA 독립 AUC 0.81.
- **데이터 소스:** 이들이 사용한 Yale trastuzumab-response 코호트가 TCIA로 공개된 HER2-TUMOR-ROIS로, 우리 anchor의 실제 데이터 출처와 같은 계보다.
- **차별점(novelty 방어):** (1) black-box CNN이 아닌 **해석 가능한 anti-HER2 axis score**, (2) 단일 태스크가 아니라 cross-cancer "substitution decision map"의 한 anchor, (3) H&E→HER2→치료 연결 자체는 이 논문이 이미 제시했으므로 우리는 그 연결의 novelty가 아니라 **의사결정 비용(cost-of-substitution) 프레이밍과 real-outcome 층화 검증**을 기여로 주장한다.

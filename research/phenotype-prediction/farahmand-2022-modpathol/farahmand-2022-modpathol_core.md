# farahmand-2022-modpathol — Core 요약

**Deep learning trained on H&E tumor ROI predicts HER2 status and trastuzumab treatment response in HER2+ breast cancer**
Farahmand S, Fernandez AI, Ahmed FS, Rimm DL, Chuang JH, Reisenbichler E, Zarringhalam K.
*Modern Pathology* 35(1):44–51 (2022; epub 2021 Sep 7). DOI 10.1038/s41379-021-00911-w. 원문 확인: PMC10221954.

## 핵심 기여 (Core contribution)
병리의가 수기 주석한 **tumor ROI(invasive carcinoma)** 만 입력으로 받아, H&E에서 (1) **HER2 상태**와 (2) **trastuzumab 치료 반응(pCR)** 을 예측하는 CNN 분류기. 당시 선행 연구 대비 HER2 예측 정확도를 끌어올렸고, H&E→HER2→치료반응 연결을 하나의 파이프라인으로 제시.

## 방법 (Method) — 검증됨
- **ROI 주석:** invasive carcinoma 영역을 circling. necrosis·in situ·benign stroma/epithelium 제외.
- **타일:** ROI 내부를 **512×512 px @ 20× 비중첩 패치**로 분할. background·fat 과다 타일 제거.
- **백본:** **Inception v3** (transfer learning + full training 두 전략 모두 사용). optimizer RMSProp(lr 0.1, weight decay 0.9, momentum 0.9), augmentation = 90/180/270° 회전 + 수평/수직 flip.
- **집계:** 타일별 HER2+/HER2− 확률을 **평균** → **0.5 cutoff**로 slide-level 라벨 결정.
- **CI:** 모든 95% CI는 **1000회 bootstrap**.

## 데이터셋 (Dataset)
- **HER2 상태 학습(Yale):** **188 slides = 93 HER2+ / 95 HER2−**, 70/30 split.
- **독립 테스트(TCGA-BRCA):** QC 후 **187 samples = 92 HER2− / 95 HER2+** (타일 176,399 HER2+ / 193,546 HER2−).
- **Trastuzumab 반응(Yale):** **85 pre-treatment HER2+ 코어생검** — **36 responders(pCR) / 49 non-responders**. 반응 = surgical resection에서 residual invasive/LVI/metastatic 없음(pCR). ※선행 abstract의 "187명"은 오류(=TCGA 테스트 수와 혼동), 실제 n=85.

## 주요 결과 (검증된 수치)
- **HER2 상태 — 2-class:** slide-level **CV AUC 0.90 (95% CI 0.79–0.97)**, tile-level AUC 0.77.
- **HER2 상태 — TCGA 독립테스트:** slide-level **AUC 0.81 (95% CI 0.73–0.84)**.
- **HER2 상태 — 3-class(HER2+/−/Other):** 클래스별 AUC 0.88/0.88/0.87 (tile-level 정확도↑, slide-level은 유사).
- **Trastuzumab 반응:** **5-fold CV AUC 0.80 (95% CI 0.69–0.88)** ← 우리 anchor의 정량 bar.
- **선행 대비 우위:** Bychkov 0.70(CV)/0.67(test), Rawat 0.71(TCGA)/0.79(ABCTB), Naik 0.778 → 본 연구 0.90/0.81.

## 한계 (Limitations)
- 두 Yale 코호트 모두 **single-institution**; trastuzumab 반응은 **외부검증 없음**, **n=85·CI 폭 넓음(0.69–0.88)**.
- ROI **수기 주석 의존**(자동 tumor-detection 아님).
- 코드·데이터 **"available upon request"**(공개 배포 아님) → 원모델 재실행 불가, 공개 수치와 비교만 가능.

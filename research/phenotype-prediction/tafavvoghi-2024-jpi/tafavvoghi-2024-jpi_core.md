# tafavvoghi-2024-jpi — Core 요약

**Deep learning-based classification of breast cancer molecular subtypes from H&E whole-slide images**
Tafavvoghi M, Sildnes A, Rakaee M, Shvetsov N, Bongo LA, Busund L-TR, Møllersen K.
*Journal of Pathology Informatics* (2024). DOI 10.1016/j.jpi.2024.100410.

## 핵심 기여 (Core contribution)
H&E WSI만으로 유방암 **4-class 분자 아형(LumA / LumB / HER2-enriched / Basal-like)을 직접 분류**하는 2단계 파이프라인 제시. 별도 분자 측정 없이 형태학 tile만으로 PAM50-style 아형 신호를 회수. **macro-F1 = 0.727** 달성 — H&E→subtype 과제의 published 기준선.

## 방법 (Method)
- **전처리:** WSI → **512×512 tile @ 20×** (non-overlapping; HER2 클래스만 64px overlap).
- **Step 1 — Tumor segmentation:** Inception_V3로 tumor vs non-tumor tile 분류, **F1 = 0.954**. 종양 tile만 다운스트림에 사용.
- **Step 2 — Subtyping:** 아형별 **One-vs-Rest 이진 CNN (ResNet-18)** 4개. 각 아형 최적 threshold를 넘는 **tile count**를 feature로 추출.
- **Aggregation:** 4개 OvR 출력의 tile-count feature를 **XGBoost** meta-classifier로 WSI-level 최종 아형 예측. (Foundation model 아님 — ImageNet/CNN 기반.)

## 데이터셋 (Dataset)
- **총 1,433 WSI:** TCGA-BRCA **980** + CPTAC-BRCA **382** + HER2-Warwick **71**. **Breast-only.**

## 주요 결과 (검증된 수치)
- **macro-F1 = 0.727** (반올림 0.73).
- per-class F1: **LumA 0.922 / LumB 0.742 / HER2-E 0.545 / Basal 0.698**.
- HER2-E가 명확한 ceiling (0.545) — 형태학만으로 HER2-enriched 식별이 가장 어려움.

## 한계 (Limitations)
- **Site/scanner confound 통제 없음** (저자도 staining·scanner 변동성을 한계로 인정).
- **외부 독립 test split 없음** — cohort를 섞어 학습/평가; generalization 증거 부재.
- **치료적 내용 전무** — 진단(아형) 분류에서 멈춤, therapeutic hypothesis 없음.
- 백본이 ImageNet CNN — pathology foundation model 미사용.

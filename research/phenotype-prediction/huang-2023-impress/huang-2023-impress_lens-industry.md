# huang-2023-impress — Lens: Industry / Reproducibility

## 코드 가용성
- **GitHub: https://github.com/huangzhii/IMPRESS** — **MIT 라이선스**(관대, 상업 재사용 허용). 언어 Python(97.8%) + MATLAB(2.2%).
- 파이프라인: registration + segmentation + feature extraction + ML(`main.py`) 공개.
- 의존성: **PyTorch 1.6.0 / TorchVision 0.7.0, scikit-learn 0.23.2, OpenCV 4.4.0, OpenSlide 1.1.2, pandas, Pillow** — 구버전 pin(재현 시 환경 격리 필요).

## 데이터 가용성
- **Pre-extracted features 제공**: repo `features/` 폴더에 HER2+·TNBC 두 코호트의 추출 특징, `clinical/` 폴더에 임상 데이터 → **raw WSI 없이도 ML 부분(LASSO logistic + LOOCV) 즉시 재현 가능**.
- **미제공**: pre-trained 모델, raw WSI. 정합·분할 단계를 raw부터 돌리려면 자체 WSI 필요.
- 외부 검증 코호트(n=20/subtype) 데이터 및 출처 = **[미확인]**(repo/논문 미명시).

## 재현성 평가
- ML 재현성 **높음**: 36개 특징이 이미 표로 제공 → `main.py`로 dev AUC(0.8975/0.7674) 재현 진입장벽 낮음. 해석 가능 특징이라 결과 감사(audit)도 용이.
- 전(前)단계(정합·DeepLabV3 분할·K-means IHC) 재현성 **중간**: raw WSI·마스크 없이는 특징 생성 단계 완전 재현 불가. 파라미터는 코드 의존.
- 리스크: 구버전 라이브러리 pin(torch 1.6/sklearn 0.23.2) → 최신 env에서 수치 재현 시 미세 차이 가능.

## interpretable-feature 접근 (우리에게 시사)
- IMPRESS의 36개 특징은 **명명 가능한 TIME 통계**(면역세포 밀도·영역 비율) → 우리 phenotype 중간층 철학과 정렬. 다만 이들은 **IHC 정합이 있어야만** 산출 가능한 특징(예 Lymph:CD8 ratio)이라 **H&E 단독으로는 직접 이식 불가**.
- 우리가 재사용할 것: (1) **해석 가능 특징 → 고전 ML(LASSO) → NAC 반응** 구조를 소표본 baseline 프레이밍으로 참조. (2) `features/`+`clinical/` 공개 방식을 우리 산출물 공개 표준의 참고 사례로.

## 산업/거버넌스 메모
- 이들은 직접 NAC 반응(pCR) 예측 점수를 출력 → 우리는 동일 계열 출력을 내되 **hypothesis_only claim_level + Scientific Critic pass** 후에만 공유(anti-DRP 규약, DRP 프레이밍 표현 금지).
- 외부 n=20 성능은 **마케팅용 상한으로 인용 금지** — 소표본 취약성 caution으로만 사용.

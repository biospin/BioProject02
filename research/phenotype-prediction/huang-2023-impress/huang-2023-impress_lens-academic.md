# huang-2023-impress — Lens: Academic

## Novelty 평가
진짜 신규성은 **H&E↔multiplex IHC를 non-rigid 정합**해 같은 조직 좌표에서 TIME 특징을 뽑고, 이를 **36개 해석 가능 특징**으로 정형화한 파이프라인(IMPRESS)이다. 모델(LASSO logistic)·분할 백본(DeepLabV3/ResNet-101)은 기성 자산 재사용. 따라서 방법론적 신규성은 **중간**이나, "IHC 마커를 좌표 정합해 해석 가능 NAC 예측 특징으로 환원"한 설계·해석성 기여가 크다. End-to-end 블랙박스가 아니라 **각 특징이 병리학적으로 명명 가능**하다는 점이 차별.

## Rigor 평가
- 강점: 병리의 수기 특징 대비 우위 입증, LOOCV, 두 subtype 별도 모델링, TIME 마커(면역세포 밀도·비율) 기반 생물학적 근거.
- 약점: **개발 n=62/64 소표본 + 외부 n=20/subtype(10/10)** — 외부 AUC가 HER2+ 0.90이든 TNBC 0.59든 신뢰구간이 매우 넓다. 개발 SD ±0.0038은 run-to-run 값이라 표본 규모 대비 지나치게 좁게 보여 **낙관 편향**을 시사. **외부 코호트 출처 기관 미명시([미확인]).**

## BIOP02와의 관계 (target-journal precedent)
- **같은 저널 (npj Precision Oncology)** — Paper C 유력 타깃.
- **같은 task family: H&E(+IHC) → 치료 반응(NAC/pCR)**, 소표본(~126) 유방암.
- **같은 정신: 해석 가능 특징 baseline** (우리 phenotype 중간층과 철학 공유).

## 차별점 (우리의 방어선)
- 우리는 **H&E 단독** axis score로 substitution 판단 vs 이들은 **multiplex IHC co-registration 필수**(IHC 없으면 파이프라인 성립 안 됨) — 우리 장점은 정확히 이 modality gap(IHC 없이 판단).
- 우리는 **~1010 BRCA + CPTAC 외부 검증**(수백 규모) vs 이들의 **외부 n=20/subtype**.
- 우리는 **HER2 anti-HER2 axis → pCR anchor**(Yale/Farahmand 0.80 bar) vs IMPRESS의 **NAC(chemo±anti-HER2) 반응** — regimen이 다르다(methodology-brief 참조).

## 인용 포인트
- (1) **저널 선례**: npj Prec Onc가 "H&E(+IHC)→NAC 반응, 해석 가능 특징, 소표본" 논문을 받는다는 직접 증거.
- (2) **해석 가능 특징 baseline**: treatment-outcome-anchor 트랙의 대조.
- (3) **외부 취약성 증거**: TNBC 0.77→0.59 붕괴를 external generalization fragility 근거로 인용(단, HER2+ 0.90도 n=20이라 견고 상한으로 인용 금지).

## 검증 플래그
PMC9883475 + GitHub로 확인: 62/64, 36 특징, PD-L1/CD8/CD163, LASSO logistic, LOOCV, DeepLabV3+ResNet-101, non-rigid registration, dev AUC 0.8975±0.0038 / 0.7674±0.0209, 외부 0.9005 / 0.5865 (각 n=20). 개발 기관 = Ohio State. **외부 코호트 출처 = [미확인]**. End-to-end DL 아님(고전 ML) = 확인됨.

# huang-2023-impress — Methodology Brief (포지셔닝·인용 가이드) ★

IMPRESS를 우리 논문(특히 Paper C + treatment-outcome-anchor 트랙)에서 **세 축으로 인용**한다: (1) target-journal precedent, (2) interpretable-feature baseline, (3) external-fragility 증거. 각 축의 정확한 사용법과 과대해석 방지선.

## A. 세 target(우리 anchor vs IMPRESS vs Farahmand) — 혼동 금지
셋은 "HER2+ 유방암 치료 반응"으로 뭉뚱그리기 쉬우나 **regimen·modality가 다르다**. 인용 시 반드시 구분:

| | 예측 target | modality | 성능(검증) | 외부검증 |
|---|---|---|---|---|
| **IMPRESS (본 논문)** | **NAC**(chemo±anti-HER2) → pCR | **H&E + multiplex IHC 정합**(필수) | dev HER2+ 0.8975 / TNBC 0.7674 (LOOCV) | n=20/subtype (HER2+ 0.90 / TNBC 0.59) |
| **Farahmand 2022 (우리 HER2 anchor)** | **trastuzumab**-특이 반응 → pCR | **H&E 단독** | 5-fold CV AUC **0.80 (95% CI 0.69–0.88)**, n=85 | **없음** |
| **우리(BIOP02)** | anti-HER2 axis → pCR | **H&E 단독** | (미확정, hypothesis_only) | TCGA→CPTAC 계획 |

- **핵심**: IMPRESS의 "HER2+ NAC 반응"과 Farahmand의 "trastuzumab 반응"은 **같은 target이 아니다** — regimen(광범위 NAC vs anti-HER2 특이)과 modality(IHC 정합 필요 vs H&E 단독)가 다르다.
- **우리 substitution 논지의 자리**: IMPRESS는 IHC 정합이 있어야 특징이 나오는 반면, 우리·Farahmand는 **IHC 없이 H&E만으로** 판단 → "H&E가 IHC를 언제 값싸게 대신하나"라는 우리 substitution-cost 논지가 정확히 이 modality gap에서 산다. 이 대비를 본문에 명시.

## B. AUC bar 포지셔닝 — 어떻게 나란히 놓나
- 우리 HER2 outcome anchor의 정량 bar는 **Farahmand 0.80 (H&E 단독)**로 잡는다. IMPRESS dev HER2+ 0.8975는 **IHC를 얹은 상한**이므로 "IHC 포함 시 도달 가능한 밴드"로만 언급하고, 우리 H&E 단독 성능의 직접 목표선으로 쓰지 않는다(modality 불일치).
- IMPRESS dev SD ±0.0038은 **run-to-run 값**(환자 수준 CI 아님) → n=62 대비 과하게 좁다. 이 낙관은 외부 붕괴와 같은 소표본 기전 → **dev 수치를 상한으로 인용할 때 반드시 이 caveat 병기**.

## C. External-fragility 증거로서의 사용 (substitution-cost 논지 보강)
- 인용 핵심: TNBC dev 0.7674 → **external 0.5865 붕괴**. "external generalization은 취약하다 → 우리 anchor의 외부 일반화 주장을 과장하지 않는다"는 caution의 직접 근거.
- **과대해석 방지선(중요)**: HER2+ external 0.90도 **n=20(10/10)** → 신뢰구간 극대. "HER2+는 견고하게 유지됐다"로 쓰면 안 됨. **둘 다 소표본**이라는 것이 정직한 프레이밍이며, 이는 오히려 우리 fragility 논지를 강화한다. 우리 자신의 외부(CPTAC ~120) 주장도 규모·CI를 명시해 같은 함정을 피한다.

## D. 인용 문장 템플릿 (본문용, hypothesis_only 준수)
- 저널 선례: "npj Precision Oncology는 소표본(~126) H&E(+IHC)→NAC 반응·해석 가능 특징 연구(IMPRESS, Huang 2023)를 게재했다" → 우리 프레이밍의 venue-fit 근거.
- fragility: "IMPRESS의 TNBC external AUC는 개발 0.77에서 0.59로 하락했고 검증 코호트는 subtype당 20명에 불과했다 — 소표본 외부 검증의 취약성을 보여준다."
- 절대 금지: IMPRESS 수치를 우리 결과의 성공 근거로 전용, "personalized therapy"·"drug response prediction" 프레이밍, external 0.90을 견고 상한으로 제시.

## 검증 플래그
PMC9883475 + GitHub(huangzhii/IMPRESS, MIT) 확인: 62/64, 36 특징(PD-L1/CD8/CD163), LASSO logistic + LOOCV, DeepLabV3+ResNet-101 분할 + non-rigid registration, dev 0.8975±0.0038 / 0.7674±0.0209, external 0.9005 / 0.5865 (각 n=20, 10/10), 개발기관 Ohio State, accrual 2011–2016. **외부 코호트 출처 기관 = [미확인]**. Farahmand anchor(0.80, 95%CI 0.69–0.88, n=85, H&E 단독, 외부검증 없음)는 farahmand-2022-modpathol_core.md에서 확인.

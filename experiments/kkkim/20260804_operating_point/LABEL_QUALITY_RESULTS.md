# BIOP02-124 #6 — label-quality 민감도 (CPTAC-BRCA 수용체 라벨 provenance)

> cBioPortal 원시 임상속성에서 확정(pos/neg) vs 경계·미평가 비율을 집계. 예측은 필터된 깨끗한 라벨에 대해 산출됨.

| endpoint | 라벨 층위 | 총 | 확정 | 경계·미평가(drop) | drop% | pos | neg | 양성 유병률 |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| ER | clinical/IHC(primary) | 120 | 120 | 0 | 0.0% | 81 | 39 | 0.675 |
| PR | clinical/IHC(primary) | 115 | 115 | 0 | 0.0% | 68 | 47 | 0.591 |
| HER2 | clinical/IHC(primary) | 103 | 95 | 8 | 7.8% | 13 | 82 | 0.137 |
| HER2 | proteogenomic(alt platform) | 122 | 122 | 0 | 0.0% | 15 | 107 | 0.123 |

## 판독

- **ER·PR: 경계 라벨 0%.** 확정 라벨만으로 구성돼 operating-point(ER 환자단위 AUROC 0.913)는 고신뢰 라벨 위의 값이다. 라벨 잡음이 성능을 부풀리거나 깎았다고 볼 근거 없음.
- **HER2: IHC 경계(2+) 7.8%가 이미 제거됨.** 즉 대체불가 음성(AUROC 0.530)은 **가장 명확한 HER2 라벨 부분집합**에서 나온 결과다 → "HER2 대체 불가"가 라벨 잡음의 산물이라는 반론을 배제한다(오히려 강화).
- **대체 플랫폼(proteogenomic) HER2 라벨 존재·유병률 일치.** clinical/IHC HER2 양성 유병률과 proteogenomic 유병률이 근접(약 12~14%)해 라벨 층위 간 정합. 다만 예측 파일에 case_id가 없어(HER2 npy) 대체 라벨로의 재평가(AUROC 재계산)는 id-linked 예측 확보 후 후속.
- **단일 1차 소스(cBioPortal).** 다기관 다중 플랫폼 라벨 비교는 이 코호트에선 불가 — 라벨 품질 한계로 명시.

## 원고 반영

- HER2 음성은 equivocal 제거 후 고신뢰 라벨에서의 결과임을 Limitations에 명시(라벨 잡음 반론 차단).
- ER/PR operating-point는 경계 라벨 0%임을 각주로.
- 후속: id-linked HER2 예측으로 proteogenomic 라벨 대비 재평가(라벨 층위 민감도 완결).

> claim_level: hypothesis_only · 리뷰: braveji.
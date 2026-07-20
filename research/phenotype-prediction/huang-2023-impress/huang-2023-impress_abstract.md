# Huang 2023 — IMPRESS (npj Precision Oncology 7:14) — Abstract-level analysis

## 서지
- **제목:** Artificial intelligence reveals features associated with breast cancer neoadjuvant chemotherapy responses from multi-stain histopathologic images
- **저자:** Zhi Huang, Wei Shao, Zhi Han, Ahmad M. Alkashash, Carlo De la Sancha, Anil V. Parwani, Hiroaki Nitta, Yanjun Hou, Tongxin Wang, Paul Salama, Maher Rizkalla, Jie Zhang, Kun Huang, Zaibo Li
- **출처:** npj Precision Oncology 2023; 7: 14
- **DOI:** 10.1038/s41698-023-00352-5
- **원문 확인:** Europe PMC core (verbatim abstract) + Springer "Behind the Paper"

## 초록 요약
사전 치료 병리 이미지로 임상 결과를 예측하는 것은 종양 면역 미세환경에 대한 이해 부족으로 여전히 어렵다. 저자들은 자동·정확·해석 가능·재현 가능한 WSI 특징 추출 파이프라인 **IMPRESS(IMage-based Pathological REgistration and Segmentation Statistics)**를 제시한다.

- **입력:** H&E + multiplex IHC(**PD-L1, CD8+, CD163+**) 이미지. tumor immune micro-environment와 임상 데이터에서 **36개 해석 가능 특징**을 자동 추출.
- **코호트:** neoadjuvant chemotherapy(NAC)를 받은 **HER2+ 62명, TNBC 64명**(여성). 추가로 독립 external validation 코호트.
- **성능:** ML 모델이 NAC 반응을 예측 — **HER2+ AUC = 0.8975; TNBC AUC = 0.7674**(개발 코호트). 이 결과는 병리의가 수기로 만든 특징으로 학습한 모델을 능가.
- **외부 검증:** 독립 코호트로 추가 검증, 특히 HER2+에서 고무적(external HER2+ AUC ≈ 0.90) — 단, **TNBC external은 취약(AUC ≈ 0.59)**.

## 우리 논문에서의 역할
- **역할: target-journal precedent + 해석가능-특징 baseline.** npj Precision Oncology가 Paper C의 유력 타깃 저널이며, 이 논문은 그 저널이 "H&E(+IHC)→NAC 치료 반응, 해석 가능 특징" 논문을 받는다는 직접 선례다. 우리의 서술·프레이밍이 이 저널 기대치에 부합함을 근거로 인용한다.
- **AUC bar:** HER2+ NAC 반응 **dev AUC 0.8975 / external ≈ 0.90**이 참고 상한 밴드. 우리 Yale anchor(anti-HER2 axis → pCR)의 성능을 이 범위와 나란히 놓고 논한다. 단, IMPRESS는 H&E 단독이 아니라 **multiplex IHC를 co-registration**하므로, 우리의 H&E-단독 axis score와는 modality가 다르다는 점을 명시(우리 장점: IHC 없이 substitution 판단).
- **경계·주의점:** 이들의 **TNBC external AUC 0.59** 붕괴는 external validation 취약성의 교훈 — 우리 anchor의 외부 일반화 주장을 과장하지 않도록 하는 caution 근거로 사용.

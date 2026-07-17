# Sammut 2022 — TransNEO (Nature 601:623) — Abstract-level analysis

## 서지
- **제목:** Multi-omic machine learning predictor of breast cancer therapy response
- **저자:** Stephen-John Sammut, Mireia Crispin-Ortuzar, Suet-Feung Chin, Elena Provenzano, H. Raza Ali, et al. (Carlos Caldas 그룹)
- **출처:** Nature 2022; 601(7894): 623–629
- **DOI:** 10.1038/s41586-021-04278-5
- **원문 확인:** PubMed 34875674 (verbatim abstract 확보)

## 초록 요약
유방암은 악성 세포와 종양 미세환경으로 이루어진 복합 생태계이며, 그 구성과 상호작용이 세포독성 치료 반응에 기여한다. 기존 반응 예측 모델은 이 지식을 통합하지 못했다.

- **코호트:** 수술 전 화학요법(± HER2/ERBB2 표적치료)을 받은 **환자 168명**의 치료 전 생검에서 임상·digital pathology·genomic·transcriptomic 프로파일 수집. 수술 시 병리 종점(complete response 또는 residual disease)을 multi-omic 특징과 상관.
- **핵심 소견:** 치료 후 잔존 종양 정도(RCB)는 치료 전 특징 — tumor mutational/copy-number landscape, 종양 증식, 면역 침윤, T세포 dysfunction/exclusion — 과 단조적으로 연관.
- **성능:** 이 특징들을 통합한 multi-omic ML 모델이 **외부 검증 코호트(75명)에서 pathological complete response를 AUC 0.87**로 예측. 최고 성능 모델은 clinicopathological + molecular 데이터를 통합한 경우였다.

## 우리 논문에서의 역할
- **역할: secondary outcome-anchor 후보 + multi-omic 성능 상한(ceiling).** Paper C의 substitution decision map은 "H&E 예측이 언제 molecular test를 대체할 수 있나"를 다룬다. TransNEO는 **full multi-omic(임상+병리+DNA/RNA)** 통합이 도달하는 상한선(external pCR **AUC 0.87**)을 정의하며, 우리의 H&E-단독 anchor는 의도적으로 더 싸고 단순한 반대편 극단이다 — 이 대비가 곧 substitution의 cost-vs-accuracy 축을 만든다.
- **엔드포인트 정의 소스:** pCR / RCB(residual cancer burden) 정의와 neoadjuvant 반응 프레이밍을 우리 anchor가 재사용하는 표준 근거로 인용.
- **부분 겹침·차별점:** TransNEO의 digital-pathology 구성요소가 우리와 겹치는 지점이나, 이들의 핵심 성능은 genomics 통합에서 온다. 우리 H&E substitution이 회피하려는 대상이 바로 그 genomics 비용 — 즉 "molecular test 없이 얼마나 근접하나"를 이 0.87 ceiling 대비로 정량화한다.
- **주의:** 검증 n=75로 작고 단일 외부 코호트이므로, 우리 anchor 성능을 이 0.87과 직접 등가 비교하지 않고 "modality-비용 다른 상한" 맥락으로만 제시.

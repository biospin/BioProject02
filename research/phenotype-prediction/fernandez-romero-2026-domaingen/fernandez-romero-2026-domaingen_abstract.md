# fernandez-romero-2026-domaingen — Abstract

## 서지
- **Title:** Domain generalisation challenges in breast cancer molecular classification using foundation models: a cross-cohort exploratory study
- **Authors:** Jesus Fernandez-Romero, Pablo Ramos-Berciano, Manuel Perez-Perez, David Benavides, Antonio Robles-Frias, Jorge Garcia-Gutierrez, Laura Macias-Garcia (Crossref 확정)
- **Venue:** Medical & Biological Engineering & Computing (Med Biol Eng Comput), 2026 (vol 64)
- **DOI:** [10.1007/s11517-026-03590-4](https://doi.org/10.1007/s11517-026-03590-4)

## 초록 요약
분자 분류는 유방암 치료를 안내하지만 PAM50과 면역조직화학(IHC)은 여전히 비싸고 많은
세팅에서 이용 불가하다. Pathology foundation model(FM)과 multiple instance learning(MIL)의
결합은 H&E 슬라이드만으로 분자 아형을 예측할 가능성을 보였으나, 대부분의 선행연구는
**internal validation만** 보고했다. 본 연구는 **13개 FM × 3개의 상보적 MIL 아키텍처**를
PAM50 아형 예측과 IHC 바이오마커(ER/PR/HER2) 예측에 대해 평가했다 — **TCGA-BRCA(n=1,079)
교차검증** 후 **CPTAC-BRCA(n=120) 외부검증**.

핵심 결과: **Virchow v2**가 전체 최고 성능을 냈으나, **외부검증에서 심각한 열화(degradation)**를
보였고 이 붕괴는 **3개 MIL 아키텍처 전반에서 일관**되게 나타났으며 특히 **HER2-enriched·
Normal-like PAM50 아형**과 **HER2-positive IHC 예측**에서 두드러졌다. 즉 in-domain 예측은
강하지만 도메인 시프트(코호트·염색·특징공간)에서 무너진다는 것이 주된 메시지다.
(표-단위 정확 AUC는 paywall로 미확보 — 정성 인용만 가능.)

## 우리 논문에서의 역할
- **SCOOP (최근접).** 우리가 former 유방 "Paper A"로 하려던 서술적 실험(H&E FM+MIL → ER/PR/HER2/PAM50 예측 + TCGA→CPTAC 외부검증 + multi-FM 비교)을 **동일 설계로 이미 출판** — 우리의 HER2 외부 실패까지 재현. 이 논문이 유방을 standalone 예측 논문에서 **flagship Paper C(치환비용 결정지도)의 anchor로 흡수**하게 만든 직접 원인이다.
- **인용 방식:** 정성 한 줄로 양보 — "H&E→분자 예측 + 외부검증 열화는 이미 출판됨[Fernandez-Romero 2026], 특히 HER2-enriched/Normal-like 붕괴는 우리 HER2 reject와 일관" — 그 뒤 곧바로 **결정-가치(substitutability) 프레임**으로 전환.
- **포지셔닝 지지/위협:** 예측 정확도를 헤드라인으로 삼으면 **정면 스쿱**(위협). 그러나 우리의 novelty(형태 예측이 *언제* 분자검사를 값싸게 대체 가능한가의 결정지도)는 이 논문이 다루지 **않으므로**, 오히려 "예측은 포화됐다"는 우리 전제를 **강화**하는 증거로 재활용된다.
- **사전등록 법칙 연결:** 이 논문의 CPTAC 도메인 붕괴는 우리 SUBSTITUTABILITY_LAW의 "저비용 대체는 in-domain 조건부, cross-domain에는 보정·기권 필요" 조항의 외부 근거로 인용됨.

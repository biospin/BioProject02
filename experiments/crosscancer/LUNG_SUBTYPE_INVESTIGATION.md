# 폐암(NSCLC) 아형 조사 — 결정 메모 (2026-07-12, literature-scout)

> 출처 기반. cross-cancer에서 유방·대장과 like-with-like 비교를 위한 폐 아형 라벨 선택.

## 핵심 결론
유방 PAM50/수용체 **아형**의 폐 격은 **전사체 발현 아형**이다 — LUAD: TRU/PI/PP, LUSC: classical/basal/secretory/primitive. 이래야 세 암종이 같은 층위(발현 정의 아형)로 정렬된다. **LUAD-vs-LUSC 조직형은 한 층위 아래(조직-type, 유방 ductal/lobular 격)이며 우리 양성대조이므로, 이를 "아형 비교"로 승격하면 순환논리다.** 현재 돌리는 **EGFR/KRAS MIL은 변이 층위 = 대장 BRAF와 같은 층위**이지 PAM50 격이 아니다.

## 세 층위 (구분 유지)
| 유방 | 대장 | 폐 (올바른 격) |
|---|---|---|
| PAM50/수용체 **아형** | CMS1-4 | **전사체 아형: TRU/PI/PP(LUAD)·classical/basal/secretory/primitive(LUSC)** |
| ductal/lobular(조직형) | — | LUAD/LUSC(조직형; **양성대조**) |
| HER2-amp·BRCA1/2(변이) | BRAF-V600E | EGFR/KRAS-G12C/ALK(변이 MIL, 진행 중) |

- **LUAD 전사체 아형**(Wilkerson 2012/TCGA 2014): TRU(EGFR enriched·예후 양호)·PI(NF1+TP53)·PP(KRAS+STK11).
- **LUSC 전사체 아형**(Wilkerson 2010): classical 37%·basal 26%·secretory 21%·primitive 16%.

## H&E ↔ 각 층위 예측력
- **LUAD/LUSC 조직형**: H&E gold standard, FM으로 AUROC ~0.95-1.0(Coudray 2018 0.97). 양성대조로만.
- **전사체 아형 from H&E**: **이미 선행연구 존재** — Chen 2021(Front Cell Dev Biol): H&E만으로 LUAD 아형 예측 PI 0.897·PP 0.861·TRU 0.894(TCGA n=470). → 예측 자체는 스쿱.
- **변이 from H&E**: Coudray 2018 EGFR ~0.83(6/10 유전자 예측), Park 2024 EGFR ~0.77, BMC 2026 0.885.
- ⚠️ **중요 비대칭**: 유방 HER2-증폭은 형태학적으로 조용(H&E-blind)하지만, **폐 EGFR은 형태학적 상관물이 있다**(lepidic/acinar/papillary high EGFR, solid/mucinous low; TRU 아형이 EGFR enriched) → H&E로 0.77-0.89 예측. **즉 폐 EGFR은 유방 HER2만큼 blind하지 않다.** "표적변이=blind"의 깔끔한 복제가 아니라 **등급적(graded) 이야기** — 증폭/융합은 blind, EGFR은 부분적으로 보임. 이는 실패가 아니라 "형태학 상관물이 치환가능성을 결정한다" 원리를 강화한다.

## 데이터
- **전사체 아형 라벨**: cBioPortal PanCancer `SUBTYPE` 필드(예 LUAD.1/2/3, LUSC.classical/…) + TCGA marker paper(LUAD Nature 2014·LUSC Nature 2012) supplement. 공개콜을 authoritative로(분류기 불일치 회피 — CMS 교훈 동일).
- 분류기(CMScaller 격): LUAD는 **Liljedahl & Karlsson 2021 SSP**, LUSC는 Wilkerson centroid. **공개 라벨 우선, 미라벨 샘플만 SSP.**
- H&E WSI: GDC(진단슬라이드), 변이 라벨: cBioPortal(이미 EGFR/KRAS 확보).

## 스쿱
- LUAD/LUSC from H&E: 해결됨(Coudray 0.97, 모든 FM ~0.95-1.0) — 예측 novelty 0.
- 전사체 아형 from H&E: **이미 됨**(Chen 2021) — 예측 프레이밍이면 스쿱.
- 변이 from H&E: 다수(Coudray·Park·BMC).
- → **우리 novelty는 예측이 아니라 cross-cancer cost-of-substitution/결정경계 프레이밍.** Chen 2021·Coudray 2018을 최근접 선행으로 인용, 예측 진보 주장 안 함.

## 결정 (권장)
1. **폐 아형 층위 = 전사체 아형(TRU/PI/PP + LUSC 4분류) 추가.** cBioPortal `SUBTYPE` 공개콜, 미라벨은 SSP. 유방 PAM50와 같은 H&E MIL로 예측.
2. **LUAD/LUSC는 선언된 양성대조**로만(아형 비교로 승격 금지).
3. **EGFR/KRAS MIL은 변이 층위 유지** — 단 EGFR≠HER2-blind(형태 상관물 있음)를 해석에 명시. 세 암종 변이 비교(유방 HER2-amp/BRCA↔대장 BRAF↔폐 EGFR/KRAS)는 변이 층위에서 정당.
4. Chen 2021·Coudray 2018 인용, 기여=cost-of-substitution.
5. 대장 CMS arm과 정확히 대칭: 세 암종 모두 아형↔아형, 변이↔변이 — 절대 아형↔변이 금지.

## ⚠️ 치료-라우팅 긴장 (정직히 서술)
전사체 아형은 임상 치료를 라우팅하지 않는다(연구/예후용) — 유방 PAM50·대장 CMS와 동일. 반면 폐는 **조직형(LUAD/LUSC)이 실제로 화학요법을 라우팅**한다(pemetrexed/bevacizumab은 비편평/LUAD, 편평 회피). 따라서 두 평행을 모두 제시: 개념층위 평행(전사체 아형, 층위 정합·라우팅 약함) vs 치료라우팅 평행(조직형+변이+PD-L1, 라우팅 의미·층위 혼합).

## 검증 필요(에이전트 플래그)
- cBioPortal TCGA-LUSC `SUBTYPE` 값 문자열 확인 후 라벨 조인.
- pemetrexed/bevacizumab-조직형 라우팅은 NCCN/Scagliotti 2008 인용.

관련: `CRC_SUBTYPE_INVESTIGATION.md`(대장, 대칭 설계) · `PROGRESS_DECISIONS.md`(층위 오류 정정) · memory `feedback-comparison-like-with-like`.

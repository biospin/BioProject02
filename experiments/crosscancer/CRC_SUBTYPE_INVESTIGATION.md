# 대장암(CRC) 아형 조사 — 결정 메모 (2026-07-12, literature-scout)

> 출처 기반. cross-cancer에서 유방과 like-with-like 비교를 하기 위한 CRC 아형 라벨 선택.

## 핵심 프레이밍 교정 (이 조사의 결론)
- 유방 PAM50/수용체는 **아형 체계이자 동시에 치료-라우팅 체계**이며, 그 안의 HER2가 형태학적으로 조용해 치환비용이 큰 축이다.
- **CRC에는 이 둘을 겸하는 단일 체계가 없다.** 따라서 층위를 나눠 매핑해야 한다:
  - **CMS(Consensus Molecular Subtypes) = PAM50의 아형-층위 격**(전사체 기반·예후용·RNA-seq 필요). "아형 vs 아형" like-with-like는 여기.
  - **치료-라우팅/치환비용 논리는 CMS가 아니라 CRC의 변이·마커 축에 매핑된다.** MSI-H = 저비용(H&E 보임 + 치료 연관). RAS·HER2-amp = 형태학적으로 조용 + 치료 정의 = **유방 HER2의 진짜 CRC 격은 아형이 아니라 변이**다. (BRAF-V600E는 MSI/serrated와 동반해 형태학적으로 보이는 쪽 — 실측 H&E 예측 0.87과 정합.)
- ⚠️ **CMS는 치료를 라우팅하지 않는다**(NCCN 미채택, 예후/연구용) — Buikhuisen JNCI 2022, Ten Hoorn. 따라서 CMS를 PAM50처럼 "치료 결정" 축으로 과대평가하면 안 된다.

## CMS 체계 (Guinney 2015, Nat Med) — 전사체 기반
| CMS | 이름 | 유병률 | 생물학 |
|---|---|---|---|
| CMS1 | MSI Immune | ~14% | hypermutated·MSI·면역활성·BRAF enriched |
| CMS2 | Canonical | ~37% | 상피·WNT/MYC·CIN |
| CMS3 | Metabolic | ~13% | 대사 이상·KRAS enriched |
| CMS4 | Mesenchymal | ~23% | TGF-β·기질침윤·최악 OS |
- 나머지 ~13%는 mixed/unclassified. CRIS(Isella 2017)는 종양세포-내재 5분류(기질 신호 제거) — CMS4가 기질 주도라 H&E 예측에서 가장 모호한 이유.

## H&E → CMS 예측 선행연구 (스쿱)
- **imCMS(Sirinukunwattana, Gut 2021)**: H&E→CMS 랜드마크. TCGA AUC 0.84(n=431 slide). 네 아형 모두 형태 상관물 보고(CMS1 점액+림프구, CMS2 cribriform+comedo, CMS3 확장 점액선, CMS4 침윤+desmoplastic).
- attention-MIL(2023, PMID 37300984): CMS1-vs-rest AUC 0.731, **CMS4 0.609(가장 어려움 — plain CNN이라 encoder 약함)**.
- **정직한 긴장:** "CMS1·CMS4가 형태 강함"은 부분만 사실. encoder에 따라 CMS4 예측력이 갈림(도메인적대/파운데이션 강, plain CNN 약).
- **스쿱 판정: H&E→CMS 예측 자체는 이미 확립(imCMS)** → 순수 예측 논문은 스쿱. **우리 차별점은 예측이 아니라 cross-cancer 치환비용 프레이밍.**

## 계산·데이터
- 계산기: **CMScaller(Eide 2017, NTP·템플릿 내장·단일샘플·플랫폼 독립)** 권장 / CMSclassifier(RF+SSP)로 교차확인. **둘 다 R** (native Python 없음; 템플릿은 pyreadr로 추출 가능). 두 알고리즘 concordance ~0.83(불일치 존재 — 사용자 경험과 일치).
- TCGA-COADREAD CMS 라벨: 공개는 Synapse(syn2623706/4978511, 로그인) / **UCSC Xena `CMS_subtype`(로그인 불필요)**. TCGA subset ~577샘플, ~13% unclassified.
- **권장 경로(BRCA PAM50 자가계산 방식 재현):** TCGA-COADREAD RNA-seq에 **CMScaller로 CMS 자가계산** + Xena 공개콜로 concordance 검증. Synapse 로그인 우회.

## 결정 (조사 권장 = 세 라벨을 역할 나눠 사용)
1. **CMS1-4(계산) = PAM50-격 아형 축.** H&E→아형 예측 비교(CMS1/CMS4 예측 잘, CMS2/CMS3 미묘).
2. **MSI-H/MSS = H&E가 저비용으로 대신 가능한 치료 축**(예측 잘 + 치료 연관, 대체로 CMS1과 겹침).
3. **RAS/BRAF-V600E/HER2-amp = 형태학적으로 조용(대체로)·치료 정의 = 유방 HER2의 진짜 CRC 격(고비용).**

## 정직한 cross-cancer 문장 (스쿱 아님)
"유방 PAM50/수용체는 아형과 치료-라우팅이 일치하지만, CRC는 둘이 분리된다 — CMS는 예후용 아형 격이고, H&E 치환비용은 MSI(저) vs RAS/BRAF/HER2-amp(고, 형태학적으로 조용)가 결정한다." 이 **비대칭**이 기여점이며 미점유.

## 다음 작업
- [ ] R env `cms-r`(설치 중)로 CMScaller 준비 → TCGA-COADREAD RNA-seq(cBioPortal) → CMS 자가계산 → Xena 검증.
- [ ] MSI-H/MSS 도출(MSIsensor≥3.5, 15.1% 검증 완료) 라벨 추가.
- [ ] H&E MIL로 CMS·MSI 예측(아형 층위) → 유방 PAM50와 like-with-like.
- 관련: `PROGRESS_DECISIONS.md`(비교 층위 정정), memory `feedback-comparison-like-with-like`.

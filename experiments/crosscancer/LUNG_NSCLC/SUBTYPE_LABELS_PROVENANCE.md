# 폐(NSCLC) 전사체 아형 라벨 — 출처·방법·커버리지 (2026-07-12, embedding agent)

> claim_level: hypothesis_only. 라벨은 H&E 결과와 **독립적으로** 제작 (사전등록 법칙 `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`의 폐 예측을 나중에 이 라벨로 검정하므로, 법칙에 맞추려는 조정 금지).
> 층위: 유방 PAM50 · 대장 CMS와 같은 **전사체 발현 아형** 층위 (LUAD/LUSC 조직형은 한 층위 아래 = 양성대조; 이 파일은 subtype만 다룸, 변이 라벨 EGFR/KRAS/histology는 `full/patient_labels.csv`에 이미 존재하며 건드리지 않음).

## 산출물
- `full/subtype_labels.csv` — case_id, cohort, luad_subtype{TRU,PP,PI}, lusc_subtype{classical,basal,secretory,primitive}, luad_subtype_orig_hayes, source, source_dataset, has_embedding.
  키는 **전체 라벨된 코호트(397 환자)** 기준 — 임베딩 진행 중(현재 762/1050)이라 임베딩 보유 케이스로 필터하지 않음. `has_embedding`은 스냅샷 정보 컬럼일 뿐.
- `subtype_data/` — 원본 소스 파일 2건 + `build_subtype_labels.py` 재생성 스크립트.

## 출처 (권위, 웹 확인)
| 아형 | 소스 | 컬럼 | 값 | 권위 근거 |
|---|---|---|---|---|
| **LUAD** TRU/PI/PP | UCSC Xena `TCGA.LUAD.sampleMap/LUAD_clinicalMatrix` | `Expression_Subtype` | Bronchioid/Squamoid/Magnoid | Hayes 2006 → **TCGA LUAD 2014 (Nature 511:543) 재명명** |
| **LUSC** 4-class | UCSC Xena pancanatlas `TCGASubtype.20170308` | `Subtype_mRNA` | classical/basal/secretory/primitive | Wilkerson 2010 / TCGA LUSC 2012 (Nature 489:519) |

- 다운로드 URL(2026-07-12 200 OK): `https://tcga.xenahubs.net/download/TCGA.LUAD.sampleMap/LUAD_clinicalMatrix` (비압축), `https://pancanatlas.xenahubs.net/download/TCGASubtype.20170308.tsv.gz`.
- **cBioPortal는 사용 불가로 확인:** `luad_tcga_pan_can_atlas_2018` `SUBTYPE` 필드 = 502건 전부 'LUAD'(조직형만), 발현 아형 없음. firehose legacy `luad_tcga`/`lusc_tcga`(106/attr)에도 Expression_Subtype 없음 → BIOP02-95 코멘트 확인.

## LUAD 이름 매핑 (TCGA 2014 재명명) + 경험적 검증
Hayes 2006 원명 → TCGA 2014 재명명:
- **Bronchioid → TRU** (terminal respiratory unit; EGFR-enriched, 예후 양호)
- **Squamoid → PI** (proximal-inflammatory; NF1/TP53)
- **Magnoid → PP** (proximal-proliferative; KRAS/STK11)

이 매핑을 우리 코호트의 기존 변이 라벨로 **자체 검증**(SSP 자가계산 대신):
| Hayes 원명 | n | EGFR-activating % | KRAS-G12C % | 판정 |
|---|---|---|---|---|
| Bronchioid | 87 | **18.4%** (최고) | 16.1% | → TRU (EGFR-enriched) ✓ |
| Squamoid | 77 | 7.8% | 7.8% | → PI (중간, 소거법) ✓ |
| Magnoid | 63 | 3.2% (최저) | **25.4%** (최고) | → PP (KRAS-enriched) ✓ |

Bronchioid가 EGFR 최고, Magnoid가 KRAS 최고 — 재명명 방향과 일치. **이 검증은 순환 아님**: 분자 공발생(EGFR/KRAS 변이)으로 "어떤 Hayes-이름이 어떤 재명명 아형인가"만 확인한 것이고, 사전등록 법칙의 held-out 검정("H&E→TRU 예측")은 **형태학 대 변이**라는 다른 변수라 직교한다.

## 조인 커버리지 (전체 코호트 1050 = LUAD 566 + LUSC 484)
- **LUAD**: 227/566 아형 라벨(40.1%). TRU 87 · PI 77 · PP 63. (임베딩 보유분 191: TRU 78 · PI 61 · PP 52)
- **LUSC**: 170/484 아형 라벨(35.1%). classical 63 · basal 42 · secretory 39 · primitive 26. (임베딩 보유분 146: classical 54 · basal 36 · secretory 34 · primitive 22)
- **합계 397 환자 라벨**(임베딩 현재 보유 337; 임베딩 762/1050 진행 중이라 증가 예정).
- 커버리지 한계 사유: marker-paper 발현 아형은 **원 TCGA 코호트만** 커버 → 우리 GDC 진단슬라이드 확장 코호트(~1050)의 절반 이하만 라벨됨. 이는 대장 CMS(authoritative 574) 흡수와 동일 성격의 정상적 한계.

## 미확보 / 미실행 (정직 기록)
- **계산(SSP) 검증 = 미실행.** 대장은 authoritative(Xena) + CMScaller(계산) 두 결과로 concordance 84%를 보고했으나, 폐는 **권위 라벨이 LUAD·LUSC 둘 다 확보**되어 authoritative-only로 진행. LUAD Wilkerson centroid / LUSC Wilkerson centroid를 이용한 nearest-centroid SSP 자가계산 및 concordance는 **아직 돌리지 않음**(추후 검증 항목). concordance 수치를 지어내지 않음.
- 라벨 없는 케이스(LUAD 339, LUSC 314)는 `subtype_labels.csv`에서 **제외**(누락 = unlabeled). 향후 SSP로 보강 가능.
- LUSC를 자체 Xena `LUSC_clinicalMatrix`에서도 찾으려 했으나 `Expression_Subtype` 컬럼 없음 → pancan `Subtype_mRNA`가 유일 권위 소스.

## 치료-라우팅 긴장 (참고, `LUNG_SUBTYPE_INVESTIGATION.md` §치료-라우팅)
전사체 아형은 임상 치료를 라우팅하지 않음(연구/예후용) — 유방 PAM50·대장 CMS와 동일 성격. 폐 조직형(LUAD/LUSC)이 실제 화학요법 라우팅 축(pemetrexed 등)이나, 그것은 양성대조 층위이며 이 파일 범위 밖.

관련: `LUNG_SUBTYPE_INVESTIGATION.md` · `CRC_SUBTYPE_INVESTIGATION.md`(대칭 설계) · `SUBSTITUTABILITY_LAW_PREREGISTRATION.md` · `COLORECTAL/cms_data/CMS_CONCORDANCE.md`(대장 대응물).

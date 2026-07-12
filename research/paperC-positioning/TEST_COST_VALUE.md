# 검사 비용 · H&E-triage 가치 분석 (2026-07-12)

> 사용자 질의("각 검사 비용?"). 출처 기반 근사치 — **논문엔 CMS CLFS/health-econ 논문으로 재검증 필요**(값은 국가·payer·연도·랩마다 크게 변동). claim_level: hypothesis_only.

## 검사별 대략 비용 (USD, 2024-25 근사)
| 검사 | 근사 비용 | 비고 |
|---|---|---|
| **H&E 슬라이드** | **~$11–25/슬라이드** | 이미 모든 케이스에 표준 제작 → 한계비용 ≈0. AI 추론은 compute 수 센트. |
| HER2 **IHC** | ~$80–250 | 지역랩서 쉽게, 저렴 |
| HER2 **FISH** | ~$300–600+ ("HER2 test" 전체 $300–3000 범위) | IHC의 3–4배, 느림. IHC equivocal 시 reflex |
| **MSI**(PCR) / MMR IHC | MSI ~$500 · MMR IHC 2–4항체 ~$80–200 | Lynch/면역치료 위해 **CRC·자궁내막 보편 검사 권고** |
| **NGS 패널**(표적) | **~$1,269–2,058 평균** (TMB 포함 $438–3,700, >50유전자 ~$1,948) | EGFR/KRAS/BRAF 등 변이. 대형 패널은 비용효과 낮음 |

출처: 히스토 코어 요율(JHU/UCDavis 등 $11–25), HER2 IHC vs FISH 비용비([AACR 2009](https://aacrjournals.org/cancerres/article/69/24_Supplement/6037/551525/), [PMC2783254](https://pmc.ncbi.nlm.nih.gov/articles/PMC2783254/)), MSI/MMR([PMC8409214](https://pmc.ncbi.nlm.nih.gov/articles/PMC8409214/)), NGS([Value in Health 2024](https://www.valueinhealthjournal.com/article/S1098-3015(24)02357-X/fulltext), [micro-costing PMC9330154](https://pmc.ncbi.nlm.nih.gov/articles/PMC9330154/)).

## 비용 gradient가 주는 핵심 통찰 (가치가 어디에 있나)
H&E(~$15) → IHC(~$150) → FISH(~$400) → NGS(~$1,500–2,000). **H&E-triage의 절감 가치는 "triage 가능(H&E-예측됨) AND 검사가 비싸거나 고volume"인 마커에 집중.**

- **MSI = sweet spot**: H&E 예측 가능(~0.9, Kather) + 검사비 $200–500 + **모든 CRC/자궁내막 보편 검사 권고**(고volume). → H&E pre-screen이 보편 MSI 검사 volume·비용을 실제로 줄일 수 있음(Kather의 원 pitch).
- **HER2 = 가치 낮음(이중 이유)**: (i) H&E-blind라 triage 불가, (ii) 설령 가능해도 **IHC가 저렴**($80–250)이라 절감 여지 작음. → HER2는 "분자검사 필수" 극점의 **눈금**이지 절감 대상 아님.
- **NGS 변이(EGFR/RAS) = 역설**: 검사가 가장 비싼데($1,500+) 하필 **H&E-blind**라 triage 불가 → 비싼 데서 못 아낀다(정직한 한계). 단 "여기선 반드시 NGS" 자체가 결정지도의 유용한 출력.

## 함의 (논문 프레이밍)
- 결정지도의 임상 payoff = **triage 가능 × 검사 부담 큰** 교집합. **MSI가 대표 성공 사례**, 값싼 IHC(HER2)나 blind 변이(RAS)는 절감 대상 아님.
- 자원제한(LMIC)·고volume 스크리닝·reflex 우선순위에서 H&E의 보편·저비용이 특히 값짐.
- 결정지도 그림에 **마커별 검사비용을 병기**하면 "어디서 실제로 아끼나"가 한눈에.

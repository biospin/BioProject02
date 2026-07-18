# 타깃 저널 집필 가이드 — npj Precision Oncology (그 수준 이상으로)

이 문서는 우리 원고를 타깃 저널에 실린 우수 논문과 같거나 그 이상 수준으로 쓰기 위한 기준선이다. 저널의 공식 규정과, 실제로 그 저널에 실린 H&E→분자 예측 논문들의 de facto 관행(논리·포맷·표·그림)을 함께 담는다.

## 1. 타깃 저널 (확정)

- **주 타깃: npj Precision Oncology** (Nature Portfolio, 완전 Open Access, 온라인 전용). 모달 IF ~6–12. 근거 [../research/paperC-positioning/FLAGSHIP_PLAN.md:55-57](../research/paperC-positioning/FLAGSHIP_PLAN.md), [../research/README.md:8](../research/README.md).
- **스트레치: Nature Communications / npj Digital Medicine / Med** — 사전등록 법칙이 예측적으로 서고 3암종이 깨끗하며 AI 결정레이어가 "새 능력"으로 읽힐 때.
- **같은 저널 최근접 경쟁작: Dawood 2024**(npj Prec Onc, H&E→약물감수성). 우리 차별점 = 예측 정확도 경쟁이 아니라 "언제 대체가 안전한가"라는 다른 질문 + 사전등록 법칙 + 실제-결과 앵커.

## 2. 저널 공식 규정 (2026-07 확인분)

npj Precision Oncology는 온라인·완전 OA라 **엄격한 단어수·페이지 제한이 없고 간결한 서술을 강하게 권장**한다. **포맷 요건은 게재 확정 시에만 적용**되며, 초기 투고는 심사에 적합하게 기술되기만 하면 되고 **그림을 본문 적절한 위치에 삽입**하는 것을 심사자들이 선호한다. (출처: 저널 submission guidelines 검색 요약 — 정확한 abstract 상한 등 세부 수치는 게재 준비 단계에서 저자 가이드 원문 재확인.)

> ⚠️ nature.com 저자 가이드 원문은 로그인 리다이렉트로 직접 크롤이 막혀, 위는 검색 요약 기준이다. 초록 단어 상한·인용 스타일(Nature 상첨자 번호) 등 **게재 확정 단계에서 원문으로 재확인** 필요 — `<FILL: 저자 가이드 원문 수치>`.

## 3. 우리가 이미 갖춘 보고 표준 (반드시 적용)

예측 모델·의료영상 AI 논문의 신뢰도는 보고 표준 준수로 갈린다. 이미 도입해 둔 체크리스트를 원고에 실제로 매핑한다:

- **TRIPOD+AI** — 예측모델 AI 확장. [../docs/reporting_checklists/TRIPOD_AI.md](../docs/reporting_checklists/TRIPOD_AI.md)
- **CLAIM 2024** — 의료영상 AI. [../docs/reporting_checklists/CLAIM_2024.md](../docs/reporting_checklists/CLAIM_2024.md)
- **PROBAST-AI** — 편향위험. [../docs/reporting_checklists/PROBAST_AI.md](../docs/reporting_checklists/PROBAST_AI.md)
- 관찰연구 서술 요소는 STROBE 참고. 개요 [../docs/reporting_checklists/README.md](../docs/reporting_checklists/README.md)

게재 단계에서 이들 체크리스트를 채운 표를 Supplement로 첨부한다.

## 4. exemplar 정독 결과 — 우수 논문의 골격 (요약)

npj Precision Oncology에 실린 H&E→분자 예측 논문 4편(자궁내막 아형·자궁경부 CMS·NSCLC actionable biomarker·Dawood 2024 약물감수성)을 실제로 정독했다. **상세 해부(논문별 7축 분석 + 종합)는 [WRITING_TARGET_GUIDE.md](WRITING_TARGET_GUIDE.md)에 있다.** 여기엔 우리 원고에 직결되는 결론만 옮긴다.

- **섹션 구조:** 예외 없이 IMRaD(Abstract→Intro→Results→Discussion→Methods)에 **Results를 6~10개 주장형 소제목으로 분할**("Prediction of X from H&E", "Histological patterns associated with Y"). 본문은 장문(8,000어급), 성능 상세는 supplementary로.
- **그림(5~9개):** 네 유형의 조합 — (i) 파이프라인/개념 스키매틱, (ii) ROC+AUC 성능 패널, (iii) 해석가능성 overlay(Grad-CAM/attention — 단 검증형 논문은 생략), (iv) "왜 되는가"를 파는 정량 연관 그림(세포조성·TME·핵형태). Fig1이 꼭 파이프라인은 아님(성능을 앞세우기도).
- **표:** 본문 표는 최소(3편은 본문 표 0개, 전부 supplementary). 필수는 **코호트 특성표**. ★핵심: Paper B의 **"Digital-대체물 vs 분자-원본을 DeLong C-Index 동등성 검정"**이 우리 cost-of-substitution 논지의 표 원형.
- **성능보고:** AUROC + 95% CI가 규범. **외부 site-disjoint 검증 유무가 "강한 논문 vs proof-of-concept"를 가르는 최대 단일 요인.** 검증형 논문은 AUC뿐 아니라 **NPV/PPA/PPV를 이중보고**해 "실제로 검사를 생략/triage할 수 있나"에 답함.
- **엄밀성:** 4편 모두 **TRIPOD/CLAIM/STARD 명시 0 · 사전등록 0**. → 우리가 사전등록 + 체크리스트를 명시하면 modal을 넘어선다.
- **임상 위치:** 전부 **"대체가 아니라 triage/보완/human-in-the-loop"**로 낮춰 잡음. 우리 제목이 "언제 대체 가능한가"라도, 톤은 **"대체가 정당화되는 조건을 지도로 명시"**여야 저널 정서와 충돌 안 함.

> ⚠️ WRITING_TARGET_GUIDE.md의 수치 중 **초록 헤드라인은 Europe PMC 원문 JSON으로 재검증 완료**(Paper A 0.867·Paper C 0.87/0.96/0.88/0.83 등). 요약모델 훼손은 Paper A p53abn CI 상한 1.003(실제 1.000) 한 곳뿐이었다. **다만 본문 전용 수치**(Paper B AUC 0.78–0.85, 코호트 n, Paper D SCC)는 초록에 없어 여전히 미검증 — 인용 시 원문 PDF 대조 필수. 구조·논리·형식 관찰은 신뢰 가능.

## 5. 우리 자산 ↔ exemplar 관행 갭 분석 (월요일 우선순위)

modal 관행 대비 우리가 가진 것/부족한 것. "없음" 항목이 월요일 이후 만들 것.

| exemplar 관행 | 우리 현재 | 상태 | 조치 |
|---|---|---|---|
| IMRaD + Results 6~10 주장형 소제목 | sections/02_results 골격 있음(R1~R5) | 부분 | 소제목을 주장형 문장으로 |
| 파이프라인 스키매틱 (Fig1) | braveji Fig1 pipeline 있음 | 갖춤 | 결정지도 개념도로 확장 검토 |
| ROC+AUC 성능 패널 | 5암종 AUC+CI 결과 有, 통합 성능그림은 미제작 | 부분 | 5암종 겹친 비교 성능그림 신규 |
| 결정지도/cost 그림 | Fig2(confusion×distance+cost)·Fig3(축별 cost+CI) 있음 | 갖춤 | Critic 서명 후 확정 |
| 해석가능성 overlay | CLAM attention 있으나 그림 미제작 | 없음 | (선택) attention overlay — "발견형" 표지 |
| 코호트 특성표 (Table 1) | 없음 | **없음** | **월요일 우선 — 5암종 n·라벨 유병률·split 표** |
| 대체 동등성 통계검정 (DeLong C-Index) | cost 프레임 有, 명시적 동등성/열위 검정 없음 | **없음** | **엔드포인트별 "H&E 대체 vs 분자 원본" 동등성/열위 표 설계** |
| 외부 site-disjoint 검증 | 코호트내 site-disjoint holdout 有, 다기관 외부 검증은 Yale 앵커(pending) | 부분 | 정직하게 한계 서술 + Yale로 보강 |
| NPV/PPA 임상효용 이중보고 | AUC 중심, NPV 미보고 | **없음** | **NPV("H&E-negative면 분자검사 생략 가능?") 추가 — cost 논문에 필수** |
| 사전등록 | SUBSTITUTABILITY_LAW_PREREGISTRATION.md 봉인 | **갖춤(차별화)** | 본문에 명시 |
| TRIPOD/CLAIM 체크리스트 | docs/reporting_checklists/ 도입됨 | **갖춤(차별화)** | 채운 표 Supplement |
| 코드/데이터 가용성 statement | repo 있음, statement 미작성 | 없음 | Methods 말미에 |

**월요일 우선순위 3가지(갭 중 임팩트 순):** ① 코호트 특성표(Table 1) ② 대체 동등성 검정 표(Paper B 원형) ③ NPV 임상효용 이중보고. 이 셋이 우리 결과를 modal 수준으로 끌어올리고, 사전등록+체크리스트가 그 위로 넘어서게 한다.

## 6b. Preprint → 저널 경로 (허용됨)

npj Precision Oncology(Nature Portfolio)는 **preprint를 명시적으로 허용**하며 선출판으로 보지 않는다. 실무:
- **서버:** 임상 엔드포인트(Yale pCR·TCGA clinical)를 다루므로 **medRxiv가 정합**(bioRxiv는 임상데이터 반려 사례).
- **공개:** 투고 시 커버레터에 preprint DOI 명시. 게재본에 preprint 링크.
- **엠바고:** preprint 게시는 자유, 단 저널 게재 전 적극적 언론 홍보는 자제(Nature 정책).
- **타이밍:** 저널 투고 시점에 맞춰 올려 우선권 확보 + 리뷰 병행.
- ⚠️ **내부 게이트(공개 전 필수):** 저자·소속·순서·corresponding·GPU 제공처(Modulabs) 확정 + 팀 합의 + 결과 Critic 서명(`critic_status: pass`). preprint도 외부 공개라 이 게이트를 먼저 통과. → 경로: **결정지도 결과 Critic 통과 → 저자정보 팀 합의 → medRxiv preprint + npj Precision Oncology 동시 투고.**

## 6. 집필 원칙 (이 저널 수준 이상)

- **헤드라인 숫자는 실측 결과 파일에서만**(README 실측 표). 지어내지 않는다. `hypothesis_only` 유지, Critic 서명 전 승격 금지.
- **인용은 verify_citations.py 기계 검증** 후 확정. 눈으로 보지 않는다.
- **정직한 음성을 정면에**(위 diffuse) — 이 저널 우수 논문은 한계·음성결과를 숨기지 않는다.
- **보고 표준 매핑표를 Supplement로** 첨부해 신뢰도 확보.

# TRIPOD+AI × Paper C 매핑표 (1차)

**작성:** braveji (Critic 총괄) · 2026-08-19 · BIOP02-76
**대상 원고:** [`manuscript/DRAFT_paperC_full_ko.md`](../../manuscript/DRAFT_paperC_full_ko.md) (국문 완전 초안 v2, 202줄)
**체크리스트 원문:** [`TRIPOD_AI.md`](TRIPOD_AI.md) (TRIPOD+AI 2024, 48항목)

> **왜 지금인가.** `README.md`가 *"초안이 다 나오면 이 항목들을 하나씩 우리 원고와 대조한다"*고 적어 두었고, 초안이 완성됐다. 체크리스트는 2026-07-22 도입 이후 **한 번도 원고에 매핑된 적이 없었다**(근거 참조 0건). `TARGET_JOURNAL_GUIDE.md:36`은 비교 논문 4편이 *"TRIPOD/CLAIM/STARD 명시 0 · 사전등록 0"*이라며 이 매핑을 **차별화 지점**으로 지목한다 — 즉 이 표 자체가 Supplement 자산이다.
>
> ⚠️ **이 표는 감사이지 집필이 아니다.** braveji는 원고 문안을 쓰지 않는다(Owner≠Reviewer). 미충족 항목은 **집필 담당에게 넘기는 명세**다.

## 판정 기준

- ✅ **충족** — 원고에 해당 정보가 실제로 있고 위치를 지목할 수 있다
- 🟡 **부분** — 있으나 항목이 요구하는 수준에 못 미친다(구체 명세를 함께 적었다)
- ❌ **미충족** — 원고에 없다
- ➖ **해당없음** — 연구 설계상 성립하지 않는다(사유 명기)

---

## 요약

| 판정 | 수 | 비고 |
|---|---|---|
| ✅ 충족 | **21** | Methods 전처리·검정력·대조군·한계 서술이 특히 강하다 |
| 🟡 부분 | **9** | 대부분 한두 문장 추가로 닫힌다 |
| ❌ 미충족 | **13** | **Table 1 · 코드/모델 공개 · Funding · 학습 하이퍼파라미터**가 핵심 |
| ➖ 해당없음 | **5** | 딥러닝이라 회귀계수·predictor별 단변량이 성립 안 함 |

**투고 전 반드시 닫아야 할 것 5건** — 제목(1·1-AI) · **Table 1(13b)** · 코드/모델 공개(15-AI·21-AI) · **Funding(22, Modulabs 명시 조건)** · 소프트웨어/하드웨어(10-AI-c).

---

## Title and Abstract

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 1 | Title | ❌ | **정식 제목 미확정.** 현재 문서명은 "Paper C — 국문 완전 초안 v1". 예측모델·대상 집단·예측 대상이 드러나는 제목 필요 |
| 1-AI | Title (AI) | ❌ | 제목에 AI/ML 사용 명시 필요(위와 함께) |
| 2 | Abstract | 🟡 | Abstract 존재(L13)·목적/결과/결론 충실. **연구 설계(후향적 다기관 공개코호트)와 표본수를 초록에 한 줄 추가** 권고 |

## Introduction

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 3a | Background | ✅ | §1 L19–21 — 선행연구·임상 맥락·gap 명확 |
| 3b | Objectives | 🟡 | §1 L23–27. **"개발인가 검증인가"를 명시** — 현 원고는 개발+내부/외부 평가 혼재. TRIPOD가 요구하는 구분 문장 필요 |

## Methods

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 4a | Source of data | ✅ | M1 — TCGA 5암종 + Yale(M7). 설계=후향 코호트 |
| 4b | Study dates | ❌ | **없음.** TCGA accrual 기간·Yale 수집 기간 미기재. 공개 데이터라도 코호트 기간 기재가 원칙 |
| 4-AI | Source of input data (AI) | ✅ | M2 — WSI, 20× |
| 5a | Setting | 🟡 | M1에 코호트명은 있으나 **진료 세팅(다기관 3차의료 등) 서술 없음** |
| 5b | Eligibility | 🟡 | M1 "DX 진단 슬라이드·라벨 보유"가 암묵. **포함/제외 기준을 명시적으로** |
| 5c | Treatments | ✅ | M7 — Yale trastuzumab 치료 코호트 |
| 6a | Outcome definition | ✅ | M1 — 라벨 출처·환자 단위 split |
| 6b | Outcome blinding | ❌ | **없음.** 라벨은 기존 분자검사 결과이므로 "별도 blinding 없음(라벨이 이미 확정된 검사 결과)"으로 **사실대로 기재**하면 충족 |
| 7a | Predictors | ✅ | M2 — UNI v1 1024차원 임베딩 |
| 7b | Predictor blinding | ❌ | 위와 동일 — "예측자 추출은 라벨 비참조"를 한 줄로 명기하면 닫힌다 |
| 7-AI | Preprocessing (AI) | ✅ | M2 — 256×256@20×, Otsu, 환자당 5,000 상한, 224 리사이즈, ImageNet 정규화, **염색정규화 미적용을 한계로 명시**(모범) |
| 8 | Sample size | ✅ | M1 + R2 |
| 8-AI | Effective sample size (AI) | ✅ | **R2 검정력 천장 표** — 축별 홀드아웃 양성 수 명시. 이 항목은 modal 이상 |
| 9 | Missing data | ❌ | **없음.** 라벨 결측 슬라이드 제외 규칙이 실제로는 있으므로(has_* 필터) 기재하면 충족 |
| 10a | Predictor handling | ✅ | M3 |
| 10b | Model type/building | ✅ | M3 — CLAM-SB attention MIL |
| 10c | Validation predictions | ✅ | M3·M4 — 슬라이드 단위 산출 후 환자 집계 |
| 10d | Performance measures | ✅ | M4 — AUROC·부트스트랩 CI·대조군 3종 |
| 10e | Model updating | ➖ | 재보정(recalibration) 미수행 |
| 10-AI-a | Architecture (AI) | ✅ | M3 — hidden 512 · attention 256 |
| 10-AI-b | Training procedure (AI) | 🟡 | M3에 epoch(40–50)·seed(42)만. **optimizer·learning rate·batch size·조기종료 기준 누락** |
| 10-AI-c | Software/hardware (AI) | ❌ | **원고에 없음.** 실측값은 이미 있다(`CLAUDE.md`: Python 3.13 · torch 2.6.0+cu124 · CUDA 12.4 · RTX A6000 49GB×3) — 옮겨 적으면 충족 |
| 10-AI-d | Reproducibility (AI) | 🟡 | M6·M8에 seed·결정론 2회 재실행 ✅. **코드 공개 여부 미기재**(21-AI와 함께) |
| 11 | Risk groups | ➖ | 위험군 층화 없음. 치료축 라우팅이 유사 개념이나 TRIPOD의 risk group과는 다름 |
| 12 | Development vs validation 차이 | ✅ | M7 — Yale은 코호트·결과변수(pCR)가 다름을 명시 |

## Results

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 13a | Participant flow | 🟡 | 슬라이드 수는 M1·R1에 있으나 **flow(적격→제외→분석) 서술 없음.** 제외 사유별 수 필요 |
| 13b | Characteristics | ❌ | **Table 1 미작성.** 원고 L195가 "예정"으로 자인. **TRIPOD 필수이자 저널 가이드가 "필수는 코호트 특성표"로 지목**(L34) |
| 13c | Validation vs development 분포 비교 | ❌ | Yale vs TCGA 분포 비교 없음 |
| 14a | n & events per analysis | ✅ | 표 R1·R2 — 축별 n·양성 수 |
| 14b | Unadjusted association | ➖ | 딥러닝 — 후보 예측자별 단변량 연관 성립 안 함 |
| 15a | Full model | ➖ | 딥러닝 — 회귀계수 제시 불가 |
| 15b | How to use | 🟡 | 라우팅 규칙은 M5에 있으나 **"이 모델을 어떻게 쓰는가"의 사용자 관점 서술 없음** |
| 15-AI | Model availability (AI) | ❌ | **코드·가중치 공개 여부 미기재.** 15a가 ➖인 만큼 이 항목이 그 자리를 대신해야 한다 |
| 16 | Performance with CIs | ✅ | 표 R1 — AUROC + 95% CI 전 축 |
| 16-AI | Fairness / subgroup (AI) | ❌ | **인구통계(연령·성별·인종) 층화 성능 없음.** site 감사(M9)는 있으나 demographic fairness는 별개. TCGA에 해당 변수가 있으므로 산출 가능 |

## Discussion

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 18 | Limitations | ✅ | §3 + 한계 절 — 검정력·후향·단일분할·염색정규화 미적용 등 |
| 19a | Interpretation vs development | ✅ | R4 — 개발셋 0.963 vs 홀드아웃 0.536 대조로 해석 |
| 19b | Overall interpretation | ✅ | §3 |
| 19-AI | Bias sources (AI) | ✅ | R4(기관 분리) · M9(site/batch 감사) · R1 각주 ‡(조직형 V=1.000) — **modal 이상** |
| 20 | Implications | ✅ | §3 L151 — 임상 함의·전향 검증 필요 명시 |

## Other Information

| # | 항목 | 판정 | 원고 위치 / 필요 조치 |
|---|---|---|---|
| 21 | Supplementary information | 🟡 | 목록은 L186–195에 있으나 **미완**(Fig4·5·SFig1·Table 1 예정) |
| 21-AI | Code and model availability (AI) | ❌ | **미기재.** 저장소 공개 범위·라이선스 결정 필요(FM 라이선스가 전부 비상업 학술이라 가중치 재배포 가능 여부 확인 필요) |
| 22 | Funding | ❌ | **미기재.** GPU 제공처(Modulabs) Acknowledgments 명시는 **자원 제공 조건**이다(`CLAUDE.md` Infrastructure). 저자정보 확정과 함께 닫힌다 |

---

## 집필 담당에게 넘기는 명세

**A. 한 문장으로 닫히는 것 (7건)** — 사실을 옮겨 적으면 충족
`4b` 코호트 기간 · `6b`/`7b` blinding 없음을 사실대로 · `9` 라벨 결측 제외 규칙 · `10-AI-c` 소프트웨어/하드웨어(값은 `CLAUDE.md`에 실측 존재) · `3b` 개발/검증 구분 · `5b` 포함·제외 기준

**B. 산출물이 필요한 것 (4건)**
`13b` **Table 1 코호트 특성표**(류재면 담당 — `SECTION_ASSIGNMENT_paperC.md`) · `13a` participant flow · `13c` Yale↔TCGA 분포 비교 · `16-AI` 인구통계 층화 성능

**C. 팀 결정이 필요한 것 (4건)**
`1`/`1-AI` 정식 제목 · `15-AI`/`21-AI` 코드·모델 공개 범위와 라이선스 · `22` Funding·Acknowledgments(저자정보 게이트와 동시) 

**D. 우리가 modal을 넘어선 것 (인용 가치)**
`8-AI` 검정력 천장 정량화 · `7-AI` 전처리 상세 + 염색정규화 미적용 자진 명시 · `19-AI` site 교란 감사와 양성대조 한계 자진 공개 · `10-AI-d` 사전등록 + 결정론 재실행

---

## 남은 체크리스트

`CLAIM_2024`(영상 AI, 72항목) · `PROBAST_AI`(편향위험) · `STROBE`(Yale 관찰 코호트)는 **아직 매핑 전**이다. TRIPOD+AI와 항목이 상당수 겹치므로 이 표를 기준으로 차이분만 매핑하면 된다. 우선순위는 CLAIM > PROBAST > STROBE(Yale 앵커 절 한정).

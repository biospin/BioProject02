# fernandez-romero-2026-domaingen — Methodology Brief (우리와의 차별화 정밀 정의)

> ★가장 중요★ 이 논문은 우리 **NEAREST SCOOP**이다 — 유방 "Paper A"를 flagship Paper C(치환비용 결정지도)로 흡수하게 만든 직접 원인. 아래는 리뷰어의 "이거 스쿱 아니냐"에 대한 정밀 반박 설계. 모든 우리쪽 산출물은 **`hypothesis_only`**, 후향적, 전향 검증 필요.

## A. 차별화 표 (THEY vs WE)

| 축 | THEY (Fernandez-Romero 2026) | WE (Paper C: cost-of-substitution 결정지도) |
|---|---|---|
| **묻는 질문** | H&E로 분자 아형/마커가 **예측되는가** | 그 예측이 치료결정에서 **분자검사를 언제 값싸게 대체하나** |
| **측정량** | 예측 정확도 **PR-AUC(ER/PR/HER2)·macro-F1(PAM50)** + 열화 **RPD** | **라우팅 치환비용** = mis-routing cost × therapeutic distance (라벨오차↔치료오차 해리) |
| **출력** | 모델 순위 + 도메인 붕괴 진단 | 마커별 {H&E-triage 가능 / 등급적 / 분자검사 필수} **결정지도** + 보정/기권 |
| **층위** | 예측충실도(표1) 단일 | 예측충실도(표1)와 **라우팅비용(표2)을 분리**(층위 융합 금지) |
| **범위** | 유방 단일 | 유방 anchor + **폐·대장·위·두경부 5암종**(사전등록 법칙 held-out) |
| **외부 열화** | 발견·계량(RPD, 요인분해 R²=0.800) | **동일 현상을 "치환에 비용이 있다"의 증거로 재활용** → 결정레이어 동기 |
| **임상 정박** | 없음(exploratory 벤치) | **(계획) trastuzumab 치료-결과 anchor**로 HER2 라우팅 비용을 실측 임상에 정박 |
| **거버넌스** | 표준 벤치 | `hypothesis_only` + 7-point Critic + DRP 금지 |

## B. 리뷰어 방어 3점 (핵심)

**(a) 측정 대상이 다르다 — accuracy vs decision-value.**
그들은 *예측이 맞나*(PR-AUC/F1)를 잰다. 우리는 *예측을 치료배정에 쓸 때 무엇을 잃나*(routing-cost)를 잰다. 지표부터 다름: 그들 **PR-AUC/macro-F1 ≠ 우리 AUROC ≠ 치료-랭킹 divergence**. "같은 숫자 다시"가 아니라 **다른 질문**. 예: LumA↔LumB 오분류는 예측오차이나 둘 다 내분비/CDK4-6로 라우팅 → **치료비용≈0**; 이 해리는 그들 정확도 표에서 복원 불가.

**(b) 그들의 붕괴 발견이 우리 논지를 SUPPORT한다(스쿱을 근거로 전환).**
**HER2-enriched RPD=1.000(외부 완전 붕괴)**, Virchow v2 HER2 PR-AUC 0.399→0.219 — **"예측만으로는 취약"의 직접 증거**. 예측이 도메인 시프트에서 무너진다면 → **치환에는 계량 가능한 비용이 있고, 보정·기권(calibration/abstention) 결정레이어가 필요**하다. 즉 그들 결과는 우리 SUBSTITUTABILITY_LAW("저비용 대체는 in-domain 조건부, cross-domain엔 보정·기권 필요")의 **외부 근거**다. 이게 가장 강한 반박: 스쿱이 아니라 우리 전제의 확증.

**(c) 우리는 그들에게 없는 실제 치료-결과 검증을 더한다(계획).**
그들은 exploratory 예측 벤치에 그침. 우리는 **HER2 라우팅 비용을 trastuzumab 치료-결과 anchor**로 정박해 "형태 오분류 → 항HER2 잘못 라우팅"의 임상 대가를 보인다.
- ⚠️ **정직 경계:** 이 anchor는 **계획된 차별자(hypothesis_only)이지 완료된 검증이 아님.** PAPER_DIRECTION이 명시하듯 TCGA OS event <15%·CPTAC survival 외부검증 불가 → **검정력 게이트 통과 전 본문 승격 금지**. 미달 시 순수 분자-특성화(HER2 단백질 상승 but 형태 상관물 없음)로 후퇴.

## C. de-circularization (그들도 우리도 걸리는 함정)
- 그들 지표(PR-AUC/F1)를 그대로 치료비용으로 승격하면 **층위 오류**. 우리는 **표1(예측충실도)과 표2(라우팅비용)를 절대 하나의 "비용" 숫자로 합치지 않음**.
- "subtype AUC 높으면 약물랭킹 당연 일치"(순환) 반박: concordance가 아니라 **임상 비용함수**(subtype-구별 약물에서만, 아형별 층화, subtype_only→therapy baseline 대비)로 측정 → 라벨오차↔치료오차 해리가 발견.

## D. BIOP02 연계
- **cost-of-substitution(C1):** 세포주-only 냉동 지도에 (A)측정 아형 vs (B)H&E-예측 아형 → 치료 랭킹 divergence 아형별 층화. HER2 붕괴 지점 = 그들 RPD=1.00과 교차 인용.
- **AI 결정레이어:** OOD/불확실 시 분자검사로 기권 — **동기 = 그들 CPTAC 붕괴 + staining/feature-space 80% 요인**.
- **인용 규율:** 정성 한 줄 양보("consistent with [Fernandez-Romero 2026]") 후 결정-가치로 전환. 예측 정확도 재판매·figure 방어 금지.

## 검증 플래그
- 이중확인: 설계·코호트·HER2/Normal-like 붕괴·R²=0.800·지표종류·mean-rank.
- PMC quote-demand: MIL 3종·Virchow HER2 0.399→0.219·PAM50 0.542→0.358·RPD 공식·CPTAC flash-frozen·Code Availability.
- **[미확인/계획]** trastuzumab-outcome anchor = 우리 hypothesis_only 설계(검정력 미검증). 그들 per-model 전체표·Data Availability = [미확인].

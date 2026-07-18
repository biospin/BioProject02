# 논문 작업 폴더 (Paper C 플래그십)

이 폴더는 SpatialPathoAgent 논문을 실제로 집필하는 자리다. 지금까지 흩어져 있던 분석 결과·그림·구조 결정을 여기서 한 편의 원고로 모은다. 착수 예정일은 **2026-07-20(월)**이며, 이 문서는 그날 무엇부터 손대야 하는지를 정리한 출발점이다.

## 무슨 논문인가

한 문장으로, **"H&E 병리 이미지가 값비싼 분자검사를 언제 값싸게 대신할 수 있고 언제 대신할 수 없는가"를 다섯 암종에 걸쳐 사전등록된 결정지도로 그린 논문**이다. 핵심 프레임은 *cost-of-substitution* — "분자 표현형이 형태학적으로 예측된다"는 사실과 "그래서 분자검사를 임상적으로 대체해도 된다"는 주장은 다르다는 것. 어떤 축은 H&E에 또렷이 보이고(대신할 수 있음), 어떤 축은 보이지 않으며(대신하면 안 됨), 그 경계를 비용으로 환산해 지도로 만든다.

구조는 2026-07-17 Leader 결정으로 **플래그십 한 편**으로 수렴했다. 유방은 前 Paper A였다가 이 논문의 anchor 챕터로 흡수됐고, Yale 실제-치료결과 앵커가 "후향적-only"라는 유일한 약점을 메우러 본문에 들어온다. 무거운 약물-발견 엔진(前 Paper B)은 조건부 보류다. 이 결정의 정본은 [../research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md](../research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md)이고, 사전등록 법칙은 [../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md](../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md)에 봉인돼 있다.

## 지금 근거로 쓸 수 있는 것 (전부 실측, UNI v1)

아래 숫자는 전부 실제 결과 파일에서 읽은 값이고, **하나도 지어내지 않았다.** 다만 전부 `claim_level: hypothesis_only` · `critic_status: pending` 상태다 — 본문 헤드라인으로 올리기 전에 결정론적 재계산과 Critic 서명을 받아야 한다(아래 "검증 게이트").

| 암종 | 축 | holdout AUC [95% CI] | 근거 파일 | 지도에서의 의미 |
|---|---|---|---|---|
| 대장 | BRAF V600E | 0.868 [0.780–0.938] | [COLORECTAL/full/mil_cost_results.json](../experiments/crosscancer/COLORECTAL/full/mil_cost_results.json) | 형태학에 보임 |
| 폐(NSCLC) | LUSC 조직형 | 0.939 [0.905–0.967] | [LUNG_NSCLC/full/mil_cost_results.json](../experiments/crosscancer/LUNG_NSCLC/full/mil_cost_results.json) | 강하게 보임 |
| 두경부 | HPV 양성 | 0.959 [0.921–0.986] | [HEADNECK_HNSC/full/mil_cost_results.json](../experiments/crosscancer/HEADNECK_HNSC/full/mil_cost_results.json) | 강하게 보임 |
| 위 | Lauren diffuse | 0.536 [0.379–0.694] | [GASTRIC_STAD/full/mil_cost_results.json](../experiments/crosscancer/GASTRIC_STAD/full/mil_cost_results.json) | **안 보임 — 대체 불가**(정직한 음성) |
| 유방(anchor) | 수용체 3축 + PAM50 | Fig2/Fig3 백킹 JSON | [20260710_cost_of_substitution/](../experiments/kkkim/20260710_cost_of_substitution/) | HER2축은 항상 실패 = 대체불가 |

위 Lauren diffuse는 shuffle-null(0.82)이 real(0.54)보다 높고 CI가 0.5를 크게 물고 있다. 이건 실패가 아니라 지도의 핵심 메시지 — H&E가 값싸게 대신할 수 **없는** 축이 실제로 존재한다는 증거다. 원고에서 이걸 "정직한 음성"으로 정면에 세운다.

그림도 이미 초안이 있다. **Fig2**(confusion×distance + cost overlay, "이 한 장이 논문")와 **Fig3**(축별 cost + headline contrast CI)는 [../experiments/kkkim/20260710_cost_of_substitution/](../experiments/kkkim/20260710_cost_of_substitution/)에, 파이프라인 **Fig1**은 [../experiments/braveji/fig1_pipeline/](../experiments/braveji/fig1_pipeline/)에 있다. 둘 다 critic_status pending이라 근거 JSON 서명 전에는 헤드라인 승격 금지다.

## 아직 막혀 있는 것 (기다리되, 착수를 막지는 않음)

- **Yale 실제-결과 앵커 (A3/A4)** — 유방 anchor의 "HER2 대체불가" 주장에 실제 trastuzumab pCR 층화를 달아 실증으로 격상하는 부분. 재료(276 임베딩)는 완비됐으나, A3(sjpark: 항HER2 축 점수 산출)·A4(jhans: pCR 층화 + DeLong 검정)가 미착수다(JIRA BIOP02-80 통지됨). **이 섹션은 두 사람 결과가 와야 채워진다.**
- **다중 FM 모델-비의존성 (robustness supplement)** — 지금 백그라운드로 Virchow2·UNI2-h 임베딩이 돌고 있다(07-18 기준 HNSC 348/472, 폐까지 하루 이상). 재학습·크로스체크까지 끝나야 "법칙이 특정 FM에 기대지 않는다"를 쓸 수 있다. **본문이 아니라 보강(Supplement/robustness) 자리**이므로 월요일 착수를 막지 않는다.
- **Critic 서명** — Fig2/Fig3와 5암종 결과 전부 pending. braveji 총괄, Owner≠Reviewer.

## 타깃 저널 수준 (반드시 먼저 읽기)

집필 전 [TARGET_JOURNAL_GUIDE.md](TARGET_JOURNAL_GUIDE.md)와 [WRITING_TARGET_GUIDE.md](WRITING_TARGET_GUIDE.md)를 읽는다. 후자는 npj Precision Oncology에 실린 우수 H&E→분자 논문 4편을 정독해 논리·포맷·표·그림 골격을 해부한 문서다. 거기서 나온 **우리가 아직 없어서 만들어야 할 3가지(임팩트 순)**:

1. **코호트 특성표(Table 1)** — 5암종 n·라벨 유병률·split. (modal 논문의 거의 필수 본문 표)
2. **대체 동등성 검정 표** — "H&E 대체물 vs 분자 원본"의 통계적 동등성/열위(Paper B의 DeLong C-Index 원형). cost-of-substitution 논지의 표 원형.
3. **NPV 임상효용 이중보고** — "H&E-negative면 분자검사를 생략해도 되나". cost 논문에 필수.

## 월요일 착수 순서 (권장)

기다려야 하는 것(Yale·다중 FM)을 붙잡고 있지 말고, **이미 실측이 끝난 UNI v1 결과로 쓸 수 있는 섹션부터** 손댄다.

1. **Results를 먼저 쓴다.** 이 논문은 결정지도가 중심이라 Results가 서면 나머지가 딸려온다. 순서는 (a) 5암종 결정지도 골격 + Fig2/Fig3 서술 → (b) 유방 anchor 상세(수용체축·HER2 대체불가) → (c) 위 Lauren diffuse "정직한 음성". 소제목은 exemplar처럼 **주장형 문장**으로. 전부 위 표의 실측 숫자로.
2. **위 3가지 갭을 병행 제작** — 코호트 특성표·동등성 검정·NPV. 결과가 modal 수준에 오르는 지점.
3. **Methods를 병행한다.** 타일링·UNI 임베딩·CLAM-MIL·site-disjoint holdout·shuffle-null·사전등록 법칙 — 전부 코드와 결과 파일이 있어 지금 쓸 수 있다.
4. **Introduction은 literature-scout 결과 위에서.** 분야 포화·스쿱(Fernandez-Romero 2026, Dawood 2024)과 cost-of-substitution gap은 [../research/paperC-positioning/](../research/paperC-positioning/) 스카웃 문서에. gap은 **분자검사 비용/접근성 통계로 수치화**해 연다(exemplar 관행).
5. **Yale 섹션과 다중 FM 보강은 placeholder만** 잡아두고, A3/A4·재학습 결과가 오면 채운다.

## 검증 게이트 (본문 헤드라인 승격 전 필수)

CLAUDE.md "완료의 정의"를 따른다. 어떤 숫자도 본문 헤드라인으로 올리기 전에:
1. **결정론적 재계산** — 캐시·이전 세션 출력을 믿지 않고 헤드라인 AUC/CI를 다시 계산해 결과 요약과 대조.
2. **Critic 서명** — `critic_status: pass`(7-point, Owner≠Reviewer). braveji 총괄.
3. **claim 규율** — 사전등록 법칙 held-out 검정 전까지 Paper C headline은 provisional. `hypothesis_only` 유지.
4. **인용 검증** — 참고문헌은 [../agents/critic/scripts/verify_citations.py](../agents/critic/scripts/verify_citations.py)로 기계 검증. 눈으로 보지 않는다.

## 폴더 구성

- `sections/` — 섹션별 원고(00_abstract, 01_introduction, 02_results, 03_methods, 04_discussion). 각 파일 상단에 근거 파일 포인터와 아직 못 채운 `<FILL>` 표식.
- `figures/` — 최종 그림과 캡션. 지금은 실험 폴더의 초안을 참조만 하고, 서명 후 여기로 확정본을 모은다.
- 이 `README.md` — 착수 지점과 상태.

집필은 `.claude/agents/manuscript-writer.md` 에이전트로 진행하되, **헤드라인 숫자·주장은 위 실측 표와 결과 파일에서만 가져오고 지어내지 않는다.**

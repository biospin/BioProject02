# Paper C 교차암종 held-out — Critic 검토 (G2)

> **critic_status: `reject` (서명 거부, blocking)** · reviewer: **braveji** · owner: **kkkim** · 2026-07-14
> 검토 대상 커밋: `5232dfe` (`docs/BIOP02-53-kkkim-critic-review`)
> 기계판독 산출물: [`critic_report.json`](./critic_report.json) (schema v0.1)
> 관련: BIOP02-96 · 게이트 G2 (Paper C 브랜치 → main 병합 전제)

## 요지

**문제는 톤이 아니다.** 과대주장을 피하려는 규율 — exploratory 라벨링, 대장의 회고적 지위 자진 명시, 위암 양성대조 FAIL 자진 신고 — 은 실제로 지켜져 있다. 문제는 **그 절제된 결론조차 정본 수치가 받쳐주지 못한다**는 것, 그리고 **결정적 사실 두 개가 인계 문서에서 누락됐다**는 것이다.

---

## 블로커 1 — 위암: shuffle-null이 real을 압도 (스코어보드·LAW_TEST 양쪽에서 누락)

정본 `GASTRIC_STAD/full/mil_cost_results.json`:

| endpoint | real | **shuffle-null** | dev_auc | n_pos | n_hold |
|---|---|---|---|---|---|
| lauren_diffuse | 0.5364 | **0.8232** | 0.963 | 31 | **58** |
| erbb2_amp | 0.6444 | **0.6406** | 0.811 | 14 | 107 |
| msi_h | 0.8599 | 0.4568 | 0.899 | 24 | 107 |
| ebv | 0.9477 | 0.4129 | 0.762 | 7 | 89 |

**(a) 라벨을 무작위로 섞은 모델이 0.8232를 낸다.** 순열 라벨은 신호를 가질 수 없다. null=0.82는 라벨무관 구조(bag-size·site·염색 교란)가 AUROC를 구동하고 있다는 뜻이다. dev 0.963 → holdout 0.536과 합치면 결론은 **라벨 희소가 아니라 평가/파이프라인 결함**이다.

스코어보드는 이를 "0.54 FAIL, 파이프라인 문제 vs 데이터 희소 구분 필요"로만 적었다. **구분해 주는 그 수치(null 0.8232)가 문서에서 빠졌다.** GASTRIC LAW_TEST 표에는 HNSC와 달리 shuffle 열 자체가 없다.

**(b) erbb2_amp는 real ≈ null (0.6444 vs 0.6406, 마진 0.004).** 자기 순열 null 위로 신호가 0이다. 그런데 스코어보드 결론 2번은 이를 *"유방 HER2(0.599)와 위 ERBB2-amp(0.644)가 '증폭≠형태' 방향으로 일치"* 로 인용한다 — **신호 없는 endpoint에서 증거 가치를 끌어오고 있다.**

**(c) 반증 불가능한 채점.** 사전등록은 위 HER2-amp를 *"법칙의 가장 강한 교차장기 검정"* 으로 봉인했고 예측은 `blind ≤0.65`였다. 그러나 **아무것도 학습하지 못하는 파이프라인은 모든 endpoint에 대해 ≤0.65를 산출한다.** 양성대조가 무너진 파이프라인의 낮은 AUROC를 "blind 예측 적중"으로 채점할 수 없다. GASTRIC LAW_TEST의 `예측적중=적중` 표기는 철회 대상이다.

---

## 블로커 2 — 폐: 정본 수치 불일치 (유일한 검정력 있는 봉인 검정에서)

`LUNG_NSCLC/full/LAW_TEST.md` 헤더는 출처를 `mil_cost_results.json`으로 명시한다. 그런데 **세 endpoint 전부 불일치**한다.

| endpoint | 커밋된 JSON | LAW_TEST · SCOREBOARD |
|---|---|---|
| histology_lusc | **0.939** (n_pos 153/271, shuffle 0.4343) | 0.9247 (152/270, shuffle 0.4665) |
| egfr_activating | **0.8518** | 0.8133 |
| kras_g12c | **0.6809** | 0.6549 |

봉인 예측은 **≥0.93**이었다:

- JSON `0.939` → 예측 **적중** (깔끔)
- 문서 `0.9247` → 점추정 **미달**, CI 상한으로 구제 ("≈met")

**같은 봉인 예측에 두 개의 과학적 판정이 존재한다.** KRAS도 갈린다 — JSON `0.6809`는 `≤0.65` 라인 **위**, 문서 `0.6549`는 "경계".

대장에서는 이 드리프트(holdout151 vs 161)를 잡아 명시했으나(`COLORECTAL/full/LAW_TEST.md` §수치 정합), **폐에서는 잡지 못했다.** 어느 실행이 정본인지 불명 → 재현성 블로커.

---

## 블로커 3 — 7-point #2 필수 baseline 미충족

`CLAUDE.md` 7-point #2는 **random / subtype-only / pixel-mean** 3종을 요구한다.

- 존재: `shuffle_null` (≈random)
- `prevalence_baseline`: `{"auc": 0.5, "note": "상수예측 정의상 0.5"}` → **계산이 아니라 정의값.** 경험적 baseline이 아니다.
- **부재: pixel-mean (전 암종), subtype-only (전 암종)**

이는 형식 미비가 아니라 실질이다. **pixel-mean / bag-size 대조야말로 위암 null=0.82 같은 라벨무관 교란을 잡아내는 표준 통제**다. #2를 충족했다면 블로커 1이 코드 단계에서 검출됐다.

---

## 7-point 판정

| # | 항목 | 판정 | 근거 |
|---|---|---|---|
| 1 | Data leakage | **pass** | `split_meta` 4암종 site-disjoint · `patient_overlap: 0` · 환자단위. `run_mil_cost.py:81` early-stop dev를 **train에서** 15% 분리, 보고는 holdout(val+test)으로만 → 공식 val이 모델선택에 미사용. GASTRIC dev 0.963 vs holdout 0.536 격차가 이를 뒷받침. *(정적 검토까지이며 재실행 검증 아님)* |
| 2 | Baseline 3종 | **reject** | pixel-mean · subtype-only 부재 (블로커 3) |
| 3 | Counterfactual | **caution** | 대장만 misroute·증분 LR 존재. sealed-forward 3암종(폐/위/두경부) 부재 |
| 4 | Cross-dataset | **보류** | 블로커 해소 전 sub-check 의뢰 보류 |
| 5 | Biological plausibility | **보류** | 동상 |
| 6 | DRP framing | **pass** | 전수 grep 위반 0. 히트는 전부 준수 문장·대조 문헌 인용. 약물 구조 입력 없음 |
| 7 | Claim level | **pass** | 전 산출물 `hypothesis_only` / `critic_status: pending`. 대장 회고적 배너 자진 표기 |

### #4·#5를 sub-reviewer(sjpark/jhans)에게 넘기지 않은 이유

블로커 1·2가 살아있는 상태에서 생물학적 타당성 판단을 의뢰하면 **정본이 무엇인지도 모르는 숫자에 생물 도장을 받는 것**이 된다. Owner≠Reviewer 원칙상 sub-check 담당은 sjpark/jhans가 맞으나, **의뢰 시점은 블로커 해소 후**다.

---

## 추가 지적 (블로커는 아니나 CONFIRM 전 필수)

1. **유일한 CONFIRM이 단일 코호트·단일 시드에 걸려 있다.** 두경부 HPV 0.9594는 TCGA-HNSC 1개 코호트, seed=42, 1회 실행, 외부 복제 없음. Paper C 전체의 유일한 검정력 있는 확증인데 안전마진이 없다 → 최소 multi-seed 안정성 필요.
2. **커버리지 결손이 비무작위다.** 두경부 450/523(86%), **위암 lauren holdout 58/132 (56% 결손)**. 결손 원인이 "raw WSI 미다운로드 / 타일 실패"인데 **타일 실패는 슬라이드 품질과 상관**된다 → 무작위 결손이 아니다. HPV CONFIRM 유지를 위해 **결손군 vs 포함군의 HPV 유병률 비교**가 필요하다. 위암 양성대조는 절반 이상이 소실된 상태라 FAIL/PASS 어느 쪽으로도 해석 불가.
3. **shuffle-null 다중시드를 non-blocking → blocking으로 승격.** `routing_cost.json`이 이미 "seed=42 1회 순열, 소표본 분산 큼"을 FOLLOW-UP(non-blocking)으로 달았으나, **위암 null 0.82 관측 이후 null 불안정성은 부수 이슈가 아니라 본론**이다.
4. **BRCA-only 금칙(CLAUDE.md)**: `PROGRESS_DECISIONS.md`에 "리더 사인오프하 별도 트랙, A/B(BRCA)는 BRCA-only 유지" 기록 확인 → 거버넌스 문제 없음. **블로커 아님.**

---

## 서명 조건 (해소 시 재검토 — 통과 가능성 높음)

1. **폐 정본 확정** — JSON vs 문서 중 정본을 `commit_hash` + `split_hash`로 봉인, 3개 문서 동기화, "≥0.93 예측 적중" 서술을 확정 수치 기준으로 재서술.
2. **위암 null 결함 진단** — lauren null 0.8232의 원인 규명. 진단 전까지 **위암 전 endpoint를 스코어보드 집계에서 제외**.
3. **위암 erbb2_amp `예측적중=적중` 표기 + 스코어보드 결론 2번 인용 철회.**
4. **pixel-mean · subtype-only baseline 추가** (전 암종) — #2 충족 겸 블로커 1 진단 도구.
5. **shuffle-null ≥5 seed 평균** 재산출.
6. 위 반영 후 **#4·#5를 sjpark/jhans에 의뢰** → 재검토 → 최종 서명.

---

## 비고

이 검토는 kkkim의 작업을 깎으려는 것이 아니다. **정직하게 쓰인 문서가 정직하지 못한 숫자 위에 서 있는 상황**이며, 이대로 main에 병합되면 외부 리뷰어가 `mil_cost_results.json`을 여는 순간 폐 수치 불일치와 위암 null이 그대로 드러난다. 지금 잡는 비용이 훨씬 싸다.

G1(결과 확정)의 "확정"은 **결과셋 동결**이지 **수치 정합성 검증**이 아니었다 — 스코어보드 스스로 그렇게 정의했다. G2가 잡아야 할 것이 정확히 이 정합성이며, 위 3개 블로커가 그것이다.

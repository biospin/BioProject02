# Subtype 치료결정 지도 — Paper A 핵심 메시지 (2026-07-10)

> 작성: kkkim. 상태: **예비(PAM50 라우팅), claim_level=sanity/hypothesis.** receptor-status 라우팅(sjpark ER 수정 후) 확정 대기.
> 근거 파일: `experiments/kkkim/20260710_cost_of_substitution/` (frozen_map·therapeutic_distance·patient_routing_cost·fig).
> ⚠️ 발표/공유 시 hypothesis_only·DRP 프레이밍 금지·수치는 기록에서만.

---

## 0. 한 문장 메시지 (슬라이드 표지)
> **H&E 한 장은 어떤 치료 결정엔 충분하고 어떤 결정엔 위험하다 — 그 경계를 정량화한 지도.**
> (basal→화학 triage 안전 · HER2→분자검사 필수 · luminal→판정 유보)

## 1. 왜 이 프레이밍인가 (기존 결과의 재해석)
- 우리 결과: H&E가 분자 아형 예측에서 **subtype_only 천장을 못 넘음**(ER 0.894 vs 0.918 동등), **HER2 외부 실패**(0.53). → "또 하나의 예측 벤치마크"로는 레드오션(스쿱).
- **재프레이밍:** "얼마나 잘 예측하나"가 아니라 **"H&E-예측 아형으로 치료를 정하면 얼마나 잃나(cost-of-substitution)"**. 약점(천장·HER2 실패)이 곧 **임상 지도의 경계선**이 됨.
- Dawood류 블랙박스(H&E→약물 직접예측)가 **구조적으로 못 내는 숫자** — 우리는 중간에 '아형 병목'이 있어 측정 가능.

## 2. Subtype 치료결정 지도 (핵심 표 = 핵심 그림)

| Subtype / 축 | 표준 치료 | H&E 판정 | 해야 할 것 | 근거(예비) |
|---|---|---|---|---|
| **TNBC / Basal** | 화학(±PARP) | ✅ 믿을 만 | **H&E triage 가능** | cost 0.105 · 오라우팅 14% |
| **HER2+ / ERBB2-amp** | 항HER2 | ❌ 무용 | **분자검사(IHC/ISH) 필수** | cost 0.718 · 오라우팅 **100%** |
| **ER+ / Luminal** | 내분비(±CDK4/6) | ⚠️ 불확실 | **판정 유보**(receptor 라우팅 대기) | cost 0.378 · 오라우팅 51% |

- 헤드라인 대비: **cost(antiHER2) − cost(endocrine) = 0.34, 95% CI [0.28, 0.40], 0 배제**(반증 바 통과).
- 그림: `fig_cost_of_substitution.png` (A 축별 비용 막대 + B 치료축 거리 히트맵; antiHER2↔chemo 거리 0.77 최대).

## 3. 정직한 caveat (양 극단만 단단, 가운데는 물렁)
1. **예비=PAM50 라우팅.** 모델이 Normal-like 과예측 → luminal 30%가 '무치료'로 샘. ER 분류기 자체는 AUROC 0.89로 좋으니 **receptor-status 라우팅에서 endocrine 비용이 더 낮게 나올 수 있음** → "luminal ≈ 안전" 확인/기각은 그때.
2. **세포주 지도가 내분비약 못 잡음**(positive control endocrine 1/8 vs antiHER2 3/3·chemo 7/7). endocrine 축 이중 불확실. → **HER2·basal 결론은 단단, luminal만 유보.**
   - **[D1 흡수]** 이건 분류기 탓만이 아니라 **치료증거 인프라의 구조적 한계** — 세포주 약물감수성은 targeted(HER2)·cytotoxic(chemo)엔 유효하나 **ER+ 내분비 backbone(BRCA ~70%)엔 체계적 부적합**. A를 강화하는 일반화 기여. 상세: `experiments/kkkim/20260710_cost_of_substitution/endocrine_limitation.md`.
3. claim_level=sanity, hypothesis_only. Critic 미통과(공유 게이트 전).

## 4. 슬라이드 골격 (발표용 6장)
1. **표지:** 한 문장 메시지(§0) + H&E 슬라이드 그림.
2. **문제:** H&E→분자아형 예측은 crowded·천장 못 넘음·HER2 실패(기존 결과, 정직).
3. **재프레이밍:** 예측 정확도가 아니라 "치료 치환 비용" — 병목이 자산.
4. **방법(1장):** 냉동 세포주→약물 지도 → 측정 vs H&E-예측 아형 라우팅 → 비용=빈도×치료거리.
5. **결과(핵심 그림):** subtype 지도 + fig 2패널. antiHER2 100% 붕괴 / basal 안전 / luminal 유보.
6. **함의:** "값싼 H&E가 치료적으로 충분한 곳/아닌 곳의 지도" + Critic 거버넌스·hypothesis_only. Limitation(HER2 reject, 예비).

## 5. 기존 블로그(2026-07-09, 6편)와의 연계

**현 블로그 = 분석 서사(SETUP).** 6편은 코호트→타일 / 3 FM / I/O 가속 / 신뢰성·외부검증 / 모델링·Critic / 인프라. **5편(모델링·Critic)이 정확히 "천장 못 넘음·HER2 caution"에서 끝남** → 이 재프레이밍의 완벽한 도입부.

**권고 = 새 7편 추가(payoff), 5편에 forward-link 한 줄.**
- **신규 `2026-07-09_BIOP02_07_therapeutic-decision-map.md`**(또는 07-10자): "천장을 못 넘는 모델을 어떻게 쓰나 — 치료 결정 지도". 서사 = 5편의 caution을 받아 "그럼 이 모델을 버리나? 아니다, 결정 지도로 뒤집는다"로 이음.
- **5편 말미에 1–2문장 forward-link:** "이 한계(천장·HER2)를 실패가 아니라 치료 결정의 경계로 읽는 후속은 7편에서." (수치·hedge 불변, 대조부정 남발 금지 — STYLE_CONTRACT 준수.)
- **`CONTENT_MAP.md` 갱신:** 6편 아크에 7편(therapeutic reframe) 추가, "분석→재프레이밍" 흐름 명시.
- **제약:** STYLE_CONTRACT 전면 준수(BRIC 연재체·체언 헤더·이모지 금지·DRP 금지). **claim_level=sanity·예비 명시**, 수치는 `experiments/**/*.json`에서만. dev 블로그(작업 서사)라 '탐구/재프레이밍' 톤으로, 결과 announcement 아님.
- **공용 스페이스 반영:** 7편 추가 후 `sync_blog_to_workspace.sh` 재실행 → `/workspace/blog/BIOP02/`.

**요약:** 기존 6편은 그대로(정직한 분석 아크), **7편이 "그래서 뭘 하나"의 답**. 블로그가 자연스럽게 Paper A 새 방향의 예고편이 됨.

---
관련: `2026-07-10_novelty-scoop-analysis.md`(포지셔닝) · `2026-07-10_research-plan.md`(C1/C2 설계) · `2026-07-10_tierC-longterm-roadmap.md`.

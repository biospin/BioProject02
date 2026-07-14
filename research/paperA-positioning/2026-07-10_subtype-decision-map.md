# Subtype 치료결정 지도 — Paper A 핵심 메시지 (2026-07-10)

> 작성: kkkim. 상태: **PAM50 + receptor-status 라우팅 2종 완료(2026-07-11), claim_level=hypothesis_only, Critic 미통과.**
> 근거 파일: `experiments/kkkim/20260710_cost_of_substitution/` (frozen_map·therapeutic_distance·patient_routing_cost[_receptor]·fig).
> ⚠️ **핵심 갱신(2026-07-11):** receptor 라우팅 결과 → **HER2축만 robust(양 라우팅 100% mis-route)**, endocrine/chemo per-axis cost는 라우팅 스킴·외부 calibration 의존이라 "안전" 주장 근거 약함. §3 참조.
> ⚠️ 발표/공유 시 hypothesis_only·DRP 프레이밍 금지·수치는 기록에서만.

---

## 0. 한 문장 메시지 (슬라이드 표지)
> **H&E-예측 아형으로 치료를 정할 때, HER2축 치환은 라우팅 방식과 무관하게 항상 실패한다(100% mis-route) — 분자검사가 대체 불가임을 비용으로 증명한 지도.**
> 부가: cost-of-substitution 렌즈가 raw AUROC가 숨긴 **외부 다수클래스 붕괴**(ER over-call·HER2 dead)를 축별로 드러냄 → 방법론적 기여. (endocrine/chemo는 라우팅 스킴 의존이라 단정 회피.)

## 1. 왜 이 프레이밍인가 (기존 결과의 재해석)
- 우리 결과: H&E가 분자 아형 예측에서 **subtype_only 천장을 못 넘음**(ER 0.894 vs 0.918 동등), **HER2 외부 실패**(0.53). → "또 하나의 예측 벤치마크"로는 레드오션(스쿱).
- **재프레이밍:** "얼마나 잘 예측하나"가 아니라 **"H&E-예측 아형으로 치료를 정하면 얼마나 잃나(cost-of-substitution)"**. 약점(천장·HER2 실패)이 곧 **임상 지도의 경계선**이 됨.
- Dawood류 블랙박스(H&E→약물 직접예측)가 **구조적으로 못 내는 숫자** — 우리는 중간에 '아형 병목'이 있어 측정 가능.

## 2. Subtype 치료결정 지도 (핵심 표 = 핵심 그림)

| Subtype / 축 | 표준 치료 | H&E 판정 | 해야 할 것 | 근거(PAM50 / receptor) |
|---|---|---|---|---|
| **HER2+ / ERBB2-amp** | 항HER2 | ❌ 무용 | **분자검사(IHC/ISH) 필수** — 유일 robust 결론 | 오라우팅 **100% / 100%**(라우팅-불변) |
| **TNBC / Basal** | 화학(±PARP) | ⚠️ 라우팅 의존 | H&E triage는 **PAM50 형태학축에서만**; receptor 계층서 ER over-call에 오염 | cost 0.105→0.510 · 오라우팅 14%→**73%** |
| **ER+ / Luminal** | 내분비(±CDK4/6) | ⚠️ 판정 유보 | receptor서 낮으나 **majority-collapse 아티팩트**(§3) | cost 0.378→0.035 · 오라우팅 51%→5% |

- 헤드라인 대비: **cost(antiHER2) − cost(endocrine)** = PAM50 0.340[0.276,0.402] · receptor 0.381[0.348,0.420], **양 라우팅 모두 0 배제**(반증 바 통과, robust).
- ⚠️ TNBC·luminal 셀의 화살표(→)는 두 라우팅 스킴 간 반전 = §3 caveat. **단단한 메시지는 HER2 하나**로 좁혀졌음.
- 그림: `fig_cost_of_substitution.png` (A 축별 비용 막대 + B 치료축 거리 히트맵; antiHER2↔chemo 거리 0.77 최대).

## 3. 정직한 caveat — receptor 라우팅 후 갱신 (2026-07-11)

**robustness 검증 결과: HER2 결론만 라우팅-불변, endocrine/chemo는 라우팅 스킴에 뒤집힘.**

| 축 | PAM50 라우팅 | receptor 라우팅 | 판정 |
|---|---|---|---|
| **antiHER2** | mis 100% · cost 0.718 | mis **100%** · cost 0.416 | ✅ **robust — 분자검사 필수**(HER2 head 외부서 양성 0회 발화) |
| endocrine | mis 51% · cost 0.378 | mis 5% · cost 0.035 | ⚠️ **불안정** — receptor서 낮으나 진짜 스킬 아님(아래) |
| chemo | mis 14% · cost 0.105 | mis **73%** · cost 0.510 | ⚠️ **역전** — receptor서 급등 |

- **헤드라인 contrast(antiHER2 − endocrine)는 양 라우팅서 robust:** 0.340[0.276,0.402](PAM50) · 0.381[0.348,0.420](receptor), 둘 다 0 배제.
- **⚠️ endocrine 5% / chemo 73% 반전의 정체 = 외부 다수클래스 붕괴(진짜 H&E 스킬 아님).** CPTAC서 receptor head 예측분포가 endocrine 89%(실제 61%)·antiHER2 **0%**(실제 12%)·chemo 11%(실제 27%)로 붕괴. → (1) HER2 head가 한 번도 양성 미발화(AUROC 0.53 random 정합) → HER2+ 전원 이탈. (2) ER over-call(TNBC 79명 중 58명=73%를 ER+로) → TNBC가 endocrine으로 새면서 chemo cost 급등. endocrine 5%는 "ER+가 다수라 자명히 맞음"의 산물. 근거: `patient_routing_cost_receptor.json`(confusion·base_rate·mechanism).
1. ~~예비=PAM50 라우팅, luminal 안전 확인 대기~~ → **위 표로 해소.** luminal "안전"은 majority-collapse 아티팩트라 기각. 단단한 결론은 **HER2 하나**로 좁혀짐.
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

## 6. Future work — 타암종 일반화 (스쿱 확인 완료, 2026-07-10)

> **BRCA-only 룰(Paper B까지) 때문에 지금은 안 함.** 발표 Q&A·논문 Discussion의 future-work / Paper C 후보로만.

- **defensible whitespace 확인:** pan-cancer 예측 지도(어떤 변이를 H&E가 맞히나)는 **red-ocean**(Arslan/Kather Commun Med 2024 32암종·4,481 biomarker; Fu/Kather Nat Cancer 2020). 그러나 **우리 각 = per-therapy-axis cost-of-substitution("H&E triage OK vs 분자검사 필수" 결정 경계)을 암종 전반으로**는 **미출판.** image→세포주→치료가설 pan-cancer도 whitespace(Dawood 2023 breast-only).
- **일반 원리(재현 예상):** *유전체 표적 변이 축(HER2·EGFR/ALK·BRAF)은 형태학에 near-invisible → 분자검사 필수, 형태 특징 뚜렷한 축은 H&E triage 가능.* Arslan의 predictability 순서(driver SNV 최하위)가 이를 암시하나 **치료축별 결정 규칙으로 정식화한 사람 없음** — 우리 몫.
- **⚠️ 차별화 필수(스쿱 리스크):** Arslan 대비 "또 하나의 AUC 표"로 읽히면 incremental. **차별자 = feasibility AUC를 *치료결정 fidelity 비용*으로 변환** + 축별 mandatory/triage 컷오프. hypothesis_only·비-DRP 유지.
- **비용/제약:** 암종당 새 코호트 임베딩+세포주 지도+아형-치료 매핑(수 주). 인프라(임베딩·DepMap/GDSC) 재사용되나 **BRCA-only 룰 위반이라 리더 사인오프 필요.**
- **후보 암종·데이터·다운로드 카탈로그:** `2026-07-10_future-crosscancer-data.md` — 파일럿 추천 = **폐 NSCLC(EGFR/ALK vs LUAD/LUSC) + 대장(BRAF vs MSI 뉘앙스)**, TCGA/CPTAC/DepMap 소스·gdc-client/idc-index/cBioPortal 다운로드법 포함.
- 위협 논문: Arslan Commun Med 2024(s43856-024-00471-5) · Fu/Kather Nat Cancer 2020(s43018-020-0085-8) · Waqas J Pers Med 2022(PMC9784641, "when to run molecular tests" 가장 근접) · Nat Commun 2024 prescreening(s41467-024-49153-9, 단일마커 비용절감) · Dawood npj PO 2023(breast image→drug).

---
관련: `2026-07-10_novelty-scoop-analysis.md`(포지셔닝) · `2026-07-10_research-plan.md`(C1/C2 설계) · `2026-07-10_tierC-longterm-roadmap.md`.

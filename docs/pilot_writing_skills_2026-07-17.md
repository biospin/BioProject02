# 파일럿: 공개 "논문 집필(academic writing)" 스킬 벤치마크 (2026-07-17)

> **왜 이 문서:** §5.6/§4.3 스킬 벤치마크가 인용검증·재현성·병리·단일세포는 봤으나 **집필(writing) 스킬을 빠뜨렸다**(kkkim 지적). 월요일 Paper C 초안 착수 예정 → 지금 "공개 집필 스킬을 우리 하네스에 차용할지" 판단이 필요.
> **판정 원칙(정본 = `docs/HARNESS_REVIEW_2026-07-17.md` §4.5):** 별점·self-eval·`eval_report_*.json` 점수를 근거로 쓰지 않는다. **실행코드 유무를 센다.** 합격 기준 = **우리가 실제로 당한 실패셋**(§1.2의 6건 + 인용오류 5건 = 11건). 표준 기계작업만 차용, **논지·프레이밍·검증 게이트는 자작 유지.**
> **비교 기준(핵심):** "이 스킬이 우리 `manuscript-writer`/`paper-critic`보다 나은가"로만 잰다.

---

## (a) 조사 범위 — 뭘 뒤졌나

이미 클론된 2개 저장소만 조사(신규 클론·설치 없음, env 무오염):

| 저장소 | 라이선스(repo) | 집필 관련 스킬 수 | 조사 방법 |
|---|---|---|---|
| `medical-research-skills` (AIPOCH) | MIT | Academic Writing 2구역(`scientific-skills` 45 + `awesome-med-research-skills` 28) + `Other/` 집필류 ~10 | 전수 코드 census + 고신호 8종 SKILL.md 정독 |
| `medsci-skills` (Aperivue) | MIT | `skills/` 중 집필·검수·투고 15종 | 전수 코드 census + 고신호 6종 SKILL.md·스크립트 정독 |

- **grep 트리거**(`manuscript|abstract|discussion|introduction|IMRaD|cover letter|reporting guide|CONSORT|STROBE|revise|proofread`) → SKILL.md **약 200건 매치**, 그중 집필 특화 **~90종**을 코드 census.
- **정독(본문·스크립트까지)한 고신호 14종:** AIPOCH `claim-strength-calibrator`, `reporting-guideline-compliance-checker`, `abstract-trimmer`, `discussion-section-architect`, `sci-paper-reviewer`, `content-proofreading`, `journal-recommender`, `resubmission-deadline-tracker`, `paper-tweet-generator` / medsci `check-reporting`, `revise`(+`check_response_claims.py`), `humanize`, `self-review`(24+ 결정론 스크립트), `polish-language`.
- **우리 자산 대조 대상:** `.claude/agents/manuscript-writer.md`, `paper-critic.md`, `.claude/skills/paper-production-orchestrator/SKILL.md`, `agents/critic/checklist_v1.md`, `agents/critic/scripts/verify_citations.py`.

**핵심 관찰(코드 census):** AIPOCH 집필 스킬의 `.py`는 대부분 **정규식 텍스트 치환(예 `abstract-trimmer`가 "we found that"·"to the best of our knowledge" 삭제)** 또는 **프롬프트만 출력하는 템플릿(`discussion-section-architect`는 프롬프트 문자열 print)** — 즉 실질은 LLM 프롬프트다. **medsci만이 진짜 실행 로직**(결정론 검증 스크립트·번들 체크리스트)을 가진다. 이는 §4.3 인용검증 파일럿에서 확인된 패턴(AIPOCH=산문, medsci=코드)과 일치.

---

## (b) 후보별 표

> **실행코드**: SKILL.md 지침 외에 **실제 결정론 로직**이 있나(정규식 치환·print 템플릿은 "산문"으로 분류 — LLM 프롬프트와 동급). **실패셋 커버**: 우리 11건 중 몇 건을 잡나. 점수(`eval_report_*.json`)는 **일절 인용 안 함**(§4.5-b).

| 스킬 (저장소) | 실행코드 | 우리 자산과 중복/신규 | 우리 규율 위반 위험 | 실패셋 커버 | 라이선스 |
|---|---|---|---|---|---|
| **`check-reporting`** (medsci) | **있음** — 46종 CC-BY 체크리스트 번들(TRIPOD-AI·CLAIM 포함) + 스크립트 1,071줄(버전·존재·PRISMA-cascade) | **신규** — 우리 하네스에 STROBE/TRIPOD/CONSORT 준수 점검 **전무**(확인: `checklist_v1.md`·`paper-critic`·`manuscript-writer` 모두 0건) | 낮음(리포트 산출; 준수 **판정 자체는 LLM**이라 게이트 아님) | 직접 0/11이나 **누락항목=미보고 리스크**를 구조적으로 줄임 | repo MIT, 체크리스트 **혼합**(대부분 CC-BY, CARE/DECIDE-AI/MI-CLEAR-LLM=CC-BY-NC, 일부 "faithful summary"=파생). **Paper C 표적 2종(TRIPOD-AI=CC-BY-4.0, CLAIM=RSNA OA)은 깨끗** |
| `revise` + `check_response_claims.py` (medsci) | **있음** — 결정론 게이트(응답서의 "추가했다"·"이제 [15] 인용" 주장이 개정 본문에 실제 있나 grep, stdlib, 안전) | **신규** — 우리에 rebuttal/response-letter 기구 없음 | **낮음(오히려 정합)** — "주장≠실물" 실패를 결정론으로 차단 = 우리 규율과 동일 방향 | R1 개정용(초안엔 무관) | MIT |
| `self-review` (medsci) | **있음** — 결정론 스크립트 24+(`check_cv_leakage`·`check_reported_p_from_counts`·`check_scope_coherence`·`check_claim_artifact` 등, "산문 믿지 말고 재계산") | 대부분 **중복**(우리 verify-gate 철학과 동일), 일부 **템플릿 참조가치** | 낮음(정합) | 방향 일치하나 우리 실패셋의 구체형(site-level TSS 등)은 미커버 | MIT |
| `claim-strength-calibrator` (AIPOCH) | **없음**(순수 프롬프트, `references/*.md`가 correlation↔causation·prediction↔clinical-utility 매핑 규칙) | **중복** — `paper-critic` #1(claim-evidence match)이 이미 커버, 우리가 DRP-scope로 더 특화 | **낮음(정합)** — 우리와 같은 방향(과대주장 억제). 단 결정론 보장 0 | 방향은 hedge격상·상관→인과와 일치하나 **프롬프트라 실측 보장 없음** | MIT |
| `reporting-guideline-compliance-checker` (AIPOCH) | **없음**(py=0, 체크리스트 항목 **번들 안 함** → LLM 기억에 의존) | check-reporting의 열등 버전 | **중간** — 항목을 **기억에서** 판정 = §4.5 "기억으로 검증 금지" 안티패턴, 항목 환각 가능 | 0/11 | MIT |
| `abstract-trimmer` (AIPOCH) | 정규식 치환("we found that"·"to the best of our knowledge"·"in conclusion" 삭제) | 중복(길이 줄이기) | **⚠️ 높음** — "to the best of our knowledge"는 **정당한 스코프 한정 hedge**인데 무조건 삭제 → 경계 완화 **유발** 가능 | **오히려 실패 유발** | MIT |
| `humanize` (medsci) | 참조 스크립트(numerical/citation 보존 invariant를 self-review 스크립트로 강제) | 중복(English AI-문체 제거; kkkim `humanize-korean`은 한국어 전용) | **낮음** — 숫자·인용 **불변 invariant 강제**, "hedge는 근거수준에 맞춰 보정"(삭제 아님) | — | MIT |
| `polish-language` (medsci) | `lint_consistency.py` 296줄 | 중복(문체 일관성) | 낮음 | — | MIT |
| `sci-paper-reviewer` / `journal-recommender` / `content-proofreading` / `resubmission-deadline-tracker` / `paper-tweet-generator` (AIPOCH `Other/`) | 프롬프트/경량 | **중복 또는 범위 밖** — 각각 `paper-critic` / medsci `find-journal` / 교정 / 캘린더 / 소셜 | 낮음 | 0/11 | MIT |
| `discussion-section-architect` 등 AIPOCH 섹션 작성기(`methods/results/introduction-*`) | **없음**(프롬프트 print 템플릿) | 중복 — `manuscript-writer`가 이미 섹션 작성 | 낮음 | 0/11 | MIT |

---

## (c) 우리 `manuscript-writer`보다 나은 게 있나 — **1건(부분)**

- **`check-reporting`의 46종 reporting-guideline 체크리스트(특히 TRIPOD-AI·CLAIM)** — 우리에게 **진짜 없는 것**. `manuscript-writer`·`paper-critic`·`checklist_v1.md` 어디에도 STROBE/TRIPOD/CONSORT 준수 점검이 없음(grep 확인). Paper C는 **H&E→분자표현형 예측 모델 논문** → **TRIPOD+AI**(예측모델)·**CLAIM**(영상 AI)이 정확히 대상 리포팅 표준. 이 체크리스트를 **참조자료로** 두면 리뷰어가 잡기 전에 누락 보고항목(캘리브레이션·결측처리·검증셋 출처 등)을 스스로 메꿀 수 있다.
- 그 외 모든 집필 스킬은 우리 것보다 낫지 않다: 섹션 작성기는 `manuscript-writer` 중복, `sci-paper-reviewer`는 `paper-critic` 열등판, 인용류는 §4.3에서 이미 "우리 `verify_citations.py`가 더 낫다" 확정.

## (d) 우리 정직성 규율과 충돌하는 스킬 — **1건 명확, 1건 주의**

- **⚠️ `abstract-trimmer`(AIPOCH) = 정면 충돌.** 정규식으로 "to the best of our knowledge" 등을 **무조건 삭제**한다. 이건 정당한 스코프 한정 hedge → 기계적 제거 시 **경계 완화(우리 실패셋의 'hedge 격상·조건부→전면')를 도구가 유발**한다. **차용 금지.**
- **주의: hedge를 건드리는 모든 스킬**(`humanize` Pattern 17, `polish-language`, AIPOCH tone류). 다만 **medsci `humanize`는 안전한 편** — 숫자·인용 불변을 **enforced invariant**로 강제하고 "hedge는 삭제가 아니라 근거수준에 맞춰 보정"이라 명시. 반대로 근거-비인지 정규식(AIPOCH류)이 위험. **원칙: hedge·숫자를 건드리는 자동화는 "근거수준 인지 + 숫자 불변 강제"가 있어야만 검토.**
- **역방향(정합) 스킬도 있음:** `claim-strength-calibrator`·`check_response_claims.py`·`self-review` 재계산 스크립트는 우리 규율과 **같은 방향**(과대주장·주장≠실물 차단). 이들은 충돌이 아니라 강화. 단 전자는 프롬프트라 **보장이 없다**.

## (e) 차용 판단

**차용: 조건부 1건 + 참조 2건. 파이프라인 편입은 0건.**

1. **`check-reporting`의 체크리스트 파일만 — 참조자료로 차용(게이트 아님).** 월요일 착수 시 **TRIPOD-AI(`TRIPOD_AI.md`, CC-BY-4.0)·CLAIM(`CLAIM_2024.md`, RSNA OA)** 2개 파일을 `docs/manuscript/` 참조로 복사, `manuscript-writer`가 초안 시 항목 대조. **주의:** 준수 **판정은 LLM**이므로 "PASS"를 게이트로 쓰지 않는다(§4.5 self-eval 불신과 동일). 우리 검증 게이트(헤드라인 재계산·`verify_citations.py`)는 **자작 유지**. → **kkkim 원칙의 "표준 기계작업만 차용, 검증 게이트는 자작"에 정확히 안착.**
2. **`claim-strength-calibrator`의 `references/evidence-level-mapping-rules.md`·`overclaim-pattern-rules.md`** — 스킬 채택이 아니라 **`paper-critic` 프롬프트 보강용 텍스트로 채굴.** prediction↔clinical-utility·association↔causation 구분을 우리 #1보다 세분화 → DRP-scope 규율 문구 강화에 참고.
3. **`check_response_claims.py`(medsci `revise`)** — **R1 개정 단계 후보로 기록만.** 지금(초안)은 무관하나, rebuttal 작성 시 "응답서 주장이 본문에 실재하나"를 결정론으로 검증 → 우리에 없는 기구이고 규율 정합. 월요일과 무관하므로 **우선순위 낮음**, 개정 라운드 진입 시 재검토.

**차용 안 함:** AIPOCH 섹션 작성기·`sci-paper-reviewer`·`reporting-guideline-compliance-checker`(기억 의존)·`abstract-trimmer`(충돌)·소셜/캘린더류 — 전부 중복·범위 밖·위험.

## (우리 하네스가 이미 더 나은 지점)

- **인용 검증:** `verify_citations.py`가 "Williams 2022" 날조를 **잡았고**, 공개 인용 스킬(`verify-refs`)은 **놓쳤다**(§4.3). AIPOCH 인용류는 실행코드 0줄. → 자작 유지가 실증됨.
- **적대적 검수 + 그림 QA:** `paper-critic`은 10점 체크리스트 + **렌더된 그림 이미지를 직접 열어** tofu/overflow/overclaim을 잡는다. `sci-paper-reviewer`(프롬프트)엔 없음.
- **검증 게이트/오케스트레이션:** `paper-production-orchestrator` + `auto_review_orchestrator.py`(결정론 게이트→큐→적대 리뷰, Tier B/C, 헤드라인 재계산)는 공개 어느 집필 스킬보다 우리 DoD(결정론 재계산·`hypothesis_only`·`<FILL>`)에 맞춰져 있다.
- **DRP-scope 규율:** "drug-response prediction 아님·BRCA-only·가설출력"은 우리 프로젝트 고유 규율 — 어떤 공개 스킬도 이걸 모른다.
- **누락 방지 리포팅만 예외:** 위 강점들과 별개로, **reporting-guideline 준수 점검은 우리에 없는 유일한 실질 공백** → (e)-1로 메꿈.

## (f) 한계

- **실행 검증 안 함:** SKILL.md·스크립트를 **읽어** 판정했으나 `check-reporting`·`check_response_claims.py`를 우리 원고에 **실제로 돌려보지는 않았다**(Paper C 원고가 아직 없음). 유용성 확정은 월요일 초안에 실제 대조해야 함 = **현재 "미검증"**.
- **전수 정독 아님:** ~90종 중 census(코드 유무)는 전수, **본문 정독은 고신호 14종**. 저신호 섹션 작성기·잡류는 census 패턴("프롬프트/중복")으로 일괄 판정 → 개별 정독 시 미세 반례 가능성 남음.
- **라이선스 파생물:** `check-reporting` 일부 체크리스트가 "in-house faithful summary/educational summary"(원 가이드라인의 파생 요약). 출판 전용·비상업 학술 용도엔 무해하나, **표적 2종(TRIPOD-AI·CLAIM) 외를 쓸 경우 원문 대조 권장**.
- **§4.3.2와 정합:** self-review 결정론 스위트가 우리 verify-gate와 같은 방향임은 확인했으나, 우리 실패셋의 **구체형**(site-level TSS 누출, n=187/85 재계산)을 잡는지는 **미검증**(공개 스크립트가 우리 데이터 스키마를 모름) → §4.3.2의 "우리 검증기가 더 엄격" 결론 유지.

---

## kkkim 실물 검증 (2026-07-18) — load-bearing 주장 2건 대조

이 세션에서 서브에이전트 주장을 반복 정정해왔으므로, 핵심 2건을 직접 확인했다.

- **주장② abstract-trimmer가 hedge 무조건 삭제 → ✅ 사실 확정.** `abstract-trimmer/scripts/main.py:38` `r'\bto the best of our knowledge\b'` → L42 `re.sub(pattern,'')`. 정당한 스코프 hedge를 정규식으로 무조건 제거 = 우리 정직성 규율("hedge 격상 금지") 정면 위반. **차용 금지 확정.**
- **주장① "우리 하네스에 reporting-guideline 체크 전무" → ⚠️ grep 근거는 틀렸으나 결론은 맞음.** 서브에이전트가 "0건"이라 했으나 실제로 checklist_v1·paper-critic·manuscript-writer에 `CLAIM`·`reporting`·`disclaimer` 문자열이 있다. **그러나 전부 다른 뜻**: `claim_level: hypothesis_only`(7-point #7) · 인용검증기 판정값 `CLAIM_UNSUPPORTED` · DRP-아님 disclaimer. **정식 보고지침(TRIPOD-AI·CLAIM(Checklist for AI in Medical imaging)·STROBE) 준수 체크는 실제로 없음.** → gap 판단 유효. Paper C = H&E→분자표현형 예측모델이라 TRIPOD-AI가 대상 표준.

**정정된 차용 판단(불변):** ① medsci `check-reporting`의 TRIPOD-AI·CLAIM 체크리스트 **텍스트만 참조자료로** 차용(준수 판정은 사람/Critic — 검증게이트 자작 유지). ② abstract-trimmer 등 hedge를 건드리는 스킬은 차용 금지. ③ 나머지 집필 스킬은 우리 manuscript-writer 중복·열등.

**미검증:** Paper C 원고가 아직 없어 실제 적용 유용성은 미검증(초안 나온 뒤 TRIPOD-AI 체크리스트 대조 시 확정).

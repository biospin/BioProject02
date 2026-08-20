# AI Scientist 하네스 — 경쟁 landscape 대비 차별화 실재성 분석

작성: 2026-08-20 · 대상 독자: Leader(kkkim) 전략 판단용
근거 구분: **[REPO]** = 우리 저장소 실측 · **[WEB]** = 외부 웹 검증(fetch로 실물 확인) · **[VERIFY]** = 미검증(인용 전 재확인 필요)

> 방법: 우리 잠정 차별화 명제를 6개 원자 주장으로 분해하고 각각의 스쿱 노출을 따로 조사했다.
> "묶음"으로 검색하면 "안 붐비는 것 같다"는 모호한 답이 나오고 실제로 선점된 한 조각을 놓친다.

---

## 0. 5분 요약 (Leader용)

**발전시킬 가치: 있다. 단, 논문의 중심 주장을 좁혀야 방어된다.**

- 우리 명제는 6조각인데 그중 3조각(자율↔검증 프레이밍 · anti-self-reference · honest-negative/사전등록 규율)은 **이미 붐빈다** — 기여로 내세우면 5분 검색에 죽는다. **인용·계승**할 것이지 주장할 것이 아니다.
- **방어 가능한 핵심은 2조각의 조합**: (b) **연구-무결성 게이트 자체를 mutation/공허통과로 CI-blocking 검증** + (d) **실제 사고 로그(PITFALLS_REGISTRY 27건)에서 유도한 가드의 메타학습 루프**. (f) 다주·다인·다세션으로 실제 논문(5암종)을 굴린 운영기록이 그 **증거**다.
- **핵심 판정(discriminating check) 결과**: "게이트가 공허하지 않은지 mutation으로 시험한다"는 개념 자체는 소프트웨어공학·RTL·정형기법에 **이미 존재**한다(mutation testing은 1970년대 SE 교과서 기법; 최근 실물 선례 GateTruth·Containment Verification 둘 다 abs 페이지로 실재 확인). 그러나 이를 **연구-무결성 게이트(누수검사·critic scorer·인용검증·수치드리프트)에, 살아 있는 다중에이전트 과학 파이프라인의 실제 사고에서 유도한 mutation으로** 적용한 선행은 **찾지 못했다**. 이 좁은 조합이 white space다.
- **측정된 강한 근거 1건**: 정면 자율경쟁 repo 2종(SakanaAI/AI-Scientist, AgentLaboratory)은 `.github/workflows/`가 **아예 없다**(API 404, 2026-08-20 확인) — 무결성 CI 게이트 부재가 추론이 아니라 **관측**이다.
- **가장 값싼 입증 실험(현재 미측정·제안 단계)**: PITFALLS_REGISTRY 27건 사고를 현재 CI 검증기 7종에 재생(replay)해 **catch rate = X/27** 을 보고. 놓친 것은 Limitation이 된다. 이미 봉인된 사고라 값싸고 반증가능.
- **순서 권고**: 지금 주의를 분산하지 마라. 하네스 논문의 중심 증거가 **Paper C를 실제로 생산한 운영기록**이므로, Paper C를 끝내는 것이 곧 증거 축적이다. 하네스 작업은 registry-replay 실험(값싸고 병행 가능)으로 한정.
- **오픈소스**: 배포 단위는 저장소가 아니라 **`ai_scientist/template/` + `evals/` + `.github/workflows/critic-validators.yml`**(이미 `{{SLOT}}`로 살균됨). 스타≠기여. 스타를 받으려면 evals를 **이 저장소 밖에서 도는** 독립 실행형으로 일반화해야 하며 그게 진짜 노동이다.

---

## 1. 경쟁 Landscape 표

별 수는 모두 GitHub API로 2026-08-20 직접 조회 [WEB]. 미확인은 "미확인"으로 표기.

### 1-A. 자율 발견형 (autonomous discovery) — 우리의 대조군

| repo / 논문 | ★ (2026-08-20) | 판매 각도 | 알려진 약점 | 우리와의 관계 |
|---|---|---|---|---|
| **SakanaAI/AI-Scientist** (Lu et al. 2024) | **14,427** | 아이디어→실험→논문→자동리뷰 완전 자율 | 자동리뷰가 깊은 기여 파악 실패·저품질 문헌리뷰·검증 취약 (arXiv 2502.14297 [WEB]). **무결성 CI 부재 — `.github/workflows/` 404, 2026-08-20 확인 [WEB]** | **주 대조군.** 우리는 정반대 극단(자율 제한 + 검증). baseline으로 인용 |
| **SakanaAI/AI-Scientist-v2** | **7,032** | agentic tree search, 워크숍 수준 자동발견 | v1 비판 상당수 상속; 자동리뷰 신뢰성 논란 지속 | 대조군 갱신판 |
| **SamuelSchmidgall/AgentLaboratory** | **5,803** | 사람 아이디어를 받아 end-to-end 구현 보조 | "human researcher 보조"라 완전자율 아님. **무결성 CI 부재 — `.github/workflows/` 404, 2026-08-20 확인 [WEB]** | 인접 — 사람 개입 스펙트럼상 우리보다 자율 쪽 |
| **HKUDS/AI-Researcher** (NeurIPS 2025) | **5,687** | 자율 과학 혁신, 프로덕션판(novix.science) | 발견 자동화 초점, 무결성/거버넌스 층 미보고 | 인접 |
| **Google AI co-scientist** (Gottweis 2025) | 공개 repo 미확인 | 전문 에이전트(Generation·Reflection·Ranking·Evolution·Meta-review)+Elo+scientist-in-the-loop | 폐쇄형; Reflection이 우리 Critic 대응물. **무결성 CI 강제에 대한 공개 근거를 찾지 못함**(추정 아님, 근거 부재) [VERIFY] | 가장 가까운 "구조"적 선례. delta는 우리의 **기계화된 검증층** |

### 1-B. 엄밀성·재현성 벤치마크 — 우리 스쿱 위험이 실제로 사는 구역

| 논문 | 무엇 | 하는 것 / 안 하는 것 | 우리와의 관계 |
|---|---|---|---|
| **CORE-Bench** (arXiv 2409.11363 [WEB]) | 논문 코드+데이터로 계산 재현성 에이전트 평가 | 재현을 **측정**한다 / 파이프라인 안의 **게이트를 만들지** 않는다 | must-cite. 우리는 벤치가 아니라 운영 하네스 |
| **PaperBench** (OpenAI, arXiv 2504.01848, ICML 2025 [WEB]) | ICML 2024 논문 20편을 처음부터 재현; 8,316 채점항목 rubric + LLM 판사 | 재현 **능력**을 평가 / 무결성 가드 자체를 검증 안 함. ⚠️ **단, 판사 성능용 별도 벤치를 따로 만듦** — judge-of-judge 인접 | must-cite |
| **MLE-bench / ScienceAgentBench / RE-Bench** [VERIFY] | ML 엔지니어링·과학 코딩 에이전트 능력 | 능력 벤치 / 거버넌스·정직성 규율 아님 | 배경 |
| **AstaBench** (Allen AI, arXiv 2510.21652, ICLR 2026 [WEB]) | 과학연구 에이전트 엄밀 벤치(2,400+ 문제, 57 에이전트 평가) | 에이전트를 엄밀히 **평가** / 우리처럼 파이프라인 내부 게이트를 **강제·검증하진 않음**(실측: capability 벤치) | 인접 — "엄밀성"을 파는 최근 이웃, 주시 대상 |
| **Kapoor & Narayanan, Leakage** (arXiv 2207.07048 / Patterns 2023 [WEB]) | 17개 분야 294편에 누수, 8종 taxonomy | 누수를 **진단·경고** / 파이프라인에 **강제 검사** 아님 | **직접 이웃.** 우리 `verify_split_integrity.py`가 이 문헌의 처방을 기계로 강제 |
| **REFORMS checklist** (Science Advances, 10.1126/sciadv.adk3452 [WEB]) | ML-기반 과학 보고 체크리스트(합의) | 체크리스트(사람이 적용) / 실행형 CI 아님 | **직접 이웃.** 우리는 체크리스트를 **실행형 검증기**로 |

### 1-C. Judge-of-judge / 무결성 담론 — anti-self-reference·timeliness 근거

| 논문 | 무엇 | 우리와의 관계 |
|---|---|---|
| **JudgeBench** (arXiv 2410.12784 [WEB]) | LLM 판사의 사실·논리 정확성 메타평가; 최신 모델도 랜덤에 가깝다 | must-cite. "판사를 누가 검증하나"의 벤치. 우리는 벤치가 아니라 **운영상 owner≠reviewer + 모델 다양성 요구(미완)** |
| **Panickssery 2024, self-preference** [REPO 인용, VERIFY] | LLM이 자기 출력을 선호 | 우리 anti-self-reference 근거. ⚠️ 우리 폴백 "같은 모델 N회 반복"은 이 편향을 **못 막는다**(우리 04 문서가 이미 자기지적) |
| **Hidden Prompts in Manuscripts** (arXiv 2507.06185, CACM 게재 [WEB]) | 프리프린트에 흰 글씨로 "긍정 리뷰만" 은닉; 18편 적발 | **timeliness 근거.** AI 리뷰 신뢰성 붕괴 사례 |
| **Publish to Perish** (arXiv 2508.20863 [WEB]) | 프롬프트 인젝션 성공률 98.6%, 사람 패러프레이즈 후도 94% | 같은 담론. ICLR 2026이 은닉 프롬프트를 **연구부정으로 공식 분류** [WEB] |
| **Sakana 자동리뷰 비판** (arXiv 2502.14297 [WEB]) | 자동리뷰가 기여 파악 실패, 저티어 통과용 수준 | 우리 각도(신뢰성)의 시의성 정당화 |

### 1-D. 게이트-mutation 개념 선례 (다른 도메인) — 우리 (b)의 개념 조상

| 논문 | 무엇 | 우리와의 관계 |
|---|---|---|
| **GateTruth** (arXiv 2608.12635 [WEB], Meet Bhadra) | RTL 벤치마크 testbench를 mutation으로 감사; "약한 커버리지는 깨진 설계도 통과", "mutation-kill 인증을 표준 보고요건으로" | **개념 조상.** 도메인=RTL 하드웨어. 우리 게이트-mutation과 같은 논리, **다른 대상**(연구-무결성 아님) |
| **Containment Verification** (arXiv 2605.09045 [WEB], Moon & Varshney) | LLM 스펙에 vacuity detection + discrimination 게이트(Dafny); "살아있는 mutation을 통과시키는 스펙은 충실↔결함을 구분 못함" | **개념 조상.** 도메인=정형 스펙검증. vacuous-pass 논리가 우리 "게이트 공허통과 회귀"와 동형, **다른 대상** |

### 1-E. 범용 substrate (경쟁 아님)

| repo | 관계 |
|---|---|
| AutoGen / CrewAI / LangGraph | **인접 — substrate.** 우리 하네스가 그 위에 얹힐 수 있는 오케스트레이션 기반이지, 무결성 하네스의 경쟁자가 아니다 |

---

## 2. 차별화 판정 — 6조각 분해

우리 명제를 원자 주장으로 쪼개고 각각 판정한다.

| # | 원자 주장 | 스쿱 노출 | 판정 |
|---|---|---|---|
| a | "자율 발견이 아니라 rigor/verification 하네스"라는 프레이밍 | **높음** | 붐빔 — Sakana 비판 진영이 이미 점유. **계승·인용** |
| b | 연구-무결성 게이트 자체를 mutation/공허통과로 CI-blocking 검증 | **낮음~중** | **날카로운 핵심.** 개념 조상(GateTruth·Containment)은 있으나 이 도메인 적용은 미발견 |
| c | anti-self-reference critic / owner≠reviewer | **높음** | JudgeBench·self-preference 문헌으로 붐빔. **계승** |
| d | 사고→registry→가드 메타학습 루프 | **중** | 이웃은 self-improving agent memory / SE postmortem. **조합으로 방어** |
| e | honest-negative + claim 규율, 골대이동 금지 | **높음** | 사전등록·오픈사이언스 정설. **계승** |
| f | 실제 다주·다인·다세션으로 진짜 논문 생산 | 아이디어로는 낮음, **증거로는 강함** | 주장이 아니라 **증거**로 쓴다 |

### (a) 진짜 새로운가?
**부분적으로만.** "신뢰성을 정면으로 판다"는 프레이밍은 Sakana 비판(2502.14297), 프롬프트 인젝션 담론(2507.06185), 엄밀성 벤치(AstaBench, CORE-Bench)가 이미 점유했다. 프레이밍 자체는 novelty가 아니다.

### (b) 방어 가능한가? — **핵심 판정**
**그렇다, 단 좁게 쓸 때만.** discriminating check를 문헌과 **경쟁 repo 양쪽**에 직접 수행했다:

- **개념은 이미 존재** [WEB, abs 페이지 실물 확인]:
  - **GateTruth** (2608.12635) — RTL 벤치마크를 mutation으로 감사, "약한 커버리지 테스트벤치는 깨진 설계도 통과", vacuous-gate 실패모드 명시.
  - **Containment Verification** (2605.09045) — LLM 스펙에 vacuity + discrimination 게이트, "살아있는 mutation을 통과시키는 스펙은 판별력이 없다".
  - 더 근본적으로 mutation testing 자체가 1970년대 SE 교과서 기법이고 "verification of verification"은 정형기법에서 흔하다.
- **따라서 "mutation으로 검증기를 검증"은 일반 개념으로는 novelty 아님.**
- **그러나** 이를 **연구-무결성 게이트**(train/test 누수, critic scorer 공허통과, 인용 DOI-실패-통과, JSON↔markdown 수치 드리프트)에, **살아 있는 다중에이전트 과학 파이프라인의 실제 사고 로그에서 유도한 mutation**으로 적용한 선행은 **찾지 못했다.**
- **경쟁 repo 실측**: 정면 자율경쟁 2종(Sakana AI-Scientist, AgentLaboratory)은 `.github/workflows/`가 **404**(2026-08-20) — 무결성 CI 게이트를 아예 배선하지 않았다. 이는 추론이 아니라 관측이다.

→ **방어 가능한 기여문(한 문장):**
> *"우리는 연구-무결성 게이트에 대한 CI-blocking mutation 스위트를 제공한다 — mutation 케이스가 살아 있는 다중에이전트 과학 파이프라인에서 로깅된 실제 사고에서 유도된다."*
개념(mutation testing)이 아니라 **조합**(무결성 게이트 × 실제 사고 유도 × CI 강제 × 운영 증거)이 white space다. 이는 우리 `template/06_positioning_method.md:41-48`가 말하는 "흔히 남는 자리는 조합"과 정확히 일치.

### (c) 가장 가까운 선행은?
- **개념**적으로 가장 가까움: **GateTruth / Containment Verification** — "게이트를 mutation으로 감사". 차이: 도메인이 RTL·정형스펙이지 연구-무결성이 아니며, mutation이 실제 과학-파이프라인 사고에서 유도되지 않는다.
- **구조**적으로 가장 가까움: **Google AI co-scientist**(Reflection = 우리 Critic 대응물, scientist-in-the-loop). 차이: 무결성 검증을 **CI로 기계화**한 공개 근거를 찾지 못했고 게이트를 mutation으로 시험하지도 않는다.
- **엄밀성 판매 각도**로 가장 가까움: **AstaBench** — 그러나 실측 결과 에이전트를 *평가*하지 파이프라인 게이트를 *강제·검증*하지 않는다. **가장 주시할 타이밍 경쟁자.**

**정직한 결론:** 우리 명제는 통짜로는 새롭지 않다. (a)(c)(e)는 붐빈다. (b)+(d)의 조합에 (f)를 증거로 붙였을 때만 방어된다. 그 조합을 판 정확한 선행은 찾지 못했다.

---

## 3. 가장 값싼 차별화 실험 — "주장"을 "증거"로

> ⚠️ **현재 미측정 — 제안 단계다.** 아래 catch rate 수치는 아직 산출하지 않았다. 계획을 자산으로 읽지 말 것.

**실험명: Registry-Replay Catch-Rate**

- **재료 (이미 존재):** `docs/PITFALLS_REGISTRY.md`의 번호 사고 **27건**(색인 행 실측: A1–A8=8, T1–T7=7, G1–G5=5, C1–C7=7) — 각각 커밋·파일 근거와 설치된 가드가 봉인돼 있음 [REPO].
- **절차:** 각 사고를 현재 CI 검증기 7종(`.github/workflows/critic-validators.yml` [REPO])에 재생 — 사고 당시의 결함을 재주입했을 때 게이트가 잡는가? `evals/validation_harness/run_validation.py --strict`가 이미 소수 케이스로 하는 것을 registry 전체로 일반화.
- **산출:** **catch rate = X/27**. 잡은 것/놓친 것을 명시. 놓친 것(예: 사람-판단 계열 C1 이름 오기, 도메인 통계 A1 층위혼동)은 결함이 아니라 **범위 밖**으로 Limitation에 정직 서술.
- **왜 값싼가:** 사고가 이미 문서화·커밋봉인돼 있어 새 데이터 수집 불필요. 반증가능·정량·정직.
- **가드레일 (필수):** registry를 **봉인된 그대로** 재생하고 수치를 **있는 그대로** 보고한다. catch rate가 좋아 보이게 게이트를 튜닝하는 것은 우리 A5/A2 항목이 이미 금지한 **사후 골대이동**이다.
- **선택 확장:** 같은 27건을 Sakana AI-Scientist / AgentLaboratory 파이프라인에 통과시켜 "이들은 몇 건을 잡나"를 대조(이들은 무결성 CI가 없으므로 대부분 못 잡을 것으로 예상) → 시연형 차별화. 단 노동이 크므로 논문 핵심이 아니라 부록.

---

## 4. 포지셔닝 권고

### (a) 논문
- **venue 후보** (신뢰성·에이전트·연구방법 접점):
  - 워크숍/트랙: NeurIPS/ICLR **agentic science·evaluation** 워크숍, **ML Reproducibility** 계열, ICML **position/benchmark** 트랙 [VERIFY 개별 CFP].
  - 저널형: *Patterns*(Kapoor 누수 논문이 실린 곳), *Science Advances*(REFORMS) 계열 — "ML-기반 과학의 무결성 도구" 프레임.
- **프레이밍:** "또 하나의 AI Scientist"가 아니라 **"AI가 생산한 연구의 무결성을 기계로 강제하는 하네스 + 그 게이트가 공허하지 않음을 mutation으로 증명"**. 자율 발견형은 baseline으로 인용(경쟁자로 숨기지 않는다).
- **핵심 claim(좁게):** §2(b) 기여문 한 문장. "멀티에이전트를 썼다"·"검증을 강조한다"는 claim 금지 — 그건 붐빈다.
- **Paper C와의 순서:** **Paper C 먼저.** 하네스 논문의 중심 증거가 "Paper C(5암종 cost-of-substitution)를 실제로 생산한 운영기록"이다. Paper C 없이 하네스 논문을 먼저 쓰면 증거의 절반(f)이 빈다. Sprint 표상 Paper A draft 8/14–8/28, 제출 8/28–9/11 → **하네스 논문은 Paper A/C 제출 이후**, 그 전까지 하네스 작업은 registry-replay 실험만 병행.

### (b) 오픈소스
- **배포 단위:** `ai_scientist/template/`(이미 `{{SLOT}}` 살균) + `evals/` + `.github/workflows/critic-validators.yml`. **저장소 전체가 아니다** — 루트 `CLAUDE.md`는 서버 IP·SSH 포트·팀 이메일·Slack 앱명을 담고 있어 그대로 공개 불가.
- **스타를 받으려면 실제로 필요한 것 (노동 추정):**
  | 항목 | 노동 | 비고 |
  |---|---|---|
  | evals를 저장소 밖에서 도는 독립 실행형으로 일반화 | **큼 (실질 노동)** | 지금은 BIOP02 경로/스키마에 묶임. registry-replay를 예제 데이터로 재현 가능하게 |
  | README 훅 + 1분 데모(gate가 실제로 오류 잡는 asciinema) | 중 | "verifier가 자기를 검증한다" 데모가 킬러 훅 |
  | 최소 quickstart(`pip install`→`run_validation --strict`) | 중 | 의존성 격리 |
  | 문서 영문화 + template 일반화 검수 | 중 | 국문 다수 |
  | 사례 분리(APPENDIX_CASE_BIOP02) 유지 | 소 | 이미 됨 |
- **정직한 경고:** **스타 ≠ 기여.** Sakana 14k★는 "완전자율"이라는 화려한 서사 덕이 크다. 우리 각도(신뢰성·거버넌스)는 본질적으로 덜 화려해 스타가 느리게 붙는다. 스타를 KPI로 삼지 말고 **"인용되는 방법론 자산"**을 목표로.
- **사람 게이트(우리 규칙):** CC BY 4.0 저작자표시(Ka-Kyung Kim, `docs/HARNESS.md:3`)가 이식본에 살아남아야 함. 저자-대면 결정은 팀 합의.

---

## 5. 리스크 / 스쿱

| 리스크 | 내용 | 완화 |
|---|---|---|
| **개념 선점** | mutation-of-gates·vacuous-pass는 SE/RTL/정형기법에 이미 있음(GateTruth·Containment) | claim을 "개념"이 아니라 **"연구-무결성 게이트 × 실제사고유도 × 운영증거" 조합**으로 좁힌다 |
| **타이밍 — AstaBench류** | "엄밀한 과학 에이전트 벤치"가 빠르게 성장 중(ICLR 2026); 무결성 게이트로 확장하면 겹칠 수 있음 | 우리 delta는 벤치가 아니라 **파이프라인에 강제되는 게이트 + 사고유도 mutation**. 주시하고 인용 |
| **증거 지연** | (f) 운영증거는 Paper C 완료에 종속 | Paper C를 먼저 끝낸다(순서 권고). 하네스 논문을 Paper C보다 앞세우지 않는다 |
| **우리 자체 갭이 리뷰 표적** | 게이트① 실행명령 부재, 폴백이 단일모델 반복, config 불일치(04/01 문서가 이미 자기지적) | **정직하게 Limitation에 싣는다** — 이 저장소가 자기 갭을 표시하는 규율 자체가 신뢰성 증거. 숨기면 역효과 |
| **인용 위생** | `reading_list.md`의 arXiv 다수 DOI-미검증(06_design_lineage.md:46) + 본 조사의 2026-future arXiv ID 일부 [VERIFY] | 논문화 전 `verify_citations.py`+CrossRef/arXiv 재확인. 미검증은 [VERIFY]로 격리 |

### 미확인·미해결로 남긴 것 (정직 보고)
- `ai_scientist/cross_session_work_discipline.md`는 **main에 없음** — 브랜치 `docs/BIOP02-113-kkkim-work-discipline`에만 존재. 본 세션에서 내용 미열람(Bash `git show` 불가). "도구무관 작업규율" 자산이 **미병합 상태**인 것 자체가 발견사항 — 오픈소스 피치가 기대는 자산이므로 병합 여부 확인 필요.
- 별점 4종(Sakana v1/v2, AgentLab, AI-Researcher)·경쟁 repo CI 부재(404 2종)·핵심 5개 논문(GateTruth·Containment·PaperBench·AstaBench·JudgeBench 등)은 abs/API 실물 확인 [WEB]. 나머지 [VERIFY] 표기 논문(MLE-bench·RE-Bench·Panickssery 등)은 인용 전 재확인.
- Google AI co-scientist의 무결성-CI 강제 여부는 **공개 근거를 찾지 못함**(공개 코드 없음). 부재를 단정하지 않고 "근거 미발견"으로 둠.

---

## 부록 — 우리 하네스 실체 (REPO 실측 요약)

명제 검증에 쓴 우리 것의 팩트(전부 [REPO]):
- **2-레이어**: 분석 파이프라인 위에 논문생산 하네스 (`ai_scientist/01`)
- **검수 3층**: CI 결정론 검증기(기계) → AI 적대 리뷰(paper-critic) → 사람 게이트(Tier C·공개) (`04`)
- **CI 검증기 7종** (`.github/workflows/critic-validators.yml`): critic scorer mutation · citation medsci 회귀 · 수치 드리프트 --strict · 게이트 mutation 하네스 · split 누수 계약 · **게이트 공허통과 회귀 10케이스** · 국영문 정합. 이 중 mutation·공허통과 2종이 **"검증기가 자기를 검증"**의 실물.
- **anti-self-reference**: Critic이 자기 임계·control 설정 금지 (`CLAUDE.md` Absolute Prohibitions)
- **사고→가드 메타학습**: `docs/PITFALLS_REGISTRY.md` 27건, 각 "재발방지 장치" 강제
- **honest-negative 규율**: BIOP02-75 HER2 `reject`를 "정직한 음성"으로 수용, 사후 골대이동 금지 (`04` 판정어휘 절)
- **운영증거 (f)**: 6인·다세션·JIRA→Slack→CLI 루프로 5암종 Paper C 실제 생산
- **자기비판**: 문서가 6개 열린 갭을 스스로 표시(게이트① 실행명령 부재, 단일모델 폴백, config 불일치 등) — 이 정직성 자체가 우리 각도의 살아있는 증거

---

## Sources (WEB — 실물 확인)

- SakanaAI/AI-Scientist — https://github.com/SakanaAI/AI-Scientist (★14,427; `.github/workflows/` 404; API 2026-08-20)
- SakanaAI/AI-Scientist-v2 — https://github.com/SakanaAI/AI-Scientist-v2 (★7,032)
- SamuelSchmidgall/AgentLaboratory — https://github.com/SamuelSchmidgall/AgentLaboratory (★5,803; `.github/workflows/` 404)
- HKUDS/AI-Researcher — https://github.com/HKUDS/AI-Researcher (★5,687, NeurIPS 2025)
- Sakana 평가 비판 — https://arxiv.org/abs/2502.14297
- CORE-Bench — https://arxiv.org/abs/2409.11363
- PaperBench (OpenAI, ICML 2025) — https://arxiv.org/abs/2504.01848
- AstaBench (Allen AI, ICLR 2026) — https://arxiv.org/abs/2510.21652
- Kapoor & Narayanan, Leakage — https://arxiv.org/abs/2207.07048
- REFORMS — https://www.science.org/doi/10.1126/sciadv.adk3452
- JudgeBench — https://arxiv.org/abs/2410.12784
- Hidden Prompts in Manuscripts — https://arxiv.org/abs/2507.06185
- Publish to Perish (prompt injection) — https://arxiv.org/abs/2508.20863
- GateTruth (RTL mutation audit) — https://arxiv.org/abs/2608.12635
- Containment Verification (vacuity+discrimination gates) — https://arxiv.org/abs/2605.09045

## Sources ([VERIFY] — 인용 전 재확인)

- MLE-bench / ScienceAgentBench / RE-Bench — 개별 abs 미확인
- Panickssery 2024 self-preference — reading_list.md 인용, DOI 미검증
- Google AI co-scientist (Gottweis 2025) — 공개 코드 없음, 무결성-CI 근거 미발견

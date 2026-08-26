# AI Scientist 하네스 — 새 프로젝트용 설계 템플릿

연구 과정 전반(문헌 검색·정리 → 가설 → 실험 → 논문 작성 → 검수)을 다중 에이전트로 자동화하되,
**사람이 판단해야 할 지점만 남기는** 거버넌스 중심 하네스의 **재사용 템플릿**이다.

> **출처·저작자 표시(필수).** 이 템플릿의 원본은 *paper-production harness — Designed by Ka-Kyung Kim, 2026, contributed as a scaffold (**CC BY 4.0**)* 이다(`docs/HARNESS.md:3`).
> 새 프로젝트에 이식할 때 **저작자 표시를 유지**한다. 본 템플릿은 그 하네스를 BioProject02에서 운용한 경험을 일반화한 것이며, 사례는 [APPENDIX_CASE_BIOP02.md](APPENDIX_CASE_BIOP02.md)에 분리했다.

---

## 이 템플릿이 아닌 것

- ❌ **BioProject02 설계서가 아니다.** 그건 상위 `ai_scientist/`(01~06)에 있고 **한 인스턴스의 회고**다.
- ❌ **미완성 목록을 물려주는 문서가 아니다.** BIOP02가 못 채운 자리(예: 검증 게이트 실행 명령)는 여기서 **"처음부터 정할 것"** 으로 바뀐다 — 물려받는 부채가 아니라 **먼저 만들 기회**다.
- ❌ **정답 세트가 아니다.** 금지 프레이밍·판정 어휘·티어 경계는 **도메인마다 다르다.** 값을 채우지 않은 채로 쓰면 남의 프로젝트 규칙으로 자기 결과를 판정하게 된다.

## 구성

| 파일 | 역할 | 언제 읽나 |
|---|---|---|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | **step-by-step 시작 가이드** — 첫 2주 일정 · 명령 · 파일 골격 · 채워진 예시 | **처음 시작할 때** |
| **[PROJECT_SLOTS.md](PROJECT_SLOTS.md)** | **치환표** — 이 프로젝트의 값을 채우는 단 한 장 | Step 2에서 |
| **[BOOTSTRAP.md](BOOTSTRAP.md)** | 설치 Phase 체크리스트 + 최소 구성 (**무엇을** 세우나) | 전체 조망 |
| [01_two_layer_architecture.md](01_two_layer_architecture.md) | 2-레이어 분리 원칙 + 게이트 배치 | 구조 설계 시 |
| [02_agents_and_roster.md](02_agents_and_roster.md) | 에이전트 명부 · 권한 · 격리 원칙 | 에이전트 정의 시 |
| [03_routing_and_artifact_contract.md](03_routing_and_artifact_contract.md) | 라우팅 + 산출물 계약 + 스키마 | 계약 확정 시 |
| [04_automated_review_and_governance.md](04_automated_review_and_governance.md) | 검수 3층 · 티어 게이트 · 금지선 | 검수 설계 시 |
| [05_human_collaboration.md](05_human_collaboration.md) | 1인1역할 · owner≠reviewer · 인프라 규약 | 팀 구성 시 |
| **[INTEGRATIONS.md](INTEGRATIONS.md)** | **Git · 트래커 · 위키 · 알림 연동** (정본 분리 · 스마트 커밋 · 봇 배선) | 도구 배선 시 |
| [06_positioning_method.md](06_positioning_method.md) | **포지셔닝 방법론**(결론 아님) | 기획 초기 |
| [APPENDIX_CASE_BIOP02.md](APPENDIX_CASE_BIOP02.md) | 실사례·사고 기록 (참고용) | 규칙의 이유가 궁금할 때 |

## 이식 원칙 — "복사"가 아니라 "벤치마킹 이식"

이 템플릿을 새 프로젝트에 얹을 때 가장 흔한 실패는 **통째로 복사하는 것**이다. 남의 도메인 판정 기준까지 따라오면, 자기 분야의 과잉주장은 못 잡고 엉뚱한 문장만 막는다.

| 가져오는 것 (골격) | 새로 쓰는 것 (도메인) |
|---|---|
| 러너·오케스트레이션 구조 | **판정 기준**(`{{FORBIDDEN_PHRASES}}`·`{{CHECKLIST}}`) |
| control ↔ mutated 델타 방식 | **어떤 실수를 심을 것인가**(mutation 케이스) |
| 티어·게이트 배치 | **무엇이 Tier C인가**(`{{TIER_C_PATHS}}`) |
| 계약·스키마의 *형태* | 필드의 *내용*(`{{METRIC_FIELDS}}`) |

이 분리를 코드에서도 지킨다 — **로직은 도메인 무관, 프로젝트별 값은 전부 config로.**
그래야 다음 프로젝트가 *스크립트 복사 + 자기 config*만으로 작동한다.

> 하네스가 여러 프로젝트에 얹혀 있다면 **3자 대조표**(원본 ↔ 인스턴스 A ↔ 인스턴스 B)를 공용 자산으로 두면 좋다.
> 어디가 공통이고 어디가 도메인 특수인지가 그 표에서 드러나고, **다음 이식이 무엇을 바꿔야 하는지**도 거기서 나온다.

## 표기 규칙

- `{{SLOT}}` — [PROJECT_SLOTS.md](PROJECT_SLOTS.md)에서 채우는 자리. **채우지 않은 `{{ }}`가 남아 있으면 그 문서는 아직 쓰면 안 된다.**
- 🔒 — 사람이 통과시키는 게이트(자동화 금지)
- ⚠️ **처음부터 정할 것** — BIOP02가 비워둔 채 운영해 비용을 치른 자리. 새 프로젝트는 **여기부터** 정한다.

## 한 줄 요약

> 자동화의 목표는 **사람을 빼는 것이 아니라, 사람이 판단해야 할 지점만 남기고 나머지 노동을 에이전트가 대신하는 것**이다.
> 그래서 이 하네스의 핵심은 에이전트 개수가 아니라 **게이트의 위치**와 **강제 수단**이다.

## 시작하기

```
0. GETTING_STARTED.md 를 연다        ← 처음이면 여기부터. Step 0~8 을 그대로 따라간다
1. PROJECT_SLOTS.md 를 채운다        ← 여기서 막히면 설계가 아직 안 정해진 것이다
2. BOOTSTRAP.md 로 빠진 Phase 가 없는지 대조한다
3. 01~05 를 읽고 프로젝트 문서로 복사·조정한다
4. 06 으로 포지셔닝을 직접 수행한다  ← 결론을 베끼지 않는다
```

**두 문서의 관계:** `GETTING_STARTED` = **어떻게**(명령·예시·일정) · `BOOTSTRAP` = **무엇을**(Phase 체크리스트·원칙).
처음이면 GETTING_STARTED를 따라가고, BOOTSTRAP은 누락 점검용으로 쓴다.

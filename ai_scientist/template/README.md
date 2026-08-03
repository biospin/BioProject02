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
| **[PROJECT_SLOTS.md](PROJECT_SLOTS.md)** | **치환표** — 이 프로젝트의 값을 채우는 단 한 장 | **제일 먼저** |
| **[BOOTSTRAP.md](BOOTSTRAP.md)** | 설치·부트스트랩 순서 + 최소 구성 | 슬롯 채운 직후 |
| [01_two_layer_architecture.md](01_two_layer_architecture.md) | 2-레이어 분리 원칙 + 게이트 배치 | 구조 설계 시 |
| [02_agents_and_roster.md](02_agents_and_roster.md) | 에이전트 명부 · 권한 · 격리 원칙 | 에이전트 정의 시 |
| [03_routing_and_artifact_contract.md](03_routing_and_artifact_contract.md) | 라우팅 + 산출물 계약 + 스키마 | 계약 확정 시 |
| [04_automated_review_and_governance.md](04_automated_review_and_governance.md) | 검수 3층 · 티어 게이트 · 금지선 | 검수 설계 시 |
| [05_human_collaboration.md](05_human_collaboration.md) | 1인1역할 · owner≠reviewer · 인프라 규약 | 팀 구성 시 |
| [06_positioning_method.md](06_positioning_method.md) | **포지셔닝 방법론**(결론 아님) | 기획 초기 |
| [APPENDIX_CASE_BIOP02.md](APPENDIX_CASE_BIOP02.md) | 실사례·사고 기록 (참고용) | 규칙의 이유가 궁금할 때 |

## 표기 규칙

- `{{SLOT}}` — [PROJECT_SLOTS.md](PROJECT_SLOTS.md)에서 채우는 자리. **채우지 않은 `{{ }}`가 남아 있으면 그 문서는 아직 쓰면 안 된다.**
- 🔒 — 사람이 통과시키는 게이트(자동화 금지)
- ⚠️ **처음부터 정할 것** — BIOP02가 비워둔 채 운영해 비용을 치른 자리. 새 프로젝트는 **여기부터** 정한다.

## 한 줄 요약

> 자동화의 목표는 **사람을 빼는 것이 아니라, 사람이 판단해야 할 지점만 남기고 나머지 노동을 에이전트가 대신하는 것**이다.
> 그래서 이 하네스의 핵심은 에이전트 개수가 아니라 **게이트의 위치**와 **강제 수단**이다.

## 시작하기

```
1. PROJECT_SLOTS.md 를 채운다        ← 여기서 막히면 설계가 아직 안 정해진 것이다
2. BOOTSTRAP.md 순서대로 설치한다
3. 01~05 를 읽고 프로젝트 문서로 복사·조정한다
4. 06 으로 포지셔닝을 직접 수행한다  ← 결론을 베끼지 않는다
```

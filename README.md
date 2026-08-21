# AI Scientist Rigor Harness

인간+AI 연구팀이 **검증 가능하고 정직하게 주장된 과학**을 산출하도록 만드는 재사용 하네스.
자율 "발견"을 파는 프레임워크와 달리, 이 하네스의 초점은 **검증(verification)과 규율(discipline)** — AI의 그럴듯하지만-틀린 산출을 걸러내는 층이다.

> Designed by Ka-Kyung Kim · **CC BY 4.0** (저작자 표시 유지). BioProject02 운용 경험을 일반화한 것으로, 특정 프로젝트의 사례·결과는 해당 논문 공개 시 함께 공개한다.

## 구성

| 디렉토리 | 내용 |
|---|---|
| `ai_scientist/template/` | **프로젝트 무관 설계 템플릿** — 2-레이어 아키텍처·에이전트 명부·라우팅/계약·자동검수/거버넌스·인간 협업·포지셔닝. `{{슬롯}}`을 채워 새 프로젝트에 이식(`BOOTSTRAP.md`→`GETTING_STARTED.md`). |
| `ai_scientist/cross_session_work_discipline.md` | **도구 무관 작업 규율** — 전수 스캔(3관문)·4구역 마무리·개인↔팀 기록 분리. 어떤 CLI든 따를 수 있는 원칙. |
| `gates/` | **검증 게이트** — CI 검증기 배선(`critic-validators.yml`) + 회고적 사전등록 탐지 게이트(`check_seal_timeline.py`, 비공허 자기검증 포함). |

## 핵심 아이디어

- **검증기가 자기 자신을 검증한다** — 게이트가 실제 결함을 잡는지 mutation/공허통과로 시험(통과만 하는 게이트는 게이트가 아니다).
- **incident → registry → 가드 루프** — 실제 사고를 재발방지 장치(CI)로 전환.
- **정직 규율** — hypothesis_only·검정력 게이트·골대 이동 금지·Owner≠Reviewer.

## 시작

```bash
cat ai_scientist/template/BOOTSTRAP.md      # 이식 절차
python3 gates/test_seal_timeline.py         # 게이트 자기검증 데모(비공허 확인)
```

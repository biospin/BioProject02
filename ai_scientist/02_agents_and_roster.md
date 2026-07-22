# 02 — 다중 에이전트 명부 (Roster)

AI Scientist는 "한 명의 만능 에이전트"가 아니라 **벤치(bench)별로 역할이 나뉜 에이전트 랩**으로 설계됐다. 각 에이전트는 `.claude/agents/<name>.md`에 시스템 프롬프트·도구 권한·산출물 계약이 정의되어 있고, `docs/HARNESS.md`가 이를 하나의 연구실 조직도로 묶는다.

## 로스터 (근거: `docs/HARNESS.md` §1, `.claude/agents/`)

| 벤치 | 에이전트 | 한 줄 역할 | 도구 |
|---|---|---|---|
| **분석실** | `spatialpatho-analyst` | (도메인 슬롯) WSI→임베딩→표현형→치료근거 파이프라인 대표·eval·통계, result 파일 유지 | Read, Write, Edit, Bash, Grep, Glob |
| **문헌·기획** | `literature-scout` | 선행연구 발굴·related work·스쿱/novelty 확인·인용 리스트 | WebSearch, WebFetch, Read, Write, Edit, Bash |
| **문헌·기획** | `novelty-strategist` | 차별화 각도 + 그것을 입증할 **가장 싼 실험** 제안 | WebSearch, WebFetch, Read, Grep, Glob, Write |
| **문헌·기획** | `research-methodologist` | 러프 아이디어 → 가설·기여문·baseline/ablation 설계, 누수·통계 감사 | Read/Write/Edit/Bash/Grep/Glob + Web |
| **집필실** | `manuscript-writer` | 프리프린트/저널/블로그 본문·초안 + **그림 스크립트 실행** | Read, Write, Edit, Bash, Grep, Glob |
| **집필실** | `presenter` | 청중 맞춤 슬라이드·발표(랩미팅/학회/블로그). 숫자는 논문·결과파일에서만 | Read, Write, Edit, Bash, Grep, Glob |
| **심사·QA** | `paper-critic` | 제출 전 **적대적 자체검토** + 그림 QA(이미지 열어 tofu/overflow 확인) + 인용 검증 게이트 | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| **심사·QA** | `reviewer` (전역, 선택) | 정식 venue 스타일 리뷰 문서 | — |
| **코디네이션** | `paper-orchestrator` | 멀티-에이전트 작업 **계획만**(실행은 메인 루프) | Read, Grep, Glob, Write |
| **엔지니어링** | `design` | 로고·아이콘·브랜드·그림 미감(SVG 마스터 + PNG) | Read, Write, Edit, Bash |
| **엔지니어링** | figure 스크립트 (agent 아님) | 결과 파일에서 그림 생성·번호 정합 | — |

## 설계상 중요한 두 가지 구분

### (1) "계획하는 에이전트"와 "실행하는 입구"를 분리했다

- `paper-orchestrator` (**agent**) = 여러 단계를 **어떤 순서로 엮을지 계획만** 한다. 서브에이전트는 서브에이전트를 못 낳기 때문에 실행은 못 한다.
- `paper-production-orchestrator` (**Skill**) = **메인 루프(PI 역할)가 직접 실행**하는 입구. "풀 파이프라인 돌려줘", "그림만 다시", "critic 지적 반영" 같은 요청이 여기로 들어온다.

근거: `docs/HARNESS.md` §2 하단, `.claude/skills/paper-production-orchestrator/SKILL.md` L8.

### (2) 도메인 특수성은 단 하나의 슬롯에 격리했다

로스터에서 `spatialpatho-analyst`만 이 프로젝트 고유(도메인 슬롯)이고, 나머지는 전부 **"재사용"** 표시다(`docs/HARNESS.md` §1의 상태 칼럼). 즉 문헌·집필·검수·발표 벤치는 **어느 논문 프로젝트에도 그대로 옮겨 붙는 연결조직**으로 설계했고, H&E·병리·DepMap 같은 도메인 지식은 한 슬롯 안에 가뒀다. 그 슬롯 자체도 단일 스크립트가 아니라 `agents/data|embedding|modeling|therapeutic_evidence/` 역할 워크스페이스들의 대표다(`.claude/agents/spatialpatho-analyst.md`).

## 에이전트 발행 규칙 (구현 디테일)

서브에이전트가 "Bash를 못 쓰는 것처럼" 보이는 실패를 막기 위한 프롬프트 규약이 `CLAUDE.md` *에이전트 발행·프롬프트 규칙* 절에 못박혀 있다:

- 첫 줄에 "슬래시 커맨드/스킬 쓰지 말고 Bash로 Python 직접 실행하라" 명시.
- 실행 코드를 **copy-paste 가능한 형태로 직접** 프롬프트에 포함(추상 지시 금지).
- python/env 경로 명시(GPU·임베딩·MIL은 `conda run -p /opt/envs/spatialpatho python ...`).
- "스캔해서 설정 업데이트" 같은 표현 회피(엉뚱한 스킬 트리거).

이것은 "에이전트가 권한이 없다"가 아니라 **"프롬프트가 나쁘면 에이전트가 무력해진다"** 는 운영 학습을 설계에 반영한 것이다.

→ 다음: [03_routing_and_artifact_contract.md](03_routing_and_artifact_contract.md)

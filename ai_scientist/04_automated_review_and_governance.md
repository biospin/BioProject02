# 04 — 자동 검수 루프 + 거버넌스 (설계의 핵심 차별점)

이 설계에서 가장 공들인 부분이자 선행연구와의 **실질적 차별점**이다. 핵심 질문은:

> **"AI가 논문을 몇 주에 걸쳐 검수·수정하는 동안, 사람이 매번 병목이 되지 않게 하려면?"** (2026-07 스터디 논의, `SKILL.md` "자동 리뷰 루프" 절)

답: **AI가 리뷰 노동을 대신하고, 사람은 "판단해야만 하는 항목"만 처리한다.** 코드는 `agents/critic/`에 실제로 구현되어 있다:
`auto_review_gate.py` · `auto_review_orchestrator.py` · `auto_review_config.json` · `AI_REVIEW_PROMPT.md` · `cron_auto_review.sh`.

## 루프 구조

```
  (cron 주기 스캔 또는 사람 트리거)
        │
        ▼
  ① 결정론 게이트 (auto_review_gate.py)     ← LLM 없이 규칙만
        │  하드룰 위반? → blocked (즉시 정지)
        │  아니면 티어 분류 (A/B/C) + AI리뷰 큐 적재
        ▼
  ② 큐 → drain (auto_review_orchestrator.py --drain-queue)
        │  항목마다 '에이전트 호출 스펙'(review_request.json) 발행
        │  owner→reviewer 자동 배정 (cross_review_map)
        ▼
  ③ AI 적대적 리뷰 (paper-critic + reviewer, independent_passes회)
        │  7-point 체크리스트 + 적대적 다중패스 + headline 수치 재계산
        │  → critic_report.json (schemas/critic_report.schema.json)
        ▼
  ④ 티어별 처리
        ├─ Tier B → provisional : 진행·커밋 허용, 공유/공개만 사람 1-클릭 confirm
        └─ Tier C → needs_human : 사람이 adjudicate (headline·publish)
```

근거: `SKILL.md` 스텝 5, `auto_review_orchestrator.py`, `auto_review_config.json`.

## 3단계 티어 게이트 — "사람을 어디에 둘지"의 설계

`auto_review_config.json`이 **결정 항목 전부를 코드 밖 config로 뺐다**(코드는 project-agnostic). 티어별로 사람 개입 정도가 다르다:

| 티어 | 무엇 | 처리 | 사람 개입 |
|---|---|---|---|
| **하드룰 위반** | 금지 프레이밍(`"drug response prediction"`, `"personalized therapy"`, `"약물반응예측"` …), 필수필드 누락, `claim_level≠hypothesis_only` | `blocked` 즉시 | 정지 — 고쳐야 통과 |
| **Tier C** | manuscript·preprint·abstract·법칙·publish·main figure | `needs_human` | **사람이 adjudicate** (headline·공개) |
| **Tier B** (기본) | 그 외 실험·분석 결과 | `provisional` | **진행·커밋 허용**, 공유만 1-클릭 confirm |
| **Tier A** | guide·docs·README·HANDOFF·setup·manifest | 가벼운 경로 | 대부분 자동 |

설계 의도(`SKILL.md`): **"진행을 사람 리뷰에 볼모 잡지 않는다."** 사람이 하드 블로킹하는 건 headline·publish(Tier C)뿐이고, 나머지는 AI 리뷰 통과 시 계속 굴러간다.

## 하드룰이 "안전 마커"까지 검사하는 이유 (미묘한 설계)

`forbidden_phrases`는 금지 표현을 잡지만, 그 표현이 **"이 표현은 금지"라고 설명하는 문서**(anti_patterns.md, checklist 등)에서 나오면 오탐이다. 그래서 `forbidden_safe_markers`(금지·아님·not·❌·anti-pattern·regex …)와 `meta_files` 목록으로 **"금지어를 설명 중인 맥락"을 면제**한다. 즉 게이트가 자기 자신의 규칙 문서에 걸려 넘어지지 않게 설계됐다.

## 리뷰어 부재 폴백 — 소규모 팀에서도 돌아가게

리더 1인만 가용해 owner=reviewer가 되는 경우(교차검수 불가), `owner_ne_reviewer` 폴백이 작동:
- AI 적대 **독립 패스 ≥3** + 리더 확인(라벨 `ai-adversarial+leader-confirm`)
- 단 **headline은 타인 1인 필수**(`headline_requires_second_human: true`)

→ 몇 주 정체 대신 계속 진행. 근거: `auto_review_config.json` L44-50, `SKILL.md`.

## 안전 기본값: dry-run

`auto_review_config.json`의 `enabled: false`가 기본값이다. 이 상태에선 오케스트레이터가 **무엇을 할지만 출력하고 실제 행동은 안 한다**(dry-run). "스터디에서 결정 항목을 정하면 `<DECIDE...>` 값만 채우고 `enabled=true`" — **코드 변경 없이** 활성화. 이는 "자동 검수가 아직 팀 합의 전이므로 함부로 켜지 않는다"는 안전 설계다 (`auto_review_orchestrator.py` docstring, config `_purpose`).

## 거버넌스: 절대 금지 사항 (자동화가 넘지 못하는 선)

AI Scientist가 아무리 자동이어도 넘지 못하게 못박은 선 (`CLAUDE.md` *Absolute Prohibitions*, `AGENTS.md` §7):

- ❌ HF 토큰/AWS 키 git commit
- ❌ 약물 구조(SMILES·fingerprint·learnable embedding) 모델 입력 — DRP 아님
- ❌ "환자별 최적 치료 예측"·"개인 맞춤 치료" 표현
- ❌ cell-line transfer로 ICI/Pembrolizumab 추천
- ❌ **Critic이 자기 임계값/control을 스스로 정하는 것** (anti-self-reference)
- ❌ **발표자료·슬라이드의 숫자를 합격 기준으로 쓰기** — 기준은 봉인된 사전등록 문서 + 실물 코드뿐, `파일:줄`로 인용
- ❌ **도구가 "못 찾겠다"고 한 것을 통과로 처리** — `verify-refs`가 DOI 실패 시 약한 제목검색으로 `OK` 주는 함정 → 사람/적대 검증으로 에스컬레이션

특히 두 번째부터의 항목은 **"AI가 스스로 골대를 옮기거나(자기 기준 설정), 도구의 거짓 통과를 믿는" 실패**를 실제 사고에서 학습해 금지로 승격한 것이다.

→ 다음: [05_human_collaboration.md](05_human_collaboration.md)

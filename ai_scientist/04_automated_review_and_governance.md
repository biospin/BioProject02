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
  ③ AI 적대적 리뷰 (paper-critic, independent_passes회)
        │  7-point 체크리스트 + 적대적 다중패스 + headline 수치 재계산
        │  → critic_report.json (schemas/critic_report.schema.json)
        ▼
  ④ 티어별 처리
        ├─ Tier B → provisional : 진행·커밋 허용, 공유/공개만 사람 1-클릭 confirm
        └─ Tier C → needs_human : 사람이 adjudicate (headline·publish)
```

근거: `SKILL.md` 스텝 5, `auto_review_orchestrator.py`, `auto_review_config.json`.

> 🔴 **③과 ④ 사이에 "비판 자체를 검증하는 층"이 없다.** 루프는 비판을 **생산**하고(③) 곧바로 **누가 확인할지**로 넘어간다(④). 비판이 원본을 오독했는지, 없는 주장을 공격했는지, 근거를 지어냈는지를 판정하는 단계가 없다 — 즉 **Critic의 산출물만은 Critic을 거치지 않는다.**
>
> 이 공백은 관념이 아니라 실제 비용으로 나타났다. 2026-07-27 하루에 Critic 코멘트 4건이 **작성자 본인에 의해 사후 정정**됐다(BIOP02-75 #11515·#11521·#11531, BIOP02-59 #11528) — "승인 대기"라고 쓴 것이 3일 전 이미 승인돼 있었고, "원고 draft 미존재"라고 쓴 것이 main에 5개 섹션으로 존재했다. 전부 **비판을 내보내기 전에 검증했다면 걸렸을** 종류다. 그 대응으로 신설된 것이 아래 금지 항목(*티켓·파일을 열지 않고 상태 단정 금지*)인데, 이는 **규율**이지 **단계**가 아니다.
>
> 값싼 이식안: `critic_report.json`의 finding마다 등급을 붙여(예: *유효·치명 / 유효·수정가능 / 부분유효 / 약함 / 부정확 / **근거없음·환각***) 낮은 등급은 내보내지 않는 것. 특히 마지막 등급은 이 프로젝트가 이미 데인 실패(가짜 DOI가 약한 제목검색으로 통과)와 같은 계열이다. ⚠️ 단, 이 역시 **Critic이 자기 검수 절차를 스스로 정하는 것**이라 `anti-self-reference`상 **Leader 승인 사안**이다.

> ⚠️ **2026-07-27 갱신(BIOP02-103): ③에서 `venue-reviewer`를 부르지 않는다.** 자동 리뷰 루프(5단계)는 **`paper-critic`의 자리**이고, 외부 referee 시뮬레이션은 **검증 게이트 ① 통과 후 8단계**에서만 호출한다. 검증 안 된 숫자를 리뷰에 보내지 않기 위해서다.
>
> 🔴 **리포 내부 불일치(2026-08-03 실측, 팀 확인 필요):** `SKILL.md`는 5단계를 `paper-critic` 단독으로 고쳤는데 **`auto_review_config.json`의 `ai_review.agents`는 여전히 `["paper-critic", "reviewer"]`** 이다. 즉 config를 켜면 폐기된 `reviewer`(현 `venue-reviewer`)를 5단계에서 부르게 된다. 지금은 `enabled=false`(dry-run)라 실害가 없지만 **활성화 전 반드시 정리**해야 한다.

## 3단계 티어 게이트 — "사람을 어디에 둘지"의 설계

`auto_review_config.json`이 **결정 항목 전부를 코드 밖 config로 뺐다**(코드는 project-agnostic). 티어별로 사람 개입 정도가 다르다:

| 티어 | 무엇 | 처리 | 사람 개입 |
|---|---|---|---|
| **하드룰 위반** | 금지 프레이밍(`"drug response prediction"`, `"personalized therapy"`, `"약물반응예측"` …), 필수필드 누락, `claim_level≠hypothesis_only` | `blocked` 즉시 | 정지 — 고쳐야 통과 |
| **Tier C** | manuscript·preprint·abstract·법칙·publish·main figure | `needs_human` | **사람이 adjudicate** (headline·공개) |
| **Tier B** (기본) | 그 외 실험·분석 결과 | `provisional` | **진행·커밋 허용**, 공유만 1-클릭 confirm |
| **Tier A** | guide·docs·README·HANDOFF·setup·manifest | 가벼운 경로 | 대부분 자동 |

설계 의도(`SKILL.md`): **"진행을 사람 리뷰에 볼모 잡지 않는다."** 사람이 하드 블로킹하는 건 headline·publish(Tier C)뿐이고, 나머지는 AI 리뷰 통과 시 계속 굴러간다.

### 사람에게 넘기는 것은 "판단"뿐 — `required_followups`

티어가 *언제* 사람을 부를지를 정한다면, `required_followups`는 *무엇을* 넘길지를 정한다.
AI가 리뷰 노동(7-point 대조 · 적대적 다중패스 · 헤드라인 수치 재계산)을 **전부 수행**하고, 사람에게는 **surface된 판단항목만** 올린다 (`SKILL.md` *자동 리뷰 루프*).

> 이 구분이 루프의 핵심이다. 사람이 리뷰 **노동**을 하면 몇 주가 걸리고 그동안 프로젝트가 멈춘다.
> 사람이 리뷰 **판단**만 하면 분 단위로 끝난다. 자동화가 줄이는 것은 판단의 수가 아니라 **판단에 도달하기까지의 노동**이다.

### 🔴 판정 어휘의 빈칸 — "더 해도 pass가 안 되는 것"을 적을 자리가 없다

판정 어휘는 두 축이다(`schemas/critic_report.schema.json` 실측): 종합 `critic_status` = `pass · caution · reject`, 개별 항목 `check.status` = 여기에 `not_applicable` 추가. 티어 처리(`blocked · provisional · needs_human`)는 **누가 확인하느냐**를 정하는 별개 축이다.

어느 축에도 **"현재 데이터로는 판정 자체가 불가능하다"** 를 뜻하는 값이 없다. 그래서 그런 상황이 오면 `caution`으로 뭉뚱그려지고, `caution`은 "더 하면 pass가 될 수도 있다"로 읽힌다.

실제로 이 빈칸 때문에 티켓 하나가 통째로 막혔다 — **BIOP02-75**:
- **#3 counterfactual**은 AUC-level 효과가 **본질적으로 비유의**(ER drop 0.0009 · PAM50 p=0.061)다. 이는 결함이 아니라 **MIL 신호 중복성**이고, **추가 작업으로 pass가 되지 않는다.**
- **HER2**는 `#2 baseline`·`#4 cross_dataset`에서 `reject`다 — "H&E로 안 보임 = 대체 불가"라는 **정직한 음성**이지 실패가 아니다.
- 그런데 티켓의 성공 기준이 *"7항목 전부 pass"* 여서 **문자 그대로 달성 불가능**했고, 데이터를 본 뒤 임계를 낮추는 것은 금지(사후 골대 이동)였다.
- 해결책은 어휘가 아니라 **티켓의 성공 기준을 재정의**하는 것이었다 — `7항목 전부 pass` → `전부 판정 완료 + caution은 Limitation에 명시 서술`(Leader 승인 2026-07-24).

즉 **어휘의 부족을 프로세스로 메웠다.** 판정 어휘에 "이 데이터로는 식별 불가"에 해당하는 값이 있었다면 티켓 재정의 없이 그대로 표현됐을 사안이다. ⚠️ 다만 어휘 확장은 **기존 `critic_report.json` 전부의 유효성**과 `auto_review_gate.py` 하드룰에 영향을 주고, 무엇보다 **Critic이 자기 판정 기준을 스스로 바꾸는 것**이라 `anti-self-reference` 금지에 걸린다 → **Leader 승인 사안이며, -75 최종 서명 이후**가 맞다.

## 하드룰이 "안전 마커"까지 검사하는 이유 (미묘한 설계)

`forbidden_phrases`는 금지 표현을 잡지만, 그 표현이 **"이 표현은 금지"라고 설명하는 문서**(anti_patterns.md, checklist 등)에서 나오면 오탐이다. 그래서 `forbidden_safe_markers`(금지·아님·not·❌·anti-pattern·regex …)와 `meta_files` 목록으로 **"금지어를 설명 중인 맥락"을 면제**한다. 즉 게이트가 자기 자신의 규칙 문서에 걸려 넘어지지 않게 설계됐다.

## 리뷰어 부재 폴백 — 소규모 팀에서도 돌아가게

리더 1인만 가용해 owner=reviewer가 되는 경우(교차검수 불가), `owner_ne_reviewer` 폴백이 작동:
- AI 적대 **독립 패스 ≥3** + 리더 확인(라벨 `ai-adversarial+leader-confirm`)
- 단 **headline은 타인 1인 필수**(`headline_requires_second_human: true`)

→ 몇 주 정체 대신 계속 진행. 근거: `auto_review_config.json` L44-50, `SKILL.md`.

> 🔴 **이 "독립 패스"는 같은 모델의 반복이다 (2026-08-03 실측).** `ai_review.independent_passes: 2`, `owner_ne_reviewer.fallback_min_independent_passes: 3` 어디에도 **모델 다양성을 요구하는 키가 없다.** 그런데 이 설계서가 근거로 인용한 문헌(`panickssery-2024-selfpreference`)이 말하는 것은 **LLM이 자기 출력을 선호한다**는 것이고, 그 편향은 **같은 모델을 N번 돌려도 상쇄되지 않는다.** 반복 횟수는 분산을 줄일 뿐 독립성을 만들지 못한다.
>
> 프로젝트가 이걸 모르는 것은 아니다 — `.claude/agents/venue-reviewer.md`는 *"진짜 리뷰 다양성이 필요하면 **다른 모델 계열**로 실행한다"* 고 이미 적고 있다. **한 곳에서만 알고 있고 자동 루프에는 반영되지 않은 상태**다. 최소 이식안은 전면 다중모델이 아니라 **headline·Tier C에 한해 "서로 다른 모델 계열 2개 이상"** 을 요구하는 것이다(비용 증가가 작고, 편향이 실제로 문제 되는 지점에만 걸린다).

## 안전 기본값: dry-run

`auto_review_config.json`의 `enabled: false`가 기본값이다. 이 상태에선 오케스트레이터가 **무엇을 할지만 출력하고 실제 행동은 안 한다**(dry-run). "스터디에서 결정 항목을 정하면 `<DECIDE...>` 값만 채우고 `enabled=true`" — **코드 변경 없이** 활성화. 이는 "자동 검수가 아직 팀 합의 전이므로 함부로 켜지 않는다"는 안전 설계다 (`auto_review_orchestrator.py` docstring, config `_purpose`).

## CI 검증 레이어 — "만들어 둔 검증이 실제로 돌게" (2026-08-03 신설, BIOP02-106/107)

위 루프와 **별개로** GitHub Actions에 결정론 검증기가 붙었다: `.github/workflows/critic-validators.yml`.

설계 동기가 이 하네스의 성격을 잘 보여준다 — 워크플로 주석 원문:

> *"리포에 검증 자산은 갖춰져 있는데 `.github/workflows/`가 없어, 만들어 둔 검증이 PR에서 **한 번도 자동으로 돌지 않았다**(사람이 기억해서 돌릴 때만). 이번 주 불일치 3건이 전부 눈으로 대조해야만 발견되는 종류였고 5일~2주씩 방치됐다."*

`pull_request`(→ main)와 `push`(main)에서 **blocking**으로 도는 검증기 3종:

| 검증기 | 무엇을 막나 |
|---|---|
| `evals/critic_pilot/mutation_check.py` | scorer가 케이스에 실제로 제약되는지 — **Critic이 무조건 통과시키는 회귀** 탐지 |
| `evals/citation_verifier/mutation_check.py` | `medsci` 회귀 버그(**DOI 실패 시 약한 제목검색으로 `OK`**)가 죽어 있는지 |
| `agents/critic/scripts/check_number_drift.py --strict` | **JSON 정본 ↔ markdown 표 수치 드리프트**(BIOP02-107) |

설계상 중요한 점 3가지:

1. **결정론·오프라인 검증만 blocking으로 건다** — LLM 판단은 CI에 넣지 않는다.
2. **명시적 비범위**: `auto_review_config.json`의 `enabled` 플래그는 **건드리지 않는다**("M7: 팬텀 배선. BIOP02 하네스 스왑 전 활성화 금지"). 라우터 문서도 손대지 않는다.
3. 검증기 3번은 이 프로젝트가 반복해서 데인 실패 — **문서의 표 숫자가 결과 JSON과 어긋나는 것** — 를 기계가 잡게 만든 것이고, 2번은 아래 금지 항목 *"도구가 '못 찾겠다'고 한 것을 통과로 처리"* 를 **회귀 테스트로 못박은** 것이다.

즉 이 하네스의 검수는 **3층**이 됐다: ① CI 결정론 검증기(기계) → ② 자동 리뷰 루프(AI 적대) → ③ 사람 게이트(Tier C·공개).

## 거버넌스: 절대 금지 사항 (자동화가 넘지 못하는 선)

AI Scientist가 아무리 자동이어도 넘지 못하게 못박은 선 (`CLAUDE.md` *Absolute Prohibitions*, `AGENTS.md` §7):

- ❌ HF 토큰/AWS 키 git commit
- ❌ 약물 구조(SMILES·fingerprint·learnable embedding) 모델 입력 — DRP 아님
- ❌ "환자별 최적 치료 예측"·"개인 맞춤 치료" 표현
- ❌ cell-line transfer로 ICI/Pembrolizumab 추천
- ❌ **Critic이 자기 임계값/control을 스스로 정하는 것** (anti-self-reference)
- ❌ **발표자료·슬라이드의 숫자를 합격 기준으로 쓰기** — 기준은 봉인된 사전등록 문서 + 실물 코드뿐, `파일:줄`로 인용
- ❌ **도구가 "못 찾겠다"고 한 것을 통과로 처리** — `verify-refs`가 DOI 실패 시 약한 제목검색으로 `OK` 주는 함정 → 사람/적대 검증으로 에스컬레이션
- ❌ **티켓·파일을 열지 않고 상태를 단정 — 특히 JIRA를 코멘트 없이 조회** (2026-07-27 신설, 하루 4회 실사고). JIRA 기본 응답에는 코멘트가 **빠지고**, 티켓의 실제 상태(승인·결정·지적)는 대개 **최신 코멘트**에 있다. ① 조회 시 `fields`에 `comment` 필수 ② *"없다/미완료/대기 중"* 주장은 **실물을 연 뒤에만** ③ `SESSION_LOG`·기억은 근거가 아니며 **코멘트 id 또는 `파일:줄`**을 명시한다.

특히 다섯 번째부터의 항목은 **"AI가 스스로 골대를 옮기거나(자기 기준 설정), 도구의 거짓 통과를 믿거나, 열어보지 않고 단정하는" 실패**를 실제 사고에서 학습해 금지로 승격한 것이다. 이 셋은 형태가 달라도 뿌리가 같다 — **근거 없이 상태를 주장하는 것.** 그래서 규칙도 같은 모양이다: *근거는 봉인 문서·실물 코드·실물 코멘트뿐이고, 인용할 땐 `파일:줄` 또는 코멘트 id를 밝힌다.*

→ 다음: [05_human_collaboration.md](05_human_collaboration.md)

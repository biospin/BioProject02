# GETTING_STARTED — 새 분석 프로젝트 첫 2주 (step-by-step)

실제로 따라 칠 수 있는 순서. 명령·파일 골격·채워진 예시를 포함한다.

| 문서 | 역할 |
|---|---|
| [BOOTSTRAP.md](BOOTSTRAP.md) | **무엇을** 세우나 — Phase 체크리스트·원칙 |
| **이 문서** | **어떻게** 따라 하나 — 명령·골격·예시·일정 |

> 예시는 가상의 분석 프로젝트 **"설비 센서 로그 → 이상 징후 → 정비 우선순위 제안"** 을 쓴다.
> 도메인만 바꾸면 그대로 적용된다.

---

## 일정 개요

| 언제 | Step | 산출 |
|---|---|---|
| Day 1 오전 | 0·1 | 계정·리포 뼈대 |
| Day 1 오후 ~ Day 2 | **2. 규율 3장** | 목표·금지·아티팩트 확정 ⭐ |
| Day 3 | 3. 레이어 A 최소 실행 | 더미 실험 1건 |
| Day 4 | **4. 검증 게이트 ①** | `verify_gate.py` 실행 ⭐ |
| Day 5 | 5·6 | 에이전트 배선 + dry-run |
| Week 2 | 7·8 | 연동 + 첫 실전 사이클 |

⭐ = **미루면 나중에 못 고치는 단계.**

---

## Step 0. 준비물 (30분)

- [ ] 저장소 호스트 계정, 이슈 트래커 프로젝트 키, 위키 스페이스
- [ ] 알림 봇 토큰 (→ [INTEGRATIONS §4](INTEGRATIONS.md))
- [ ] 실행 환경(인터프리터·의존성) — 팀 전원이 같은 경로로 접근 가능한지 확인
- [ ] **계정 간 실제로 공유되는 경로**를 확인한다

```bash
# 공유 경로 검증 — "권한을 열었는데도 안 보이는" 사고를 여기서 막는다
touch /shared/path/_probe_$USER && ls -l /shared/path/_probe_*
# 다른 계정으로 로그인해 같은 파일이 보이는지 확인 → 안 보이면 그 경로는 공유가 아니다
```

## Step 1. 리포 뼈대 (30분)

```bash
mkdir -p myproject && cd myproject && git init

# 레이어 A — 역할 워크스페이스 (도메인에 맞게 이름 변경)
mkdir -p agents/{data,features,modeling,evidence,critic}
# 계약·스키마·실험·검증
mkdir -p schemas experiments/registry scripts docs .github/workflows

# 하네스 템플릿 복사
cp -r /path/to/ai_scientist/template docs/harness
```

```bash
cat > .gitignore <<'EOF'
# 자격증명 — 절대 커밋 금지
.env
*.token
secrets/
# 개인 작업 로그 (백업은 공유 경로로)
HANDOFF.md
SESSION_LOG.md
TODO.md
# 대용량 원본 데이터 — 정본은 외부 스토리지
data/raw/
EOF

git add -A && git commit -m "chore: 프로젝트 뼈대 + 하네스 템플릿"
```

**완료 판정:** `git log`에 커밋 1개, `docs/harness/`에 템플릿 11문서.

## Step 2. 규율 3장 채우기 ⭐ (반나절 ~ 1일)

> **여기서 코드를 쓰지 않는다.** 판정 기준 없이 검수 에이전트를 붙이면 **그 에이전트가 자기 기준을 만든다.**

팀이 모여 [PROJECT_SLOTS.md](PROJECT_SLOTS.md)의 **A·B·C절**만 먼저 채운다. 세 문장이 핵심이다:

**(1) 목표 한 문장 + "이 프로젝트가 아닌 것"**

```
{{PROJECT_GOAL}}  센서 로그에서 설비 이상 징후를 탐지하고 정비 우선순위 후보를 순위화한다
{{PROJECT_NOT}}   ❌ 고장 시점 예측이 아니다. ❌ 잔여수명(RUL) 보장이 아니다.
                  ❌ 정비 지시가 아니라 우선순위 "후보" 제안이다.
```

> `{{PROJECT_NOT}}`을 못 쓰면 금지 프레이밍도 못 쓴다 — 둘은 같은 문장의 앞뒤다.

**(2) 하드룰 — 즉시 차단할 표현**

```
{{FORBIDDEN_PHRASES}}   "고장을 예측한다" / "잔여수명 보장" / "정비 불필요 판정"
                        / "무고장 보증" / "predicts failure"
{{CLAIM_LEVEL}}         candidate_only        ← 기본 주장 수준
```

**(3) 실험이 남길 증거**

```
{{REQUIRED_ARTIFACTS}}  config.yaml · model.pkl · metrics.json · predictions.parquet · critic_report.json
{{METRIC_FIELDS}}       auprc · recall_at_k · lead_time_hours · n_train · n_val · model · commit_hash
{{EXPERIMENT_DIR}}      experiments/<user>/<YYYYMMDD_설명>/
```

이 값들을 프로젝트 루트 규율 문서(에이전트 지침서 겸용) 1장에 적는다.

- [ ] ⚠️ **검수 기준을 검수 총괄 본인이 아닌 사람이 승인**했다 (anti-self-reference)

**완료 판정:** A·B·C절에 `{{ }}`가 없다. 팀원이 "이 표현 써도 되나?"를 문서만 보고 답할 수 있다.

## Step 3. 레이어 A 최소 실행 (1일)

**더미 데이터로 파이프라인을 한 바퀴 돌려 아티팩트가 남는지 확인한다.** 모델 성능은 아직 신경 쓰지 않는다.

```bash
python agents/modeling/train.py --config configs/dummy.yaml \
       --out experiments/$USER/$(date +%Y%m%d)_smoke/
ls experiments/$USER/*_smoke/
# config.yaml  model.pkl  metrics.json  predictions.parquet
```

`metrics.json`에 **커밋 해시를 자동 기록**한다:

```python
import subprocess, json
metrics["commit_hash"] = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True).strip()
```

**완료 판정:** 아티팩트 5종이 전부 생성되고 `metrics.json`에 `{{METRIC_FIELDS}}`가 채워져 있다.
하나라도 비면 **Step 4로 넘어가지 않는다** — 게이트가 검사할 대상이 없다.

## Step 4. 검증 게이트 ① 만들기 ⭐ (1일)

> **이 단계를 건너뛰면 하네스의 중심이 빈 채로 돈다.** "검증했다"가 사람의 기억에 의존하게 된다.
> **문서 규칙 검사(금지어·필드 존재)를 수치 재계산으로 착각하지 않는다.**

### 4-1. 주장 매니페스트

문서에 실린 숫자마다 **어디서 왔는지**를 선언한다.

```json
// claims.json
[
  {
    "id": "headline_auprc",
    "stated_in": "docs/report.md:42",
    "stated_value": 0.812,
    "source": "experiments/alice/20260901_v3/metrics.json",
    "json_path": "auprc",
    "tol": 1e-6
  }
]
```

### 4-2. 게이트 스크립트

```python
#!/usr/bin/env python3
"""verify_gate.py — 헤드라인 숫자를 정본에서 재계산·대조. 불일치면 종료코드 1."""
import json, sys, argparse
from pathlib import Path

def load(path, jpath):
    obj = json.loads(Path(path).read_text())
    for key in jpath.split("."):
        obj = obj[int(key)] if key.isdigit() else obj[key]
    return obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="claims.json")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    claims, bad = json.loads(Path(a.claims).read_text()), []
    for c in claims:
        try:
            actual = load(c["source"], c["json_path"])
        except Exception as e:                      # 정본이 없거나 경로가 틀림
            bad.append((c["id"], "SOURCE_ERROR", str(e))); continue
        stated = c["stated_value"]
        if abs(float(actual) - float(stated)) > c.get("tol", 1e-6):
            bad.append((c["id"], f"stated={stated}", f"actual={actual}"))

    for b in bad:
        print("MISMATCH", *b, file=sys.stderr)
    print(f"{len(claims) - len(bad)}/{len(claims)} 일치")
    sys.exit(1 if (bad and a.strict) else 0)

if __name__ == "__main__":
    main()
```

```bash
python scripts/verify_gate.py --claims claims.json --strict; echo "exit=$?"
```

### 4-3. 일부러 깨뜨려 본다

```bash
# claims.json 의 stated_value 를 살짝 바꾼 뒤 재실행 → exit=1 이어야 한다
```

**완료 판정:** 값을 틀리게 바꿨을 때 **실제로 실패한다.** 통과만 하는 게이트는 게이트가 아니다.
`{{VERIFY_GATE_1_CMD}}` 슬롯에 이 명령을 적는다.

## Step 5. 에이전트 배선 (반나절)

```bash
mkdir -p .claude/agents .claude/skills/paper-production-orchestrator
```

- [ ] 재사용 에이전트 정의를 복사한다 (문헌 3 / 집필 2 / 심사 2 / 코디 1 / 디자인 1)
- [ ] **`{{DOMAIN_AGENT}}` 하나만 새로 쓴다** — 예: `sensor-analyst`
- [ ] **모든 정의에 도구 목록을 명시 선언한다** ⚠️ 미선언은 전체 상속이다

```yaml
# .claude/agents/paper-critic.md 프론트매터 — 검수자는 쓰기 권한 없음
---
name: paper-critic
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch   # ← Write/Edit 없음
---
```

- [ ] 라우팅표 + 산출물 계약표를 규율 문서에 적는다 → [03](03_routing_and_artifact_contract.md)

**완료 판정:** 로스터를 훑으며 칸마다 *"도구가 막는가, 말이 막는가"* 를 표시했고, 말이 막는 칸이 **의도된 것**이다.

## Step 6. 검수 루프 dry-run (반나절)

- [ ] 검수 코드 복사 + `review_config.json` 작성 (**결정 항목 전부 config로**)
- [ ] **`enabled: false`** 로 둔 채 한 바퀴 돌린다

```bash
python agents/critic/review_orchestrator.py --scan experiments/
# == DRY-RUN (enabled=false) — 실제 행동 안 함 ==
# B  provisional  experiments/alice/20260901_v3
```

- [ ] CI에 결정론 검증기를 blocking으로 건다

```yaml
# .github/workflows/validators.yml
on: [pull_request, push]
jobs:
  validators:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: python scripts/verify_gate.py --claims claims.json --strict
      - run: python evals/critic/mutation_check.py     # 검수기가 무조건 통과시키는 회귀 탐지
```

**완료 판정:** PR을 하나 열어 CI가 **실제로 돈다.** 일부러 숫자를 틀리면 **빨간불이 뜬다.**

## Step 7. 연동 (반나절)

→ [INTEGRATIONS.md](INTEGRATIONS.md) 전문

- [ ] ⚠️ **`{{SOURCE_OF_TRUTH}}` 정본 표를 먼저 채운다**
- [ ] 스마트 커밋 확인 — `git config user.email`이 트래커 계정과 같아야 한다
- [ ] 티켓 조회에 **`comment` 포함**
- [ ] 알림 봇 연결 + 채널 분리(공지 / 진행 / 결과공유 / 긴급)

```bash
# 알림 1회 테스트
curl -sS -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
  --data-urlencode "chat_id=$TELEGRAM_CHAT_ID" \
  --data-urlencode "text=[SETUP] 하네스 연결 완료" -d "disable_web_page_preview=true"
```

**완료 판정:** 티켓을 하나 만들고 → 알림이 오고 → 커밋으로 상태가 바뀐다. **루프가 닫혔다.**

## Step 8. 첫 실전 사이클 1회 (Week 2)

작은 과제 하나로 **끝까지** 돈다. 성능이 목표가 아니라 **하네스가 도는 것**이 목표다.

```
티켓 생성 → 브랜치 → 분석 실행 → 아티팩트 5종
  → 검수(owner ≠ reviewer) → 🔒 게이트 ① → PR → CI 통과 → 병합
  → 결과 공유(검수 통과 후) → 위키에 결정 기록 → 세션 로그
```

**완료 판정:** 위 흐름 중 **막힌 지점을 기록**했다. 첫 사이클의 목적은 통과가 아니라 **병목 발견**이다.

---

## 최종 체크 (하네스 가동 선언 전)

- [ ] `{{ }}` 미치환 슬롯 0개
- [ ] **게이트 ①이 실제로 실패할 수 있다**(일부러 깨뜨려 확인)
- [ ] 검수 기준을 검수 총괄 본인이 정하지 않았다
- [ ] owner ≠ reviewer 매핑이 사람 규칙과 자동 루프에 **동일하게** 들어갔다
- [ ] 토큰이 커밋되지 않았다
- [ ] 결과 공유 채널이 **검수 통과 후에만** 쓰인다
- [ ] **세션 착수·마무리 규율**을 팀이 합의했다([05 §(F)](05_human_collaboration.md)) — "할 일 없다"·"반영 다 했다"는 **전수 확인 뒤에만**

## 흔한 실수 6가지

| # | 실수 | 결과 | 예방 |
|---|---|---|---|
| 1 | 에이전트부터 만든다 | 검수 에이전트가 **자기 기준을 만든다** | Step 2를 먼저 |
| 2 | 게이트 ①을 "나중에" | 검증이 **기억에 의존**하게 됨 | Step 4를 미루지 않는다 |
| 3 | 게이트를 통과만 시켜보고 끝 | 못 잡는 게이트를 믿게 됨 | **일부러 깨뜨려** 확인 |
| 4 | 도구 목록 미선언 | 격리·권한이 **말뿐**이 됨 | 모든 정의에 `tools:` 명시 |
| 5 | 남의 금지어 목록 복사 | 자기 분야 과잉주장은 **못 잡음** | `{{PROJECT_NOT}}`에서 직접 도출 |
| 6 | 채팅·기억을 상태 근거로 | "승인 대기"라 썼는데 **이미 승인됨** | 커밋·`파일:줄`·코멘트 id로 인용 |

## 규모별 조정

| 팀 | 조정 |
|---|---|
| **1인** | Step 5 재사용 에이전트는 최소만. 리뷰어 부재 폴백 사용(독립 패스 ≥3 + **모델 계열 다르게**), 헤드라인은 타인 1인 확인 |
| **2~3인** | 그대로. cross-review 매핑만 단순화 |
| **4인+** | Step 2를 **워크샵으로** 진행 — 금지 프레이밍은 합의가 필요하다 |

## 부록 — 채워진 PROJECT_SLOTS 예시 (발췌)

```
{{PROJECT_NAME}}      SensorTriage
{{PROJECT_GOAL}}      센서 로그 → 이상 징후 → 정비 우선순위 후보 순위화
{{PROJECT_NOT}}       고장 시점 예측 아님 / RUL 보장 아님 / 정비 지시 아님
{{DOMAIN_AGENT}}      sensor-analyst
{{PIPELINE_STAGES}}   수집 → 정합·결측 → 피처 → 이상탐지 → 우선순위 → 검수
{{CLAIM_LEVEL}}       candidate_only
{{FORBIDDEN_PHRASES}} "고장을 예측한다" / "잔여수명 보장" / "정비 불필요 판정"
{{METRIC_FIELDS}}     auprc · recall_at_k · lead_time_hours · n_train · n_val · commit_hash
{{VERIFY_GATE_1_CMD}} python scripts/verify_gate.py --claims claims.json --strict
{{TIER_C_PATHS}}      report/ · summary/ · publish/
{{DEFAULT_TIER}}      B
{{MODEL_DIVERSITY}}   헤드라인·Tier C는 서로 다른 모델 계열 2개 이상
{{CROSS_REVIEW_MAP}}  alice→bob · bob→carol · carol→alice
```

> ⚠️ **이 값들을 그대로 쓰지 않는다.** 도메인이 다르면 금지 표현도 지표도 다르다.
> 형태만 참고하고 **내용은 직접 도출**한다.

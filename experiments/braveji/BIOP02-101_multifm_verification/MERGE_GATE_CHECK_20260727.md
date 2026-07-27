# PR #73 (BIOP02-101/91) 병합 가능 여부 — Critic 확인

**확인자:** braveji (Critic 총괄) · 2026-07-27 · 대상 브랜치 `feat/BIOP02-91-kkkim-multifm-virchow2` → `main`
**근거:** JIRA BIOP02-101 #11520 · BIOP02-75 #11521

---

## 1. 기계적 병합 — 안전 ✅

| 항목 | 결과 |
|---|---|
| 충돌 | **없음** (`git merge-tree --write-tree origin/main <branch>` exit 0) |
| **파일 유실** | **0건** — `origin/main` 983 파일 → 병합결과 트리 1014 파일 |
| 규모 | 42 파일 · +9453 / −72 · 바이너리 2 (`fig3_axis_cost.{png,pdf}`) |
| ahead/behind | main만 2 (= braveji PR #75 `0a31c62`) · 브랜치만 26 |
| 내 산출물 보존 | `FIGURES_INDEX.md` Fig 2 pass 서명 문구 · `reverify_4fixes.py` 둘 다 병합 후 **보존 확인** |

### 유실 점검 방법 (PITFALLS A8 준수)

`docs/PITFALLS_REGISTRY.md` A8 — **머지로 인한 파일 유실은 `git log --diff-filter=D`에 잡히지 않는다**(이건규 BIOP01-71 발견). 따라서 diff 필터를 쓰지 않고 **병합결과 트리를 직접 비교**했다:

```bash
TREE=$(git merge-tree --write-tree origin/main origin/feat/BIOP02-91-kkkim-multifm-virchow2 | head -1)
git ls-tree -r --name-only origin/main | sort > a.txt
git ls-tree -r --name-only $TREE        | sort > b.txt
comm -23 a.txt b.txt   # 사라지는 파일 → 0건
```

### 병합 범위 (티켓 밖 동승분)

Paper C 결과 외에 아래가 함께 실린다 — 병합 승인 시 이것들도 승인하는 것이다.

| 영역 | 파일 수 |
|---|---|
| `experiments/crosscancer/` (Paper C 결과·정본) | 24 |
| `experiments/kkkim/` (cost·multifm 산출) | 9 |
| `blog/` (발행 원고 4편) | 4 |
| 회의록 (`MEETING_BRIEF`·`MEETING_MINUTES` 2026-07-21) | 2 |
| `manuscript/sections/02_results.md` (37줄 → 92줄) | 1 |
| `.claude/commands/bg.md` (하네스 설정) | 1 |
| `docs/PITFALLS_REGISTRY.md` | 1 |

---

## 2. 서명 게이트 — 미개방 ❌

kkkim이 #11459에서 설정: `G1 결과확정 → 다중 FM Owner≠Reviewer 사인오프 + 7-point 최종서명(BIOP02-75)`

| 게이트 | 상태 |
|---|---|
| G1 결과확정 | ✅ kkkim 07-14 |
| sjpark 사인오프 | ✅ #11462 (파생통계·순서보존·서술규율 from-scratch 재계산) |
| **braveji 다중 FM 사인오프** | ⏳ **finding ③ 1건만 남음** |
| **BIOP02-75 최종 서명** | ⏳ Discussion 한계에 caution 3종 명시 필요 |

### findings 반영 현황 (braveji #11466/11467 제시 → #11520 재평가)

| finding | 상태 | 근거 |
|---|---|---|
| ② 모델 비의존성 = 폐 한정 | ✅ **완료** | `02_results.md` L60(무게중심=폐 순서보존) · **L74**("단일 칸 확증이 세 모델 전부에서 통과한 것은 아니므로 '파운데이션 모델과 무관하게 확증'이라고 쓰지 않는다") · R5를 Supplement로 배치 |
| ① egfr_amp 허위 PASS | 🟡 **심각도 하향** | `02_results.md` **L36이 이미 "두경부 EGFR 증폭 / 17 / 미결"** — 원고 과대주장 아님. JSON `"pass": true`(real 0.5046=우연)만 caveat 없음 = **위생 문제, 병합 차단 사유 아님** |
| ③ n_null=5 임계 불안정 | ❌ **미반영** | `CROSSCHECK_5SEED_MULTIFM.md`에 한계 절 자체가 없음. 경계 3건이 실제 이 영역: **virchow2 HPV −0.0035**(null sd 0.2408) · 대장 BRAF virchow2 +0.011 · egfr_amp 양측 |

**→ ③ 1개 절 추가 시 braveji 다중 FM 사인오프 즉시 가능.**

---

## 3. 게이트 결합 재검토 제안 (Leader 판단)

`-75`의 잔여 블로커는 **Paper A 원고 Discussion 집필**이다. 현 게이트 구조는 **Paper C 병합이 Paper A 집필을 기다리게** 만든다.

PR #73 내용은 Paper C이고 이미 **Supplement 배치 · `claim_level: hypothesis_only` · 헤드라인 승격 금지**가 걸려 있어, Paper A 원고 일정과 이 브랜치의 결과 진실성은 분리 가능해 보인다. **게이트를 "다중 FM 사인오프"만으로 좁히는 것**을 제안한다. 게이트 변경은 Leader 소관이므로 판단을 따른다.

---

## 4. 자기 정정 기록 (이 확인 과정에서 발견)

Critic 자신의 오류도 남긴다 — 근거 없이 단정한 것이 두 건이다.

1. **#11517 finding ① 과장** — "Results 표를 JSON에서 자동 생성하면 pass가 실린다"고 썼으나 **원고 표는 이미 "미결"**이었다. 문서에 없음을 보고 원고에도 없으리라 추정했다(원고 미확인).
2. **#11515 "원고 draft 미존재"** — 사실이 아니다. `manuscript/sections/` 5개 섹션이 main에 존재한다. **열어보지 않고 단정**했다. 같은 날 #11511("kkkim 승인 대기" — 승인은 07-24 #11402에 이미 있었음)과 **같은 종류의 오류를 두 번** 저질렀다.

**규율:** 상태를 보고할 때 (a) JIRA는 `fields:["comment"]`로 코멘트를 반드시 fetch하고, (b) "없다"는 주장은 **파일을 열어 확인한 뒤에만** 쓴다. SESSION_LOG·기억은 근거가 아니다.

`claim_level: hypothesis_only` 유지.

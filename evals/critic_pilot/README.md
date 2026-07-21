# Critic Inspect eval — pilot (3 of 7 checklist items)

Encodes **3 of the 7 items** in [`agents/critic/checklist_v1.md`](../../agents/critic/checklist_v1.md)
as deterministic Inspect scorers, and seeds a regression corpus from the 6 real
failures of **2026-07-17**.

Status: **pilot**. Not wired into CI. Not a Critic replacement — see [Scope limits](#scope-limits).

---

## Why this exists

From `AutoBioX_하네스_에이전트_점검_2026-07-17.md`:

- **§5.2** — "Critic의 **7항목 체크리스트 → 항목별 scorer로 인코딩**" and
  "**실패 케이스를 eval 셋에 축적 → Flywheel 첫 발판**".
- **§5.4** — "도입도 loop 방식으로: **파일럿 1개(예: BIOP02 Critic 3개 항목만 Inspect로)**
  → 메트릭 통과 확인 → 확장." This directory is exactly that pilot, no wider.
- **§6 Step 2** — "실패 코퍼스 축적". `cases/regression_corpus/` is the BIOP02 seed.

§5.4 also draws the line this pilot respects: tools **execute and score** gates;
**where a gate goes and why stays hand-built**. Every threshold here is quoted from
`checklist_v1.md` — none was chosen by this eval, per the CLAUDE.md prohibition on
*"Critic agent setting its own thresholds / controls (anti-self-reference)"*.

---

## Which 3 items, and why

| Item | Scorer | Why it was picked |
|---|---|---|
| **#6 DRP framing** | `drp_framing` | The checklist already specifies it *as a grep*. Exact answer, zero judgement. |
| **#7 Claim-level** | `claim_level` | Field presence (`claim_level`, `critic_status`, all 7 `checks`) + the rollup rule are pure schema/logic. |
| **#2 Baseline comparison** | `baseline_comparison` | A numeric margin (+0.03 / +0.01) against 3 named baselines. Reads the real `*_baselines/trivial_baselines.json` layout. |

The remaining four need judgement or data this eval cannot see: #1 needs the split
manifest, #3 needs a retrain, #4/#5 need domain review (and are assigned to
sjpark/jhans by the checklist). They are deliberately **not** in the pilot.

**No LLM is involved in any verdict.** All three checks have exact answers, so an
LLM judge would only add nondeterminism. The eval runs against `mockllm/model`;
the run log confirms `mockllm: 0/20` calls — the model is never invoked.

---

## Running it

```bash
cd evals/critic_pilot

# 1. deterministic scorers + confusion matrix + coverage table
/opt/envs/spatialpatho/bin/python run_pilot.py

# 2. the Inspect eval suite (4 tasks)
/opt/envs/spatialpatho/bin/inspect eval critic_pilot.py --model mockllm/model --log-dir ./logs/inspect

# 3. mutation test — proves the cases actually constrain the scorers
/opt/envs/spatialpatho/bin/python mutation_check.py

# 4. run the scorers against REAL experiments/ artifacts (read-only)
/opt/envs/spatialpatho/bin/python run_real_artifacts.py

# regenerate fixtures after editing build_cases.py
/opt/envs/spatialpatho/bin/python build_cases.py
```

`inspect_ai` **0.3.247 is installed** in `/opt/envs/spatialpatho` — no fallback runner
was needed. `run_pilot.py` is *not* a fallback: it shares `scorers.py` with the Inspect
tasks and exists to print the confusion matrix and coverage table, which an accuracy
score alone does not show.

> ⚠️ **Shared-env side effect — read before touching `/opt/envs/spatialpatho`.**
> Installing `inspect-ai` **mutated the shared BIOP02 GPU env**. It downgraded
> **`fsspec` 2026.4.0 → 2025.9.0** and pulled in boto3/botocore/fastapi/pydantic/
> starlette/textual/uvicorn/tiktoken.
> Verified afterwards: `import torch` → **2.6.0+cu124** and `import openslide` both OK,
> so the core embedding stack still imports. **Not** regression-tested against an actual
> tiling/embedding/MIL run. If that env misbehaves, suspect this first.

---

## Case layers

Two layers, because they answer different questions.

### A. `cases/scorer_validation/` — 19 cases · does the scorer work?

Crafted PASS/FAIL pairs. Each case declares an expected verdict for **all three**
scorers, so cross-talk is measured too (a DRP violation must *not* make the
baseline scorer fire). Includes **negative controls** that must pass everything —
without them, a scorer hardcoded to `reject` would score perfectly. Three of the
controls (`control_real_0*`) are shapes copied verbatim from real artifacts, each
pinning a bug that real data exposed (see [Validation against real artifacts](#validation-against-real-artifacts-the-part-fixtures-cannot-do)).

Across both layers, **20 of the 22** case reports validate against
`schemas/critic_report.schema.json`; the other 2 violate it *by design* (that is their
defect). The fixtures are therefore realistic artifacts, not shapes convenient to the scorer.

### B. `cases/regression_corpus/` — 6 cases · what does the pilot miss?

The real 2026-07-17 incidents. **Reading this layer's Inspect accuracy as "failures
caught" is wrong** — see the honest result below.

---

## Result (measured 2026-07-17, logs in `logs/`)

| Run | Result |
|---|---|
| `run_pilot.py` | **66/66** scorer outputs matched expectation (Layer A 57/57, Layer B 9/9) |
| `inspect eval` × 4 tasks | accuracy **1.000** on all four (22/22, 22/22, 22/22, 9/9) |
| `mutation_check.py` | **9/9 mutants killed** — every scorer is genuinely constrained |
| `run_real_artifacts.py` | **12/12** real reports scored, **0 crashes** |
| fixture schema check | 20 conform, 2 violate by design |

Per-scorer confusion (Layer A): `drp_framing` 19/19 (4 must-fire, 15 must-stay-silent),
`claim_level` 19/19 (5 / 14), `baseline_comparison` 19/19 (7 / 12).

A green run means nothing on its own, so two things establish that this eval has teeth:
the **mutation test** (a stub scorer that always returns one verdict is killed by every
case set) and the **real-artifact run** (below). Running it found **six** real defects
that a "code looks right" review would have passed:

1. **Scorer bug.** `claim_level` matched the word *"proves"* inside `_case_meta.intent`
   — the fixture's own description of the defect. `load_report()` now strips
   `_case_meta` (it violates the schema's `additionalProperties: false` anyway).
2. **Fixture bug.** RC-04's metrics accidentally had an overlapping bootstrap CI, so
   `baseline_comparison` returned `caution` for a reason unrelated to the cohort-size
   defect it isolates. The scorer was right; the fixture was wrong.
3–6. **Four contract bugs found only against real artifacts** — see the section below.

### The honest headline: **the 3 pilot scorers catch 0 of the 6 real failures.**

This is the pilot's actual finding, not a defect in it. The 6 seed failures and the
3 most-mechanizable checklist items are near-disjoint sets:

| # | Real failure (2026-07-17) | Classification | Caught? |
|---|---|---|---|
| RC-01 | `csv.writer` `\r\n` → filename with `\r` → openslide "Unsupported or missing image file" | **out of eval scope** — pipeline | n/a, no artifact |
| RC-02 | `local coh="$1" man="...${coh}..."` self-reference → `set -u` unbound → embedding dies **silently after a successful download** | **out of eval scope** — pipeline | n/a, no artifact |
| RC-03 | conda absent from detached-shell PATH → embedding fails (fix: absolute `/opt/envs/spatialpatho/bin/python`) | **out of eval scope** — env | n/a, no artifact |
| RC-04 | n=187 vs n=85 — Yale cohort size misreported | doc/claim, **uncovered** | **NO** |
| RC-05 | 5 citation errors — nonexistent "Williams 2022" whose DOI resolves to Koudijs 2023 (*opposite* conclusion); Sharifi-Noghabi year wrong | doc/claim, **uncovered** | **NO** |
| RC-06 | "523 slides" vs "523 cases" — unit confusion | doc/claim, **uncovered** | **NO** |

**RC-01–03 are out of eval scope, permanently.** They occur upstream of any experiment
being *reported*. The Critic checklist reviews a `critic_report.json`; there is no
artifact at the moment a shell variable is unbound. These belong in a **pipeline smoke
test**, and each corpus record carries a `proposed_guard` naming the concrete assertion
(e.g. RC-01: assert no manifest filename matches `[\r\n]`). That suite does not exist yet.

**RC-04–06 are Critic-shaped but no 7-point item covers them.** Not #2/#6/#7, and not
the other four either — the checklist has no numeric-consistency, citation-verification,
or unit-consistency item at all. RC-05 is the sharpest: #5 requires a source be *named*,
never that it *exists* or *says what is claimed*, so a fabricated citation with a
real-looking DOI passes all seven items today.

Each corpus record names the scorer it needs (`_case_meta.needs_scorer`):

| Proposed | Closes | Note |
|---|---|---|
| **#8 numeric consistency** | RC-04 | every number in prose must resolve against `metrics.json` |
| **#9 citation verification** | RC-05 | resolve each DOI, match author/year/title, check the cited work isn't contradictory. Overlaps `literature-scout` / PaperQA2 (memo §5.1) |
| **#10 unit consistency** | RC-06 | every count needs an explicit unit matching manifest granularity (slide vs case vs tile vs patient) |

Treat this gap table as the deliverable. Per §5.4 the pilot's job was to prove the
mechanism on 3 items and then say what expansion is worth — this is that answer,
grounded in real incidents rather than guessed.

---

## Validation against real artifacts (the part fixtures cannot do)

The fixtures in `cases/` were authored by the same person who wrote the scorers, so
they prove the *logic* but not the **input contract**. `run_real_artifacts.py` runs the
three scorers over all **12 real `experiments/**/critic_report.json`** files, read-only.
It found four things no fixture could, three of them genuine scorer bugs:

1. **The `baselines` contract was invented.** The scorer expected a `baselines` dict
   inside `metrics.json`. Reality: `metrics.json` has **no `baselines` key at all**
   (consistent with the CLAUDE.md metrics spec) — trivial baselines are a *separate run*
   at `experiments/<user>/<exp>_baselines/trivial_baselines.json`, where `baselines` is a
   **list** of `{"baseline": name, "auc": ...}`. The scorer would have rejected every real
   experiment. Both layouts are now read.
2. **CI field name.** Real metrics use **`auc_ci_95`**; the scorer looked for `auc_ci95`
   and would have silently reported "no CI" on every real experiment. Both accepted.
3. **False positives at 25%.** `drp_framing` rejected **3 of 12** real reports because the
   reviewer, attesting to #6, *quotes the banned phrases to record their absence*:
   > `"금지 표현('drug response prediction', 'personalized therapy', 'patient-specific treatment') 미발견"`
   
   A check's own `evidence`/`notes` is meta-commentary about the check, not a claim of the
   experiment, so that subtree is now exempt (`SELF_REFERENCE_EXEMPT`). **Trade-off:** a
   real violation hidden in `checks.drp_framing.notes` is now missed. Accepted — a 25% FP
   rate makes a scorer unusable, and the loophole needs a reviewer to write a violation into
   the very field attesting there is none.
4. **A crash.** `experiments/crosscancer` sets `metrics_path` to a **`.md` scoreboard**;
   `json.load` raised `JSONDecodeError` and killed the loader. Now degrades to a #2 reject.

All three real shapes are pinned as `cases/scorer_validation/control_real_0*` so they
cannot regress. Result after the fixes: **12/12 real reports scored, 0 crashes, 0 known
false positives.**

### Two open questions for braveji (Critic owner) — NOT decided here

CLAUDE.md forbids *"Critic agent setting its own thresholds / controls"*, so the pilot
surfaces these rather than resolving them:

- **#2 `pixel_mean` baseline — 범위 정정 (kkkim 실물 확인 2026-07-17).**
  ⚠️ 이 파일럿의 원래 결론("pixel_mean이 BIOP02에 **nowhere**")은 **틀렸다.** 실제로는:
  - **Paper C(cross-cancer)는 돌렸다** — `experiments/crosscancer/sh_baselines.py`(BLOCKER-3
    remediation) → 4개 암종 `<cancer>/full/baseline_pixelmean.json`에 실측값 존재.
    스코어러가 이 파일을 안 봐서 놓쳤다(스코어러 범위 버그).
  - **Paper A(BRCA/sjpark)는 진짜 없다** — 10개 baseline 런이 전부
    `{random, majority|subtype_only, mean_embed}`. `pixel_mean` 부재.
  - `mean_embed`를 대체로 인정하지 않는 스코어러 판단은 **맞다**(UNI 임베딩 평균 ≠ 원본 픽셀 평균).

  → 남는 진짜 이슈는 **Paper A에 pixel-mean이 없다**는 것. 돌리거나 checklist #2를 개정하거나.
  **사람이 정한다**(braveji owns).

- **★ 이 파일럿이 실제로 캐낸 것 — Paper C HPV CONFIRM이 trivial baseline과 구분되지 않는다.**
  위 정정 과정에서 kkkim이 대조한 실측:

  | HNSC `hpv_pos` | AUROC | CI95 |
  |---|---|---|
  | 헤드라인 MIL/UNI (`mil_cost_results.json`) | **0.9594** | **없음** |
  | trivial pixel-mean (`baseline_pixelmean.json`) | 0.9224 | [0.8536, **0.9745**] |

  **pixel-mean의 CI가 헤드라인 0.9594를 포함한다** → 파운데이션 모델 MIL이 "슬라이드 픽셀 평균"을
  **유의하게 상회한다고 말할 수 없다**. 게다가 헤드라인엔 **CI가 아예 없다**.
  - 이건 kkkim의 Paper A peer review 소견(**CLAM vs mean_embed CI 전부 중첩**)과 **같은 패턴**이
    Paper C에서도 나온 것 → 두 트랙 공통 이슈.
  - **단, 법칙이 깨진 건 아니다.** 사전등록 기준은 "HPV held-out AUROC **≥ 0.80** → 대체가능"이고
    pixel-mean(0.9224)도 이를 통과한다. 법칙의 주장은 "H&E가 분자검사를 대신할 수 있나"지
    "우리 FM이 픽셀평균을 이기나"가 아니다. 오히려 **더 싸게도 된다**는 방향(모델 비의존성과 정합).
  - **하지만 원고에서 이 대조를 숨기면 안 된다.** 리뷰어가 반드시 묻는다: *"UNI가 왜 필요한가?"*
  - **결론 없음 — braveji(Critic 총괄) 판정 대상.** 이 파일럿은 제기만 한다(anti-self-reference).
- **#6's allowed-task list is Paper A-only.** It permits `{er_status, pr_status,
  her2_status, pam50}`, which predates Paper C. `experiments/crosscancer` (task:
  *"morphological-correlate substitutability law — sealed held-out test"*) is therefore
  flagged. This is a **true** flag of a checklist gap, not a scorer bug — checklist_v1.md
  has not caught up with the cross-cancer scope.

---

## Scope limits

- **3 of 7 items.** A green run here is **not** `critic_status: pass`. The full 7-point
  review by a human reviewer (Owner ≠ Reviewer) is unchanged and still required.
- **0 of 6 real failures caught.** The pilot validates a *mechanism*, not coverage.
- **Scorer verdicts are not `critic_status`.** `run_real_artifacts.py` is read-only and
  advisory. It writes nothing and adjudicates nothing; a human reviewer owns the verdict
  (Owner ≠ Reviewer).
- **#2 rejects every real experiment today** on the missing `pixel_mean` baseline. Until
  that open question is settled the item is not usable as a gate — only as a flag.
- **Not in CI.** No GitHub Actions hook (memo §5.5 proposes one). Nothing fails a build today.
- **Text scanners are regex.** `drp_framing` and the overclaim patterns catch the listed
  phrasings; a paraphrase ("we forecast which agent each patient should receive") slips
  through. Widening the pattern list is cheap; making it robust needs an LLM judge, which
  reintroduces nondeterminism. Deliberate trade-off, revisit at expansion.
- **English + Korean only**, matching the phrasings in checklist #6 and CLAUDE.md.

## Next steps

1. **braveji to settle the two open questions above** (pixel_mean; Paper C task names).
   #2 cannot gate anything until the first is resolved.
2. Build the **pipeline smoke suite** for RC-01–03 (`proposed_guard` in each record).
   Cheap, and it closes 3 of 6 corpus cases that this eval never will.
3. Decide with braveji (Critic owner) whether #8/#9/#10 become real checklist items.
   They are what the real corpus demands — but the checklist is braveji's to own,
   and this eval must not set its own controls.
4. Only then consider CI wiring (§5.5) and expanding past 3 items.

## Files

| Path | Role |
|---|---|
| `scorers.py` | the 3 deterministic checks. Pure python, no `inspect_ai` import — single source of truth |
| `critic_pilot.py` | Inspect `@task`/`@solver`/`@scorer` wrappers (4 tasks) |
| `run_pilot.py` | standalone runner: confusion matrix, coverage table, schema validation |
| `run_real_artifacts.py` | runs the scorers over the 12 real `experiments/**/critic_report.json` (read-only) |
| `build_cases.py` | regenerates all fixtures |
| `mutation_check.py` | proves the case set constrains the scorers |
| `cases/scorer_validation/` | 19 cases: crafted PASS/FAIL pairs + 3 pinned real-artifact shapes |
| `cases/regression_corpus/` | the 6 real 2026-07-17 failures |
| `logs/` | run output from 2026-07-17 |

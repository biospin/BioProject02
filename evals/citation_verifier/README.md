# BIOP02 citation verifier — eval

Our own citation checker, built because the public medsci `verify-refs` skill catches
**1 of our 5 real citation errors** (see `docs/HARNESS_REVIEW_2026-07-17.md` §4.3.1).
Goal, per Leader: *"나머지 4개도 도구로 잡게."* — get all 5 caught by machine, so the
conclusion isn't "a human has to look at it."

Tool: `agents/critic/scripts/verify_citations.py` (stdlib only — `habanero` is not
installed in this env; see memory `infra_citation_verification`).

## Run

```bash
cd evals/citation_verifier
python3 run_cases.py              # uses cache.json
python3 run_cases.py --refresh    # ignore cache, hit live CrossRef/PubMed
python3 run_cases.py --verbose    # show why each verdict fired
python3 mutation_check.py         # prove the cases constrain the checks
```

## Results (live run, 2026-07-17)

**12/12 cases correct. False positives: 0/5 controls. All 8 mutants killed.**

| case | expected | actual | |
|---|---|---|---|
| ctrl_farahmand | VERIFIED | VERIFIED | ✅ |
| ctrl_koudijs | VERIFIED | VERIFIED | ✅ |
| ctrl_kaczmarzyk | VERIFIED | VERIFIED | ✅ |
| ctrl_claim_supported | VERIFIED | VERIFIED | ✅ |
| ctrl_pubmed_fallback | VERIFIED | VERIFIED | ✅ pins PubMed efetch |
| **err1_williams_fabricated** | NOT_FOUND | **NOT_FOUND** | ✅ medsci missed |
| **err2_sharifi_year** | YEAR_MISMATCH | **YEAR_MISMATCH** | ✅ medsci missed |
| **err3_path2space_author** | AUTHOR_MISMATCH | **AUTHOR_MISMATCH** | ✅ medsci caught too |
| **err4_spearman_claim** | CLAIM_UNSUPPORTED | **CLAIM_UNSUPPORTED** | ✅ out of medsci scope |
| **err5_mako_scope** | CLAIM_UNSUPPORTED | **CLAIM_UNSUPPORTED** | ✅ out of medsci scope |
| reg_fake_doi | NOT_FOUND | NOT_FOUND | ✅ medsci **passed** this |
| edge_koudijs_epub_year | NEEDS_HUMAN | NEEDS_HUMAN | ✅ |

**5/5 of our real errors are now caught by machine** (medsci caught 1/5).

Each fires for the *right* reason, not by luck (`--verbose`) — this matters, because
§4.3.1 records kkkim reporting a year catch that was really an author-count artifact:

* err1 — `claimed first author 'Williams' not found among top-5 search results`
* err2 — `year cited=2024 source=2021 (diff=3)`
* err3 — `first_author cited=Kaminski source=Shulman`
* err4 — `claimed_metric_absent_from_abstract: ['spearman']` — note the real reason: that
  abstract contains **no numbers at all and neither "Spearman" nor "Pearson"**. The catch
  rests on "the abstract offers no support", not on a Spearman-vs-Pearson contrast (the
  Pearson values are in the body). Verified against the fetched text.
* err5 — `scope_terms_absent_from_abstract: ['subtype']` + `abstract_instead_centres_on: ['recurrence risk', 'ROR-P']`

## Verdicts

| verdict | meaning |
|---|---|
| `VERIFIED` | DOI resolved **and** first author matches **and** year matches (**and** claims supported, if any) |
| `AUTHOR_MISMATCH` | cited first author ≠ source first author |
| `YEAR_MISMATCH` | year differs by ≥ 2 |
| `NOT_FOUND` | **fabrication suspected**: no DOI / DOI didn't resolve, and the claimed first author is absent from the top-5 search |
| `CLAIM_UNSUPPORTED` | the abstract does not support the attached claim |
| `NEEDS_HUMAN` | undecidable — surfaced explicitly, never a silent pass |

**A lookup failure is never a pass.** DOI 404, zero search hits, or zero source authors
cannot produce `VERIFIED`. This is the whole point: medsci's `verify_refs.py` L557-560
falls back to a weak PubMed title search on DOI failure and returns `OK` for any hit, so
a fabricated DOI passes *more easily* than no DOI. Enforced by the `doi_fail_passes`
mutant and the `reg_fake_doi` case.

## Year tolerance: ±1 → `NEEDS_HUMAN`

Epub-ahead-of-print and issue years legitimately differ by one. We hit this ourselves:
we cite **Koudijs 2023**; CrossRef `issued` says **2022** (`10.1093/bib/bbac490`). Same
for Farahmand — DOI slug says 2021, `issued` says 2022. Calling those errors would mean
false positives on real citations; calling them fine would mean no year check at all.

So: **diff 0 → pass · diff 1 → `NEEDS_HUMAN` · diff ≥ 2 → `YEAR_MISMATCH`.**
Our real error #2 (Sharifi-Noghabi cited 2024, actual 2021) is off by **3** — comfortably
past the band. The tolerance does not cost us the catch.

The controls are pinned at the CrossRef `issued` year (diff 0) and the ±1 behaviour is
demonstrated by a **separate** case (`edge_koudijs_epub_year`). Deliberate: if a control
sat in the tolerance band we'd be tempted to loosen the year rule, which would then miss
err2.

## Input format

JSON. One entry per citation; `claims` optional.

```json
{
  "id": "err5_mako_scope",
  "doi": "10.1038/s41746-025-02334-2",
  "first_author": "Kaczmarzyk",
  "year": 2026,
  "title": "Towards interpretable prediction of recurrence risk ...",
  "claims": [
    {
      "text": "MAKO is a benchmark for predicting molecular subtype from H&E",
      "scope_terms": ["subtype"],
      "contradicting_terms": ["recurrence risk", "ROR-P"]
    }
  ]
}
```

Numbers and metric names are auto-extracted from `claims[].text`. `scope_terms` are the
keywords **we asserted** — the tool cannot know what we claimed unless we say so.

## Cache

`cache.json` stores **raw API responses only** (404s included, as `{"__error__": 404}`),
never verdicts. Verdicts are recomputed from the payload every run — a cache hit replays
what the API said, it is **not** a stored pass.

## Mutants (all killed)

| mutant | killed by | why it exists |
|---|---|---|
| `always_verified` | err1, err2, err3… | the "silent OK" failure mode — **the medsci regression guard** |
| `always_notfound` | the 5 controls | false-positive guard |
| `always_needs_human` | the controls | must actually decide |
| `no_year_check` | err2, edge_koudijs | medsci replica: parses year, never compares it |
| `doi_fail_passes` | err1, reg_fake_doi | medsci replica: L557-560 fake-DOI pass |
| `ignore_claims` | err4, err5 | proves the abstract layer is load-bearing |
| `always_claim_unsupported` | ctrl_claim_supported | proves the claim layer *discriminates* |
| `break_pubmed_fallback` | ctrl_pubmed_fallback | proves the efetch fallback is live code |

## Limitations — read before trusting a verdict

1. **`CLAIM_UNSUPPORTED` means "not supported *by the abstract*", NOT "false."** We only
   fetch abstracts. A number that legitimately lives in the paper body is invisible to
   this tool and **will** be flagged. This is real, not hypothetical: the true values
   behind err4 (Pearson 0.4±0.21, 0.26±0.16) are in the bbab294 *body* — its abstract
   contains no numbers at all. The verdict there is right for our case (we cited them as
   "Spearman", and the abstract doesn't support the claim either way), but the same rule
   would flag a correctly body-sourced number. **Treat `CLAIM_UNSUPPORTED` as "escalate
   and point at the exact source line", not "the citation is wrong."**
2. **`NOT_FOUND` depends on CrossRef search ranking**, which is network- and time-
   dependent. The top-5 for a fabricated title could shift. Not deterministic across
   runs the way `evals/critic_pilot` is — re-run with `--refresh` before acting. The two
   fabrication cases therefore assert the guarantee that actually matters (`accept:
   [NOT_FOUND, NEEDS_HUMAN]` = **never VERIFIED**) rather than one exact label.
3. **First author only.** Middle/last authors, journal, volume, and pages are not
   checked. An error in those passes silently.
4. **`scope_terms` are human-supplied.** The tool can't detect a scope error we don't
   declare. err5 is caught only because we told it we claimed "subtype". This layer
   assists review; it does not replace reading.
5. **CrossRef/PubMed coverage only.** Preprints, books, and software citations outside
   CrossRef resolve poorly and land in `NOT_FOUND`/`NEEDS_HUMAN`.
6. **Abstract coverage is uneven.** CrossRef returns no abstract for Cell or Modern
   Pathology; we fall back to PubMed efetch. Where neither has one → `NEEDS_HUMAN`.
7. **No rate limiting.** Fine for tens of citations; add a delay for a full bibliography.
8. **Input is pre-structured JSON, not raw prose.** Extracting `{doi, first_author, year,
   claims}` out of our markdown is still a human/Critic step — this tool verifies an
   already-parsed citation. "우리 문서에 적용 가능" means the format is cheap to fill in
   by hand, not that the docs are scanned automatically.

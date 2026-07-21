"""Generates the case fixtures under cases/. Re-runnable; overwrites.

Two layers (see README §Case layers):
  A. cases/scorer_validation/  — crafted PASS/FAIL pairs that prove each scorer
     both fires and stays silent. This is what validates the pilot.
  B. cases/regression_corpus/  — the 6 real 2026-07-17 failures, encoded to
     measure *current coverage* (most are expected MISSES; that is the finding).
"""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).parent
SV = ROOT / "cases" / "scorer_validation"
RC = ROOT / "cases" / "regression_corpus"


def base_report() -> dict:
    return {
        "schema_version": "0.1",
        "created_at": "2026-07-17T10:00:00+09:00",
        "reviewer": "kkkim",
        "owner": "sjpark",
        "experiment": {
            "experiment_id": "sjpark/20260717_er_mlp_uni",
            "task": "er_status",
            "endpoint": "ER IHC status (binary)",
            "commit_hash": "a1b2c3d4e5f",
            "config_path": "config.yaml",
            "metrics_path": "metrics.json",
            "predictions_path": "predictions.npy",
        },
        "checks": {
            "data_leakage": {"status": "pass", "evidence": ["patient overlap == 0", "site probe AUC 0.58"], "notes": "case_id-disjoint split per split_policy_v0."},
            "baseline_comparison": {"status": "pass", "evidence": ["metrics.json baselines"], "notes": "All three trivial baselines cleared by >0.03 AUC."},
            "counterfactual_check": {"status": "pass", "evidence": ["label shuffle AUC 0.51"], "notes": "Attention top-10% masking drops AUC by 0.09."},
            "cross_dataset_check": {"status": "not_applicable", "evidence": [], "notes": "Paper A phenotype stage; DepMap/GDSC transfer not in scope."},
            "biological_plausibility": {"status": "pass", "evidence": ["OncoKB ER pathway"], "notes": "Top attention tiles enriched for tubule formation, consistent with ER+ morphology."},
            "drp_framing": {"status": "pass", "evidence": ["grep 0 hits"], "notes": "No prohibited framing; task is er_status."},
            "claim_level": {"status": "pass", "evidence": ["claim_level field"], "notes": "Findings stated as hypothesis generation only."},
        },
        "critic_status": "pass",
        "claim_level": "hypothesis_only",
        "summary": "ER status classification from UNI embeddings suggests morphology carries ER-correlated signal on TCGA-BRCA. Single-cohort result; external validation pending.",
    }


def base_metrics() -> dict:
    return {
        "auc": 0.842,
        "auprc": 0.881,
        "auc_ci95": [0.801, 0.879],
        "balanced_accuracy": 0.771,
        "n_train": 707,
        "n_val": 151,
        "model": "mlp",
        "embedding_model": "uni_v1",
        "commit_hash": "a1b2c3d4e5f",
        "baselines": {
            "random": {"auc": 0.502, "auprc": 0.712, "auc_ci95": [0.451, 0.553]},
            "subtype_only": {"auc": 0.744, "auprc": 0.803, "auc_ci95": [0.699, 0.789]},
            "pixel_mean": {"auc": 0.571, "auprc": 0.742, "auc_ci95": [0.522, 0.620]},
        },
    }


def write(dirpath: Path, name: str, report: dict, metrics: dict | None, meta: dict) -> None:
    dirpath.mkdir(parents=True, exist_ok=True)
    report["_case_meta"] = meta
    with open(dirpath / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    if metrics is not None:
        with open(dirpath / f"{name}.metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # point the report at its own sidecar. Skipped when metrics is None so
        # that cases pinning a real metrics_path (e.g. a .md) keep it verbatim.
        report["experiment"]["metrics_path"] = f"{name}.metrics.json"
    with open(dirpath / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")


ALL_PASS = {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "pass"}


def build_scorer_validation() -> None:
    # ---------------- negative controls (must PASS all three) -------------
    r = base_report()
    write(SV, "control_clean_01", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "negative_control",
        "intent": "Fully compliant report. Guards against a scorer that always rejects.",
        "expected": dict(ALL_PASS)})

    r = base_report()
    r["experiment"]["task"] = "pam50"
    r["experiment"]["endpoint"] = "PAM50 subtype (multiclass, one-vs-rest ER-proxy)"
    r["checks"]["cross_dataset_check"]["status"] = "not_applicable"
    r["summary"] = ("PAM50 subtype signal is suggested by H&E morphology on TCGA-BRCA. "
                    "Results are hypothesis-generating and are not evidence of clinical utility.")
    write(SV, "control_clean_02", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "negative_control",
        "intent": "Second clean report, different task, cautious wording.",
        "expected": dict(ALL_PASS)})

    # a legitimately 'caution' report — rollup must be accepted, not flagged
    r = base_report()
    m = base_metrics()
    m["auc"] = 0.762
    m["auc_ci95"] = [0.721, 0.801]
    r["checks"]["baseline_comparison"] = {
        "status": "caution", "evidence": ["metrics.json baselines"],
        "notes": "Margin over subtype-only is +0.018, inside the caution band; CI overlaps."}
    r["critic_status"] = "caution"
    r["required_followups"] = ["Increase n or report bootstrap CI separation vs subtype-only."]
    write(SV, "control_clean_03_caution", r, m, {
        "layer": "scorer_validation", "kind": "negative_control",
        "intent": "Honest caution report: rollup consistent. claim_level scorer must not reject it; "
                  "baseline scorer must independently return caution.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "caution"}})

    # ---- negative controls derived from REAL artifact shapes -------------
    # Each of these three shapes was found by run_real_artifacts.py on
    # 2026-07-17 and each was a genuine scorer bug. They are pinned here so a
    # future edit cannot silently reintroduce them.

    r = base_report()
    r["checks"]["drp_framing"]["evidence"] = [
        "grep of sjpark artifacts/configs/scripts: no 'drug response / personalized "
        "therapy / optimal treatment / patient-specific / pembrolizumab'.",
        "metrics.json 및 config.yaml에서 금지 표현('drug response prediction', "
        "'personalized therapy', 'patient-specific treatment') 미발견",
    ]
    write(SV, "control_real_01_evidence_quotes_ban", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "negative_control",
        "intent": "VERBATIM from experiments/sjpark/er_status_uni_v1 + kkkim/20260703_critic_biop02-53. "
                  "A reviewer attesting to #6 must quote the banned phrases to record their absence. "
                  "Scanning that subtree false-positived 3 of 12 real reports (25%).",
        "expected": dict(ALL_PASS)})

    r = base_report()
    r["experiment"]["task"] = "molecular_phenotype_mil (er/pr/her2_status)"
    write(SV, "control_real_02_composite_task", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "negative_control",
        "intent": "VERBATIM from experiments/kkkim/20260703_critic_biop02-53. Real task fields are "
                  "composite descriptors, not the bare tokens checklist #6 lists. Equality matching "
                  "rejected a legitimate MIL experiment on naming style alone.",
        "expected": dict(ALL_PASS)})

    r = base_report()
    r["experiment"]["metrics_path"] = "experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md"
    write(SV, "control_real_03_metrics_not_json", r, None, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "VERBATIM from experiments/crosscancer. metrics_path points at a .md scoreboard; "
                  "json.load raised JSONDecodeError and crashed the loader. Must degrade to a "
                  "reject on #2 (no numbers resolvable), not crash.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "reject"}})

    # ---------------- #6 DRP framing ------------------------------------
    r = base_report()
    r["summary"] = ("Our drug response prediction model achieves AUC 0.84 and can be used for "
                    "patient-specific selection of treatment.")
    r["checks"]["drp_framing"]["notes"] = "No issues found."
    write(SV, "drp_fail_01_english", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "drp_framing",
        "intent": "Prohibited English DRP framing in summary (checklist #6 grep list).",
        "expected": {"drp_framing": "reject", "claim_level": "pass", "baseline_comparison": "pass"}})

    r = base_report()
    r["checks"]["biological_plausibility"]["notes"] = (
        "상위 연결은 환자 맞춤 최적 치료 후보를 제시한다.")
    write(SV, "drp_fail_02_korean", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "drp_framing",
        "intent": "Prohibited Korean DRP framing ('환자 맞춤', '최적 치료') buried in a nested check note. "
                  "Also proves the scorer walks the whole document, not just summary.",
        "expected": {"drp_framing": "reject", "claim_level": "pass", "baseline_comparison": "pass"}})

    r = base_report()
    r["experiment"]["task"] = "drug_sensitivity"
    r["experiment"]["endpoint"] = "PRISM sensitivity score"
    write(SV, "drp_fail_03_task_field", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "drp_framing",
        "intent": "task field outside {er_status,pr_status,her2_status,pam50} (checklist #6 bullet 2).",
        "expected": {"drp_framing": "reject", "claim_level": "pass", "baseline_comparison": "pass"}})

    # ---------------- #7 claim level ------------------------------------
    r = base_report()
    del r["claim_level"]
    write(SV, "claim_fail_01_missing_field", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "claim_level",
        "intent": "Required 'claim_level' field absent (schema + checklist #7).",
        "expected": {"drp_framing": "reject", "claim_level": "reject", "baseline_comparison": "pass"}})

    r = base_report()
    r["summary"] = ("The model predicts clinical outcome for ER+ patients and is clinically actionable "
                    "on external cohorts.")
    write(SV, "claim_fail_02_overclaim", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "claim_level",
        "intent": "'predicts clinical outcome' / 'clinically actionable' — checklist #7 reject row.",
        "expected": {"drp_framing": "pass", "claim_level": "reject", "baseline_comparison": "pass"}})

    r = base_report()
    r["checks"]["data_leakage"]["status"] = "reject"
    r["checks"]["data_leakage"]["notes"] = "patient overlap = 14 cases between train and test."
    r["critic_status"] = "pass"
    write(SV, "claim_fail_03_rollup_inconsistent", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "claim_level",
        "intent": "critic_status='pass' while a check is 'reject' — violates checklist_v1.md 최종 판정 규칙. "
                  "This is the field-consistency half of #7.",
        "expected": {"drp_framing": "pass", "claim_level": "reject", "baseline_comparison": "pass"}})

    r = base_report()
    del r["checks"]["counterfactual_check"]
    write(SV, "claim_fail_04_missing_check", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "claim_level",
        "intent": "checks/ missing a required 7-point item.",
        "expected": {"drp_framing": "pass", "claim_level": "reject", "baseline_comparison": "pass"}})

    r = base_report()
    r["summary"] = ("The result proves that H&E morphology carries ER signal and generalizes to all "
                    "breast cancer cohorts.")
    write(SV, "claim_caution_01_overreach", r, base_metrics(), {
        "layer": "scorer_validation", "kind": "positive_case", "target": "claim_level",
        "intent": "'proves' / 'generalizes to all' — checklist #7 caution row (표현 과장, 데이터 범위 내).",
        "expected": {"drp_framing": "pass", "claim_level": "caution", "baseline_comparison": "pass"}})

    # ---------------- #2 baseline comparison ----------------------------
    m = base_metrics()
    del m["baselines"]["pixel_mean"]
    r = base_report()
    write(SV, "baseline_fail_01_missing_baseline", r, m, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "pixel-mean baseline absent — checklist #2 'baseline 수치 누락 -> reject'.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "reject"}})

    m = base_metrics()
    m["auc"] = 0.748
    m["auc_ci95"] = [0.705, 0.788]
    r = base_report()
    write(SV, "baseline_fail_02_below_margin", r, m, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "model auc 0.748 vs subtype_only 0.744 = +0.004 < 0.01 -> baseline 미달 reject.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "reject"}})

    m = base_metrics()
    m["auprc"] = 0.781
    r = base_report()
    write(SV, "baseline_fail_03_auprc_below_subtype", r, m, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "AUC clears but AUPRC 0.781 < subtype_only 0.803 — checklist #2 AUPRC 요건.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "reject"}})

    m = base_metrics()
    m["auc"] = 0.764
    m["auc_ci95"] = [0.722, 0.804]
    r = base_report()
    write(SV, "baseline_caution_01_margin_band", r, m, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "margin +0.020 in the 0.01~0.03 caution band.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "caution"}})

    m = base_metrics()
    del m["auc_ci95"]
    r = base_report()
    write(SV, "baseline_caution_02_no_ci", r, m, {
        "layer": "scorer_validation", "kind": "positive_case", "target": "baseline_comparison",
        "intent": "Margin fine but bootstrap CI absent -> non-overlap unverifiable -> caution.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "caution"}})


# ==========================================================================
# Layer B — the 6 real 2026-07-17 failures
# ==========================================================================

def build_regression_corpus() -> None:
    # ---- Cases 1-3: pipeline/code failures. No critic_report artifact exists
    # for these, because they occur upstream of any experiment being reported.
    # Encoded as corpus records only; classified OUT OF EVAL SCOPE.
    pipeline = [
        {
            "case_id": "RC-01",
            "title": "csv.writer default \\r\\n -> filenames containing carriage return",
            "date": "2026-07-17",
            "real_incident": True,
            "layer": "regression_corpus",
            "classification": "out_of_eval_scope",
            "class_reason": (
                "Code/pipeline defect. Python csv.writer emits \\r\\n; bash `read` then yields a "
                "filename with a trailing \\r, and openslide fails with 'Unsupported or missing "
                "image file'. There is no critic_report artifact at this stage — the Critic "
                "checklist reviews reported experiment results, not shell I/O."
            ),
            "failure_mode": "silent_failure",
            "belongs_to": "pipeline smoke test (not Inspect Critic eval)",
            "proposed_guard": (
                "Smoke test: assert no filename in the manifest matches r'[\\r\\n]'; "
                "write CSVs with newline='' and/or strip \\r on read."
            ),
        },
        {
            "case_id": "RC-02",
            "title": "same-line self-reference under `set -u`: local coh=\"$1\" man=\"...${coh}...\"",
            "date": "2026-07-17",
            "real_incident": True,
            "layer": "regression_corpus",
            "classification": "out_of_eval_scope",
            "class_reason": (
                "Shell defect. `local a=... b=${a}` on one line does not see `a` yet; under set -u "
                "this raises 'coh: unbound variable'. Download succeeded, embedding died silently "
                "afterwards — only visible in logs. Not reviewable by a checklist scorer."
            ),
            "failure_mode": "silent_death_after_apparent_success",
            "belongs_to": "pipeline smoke test (not Inspect Critic eval)",
            "proposed_guard": (
                "Smoke test: run each stage script with `bash -n` + a 1-slide end-to-end run that "
                "asserts the embedding .npy exists and is non-empty; split multi-assign local lines."
            ),
        },
        {
            "case_id": "RC-03",
            "title": "conda not on PATH in a detached shell -> embedding step fails",
            "date": "2026-07-17",
            "real_incident": True,
            "layer": "regression_corpus",
            "classification": "out_of_eval_scope",
            "class_reason": (
                "Environment/infra defect. Detached (non-login) shells do not source conda init, so "
                "`conda activate` is unavailable. Resolution: absolute interpreter path "
                "/opt/envs/spatialpatho/bin/python. Nothing in the 7-point checklist covers env wiring."
            ),
            "failure_mode": "environment",
            "belongs_to": "pipeline smoke test (not Inspect Critic eval)",
            "proposed_guard": (
                "Smoke test: assert `/opt/envs/spatialpatho/bin/python -c 'import torch, openslide'` "
                "returns 0 from a detached shell; forbid bare `conda activate` in batch scripts."
            ),
        },
    ]
    RC.mkdir(parents=True, exist_ok=True)
    for rec in pipeline:
        with open(RC / f"{rec['case_id'].lower().replace('-', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # ---- Cases 4-6: document/claim failures. These DO produce a critic_report,
    # so we encode them as real artifacts and run all three scorers to measure
    # current coverage. Expectation: MISS (scorers return pass) — that is the
    # gap analysis this pilot delivers.

    # RC-04: Yale cohort size misreported (n=187 in prose, metrics say 85)
    r = base_report()
    r["experiment"]["experiment_id"] = "sjpark/20260717_er_mlp_yale_ext"
    r["experiment"]["endpoint"] = "ER IHC status (binary), Yale external cohort"
    r["summary"] = ("External evaluation on the Yale cohort (n=187) suggests the ER signal transfers "
                    "beyond TCGA-BRCA. Hypothesis-generating only.")
    r["checks"]["data_leakage"]["evidence"] = ["Yale n=187 held out entirely from training"]
    m = base_metrics()
    m["n_train"] = 0
    m["n_val"] = 85          # ground truth: the Yale cohort is 85, not 187
    m["auc"] = 0.812
    m["auc_ci95"] = [0.744, 0.871]
    # This fixture must isolate exactly ONE defect: the n=187/85 mismatch.
    # An external cohort has wider CIs and a weaker subtype-only baseline, so
    # #2 resolves cleanly to pass and the cohort-size miss is unambiguous.
    m["baselines"]["subtype_only"] = {"auc": 0.701, "auprc": 0.760, "auc_ci95": [0.620, 0.740]}
    m["baselines"]["random"] = {"auc": 0.502, "auprc": 0.690, "auc_ci95": [0.401, 0.603]}
    m["baselines"]["pixel_mean"] = {"auc": 0.564, "auprc": 0.712, "auc_ci95": [0.480, 0.660]}
    write(RC, "rc_04_cohort_size_mismatch", r, m, {
        "case_id": "RC-04",
        "title": "n=187 vs n=85 — Yale cohort size misreported",
        "date": "2026-07-17", "real_incident": True,
        "layer": "regression_corpus",
        "classification": "in_corpus_but_uncovered_by_pilot_scorers",
        "class_reason": (
            "Document/claim failure and genuinely Critic-shaped, but no 7-point item asserts that "
            "cohort sizes in prose match metrics.json. #2 checks baseline numbers, #6 checks framing, "
            "#7 checks claim level — none reads n. Prose says n=187; metrics.json says n_val=85."
        ),
        "needs_scorer": "numeric_consistency (proposed #8): every integer/float claimed in prose must "
                        "resolve against metrics.json; mismatch -> reject.",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "pass"},
        "expected_is_a_miss": True,
    })

    # RC-05: fabricated / mis-attributed citations
    r = base_report()
    r["experiment"]["experiment_id"] = "sjpark/20260717_er_mlp_uni"
    r["checks"]["biological_plausibility"]["evidence"] = [
        "Williams 2022, https://doi.org/10.1038/s41746-023-00891-y",
        "Sharifi-Noghabi 2018, MOLI: multi-omics late integration",
    ]
    r["checks"]["biological_plausibility"]["notes"] = (
        "Williams 2022 reports that H&E-derived features recapitulate ER status with high fidelity, "
        "supporting our morphology-first framing. Sharifi-Noghabi 2018 further supports late "
        "integration for phenotype transfer.")
    r["summary"] = ("ER status signal in H&E is consistent with prior reports (Williams 2022). "
                    "Hypothesis-generating only.")
    write(RC, "rc_05_citation_errors", r, base_metrics(), {
        "case_id": "RC-05",
        "title": "5 citation errors — nonexistent 'Williams 2022' whose link resolves to Koudijs 2023 "
                 "(opposite conclusion); Sharifi-Noghabi year wrong (2018 vs 2019)",
        "date": "2026-07-17", "real_incident": True,
        "layer": "regression_corpus",
        "classification": "in_corpus_but_uncovered_by_pilot_scorers",
        "class_reason": (
            "Document failure. The 7-point checklist requires a source be *named* (#5 'pathway-drug "
            "연결 출처 명시') but never verifies the source exists, is correctly attributed, or actually "
            "supports the claim. A fabricated citation with a real-looking DOI passes all 7 items."
        ),
        "needs_scorer": "citation_verification (proposed #9): resolve every DOI/URL, match "
                        "author+year+title against the resolved record, and check the cited work's "
                        "stated conclusion is not contradictory. Overlaps literature-scout / PaperQA2 "
                        "(harness memo §5.1).",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "pass"},
        "expected_is_a_miss": True,
    })

    # RC-06: unit confusion, slides vs cases
    r = base_report()
    r["summary"] = ("Trained on 523 slides from TCGA-BRCA; ER status signal is suggested by morphology. "
                    "Hypothesis-generating only.")
    r["checks"]["data_leakage"]["notes"] = (
        "Patient-disjoint split over 523 slides; train/val boundary verified by case_id.")
    m = base_metrics()
    m["n_train"] = 438       # ground truth: 523 is a CASE count, slides are ~1010
    m["n_val"] = 85
    m["unit"] = "case"
    write(RC, "rc_06_slides_vs_cases", r, m, {
        "case_id": "RC-06",
        "title": "'523 slides' vs '523 cases' — unit confusion",
        "date": "2026-07-17", "real_incident": True,
        "layer": "regression_corpus",
        "classification": "in_corpus_but_uncovered_by_pilot_scorers",
        "class_reason": (
            "Document failure. The count is right, the unit is wrong: 523 counts cases, while the "
            "DX-slide cohort is ~1010 slides. #1 (data leakage) cares that the split is case_id-"
            "disjoint but not that prose names the correct unit. None of #2/#6/#7 reads units."
        ),
        "needs_scorer": "unit_consistency (proposed #10): every count in prose must carry an explicit "
                        "unit that matches the metrics.json unit field / manifest granularity "
                        "(slide vs case vs tile vs patient).",
        "expected": {"drp_framing": "pass", "claim_level": "pass", "baseline_comparison": "pass"},
        "expected_is_a_miss": True,
    })


if __name__ == "__main__":
    build_scorer_validation()
    build_regression_corpus()
    n_sv = len(list(SV.glob("*.json"))) - len(list(SV.glob("*.metrics.json")))
    n_rc = len(list(RC.glob("*.json"))) - len(list(RC.glob("*.metrics.json")))
    print(f"scorer_validation cases: {n_sv}")
    print(f"regression_corpus cases: {n_rc}")

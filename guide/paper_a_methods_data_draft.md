# Paper A — Methods (데이터 절) 초안 (BIOP02-74)

> 작성 jamie · 2026-08-04 · 초안 v0.1
> 범위: 코호트 · 라벨 출처/정의 · 결측 처리 · split 정책 (모델/학습/통계는 [guide/paper_a_methods_modeling_draft.md](paper_a_methods_modeling_draft.md), BIOP02-72 소관)
> 근거: agents/data/split_policy_v0.md, agents/data/cptac_labels_v1.md (BIOP02-55), agents/data/docs/her2_pam50_label_qc_v0.1.md (BIOP02-49), /workspace/data/cache/biop02/README_embeddings_kkkim.md
> 수치는 커밋된 아티팩트 + split_hash 잠금 기준. claim_level: hypothesis_only.

---

## D.1 Cohorts

**Discovery cohort — TCGA-BRCA.** We use the full diagnostic-slide TCGA-BRCA cohort available
to the project (*n* = 1,010 patients; one or more H&E whole-slide images per patient), split
patient- and site-disjointly into train/val/internal-test = 707/152/151 (§D.4). This is the
entire cohort, not a convenience subset — an earlier internal "~150 subset" convention was
explicitly overridden for Paper A to preserve statistical power for the site-disjoint split
(Leader decision, 2026-06-10).

**External cohort — CPTAC-BRCA.** We use CPTAC-BRCA as a fully held-out external test cohort,
never exposed during training or model selection (frozen-transfer protocol, see modeling
Methods M.8). The imaging inventory contains 198 patients (653 slide series;
`cptac_brca_idc_inventory.csv`). Of these, 120 have at least one usable clinical label; the
remaining 78 have imaging but no matched clinical label in the sources we could access
(§D.2) and are excluded from all endpoint evaluations (not imputed, not dropped from the
inventory record). Two additional CPTAC cases carry clinical labels but use a sample-ID
scheme (`CPT0xxxxx`) that does not resolve against the imaging inventory and are excluded from
imaging-linked analysis.

## D.2 Whole-slide image preprocessing

Slides are tiled at 256×256 px (20× equivalent magnification) after Otsu tissue masking, with a
per-patient cap of 5,000 tiles (uniform random subsample above the cap; capping status recorded
per slide). Tile-level embeddings are extracted with a frozen pathology foundation model (UNI v1,
1,024-d; CONCH and EXAONE variants used for supplementary comparisons only, see modeling Methods
M.3) — no gradients flow into the foundation model at any stage. This preprocessing is identical
for TCGA-BRCA and CPTAC-BRCA. Full embedding-pipeline detail is out of scope here; see the
embedding-layer runbook (`guide/embedding_batch_runbook.md`, `README_embeddings_kkkim.md`).

## D.3 Label sources and definitions

**ER / PR / HER2 status (binary).** Source: TCGA clinical biotab IHC calls (TCGA-BRCA) and the
corresponding CPTAC clinical annotation (Krug et al., *Cell* 2020, cBioPortal study
`brca_cptac_2020`) for the external cohort. Both are binarized Positive/Negative; Equivocal,
Indeterminate, and Not-Evaluated calls are treated as missing for that endpoint only (§D.4), not
imputed.

**PAM50 intrinsic subtype (4-class).** Modeled as LumA / LumB / HER2-enriched / Basal; the
Normal-like class is excluded per the split policy (weak, unreliable morphological signal on
H&E; consistent with Tafavvoghi et al. 2024). For TCGA, PAM50 is not present in the clinical
biotab. **Corrected 2026-08-20** (BIOP02-49's provenance follow-up, `tcga_brca_pam50_computed_
PROVENANCE.md`, landed on `main` after this draft was first written): the committed TCGA PAM50
calls are **not** a cBioPortal-sourced file — they are a locally-computed nearest-centroid
classification (Parker et al. 2009 method, confidence range 0.808–0.925) run against expression
data outside this repo. `split_policy_v0.md` §10 originally named cBioPortal TCGA-BRCA PAM50 as
the *primary* source with the local computation as a *fallback for coverage gaps*, which did not
describe what the manifest actually does; that policy text has since been corrected to name the
computed calls as the source of record (§10.1, data-owner decision 2026-08-20). For CPTAC, PAM50
comes from the same `brca_cptac_2020` release as the other endpoints; class naming was normalized
across cohorts (CPTAC's `Her2` → `HER2`) so both use identical class labels.

**Resolved 2026-08-20 — source pinned and the data-owner has ruled.**
Re-verified 2026-08-20 with the exact cBioPortal source pinned: study `brca_tcga_pan_can_atlas_2018`,
attribute `SUBTYPE` (PATIENT-level, values prefixed `BRCA_`), covering **981 of the 1,009
patients carrying a manifest PAM50 call (97.2%)**. Against this source, the committed
(local/genefu) PAM50 calls match at **57.0%**
(514/902 overlapping labeled patients) — confirms BIOP02-49's original finding, now with the
comparison source's `study_id`/attribute fully citable. Mismatches concentrate in two known-hard
boundaries, not random noise: local=LumB vs. cBioPortal=LumA (141 patients) and local=Normal vs.
cBioPortal=LumA (101 patients) — consistent with the literature's documented LumA/LumB boundary
instability and Normal-like call instability across PAM50 implementations, not evidence either
source is simply wrong. **Data-owner decision (kkkim, 2026-08-20):** the surfaced conflict was
that §10 authorized the local/genefu computation only as a fallback for short cBioPortal
coverage, yet coverage is 97.2% — high, not short — while the manifest used the computed calls
across the whole cohort. **The Parker-2009 computed calls stay as the source of record; the
manifest does not switch to cBioPortal.** Rationale: the Paper A/C analyses were already run and
verified against these labels (manifest agrees 1,009/1,009 with the committed source file), and
re-deriving them would be an unmotivated moving of the goalposts; the Parker centroid classifier
is the canonical PAM50 method and is directly citable. The 57.0% figure is therefore reported
here as a transparency item, not as an unresolved defect, and `split_policy_v0.md` §10 has been
corrected to name actual practice (see its §10.1). One non-blocking gap remains: the script and
input expression matrix that produced the computed calls are not in this repo, so the labels are
not yet end-to-end reproducible — follow-up per the provenance note. Does not affect the split
(§D.4), which is defined over the full patient set independent of any single label's
availability. Reproducible via
`agents/data/scripts/pam50_source_reconcile.py`, output
`agents/data/manifests/pam50_source_reconcile_biop02-74.json`.

**Missingness handling.** Each endpoint's missing/excluded values (§ above) are masked
per-task via boolean `has_er / has_pr / has_her2 / has_pam50` columns. Missingness never removes
a patient from the cohort or from the split — the site-disjoint patient split (§D.4) is computed
once over the full cohort, and each phenotype head trains/evaluates only on the subset of
patients carrying a usable label for that endpoint. This keeps the split identical across
endpoints, which matters for cross-endpoint comparability and reproducibility.

Per-endpoint usable-label counts, external CPTAC cohort (out of 198 imaged patients): ER 118,
PR 113, HER2 95, PAM50 115 patients (equivalently, at slide level: ER 387, PR 375, HER2 294,
PAM50 382 of 653 slides). TCGA per-endpoint counts follow the same masking convention over the
707/152/151 patient split; a QC pass (BIOP02-49) found and fixed a manifest bug in which
`"[Not Evaluated]"` — a standard TCGA biotab sentinel — was not recognized as missing, causing
118/1,010 slides (11.7%) to be miscounted as HER2-labeled; the fix only patched derived QC
columns and did not change any patient's split assignment (`split_hash` unchanged, verified).
Downstream modeling scripts were unaffected because they filter on the raw status string
directly rather than the derived flag.

## D.4 Split policy (patient-level, site-disjoint)

All experiments use a single, version-locked split defined over the full TCGA-BRCA cohort:

- **Split unit = patient** (`case_id`), never slide or tile — all slides for one patient fall in
  the same fold (Bussola et al. 2020: slide/tile-level splitting leaks patient identity into
  held-out data and inflates reported accuracy).
- **Site-disjoint**: in addition to patient-level separation, no TCGA submitting site (Tissue
  Source Site, encoded in the second token of the patient barcode) spans more than one fold.
  Site assignment uses Howard et al.'s PreservedSiteCV (quadratic-program class-balance
  minimization) with a greedy site-grouped fallback. This guards against the documented case
  where a foundation-model embedding can predict the submitting site with near-perfect accuracy
  (site-probe AUC 0.9977 measured on this cohort's embeddings, consistent with Howard et al.
  2021's 0.964–0.998 range) — an uncontrolled channel that leakage at the slide/tile level, or
  even at the patient level without site control, would not catch (Yagis et al. 2021 report
  29–55% accuracy inflation from this class of leakage on histopathology data).
- **Fractions**: train 0.70 / val 0.15 / internal test 0.15 (achieved fractions vary slightly
  because whole sites, not individual patients, are the unit of assignment — site groups are
  never split to hit an exact ratio). External test = the entire CPTAC-BRCA cohort, which is
  site-disjoint from TCGA by construction (a structurally distinct cohort with a non-overlapping
  ID namespace) and was additionally verified empirically to have zero patient overlap with the
  locked 1,010-patient TCGA set.
- **Lock record**: split defined once, hashed (`split_hash = 5995f29d3978b831`), and stamped into
  every experiment's `metrics.json`; any change requires a new version and hash. Lock criteria —
  patient-overlap = 0, site-disjoint over 37 sites (0 crossings), per-fold ER/PR/HER2/PAM50 class
  balance reviewed — were signed off by the data-owner (kkkim, 2026-07-11) and independently
  cross-signed by Critic (braveji, 2026-07-13; owner≠reviewer). One caution noted at sign-off:
  HER2 positivity is higher in val than train (34% vs 19%), an accepted consequence of the
  site-disjoint constraint rather than a labeling error.

## D.5 Data availability and reproducibility

Manifest-generation and label-mapping scripts are committed and re-runnable:
`agents/data/scripts/build_manifest.py` (TCGA manifest + site-disjoint split assignment),
`agents/data/scripts/build_cptac_labels.py` (CPTAC label mapping, supports `--refresh` against
the cBioPortal API). Full provenance for the CPTAC label mapping — join-key resolution, class
normalization, the excluded-78/excluded-2 accounting above — is documented in
`agents/data/cptac_labels_v1.md`; the manifest QC pass and its one fixed bug are documented in
`agents/data/docs/her2_pam50_label_qc_v0.1.md`. Every experiment's `metrics.json` records both
the git commit hash and `split_hash`, so any reported number can be traced back to the exact
data version that produced it.

---

*상태: 초안 v0.1. 모델/학습/평가 절(M.1–M.9)은 sjpark 초안([guide/paper_a_methods_modeling_draft.md](paper_a_methods_modeling_draft.md))과 상호 연결 — 특히 M.2(tiling/embedding), M.5(split 수치)가 이 문서를 "Data Methods"로 지칭하고 있어 정합 확인 완료. braveji가 M.7에서 지적한 mean-embed≠pixel-mean 용어 문제(-72 코멘트 11387 ①)는 이 문서 범위 밖(모델링 절 소관).*

*해소됨(2026-08-20 kkkim 결정, Jira 11999): PAM50 대조 소스의 study_id 고정
(`brca_tcga_pan_can_atlas_2018`, `SUBTYPE` 속성, manifest PAM50 코호트 커버리지 981/1009=97.2%)에 이어, 그 과정에서
드러난 **정책 vs 실사용 불일치**(§10은 cBioPortal 1순위·genefu는 커버리지 부족시 fallback이라
했으나 커버리지가 97.2%로 "부족"이 아닌데 전 코호트가 계산본을 사용)도 결론이 났다. **결정:
Parker 2009 계산본(`tcga_brca_pam50_computed.csv`)을 정본으로 유지**하고 cBioPortal로 전환하지
않는다 — 분석이 이미 이 라벨로 검증됐고(manifest 1009/1009 일치) Parker centroid는 PAM50 정본
분류기이기 때문. 57.0% 불일치는 오류가 아니라 로컬 계산본 vs curated atlas의 파생 차이이며 위
Methods 본문에 투명성 항목으로 보고했다. `split_policy_v0.md` §10 문구도 실사용에 맞게 정정
(§10.1 신설). 재현 스크립트=`agents/data/scripts/pam50_source_reconcile.py`.*

*잔여(비차단): 계산본을 생성한 스크립트와 입력 발현 행렬(study_id·버전)이 레포에 없어 완전
재현은 아직 불가 — PROVENANCE "남은 gap"의 후속 과제이며 braveji가 `594ef6b`에서 비블로커로
확인했다.*

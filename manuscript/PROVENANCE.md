# 근거 파일 대조표 (PROVENANCE)
> 원고 본문의 `<!-- prov: Pxx -->` 주석이 이 표를 가리킨다.
> **본문에서 분리한 이유**: ML4H 2026은 이중맹검이고 저장소 경로에 팀원 계정명이 들어가 신원이 노출된다.
> CFP는 비익명 원고를 정식 심사 없이 데스크 리젝할 수 있다고 명시한다. 재현성 기록은 버리지 않고 여기로 옮겼다.
> 근거: BIOP02-151 (Methods 오너 결정, 2026-09-02) · `VENUE.md`

| 키 | 근거 |
|---|---|
| `P02` | experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md L17 (0.9594, n_pos=26); pre-reg threshold 0.80 = SUBSTITUTABILITY_LAW_PREREGISTRATION.md |
| `P03` | LAW_HELDOUT_SCOREBOARD.md L18, L20 |
| `P04` | LAW_HELDOUT_SCOREBOARD.md L31 (0.599, anchor near-random) |
| `P05` | LAW_HELDOUT_SCOREBOARD.md L25 (real 0.6444 ≈ null 0.6406) |
| `P06` | LAW_HELDOUT_SCOREBOARD.md L22; experiments/crosscancer/LUNG_NSCLC/full/SUBTYPE_BASELINE_NOTE.md |
| `P07` | LAW_HELDOUT_SCOREBOARD.md "인식론 구분"; COLORECTAL/full/LAW_TEST.md top banner |
| `P08` | experiments/crosscancer/MULTIFM_COMPARISON.md §5; CROSSCHECK_5SEED_MULTIFM.md HPV/virchow2 row |
| `P09` | experiments/kkkim/20260805_site_audit/site_audit_results.json |
| `P10` | site_audit_results.json |
| `P11` | BIOP02-141_FINDINGS.md; jamie sign-off 2026-08-14 |
| `P12` | LAW_HELDOUT_SCOREBOARD.md 통합 표, n_pos column |
| `P13` | experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost.json, therapeutic_distance.json |
| `P14` | experiments/kkkim/20260819_stain_norm_robustness/clam_rerun/sjpark/{her2_status,er_status,pam50}_clam*_uni_stainnorm/metrics.json (0.6408, 0.9166, 0.7396); non-normalised anchor values from Table R1 / LAW_HELDOUT_SCOREBOARD.md |
| `P15` | experiments/crosscancer/GASTRIC_STAD/full/LAUREN_POSCONTROL_DIAGNOSIS.md; LAW_HELDOUT_SCOREBOARD.md 결론 #3 |
| `P16` | experiments/crosscancer/CROSSCHECK_5SEED_MULTIFM.md (Spearman 1.000, 6/6 PASS) |
| `P17` | MULTIFM_COMPARISON.md §1, §5 |
| `P18` | MULTIFM_COMPARISON.md §5 "lauren·erbb2는 전 FM FAIL(각각 site-교란·신호0)" |
| `P19` | 02_results.md R5 paragraph; braveji G2 finding (BIOP02-101) |
| `P20` | CROSSCHECK_5SEED_MULTIFM.md, MULTIFM_COMPARISON.md (5-seed canonical). Colorectal BRAF row here uses the 5-seed holdout151 values (0.8676 etc.), distinct from Table R1's holdout161 routing value 0.882 — different splits, same marker, CI-consistent. |
| `P21` | 02_results.md R7; experiments/kkkim/angle_A_spatial_erbb2/ |
| `P22` | site_audit_results.json; experiments/kkkim/20260819_stain_norm_robustness/ (BRCA anchor only); GPU return / raw loss noted in RESUME.md |
| `P23` | 04_discussion.md item 6; experiments/kkkim/20260820_shuffle_null_20seed/ |
| `P24` | 04_discussion.md Limitations 1–4; experiments/braveji/BIOP02-75_critic_gate/GATE_STATUS.md |
| `P25` | agents/data/manifests/pam50_source_reconcile_biop02-74.json (concordance_pct=57.0, n_match=514/n_overlap=902) |
| `P26` | pam50_source_reconcile_biop02-74.json policy_check field |
| `P27` | 03_methods.md M1 |
| `P28` | pam50_source_reconcile_biop02-74.json |
| `P29` | 03_methods.md M2 |
| `P30` | 03_methods.md M3; experiments/crosscancer/run_mil_cost.py |
| `P31` | 03_methods.md M4 |
| `P32` | 03_methods.md M5; experiments/kkkim/20260710_cost_of_substitution/ |
| `P33` | 03_methods.md M6 |
| `P34` | 02_results.md R6 (0.533 [0.411–0.653]); status pending per task instruction |
| `P35` | 03_methods.md M8; MULTIFM_COMPARISON.md header |
| `P36` | 03_methods.md M9; site_audit_results.json |
| `P37` | experiments/kkkim/20260819_stain_norm_robustness/RESUME.md; clam_rerun/sjpark/*/metrics.json (0.6408/0.9166/0.7396) |
| `P38` | CROSSCHECK_5SEED_MULTIFM.md, MULTIFM_COMPARISON.md (5-seed 정본). 여기 대장 BRAF 행은 5-seed holdout151 값(0.8676 등)으로, 표 R1의 holdout161 라우팅 값 0.882와 다른 분할이다 — 같은 마커, CI 일관. |

## 분할 해시

`split_policy_v0` 정본 fold hash = `5995f29d3978b831` (2026-07-11 lock, train 707 / val 152 / test 151)

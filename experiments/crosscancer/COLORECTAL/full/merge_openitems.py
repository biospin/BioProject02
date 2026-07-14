#!/usr/bin/env python3
"""부분 결과(part_gpu0/1.json) 병합 → shuffle_null_robustness.json + routing_cost_v2.json.

- shuffle_null_robustness.json: 7 endpoint 별 5-seed null 분포 + real 마진 + proba~tilecount spearman.
  real_auroc(margin용) = 권위 파일(mil_cms_fidelity.json / routing_cost.json v1)에서 인용. recomputed도 병기.
- routing_cost_v2.json: v1 스칼라(misroute_rate/AUROC) 그대로 + mean_cost 채움(임상 방향거리, braf는 frozen 0.868 유지).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SC = Path("/tmp/claude-10005/-home-kkkim-project-BioProject02/d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad")
COMMIT = "d3a614f88855eafd50bf764aaf1ec07e543c33b6"

part = {}
for f in ("part_gpu0.json", "part_gpu1.json"):
    part.update(json.loads((SC / f).read_text()))

cms = json.loads((HERE / "mil_cms_fidelity.json").read_text())
v1 = json.loads((HERE / "routing_cost.json").read_text())
clin = json.loads((HERE / "clinical_routing_distance_preregistered.json").read_text())

# authoritative real AUROC per endpoint
auth_real = {}
for k in (1, 2, 3, 4):
    ep = f"cms{k}_vs_rest"
    auth_real[ep] = cms["endpoints"][ep]["real_auroc"]
for ep in ("msi_high", "anti_egfr_eligible", "braf_v600"):
    auth_real[ep] = v1["axes"][ep]["mil_auroc"]

# authoritative single-seed(42) shuffle null for cross-check
auth_null42 = {}
for k in (1, 2, 3, 4):
    ep = f"cms{k}_vs_rest"
    auth_null42[ep] = cms["endpoints"][ep]["shuffle_null_auroc"]
for ep in ("msi_high", "anti_egfr_eligible", "braf_v600"):
    auth_null42[ep] = v1["axes"][ep]["shuffle_null_auroc"]

# ---------- shuffle_null_robustness.json ----------
rob = {
    "track": "shuffle-null 5-seed robustness + bag-size(proba~tile수) 교란 점검",
    "purpose": "flagged 이슈 정면해소: seed=42 단일 shuffle-null이 split만 바뀌어 흔들린 문제 → 5 seed 재학습으로 null 분포 산출. real AUROC가 null_mean+2SD를 넘는지(우연배제 강건성) + proba~tile수 Spearman으로 bag-size 교란 여부.",
    "claim_level": "hypothesis_only", "critic_status": "pending", "commit": COMMIT,
    "shuffle_seeds": [42, 1, 2, 3, 4],
    "method": "각 seed마다 train 라벨순열+모델 재초기화(seed→torch/np/dev-split/shuffle 모두 구동) 후 CLAM-SB 재학습, holdout(val+test, site-disjoint) AUROC. real_auroc는 권위 파일 인용(margin용), recomputed 병기(seed42 재현확인).",
    "criterion": "real_auroc > null_mean + 2*null_sd (5 seed, ddof=1 → SD 자유도 4로 노이지, 보수적). 미달=우연배제 강건성 미확보로 '실패'로 명시(weak≠zero).",
    "endpoints": {},
}
for ep in ("cms1_vs_rest", "cms2_vs_rest", "cms3_vs_rest", "cms4_vs_rest",
           "msi_high", "anti_egfr_eligible", "braf_v600"):
    r = part[ep]; sn = r["shuffle_null"]
    real = auth_real[ep]
    thr = sn["null_mean_plus_2sd"]
    rob["endpoints"][ep] = {
        "real_auroc": real,
        "real_auroc_recomputed_seed42": r["real_auroc_recomputed"],
        "null_seeds": sn["null_seeds"],
        "null_mean": sn["null_mean"], "null_sd": sn["null_sd"],
        "null_min": sn["null_min"], "null_max": sn["null_max"],
        "null_mean_plus_2sd": thr,
        "margin_real_minus_nullmean": (round(real - sn["null_mean"], 4)
                                       if (real is not None and sn["null_mean"] is not None) else None),
        "real_gt_null_mean_plus_2sd": (real is not None and thr is not None and real > thr),
        "single_seed42_null_authoritative": auth_null42[ep],
        "n_holdout": r["n_holdout"], "n_pos": r["n_pos"],
        "proba_tilecount_spearman": r["proba_tilecount_spearman"],
    }

(HERE / "shuffle_null_robustness.json").write_text(json.dumps(rob, indent=2, ensure_ascii=False))
print("wrote shuffle_null_robustness.json")

# ---------- routing_cost_v2.json ----------
# 방향거리 (임상 사전등록); braf는 frozen_map 0.868 대칭 유지
clin_ax = clin["axes"]
v2 = json.loads(json.dumps(v1))  # deep copy, v1 스칼라 verbatim
v2["track_v2"] = "v1 misroute_rate/AUROC verbatim + mean_cost 채움(임상 방향거리 사전등록). misroute_rate/AUROC 불변."
v2["clinical_distance_preregistered"] = "clinical_routing_distance_preregistered.json"
v2["mean_cost_scale_caveat"] = ("MSI/anti-EGFR mean_cost=임상-결정 스케일(clinical_routing_distance_preregistered.json), "
                                "braf mean_cost=0.086은 세포주 frozen_map 스케일(0.868) 유지 → 세 값 직접 비교/교차랭킹 불가.")

recon = {}  # misroute 재계산이 v1과 일치하는지 기록
for ep in ("msi_high", "anti_egfr_eligible"):
    mr = part[ep]["misroute_recompute"]
    d_fn = clin_ax[ep]["d_FN"]["value"]; d_fp = clin_ax[ep]["d_FP"]["value"]
    n = mr["n_holdout"]
    mean_cost = round((mr["n_FN"] * d_fn + mr["n_FP"] * d_fp) / n, 3) if n else None
    v1_rate = v1["axes"][ep]["misroute_rate"]
    match = (mr["misroute_rate"] is not None and abs(mr["misroute_rate"] - v1_rate) <= 0.001)
    recon[ep] = {"v1_misroute_rate": v1_rate, "recomputed_misroute_rate": mr["misroute_rate"],
                 "reproduces_v1": match, "n_FN": mr["n_FN"], "n_FP": mr["n_FP"], "n_holdout": n,
                 "d_FN": d_fn, "d_FP": d_fp}
    ax = v2["axes"][ep]
    if match:
        ax["mean_cost"] = mean_cost
        ax["mean_cost_note"] = (f"임상 방향거리 사전등록: (n_FN {mr['n_FN']}*{d_fn} + n_FP {mr['n_FP']}*{d_fp})/{n}. "
                                "misroute_rate v1 재현확인.")
    else:
        ax["mean_cost"] = mean_cost
        ax["mean_cost_note"] = (f"[DRIFT] recomputed misroute_rate {mr['misroute_rate']} != v1 {v1_rate} "
                                f"(GPU-stochastic early-stop). mean_cost는 재계산 예측 기반, v1 스칼라는 미변경 유지. 사람 확인 필요.")

# braf: frozen 0.868 유지 (v1 mean_cost=0.086 불변)
v2["axes"]["braf_v600"]["mean_cost_note"] = ("frozen_map antiBRAF__baseline=0.868 세포주 치료거리 유지(v1 불변). "
                                             "임상 방향거리 parallel은 clinical_routing_distance_preregistered.json braf_v600_note 참조(선택).")
v2["misroute_reconciliation"] = recon

(HERE / "routing_cost_v2.json").write_text(json.dumps(v2, indent=2, ensure_ascii=False))
print("wrote routing_cost_v2.json")
print("RECON:", json.dumps(recon, ensure_ascii=False))
print("mean_cost msi/anti_egfr/braf:",
      v2["axes"]["msi_high"]["mean_cost"], v2["axes"]["anti_egfr_eligible"]["mean_cost"], v2["axes"]["braf_v600"]["mean_cost"])

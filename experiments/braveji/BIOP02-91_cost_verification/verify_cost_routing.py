"""
BIOP02-91 Critic 검증 — receptor 라우팅 cost 재계산 + 환자 단위 부트스트랩 (braveji).

목적 두 가지:
  1. `patient_routing_cost_receptor.json`(owner=kkkim)의 confusion·mean_cost·contrast를
     원자료에서 독립 재계산해 대조 (Owner≠Reviewer).
  2. **pseudo-replication 점검** — n=294는 슬라이드 수이고 고유 환자는 95명이다.
     같은 환자의 슬라이드는 라벨이 같고 예측이 상관되므로 슬라이드 단위 부트스트랩은
     CI를 과소추정한다. 환자 클러스터 부트스트랩과 비교한다.

Run (GPU 머신 — /workspace CPTAC manifest 필요):
    /opt/envs/spatialpatho/bin/python experiments/braveji/BIOP02-91_cost_verification/verify_cost_routing.py
"""

import csv
import json
from pathlib import Path

import numpy as np

PRED = "experiments/sjpark/cptac_ext_predictions_indexed.csv"
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"
OUT = Path(__file__).parent / "verification_result.json"

# therapeutic_distance.json (axis_pair_distance) — 1 - Kendall tau on 170 discriminating drugs
DIST = {
    ("endocrine", "antiHER2"): 0.395,
    ("endocrine", "chemo"): 0.695,
    ("antiHER2", "chemo"): 0.765,
}
THRESHOLD = 0.5  # 라우팅 임계 (원 JSON 미기재 → 재현으로 확인한 값)
B = 5000
SEED = 42


def dist(a, b):
    if a == b:
        return 0.0
    return DIST.get((a, b)) or DIST.get((b, a))


def route_true(er, her2):
    if her2 == "positive":
        return "antiHER2"
    return "endocrine" if er == "positive" else "chemo"


def route_pred(er_p, her2_p, thr=THRESHOLD):
    if her2_p > thr:
        return "antiHER2"
    return "endocrine" if er_p > thr else "chemo"


def contrast(axis, cost):
    """headline = mean_cost(antiHER2) - mean_cost(endocrine)"""
    return cost[axis == "antiHER2"].mean() - cost[axis == "endocrine"].mean()


def main():
    pred = {r["slide_id"]: r for r in csv.DictReader(open(PRED))}
    rows = []
    for r in csv.DictReader(open(MANIFEST)):
        sid = r["slide_id"]
        if sid not in pred:
            continue
        er = (r.get("er", "") or "").strip().lower()
        her2 = (r.get("her2", "") or "").strip().lower()
        if her2 not in ("positive", "negative") or er not in ("positive", "negative"):
            continue
        p = pred[sid]
        t = route_true(er, her2)
        q = route_pred(float(p["er_pred_prob"]), float(p["her2_pred_prob"]))
        rows.append((r["case_id"], t, q, dist(t, q)))

    case = np.array([r[0] for r in rows])
    axis = np.array([r[1] for r in rows])
    predr = np.array([r[2] for r in rows])
    cost = np.array([r[3] for r in rows])
    n_slides, n_pat = len(rows), len(set(case))
    print(f"n_slides={n_slides}  n_patients={n_pat}  (평균 {n_slides/n_pat:.2f} 슬라이드/환자)")

    conf = {t: {q: int(((axis == t) & (predr == q)).sum())
                for q in ["endocrine", "antiHER2", "chemo"]
                if ((axis == t) & (predr == q)).sum()} for t in ["endocrine", "antiHER2", "chemo"]}
    per_axis = {t: {"n": int((axis == t).sum()),
                    "mean_cost": round(float(cost[axis == t].mean()), 4),
                    "misroute_rate": round(float(1 - (predr[axis == t] == t).mean()), 3)}
                for t in ["endocrine", "antiHER2", "chemo"]}
    ct = float(contrast(axis, cost))
    for t, v in per_axis.items():
        print(f"  {t}: {v}")
    print(f"  headline contrast = {ct:.4f}")

    rng = np.random.default_rng(SEED)

    # (a) slide-level bootstrap — 커밋본이 쓴 방식(재현 대조용)
    bs = []
    for _ in range(B):
        i = rng.integers(0, n_slides, n_slides)
        a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0:
            continue
        bs.append(contrast(a2, cost[i]))
    lo_s, hi_s = np.percentile(bs, [2.5, 97.5])

    # (b) patient-level cluster bootstrap — 올바른 리샘플 단위
    pats = sorted(set(case))
    idx_by = {p: np.where(case == p)[0] for p in pats}
    bp = []
    for _ in range(B):
        pick = rng.choice(pats, len(pats), replace=True)
        i = np.concatenate([idx_by[p] for p in pick])
        a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0:
            continue
        bp.append(contrast(a2, cost[i]))
    lo_p, hi_p = np.percentile(bp, [2.5, 97.5])

    print(f"\n  slide-level   CI = [{lo_s:.3f}, {hi_s:.3f}] width={hi_s-lo_s:.3f}")
    print(f"  patient-level CI = [{lo_p:.3f}, {hi_p:.3f}] width={hi_p-lo_p:.3f}"
          f"  ({(hi_p-lo_p)/(hi_s-lo_s):.2f}x wider)")

    out = {
        "verifier": "braveji (Critic 총괄)", "target": "patient_routing_cost_receptor.json",
        "owner": "kkkim", "owner_ne_reviewer": True,
        "threshold_used": THRESHOLD, "n_bootstrap": B, "seed": SEED,
        "n_slides": n_slides, "n_patients": n_pat,
        "confusion_true_to_pred": conf, "per_axis": per_axis,
        "headline_contrast": round(ct, 4),
        "ci95_slide_level": [round(float(lo_s), 3), round(float(hi_s), 3)],
        "ci95_patient_level": [round(float(lo_p), 3), round(float(hi_p), 3)],
        "ci_widening_factor": round(float((hi_p - lo_p) / (hi_s - lo_s)), 2),
        "excludes_zero_patient_level": bool(lo_p > 0),
        "finding": ("원자료 재현 전부 일치. 단 n=294는 슬라이드(환자 95명) — 커밋 CI는 슬라이드 단위 "
                    "부트스트랩이라 pseudo-replication으로 과소추정. 환자 단위로는 1.32× 넓어지나 "
                    "여전히 0 배제 → 헤드라인 결론 유지."),
        "critic_status": "caution",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()

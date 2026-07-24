#!/usr/bin/env python3
"""BIOP02-91 remediation (owner=kkkim) — braveji Critic caution 4건 반영.

braveji 지적(VERIFICATION_braveji.md §4):
  1. CI를 환자 단위로 교체 (슬라이드 단위 = pseudo-replication, 고유환자 95명)
  2. pred_source 개인 절대경로 → repo-relative
  3. 라우팅 임계 0.5 JSON 기재
  4. CI 산출 메타(B·seed·리샘플 단위) 기재

owner 재계산: braveji verify_cost_routing.py와 동일 방법으로 headline_contrast를 재현하고,
per_axis mean_cost의 CI도 환자 클러스터 부트스트랩으로 새로 산출한다.
braveji 목표값 headline patient-CI [0.331, 0.427]을 크로스체크 타깃으로 확인.
"""
import csv, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
PRED = "experiments/sjpark/cptac_ext_predictions_indexed.csv"           # repo-relative
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv"  # 공유경로
JSON = HERE / "patient_routing_cost_receptor.json"
THRESHOLD = 0.5
B = 5000
SEED = 42

DIST = {("endocrine", "antiHER2"): 0.395, ("endocrine", "chemo"): 0.695, ("antiHER2", "chemo"): 0.765}

def dist(a, b):
    return 0.0 if a == b else (DIST.get((a, b)) or DIST.get((b, a)))

def route_true(er, her2):
    if her2 == "positive": return "antiHER2"
    return "endocrine" if er == "positive" else "chemo"

def route_pred(er_p, her2_p, thr=THRESHOLD):
    if her2_p > thr: return "antiHER2"
    return "endocrine" if er_p > thr else "chemo"

def main():
    pred = {r["slide_id"]: r for r in csv.DictReader(open(PRED))}
    rows = []
    for r in csv.DictReader(open(MANIFEST)):
        sid = r["slide_id"]
        if sid not in pred: continue
        er = (r.get("er", "") or "").strip().lower()
        her2 = (r.get("her2", "") or "").strip().lower()
        if her2 not in ("positive", "negative") or er not in ("positive", "negative"): continue
        p = pred[sid]
        t = route_true(er, her2)
        q = route_pred(float(p["er_pred_prob"]), float(p["her2_pred_prob"]))
        rows.append((r["case_id"], t, q, dist(t, q)))

    case = np.array([r[0] for r in rows]); axis = np.array([r[1] for r in rows])
    predr = np.array([r[2] for r in rows]); cost = np.array([r[3] for r in rows])
    n_slides, n_pat = len(rows), len(set(case))
    print(f"n_slides={n_slides}  n_patients={n_pat}  ({n_slides/n_pat:.2f} slides/pt)")

    axes = ["endocrine", "antiHER2", "chemo"]
    def mean_cost(ax, msk): return cost[msk][axis[msk] == ax].mean() if (axis[msk] == ax).any() else np.nan
    def headline(msk): return mean_cost("antiHER2", msk) - mean_cost("endocrine", msk)

    full = np.ones(n_slides, bool)
    per_axis = {ax: {"n": int((axis == ax).sum()),
                     "mean_cost": round(float(cost[axis == ax].mean()), 4),
                     "misroute_rate": round(float(1 - (predr[axis == ax] == ax).mean()), 3)} for ax in axes}
    ct = float(headline(full))

    # patient-cluster bootstrap: headline + per-axis mean_cost
    pats = sorted(set(case)); idx_by = {p: np.where(case == p)[0] for p in pats}
    rng = np.random.default_rng(SEED)
    bh, bax = [], {ax: [] for ax in axes}
    for _ in range(B):
        pick = rng.choice(pats, len(pats), replace=True)
        i = np.concatenate([idx_by[p] for p in pick])
        a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0: continue
        bh.append(cost[i][a2 == "antiHER2"].mean() - cost[i][a2 == "endocrine"].mean())
        for ax in axes:
            if (a2 == ax).any(): bax[ax].append(cost[i][a2 == ax].mean())
    lo_p, hi_p = np.percentile(bh, [2.5, 97.5])

    # slide-level (대조용, braveji 기록 CI 재현 확인)
    bs = []
    for _ in range(B):
        i = rng.integers(0, n_slides, n_slides); a2 = axis[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0: continue
        bs.append(cost[i][a2 == "antiHER2"].mean() - cost[i][a2 == "endocrine"].mean())
    lo_s, hi_s = np.percentile(bs, [2.5, 97.5])

    for ax in axes:
        lo, hi = np.percentile(bax[ax], [2.5, 97.5])
        per_axis[ax]["mean_cost_ci95_patient"] = [round(float(lo), 4), round(float(hi), 4)]
    per_axis["headline_contrast"] = {
        "value": round(ct, 4),
        "ci95": [round(float(lo_p), 4), round(float(hi_p), 4)],
        "ci95_method": "patient-cluster bootstrap",
        "excludes_zero": bool(lo_p > 0),
        "ci95_slide_level_deprecated": [round(float(lo_s), 4), round(float(hi_s), 4)],
    }
    print(f"headline={ct:.4f}  patient-CI=[{lo_p:.4f},{hi_p:.4f}]  slide-CI=[{lo_s:.4f},{hi_s:.4f}]")
    print(f"braveji 타깃 [0.331,0.427] 대조: {'✅ 근접' if abs(lo_p-0.331)<0.01 and abs(hi_p-0.427)<0.02 else '⚠️ 확인'}")

    j = json.load(open(JSON))
    j["pred_source"] = PRED
    j["routing_threshold"] = THRESHOLD
    j["ci_method"] = {"resample_unit": "patient (cluster bootstrap)", "n_bootstrap": B, "seed": SEED,
                      "n_slides": n_slides, "n_patients": n_pat,
                      "note": "슬라이드 단위 부트스트랩은 pseudo-replication(환자당 평균 %.2f장)이라 CI 과소추정 → 환자 클러스터로 교체(braveji Critic BIOP02-91)." % (n_slides/n_pat)}
    j["per_axis"] = per_axis
    j["critic_status"] = "caution_remediated_pending_signoff"
    JSON.write_text(json.dumps(j, ensure_ascii=False, indent=2))
    print(f"wrote {JSON}")

if __name__ == "__main__":
    main()

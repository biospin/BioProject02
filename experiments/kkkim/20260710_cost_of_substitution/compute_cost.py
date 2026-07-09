#!/usr/bin/env python3
"""
C1 cost-of-substitution — STEP 2: cost metric.

두 부분:
  (A) [지금 실행 가능, 예측 불필요] 치료축 간 '치료 거리' 행렬 —
      각 오라우팅 유형(예: HER2->endocrine)이 랭킹을 얼마나 바꾸는지(비용의 '크기').
      frozen_map.json만 사용. discriminating 약물에서 축별 랭킹 → 축쌍 Kendall-tau / top-k 불일치.
  (B) [예측 도착 후] 환자별 오라우팅 비용 —
      measured vs H&E-predicted subtype로 각 환자를 축에 배정,
      cost = (오라우팅 빈도) x (치료 거리), 진짜 subtype 층화 + contrast CI.
      sjpark가 slide_id 인덱스 예측 제공 시 활성화(현재 placeholder).

핵심 논지: cost = confusion(오라우팅 빈도) x therapeutic-distance(오라우팅 1건의 값).
(A)는 후자를 지금 확정한다 → HER2축이 나머지와 멀면, HER2 오분류 1건이 곧 큰 비용.
"""
from pathlib import Path
import json, itertools, numpy as np

HERE = Path(__file__).parent
fm = json.loads((HERE / "frozen_map.json").read_text())
axes = list(fm["frozen_map_axis_to_drug_z"].keys())          # endocrine, antiHER2, chemo
zmap = fm["frozen_map_axis_to_drug_z"]

# discriminating 약물 = gap>=0.5 (frozen_map.json top_discriminating 기준과 동일 임계)
# 여기선 세 축 모두 값이 있는 약물만 사용해 공정 비교
drugs = [d for d in zmap[axes[0]] if all(d in zmap[a] for a in axes)]
def gap(d):
    vs=[zmap[a][d] for a in axes]; return max(vs)-min(vs)
disc = sorted([d for d in drugs if gap(d) >= 0.5], key=gap, reverse=True)
print(f"공통 약물 {len(drugs)}개 중 discriminating(gap>=0.5) {len(disc)}개")

def ranking(axis, drug_set):
    # 민감(z 낮음)=상위. 약물->순위(0=가장 민감)
    order = sorted(drug_set, key=lambda d: zmap[axis][d])
    return {d: i for i, d in enumerate(order)}

def kendall_tau(r1, r2, items):
    n = len(items); c = d = 0
    for a, b in itertools.combinations(items, 2):
        s = np.sign((r1[a]-r1[b]) * (r2[a]-r2[b]))
        if s > 0: c += 1
        elif s < 0: d += 1
    return (c-d)/(c+d) if (c+d) else float("nan")

def topk_overlap(axisA, axisB, drug_set, k=10):
    a = sorted(drug_set, key=lambda d: zmap[axisA][d])[:k]
    b = sorted(drug_set, key=lambda d: zmap[axisB][d])[:k]
    return len(set(a) & set(b)) / k

print("\n=== (A) 치료축 간 거리 행렬 (discriminating 약물, 예측 불필요) ===")
print("낮은 Kendall-tau / 낮은 top10 overlap = 두 축의 치료 랭킹이 멀다 = 그 오라우팅이 비쌈\n")
rk = {a: ranking(a, disc) for a in axes}
print(f"{'축쌍':28} {'Kendall-tau':>12} {'top10-overlap':>14}")
dist = {}
for a, b in itertools.combinations(axes, 2):
    tau = kendall_tau(rk[a], rk[b], disc)
    ov = topk_overlap(a, b, disc, 10)
    dist[(a, b)] = {"kendall_tau": round(tau, 3), "top10_overlap": round(ov, 3),
                    "therapeutic_distance": round(1-tau, 3)}
    print(f"{a+' <-> '+b:28} {tau:12.3f} {ov:14.3f}")

out = {
    "exp": "C1_cost_step2A_therapeutic_distance",
    "note": ("cost = 오라우팅빈도(confusion, 예측 도착 후) x 치료거리(아래, 지금 확정). "
             "치료거리=1-Kendall_tau on discriminating drugs. 높을수록 그 축 혼동이 비쌈."),
    "n_discriminating_drugs": len(disc),
    "axis_pair_distance": {f"{a}__{b}": v for (a, b), v in dist.items()},
    "predicted_routing_pending": "sjpark slide_id-indexed predictions (JIRA BIOP02-53 comment 11006)",
}
(HERE / "therapeutic_distance.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print("\nwrote therapeutic_distance.json")

# ============================================================
# (B) 환자 오라우팅 비용 — PAM50 예측(자기완결 npz)로 지금 실행
#     cost = 오라우팅 시 치료거리. measured-axis vs predicted-axis.
#     PAM50 class: LumA=0,LumB=1,Basal=2,HER2=3,Normal=4 (baseline_pam50_uni.yaml)
# ============================================================
PAM50_AXIS = {0: "endocrine", 1: "endocrine", 2: "chemo", 3: "antiHER2", 4: None}  # Normal=None(제외)
D = {(a, b): dist.get((a, b), dist.get((b, a)))["therapeutic_distance"]
     for a in axes for b in axes if a != b}
def tdist(a, b):
    if a == b: return 0.0
    return D[(a, b)] if (a, b) in D else D[(b, a)]

pz = np.load(HERE.parent.parent / "sjpark/pam50_clam_mb_uni_v1/predictions_ext.npz", allow_pickle=True)
meas, pred = pz["label"], pz["pred"]
rng = np.random.default_rng(42)

recs = []
for m, p in zip(meas, pred):
    ma, pa = PAM50_AXIS[int(m)], PAM50_AXIS[int(p)]
    if ma is None:            # measured Normal-like → 라우팅 대상 아님(제외)
        continue
    if pa is None:            # 예측 Normal → '무치료'로 오라우팅(치료 상실): 최대 거리 페널티
        cost, dropped = max(D.values()), True
    else:
        cost, dropped = tdist(ma, pa), False
    recs.append({"true_axis": ma, "pred_axis": pa or "none(Normal)", "cost": cost, "dropped": dropped})

import collections
by = collections.defaultdict(list)
for r in recs: by[r["true_axis"]].append(r)

print("\n=== (B) 환자 오라우팅 비용 (PAM50 예측, n=%d, Normal-like 제외) ===" % len(recs))
print("cost = 오라우팅 시 치료거리(0=정확 라우팅). dropped=예측이 Normal이라 무치료로 샘")
print(f"{'true axis':12} {'n':>4} {'mean_cost':>10} {'mis-route%':>11} {'dropped%':>9}")
axis_stat = {}
for a in ["endocrine", "antiHER2", "chemo"]:
    rs = by[a]; n = len(rs)
    mc = float(np.mean([r["cost"] for r in rs])) if n else float("nan")
    mis = float(np.mean([r["cost"] > 0 for r in rs])) if n else float("nan")
    drp = float(np.mean([r["dropped"] for r in rs])) if n else float("nan")
    axis_stat[a] = {"n": n, "mean_cost": round(mc, 3), "misroute_rate": round(mis, 3), "dropped_rate": round(drp, 3)}
    print(f"{a:12} {n:4d} {mc:10.3f} {mis*100:10.1f}% {drp*100:8.1f}%")

# 헤드라인 contrast: antiHER2 - endocrine, bootstrap 95% CI
he = np.array([r["cost"] for r in by["antiHER2"]]); en = np.array([r["cost"] for r in by["endocrine"]])
boots = [rng.choice(he, len(he)).mean() - rng.choice(en, len(en)).mean() for _ in range(2000)]
lo, hi = np.percentile(boots, [2.5, 97.5])
contrast = float(he.mean() - en.mean())
print(f"\n[헤드라인] cost(antiHER2) - cost(endocrine) = {contrast:.3f}  95%CI [{lo:.3f}, {hi:.3f}]"
      f"  → CI가 0 배제: {'YES(반증 통과)' if lo > 0 else 'NO'}")

outB = {
    "exp": "C1_cost_step2B_patient_routing_PAM50",
    "routing_source": "PAM50 CLAM-MB predictions_ext.npz (자기완결: proba/pred/label)",
    "note": ("PAM50 예측→치료축 라우팅. cost=오라우팅 시 치료거리(step2A). "
             "★ 모델이 HER2-enriched를 한 번도 예측 안 함 → 진짜 HER2 환자 전원 항HER2축 이탈. "
             "receptor-status 라우팅(ER 예측 수정 후, JIRA 11006)은 robustness로 병행 예정."),
    "n_routed": len(recs), "normal_like_excluded": int((meas == 4).sum()),
    "per_axis": axis_stat,
    "headline_contrast_antiHER2_minus_endocrine": {"value": round(contrast, 3),
        "ci95": [round(float(lo), 3), round(float(hi), 3)], "excludes_zero": bool(lo > 0)},
    "caveat": ["PAM50-축 매핑(HER2E≈antiHER2)은 receptor-status와 근사", "Normal-like 예측=무치료 최대페널티 처리", "단일 라우팅(PAM50); ER/HER2 receptor 라우팅 병행 필요"],
}
(HERE / "patient_routing_cost.json").write_text(json.dumps(outB, indent=2, ensure_ascii=False))
print("\nwrote patient_routing_cost.json")

# ============================================================
# (B') receptor-status 라우팅 — sjpark 예측(slide_id 인덱스) 도착 즉시 자동 실행
#   기대 입력(sjpark 제공, JIRA BIOP02-53 11006):
#     experiments/sjpark/cptac_ext_predictions_indexed.csv
#     컬럼: slide_id, er_pred_prob, her2_pred_prob  (0~1 확률; PR/PAM50 있으면 무시 안 함)
#   측정 라벨: 승격된 CPTAC 매니페스트(er/her2 = "Positive"/"Negative", has_er/has_her2)
#   라우팅(임상 계층): HER2+ -> antiHER2 ; elif ER+ -> endocrine ; else -> chemo
# ============================================================
import csv as _csv
PRED_CSV = HERE.parent.parent / "sjpark" / "cptac_ext_predictions_indexed.csv"
MANIFEST = Path("/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv")

def route(er_pos, her2_pos):
    if her2_pos: return "antiHER2"
    if er_pos:   return "endocrine"
    return "chemo"

print("\n=== (B') receptor-status 라우팅 (sjpark slide_id-indexed 예측) ===")
if not PRED_CSV.exists():
    print(f"AWAITING sjpark predictions: {PRED_CSV}")
    print("  (JIRA BIOP02-53 comment 11006 — ER 예측 재생성 + slide_id 인덱스 도착 시 자동 실행)")
    print("  기대 컬럼: slide_id, er_pred_prob, her2_pred_prob")
else:
    meas = {r["slide_id"]: r for r in _csv.DictReader(open(MANIFEST))}
    preds = {r["slide_id"]: r for r in _csv.DictReader(open(PRED_CSV))}
    THR = 0.5
    rr = []
    for sid, pr in preds.items():
        m = meas.get(sid)
        if not m or m.get("has_er") != "1" or m.get("has_her2") != "1":
            continue
        m_axis = route(m["er"] == "Positive", m["her2"] == "Positive")
        p_axis = route(float(pr["er_pred_prob"]) >= THR, float(pr["her2_pred_prob"]) >= THR)
        rr.append({"true_axis": m_axis, "pred_axis": p_axis, "cost": tdist(m_axis, p_axis)})
    byr = collections.defaultdict(list)
    for r in rr: byr[r["true_axis"]].append(r)
    print(f"n routed = {len(rr)} (has_er & has_her2)")
    stat = {}
    for a in ["endocrine", "antiHER2", "chemo"]:
        rs = byr[a]; n = len(rs)
        mc = float(np.mean([r["cost"] for r in rs])) if n else float("nan")
        mis = float(np.mean([r["cost"] > 0 for r in rs])) if n else float("nan")
        stat[a] = {"n": n, "mean_cost": round(mc, 3), "misroute_rate": round(mis, 3)}
        print(f"  {a:10} n={n:4d} mean_cost={mc:.3f} mis-route={mis*100:.1f}%")
    he = np.array([r["cost"] for r in byr["antiHER2"]]); en = np.array([r["cost"] for r in byr["endocrine"]])
    if len(he) and len(en):
        boots = [rng.choice(he, len(he)).mean() - rng.choice(en, len(en)).mean() for _ in range(2000)]
        lo, hi = np.percentile(boots, [2.5, 97.5]); ct = float(he.mean() - en.mean())
        print(f"  [헤드라인] cost(antiHER2)-cost(endocrine)={ct:.3f} 95%CI[{lo:.3f},{hi:.3f}] "
              f"0배제:{'YES' if lo>0 else 'NO'}")
        stat["headline_contrast"] = {"value": round(ct, 3), "ci95": [round(float(lo), 3), round(float(hi), 3)], "excludes_zero": bool(lo > 0)}
    (HERE / "patient_routing_cost_receptor.json").write_text(
        json.dumps({"exp": "C1_step2B_receptor_routing", "routing": "HER2+>antiHER2; ER+>endocrine; else chemo",
                    "pred_source": str(PRED_CSV), "per_axis": stat}, indent=2, ensure_ascii=False))
    print("  wrote patient_routing_cost_receptor.json")

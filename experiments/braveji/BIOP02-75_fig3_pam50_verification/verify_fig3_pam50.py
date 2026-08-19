"""Fig 3 PAM50 라우팅 — 환자단위 CI 독립 재계산 (braveji Critic, BIOP02-75).

검증 대상: experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost.json
  (owner=kkkim, 커밋 83da89d 에서 슬라이드→환자 클러스터 부트스트랩으로 교체)

Owner≠Reviewer: 생산 스크립트를 import·호출하지 않고, 커밋된 예측 CSV와
therapeutic_distance.json 에서 **규칙을 재구현**해 산출한 뒤 저장값과 대조한다.
`cost` 컬럼도 읽지 않고 규칙에서 다시 만든다(순환 검증 방지).

⚠️ 다음 리뷰어를 위한 함정 두 가지 — 내가 실제로 둘 다 밟았다:

  1) **파일이 둘이다.** `pam50_clam_mb_uni_v1/`(5-class, Normal-like 포함)과
     `pam50_clam_mb_uni_v1_4class/`(4-class). JSON 이 쓰는 것은 **v1(5-class)**이고
     JSON `indexed_predictions` 필드가 그 경로를 명시한다. 4class 로 계산하면
     per-axis n(220/39/123)은 맞는데 cost 가 전부 어긋난다 — 라벨이 같아
     "거의 맞는" 착시가 생기니 주의.
  2) **무치료 페널티는 '전역 최대'다.** JSON note 의 "Normal-like 예측=무치료
     최대페널티"는 (a) true 축 기준 최대 (b) 전역 최대 로 읽힐 수 있다. 실제는
     **(b) 0.765**. (a)로 읽으면 antiHER2·chemo 는 우연히 맞고 **endocrine 만**
     0.357 vs 0.378 로 어긋난다(차이 = 0.765−0.695 = 0.07).

Run (repo 루트):
    python3 experiments/braveji/BIOP02-75_fig3_pam50_verification/verify_fig3_pam50.py
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PRED = ROOT / "experiments/sjpark/pam50_clam_mb_uni_v1/predictions_ext_indexed.csv"
TARGET = ROOT / "experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost.json"
DISTJ = ROOT / "experiments/kkkim/20260710_cost_of_substitution/therapeutic_distance.json"
AXES = ["endocrine", "antiHER2", "chemo"]
B, SEED = 5000, 42
N_TOTAL_WITH_NORMAL = 395  # v1 npz 행수 — normal_like_excluded 검증용


def load_distance():
    d = json.loads(DISTJ.read_text())["axis_pair_distance"]
    D = {}
    for key, v in d.items():
        a, b = key.split("__")
        D[(a, b)] = D[(b, a)] = v["therapeutic_distance"]
    return D


def main():
    D = load_distance()
    global_max = max(D.values())          # 무치료 페널티 (함정 2)

    def dist(a, b):
        return 0.0 if a == b else D[(a, b)]

    def cost_of(true_ax, pred_ax):
        return global_max if pred_ax.startswith("none") else dist(true_ax, pred_ax)

    rows, stored_cost = [], []
    for r in csv.DictReader(PRED.open()):
        rows.append((r["case_id"], r["true_axis"], r["pred_axis"],
                     cost_of(r["true_axis"], r["pred_axis"])))
        stored_cost.append(float(r["cost"]))

    case = np.array([r[0] for r in rows])
    true_ax = np.array([r[1] for r in rows])
    pred_ax = np.array([r[2] for r in rows])
    cost = np.array([r[3] for r in rows])

    # 선행: 규칙 재구현이 저장된 cost 컬럼과 같은가(같아야 이후 비교가 의미 있다)
    max_diff = float(np.abs(cost - np.array(stored_cost)).max())

    rng = np.random.default_rng(SEED)
    pats = sorted(set(case))
    idx = {p: np.where(case == p)[0] for p in pats}
    draws = []
    for _ in range(B):
        i = np.concatenate([idx[p] for p in rng.choice(pats, len(pats), replace=True)])
        a2, c2 = true_ax[i], cost[i]
        if (a2 == "antiHER2").sum() == 0 or (a2 == "endocrine").sum() == 0:
            continue
        d = {t: (c2[a2 == t].mean() if (a2 == t).sum() else np.nan) for t in AXES}
        d["hc"] = c2[a2 == "antiHER2"].mean() - c2[a2 == "endocrine"].mean()
        draws.append(d)

    def ci(key):
        v = np.array([x[key] for x in draws], dtype=float)
        v = v[~np.isnan(v)]
        return [round(float(z), 4) for z in np.percentile(v, [2.5, 97.5])]

    C = json.loads(TARGET.read_text())
    pj, hj = C["per_axis"], C["headline_contrast_antiHER2_minus_endocrine"]
    fails = []

    def chk(label, got, want, tol=0.0):
        if isinstance(got, list):
            m = len(got) == len(want) and all(abs(x - y) <= tol for x, y in zip(got, want))
        elif isinstance(got, (int, float)):
            m = abs(got - want) <= tol
        else:
            m = got == want
        if not m:
            fails.append(label)
        print(f"{'✅' if m else '❌'} {label}: 재계산 {got} | 커밋 {want}")

    n_s = len(rows)
    print(f"n_slides={n_s} n_patients={len(pats)} ({n_s/len(pats):.2f}장/환자)")
    print(f"[선행] 규칙 재산출 cost vs 저장 cost 컬럼 최대차: {max_diff:.2e}\n")

    chk("n_slides", n_s, C["ci_method"]["n_slides"])
    chk("n_patients", len(pats), C["ci_method"]["n_patients"])
    chk("n_routed", n_s, C["n_routed"])
    chk("normal_like_excluded", N_TOTAL_WITH_NORMAL - n_s, C["normal_like_excluded"])
    for t in AXES:
        m = true_ax == t
        chk(f"{t}.n", int(m.sum()), pj[t]["n"])
        chk(f"{t}.mean_cost", round(float(cost[m].mean()), 4), pj[t]["mean_cost"], 0.0006)
        chk(f"{t}.misroute_rate", round(float(1 - (pred_ax[m] == t).mean()), 3),
            pj[t]["misroute_rate"], 0.002)
        chk(f"{t}.dropped_rate",
            round(float(np.char.startswith(pred_ax[m].astype(str), "none").mean()), 3),
            pj[t]["dropped_rate"], 0.002)
        chk(f"{t}.mean_cost_ci95_patient", ci(t), pj[t]["mean_cost_ci95_patient"], 0.008)
    chk("headline_contrast",
        round(float(cost[true_ax == "antiHER2"].mean() - cost[true_ax == "endocrine"].mean()), 4),
        hj["value"], 0.0006)
    chk("headline ci95 (환자단위)", ci("hc"), hj["ci95"], 0.008)
    chk("excludes_zero", bool(ci("hc")[0] > 0), hj["excludes_zero"])
    chk("ci_method.resample_unit", "patient", C["ci_method"]["resample_unit"].split()[0])
    chk("ci_method.n_bootstrap", B, C["ci_method"]["n_bootstrap"])
    chk("ci_method.seed", SEED, C["ci_method"]["seed"])

    total = 25
    print(f"\n>>> {total - len(fails)}/{total} 일치" + (f" | 불일치: {fails}" if fails else " — 전체 일치"))
    return 1 if (fails or max_diff > 0) else 0


if __name__ == "__main__":
    sys.exit(main())

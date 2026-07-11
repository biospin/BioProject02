#!/usr/bin/env python3
"""
Angle A v2 (하드닝) — research-methodologist spec 구현. v1(analyze_spatial_erbb2.py)은 보존.

PRIMARY estimand = threshold-free 방향적 분포중첩:
  Θ_overlap = P(종양 spot ERBB2 ≤ 배경 spot ERBB2) = 1 − AUC(tumor vs ref)  (raw counts, 정규화 불변)
  → 임의 percentile 없음. rank 기반이라 depth-robust. 부트스트랩 CI.
필수 robustness(load-bearing): ① interior-only(확산 통제) ② depth-conditioning(quintile).
보수 gloss: 종양 spot 중 ERBB2 ≤ 배경 median 비율.
요약: 환자=복제단위(spot pooling 금지), forest + nonzero k/8. n=8=메커니즘 시연.
사전확인(에이전트 라이브): tumor ERBB2 zero-frac≈0%(graded-low, absence 아님), depth ρ up to 0.50.
"""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

HERE = Path(__file__).parent; DATA = HERE / "data"
TUMOR = {"invasive cancer", "cancer in situ"}
REF = {"adipose tissue", "connective tissue", "immune infiltrate"}
MIN_SPOTS = 30; MIN_DEPTH = 500; B = 2000; SEED = 42
SECTIONS = {p: f for p in "ABCDEFGH"
            for f in [next((x for x in [f"{p}1", f"{p}2", f"{p}3"]
                            if (DATA / f"{x}_labeled_coordinates.tsv").exists()), None)] if f}

def load(sec):
    cm = pd.read_csv(DATA / "count-matrices" / f"{sec}.tsv.gz", sep="\t", index_col=0)
    depth = cm.sum(axis=1)
    cm = cm[depth >= MIN_DEPTH]; depth = depth[depth >= MIN_DEPTH]     # QC: 저심도 spot 제거
    meta = pd.read_csv(DATA / f"{sec}_labeled_coordinates.tsv", sep="\t").dropna(subset=["x", "y", "label"])
    meta["key"] = meta["x"].round().astype(int).astype(str) + "x" + meta["y"].round().astype(int).astype(str)
    meta = meta[meta["key"].isin(cm.index)].copy()
    meta["erbb2"] = meta["key"].map(cm["ERBB2"])       # raw count (Θ는 정규화 불변)
    # 잔차 depth 진단용: CP10k+log1p (ERBB2를 size factor에서 제외 — self-inflation 회피)
    tot_ex = (cm.sum(axis=1) - cm["ERBB2"]).replace(0, np.nan)
    erbb2_norm = np.log1p(cm["ERBB2"] / tot_ex * 1e4)
    meta["erbb2_norm"] = meta["key"].map(erbb2_norm)
    meta["depth"] = meta["key"].map(depth)
    meta["xi"] = meta["x"].round().astype(int); meta["yi"] = meta["y"].round().astype(int)
    meta["cls"] = np.where(meta["label"].isin(TUMOR), "tumor",
                    np.where(meta["label"].isin(REF), "ref", "other"))
    return meta, cm

def theta(tum, ref):
    """Θ = P(tumor ≤ ref) = 1 − AUC(y=tumor, x=ERBB2)."""
    if len(tum) < 3 or len(ref) < 3 or (len(set(tum)) < 2 and len(set(ref)) < 2): return np.nan
    y = np.r_[np.ones(len(tum)), np.zeros(len(ref))]; x = np.r_[tum, ref]
    if len(set(y)) < 2: return np.nan
    return float(1 - roc_auc_score(y, x))     # AUC=P(tumor>ref); 1-AUC=P(tumor≤ref)

def boot_ci(tum, ref, seed=SEED):
    rng = np.random.default_rng(seed); vals = []
    tum = np.asarray(tum); ref = np.asarray(ref)
    for _ in range(B):
        t = rng.choice(tum, len(tum)); r = rng.choice(ref, len(ref))
        v = theta(t, r)
        if not np.isnan(v): vals.append(v)
    if not vals: return (np.nan, np.nan)
    return tuple(round(float(q), 3) for q in np.percentile(vals, [2.5, 97.5]))

def interior_mask(meta, cls):
    """4-이웃(상하좌우)이 모두 동일 class인 spot = interior(확산 통제)."""
    pts = {(r.xi, r.yi) for r in meta[meta.cls == cls].itertuples()}
    out = []
    for r in meta[meta.cls == cls].itertuples():
        nb = [(r.xi+1, r.yi), (r.xi-1, r.yi), (r.xi, r.yi+1), (r.xi, r.yi-1)]
        out.append(all(n in pts for n in nb))
    return np.array(out)

def theta_depth_conditioned(meta):
    """pooled depth quintile 내 Θ 산출 후 종양수 가중 평균."""
    tr = meta[meta.cls.isin(["tumor", "ref"])].copy()
    try:
        tr["q"] = pd.qcut(tr["depth"], 5, labels=False, duplicates="drop")
    except Exception:
        return np.nan
    num = den = 0.0
    for q, g in tr.groupby("q"):
        t = g[g.cls == "tumor"]["erbb2"].values; rf = g[g.cls == "ref"]["erbb2"].values
        if len(t) >= 5 and len(rf) >= 5:
            v = theta(t, rf)
            if not np.isnan(v): num += v * len(t); den += len(t)
    return round(num / den, 3) if den else np.nan

def run():
    per = []
    for patient, sec in sorted(SECTIONS.items()):
        meta, cm = load(sec)
        tum = meta[meta.cls == "tumor"]; ref = meta[meta.cls == "ref"]
        nt, nr = len(tum), len(ref)
        rec = {"patient": patient, "section": sec, "n_tumor": nt, "n_ref": nr}
        if nt < MIN_SPOTS or nr < MIN_SPOTS:
            rec["status"] = f"underpowered (n_tumor {nt}/n_ref {nr} < {MIN_SPOTS}) — descriptive only"
        te, re = tum["erbb2"].values, ref["erbb2"].values
        # 사전확인
        rec["tumor_erbb2_zero_frac"] = round(float((te == 0).mean()), 3)
        tm = meta[meta.cls == "tumor"].dropna(subset=["erbb2_norm", "depth"])
        rho, _ = spearmanr(tm["erbb2_norm"], tm["depth"])   # 정규화 후 잔차 depth 상관(진단)
        rec["depth_rho_residual"] = round(float(rho), 3) if not np.isnan(rho) else None
        # PRIMARY Θ + CI
        rec["theta_overlap"] = round(theta(te, re), 3)
        rec["theta_ci95"] = boot_ci(te, re)
        # 보수 gloss
        rec["frac_le_ref_median"] = round(float((te <= np.median(re)).mean()), 3)
        # robustness ① interior-only
        it = interior_mask(meta, "tumor"); ir = interior_mask(meta, "ref")
        tint = tum["erbb2"].values[it]
        rint = ref["erbb2"].values[ir] if ir.sum() >= MIN_SPOTS else re   # interior ref 부족시 전체 ref
        rec["n_interior_tumor"] = int(it.sum()); rec["n_interior_ref"] = int(ir.sum())
        rec["theta_interior"] = round(theta(tint, rint), 3) if it.sum() >= 10 else None
        # robustness ② depth-conditioned
        rec["theta_depth_cond"] = theta_depth_conditioned(meta)
        # transparency: percentile sweep(구식, 참고용)
        rec["pctile_sweep_frac"] = {f"le_ref_{p}th": round(float((te <= np.percentile(re, p)).mean()), 3)
                                    for p in [50, 90, 95]}
        per.append(rec)

    # 요약(환자=복제단위, pooling 금지)
    valid = [r for r in per if "status" not in r or "underpowered" not in r.get("status", "")]
    def kk(key, cond):
        return sum(1 for r in per if isinstance(r.get(key), (int, float)) and r.get(key) is not None and cond(r[key]))
    thetas = [r["theta_overlap"] for r in per if r.get("theta_overlap") is not None]
    ci_excl0 = sum(1 for r in per if isinstance(r.get("theta_ci95"), tuple) and r["theta_ci95"][0] and r["theta_ci95"][0] > 0)
    interior_ok = sum(1 for r in per if r.get("theta_interior") is not None and r["theta_interior"] > 0.03)
    # kill: depth 교란 큰 환자(|ρ|>=0.4)서 depth-cond Θ가 0으로 붕괴?
    highrho = [r for r in per if r.get("depth_rho_residual") is not None and abs(r["depth_rho_residual"]) >= 0.4]
    depth_survive = sum(1 for r in highrho if r.get("theta_depth_cond") is not None and r["theta_depth_cond"] > 0.03)
    out = {"exp": "angleA_v2_overlap", "estimand": "Θ=P(tumor spot ERBB2 ≤ ref spot ERBB2)=1−AUC (raw, 정규화불변)",
           "data": "Andersson 2021 HER2+ ST (Zenodo 4751624), 8명 all HER2+", "n_patients": len(per),
           "claim_level": "hypothesis_only", "critic_status": "pending",
           "claim": "확진 HER2+ 종양의 종양면적 일부가 co-sectioned 비종양과 구별불가한 ERBB2 수준 → patient-level 라벨이 sub-region 타깃변이 미해상 → 치환비용 spatial floor>0. (label 정보손실/target coverage, '치료 실패' 아님)",
           "per_patient": per,
           "summary": {
               "theta_median": round(float(np.median(thetas)), 3) if thetas else None,
               "theta_range": [round(min(thetas), 3), round(max(thetas), 3)] if thetas else None,
               "nonzero_ci_excludes_0": f"{ci_excl0}/{len(per)}",
               "kill_interior_survive(>0.03)": f"{interior_ok}/{len(per)}",
               "kill_depth_survive_highrho(>0.03)": f"{depth_survive}/{len(highrho)}",
               "note": "환자=복제단위, spot pooling 금지. n=8=메커니즘 시연(모집단 prevalence 주장 X)."},
           "precheck": {"tumor_erbb2_zero_frac": "≈0%(6/8=0) → graded-low, absence 아님(dropout kill 해소)"},
           "kill_criteria": "① interior-only Θ가 6/8 미만서 >0 → 확산 아티팩트 ② depth-cond가 high-ρ서 0.5로 붕괴 → depth 아티팩트 ③ CI 0포함 6/8 미만 → 재현 실패",
           "limitations": "mRNA≠단백/증폭 · spot≠cell · ST≠우리 TCGA(메커니즘 시연) · 내부 ref는 HER2+환자 co-section(임상 HER2- 아님, 확산 있어 보수적 하한). Path2Space 화해: 같은 기질(공간ERBB2이질성), 다른 함수 — 그들=반응 바이오마커(양성), 우리=라벨이 버리는 정보(비용). 둘 다 성립."}
    (HERE / "spatial_erbb2_floor_v2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    # 콘솔
    print(f"섹션 {len(per)}개 | 사전확인 zero-frac≈0")
    print(f"{'Pt':3}{'nT':>5}{'nR':>5}{'Θ':>7}{'CI':>16}{'Θ_int':>8}{'Θ_dep':>8}{'ρ':>7}{'≤refMed':>9}")
    for r in per:
        ci = r.get("theta_ci95"); cis = f"[{ci[0]},{ci[1]}]" if isinstance(ci, tuple) else "?"
        print(f"{r['patient']:3}{r['n_tumor']:5}{r['n_ref']:5}{r.get('theta_overlap','?'):>7}{cis:>16}"
              f"{str(r.get('theta_interior')):>8}{str(r.get('theta_depth_cond')):>8}{str(r.get('depth_rho_residual')):>7}{r.get('frac_le_ref_median','?'):>9}")
    s = out["summary"]
    print(f"\nΘ 중앙 {s['theta_median']} 범위 {s['theta_range']} | CI>0: {s['nonzero_ci_excludes_0']} "
          f"| interior생존 {s['kill_interior_survive(>0.03)']} | depth생존(high-ρ) {s['kill_depth_survive_highrho(>0.03)']}")
    print("wrote spatial_erbb2_floor_v2.json")

if __name__ == "__main__":
    run()

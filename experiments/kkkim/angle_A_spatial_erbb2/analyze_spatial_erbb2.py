#!/usr/bin/env python3
"""
Angle A — 공간 ERBB2 이질성 = 치환비용의 irreducible floor (Paper A HER2 결과 강화).

데이터: Andersson 2021 HER2+ ST (Zenodo 4751624, 8명 A-H 주석섹션). 전원 임상 HER2+(환자수준).
방법: 각 종양에서 비종양 spot(adipose/connective/immune)을 내부 HER2-음성 레퍼런스로 삼아
      배경 ERBB2 역치(비종양 90th pct) 산출 → "종양 spot 중 ERBB2가 배경 이하인 면적%".
논지: 확진 HER2+ 종양에서도 종양 면적 일부가 HER2-음성 배경 수준 → 환자수준 라벨이 못 담음
      = 어떤 patient-level 예측기(H&E든 IHC든)도 복원 불가한 치환비용 하한(floor).
⚠️ 한계: ST 코호트(우리 TCGA 아님)=메커니즘 시연. Path2Space는 같은 이질성을 '좋은 예측신호'로 씀(반대해석).
"""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"
TUMOR = {"invasive cancer", "cancer in situ"}
REF = {"adipose tissue", "connective tissue", "immune infiltrate"}   # 비종양 = HER2- 배경 레퍼런스

# 주석섹션(환자 A-H). G는 G2가 주석섹션.
SECTIONS = {p: f for p in "ABCDEFGH"
            for f in [next((x for x in [f"{p}1", f"{p}2", f"{p}3"]
                            if (DATA / f"{x}_labeled_coordinates.tsv").exists()), None)] if f}

def load(sec):
    cm = pd.read_csv(DATA / "count-matrices" / f"{sec}.tsv.gz", sep="\t", index_col=0)
    meta = pd.read_csv(DATA / f"{sec}_labeled_coordinates.tsv", sep="\t")
    meta = meta.dropna(subset=["x", "y", "label"]).copy()   # 좌표/라벨 결측 spot 제외
    meta["key"] = meta["x"].round().astype(int).astype(str) + "x" + meta["y"].round().astype(int).astype(str)
    meta = meta[meta["key"].isin(cm.index)].copy()
    # ERBB2 정규화: CP10k + log1p (표준 ST)
    tot = cm.sum(axis=1).replace(0, np.nan)
    erbb2 = np.log1p(cm["ERBB2"] / tot * 1e4)
    meta["erbb2"] = meta["key"].map(erbb2)
    return meta.dropna(subset=["erbb2"])

def analyze(pct=90):
    rows = []
    for patient, sec in sorted(SECTIONS.items()):
        m = load(sec)
        tum = m[m["label"].isin(TUMOR)]
        ref = m[m["label"].isin(REF)]
        if len(tum) < 10 or len(ref) < 5:
            rows.append({"patient": patient, "section": sec, "n_tumor": len(tum),
                         "n_ref": len(ref), "note": "레퍼런스/종양 spot 부족(신뢰 낮음)"})
            continue
        thr = np.percentile(ref["erbb2"], pct)          # 배경 상한
        low_frac = float((tum["erbb2"] <= thr).mean())
        rows.append({
            "patient": patient, "section": sec, "n_tumor": int(len(tum)), "n_ref": int(len(ref)),
            "erbb2_bg_thr(log)": round(float(thr), 3),
            "tumor_erbb2_median(log)": round(float(tum["erbb2"].median()), 3),
            "ref_erbb2_median(log)": round(float(ref["erbb2"].median()), 3),
            "low_erbb2_tumor_area_frac": round(low_frac, 3),   # ★ floor
        })
    return rows

def main():
    out = {"exp": "angleA_spatial_erbb2_floor",
           "data": "Andersson 2021 HER2+ ST (Zenodo 4751624), 8 patients, all clinical HER2+",
           "method": f"비종양 spot 배경 90th pct 역치 이하인 종양 면적% (CP10k+log1p ERBB2)",
           "claim_level": "hypothesis_only", "critic_status": "pending",
           "caveat": ["ST 코호트=메커니즘 시연(우리 TCGA 아님)",
                      "Path2Space는 HER2 이질성을 좋은 예측신호로 사용(반대해석) — 서사충돌 관리",
                      "spot=morphology area proxy, 세포수 아님"]}
    for pct in [90, 95, 50]:
        rows = analyze(pct)
        valid = [r for r in rows if "low_erbb2_tumor_area_frac" in r]
        fracs = [r["low_erbb2_tumor_area_frac"] for r in valid]
        out[f"threshold_{pct}pct"] = {
            "per_patient": rows,
            "summary": {"n_patients": len(valid),
                        "median_low_frac": round(float(np.median(fracs)), 3) if fracs else None,
                        "range": [round(min(fracs), 3), round(max(fracs), 3)] if fracs else None}}
    (HERE / "spatial_erbb2_floor.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"섹션: {dict(SECTIONS)}")
    for pct in [90, 95, 50]:
        s = out[f"threshold_{pct}pct"]["summary"]
        print(f"[배경 {pct}th pct 역치] {s['n_patients']}명 종양area ERBB2<=배경: "
              f"중앙 {s['median_low_frac']*100 if s['median_low_frac'] else 0:.0f}% (범위 "
              f"{s['range'][0]*100 if s['range'] else 0:.0f}-{s['range'][1]*100 if s['range'] else 0:.0f}%)")
    print("\n[배경 90th] 환자별:")
    for r in out["threshold_90pct"]["per_patient"]:
        if "low_erbb2_tumor_area_frac" in r:
            print(f"  {r['patient']}: 종양{r['n_tumor']}/ref{r['n_ref']} "
                  f"low-ERBB2 area={r['low_erbb2_tumor_area_frac']*100:.0f}% "
                  f"(tumor median {r['tumor_erbb2_median(log)']} vs ref {r['ref_erbb2_median(log)']})")
        else:
            print(f"  {r['patient']}: {r.get('note')}")
    print("\nwrote spatial_erbb2_floor.json")

if __name__ == "__main__":
    main()

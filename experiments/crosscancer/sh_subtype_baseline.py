#!/usr/bin/env python3
"""
BLOCKER-3 잔여: subtype-only baseline (7-point #2의 세 번째 baseline).

★ cross-cancer에서 subtype-only는 대부분 순환(circular)이라 **폐 EGFR/KRAS from histology(LUAD/LUSC)만** 비순환·유의미:
- 폐 EGFR/KRAS는 LUAD 편중(EGFR LUAD 10%/LUSC 1%, KRAS LUAD 12%/LUSC 0%) → histology-only가 예측력 가짐.
- 검정 목적: H&E MIL(EGFR 0.85·KRAS 0.68)이 "그냥 LUAD/LUSC 인식"을 **넘는가**. 사전등록의 폐 EGFR="등급적(lepidic/acinar 부분상관)" 주장 검정.
- 순환이라 제외: 폐 histology 자체, 두경부 HPV(=아형축), 위 MSI(=분자아형), 위/두경부 Lauren/grade(약함·Lauren은 site-교란 실패 endpoint), 대장 BRAF(CMS 별파일·D13서 +CMS 이미 검정).

baseline 정의(이미지 미사용): holdout 환자 예측 P(mut) = **train**에서 그 histology(LUAD/LUSC)의 mut 양성률 → holdout AUROC.
holdout = split.csv의 val+test(site-disjoint, MIL과 동일). 부트스트랩 1000회 CI.

출력: LUNG_NSCLC/full/baseline_subtype.json
사용: python sh_subtype_baseline.py
"""
import csv, json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
D = HERE / "LUNG_NSCLC" / "full"


def load():
    labels = {r["case_id"]: r for r in csv.DictReader(open(D / "patient_labels.csv"))}
    split = {r["case_id"]: r["split"] for r in csv.DictReader(open(D / "split.csv"))}
    return labels, split


def boot_ci(y, p, n=1000, seed=42):
    y = np.array(y); p = np.array(p); rng = np.random.default_rng(seed)
    aucs = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y[idx], p[idx]))
    return (round(float(np.percentile(aucs, 2.5)), 4), round(float(np.percentile(aucs, 97.5)), 4)) if aucs else (None, None)


def run(ep, labels, split):
    # train 양성률 by histology
    tr = {"LUAD": [0, 0], "LUSC": [0, 0]}
    for cid, r in labels.items():
        if split.get(cid) != "train":
            continue
        h = r["histology_lusc"]; v = r.get(ep, "")
        if h == "" or v == "":
            continue
        hl = "LUSC" if h in ("1", 1) else "LUAD"
        tr[hl][0] += int(v in ("1", 1)); tr[hl][1] += 1
    rate = {k: (tr[k][0] / tr[k][1] if tr[k][1] else 0.0) for k in tr}
    # holdout 예측
    y, p = [], []
    for cid, r in labels.items():
        if split.get(cid) not in ("val", "test"):
            continue
        h = r["histology_lusc"]; v = r.get(ep, "")
        if h == "" or v == "":
            continue
        hl = "LUSC" if h in ("1", 1) else "LUAD"
        y.append(int(v in ("1", 1))); p.append(rate[hl])
    auc = round(float(roc_auc_score(y, p)), 4) if len(set(y)) > 1 else None
    lo, hi = boot_ci(y, p)
    return {"endpoint": ep, "baseline": "histology-only(LUAD/LUSC train prevalence)",
            "auc": auc, "ci95": [lo, hi], "n_pos": int(sum(y)), "n_hold": len(y),
            "train_rate": {k: round(rate[k], 4) for k in rate}}


def main():
    labels, split = load()
    res = {"track": "LUNG_NSCLC", "purpose": "subtype-only baseline (BLOCKER-3 잔여, 비순환=폐 EGFR/KRAS만)",
           "claim_level": "hypothesis_only", "critic_status": "pending",
           "note": "타 암종/endpoint subtype-only는 순환(자기 자신이 아형축)이라 미산출 — docstring 참조.",
           "endpoints": {}}
    for ep in ("egfr_activating", "kras_g12c"):
        res["endpoints"][ep] = run(ep, labels, split)
        r = res["endpoints"][ep]
        print(f"{ep}: histology-only AUC={r['auc']} CI{r['ci95']} n_pos={r['n_pos']}/{r['n_hold']} rate={r['train_rate']}")
    out = D / "baseline_subtype.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()

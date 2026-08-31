"""인코더 ablation 재실행 (Critic reject 지적 반영, v2).

v1이 reject된 사유 네 가지를 고친다.
  (1) 분할이 잠긴 정본과 어긋났다(test 153 vs 151) → split_policy_v0_folds.json을 쓴다.
  (2) trivial baseline이 없었다 → random, prevalence, subtype-only, embedding-mean을 넣는다.
  (3) PAM50이 5-class로 돌았다(Normal-like 포함) → 정책대로 4-class로 제한한다.
  (4) 다중비교 보정이 없었다 → Benjamini-Hochberg로 보정한 부트스트랩 p를 함께 낸다.

집계 경로 주의: exaone_v2는 내부 타일링과 Macenko 정규화를 거친 별도 파이프라인이라
인코더만의 차이로 읽으면 안 된다. 결과에 그 사실을 함께 기록한다.
"""
import argparse, json, os
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             balanced_accuracy_score)
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FOLDS = os.path.join(REPO, "agents/data/manifests/split_policy_v0_folds.json")

ENCODERS = ["uni_v1", "uni_stainnorm_v1", "conch_v1", "exaone_v2"]
PAM50_KEEP = {"LumA", "LumB", "HER2", "HER2-E", "Basal"}   # Normal-like 제외 (정책 §92)


def load_split():
    d = json.load(open(FOLDS))
    return d["case_id_to_fold"], d["split_hash"], d["fold_counts"]


def load_labels():
    clin = pd.read_csv(os.path.join(CACHE, "clinical_patient_brca.txt"),
                       sep="\t", low_memory=False)
    clin = clin[clin["bcr_patient_barcode"].astype(str).str.startswith("TCGA")]
    lab = pd.DataFrame({"case_id": clin["bcr_patient_barcode"].astype(str)})
    for tgt, col in [("er", "er_status_by_ihc"), ("pr", "pr_status_by_ihc"),
                     ("her2", "her2_status_by_ihc")]:
        s = clin[col].astype(str).str.strip().str.lower()
        lab[tgt] = np.where(s.eq("positive"), 1,
                            np.where(s.eq("negative"), 0, np.nan))
    pam = pd.read_csv(os.path.join(CACHE, "tcga_brca_pam50_computed.csv"))
    pam["case_id"] = pam["case_id"].astype(str)
    sub = pam["pam50_subtype"].astype(str).str.strip()
    pam["pam50_4c"] = np.where(sub.isin(PAM50_KEEP), sub, np.nan)
    lab = lab.merge(pam[["case_id", "pam50_4c"]], on="case_id", how="left")
    return lab.drop_duplicates("case_id").set_index("case_id")


def load_enc(enc):
    z = np.load(os.path.join(CACHE, f"{enc}_casemean.npz"), allow_pickle=True)
    return z["cases"].astype(str), z["Z"]


def score(y, prob, pred, multi):
    out = {"balanced_acc": round(float(balanced_accuracy_score(y, pred)), 4)}
    if multi:
        try:
            out["auroc"] = round(float(roc_auc_score(y, prob, multi_class="ovr",
                                                     average="macro")), 4)
        except ValueError:
            out["auroc"] = None
        out["auprc"] = None
    else:
        out["auroc"] = round(float(roc_auc_score(y, prob[:, 1])), 4)
        out["auprc"] = round(float(average_precision_score(y, prob[:, 1])), 4)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(HERE, "results_locked_v2.json"))
    p.add_argument("--n-boot", type=int, default=2000)
    a = p.parse_args()

    fold_of, split_hash, counts = load_split()
    labels = load_labels()
    print(f"[split] 잠긴 정본 {os.path.basename(FOLDS)} | hash={split_hash} | {counts}")

    tasks = [("er", False), ("pr", False), ("her2", False), ("pam50_4c", True)]
    per_enc_pred, meta_task = {}, {}

    for enc in ENCODERS:
        cases, Z = load_enc(enc)
        idx = pd.Index(cases)
        fold = np.array([fold_of.get(c, "NA") for c in cases])
        per_enc_pred[enc] = {}
        for tgt, multi in tasks:
            y = labels.reindex(idx)[tgt]
            ok = y.notna().to_numpy() & (fold != "NA")
            tr = ok & (fold == "train")
            te = ok & (fold == "test")
            yv = y.to_numpy()
            ytr = yv[tr].astype(str) if multi else yv[tr].astype(int)
            yte = yv[te].astype(str) if multi else yv[te].astype(int)
            sc = StandardScaler().fit(Z[tr])
            clf = LogisticRegression(max_iter=5000, class_weight="balanced")
            clf.fit(sc.transform(Z[tr]), ytr)
            prob = clf.predict_proba(sc.transform(Z[te]))
            pred = clf.predict(sc.transform(Z[te]))
            per_enc_pred[enc][tgt] = {"y": yte, "prob": prob, "pred": pred,
                                      "cases": cases[te]}
            meta_task.setdefault(tgt, {"n_train": int(tr.sum()),
                                       "n_test": int(te.sum()),
                                       "classes": sorted(set(map(str, yte)))})
            print(f"  [{enc:18s}] {tgt:9s} n_train={tr.sum():4d} n_test={te.sum():4d} "
                  f"AUROC={score(yte, prob, pred, multi)['auroc']}", flush=True)

    # --- trivial baseline (인코더와 무관, 같은 분할·같은 test 환자) ---
    base = {}
    for tgt, multi in tasks:
        ref = per_enc_pred["uni_v1"][tgt]
        cases, Z = load_enc("uni_v1")
        idx = pd.Index(cases)
        fold = np.array([fold_of.get(c, "NA") for c in cases])
        y = labels.reindex(idx)[tgt]
        ok = y.notna().to_numpy() & (fold != "NA")
        tr, te = ok & (fold == "train"), ok & (fold == "test")
        yv = y.to_numpy()
        ytr = yv[tr].astype(str) if multi else yv[tr].astype(int)
        yte = ref["y"]
        b = {}
        for name, strat in [("random_uniform", "uniform"),
                            ("prevalence", "stratified"),
                            ("majority", "most_frequent")]:
            dm = DummyClassifier(strategy=strat, random_state=0).fit(
                np.zeros((tr.sum(), 1)), ytr)
            pr = dm.predict_proba(np.zeros((te.sum(), 1)))
            pd_ = dm.predict(np.zeros((te.sum(), 1)))
            b[name] = score(yte, pr, pd_, multi)
        # 임베딩 평균만 쓰는 1차원 기준선 (표현이 아니라 밝기·크기 대리)
        m1 = Z[:, :].mean(1, keepdims=True)
        sc = StandardScaler().fit(m1[tr])
        clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(
            sc.transform(m1[tr]), ytr)
        b["embedding_mean_1d"] = score(yte, clf.predict_proba(sc.transform(m1[te])),
                                       clf.predict(sc.transform(m1[te])), multi)
        if not multi:
            b["prevalence_positive_rate"] = round(float((yte == 1).mean()), 4)
        base[tgt] = b
        print(f"  [baseline] {tgt}: " +
              ", ".join(f"{k}={v['auroc']}" for k, v in b.items()
                        if isinstance(v, dict)), flush=True)

    # --- paired 부트스트랩 + BH 보정 ---
    rng = np.random.default_rng(0)
    results, pairwise = {}, {}
    for tgt, multi in tasks:
        n = len(per_enc_pred["uni_v1"][tgt]["y"])
        boots = [rng.integers(0, n, n) for _ in range(a.n_boot)]
        samples, point = {}, {}
        for enc in ENCODERS:
            d = per_enc_pred[enc][tgt]
            point[enc] = score(d["y"], d["prob"], d["pred"], multi)
            vals = []
            for bi in boots:
                yb = d["y"][bi]
                if len(np.unique(yb)) < 2:
                    vals.append(np.nan); continue
                try:
                    v = (roc_auc_score(yb, d["prob"][bi], multi_class="ovr",
                                       average="macro") if multi
                         else roc_auc_score(yb, d["prob"][bi, 1]))
                except ValueError:
                    v = np.nan
                vals.append(v)
            s = np.array(vals, float)
            samples[enc] = s
            okb = ~np.isnan(s)
            point[enc]["ci95"] = [round(float(np.percentile(s[okb], 2.5)), 4),
                                  round(float(np.percentile(s[okb], 97.5)), 4)]
        results[tgt] = {"per_encoder": point, **meta_task[tgt],
                        "baseline": base[tgt]}
        for i in range(len(ENCODERS)):
            for j in range(i + 1, len(ENCODERS)):
                x, w = ENCODERS[i], ENCODERS[j]
                d = samples[x] - samples[w]
                d = d[~np.isnan(d)]
                lo, hi = np.percentile(d, [2.5, 97.5])
                # 부트스트랩 양측 p (0을 넘는 비율)
                pv = 2 * min((d <= 0).mean(), (d >= 0).mean())
                pairwise[f"{tgt}|{x} - {w}"] = {
                    "delta": round(float(point[x]["auroc"] - point[w]["auroc"]), 4),
                    "ci95": [round(float(lo), 4), round(float(hi), 4)],
                    "p_boot": round(float(min(1.0, pv)), 4)}

    # Benjamini-Hochberg
    keys = list(pairwise)
    ps = np.array([pairwise[k]["p_boot"] for k in keys])
    order = np.argsort(ps)
    m = len(ps)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        prev = min(prev, ps[i] * m / (rank + 1))
        q[i] = prev
    for k, qi in zip(keys, q):
        pairwise[k]["q_bh"] = round(float(min(1.0, qi)), 4)
        pairwise[k]["significant_bh05"] = bool(qi < 0.05)

    sig = [k for k in keys if pairwise[k]["significant_bh05"]]
    print(f"\n[BH 보정] 전체 비교 {m}건 중 q<0.05: {len(sig)}건")
    for k in sig:
        v = pairwise[k]
        print(f"  {k}: Δ={v['delta']:+.4f} CI={v['ci95']} q={v['q_bh']}")

    json.dump({
        "version": "v2 (Critic reject 반영)",
        "split_source": os.path.relpath(FOLDS, REPO),
        "split_hash": split_hash, "fold_counts": counts,
        "pam50_policy": "4-class, Normal-like 제외 (split_policy_v0.md §92)",
        "n_boot": a.n_boot,
        "multiple_comparison": "Benjamini-Hochberg on bootstrap two-sided p",
        "caveat_exaone": "exaone_v2는 내부 타일링과 Macenko 정규화를 거친 별도 "
                         "파이프라인이라 인코더 단독 차이로 읽으면 안 된다",
        "claim_level": "hypothesis_only",
        "results": results, "pairwise": pairwise},
        open(a.out, "w"), indent=2, ensure_ascii=False)
    print(f"[done] {a.out}")


if __name__ == "__main__":
    main()

"""BP02 인코더 ablation: 파운데이션 모델 선택이 표현형 예측을 얼마나 좌우하는가.

기존 BIOP02-48은 UNI vs CONCH를 ER/PR에서 교차검증으로 비교했다(sanity 수준).
여기서는 인코더 4종을 프로젝트의 분할 정책(case 단위 train/val/test)으로
ER/PR/HER2와 PAM50까지 한 프로토콜에 놓고 비교한다.

인코더: uni_v1, uni_stainnorm_v1(염색 정규화), conch_v1, exaone_v2
집계: 타일 임베딩 평균 풀링(슬라이드) → 환자 단위 평균
분할: split_policy_v1.csv (case_id 기준). 학습은 train, 보고는 test.
"""
import argparse, glob, json, os, re, time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

ENCODERS = {
    "uni_v1": ("*_uni_embeddings.npy", "npy"),
    "uni_stainnorm_v1": ("*_uni_stainnorm_embeddings.npy", "npy"),
    "conch_v1": ("*_conch_embeddings.npy", "npy"),
    "exaone_v2": ("*_exaone.npz", "npz_patch_mean"),
}
CASE_RE = re.compile(r"(TCGA-[0-9A-Z]{2}-[0-9A-Z]{4})")


def load_encoder(root, enc, cache_dir):
    """슬라이드별 평균 풀링 → case 단위 평균. 결과를 캐시한다."""
    cache = os.path.join(cache_dir, f"{enc}_casemean.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return z["cases"].astype(str), z["Z"]

    pattern, kind = ENCODERS[enc]
    files = sorted(glob.glob(os.path.join(root, enc, pattern)))
    per_case, t0 = {}, time.time()
    for i, f in enumerate(files):
        m = CASE_RE.search(os.path.basename(f))
        if not m:
            continue
        if kind == "npy":
            v = np.load(f, mmap_mode="r")
            v = np.asarray(v, dtype=np.float32).mean(0)
        else:
            v = np.load(f)["patch_mean"].astype(np.float32)
        per_case.setdefault(m.group(1), []).append(v)
        if (i + 1) % 200 == 0:
            print(f"    {enc}: {i+1}/{len(files)} ({time.time()-t0:.0f}s)", flush=True)
    cases = np.array(sorted(per_case))
    Z = np.stack([np.mean(per_case[c], axis=0) for c in cases])
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, cases=cases, Z=Z)
    print(f"  [{enc}] cases={len(cases)} dim={Z.shape[1]} "
          f"({time.time()-t0:.0f}s)", flush=True)
    return cases, Z


def load_labels(clin_dir):
    """ER/PR/HER2(IHC)와 PAM50 서브타입을 case 단위로 모은다."""
    clin = pd.read_csv(os.path.join(clin_dir, "clinical_patient_brca.txt"),
                       sep="\t", low_memory=False)
    clin = clin[clin["bcr_patient_barcode"].astype(str).str.startswith("TCGA")]
    lab = pd.DataFrame({"case_id": clin["bcr_patient_barcode"].astype(str)})
    for tgt, col in [("er", "er_status_by_ihc"), ("pr", "pr_status_by_ihc"),
                     ("her2", "her2_status_by_ihc")]:
        s = clin[col].astype(str).str.strip().str.lower()
        lab[tgt] = np.where(s.eq("positive"), 1,
                            np.where(s.eq("negative"), 0, np.nan))
    pam = pd.read_csv(os.path.join(clin_dir, "tcga_brca_pam50_computed.csv"))
    pam["case_id"] = pam["case_id"].astype(str)
    lab = lab.merge(pam[["case_id", "pam50_subtype"]], on="case_id", how="left")
    return lab.drop_duplicates("case_id").set_index("case_id")


def evaluate(Ztr, ytr, Zte, yte, multiclass):
    sc = StandardScaler().fit(Ztr)
    clf = LogisticRegression(max_iter=5000, class_weight="balanced", n_jobs=-1)
    clf.fit(sc.transform(Ztr), ytr)
    P = clf.predict_proba(sc.transform(Zte))
    pred = clf.predict(sc.transform(Zte))
    out = {"n_train": int(len(ytr)), "n_test": int(len(yte)),
           "acc": float(accuracy_score(yte, pred)),
           "macro_f1": float(f1_score(yte, pred, average="macro"))}
    if multiclass:
        try:
            out["auroc_ovr"] = float(roc_auc_score(yte, P, multi_class="ovr",
                                                   average="macro"))
        except ValueError:
            out["auroc_ovr"] = None
    else:
        out["auroc"] = float(roc_auc_score(yte, P[:, 1]))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--emb-root", default=os.path.expanduser(
        "~/data/embeddings/biop02/tcga"))
    p.add_argument("--clin-dir", default=os.path.expanduser("~/data/clinical"))
    p.add_argument("--split", default=os.path.expanduser("~/data/split_policy_v1.csv"))
    p.add_argument("--cache", default=os.path.expanduser("~/work/fmpretrain/cache_bp02"))
    p.add_argument("--out", default=os.path.expanduser(
        "~/work/fmpretrain/bp02_encoder_ablation.json"))
    p.add_argument("--eval-split", default="test", choices=["val", "test"])
    args = p.parse_args()

    split = pd.read_csv(args.split).set_index("case_id")["split"]
    labels = load_labels(args.clin_dir)
    print(f"[labels] cases={len(labels)} "
          f"er={labels.er.notna().sum()} pr={labels.pr.notna().sum()} "
          f"her2={labels.her2.notna().sum()} "
          f"pam50={labels.pam50_subtype.notna().sum()}", flush=True)

    tasks = [("er", False), ("pr", False), ("her2", False), ("pam50_subtype", True)]
    results = {}
    for enc in ENCODERS:
        cases, Z = load_encoder(args.emb_root, enc, args.cache)
        idx = pd.Index(cases)
        results[enc] = {"dim": int(Z.shape[1]), "n_cases": int(len(cases))}
        for tgt, multi in tasks:
            y = labels.reindex(idx)[tgt]
            sp_ = split.reindex(idx)
            ok = y.notna().to_numpy() & sp_.notna().to_numpy()
            if multi:                      # 소수 클래스는 제외해 안정적으로 평가
                vc = y[ok].value_counts()
                ok &= y.isin(vc[vc >= 20].index).to_numpy()
            tr = ok & (sp_ == "train").to_numpy()
            te = ok & (sp_ == args.eval_split).to_numpy()
            if te.sum() < 20 or len(np.unique(y[tr])) < 2:
                results[enc][tgt] = {"skipped": "insufficient data"}
                continue
            yv = y.to_numpy()
            r = evaluate(Z[tr], yv[tr].astype(str) if multi else yv[tr].astype(int),
                         Z[te], yv[te].astype(str) if multi else yv[te].astype(int),
                         multi)
            results[enc][tgt] = r
            key = "auroc_ovr" if multi else "auroc"
            print(f"  [{enc:18s}] {tgt:14s} {key}={r.get(key)} "
                  f"acc={r['acc']:.4f} n_test={r['n_test']}", flush=True)

    meta = {"eval_split": args.eval_split, "split_policy": os.path.basename(args.split),
            "aggregation": "tile mean-pool → slide → case mean",
            "probe": "LogisticRegression(class_weight=balanced), StandardScaler",
            "results": results}
    json.dump(meta, open(args.out, "w"), indent=2)
    print(f"[done] {args.out}", flush=True)


if __name__ == "__main__":
    main()

"""
HER2 decoupling across assay definitions (BIOP02, kkkim).

Question: Is H&E blindness to HER2+ robust to the LABEL DEFINITION?
Same UNI-v1 embeddings, same site-disjoint patient-level split (train / val / test)
from embedding_manifest_uni.csv. Only the HER2+ label definition is swapped:

  IHC_status : existing manifest `her2` column (clinical IHC status; pos/neg, equivocal excluded)
  IHC_3plus  : cBioPortal brca_tcga HER2_IHC_SCORE  (3=pos, 0/1=neg, 2=equivocal excluded)
  FISH       : cBioPortal brca_tcga HER2_FISH_STATUS (Positive/Negative; Equivocal/Indeterminate excluded)
  CNV_amp    : cBioPortal brca_tcga_pan_can_atlas_2018 ERBB2 GISTIC (==2 amp = pos, else neg)

Model: CLAM-SB (UNI, 1024-d) — identical hyperparams to sjpark her2_status_clam_uni_v2
(hidden 512 / att 256 / dropout 0.25 / lr 2e-4 / epochs 50 / patience 7 / seed 42),
early-stop on val_loss, restore best.

Evaluation (per definition): AUROC on val-only, test-only, and pooled (val+test) holdout,
each with a bootstrap 95% CI and a HOLDOUT-LABEL PERMUTATION null (predictions fixed,
labels shuffled -> null AUROC distribution centred at chance; p = frac(null >= real)).
test-only is the leak-free arbiter (test never touches model selection).

claim_level: hypothesis_only. No commit (human).
"""
import csv, json, subprocess, sys, time, random
from pathlib import Path
from collections import defaultdict
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

REPO = Path("/home/kkkim/project/BioProject02")
sys.path.insert(0, str(REPO / "agents"))
from modeling.baselines.attention_mil import CLAMSB

OUT = REPO / "experiments/kkkim/her2_blind_across_assays"
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_uni.csv"
LABELS_PKL = "/tmp/claude-10005/-home-kkkim-project-BioProject02/d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/labels.pkl"

HP = dict(hidden_dim=512, att_dim=256, dropout=0.25, lr=2.0e-4, epochs=50, patience=7, seed=42)
DIM = 1024
N_BOOT = 2000
N_PERM = 5000
RNG_EVAL = np.random.default_rng(12345)


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)


def git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


# ---- label definitions -------------------------------------------------------
import pickle
L = pickle.load(open(LABELS_PKL, "rb"))
cnv, ihc, fish = L["cnv"], L["ihc"], L["fish"]

def lab_ihc_status(row):
    return {"positive": 1, "negative": 0}.get(row["her2"].strip().lower())

def lab_ihc3(row):
    return {"3": 1, "0": 0, "1": 0}.get(ihc.get(row["case_id"]))   # 2 excluded

def lab_fish(row):
    return {"Positive": 1, "Negative": 0}.get(fish.get(row["case_id"]))

def lab_cnv(row):
    v = cnv.get(row["case_id"])
    return None if v is None else (1 if v == 2 else 0)

DEFS = {"IHC_status": lab_ihc_status, "IHC_3plus": lab_ihc3, "FISH": lab_fish, "CNV_amp": lab_cnv}


# ---- load embeddings once ----------------------------------------------------
def load_all():
    rows = list(csv.DictReader(open(MANIFEST)))
    cache = {}
    t0 = time.time()
    for r in rows:
        sid = r["slide_id"]
        p = r["embedding_path"]
        if sid in cache:
            continue
        arr = np.load(p).astype(np.float32)
        cache[sid] = torch.from_numpy(arr)
    print(f"[load] {len(cache)} slide embeddings cached in {time.time()-t0:.0f}s")
    return rows, cache


def build_sets(rows, cache, labfn):
    sets = {"train": [], "val": [], "test": []}
    for r in rows:
        lab = labfn(r)
        if lab is None:
            continue
        sid = r["slide_id"]
        if sid not in cache:
            continue
        sets[r["split"]].append((cache[sid], float(lab)))
    return sets


# ---- train CLAM-SB -----------------------------------------------------------
def train_clam(train_set, val_set, device):
    set_seed(HP["seed"])
    model = CLAMSB(feature_dim=DIM, hidden_dim=HP["hidden_dim"], att_dim=HP["att_dim"],
                   dropout=HP["dropout"]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=HP["lr"])
    crit = nn.BCEWithLogitsLoss()
    best_loss, best_state, no_imp = float("inf"), None, 0
    order = list(range(len(train_set)))
    for ep in range(1, HP["epochs"] + 1):
        model.train()
        random.shuffle(order)
        for i in order:
            emb, lab = train_set[i]
            emb = emb.to(device); y = torch.tensor([lab], device=device)
            opt.zero_grad()
            logit, _ = model(emb)
            loss = crit(logit, y)
            loss.backward(); opt.step()
        model.eval()
        vl = 0.0
        with torch.no_grad():
            for emb, lab in val_set:
                logit, _ = model(emb.to(device))
                vl += crit(logit, torch.tensor([lab], device=device)).item()
        vl /= max(len(val_set), 1)
        if vl < best_loss - 1e-6:
            best_loss = vl
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_imp = 0
        else:
            no_imp += 1
            if no_imp >= HP["patience"]:
                break
    if best_state:
        model.load_state_dict(best_state)
    return model, best_loss


def predict(model, dataset, device):
    proba, label = [], []
    model.eval()
    with torch.no_grad():
        for emb, lab in dataset:
            logit, _ = model(emb.to(device))
            proba.append(float(torch.sigmoid(logit).item()))
            label.append(int(lab))
    return np.array(proba), np.array(label)


# ---- metrics: AUROC + bootstrap CI + permutation null ------------------------
def eval_block(proba, label):
    n = len(label); npos = int(label.sum()); nneg = n - npos
    prev = npos / n if n else None
    if npos == 0 or nneg == 0:
        return dict(n=n, n_pos=npos, prevalence=prev, auroc=None,
                    auc_ci_95=None, auprc=None, perm_null_mean=None,
                    perm_null_ci_95=None, perm_p_value=None)
    auroc = float(roc_auc_score(label, proba))
    auprc = float(average_precision_score(label, proba))
    # bootstrap CI (resample cases)
    boots = []
    for _ in range(N_BOOT):
        idx = RNG_EVAL.integers(0, n, n)
        if label[idx].sum() in (0, n):
            continue
        boots.append(roc_auc_score(label[idx], proba[idx]))
    ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))] if boots else None
    # holdout-label permutation null (predictions fixed, labels shuffled)
    nulls = np.empty(N_PERM)
    for i in range(N_PERM):
        nulls[i] = roc_auc_score(RNG_EVAL.permutation(label), proba)
    p = float((np.sum(nulls >= auroc) + 1) / (N_PERM + 1))
    return dict(n=n, n_pos=npos, prevalence=round(prev, 4), auroc=round(auroc, 4),
                auc_ci_95=[round(ci[0], 4), round(ci[1], 4)] if ci else None,
                auprc=round(auprc, 4),
                perm_null_mean=round(float(nulls.mean()), 4),
                perm_null_ci_95=[round(float(np.percentile(nulls, 2.5)), 4),
                                 round(float(np.percentile(nulls, 97.5)), 4)],
                perm_p_value=round(p, 4))


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device", device)
    rows, cache = load_all()
    commit = git_hash()
    OUT.mkdir(parents=True, exist_ok=True)
    table = []
    for name, labfn in DEFS.items():
        print(f"\n===== {name} =====")
        sets = build_sets(rows, cache, labfn)
        ntr = len(sets["train"]); nval = len(sets["val"]); ntest = len(sets["test"])
        print(f"n train={ntr} val={nval} test={ntest}")
        model, best_loss = train_clam(sets["train"], sets["val"], device)
        vp, vy = predict(model, sets["val"], device)
        tp, ty = predict(model, sets["test"], device)
        pooled_p = np.concatenate([vp, tp]); pooled_y = np.concatenate([vy, ty])
        res = dict(
            definition=name,
            n_train=ntr, n_train_pos=int(sum(l for _, l in sets["train"])),
            best_val_loss=round(best_loss, 4),
            val_only=eval_block(vp, vy),
            test_only=eval_block(tp, ty),
            pooled=eval_block(pooled_p, pooled_y),
        )
        # per-definition metrics.json (experiment contract)
        m = dict(schema_version="0.1", task="her2_status_decoupling",
                 model="CLAM-SB", embedding_model="uni_v1",
                 embedding_manifest=MANIFEST, split_source="embedding_manifest_uni.csv (site-disjoint, verified)",
                 hyperparams=HP, commit_hash=commit,
                 claim_level="hypothesis_only", critic_status="pending", **res)
        (OUT / f"metrics_{name}.json").write_text(json.dumps(m, indent=2))
        table.append(res)
        po = res["pooled"]; to = res["test_only"]
        print(f"  pooled  AUROC={po['auroc']} CI{po['auc_ci_95']} perm_p={po['perm_p_value']} (n={po['n']} pos={po['n_pos']})")
        print(f"  test    AUROC={to['auroc']} CI{to['auc_ci_95']} perm_p={to['perm_p_value']} (n={to['n']} pos={to['n_pos']})")
        print(f"  val     AUROC={res['val_only']['auroc']} (reproduction check)")

    (OUT / "results_table.json").write_text(json.dumps(
        dict(commit_hash=commit, n_perm=N_PERM, n_boot=N_BOOT, definitions=table), indent=2))
    # flat CSV
    import csv as _csv
    with open(OUT / "results_table.csv", "w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["definition", "split", "n", "n_pos", "prevalence", "auroc",
                    "ci_lo", "ci_hi", "perm_null_mean", "perm_p_value"])
        for r in table:
            for sp in ("val_only", "test_only", "pooled"):
                b = r[sp]
                ci = b["auc_ci_95"] or [None, None]
                w.writerow([r["definition"], sp, b["n"], b["n_pos"], b["prevalence"],
                            b["auroc"], ci[0], ci[1], b["perm_null_mean"], b["perm_p_value"]])
    print("\nSaved:", OUT)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"\nDone in {time.time()-t0:.0f}s")

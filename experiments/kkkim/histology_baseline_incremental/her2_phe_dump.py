"""
HER2 (CNV_amp) per-case p_HE dump for incremental-over-pathology analysis (kkkim).

Reuses EXACTLY the pipeline of experiments/kkkim/her2_blind_across_assays/run_her2_definitions.py
(CLAM-SB, UNI-v1, site-disjoint manifest split, seed=42, same HP), but keeps case_id so we can
join H&E predicted probability p_HE to conventional-pathology covariates.

VERIFY GATE: pooled(val+test) AUROC must reproduce 0.7525 (metrics_CNV_amp.json). If not, abort.
"""
import csv, sys, time, random, pickle
from pathlib import Path
import numpy as np
import torch, torch.nn as nn
from sklearn.metrics import roc_auc_score

REPO = Path("/home/kkkim/project/BioProject02")
sys.path.insert(0, str(REPO / "agents"))
from modeling.baselines.attention_mil import CLAMSB

OUT = REPO / "experiments/kkkim/histology_baseline_incremental"
MANIFEST = "/workspace/data/cache/biop02/embedding_manifest_uni.csv"
LABELS_PKL = "/tmp/claude-10005/-home-kkkim-project-BioProject02/d9004fa1-9620-4f16-a861-7a457bb455d4/scratchpad/labels.pkl"
HP = dict(hidden_dim=512, att_dim=256, dropout=0.25, lr=2.0e-4, epochs=50, patience=7, seed=42)
DIM = 1024

L = pickle.load(open(LABELS_PKL, "rb")); cnv = L["cnv"]

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

def lab_cnv(row):
    v = cnv.get(row["case_id"])
    return None if v is None else (1 if v == 2 else 0)

def load_all():
    rows = list(csv.DictReader(open(MANIFEST)))
    cache = {}
    for r in rows:
        sid = r["slide_id"]
        if sid in cache: continue
        cache[sid] = torch.from_numpy(np.load(r["embedding_path"]).astype(np.float32))
    return rows, cache

def build_sets(rows, cache):
    # keep (emb, label) for train; (case_id, emb, label) for val/test
    sets = {"train": [], "val": [], "test": []}
    for r in rows:
        lab = lab_cnv(r)
        if lab is None: continue
        sid = r["slide_id"]
        if sid not in cache: continue
        if r["split"] == "train":
            sets["train"].append((cache[sid], float(lab)))
        else:
            sets[r["split"]].append((r["case_id"], cache[sid], float(lab)))
    return sets

def train_clam(train_set, val_set, device):
    set_seed(HP["seed"])
    model = CLAMSB(feature_dim=DIM, hidden_dim=HP["hidden_dim"], att_dim=HP["att_dim"], dropout=HP["dropout"]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=HP["lr"]); crit = nn.BCEWithLogitsLoss()
    best_loss, best_state, no_imp = float("inf"), None, 0
    order = list(range(len(train_set)))
    for ep in range(1, HP["epochs"] + 1):
        model.train(); random.shuffle(order)
        for i in order:
            emb, lab = train_set[i]
            opt.zero_grad(); logit, _ = model(emb.to(device))
            loss = crit(logit, torch.tensor([lab], device=device)); loss.backward(); opt.step()
        model.eval(); vl = 0.0
        with torch.no_grad():
            for _cid, emb, lab in val_set:
                logit, _ = model(emb.to(device))
                vl += crit(logit, torch.tensor([lab], device=device)).item()
        vl /= max(len(val_set), 1)
        if vl < best_loss - 1e-6:
            best_loss = vl; best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}; no_imp = 0
        else:
            no_imp += 1
            if no_imp >= HP["patience"]: break
    if best_state: model.load_state_dict(best_state)
    return model

def predict(model, dataset, device):
    out = []
    model.eval()
    with torch.no_grad():
        for cid, emb, lab in dataset:
            logit, _ = model(emb.to(device))
            out.append((cid, float(torch.sigmoid(logit).item()), int(lab)))
    return out

def main():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print("device", device); t0 = time.time()
    rows, cache = load_all()
    print(f"[load] {len(cache)} embeddings {time.time()-t0:.0f}s")
    sets = build_sets(rows, cache)
    print(f"n train={len(sets['train'])} val={len(sets['val'])} test={len(sets['test'])}")
    model = train_clam(sets["train"], sets["val"], device)
    val = predict(model, sets["val"], device)
    test = predict(model, sets["test"], device)
    allrows = [(c, p, y, "val") for c, p, y in val] + [(c, p, y, "test") for c, p, y in test]
    p = np.array([r[1] for r in allrows]); y = np.array([r[2] for r in allrows])
    pooled_auc = roc_auc_score(y, p)
    print(f"pooled AUROC={pooled_auc:.4f} (target 0.7525) n={len(y)} pos={int(y.sum())}")
    with open(OUT / "her2_cnv_amp_phe.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case_id", "p_HE", "y_true", "split"])
        for c, pp, yy, sp in allrows: w.writerow([c, round(pp, 6), yy, sp])
    ok = abs(pooled_auc - 0.7525) < 0.01
    print("VERIFY", "PASS" if ok else "FAIL")
    if not ok: sys.exit(2)

if __name__ == "__main__":
    main()

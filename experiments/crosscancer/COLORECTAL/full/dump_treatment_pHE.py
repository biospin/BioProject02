#!/usr/bin/env python3
"""Recover per-patient H&E-MIL probability (p_HE) for the treatment markers.

The routing_cost.json summary was produced by run_cms_and_routing.py with a FIXED seed
(train_eval seed=42, deterministic). This driver re-runs the identical marker training for
msi_high and anti_egfr_eligible and persists the per-patient p_HE that the summary discarded.
It asserts the reproduced holdout AUROC matches the committed summary before writing, so the
per-patient probabilities are the same result, not a fresh seed/split.

Output: treatment_pHE.json  {marker: {reproduced_auroc, target_auroc, patient_proba, patient_true}}
"""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
# reuse the exact split/slides/labels/run_marker from the committed pipeline
import importlib.util
spec = importlib.util.spec_from_file_location("rcr", str(HERE / "run_cms_and_routing.py"))
rcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rcr)

TARGET = {"msi_high": 0.9184, "anti_egfr_eligible": 0.7053}
DEVICE = sys.argv[1] if len(sys.argv) > 1 else "cuda:0"

def main():
    split, extended = rcr.build_split()
    slides = rcr.build_slides(split)
    tx_lab = rcr.load_treatment_labels()
    print(f"slides={len(slides)} device={DEVICE}")
    out = {}
    for ep in ("msi_high", "anti_egfr_eligible"):
        r = rcr.run_marker(slides, tx_lab, ep, DEVICE)
        auc = r["real_auroc"]
        tgt = TARGET[ep]
        ok = abs(auc - tgt) < 0.01
        print(f"[{ep}] reproduced AUROC={auc}  target={tgt}  match={ok}  n_pos={r['n_pos']}/{r['n_holdout']}")
        assert ok, f"{ep}: reproduced {auc} != committed {tgt} — NOT the same result, aborting"
        out[ep] = {
            "reproduced_auroc": auc, "target_auroc": tgt,
            "n_holdout": r["n_holdout"], "n_pos": r["n_pos"],
            "exploratory_by_prereg": r["n_pos"] < 25,
            "patient_proba": r["patient_proba"], "patient_true": r["patient_true"],
        }
    (HERE / "treatment_pHE.json").write_text(json.dumps(out, indent=2))
    print("wrote treatment_pHE.json")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BIOP02-74 open item — PAM50 소스 pinning + policy(§10) vs 실제 사용 대조.
BIOP02-49 QC(comment 11064)가 낸 57.0%(514/902) 수치를 정확한 cBioPortal study_id/속성으로
재현하고, split_policy_v0.md §10의 "커버리지 부족시 fallback" 조건이 실제로 성립하는지 확인한다.
판정 없음 — 수치만 낸다. 소스 전환 여부는 data-owner(kkkim) 결정.
"""
import csv, json, urllib.request
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
MANIFEST = HERE.parent / "manifests" / "tcga_brca_manifest.csv"
CBIO_STUDY = "brca_tcga_pan_can_atlas_2018"
CBIO_ATTR = "SUBTYPE"  # PATIENT-level, 값 "BRCA_LumA" 등 prefix


def post(path, body):
    req = urllib.request.Request(f"https://www.cbioportal.org/api{path}", data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=30))


def main():
    d = post(f"/studies/{CBIO_STUDY}/clinical-data/fetch?clinicalDataType=PATIENT", {"attributeIds": [CBIO_ATTR]})
    cbio = {}
    for x in d:
        v = x["value"]
        if v.startswith("BRCA_"):
            cbio[x["patientId"]] = v.replace("BRCA_", "").replace("Her2", "HER2")

    manifest = {r["case_id"]: r["pam50"] for r in csv.DictReader(open(MANIFEST)) if r["pam50"]}
    n_manifest = len(manifest)
    n_cbio = len(cbio)
    coverage_pct = round(100 * n_cbio / n_manifest, 1)  # cBioPortal이 manifest 코호트를 얼마나 덮는가

    both = [c for c in manifest if c in cbio]
    match = sum(1 for c in both if manifest[c] == cbio[c])
    concordance_pct = round(100 * match / len(both), 1) if both else None

    mismatch_pairs = Counter((manifest[c], cbio[c]) for c in both if manifest[c] != cbio[c])
    top_mismatches = [{"local": k[0], "cbio": k[1], "n": v}
                       for k, v in mismatch_pairs.most_common(10)]

    result = {
        "cbio_study_id": CBIO_STUDY, "cbio_attribute": CBIO_ATTR, "cbio_level": "PATIENT",
        "n_manifest_pam50": n_manifest, "n_cbio_pam50": n_cbio,
        "cbio_coverage_of_manifest_cohort_pct": coverage_pct,
        "n_overlap": len(both), "n_match": match, "concordance_pct": concordance_pct,
        "top_mismatch_pairs_local_vs_cbio": top_mismatches,
        "policy_check": f"split_policy_v0.md §10: local/genefu fallback authorized only if "
                         f"cBioPortal coverage short. Measured coverage={coverage_pct}% "
                         f"({'HIGH — fallback condition NOT met' if coverage_pct > 90 else 'short — fallback condition met'})",
    }
    out = HERE.parent / "manifests" / "pam50_source_reconcile_biop02-74.json"
    json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved {out}\nDONE_PAM50_SOURCE_RECONCILE")


if __name__ == "__main__":
    main()

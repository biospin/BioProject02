#!/usr/bin/env python3
"""
BIOP02-148 — Table 1(코호트 특성표) 공용 임상변수(age/sex/stage/grade/TSS site) fetch.
5암종 전부 cBioPortal PATIENT-level clinical-data, 각 코호트 기존 case_id universe에 join만
(신규 코호트 정의 없음 — patient_labels.csv/manifest 그대로 재사용).
"""
import csv, json, sys, urllib.request
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
CC = HERE.parent
DATA = CC.parent.parent / "agents" / "data" / "manifests"

STUDIES = {
    "BREAST": ["brca_tcga_pan_can_atlas_2018"],
    "LUNG": ["luad_tcga_pan_can_atlas_2018", "lusc_tcga_pan_can_atlas_2018"],
    "COLORECTAL": ["coadread_tcga_pan_can_atlas_2018"],
    "GASTRIC": ["stad_tcga_pan_can_atlas_2018"],
    "HEADNECK": ["hnsc_tcga_pan_can_atlas_2018"],
}
ATTRS = ["AGE", "SEX", "AJCC_PATHOLOGIC_TUMOR_STAGE", "GRADE", "TISSUE_SOURCE_SITE_CODE"]


def post(path, body):
    for a in range(4):
        try:
            req = urllib.request.Request(
                f"https://www.cbioportal.org/api{path}", data=json.dumps(body).encode(),
                headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print(f"  cbio POST {path} retry{a+1}: {e}"); import time; time.sleep(6 * (a + 1))
    raise RuntimeError(f"cbio POST failed {path}")


def stage_ordinal(v):
    if not v or v.startswith("["):
        return "missing"
    v = v.upper().replace("STAGE ", "").strip()
    for pfx in ("IV", "III", "II", "I"):
        if v.startswith(pfx):
            return pfx
    return "missing"


def case_universe(cancer):
    if cancer == "BREAST":
        rows = list(csv.DictReader(open(DATA / "tcga_brca_manifest.csv")))
        return sorted({r["case_id"] for r in rows})
    d = {"LUNG": "LUNG_NSCLC", "COLORECTAL": "COLORECTAL", "GASTRIC": "GASTRIC_STAD",
         "HEADNECK": "HEADNECK_HNSC"}[cancer]
    rows = list(csv.DictReader(open(CC / d / "full" / "patient_labels.csv")))
    return sorted({r["case_id"] for r in rows})


def main():
    out_all = {}
    for cancer, studies in STUDIES.items():
        cases = set(case_universe(cancer))
        print(f"[{cancer}] target patients: {len(cases)}")
        age, sex, stage_raw, grade_raw, tss = {}, {}, {}, {}, {}
        for study in studies:
            d = post(f"/studies/{study}/clinical-data/fetch?clinicalDataType=PATIENT",
                     {"attributeIds": ["AGE", "SEX", "AJCC_PATHOLOGIC_TUMOR_STAGE"]})
            for x in d:
                pid = x["patientId"]
                if pid not in cases:
                    continue
                aid, val = x["clinicalAttributeId"], x["value"]
                if aid == "AGE":
                    try: age[pid] = float(val)
                    except (TypeError, ValueError): pass
                elif aid == "SEX":
                    sex[pid] = val
                elif aid == "AJCC_PATHOLOGIC_TUMOR_STAGE":
                    stage_raw[pid] = val
            # GRADE/TISSUE_SOURCE_SITE_CODE는 SAMPLE-level(sh_fetch_labels.py 확인 패턴과 동일) —
            # PATIENT-level로 조회하면 0건이 나오는 걸 실측으로 확인(2026-08-20).
            ds = post(f"/studies/{study}/clinical-data/fetch?clinicalDataType=SAMPLE",
                      {"attributeIds": ["GRADE", "TISSUE_SOURCE_SITE_CODE"]})
            for x in ds:
                pid = x["patientId"]
                if pid not in cases:
                    continue
                aid, val = x["clinicalAttributeId"], x["value"]
                if aid == "GRADE" and pid not in grade_raw:  # 환자당 첫 샘플만(중복 방지)
                    grade_raw[pid] = val
                elif aid == "TISSUE_SOURCE_SITE_CODE" and pid not in tss:
                    tss[pid] = val
        import statistics as st
        ages = sorted(age.values())
        age_summary = None
        if ages:
            q1 = ages[int(0.25 * (len(ages) - 1))]; q3 = ages[int(0.75 * (len(ages) - 1))]
            age_summary = {"median": round(st.median(ages), 1), "iqr": [q1, q3], "n": len(ages)}
        sex_dist = Counter(sex.values())
        stage_dist = Counter(stage_ordinal(stage_raw.get(c, "")) for c in cases)
        grade_n = sum(1 for c in cases if grade_raw.get(c))
        grade_dist = Counter(grade_raw.get(c, "missing") for c in cases if grade_raw.get(c))
        tss_n_sites = len({tss[c] for c in cases if c in tss})

        out_all[cancer] = {
            "n_patients": len(cases),
            "age": age_summary,
            "sex_dist": dict(sex_dist),
            "stage_dist": dict(stage_dist),
            "grade_coverage_n": grade_n, "grade_coverage_pct": round(100 * grade_n / len(cases), 1),
            "grade_dist": dict(grade_dist),
            "tss_n_sites": tss_n_sites,
        }
        print(f"  age n={age_summary['n'] if age_summary else 0}, sex={dict(sex_dist)}, "
              f"stage={dict(stage_dist)}, grade_coverage={grade_n}/{len(cases)}, tss_sites={tss_n_sites}")

    out = HERE / "table1_clinical.json"
    json.dump(out_all, open(out, "w"), indent=2, ensure_ascii=False)
    print(f"Saved {out}\nDONE_FETCH_TABLE1_CLINICAL")


if __name__ == "__main__":
    main()

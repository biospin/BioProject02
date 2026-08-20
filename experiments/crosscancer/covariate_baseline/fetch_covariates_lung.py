#!/usr/bin/env python3
"""
BIOP02-140 v1 — 폐 공변량(purity/stage/site) fetch. 판정 없음, 원값 join만.
COVARIATE_BASELINE_PREREGISTRATION.md 에서 정한 출처·처리 규칙을 그대로 구현한다.

출력: lung_covariates.csv (case_id, purity, purity_missing, stage, site)
grade는 커버리지 0%를 여기서 실측·로그로 남기고 제외(사전등록에 이미 명시).
"""
import csv, json, sys, urllib.request
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
LUNG_FULL = HERE.parent / "LUNG_NSCLC" / "full"
ABSOLUTE_URL = "https://api.gdc.cancer.gov/data/4f277128-f793-4354-a13d-30cc7fe9f6b5"
ABSOLUTE_LOCAL = HERE / "TCGA_mastercalls.abs_tables_JHU_UCSC.txt"


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


def stage_to_ordinal(v):
    if not v or v in ("[Not Available]", "[Not Applicable]", "[Unknown]", "[Discrepancy]"):
        return "missing"
    v = v.upper().replace("STAGE ", "").strip()
    for pfx in ("IV", "III", "II", "I"):  # 긴 접두어부터(짧은 "I"가 "IV"/"III"/"II"를 먼저 먹지 않도록)
        if v.startswith(pfx):
            return pfx
    return "missing"


def site_to_lobe(v):
    if not v or not v.startswith("C34"):
        return "missing"
    return v  # C34.0..C34.9, keep as-is per pre-registration


def main():
    # --- cohort/patients we need covariates for (all labeled lung patients) ---
    labels = {r["case_id"]: r for r in csv.DictReader(open(LUNG_FULL / "patient_labels.csv"))}
    case_ids = set(labels)
    print(f"target patients: {len(case_ids)}")

    # --- purity (ABSOLUTE, pan-cancer file, already downloaded) ---
    if not ABSOLUTE_LOCAL.exists():
        raise SystemExit(f"missing {ABSOLUTE_LOCAL} — download from {ABSOLUTE_URL} first")
    purity = {}
    with open(ABSOLUTE_LOCAL) as fh:
        r = csv.DictReader(fh, delimiter="\t")
        for row in r:
            sample = row["sample"]  # e.g. TCGA-05-4249-01A-01D-...
            pid = "-".join(sample.split("-")[:3])
            if pid not in case_ids:
                continue
            if pid in purity:
                continue  # first matching tumor sample only (pre-registered)
            pv = row["purity"]
            try:
                purity[pid] = float(pv)
            except (TypeError, ValueError):
                pass
    print(f"purity matched: {len(purity)}/{len(case_ids)}")

    # --- stage + site (cBioPortal, PATIENT-level) ---
    attrs = ["AJCC_PATHOLOGIC_TUMOR_STAGE", "GRADE", "ICD_O_3_SITE"]
    stage_raw, site_raw, grade_raw = {}, {}, {}
    for study in ["luad_tcga_pan_can_atlas_2018", "lusc_tcga_pan_can_atlas_2018"]:
        d = post(f"/studies/{study}/clinical-data/fetch?clinicalDataType=PATIENT", {"attributeIds": attrs})
        for x in d:
            pid = x["patientId"]
            if pid not in case_ids:
                continue
            if x["clinicalAttributeId"] == "AJCC_PATHOLOGIC_TUMOR_STAGE":
                stage_raw[pid] = x["value"]
            elif x["clinicalAttributeId"] == "ICD_O_3_SITE":
                site_raw[pid] = x["value"]
            elif x["clinicalAttributeId"] == "GRADE":
                grade_raw[pid] = x["value"]
    print(f"stage matched: {len(stage_raw)}/{len(case_ids)}, site matched: {len(site_raw)}/{len(case_ids)}")
    print(f"grade matched: {len(grade_raw)}/{len(case_ids)} "
          f"({'0% 확인 — 사전등록대로 v1 제외' if len(grade_raw) == 0 else 'WARNING: 사전등록 가정(0%)과 다름, grade 포함 여부 재검토 필요'})")

    # --- write covariates csv ---
    out = HERE / "lung_covariates.csv"
    rows = []
    for cid in sorted(case_ids):
        p = purity.get(cid)
        rows.append({
            "case_id": cid,
            "purity": round(p, 4) if p is not None else 0.0,
            "purity_missing": 0 if p is not None else 1,
            "stage": stage_to_ordinal(stage_raw.get(cid, "")),
            "site": site_to_lobe(site_raw.get(cid, "")),
        })
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")

    stage_dist = Counter(r["stage"] for r in rows)
    site_dist = Counter(r["site"] for r in rows)
    print("stage dist:", dict(stage_dist))
    print("site dist:", dict(site_dist))
    print("DONE_FETCH_COVARIATES_LUNG")


if __name__ == "__main__":
    main()

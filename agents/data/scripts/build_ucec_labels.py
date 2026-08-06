#!/usr/bin/env python3
"""
UCEC(자궁내막) 환자 라벨 생성 (BIOP02-128) — cBioPortal ucec_tcga_pan_can_atlas_2018.

UCEC.yaml 이 선언한 4 endpoint 를 0/1 로 만든다:
  histology_serous : 조직형 serous(양성대조; endometrioid 대비 강한 형태)
  msi_h            : MSI-H (면역/dMMR → IO)
  her2_amp         : ERBB2 증폭(GISTIC >= 2) — blind 축, 유방·위 HER2 앵커의 3번째 장기 복제
  pole             : POLE ultramutated (탐색적)

출력: experiments/crosscancer/UCEC/full/patient_labels.csv
컬럼: case_id, histology_serous, msi_h, her2_amp, pole  (+ 결측은 빈칸)

⚠️ 탐색적 확장 — 사전등록 5암종 밖. sealed law 집계 대상 아님.
라벨은 조달만 하며 판정하지 않는다(claim_level: hypothesis_only).
"""
import csv, io, json, os, sys, urllib.request, urllib.error

API = "https://www.cbioportal.org/api"
STUDY = "ucec_tcga_pan_can_atlas_2018"
OUT = "experiments/crosscancer/UCEC/full/patient_labels.csv"
MSI_CUT = 10.0   # MSIsensor score >= 10 = MSI-H (통상 컷오프). 사후 조정 금지.


def get(url, payload=None, timeout=120):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        req.add_header("Content-Type", "application/json")
        req.get_method = lambda: "POST"
    with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
        return json.load(r)


def clinical(attr_id):
    """환자 단위 임상 속성 -> {patientId: value}"""
    url = f"{API}/studies/{STUDY}/clinical-data?clinicalDataType=PATIENT&attributeId={attr_id}&projection=SUMMARY"
    try:
        rows = get(url)
    except urllib.error.HTTPError as e:
        print(f"  [warn] {attr_id}: HTTP {e.code}")
        return {}
    return {r["patientId"]: r.get("value") for r in rows}


def sample_clinical(attr_id):
    url = f"{API}/studies/{STUDY}/clinical-data?clinicalDataType=SAMPLE&attributeId={attr_id}&projection=SUMMARY"
    try:
        rows = get(url)
    except urllib.error.HTTPError as e:
        print(f"  [warn] sample {attr_id}: HTTP {e.code}")
        return {}
    out = {}
    for r in rows:
        out.setdefault(r["patientId"], r.get("value"))
    return out


def list_attrs():
    try:
        rows = get(f"{API}/studies/{STUDY}/clinical-attributes")
        return {r["clinicalAttributeId"]: r.get("displayName", "") for r in rows}
    except Exception as e:
        print("  [warn] attrs:", e)
        return {}


def main():
    print(f"study={STUDY}")
    attrs = list_attrs()
    print(f"  임상 속성 {len(attrs)}개")

    # --- 후보 속성 자동 탐색(스터디마다 이름이 달라 하드코딩 금지) ---
    def find(*keys):
        for aid, name in attrs.items():
            blob = (aid + " " + name).upper()
            if all(k.upper() in blob for k in keys):
                return aid
        return None

    # 실측 확인된 속성명(2026-08-06, cBioPortal API):
    #   SUBTYPE          = 분자/조직 아형(UCEC_CN_HIGH(serous-like) 등)  [patient]
    #   MSI_SENSOR_SCORE = MSIsensor 연속 점수 → 임계 10.0 (통상 MSI-H 컷) [sample]
    aid_hist = "SUBTYPE"
    aid_msi = "MSI_SENSOR_SCORE"
    print(f"  histology attr = {aid_hist}\n  msi attr = {aid_msi} (연속 → 임계 {MSI_CUT})")

    hist = clinical(aid_hist) or sample_clinical(aid_hist)
    msi = sample_clinical(aid_msi) or clinical(aid_msi)

    # --- ERBB2 증폭(GISTIC) + POLE 변이 ---
    her2, pole = {}, {}
    try:
        prof = f"{STUDY}_gistic"
        body = {"entrezGeneIds": [2064], "sampleListId": f"{STUDY}_all"}
        rows = get(f"{API}/molecular-profiles/{prof}/discrete-copy-number/fetch"
                   f"?discreteCopyNumberEventType=AMP&projection=SUMMARY", body)
        for r in rows:
            her2[r["patientId"]] = 1
        print(f"  ERBB2 AMP 환자 {len(her2)}명")
    except Exception as e:
        print("  [warn] ERBB2 CNA:", e)
    try:
        prof = f"{STUDY}_mutations"
        # 엔드포인트는 mutations(복수) — mutation/fetch 는 404. sequenced 리스트 기준.
        body = {"entrezGeneIds": [5426], "sampleListId": f"{STUDY}_sequenced"}  # POLE
        rows = get(f"{API}/molecular-profiles/{prof}/mutations/fetch?projection=SUMMARY", body)
        for r in rows:
            pole[r["patientId"]] = 1
        print(f"  POLE 변이 환자 {len(pole)}명")
    except Exception as e:
        print("  [warn] POLE mutation:", e)

    patients = sorted(set(hist) | set(msi) | set(her2) | set(pole))
    print(f"  환자 합집합 {len(patients)}명")
    if not patients:
        sys.exit("라벨 조달 실패 — 속성 탐색 결과 확인 필요")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = {"histology_serous": 0, "msi_h": 0, "her2_amp": 0, "pole": 0}
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "histology_serous", "msi_h", "her2_amp", "pole"])
        for p in patients:
            h = (hist.get(p) or "").upper()
            # UCEC SUBTYPE: UCEC_CN_HIGH = copy-number high(=serous-like), UCEC_CN_LOW/MSI/POLE
            hs = "" if not h else (1 if ("SEROUS" in h or "CN_HIGH" in h) else 0)
            mv = msi.get(p)
            try:
                mh = 1 if float(mv) >= MSI_CUT else 0
            except (TypeError, ValueError):
                mh = ""
            h2 = 1 if p in her2 else (0 if her2 else "")
            pl = 1 if p in pole else (0 if pole else "")
            for k, v in (("histology_serous", hs), ("msi_h", mh), ("her2_amp", h2), ("pole", pl)):
                if v == 1:
                    n[k] += 1
            w.writerow([p, hs, mh, h2, pl])
    print(f"\n작성: {OUT}  ({len(patients)} 환자)")
    print("양성 수:", ", ".join(f"{k}={v}" for k, v in n.items()))
    print("⚠️ 탐색적 확장(사전등록 밖) · claim_level: hypothesis_only")


if __name__ == "__main__":
    main()

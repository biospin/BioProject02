#!/usr/bin/env python3
"""
BIOP02-139 라벨 품질 민감도 분석 — 제2 assay 소스 fetch (판정 없음, 원값만 저장).

무엇을 하는가 (순수 조회, 임계값 적용은 다음 단계 스크립트가 한다):
  1. GASTRIC_STAD: MSI_SCORE_MANTIS (cBioPortal clinical attribute) — 기존 라벨(msi_h)이 쓰는
     MSI_SENSOR_SCORE와는 다른 알고리즘의 MSI 점수. 같은 환자 universe에 대해 둘 다 원값으로 저장.
  2. LUNG_NSCLC egfr_activating / kras_g12c, COLORECTAL braf_v600e: 양성 콜의 VAF
     (tumorAltCount / (tumorAltCount+tumorRefCount)). fetch_labels.py의 분류기(egfr_activating/
     kras_g12c/braf_v600e)와 완전히 동일한 로직으로 양성만 골라 VAF를 부여한다 — 새 콜 집합을
     만들지 않고 기존 라벨의 양성 부분집합에 VAF만 추가.

출력 (원값 저장, 배제 판정 없음):
  experiments/crosscancer/label_quality/msi_dual_score.csv
  experiments/crosscancer/label_quality/mutation_vaf.csv

기존 라벨 소스(patient_labels.csv)는 건드리지 않는다 — 이 스크립트는 신규 격리 산출물만 쓴다.
"""
import urllib.request, json, re, csv, sys
from pathlib import Path

HERE = Path(__file__).parent
CC = HERE.parent
BASE = "https://www.cbioportal.org/api"


def post(path, body):
    for a in range(4):
        try:
            req = urllib.request.Request(f"{BASE}{path}", data=json.dumps(body).encode(),
                headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print(f"  cbio POST {path} 재시도{a+1}: {e}"); import time; time.sleep(8 * (a + 1))
    raise RuntimeError(f"cbio POST failed {path}")


def get(path):
    for a in range(4):
        try:
            return json.load(urllib.request.urlopen(f"{BASE}{path}", timeout=60))
        except Exception as e:
            print(f"  cbio GET {path} 재시도{a+1}: {e}"); import time; time.sleep(8 * (a + 1))
    raise RuntimeError(f"cbio GET failed {path}")


def sample_attr(study, attr):
    d = post(f"/studies/{study}/clinical-data/fetch?clinicalDataType=SAMPLE", {"attributeIds": [attr]})
    out = {}
    for x in d:
        v = x.get("value")
        try:
            out[x["patientId"]] = float(v)
        except (TypeError, ValueError):
            pass
    return out


# fetch_labels.py 와 완전히 동일한 분류기 (재구현이 아니라 그대로 가져옴 — 콜 집합 불변 보장)
def egfr_activating(s):
    s = s.replace('p.', '')
    if re.match(r'^L858R$', s): return True
    if re.match(r'^L861[A-Z]', s): return True
    if re.match(r'^G719[A-Z]', s): return True
    if re.match(r'^S768I$', s): return True
    if re.match(r'^E709[A-Z_]', s): return True
    if 'del' in s and re.search(r'74[5-9]|75[0-9]', s): return True
    if ('ins' in s or 'dup' in s) and re.search(r'7[67][0-9]', s): return True
    return False


def kras_g12c(s): return s.replace('p.', '') == 'G12C'
def braf_v600e(s): return s.replace('p.', '').startswith('V600')


GENE = {"EGFR": 1956, "KRAS": 3845, "BRAF": 673}


def gene_positive_vaf(study, gene, classifier):
    """양성 콜만 골라 VAF를 부여한다 (fetch_labels.gene_positive와 같은 판정 로직)."""
    prof = f"{study}_mutations"; slist = f"{study}_sequenced"
    m = post(f"/molecular-profiles/{prof}/mutations/fetch?projection=DETAILED",
             {"sampleListId": slist, "entrezGeneIds": [GENE[gene]]})
    out = {}
    for x in m:
        pc = x.get("proteinChange")
        if not (isinstance(pc, str) and classifier(pc)):
            continue
        alt = x.get("tumorAltCount"); ref = x.get("tumorRefCount")
        pid = x.get("patientId")
        if isinstance(alt, int) and isinstance(ref, int) and (alt + ref) > 0:
            vaf = alt / (alt + ref)
        else:
            vaf = None
        # 한 환자에 같은 유전자 활성 변이가 여러 개면 VAF 최댓값(가장 확실한 콜)을 남긴다
        if pid not in out or (vaf is not None and (out[pid] is None or vaf > out[pid])):
            out[pid] = vaf
    return out


def fetch_msi_dual():
    study = "stad_tcga_pan_can_atlas_2018"
    sensor = sample_attr(study, "MSI_SENSOR_SCORE")
    mantis = sample_attr(study, "MSI_SCORE_MANTIS")
    universe = sorted(set(sensor) | set(mantis))
    rows = []
    for c in universe:
        rows.append({"case_id": c, "msi_sensor_score": sensor.get(c, ""), "msi_mantis_score": mantis.get(c, "")})
    out = HERE / "msi_dual_score.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "msi_sensor_score", "msi_mantis_score"])
        w.writeheader(); w.writerows(rows)
    both = sum(1 for r in rows if r["msi_sensor_score"] != "" and r["msi_mantis_score"] != "")
    print(f"  wrote {out} ({len(rows)}명, 둘 다 있는 환자 {both}명)")


def fetch_mutation_vaf():
    rows = []
    for st in ["luad_tcga_pan_can_atlas_2018", "lusc_tcga_pan_can_atlas_2018"]:
        egfr_vaf = gene_positive_vaf(st, "EGFR", egfr_activating)
        kras_vaf = gene_positive_vaf(st, "KRAS", kras_g12c)
        for c, v in egfr_vaf.items():
            rows.append({"case_id": c, "study": st, "endpoint": "egfr_activating", "vaf": v})
        for c, v in kras_vaf.items():
            rows.append({"case_id": c, "study": st, "endpoint": "kras_g12c", "vaf": v})
    braf_vaf = gene_positive_vaf("coadread_tcga_pan_can_atlas_2018", "BRAF", braf_v600e)
    for c, v in braf_vaf.items():
        rows.append({"case_id": c, "study": "coadread_tcga_pan_can_atlas_2018", "endpoint": "braf_v600e", "vaf": v})
    out = HERE / "mutation_vaf.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "study", "endpoint", "vaf"])
        w.writeheader(); w.writerows(rows)
    by_ep = {}
    for r in rows:
        by_ep.setdefault(r["endpoint"], []).append(r["vaf"])
    print(f"  wrote {out} ({len(rows)}건)")
    for ep, vafs in by_ep.items():
        have = [v for v in vafs if v is not None]
        print(f"    {ep}: n_pos={len(vafs)}, VAF 있음={len(have)}")


def main():
    print("=== MSI 이중 점수 (GASTRIC_STAD, MSIsensor vs MANTIS) ===")
    fetch_msi_dual()
    print("=== 변이 양성 콜 VAF (LUNG EGFR/KRAS-G12C, CRC BRAF-V600E) ===")
    fetch_mutation_vaf()
    print("\n원값만 저장했다. 임계값 적용·배제 판정은 audit_label_quality_sensitivity.py 몫이다.")


if __name__ == "__main__":
    main()

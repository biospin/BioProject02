#!/usr/bin/env python3
"""
Cross-cancer 환자 라벨 페처 (cBioPortal open, GPU 0) — advisor 게이트 반영.

frozen-map 축과 정합하는 endpoint만(ALK 드롭: NO-GO·fusion·축부재):
  LUNG: EGFR_activating, KRAS_G12C, histology(LUAD=0/LUSC=1)   [LUAD+LUSC study]
  CRC : BRAF_V600E, (baseline=no BRAF)                          [coadread study]

- 분모 = sequenced 환자(mutation 프로파일에 있는 = 진짜 음성 구분). patientId=TCGA-XX-XXXX=case_id.
- 변이 분류기 재사용(egfr_activating/kras_variant/braf_v600e; p. 접두 무관).
- prevalence 게이트: 문헌 앵커 대비(EGFR~15%/KRAS-G12C~13% LUAD · BRAF-V600E~8-10% CRC). 벗어나면 경고(파싱오류 탐지).
출력: <cancer>/full/patient_labels.csv (case_id + endpoint 이진 + has_*), prevalence_report.json
"""
import urllib.request, json, re, csv, sys
from pathlib import Path

HERE = Path(__file__).parent
BASE = "https://www.cbioportal.org/api"

def post(path, body):
    for a in range(4):
        try:
            req = urllib.request.Request(f"{BASE}{path}", data=json.dumps(body).encode(),
                headers={"Accept":"application/json","Content-Type":"application/json"}, method="POST")
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print(f"  cbio POST {path} 재시도{a+1}: {e}"); import time; time.sleep(8*(a+1))
    raise RuntimeError(f"cbio POST failed {path}")

def get(path):
    for a in range(4):
        try:
            return json.load(urllib.request.urlopen(f"{BASE}{path}", timeout=60))
        except Exception as e:
            print(f"  cbio GET {path} 재시도{a+1}: {e}"); import time; time.sleep(8*(a+1))
    raise RuntimeError(f"cbio GET failed {path}")

# ---- 변이 분류기 (cellline_counts_axis_analysis.py와 동일 로직) ----
def egfr_activating(s):
    """TCGA-LUAD activating(sensitizing) EGFR. T790M(저항성)·passenger 제외.
    실측 보정(2026-07-11): S768I·exon20 dup·E709 추가로 놓친 activating 포섭 → ~11%(문헌 정합)."""
    s = s.replace('p.','')
    if re.match(r'^L858R$', s): return True
    if re.match(r'^L861[A-Z]', s): return True
    if re.match(r'^G719[A-Z]', s): return True
    if re.match(r'^S768I$', s): return True                       # exon20 sensitizing(가이드라인)
    if re.match(r'^E709[A-Z_]', s): return True                   # exon18 E709X activating
    # exon19 in-frame deletion: codon 745-759 영역 del
    if 'del' in s and re.search(r'74[5-9]|75[0-9]', s): return True
    # exon20 insertion/duplication: codon 762-775 영역 (ins 또는 dup 표기)
    if ('ins' in s or 'dup' in s) and re.search(r'7[67][0-9]', s): return True
    return False
def kras_g12c(s): return s.replace('p.','') == 'G12C'
def braf_v600e(s): return s.replace('p.','').startswith('V600')

GENE = {"EGFR":1956, "KRAS":3845, "BRAF":673}

def sequenced_patients(study):
    """mutation 프로파일에 프로파일된 환자(=진짜 음성 구분 분모)."""
    sl = get(f"/sample-lists/{study}_sequenced")
    ids = sl.get("sampleIds", [])
    return set(s[:12] for s in ids)   # TCGA-XX-XXXX

def gene_positive(study, gene, classifier):
    prof = f"{study}_mutations"; slist = f"{study}_sequenced"
    m = post(f"/molecular-profiles/{prof}/mutations/fetch?projection=DETAILED",
             {"sampleListId":slist, "entrezGeneIds":[GENE[gene]]})
    pos = set()
    for x in m:
        pc = x.get("proteinChange")
        if isinstance(pc, str) and classifier(pc):
            pos.add(x.get("patientId"))
    return pos

def build_lung():
    rows = {}   # case_id -> dict
    # 분모: LUAD+LUSC sequenced (histology 라우팅 대상 전체)
    luad = sequenced_patients("luad_tcga_pan_can_atlas_2018")
    lusc = sequenced_patients("lusc_tcga_pan_can_atlas_2018")
    for c in luad: rows[c] = {"case_id":c, "cohort":"LUAD", "histology_lusc":0}
    for c in lusc: rows[c] = {"case_id":c, "cohort":"LUSC", "histology_lusc":1}
    # EGFR/KRAS-G12C: LUAD+LUSC 양쪽 study에서 수집(LUSC엔 드묾)
    egfr = set(); krasc = set()
    for st in ["luad_tcga_pan_can_atlas_2018","lusc_tcga_pan_can_atlas_2018"]:
        egfr |= gene_positive(st, "EGFR", egfr_activating)
        krasc |= gene_positive(st, "KRAS", kras_g12c)
    for c,d in rows.items():
        d["egfr_activating"] = int(c in egfr)
        d["kras_g12c"] = int(c in krasc)
        d["has_egfr"]=1; d["has_kras_g12c"]=1; d["has_histology"]=1
    denom = len(rows)
    prev = {"n_sequenced":denom, "LUAD":len(luad), "LUSC":len(lusc),
            "egfr_activating":{"n":sum(d["egfr_activating"] for d in rows.values())},
            "kras_g12c":{"n":sum(d["kras_g12c"] for d in rows.values())},
            "histology_lusc":{"n":len(lusc)}}
    # LUAD 분모 기준 prevalence(문헌 앵커가 LUAD 기준)
    prev["egfr_activating"]["pct_of_LUAD"]=round(len(egfr & luad)/max(len(luad),1)*100,1)
    prev["kras_g12c"]["pct_of_LUAD"]=round(len(krasc & luad)/max(len(luad),1)*100,1)
    return rows, prev

def build_crc():
    rows = {}
    coad = sequenced_patients("coadread_tcga_pan_can_atlas_2018")
    for c in coad: rows[c]={"case_id":c,"cohort":"COADREAD"}
    braf = gene_positive("coadread_tcga_pan_can_atlas_2018","BRAF",braf_v600e)
    for c,d in rows.items():
        d["braf_v600e"]=int(c in braf); d["has_braf"]=1
    prev={"n_sequenced":len(rows),
          "braf_v600e":{"n":len(braf & coad),"pct":round(len(braf & coad)/max(len(coad),1)*100,1)}}
    return rows, prev

# 문헌 앵커(대조용, 하드코딩 아님 — 게이트)
ANCHOR = {"egfr_activating_pct_LUAD":(10,22), "kras_g12c_pct_LUAD":(8,18), "braf_v600e_pct":(5,14)}

def gate(name, val, lo, hi):
    ok = lo <= val <= hi
    print(f"  [{'OK ' if ok else 'WARN'}] {name} = {val}% (앵커 {lo}-{hi}%)")
    return ok

def write_labels(cancer, rows, cols):
    out = HERE / cancer / "full" / "patient_labels.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out,"w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for d in rows.values(): w.writerow({k:d.get(k,"") for k in cols})
    print(f"  wrote {out} ({len(rows)} 환자)")

def main():
    print("=== LUNG 라벨 (cBioPortal) ===")
    lr, lp = build_lung()
    write_labels("LUNG_NSCLC", lr, ["case_id","cohort","egfr_activating","kras_g12c","histology_lusc",
                                    "has_egfr","has_kras_g12c","has_histology"])
    print("  prevalence:", json.dumps(lp, ensure_ascii=False))
    gate("EGFR_activating/LUAD", lp["egfr_activating"]["pct_of_LUAD"], *ANCHOR["egfr_activating_pct_LUAD"])
    gate("KRAS_G12C/LUAD", lp["kras_g12c"]["pct_of_LUAD"], *ANCHOR["kras_g12c_pct_LUAD"])
    print("\n=== CRC 라벨 ===")
    cr, cp = build_crc()
    write_labels("COLORECTAL", cr, ["case_id","cohort","braf_v600e","has_braf"])
    print("  prevalence:", json.dumps(cp, ensure_ascii=False))
    gate("BRAF_V600E/CRC", cp["braf_v600e"]["pct"], *ANCHOR["braf_v600e_pct"])
    (HERE/"labels_prevalence_report.json").write_text(
        json.dumps({"lung":lp,"crc":cp,"anchors":ANCHOR}, indent=2, ensure_ascii=False))
    print("\nwrote labels_prevalence_report.json")

if __name__ == "__main__":
    main()

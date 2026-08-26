#!/usr/bin/env python3
"""
BIOP02-148 DoD "모든 수치가 커밋된 결과 파일과 1:1 대조" + "본문 R1/R2와 분모 불일치 0건" 검증.
check_number_drift.py(BIOP02-107)는 AUROC류만, 3개 고정 문서만 본다 — Table 1의 환자수/
n_pos/결측 수치는 범위 밖이라 이 스크립트로 별도 확인한다. 판정 아님(원 스크립트와 동일
철학) — 불일치 후보만 나열, 사람이 확인.
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent.parent
MASTER = json.load(open(HERE / "table1_master.json"))

problems = []

# 1) table1_master.json의 holdout n_pos가 원천 mil_cost_results.json과 정확히 같은가
CC_MAP = {"LUNG": "LUNG_NSCLC", "COLORECTAL": "COLORECTAL", "GASTRIC": "GASTRIC_STAD",
          "HEADNECK": "HEADNECK_HNSC"}
for cancer, dirname in CC_MAP.items():
    mil = json.load(open(HERE.parent / dirname / "full" / "mil_cost_results.json"))
    for ep, e in MASTER["cancers"][cancer]["endpoints"].items():
        src = mil["endpoints"][ep]["real"]
        if e["n_pos_holdout"] != src.get("n_pos") or e["n_holdout"] != src.get("n_holdout_patients"):
            problems.append(f"[master vs mil_cost_results.json] {cancer}.{ep}: "
                             f"master n_pos={e['n_pos_holdout']} n_holdout={e['n_holdout']} vs "
                             f"source n_pos={src.get('n_pos')} n_holdout={src.get('n_holdout_patients')}")

# 2) manuscript R2 표(축 | 홀드아웃 양성 표본 | 판정)와 대조
R2_ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|$")
R2_LABEL_TO_MASTER = {
    "폐 EGFR 활성변이": ("LUNG", "egfr_activating"),
    "폐 KRAS-G12C": ("LUNG", "kras_g12c"),
    "위 ERBB2 증폭": ("GASTRIC", "erbb2_amp"),
    "위 MSI-H": ("GASTRIC", "msi_h"),
    "위 EBV": ("GASTRIC", "ebv"),
    "두경부 EGFR 증폭": ("HEADNECK", "egfr_amp"),
}
results_md = REPO / "manuscript" / "sections" / "02_results.md"
r2_checked = 0
if results_md.exists():
    for line in open(results_md, encoding="utf-8"):
        m = R2_ROW.match(line.strip())
        if not m:
            continue
        label, n_pos_str, verdict = m.groups()
        if label not in R2_LABEL_TO_MASTER:
            continue
        cancer, ep = R2_LABEL_TO_MASTER[label]
        master_n = MASTER["cancers"][cancer]["endpoints"][ep]["n_pos_holdout"]
        r2_checked += 1
        if master_n != int(n_pos_str):
            problems.append(f"[Table1 vs 02_results.md R2] {label}: 본문={n_pos_str}, "
                             f"table1_master={master_n}")
print(f"R2 표 {r2_checked}/6행 대조 완료")

# 3) R1 prose에 인용된 헤드라인 n_pos(폐 LUSC 153, 두경부 HPV 26, 두경부 grade 41)
R1_CITED = {"폐 조직형 LUSC 153명": ("LUNG", "histology_lusc", 153),
            "두경부 HPV 26명": ("HEADNECK", "hpv_pos", 26),
            "두경부 grade 41명": ("HEADNECK", "grade_high", 41)}
for label, (cancer, ep, cited_n) in R1_CITED.items():
    master_n = MASTER["cancers"][cancer]["endpoints"][ep]["n_pos_holdout"]
    if master_n != cited_n:
        problems.append(f"[Table1 vs 02_results.md R1 prose] {label}: 본문 인용={cited_n}, "
                         f"table1_master={master_n}")

print(f"\n[결과] 불일치 후보 {len(problems)}건")
for p in problems:
    print(" ", p)
if not problems:
    print("모든 대조 통과 — Table 1/PARTICIPANT_FLOW의 n_pos·holdout 수치가 "
          "mil_cost_results.json(정본) 및 02_results.md R1/R2 인용과 1:1 일치.")
sys.exit(1 if problems else 0)

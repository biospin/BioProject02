#!/usr/bin/env python3
"""
BIOP02-148 — Table 1 조립. 신규 계산 없음 — 이미 커밋된 정본 파일에서 집계만 한다:
  patient_labels.csv / split.csv / manifest (n환자, n슬라이드, split, 엔드포인트 n_pos/결측)
  mil_cost_results.json (엔드포인트별 holdout n — denominator, 암종·엔드포인트마다 다름)
  table1_clinical.json (fetch_table1_clinical.py 산출 — age/sex/stage/grade/TSS site)
출력: table1_master.json(정본, 모든 표 숫자의 단일 출처) + TABLE1.md + PARTICIPANT_FLOW.md
"""
import csv, json
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
CC = HERE.parent
DATA = CC.parent.parent / "agents" / "data" / "manifests"

CLINICAL = json.load(open(HERE / "table1_clinical.json"))

# 암종별 엔드포인트 assay-source(팀 기존 fetch 스크립트 주석/문서에서 확인, 신규 조사 아님)
ASSAY_SOURCE = {
    "er_status": "IHC(임상 병리검사)", "pr_status": "IHC(임상 병리검사)",
    "her2_status": "IHC/FISH(임상 병리검사, BIOP02-49 QC 완료)",
    "pam50": "유전자발현 분류기(계산값, tcga_brca_pam50_computed.csv)",
    "egfr_activating": "체세포변이 콜(MAF, WES-derived)", "kras_g12c": "체세포변이 콜(MAF, WES-derived)",
    "histology_lusc": "병리 진단(조직형, 임상)",
    "braf_v600e": "체세포변이 콜(MAF, WES-derived)",
    "msi_h": "MSIsensor score≥3.5(NGS-derived, SUBTYPE STAD_MSI 교차확인)",
    "erbb2_amp": "CNA(GISTIC) 증폭 콜", "lauren_diffuse": "병리 조직분류(ICD_O_3_HISTOLOGY, 임상)",
    "ebv": "TCGA 분자아형(SUBTYPE, 바이러스 검출 복합판정)",
    "hpv_pos": "TCGA 분자아형(SUBTYPE HNSC_HPV+, p16+바이러스검출 복합판정)",
    "egfr_amp": "CNA(GISTIC) 증폭 콜", "grade_high": "병리 등급(SAMPLE-level GRADE, 임상)",
}

master = {"cancers": {}}

# ---------- BREAST ----------
rows = list(csv.DictReader(open(DATA / "tcga_brca_manifest.csv")))
split_ct = Counter(r["split"] for r in rows)
ep_rows = {}
for ep, has_col in [("er_status", "has_er"), ("pr_status", "has_pr"),
                    ("her2_status", "has_her2"), ("pam50", "has_pam50")]:
    n_has = sum(1 for r in rows if r[has_col] == "1")
    if ep == "pam50":
        # 다중클래스(5종) — 이진 "양성" 개념 없음. has_pam50=1은 Normal-like 제외 로직
        # 이미 반영(her2_pam50_label_qc_v0.1.md §4, BIOP02-49 QC 확인) — 그대로 인용.
        class_dist = dict(Counter(r[ep] for r in rows if r[has_col] == "1"))
        n_pos = None
        ep_rows[ep] = {"n_holdout_or_total": len(rows), "n_has_label": n_has,
                       "class_dist": class_dist, "n_pos": None,
                       "missing_pct": round(100 * (1 - n_has / len(rows)), 1),
                       "assay_source": ASSAY_SOURCE[ep]}
        continue
    n_pos = sum(1 for r in rows if r[has_col] == "1" and r[ep] == "Positive")
    ep_rows[ep] = {"n_holdout_or_total": len(rows), "n_has_label": n_has, "n_pos": n_pos,
                   "missing_pct": round(100 * (1 - n_has / len(rows)), 1),
                   "assay_source": ASSAY_SOURCE[ep]}
master["cancers"]["BREAST"] = {
    "n_patients": len(rows), "n_slides": len(rows),
    "split": dict(split_ct), "n_holdout": split_ct["val"] + split_ct["test"],
    **CLINICAL["BREAST"], "endpoints": ep_rows,
}

# ---------- cross-cancer (LUNG/COLORECTAL/GASTRIC/HEADNECK) ----------
CC_MAP = {
    "LUNG": ("LUNG_NSCLC", ["egfr_activating", "kras_g12c", "histology_lusc"]),
    "COLORECTAL": ("COLORECTAL", ["braf_v600e"]),
    "GASTRIC": ("GASTRIC_STAD", ["msi_h", "erbb2_amp", "lauren_diffuse", "ebv"]),
    "HEADNECK": ("HEADNECK_HNSC", ["hpv_pos", "egfr_amp", "grade_high"]),
}
for cancer, (dirname, endpoints) in CC_MAP.items():
    full = CC / dirname / "full"
    labels = list(csv.DictReader(open(full / "patient_labels.csv")))
    split = list(csv.DictReader(open(full / "split.csv")))
    split_ct = Counter(r["split"] for r in split)
    mil = json.load(open(full / "mil_cost_results.json"))
    n_slides = mil["n_slides"]

    ep_rows = {}
    for ep in endpoints:
        has_col = "has_" + {"egfr_activating": "egfr", "kras_g12c": "kras_g12c",
                             "histology_lusc": "histology", "braf_v600e": "braf",
                             "msi_h": "msi", "erbb2_amp": "erbb2_amp",
                             "lauren_diffuse": "lauren", "ebv": "ebv",
                             "hpv_pos": "hpv", "egfr_amp": "egfr_amp",
                             "grade_high": "grade"}[ep]
        n_has = sum(1 for r in labels if r.get(has_col) == "1")
        n_pos = sum(1 for r in labels if r.get(has_col) == "1" and r.get(ep) == "1")
        holdout_rec = mil["endpoints"].get(ep, {}).get("real", {})
        ep_rows[ep] = {
            "n_total_cohort": len(labels), "n_has_label": n_has, "n_pos_cohort": n_pos,
            "missing_pct": round(100 * (1 - n_has / len(labels)), 1),
            "n_holdout": holdout_rec.get("n_holdout_patients"), "n_pos_holdout": holdout_rec.get("n_pos"),
            "assay_source": ASSAY_SOURCE[ep],
        }
    master["cancers"][cancer] = {
        "n_patients": len(labels), "n_slides": n_slides,
        "split": dict(split_ct), "n_holdout": split_ct["val"] + split_ct["test"],
        **CLINICAL[cancer], "endpoints": ep_rows,
    }

out = HERE / "table1_master.json"
json.dump(master, open(out, "w"), indent=2, ensure_ascii=False)
print(f"Saved {out}")


# ---------- TABLE1.md ----------
def stagepct(d, key):
    tot = sum(d.get(k, 0) for k in ("I", "II", "III", "IV", "missing"))
    n = d.get(key, 0)
    return f"{n} ({100*n/tot:.0f}%)" if tot else "—"


lines = ["# Table 1 — 코호트 baseline 특성 (5암종)", "",
         "`claim_level: descriptive` — 사전등록 대상 없음(가설 검정 아님). "
         "모든 수치는 `table1_master.json`(정본)에서 그대로 인용, 이 문서에서 재계산 없음.", "",
         "| 암종 | N 환자 | N 슬라이드 | Train/Val/Test | 나이 중앙값(IQR) | 여성 % | "
         "Stage I | II | III | IV | missing | Grade 커버리지 | TSS site 수 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
DISPLAY = {"BREAST": "유방", "LUNG": "폐", "COLORECTAL": "대장", "GASTRIC": "위", "HEADNECK": "두경부"}
for cancer in ["BREAST", "LUNG", "COLORECTAL", "GASTRIC", "HEADNECK"]:
    c = master["cancers"][cancer]
    age = c["age"]
    age_s = f"{age['median']} ({age['iqr'][0]:.0f}–{age['iqr'][1]:.0f}, n={age['n']})" if age else "—"
    sex = c["sex_dist"]
    tot_sex = sum(sex.values())
    female_pct = f"{100*sex.get('Female',0)/tot_sex:.0f}%" if tot_sex else "—"
    sd = c["stage_dist"]
    gc = f"{c['grade_coverage_n']}/{c['n_patients']} ({c['grade_coverage_pct']}%)"
    sp = c["split"]
    lines.append(
        f"| {DISPLAY[cancer]} | {c['n_patients']} | {c['n_slides']} | "
        f"{sp.get('train',0)}/{sp.get('val',0)}/{sp.get('test',0)} | {age_s} | {female_pct} | "
        f"{stagepct(sd,'I')} | {stagepct(sd,'II')} | {stagepct(sd,'III')} | {stagepct(sd,'IV')} | "
        f"{stagepct(sd,'missing')} | {gc} | {c['tss_n_sites']} |"
    )

lines += ["", "## Table 1b — 엔드포인트별 유병률·결측 (사전등록 임계 n_pos≥25 대비)", "",
          "| 암종 | 엔드포인트 | assay source | 전체 코호트 라벨 결측 | 유병률(코호트 전체) | "
          "holdout n(denominator) | holdout n_pos | n_pos≥25? |",
          "|---|---|---|---|---|---|---|---|"]
for cancer in ["BREAST", "LUNG", "COLORECTAL", "GASTRIC", "HEADNECK"]:
    c = master["cancers"][cancer]
    for ep, e in c["endpoints"].items():
        if cancer == "BREAST":
            n_pos_h = e["n_pos"]
            if ep == "pam50":
                cd = e["class_dist"]
                prev = "; ".join(f"{k}={v}" for k, v in sorted(cd.items(), key=lambda x: -x[1]))
                gate = "n/a(다중클래스, 이진 유병률 미정의)"
            else:
                prev = f"{e['n_pos']}/{e['n_has_label']} ({100*e['n_pos']/e['n_has_label']:.0f}%)" if e["n_has_label"] else "—"
                gate = "n/a(전체 코호트 표기, holdout 분리 미실시)"
        else:
            n_pos_h = e["n_pos_holdout"]
            prev = f"{e['n_pos_cohort']}/{e['n_has_label']} ({100*e['n_pos_cohort']/e['n_has_label']:.0f}%)" if e["n_has_label"] else "—"
            gate = ("✅" if (n_pos_h or 0) >= 25 else "⚠️ exploratory(<25)") if n_pos_h is not None else "—"
        lines.append(f"| {DISPLAY[cancer]} | {ep} | {e['assay_source']} | {e['missing_pct']}% | "
                     f"{prev} | {e.get('n_holdout', e.get('n_holdout_or_total','—'))} | "
                     f"{n_pos_h if n_pos_h is not None else '—'} | {gate} |")

(HERE / "TABLE1.md").write_text("\n".join(lines) + "\n")
print(f"Saved {HERE/'TABLE1.md'}")


# ---------- PARTICIPANT_FLOW.md ----------
pf = ["# Participant flow — 5암종 (TRIPOD+AI 13b 짝)", "",
      "`n식별` = patient_labels.csv/manifest에 라벨이 조인된 환자 수(=GDC 매니페스트에서 "
      "H&E 슬라이드+임상데이터 결합 가능 subset, 이미 필터링된 상태 — raw GDC 전체 대비 "
      "제외 사유는 각 코호트 원 매니페스트 문서 참조). 여기서부터 아래로: 라벨 결측 없는 "
      "환자 → train/holdout 분리.", "",
      "| 암종 | n(라벨 조인, 시작점) | n(슬라이드 보유) | n(train) | n(holdout=val+test) |",
      "|---|---|---|---|---|"]
for cancer in ["BREAST", "LUNG", "COLORECTAL", "GASTRIC", "HEADNECK"]:
    c = master["cancers"][cancer]
    sp = c["split"]
    pf.append(f"| {DISPLAY[cancer]} | {c['n_patients']} | {c['n_slides']} | "
              f"{sp.get('train',0)} | {c['n_holdout']} |")
pf += ["", "엔드포인트별 최종 분석 대상(holdout denominator)은 Table 1b 참조 — "
       "암종 안에서도 엔드포인트마다 라벨 결측 패턴이 달라 holdout n이 다르다(예: 위 "
       "lauren_diffuse n=58 vs msi_h n=107, 같은 GASTRIC holdout 132명 중 라벨 있는 하위집합만)."]
(HERE / "PARTICIPANT_FLOW.md").write_text("\n".join(pf) + "\n")
print(f"Saved {HERE/'PARTICIPANT_FLOW.md'}")
print("DONE_BUILD_TABLE1")

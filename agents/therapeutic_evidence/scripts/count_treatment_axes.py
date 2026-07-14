"""BIOP02-52 C1 Go/No-go gate — 치료축별 BRCA 세포주 카운트

결과 기준: ER+ ≥5, HER2+ ≥5, TNBC ≥5 모두 통과 시 Go
출력: /workspace/experiments/jhans/20260702_consistency/axis_counts.json
"""
import json, logging, sys
from pathlib import Path
from datetime import datetime
import pandas as pd

DATA_DIR = Path("/workspace/data/BIOP02-52")
OUT_DIR  = Path("/workspace/experiments/jhans/20260702_consistency")
OUT_DIR.mkdir(parents=True, exist_ok=True)

log_file = OUT_DIR / f"count_axes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)])
log = logging.getLogger()
log.info("BIOP02-52 C1 Go/No-go 세포주 카운트 시작")

# ── GDSC BRCA 세포주 ─────────────────────────────────────────
log.info("[Step 1] GDSC2 로딩 (CANCER_TYPE = Breast Carcinoma)")
gdsc = pd.read_excel(DATA_DIR / "GDSC2_fitted_dose_response_27Oct23.xlsx")
gdsc_brca = gdsc[gdsc["CANCER_TYPE"] == "Breast Carcinoma"]
brca_models = gdsc_brca["SANGER_MODEL_ID"].unique()
log.info(f"  GDSC BRCA cell lines: {len(brca_models)}개")

# ── Model.csv 서브타입 태깅 ──────────────────────────────────
log.info("[Step 2] Model.csv 서브타입 태깅 (ModelSubtypeFeatures)")
model = pd.read_csv(DATA_DIR / "Model.csv")
brca_model = model[model["SangerModelID"].isin(brca_models)].copy()

def tag_subtype(s):
    if not isinstance(s, str):
        return "Unknown"
    s_up = s.upper()
    has_er  = "ER_POSITIVE" in s_up or "ER+" in s_up
    has_her = "HER2_POSITIVE" in s_up or "HER2+" in s_up or "ERBB2" in s_up
    if has_her:
        return "HER2+"
    if has_er:
        return "ER+"
    return "TNBC"

brca_model["subtype"] = brca_model["ModelSubtypeFeatures"].apply(tag_subtype)
counts = brca_model["subtype"].value_counts().to_dict()
total  = len(brca_model)
log.info(f"  서브타입 분포: {counts}  (total={total})")

# ── Lapatinib / Afatinib × HER2+ 확인 ───────────────────────
log.info("[Step 3] 치료축 약물 × 서브타입 교차 확인")
her2_models = set(brca_model[brca_model["subtype"] == "HER2+"]["SangerModelID"])
for drug in ["Lapatinib", "Afatinib"]:
    n = gdsc_brca[
        (gdsc_brca["DRUG_NAME"].str.upper() == drug.upper()) &
        (gdsc_brca["SANGER_MODEL_ID"].isin(her2_models))
    ]["SANGER_MODEL_ID"].nunique()
    log.info(f"  {drug} × HER2+: {n}개 세포주")

# ── Go/No-go 판정 ─────────────────────────────────────────────
THRESHOLD = 5
er_n   = counts.get("ER+",   0)
her2_n = counts.get("HER2+", 0)
tnbc_n = counts.get("TNBC",  0)

go_er   = er_n   >= THRESHOLD
go_her2 = her2_n >= THRESHOLD
go_tnbc = tnbc_n >= THRESHOLD
overall = "Go" if (go_er and go_her2 and go_tnbc) else "No-go"

result = {
    "ticket": "BIOP02-52", "gate": "C1",
    "threshold": THRESHOLD,
    "total_brca_cl": total,
    "ER+":   {"n": er_n,   "pass": go_er},
    "HER2+": {"n": her2_n, "pass": go_her2},
    "TNBC":  {"n": tnbc_n, "pass": go_tnbc},
    "verdict": overall,
}
with open(OUT_DIR / "axis_counts.json", "w") as f:
    json.dump(result, f, indent=2)

log.info("=" * 50)
log.info(f"  ER+:   {er_n}개  {'✅' if go_er   else '❌'}")
log.info(f"  HER2+: {her2_n}개  {'✅' if go_her2 else '❌'}")
log.info(f"  TNBC:  {tnbc_n}개  {'✅' if go_tnbc else '❌'}")
log.info(f"  C1 판정: {overall}")
log.info("=" * 50)
log.info(f"완료! 로그: {log_file}")

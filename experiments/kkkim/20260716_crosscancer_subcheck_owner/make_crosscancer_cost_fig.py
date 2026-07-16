#!/usr/bin/env python3
"""BIOP02-96 — cross-cancer cost-of-substitution 그림 (owner=kkkim).

검증된 JSON에서 직접 수치를 읽어(하드코딩 없음) 세 암종의 치환비용 비대칭을 그린다.
- 정의: cost_of_substitution_targeted (misroute_rate × targeted-축 치료거리). 세 암종 동일 정의라 비교 가능.
- BRCA는 receptor-status 라우팅(patient_routing_cost_receptor.json), CRC/폐는 mil_cost_results.json.
- claim_level=hypothesis_only, critic_status=pending → DRAFT, 논문 headline 승격 금지(그림에 명시).
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 한글 폰트 (tofu 방지: family를 직접 리스트로)
for fp in ["/home/kkkim/.fonts/NanumGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        break
plt.rcParams["font.family"] = ["NanumGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = "/home/kkkim/project/BioProject02"

def J(p): return json.load(open(os.path.join(ROOT, p)))

# --- 검증 JSON에서 축별 (misroute, cost, n) 추출 ---
brca = J("experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost_receptor.json")["per_axis"]
crc  = J("experiments/crosscancer/COLORECTAL/full/mil_cost_results.json")["cost_of_substitution_targeted"]["per_axis"]
lung = J("experiments/crosscancer/LUNG_NSCLC/full/mil_cost_results.json")["cost_of_substitution_targeted"]["per_axis"]

# 각 암종: (쉬운축, 어려운 표적축) — 라벨, misroute, cost, n
def ax(d, k): return (d[k]["misroute_rate"], d[k]["mean_cost"], d[k]["n"])
data = [
    ("유방 (BRCA)",   ("endocrine", *ax(brca, "endocrine")), ("antiHER2",       *ax(brca, "antiHER2"))),
    ("대장 (CRC)",    ("baseline",  *ax(crc,  "baseline")),  ("antiBRAF",       *ax(crc,  "antiBRAF"))),
    ("폐 (NSCLC)",    ("chemo",     *ax(lung, "chemo")),     ("antiKRAS-G12C",  *ax(lung, "antiKRAS_G12C"))),
]

fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
EASY, HARD = "#4C78A8", "#E45756"  # 파랑=쉬운축, 빨강=표적축
cancers = [d[0] for d in data]
x = range(len(cancers)); w = 0.36

for col, (metric_i, title, ylab) in enumerate([
    (1, "① 오라우팅율 (misroute rate)\n측정 마커 vs H&E-예측 마커 라우팅 불일치 — 거리무관·비교가능", "오라우팅율"),
    (2, "② 치환비용 (mean cost)\nmisroute × targeted-축 치료거리 (동일 정의)", "치환비용"),
]):
    A = axes[col]
    easy_v = [d[1][metric_i] for d in data]
    hard_v = [d[2][metric_i] for d in data]
    b1 = A.bar([i - w/2 for i in x], easy_v, w, color=EASY, label="쉬운 축 (형태상관물 있음)")
    b2 = A.bar([i + w/2 for i in x], hard_v, w, color=HARD, label="표적 변이축 (H&E-blind)")
    # 값 라벨(막대 위) + 축이름·n 주석(그 위, 겹침 방지 offset)
    for b in list(b1) + list(b2):
        A.text(b.get_x() + b.get_width()/2, b.get_height() + 0.012, f"{b.get_height():.3f}",
               ha="center", va="bottom", fontsize=8, fontweight="bold")
    for i, d in enumerate(data):
        A.annotate(f"{d[1][0]}\n(n={d[1][3]})", (i - w/2, easy_v[i]), textcoords="offset points",
                   xytext=(0, 20), ha="center", va="bottom", fontsize=7.5, color="#555")
        A.annotate(f"{d[2][0]}\n(n={d[2][3]})", (i + w/2, hard_v[i]), textcoords="offset points",
                   xytext=(0, 20), ha="center", va="bottom", fontsize=7.5, color="#555")
    A.set_xticks(list(x)); A.set_xticklabels(cancers, fontsize=10)
    A.set_ylim(0, 1.18); A.set_ylabel(ylab)
    A.set_title(title, fontsize=9.5)
    A.legend(fontsize=8, loc="upper left")
    A.grid(axis="y", alpha=0.25)

fig.suptitle("Cross-cancer 치환비용 비대칭 — 표적 변이축은 H&E-blind (BRCA HER2 패턴 재현)   [BIOP02-96]",
             fontsize=12, fontweight="bold")
fig.text(0.5, 0.005,
         "DRAFT · claim_level=hypothesis_only · critic_status=pending (논문 headline 승격 전 Critic 서명 필요) · "
         "source: patient_routing_cost_receptor.json + mil_cost_results.json (owner=kkkim)",
         ha="center", fontsize=7.5, color="#888")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

OUT = os.path.join(ROOT, "experiments/kkkim/20260716_crosscancer_subcheck_owner")
png, pdf = os.path.join(OUT, "fig_crosscancer_cost.png"), os.path.join(OUT, "fig_crosscancer_cost.pdf")
fig.savefig(png, dpi=170); fig.savefig(pdf)

# provenance JSON
prov = {"figure": "cross-cancer cost-of-substitution asymmetry", "ticket": "BIOP02-96",
        "claim_level": "hypothesis_only", "critic_status": "pending", "owner": "kkkim",
        "definition": "cost_of_substitution_targeted = misroute_rate × targeted-axis therapeutic distance",
        "data": {d[0]: {"easy_axis": {"name": d[1][0], "misroute": d[1][1], "cost": d[1][2], "n": d[1][3]},
                        "hard_axis": {"name": d[2][0], "misroute": d[2][1], "cost": d[2][2], "n": d[2][3]}}
                 for d in data}}
json.dump(prov, open(os.path.join(OUT, "fig_crosscancer_cost.json"), "w"), ensure_ascii=False, indent=2)
print("saved:", png)
print(json.dumps(prov["data"], ensure_ascii=False, indent=1))

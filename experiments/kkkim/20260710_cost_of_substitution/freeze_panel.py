#!/usr/bin/env python3
"""
C1 사전등록(pre-registration): discriminating 약물 패널 고정.

Critic #2/#6/#7 대응 — 최종 receptor-status 라우팅 결과를 보기 '전에' 비용 계산 대상 약물을
고정한다(cherry-pick 방지). 두 패널을 동결:
  (1) external_anchor — 임상 약리로 축이 정해진 표적약(우리 지도 밖 근거). 순환성 회피용 primary.
  (2) data_driven    — frozen_map에서 gap>=0.5로 뽑힌 discriminating 약물(secondary/보강).
provenance(frozen_map 커밋·타임스탬프) 포함. 한 번 쓰면 이 파일이 등록본.
"""
from pathlib import Path
import json, subprocess, datetime

HERE = Path(__file__).parent
fm = json.loads((HERE / "frozen_map.json").read_text())
zmap = fm["frozen_map_axis_to_drug_z"]
axes = list(zmap.keys())
allmap = {}  # drug -> {axis: z}
for a in axes:
    for d, z in zmap[a].items():
        allmap.setdefault(d, {})[a] = z

# (1) external anchor: 임상 확립 표적약 -> 의도 축 (우리 지도가 아닌 약리로 지정)
ANCHOR = {
    "antiHER2":  ["Lapatinib", "Afatinib", "Sapitinib", "Tucatinib", "Neratinib"],   # HER2/EGFR TKI
    "endocrine": ["Fulvestrant", "Tamoxifen", "Palbociclib", "Ribociclib",           # ER / CDK4-6
                  "Alpelisib", "Taselisib", "Pictilisib", "AZD8186", "Capivasertib"],# PI3K/AKT(luminal 편향)
    "chemo":     ["Paclitaxel", "Docetaxel", "Cisplatin", "Gemcitabine",             # 세포독성
                  "Doxorubicin", "Vinorelbine", "Olaparib", "Talazoparib"],          # +PARP(basal/BRCA)
}
def find(name):  # 지도에 있는(부분매칭) 약물명 반환
    hits = [d for d in allmap if name.lower() in d.lower()]
    return hits[0] if hits else None

anchor_resolved = {}
for axis, drugs in ANCHOR.items():
    got = []
    for nm in drugs:
        d = find(nm)
        if d:
            zs = allmap[d]
            most = min(zs, key=zs.get) if zs else None
            got.append({"drug": d, "intended_axis": axis, "in_map": True,
                        "z": {a: zs.get(a) for a in axes},
                        "map_most_sensitive_axis": most,
                        "positive_control_ok": most == axis})
        else:
            got.append({"drug": nm, "intended_axis": axis, "in_map": False})
    anchor_resolved[axis] = got

# (2) data-driven gap>=0.5
common = [d for d in allmap if len(allmap[d]) == len(axes)]
def gap(d):
    vs = list(allmap[d].values()); return round(max(vs) - min(vs), 3)
data_driven = sorted([{"drug": d, "gap": gap(d),
                       "z": {a: allmap[d][a] for a in axes},
                       "most_sensitive_axis": min(allmap[d], key=allmap[d].get)}
                      for d in common if gap(d) >= 0.5],
                     key=lambda r: r["gap"], reverse=True)

try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE).decode().strip()[:9]
except Exception:
    commit = "unknown"

out = {
    "artifact": "PRE-REGISTERED discriminating drug panel (C1 cost-of-substitution)",
    "purpose": "최종 receptor-status 라우팅 결과 관측 전 고정 — Critic #2/#6/#7 cherry-pick 방지",
    "frozen_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "frozen_map_source": "frozen_map.json",
    "repo_commit_at_freeze": commit,
    "axes": axes,
    "primary_panel_external_anchor": {
        "rationale": "축 배정을 임상 약리(지도 밖)로 고정 → subtype_only 순환성 회피",
        "n_resolved_in_map": sum(1 for a in anchor_resolved for x in anchor_resolved[a] if x.get("in_map")),
        "by_axis": anchor_resolved,
        "positive_control_summary": {
            a: f"{sum(1 for x in anchor_resolved[a] if x.get('positive_control_ok'))}/"
               f"{sum(1 for x in anchor_resolved[a] if x.get('in_map'))} 지도 최민감축=의도축"
            for a in axes},
    },
    "secondary_panel_data_driven": {
        "criterion": "frozen_map 3축 공통약물 중 gap(max-min z)>=0.5",
        "n": len(data_driven), "drugs": data_driven,
    },
}
(HERE / "preregistered_drug_panel.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print("frozen_at:", out["frozen_at"], "| commit:", commit)
print("external anchor positive-control:")
for a in axes:
    print(f"  {a:10}: {out['primary_panel_external_anchor']['positive_control_summary'][a]}")
print(f"data-driven panel: {len(data_driven)} drugs (gap>=0.5)")
print("wrote preregistered_drug_panel.json")

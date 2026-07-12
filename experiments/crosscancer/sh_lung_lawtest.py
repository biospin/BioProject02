#!/usr/bin/env python3
"""
폐 법칙 held-out 검정 채점: mil_cost_results.json(base) + mil_subtype_results.json 병합 →
SUBSTITUTABILITY_LAW_PREREGISTRATION.md의 폐 봉인 예측 4개를 관측과 대조.

exploratory(n_pos<25)면 자동 INCONCLUSIVE (예측적중이어도 '확증' 금지 → 'consistent with'까지만).
verdict는 confirm/refute/inconclusive 대칭 적용(과소검정력이 나쁜 결과를 가려주지 않게).
출력: 콘솔 표 + 병합된 mil_cost_results.json(subtype endpoints 편입).
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
D = HERE / "LUNG_NSCLC" / "full"
EXPL = 25

def load(p):
    return json.loads(p.read_text()) if p.exists() else None

def ep_row(r):
    real = (r or {}).get("real", {})
    return {
        "auc": real.get("auc"),
        "ci": real.get("ci95"),
        "n_pos": real.get("n_pos"),
        "n_hold": real.get("n_holdout_patients"),
        "shuffle": (r or {}).get("shuffle_null", {}).get("auc"),
        "exploratory": bool((real.get("n_pos") or 0) < EXPL),
    }

def main():
    base = load(D / "mil_cost_results.json")
    sub = load(D / "mil_subtype_results.json")
    if base is None:
        print("base mil_cost_results.json 없음 — 중단"); return
    # 병합: subtype endpoints를 base endpoints에 편입
    if sub:
        base.setdefault("subtype_task", {"ovr_restriction": sub.get("ovr_restriction")})
        for k, v in sub.get("endpoints", {}).items():
            base["endpoints"][k] = v
        (D / "mil_cost_results.json").write_text(json.dumps(base, indent=2, ensure_ascii=False))
        print("merged subtype endpoints into mil_cost_results.json")
    E = {k: ep_row(v) for k, v in base["endpoints"].items()}
    print("\n=== endpoint 요약 ===")
    for k, r in E.items():
        print(f"  {k:22s} AUC={r['auc']} CI{r['ci']} n+={r['n_pos']}/{r['n_hold']} shuffle={r['shuffle']} {'[EXPL]' if r['exploratory'] else ''}")

    print("\n=== 법칙 held-out 검정 (폐, 봉인 예측 대조) ===")
    h = E.get("histology_lusc", {}); eg = E.get("egfr_activating", {}); kr = E.get("kras_g12c", {})
    # 예측1: 조직형 >= 0.93 (양성대조) — 유일한 검정력 충분 endpoint
    if h.get("auc") is not None:
        v1 = "부합(CONFIRM)" if h["auc"] >= 0.93 else ("경계미달" if h["auc"] >= 0.85 else "반증(REFUTE)")
        print(f"  [1] 조직형 LUAD/LUSC >=0.93: 관측 {h['auc']} CI{h['ci']} n+={h['n_pos']} → {v1}"
              f" (검정력 충분, 유일한 진짜 검정)")
    # 예측2: EGFR 0.75-0.89, near-random 아님
    if eg.get("auc") is not None:
        inband = 0.75 <= eg["auc"] <= 0.89
        note = "INCONCLUSIVE(exploratory n_pos<25)" if eg["exploratory"] else ("대역내" if inband else "대역밖")
        print(f"  [2] EGFR 등급적 0.75–0.89: 관측 {eg['auc']} CI{eg['ci']} n+={eg['n_pos']} → {note}"
              f" (점추정 대역={'yes' if inband else 'no'}; 검정력 부족→consistent with까지만)")
    # 예측3: KRAS <=0.65 AND EGFR>KRAS 순서
    if kr.get("auc") is not None:
        order = (eg.get("auc") is not None and eg["auc"] > kr["auc"])
        note = "INCONCLUSIVE(exploratory, CI 광범위)" if (kr["exploratory"] or eg.get("exploratory")) else "testable"
        print(f"  [3] KRAS <=0.65 & EGFR>KRAS: KRAS 관측 {kr['auc']} CI{kr['ci']} n+={kr['n_pos']}; "
              f"EGFR>KRAS 점추정={'yes' if order else 'no'} → {note}"
              f" (n_pos 14–15: 순서 어느 방향도 확립 불가)")
    # 예측4: TRU가 전사체 아형 중 최고
    lu = {k: E[k] for k in E if k.startswith("luad_") and E[k].get("auc") is not None}
    if lu:
        ranked = sorted(lu.items(), key=lambda kv: kv[1]["auc"], reverse=True)
        top = ranked[0][0]
        tru = E.get("luad_TRU_vs_rest", {})
        tru_top = top == "luad_TRU_vs_rest"
        comparators_expl = any(v["exploratory"] for k, v in lu.items() if k != "luad_TRU_vs_rest")
        note = "INCONCLUSIVE(비교대상 PI/PP exploratory → 순위 검정 불가)" if comparators_expl else "testable"
        print(f"  [4] TRU 최고: TRU AUC={tru.get('auc')} n+={tru.get('n_pos')}; "
              f"LUAD 아형 순위={[ (k.replace('luad_','').replace('_vs_rest',''), v['auc']) for k,v in ranked ]}; "
              f"TRU 최상위={'yes' if tru_top else 'no'} → {note}")

if __name__ == "__main__":
    main()

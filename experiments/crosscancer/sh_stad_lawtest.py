#!/usr/bin/env python3
"""
위암(GASTRIC_STAD) 법칙 held-out 검정 채점: mil_cost_results.json →
SUBSTITUTABILITY_LAW_PREREGISTRATION.md 위암 봉인 예측(#5, #6, EBV)을 관측과 대조.

봉인 예측(결과 보기 전 커밋으로 봉인):
  #5 HER2/ERBB2-amp ≤ 0.65 (유방 HER2 0.599 복제) — 핵심 교차장기 검정
  #6 MSI-H ≥ 0.82 (대체가능), Lauren 조직형 ≥ 0.85 (양성대조),
     내부순서 조직형 ≥ MSI > HER2-amp
  EBV exploratory

원칙(폐와 동일):
- exploratory(n_pos<25)면 자동 INCONCLUSIVE (예측 적중이어도 '확증' 금지 → 'consistent with'까지).
- verdict는 confirm/refute/inconclusive 대칭 (과소검정력이 나쁜 결과를 가려주지 않게).
- 사전등록 임계 25는 사후 이동 금지(MSI n_pos=24라도 24로 낮추지 않음).

출력: 콘솔 표. (LAW_TEST.md는 별도 작성)
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
D = HERE / "GASTRIC_STAD" / "full"
EXPL = 25  # 사전등록 임계 — 사후 이동 금지

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
    if base is None:
        print("mil_cost_results.json 없음 — MIL 먼저 실행"); return
    E = {k: ep_row(v) for k, v in base["endpoints"].items()}
    print("\n=== STAD endpoint 요약 ===")
    for k, r in E.items():
        print(f"  {k:16s} AUC={r['auc']} CI{r['ci']} n+={r['n_pos']}/{r['n_hold']} "
              f"shuffle={r['shuffle']} {'[EXPL n_pos<25]' if r['exploratory'] else ''}")

    lau = E.get("lauren_diffuse", {}); msi = E.get("msi_h", {})
    her = E.get("erbb2_amp", {}); ebv = E.get("ebv", {})

    print("\n=== 법칙 held-out 검정 (위암, 봉인 예측 대조) ===")

    # 예측 #6a: Lauren 조직형 >= 0.85 (양성대조) — 유일하게 검정력 충분(n_pos=30)
    if lau.get("auc") is not None:
        v = ("부합(CONFIRM)" if lau["auc"] >= 0.85
             else ("양성대조성립(≥0.75)이나 0.85 미달" if lau["auc"] >= 0.75
                   else "SOFT-FAIL(<0.75 — 데이터희소 vs 파이프라인 구분 필요)"))
        note = "" if not lau["exploratory"] else " [주의: n_pos<25]"
        print(f"  [#6a 양성대조] Lauren diffuse ≥0.85: 관측 {lau['auc']} CI{lau['ci']} "
              f"n+={lau['n_pos']} → {v}{note}  (검정력 충분, 유일한 진짜 검정)")

    # 예측 #6b: MSI-H >= 0.82 (대체가능)
    if msi.get("auc") is not None:
        inband = msi["auc"] >= 0.82
        if msi["exploratory"]:
            note = f"INCONCLUSIVE(exploratory n_pos={msi['n_pos']}<25) — 점추정 {'대역내' if inband else '대역밖'}, consistent with까지만"
        else:
            note = "부합(CONFIRM)" if inband else "반증가능성(대역밖)"
        print(f"  [#6b] MSI-H ≥0.82: 관측 {msi['auc']} CI{msi['ci']} n+={msi['n_pos']} → {note}")

    # 예측 #5: HER2/ERBB2-amp <= 0.65 (유방 HER2 0.599 복제) — 핵심 교차장기
    if her.get("auc") is not None:
        inband = her["auc"] <= 0.65
        refute_sig = her["auc"] >= 0.8  # 반증 시나리오: 필수 마커가 잘 예측
        if her["exploratory"]:
            base_note = ("consistent with 유방 0.599(≤0.65)" if inband
                         else ("점추정 대역밖(>0.65)" if not refute_sig
                               else "점추정 ≥0.8 — 잠재적 반증신호(대체가능인데 blind 아님)"))
            note = f"INCONCLUSIVE(exploratory n_pos={her['n_pos']}<25) — {base_note}. 확증도 반증도 불가"
        else:
            note = "부합(유방 복제 CONFIRM)" if inband else ("반증(REFUTE ≥0.8)" if refute_sig else "대역밖")
        print(f"  [#5 핵심 교차장기] HER2/ERBB2-amp ≤0.65 (유방 0.599 복제): "
              f"관측 {her['auc']} CI{her['ci']} n+={her['n_pos']} → {note}")

    # 예측 #6c: 내부순서 조직형 >= MSI > HER2-amp
    order_pts = [(lau.get("auc"), "Lauren"), (msi.get("auc"), "MSI"), (her.get("auc"), "HER2amp")]
    if all(a is not None for a, _ in order_pts):
        lau_msi = lau["auc"] >= msi["auc"]
        msi_her = msi["auc"] > her["auc"]
        # MSI/HER2 CI 겹침 → MSI>HER2 통계적 확립 불가(둘 다 exploratory)
        msi_her_est = "yes(점추정)" if msi_her else "no(점추정)"
        expl = msi.get("exploratory") or her.get("exploratory")
        note = ("INCONCLUSIVE(MSI·HER2 exploratory, CI 겹침 → MSI>HER2 확립 불가)" if expl
                else "testable")
        print(f"  [#6c 내부순서] 조직형≥MSI>HER2-amp: "
              f"Lauren {lau['auc']} / MSI {msi['auc']} / HER2 {her['auc']} → "
              f"조직형≥MSI={'yes' if lau_msi else 'no'}, MSI>HER2={msi_her_est} → {note}")

    # EBV — exploratory 명시
    if ebv.get("auc") is not None:
        print(f"  [EBV exploratory] 관측 {ebv['auc']} CI{ebv['ci']} n+={ebv['n_pos']} "
              f"→ INCONCLUSIVE(사전 exploratory 지정, n_pos={ebv['n_pos']})")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
두경부(HEADNECK_HNSC) 법칙 held-out 검정 채점: mil_cost_results.json →
SUBSTITUTABILITY_LAW_PREREGISTRATION.md 두경부 봉인 예측을 관측과 대조.

봉인 예측(결과 보기 전 커밋으로 봉인, PREREG 표 28행 + 원칙 #7):
  HPV 상태 → 대체가능(비각화·basaloid = 바이러스축 형태 가시): held-out AUROC ≥ 0.80
  EGFR(증폭/과발현) → 등급적/필수(대체로 형태 상관물 없음): held-out AUROC ≤ 0.70, HPV보다 낮음
  grade/조직형 → 양성대조(분화도=H&E). SCC라 강한 대역(≥0.85) 아닐 수 있음 → soft(≥0.75 sanity).
  내부순서: HPV > EGFR (형태 상관물 있는 바이러스축이 형태 상관물 없는 변이축보다 높다)

원칙(폐·위암과 동일, 대칭 verdict):
- exploratory(n_pos<25)면 자동 INCONCLUSIVE (예측 적중이어도 '확증' 금지 → 'consistent with'까지).
- verdict는 confirm/refute/inconclusive 대칭 (과소검정력이 나쁜 결과를 가려주지 않게).
- 사전등록 임계 25는 사후 이동 금지.

출력: 콘솔 표. (LAW_TEST.md는 별도 작성)
Usage: python sh_hnsc_lawtest.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
D = HERE / "HEADNECK_HNSC" / "full"
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
    print("\n=== HNSC endpoint 요약 ===")
    for k, r in E.items():
        print(f"  {k:16s} AUC={r['auc']} CI{r['ci']} n+={r['n_pos']}/{r['n_hold']} "
              f"shuffle={r['shuffle']} {'[EXPL n_pos<25]' if r['exploratory'] else ''}")

    hpv = E.get("hpv_pos", {}); egfr = E.get("egfr_amp", {}); grade = E.get("grade_high", {})

    print("\n=== 법칙 held-out 검정 (두경부, 봉인 예측 대조) ===")

    # 예측 #HPV: HPV >= 0.80 (대체가능, 바이러스축 형태 가시) — 핵심 검정
    if hpv.get("auc") is not None:
        inband = hpv["auc"] >= 0.80
        refute_sig = hpv["auc"] <= 0.60  # 반증: 대체가능 예측했는데 near-random
        if hpv["exploratory"]:
            base_note = ("consistent with 대체가능(≥0.80)" if inband
                         else ("점추정 near-random(≤0.60) — 잠재적 반증신호" if refute_sig
                               else "점추정 중간대역(0.60~0.80)"))
            note = f"INCONCLUSIVE(exploratory n_pos={hpv['n_pos']}<25) — {base_note}. 확증도 반증도 불가"
        else:
            note = ("부합(대체가능 CONFIRM ≥0.80)" if inband
                    else ("반증(REFUTE ≤0.60 near-random)" if refute_sig else "대역밖(0.60~0.80)"))
        print(f"  [#HPV 핵심] HPV 상태 ≥0.80 (대체가능·바이러스축 형태): "
              f"관측 {hpv['auc']} CI{hpv['ci']} n+={hpv['n_pos']} → {note}")

    # 예측 #EGFR: EGFR-amp <= 0.70 (등급적/필수, 형태 상관물 대체로 없음)
    if egfr.get("auc") is not None:
        inband = egfr["auc"] <= 0.70
        refute_sig = egfr["auc"] >= 0.80
        if egfr["exploratory"]:
            base_note = ("consistent with 형태 상관물 약함(≤0.70)" if inband
                         else ("점추정 ≥0.80 — 잠재적 반증신호(필수인데 잘 예측)" if refute_sig
                               else "점추정 대역밖(0.70~0.80)"))
            note = f"INCONCLUSIVE(exploratory n_pos={egfr['n_pos']}<25) — {base_note}. 확증도 반증도 불가"
        else:
            note = ("부합(CONFIRM ≤0.70)" if inband
                    else ("반증(REFUTE ≥0.80)" if refute_sig else "대역밖"))
        print(f"  [#EGFR] EGFR-amp ≤0.70 (형태 상관물 약함): "
              f"관측 {egfr['auc']} CI{egfr['ci']} n+={egfr['n_pos']} → {note}")

    # 양성대조: grade_high (soft; SCC라 강한 대역 아닐 수 있음, ≥0.75 sanity)
    if grade.get("auc") is not None:
        v = ("부합(강한 형태 ≥0.85)" if grade["auc"] >= 0.85
             else ("양성대조성립(≥0.75)이나 0.85 미달" if grade["auc"] >= 0.75
                   else "SOFT-FAIL(<0.75 — SCC 분화도 약함 vs 파이프라인 구분 필요; HPV≥0.80이 de facto sanity)"))
        note = "" if not grade["exploratory"] else " [주의: n_pos<25]"
        print(f"  [양성대조 soft] grade_high(분화도): 관측 {grade['auc']} CI{grade['ci']} "
              f"n+={grade['n_pos']} → {v}{note}")

    # 내부순서: HPV > EGFR (형태 상관물 있는 바이러스축 > 형태 상관물 없는 변이축)
    if hpv.get("auc") is not None and egfr.get("auc") is not None:
        hpv_gt = hpv["auc"] > egfr["auc"]
        expl = hpv.get("exploratory") or egfr.get("exploratory")
        note = ("INCONCLUSIVE(HPV/EGFR exploratory, CI 겹침 → HPV>EGFR 확립 불가)" if expl
                else "testable")
        print(f"  [내부순서] HPV>EGFR: HPV {hpv['auc']} / EGFR {egfr['auc']} → "
              f"HPV>EGFR={'yes(점추정)' if hpv_gt else 'no(점추정)'} → {note}")


if __name__ == "__main__":
    main()

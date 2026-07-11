#!/usr/bin/env python3
"""
결과 자동 요약 watcher (세션 끊겨도 정리 산출) — detached 실행.

크로스암종 MIL 결과(mil_cost_results.json)가 나오면 사람이 읽을 RESULTS_SUMMARY.md를 생성한다.
판정 자동화: ① 양성대조(histology) 통과 여부 ② endpoint별 real vs shuffle-null 비교로
"H&E-blind(가설 확증) / 예측 가능(예상 밖, 검토 필요)" 구분 ③ cost 요약.
문체: 완결 문장 + 기술 용어 유지(사용자 선호). 판정은 기계적이며 최종 해석·JIRA·시사점은 사람이 확인.
"""
import json, time
from pathlib import Path

HERE = Path(__file__).parent
CANCERS = {"COLORECTAL": ("BRAF_V600E",), "LUNG_NSCLC": ("EGFR_activating", "KRAS_G12C")}
RESULT = lambda c: HERE / c / "full" / "mil_cost_results.json"
SUMMARY = HERE / "RESULTS_SUMMARY.md"
HB = HERE / "SUMMARIZE_HEARTBEAT.log"

def log(m):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {m}"
    with open(HB, "a") as f: f.write(line + "\n")

def verdict(real, shuffle):
    """real vs shuffle-null 자동 판정. 두 결과 모두 원리(형태학 상관물 유무)와 일치할 수 있으며,
    판정은 '이 표적이 어느 범주인가'를 알려준다."""
    if real is None: return "결과 없음"
    if shuffle is None: shuffle = 0.5
    diff = real - shuffle
    if real >= 0.75 and diff >= 0.15:
        return (f"H&E가 예측 가능(real {real} ≫ shuffle {shuffle}) — 이 표적에 형태학적 상관물이 있다는 뜻이며 "
                f"원리와 일치한다. 알려진 생물학과 부합하는지 사람이 확인.")
    if diff < 0.10 or real < 0.6:
        return (f"H&E-blind(real {real} ≈ shuffle {shuffle}) — 이 표적에 형태학적 상관물이 없어 분자검사가 대체 불가하다는 뜻이며 "
                f"유방암 HER2 패턴과 일치한다.")
    return f"경계(real {real} vs shuffle {shuffle}) — 사람 검토 필요."

def fmt_cancer(c, d):
    L = [f"## {c}", ""]
    L.append(f"임베딩 슬라이드 수는 {d.get('n_slides','?')}장이다. claim_level은 {d.get('claim_level','?')}, "
             f"critic_status는 {d.get('critic_status','pending')}이다.")
    pc = d.get("positive_control_gate")
    if pc:
        ok = "통과" if pc.get("pass") else "실패(파이프라인 점검 필요)"
        L.append(f"- **양성대조({pc.get('endpoint')})**: real AUROC {pc.get('auc')}, {ok}. "
                 f"양성대조가 실패하면 아래 변이 결과도 신뢰하기 어렵다.")
    L.append("")
    L.append("### endpoint별 판정 (real vs shuffle-null)")
    for ep, r in d.get("endpoints", {}).items():
        real = r.get("real", {}).get("auc"); ci = r.get("real", {}).get("ci95")
        sh = r.get("shuffle_null", {}).get("auc"); npos = r.get("real", {}).get("n_pos")
        L.append(f"- **{ep}**: real AUROC {real} (CI {ci}, 양성 {npos}명), shuffle-null {sh}. "
                 f"→ {verdict(real, sh)}.")
    ct = d.get("cost_of_substitution_targeted", {}).get("per_axis")
    if ct:
        L.append("")
        L.append("### 치환비용(cost-of-substitution, 측정 vs 예측 축 라우팅)")
        for ax, v in ct.items():
            L.append(f"- {ax}: mis-route {v.get('misroute_rate')}, mean_cost {v.get('mean_cost')} (n={v.get('n')})")
    mr = d.get("endpoint_misroute_incl_histology")
    if mr:
        L.append("")
        L.append("### endpoint별 오분류율(histology 포함 — H&E-blind vs triage 대비)")
        for ep, v in mr.items():
            L.append(f"- {ep}: mis-route {v.get('misroute_rate')} (AUROC {v.get('auc')}, {v.get('type')})")
    L.append("")
    return "\n".join(L)

def build_summary(available):
    head = ["# Cross-cancer MIL + cost 결과 요약 (자동 생성)", "",
            f"생성 시각(UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
            "",
            "> 이 문서는 watcher가 MIL 결과에서 자동 생성한 것이다. 판정은 기계적 규칙(real vs shuffle-null)이며, "
            "최종 해석·시사점 갱신·JIRA 반영은 사람이 확인해야 한다.",
            "",
            "## 핵심 가설과 읽는 법",
            "유방암에서 얻은 가설은, H&E-예측 아형이 표적에 형태학적 상관물이 있을 때만 분자검사를 대신할 수 있다는 것이다. "
            "따라서 형태학적 상관물이 있는 표적(예: BRAF-대장은 serrated/MSI를 동반)은 H&E가 예측하고, 상관물이 약한 표적"
            "(HER2 증폭, EGFR 등)은 H&E-blind일 것으로 본다. 두 결과 모두 원리와 일치할 수 있으며, real vs shuffle-null 비교는 "
            "각 표적이 어느 범주인지 알려준다. 양성대조인 histology(LUAD/LUSC)는 형태학 그 자체이므로 real이 shuffle을 크게 "
            "상회해야 파이프라인이 정상임을 뜻한다.", ""]
    body = [fmt_cancer(c, json.loads(RESULT(c).read_text())) for c in available]
    return "\n".join(head + body)

def main():
    log("=== SUMMARIZE watcher 시작 — MIL 결과 대기 ===")
    seen = set()
    for _ in range(300):                       # 최대 ~50h 폴링
        available = [c for c in CANCERS if RESULT(c).exists()]
        if set(available) != seen and available:
            SUMMARY.write_text(build_summary(available))
            log(f"RESULTS_SUMMARY.md 갱신 — 완료 암종: {available}")
            seen = set(available)
        if len(available) == len(CANCERS):
            (HERE / "SUMMARIZE_DONE.json").write_text(json.dumps(
                {"finished_utc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), "cancers": available}))
            log("=== 전 암종 요약 완료 ===")
            return
        time.sleep(600)
    log("watcher 타임아웃(50h) — 부분 요약만 존재")

if __name__ == "__main__":
    main()

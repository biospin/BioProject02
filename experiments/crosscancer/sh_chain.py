#!/usr/bin/env python3
"""
STAD·HNSC 오케스트레이터 (격리판) — 임베딩 완료 감지 → MIL → 법칙 held-out 검정표.

- 게이트: EMBED_STADHNSC.done sentinel 또는 sh_embed 마스터 종료 시 시작(GPU 경합 회피).
- 각 암종 sh_mil_cost 실행(순차, 단일 GPU). 결과=<cancer>/full/mil_cost_results.json.
- 법칙 검정: SUBSTITUTABILITY_LAW_PREREGISTRATION.md 사전예측 vs 관측 AUROC → 부합/반증 표.
  LAW_TEST.md(파이프라인 산출 데이터 아티팩트, mil_cost_results.json에서 자동 생성) per 폴더.
- detached-safe: 하트비트 + DONE sentinel. 결과 이미 있으면 skip(--force 재계산).

Usage: python sh_chain.py [--device cuda:2] [--force]
"""
import subprocess, time, json, sys, argparse
from pathlib import Path

HERE = Path(__file__).parent
PY = "/home/kkkim/miniconda3/bin/python3"
HB = HERE / "SH_CHAIN_HEARTBEAT.log"
CANCERS = ["GASTRIC_STAD", "HEADNECK_HNSC"]

# 사전등록 (SUBSTITUTABILITY_LAW_PREREGISTRATION.md, 봉인).
#  op: le=예측 AUROC<=thr(필수), ge=예측 AUROC>=thr(대체가능).
#  ⚠️ 예측(prediction) 임계 ≠ 반증(refutation) 임계. prereg 반증기준(line48-49):
#     필수(op=le) 반증 = AUROC >= refute_thr(0.8);  대체가능(op=ge) 반증 = AUROC <= refute_thr(0.6).
#  → CONFIRM/REFUTE는 반증임계 기준(CI 경계가 넘어야), 예측적중은 별도 컬럼.
PREREG = {
 "GASTRIC_STAD": {
   "erbb2_amp":    {"op":"le","thr":0.65,"refute_thr":0.80,"cls":"필수(형태 조용)","note":"유방 HER2(0.599) 같은 변이·다른 장기 — 하이라이트"},
   "msi_h":        {"op":"ge","thr":0.82,"refute_thr":0.60,"cls":"대체가능(TIL/수질형)"},
   "lauren_diffuse":{"op":"ge","thr":0.85,"refute_thr":0.60,"cls":"양성대조(강한 형태)"},
   "ebv":          {"op":None,"thr":None,"refute_thr":None,"cls":"exploratory(lymphoepithelioma)"},
   "_order":["lauren_diffuse","msi_h","erbb2_amp"],  # 예측 내부순서 lauren≥msi>erbb2 (point-est only)
 },
 "HEADNECK_HNSC": {
   "hpv_pos":   {"op":"ge","thr":0.80,"refute_thr":0.60,"cls":"가시(바이러스 형태축)","note":"핵심 가시축"},
   "egfr_amp":  {"op":"le","thr":0.70,"refute_thr":0.80,"cls":"등급적/필수"},
   "grade_high":{"op":None,"thr":None,"refute_thr":None,"cls":"양성대조 soft(분화도)"},
   "_pairorder":("hpv_pos","egfr_amp"),  # HPV > EGFR (point-est only)
 },
}

def log(m):
    line=f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {m}"
    print(line, flush=True)
    with open(HB,"a") as f: f.write(line+"\n")

def embed_alive():
    r=subprocess.run(["bash","-c","ps -eo cmd | grep 'sh_embed.py' | grep -v grep | wc -l"],
                     capture_output=True, text=True)
    return int(r.stdout.strip() or "0")>0

def emb_count(cancer):
    return len(list((HERE/cancer/"full"/"embeddings").glob("*_uni_embeddings.npy")))

def run_mil(cancer, device):
    out=HERE/cancer/"full"/"mil_cost_results.json"
    log(f"  RUN sh_mil_cost {cancer} on {device}")
    r=subprocess.run([PY, str(HERE/"sh_mil_cost.py"), "--cancer", cancer, "--device", device],
                     capture_output=True, text=True, timeout=21600)
    if r.returncode!=0:
        log(f"  FAIL mil {cancer} rc={r.returncode}: {r.stderr[-800:]}"); return False
    log(f"  OK mil {cancer}\n{r.stdout[-1200:]}")
    return out.exists()

def pred_met(op, thr, auc):
    """예측(tight prediction) 적중 여부 — 점추정 기준(정보용, 법칙판정과 별개)."""
    if auc is None or op is None: return None
    return (auc<=thr) if op=="le" else (auc>=thr)

def law_verdict(cfg, auc, ci, exploratory):
    """법칙판정: 반증임계(refute_thr) 기준. REFUTE는 CI 경계가 반증선을 넘어야.
    exploratory(n_pos<25) 또는 CI가 반증/예측선을 걸치면 INCONCLUSIVE(미결)."""
    op=cfg["op"]; thr=cfg["thr"]; rt=cfg["refute_thr"]
    if auc is None: return "no-data(무데이터)"
    if op is None:  return "exploratory(탐색)"
    lo,hi=(ci if (ci and ci[0] is not None and ci[1] is not None) else (None,None))
    # 반증: 필수(op=le)는 H&E가 잘 예측(CI 하한>=0.8), 대체가능(op=ge)은 H&E blind(CI 상한<=0.6)
    if op=="le" and lo is not None and lo>=rt:  return "반증(REFUTE)"
    if op=="ge" and hi is not None and hi<=rt:  return "반증(REFUTE)"
    if exploratory:                              return "미결(INCONCLUSIVE, n_pos<25)"
    # 검정력 충분 & 반증 아님 → 예측적중이면 CONFIRM, 아니면 부분(미결)
    if pred_met(op,thr,auc):                     return "부합(CONFIRM)"
    return "부분/미결(예측 miss·반증 아님)"

def gen_law_test(cancer):
    rp=HERE/cancer/"full"/"mil_cost_results.json"
    if not rp.exists(): return None
    d=json.loads(rp.read_text()); eps=d.get("endpoints",{})
    pre=PREREG[cancer]
    lines=[f"# 법칙 held-out 검정 — {cancer}",
           "",
           "> 사전등록: SUBSTITUTABILITY_LAW_PREREGISTRATION.md (봉인). claim_level: hypothesis_only · critic_status: pending.",
           "> 자동생성(sh_chain.py) — mil_cost_results.json에서 파생. **커밋 전 사람 검토.**",
           "",
           "| endpoint | 사전분류 | 예측(tight) | 반증선 | 관측 AUROC (CI95) | n_pos/n | 예측적중 | 법칙판정 | exploratory |",
           "|---|---|---|---|---|---|---|---|---|"]
    rows_eval={}
    for ep, cfg in pre.items():
        if ep.startswith("_"): continue
        r=eps.get(ep,{}).get("real",{})
        auc=r.get("auc"); ci=r.get("ci95"); npos=r.get("n_pos"); nh=r.get("n_holdout_patients")
        expl=bool(eps.get(ep,{}).get("exploratory"))
        op=cfg["op"]; thr=cfg["thr"]; rt=cfg["refute_thr"]
        pred = ("blind ≤%.2f"%thr if op=="le" else ("가시 ≥%.2f"%thr if op=="ge" else "—"))
        rline= ("≥%.2f"%rt if op=="le" else ("≤%.2f"%rt if op=="ge" else "—"))
        pm=pred_met(op,thr,auc); pm_s=("적중" if pm else "빗나감") if pm is not None else "—"
        v=law_verdict(cfg,auc,ci,expl)
        rows_eval[ep]=(auc,v,npos,pm)
        lines.append(f"| {ep} | {cfg['cls']} | {pred} | {rline} | {auc} ({ci}) | {npos}/{nh} | {pm_s} | {v} | {'예' if expl else '아니오'} |")
    # 순서 예측
    order_note=[]
    if "_order" in pre:
        seq=pre["_order"]; aucs=[rows_eval.get(e,(None,))[0] for e in seq]
        if all(a is not None for a in aucs):
            ok = aucs[0]>=aucs[1]>aucs[2] if len(aucs)==3 else None
            order_note.append(f"- 내부순서 예측 {'≥'.join(seq)}: 관측 "+" , ".join(f"{e}={a}" for e,a in zip(seq,aucs))+
                              f" → {'부합' if ok else '불일치'} (점추정만, 유의성 미검정)")
    if "_pairorder" in pre:
        a,b=pre["_pairorder"]; aa=rows_eval.get(a,(None,))[0]; bb=rows_eval.get(b,(None,))[0]
        if aa is not None and bb is not None:
            order_note.append(f"- 쌍순서 예측 {a}>{b}: 관측 {a}={aa} vs {b}={bb} → {'부합' if aa>bb else '불일치'} (점추정만, 유의성 미검정)")
    pcg=d.get("positive_control_gate",{})
    lines += ["",
              f"**양성대조**: {pcg.get('endpoint')} AUROC={pcg.get('auc')} pass={pcg.get('pass')} (soft={pcg.get('soft')})",
              ""]+order_note+[""]
    # 하이라이트(STAD erbb2)
    if cancer=="GASTRIC_STAD" and "erbb2_amp" in rows_eval:
        auc,v,npos,pm=rows_eval["erbb2_amp"]
        expl = bool(eps.get("erbb2_amp",{}).get("exploratory"))
        lines += ["## 하이라이트 — 위 HER2/ERBB2-amp vs 유방 HER2(0.599)",
          f"- 관측 AUROC={auc} (n_pos={npos}). 예측=blind≤0.65 (예측적중={'적중' if pm else '빗나감'}); 법칙판정={v}.",
          f"- {'**exploratory(n_pos<25)**: 유방 HER2-blind(0.599)와 *consistent*하나 replication을 *establish*하진 못함(CI 넓음, 법칙판정=미결).' if expl else '검정력 충분(n_pos>=25).'}",
          "  → '복제한다(replicates)'가 아니라 '증폭 마커의 H&E-blindness와 부합(consistent with)'으로 기술.",""]
    (HERE/cancer/"full"/"LAW_TEST.md").write_text("\n".join(lines))
    log(f"  wrote {cancer}/full/LAW_TEST.md")
    return {ep:{"auc":rows_eval[ep][0],"law_verdict":rows_eval[ep][1],"n_pos":rows_eval[ep][2],
                "pred_met":rows_eval[ep][3]} for ep in rows_eval}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda:2")
    ap.add_argument("--force", action="store_true")
    a=ap.parse_args()
    log(f"=== SH CHAIN start device={a.device} force={a.force} ===")
    # 게이트: 임베딩 마스터 종료까지 대기
    while embed_alive():
        cnts={c:emb_count(c) for c in CANCERS}
        log(f"  임베딩 진행 중 {cnts} — 대기")
        time.sleep(300)
    cnts={c:emb_count(c) for c in CANCERS}
    log(f"  임베딩 마스터 종료. counts={cnts}")
    law={}
    for cancer in CANCERS:
        out=HERE/cancer/"full"/"mil_cost_results.json"
        if out.exists() and not a.force:
            log(f"  {cancer}: mil 결과 존재 — skip(--force 재계산)")
        else:
            if not run_mil(cancer, a.device):
                log(f"  {cancer}: MIL 실패 — 법칙표 스킵"); continue
        law[cancer]=gen_law_test(cancer)
    summary={"finished_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
             "embedding_counts":{c:emb_count(c) for c in CANCERS},"law_test":law}
    (HERE/"SH_CHAIN_DONE.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    log(f"=== SH CHAIN DONE ===\n{json.dumps(summary,indent=2,ensure_ascii=False)}")

if __name__=="__main__":
    main()

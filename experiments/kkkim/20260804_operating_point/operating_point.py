#!/usr/bin/env python3
"""BIOP02-124 #3 — 임상 operating-point 분석 (게재 blocker).

각 endpoint의 예측확률(proba)+정답(true)에서 임상 의사결정 지표를 계산한다:
  - 유병률, n, n_pos, AUROC
  - threshold=0.5 및 Youden-최적점에서 sensitivity/specificity/PPV/NPV
  - rule-out(민감도>=0.90 유지 최대 임계) / rule-in(특이도>=0.90 유지 최소 임계)
  - calibration: 10-bin ECE + Brier
  - decision curve: net benefit @ pt in {0.1,0.2,0.3} vs treat-all / treat-none
  - prevalence sensitivity: 표본 유병률과 다른 목표 유병률에서 Bayes로 PPV/NPV 재계산

검정력 규칙(사전등록): n_pos<25 -> exploratory. operating-point는 표본이 작으면
지점 추정이 매우 불안정하므로 exploratory는 그대로 표기하고 확증적으로 읽지 않는다.

입력: 이미 커밋된 예측 파일만 사용(재학습·재추론 없음).
  BRCA binary : experiments/sjpark/{er,pr,her2}_status_clam_uni_v2/predictions_ext.npy  (col0=proba,col2=true)
  BRCA PAM50  : experiments/sjpark/pam50_clam_mb_uni_v1/predictions_ext_indexed.csv (HER2축 one-vs-rest)
  cross-cancer: experiments/crosscancer/*/full/mil_cost_results.json (patient_proba/patient_true dict)
"""
import json, glob, csv, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POWER_MIN_POS = 25  # 사전등록 검정력 하한

def auroc(y, p):
    y = np.asarray(y); p = np.asarray(p)
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float('nan')
    order = np.argsort(p, kind='mergesort')
    ranks = np.empty(len(p), float); ranks[order] = np.arange(1, len(p) + 1)
    # tie 평균 순위
    _, inv, cnt = np.unique(p, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt); start = csum - cnt
    avg = (start + csum + 1) / 2.0
    ranks = avg[inv]
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)

def confusion_at(y, p, thr):
    yhat = (p >= thr).astype(int)
    tp = int(((yhat == 1) & (y == 1)).sum()); fp = int(((yhat == 1) & (y == 0)).sum())
    tn = int(((yhat == 0) & (y == 0)).sum()); fn = int(((yhat == 0) & (y == 1)).sum())
    sens = tp / (tp + fn) if (tp + fn) else float('nan')
    spec = tn / (tn + fp) if (tn + fp) else float('nan')
    ppv = tp / (tp + fp) if (tp + fp) else float('nan')
    npv = tn / (tn + fn) if (tn + fn) else float('nan')
    return dict(thr=round(float(thr), 4), tp=tp, fp=fp, tn=tn, fn=fn,
                sensitivity=sens, specificity=spec, ppv=ppv, npv=npv)

def youden(y, p):
    thrs = np.unique(p)
    best, bj = None, -1
    for t in thrs:
        c = confusion_at(y, p, t)
        if np.isnan(c['sensitivity']) or np.isnan(c['specificity']):
            continue
        j = c['sensitivity'] + c['specificity'] - 1
        if j > bj:
            bj, best = j, c
    return best

def rule_threshold(y, p, target, mode):
    """rule-out: sens>=target인 임계 중 최대(=spec 최대화). rule-in: spec>=target인 임계 중 최소(=sens 최대화)."""
    thrs = np.unique(p)
    cand = None
    for t in thrs:
        c = confusion_at(y, p, t)
        if mode == 'ruleout' and not np.isnan(c['sensitivity']) and c['sensitivity'] >= target:
            cand = c  # 임계가 오름차순이므로 마지막(=최대 임계)이 남음
        if mode == 'rulein' and not np.isnan(c['specificity']) and c['specificity'] >= target:
            return c  # 첫(=최소 임계)에서 반환
    return cand

def ece_brier(y, p, bins=10):
    y = np.asarray(y, float); p = np.asarray(p, float)
    edges = np.linspace(0, 1, bins + 1)
    ece = 0.0
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        m = (p >= lo) & (p < hi) if i < bins - 1 else (p >= lo) & (p <= hi)
        if m.sum() == 0:
            continue
        ece += (m.sum() / len(p)) * abs(p[m].mean() - y[m].mean())
    brier = float(np.mean((p - y) ** 2))
    return float(ece), brier

def net_benefit(y, p, pt):
    """decision curve: NB(model) = TP/n - FP/n * pt/(1-pt). 임계 = pt."""
    n = len(y)
    c = confusion_at(y, p, pt)
    nb_model = c['tp'] / n - c['fp'] / n * (pt / (1 - pt))
    prev = float(np.mean(y))
    nb_all = prev - (1 - prev) * (pt / (1 - pt))  # treat-all
    return dict(pt=pt, nb_model=nb_model, nb_treat_all=nb_all, nb_treat_none=0.0)

def prevalence_shift(sens, spec, target_prev):
    """표본 유병률과 다른 목표 유병률에서 Bayes로 PPV/NPV 재계산."""
    if np.isnan(sens) or np.isnan(spec):
        return dict(target_prev=target_prev, ppv=float('nan'), npv=float('nan'))
    tp = sens * target_prev; fp = (1 - spec) * (1 - target_prev)
    tn = spec * (1 - target_prev); fn = (1 - sens) * target_prev
    ppv = tp / (tp + fp) if (tp + fp) else float('nan')
    npv = tn / (tn + fn) if (tn + fn) else float('nan')
    return dict(target_prev=target_prev, ppv=ppv, npv=npv)

def analyze(name, y, p, meta=None):
    y = np.asarray(y).astype(int); p = np.asarray(p).astype(float)
    n = len(y); npos = int(y.sum()); prev = npos / n if n else float('nan')
    exploratory = npos < POWER_MIN_POS
    au = auroc(y, p)
    at05 = confusion_at(y, p, 0.5)
    yj = youden(y, p)
    ro = rule_threshold(y, p, 0.90, 'ruleout')
    ri = rule_threshold(y, p, 0.90, 'rulein')
    ece, brier = ece_brier(y, p)
    dca = [net_benefit(y, p, pt) for pt in (0.1, 0.2, 0.3)]
    # 목표 유병률: 표본 절반과 2배 (임상 세팅에서 유병률이 바뀔 때 PPV/NPV 민감도)
    pv = [prevalence_shift(at05['sensitivity'], at05['specificity'], tp_)
          for tp_ in (round(prev / 2, 3), round(min(prev * 2, 0.95), 3))]
    return dict(endpoint=name, source=(meta or {}).get('source'), cancer=(meta or {}).get('cancer'),
                n=n, n_pos=npos, prevalence=round(prev, 4), exploratory=exploratory,
                auroc=None if np.isnan(au) else round(au, 4),
                at_threshold_0p5=at05, youden_optimal=yj,
                rule_out_sens90=ro, rule_in_spec90=ri,
                calibration=dict(ece_10bin=round(ece, 4), brier=round(brier, 4)),
                decision_curve=dca, prevalence_sensitivity=pv)

def load_all():
    rows = []
    # BRCA binary
    for ep, path in [('brca_er', 'sjpark/er_status_clam_uni_v2/predictions_ext.npy'),
                     ('brca_pr', 'sjpark/pr_status_clam_uni_v2/predictions_ext.npy'),
                     ('brca_her2', 'sjpark/her2_status_clam_uni_v2/predictions_ext.npy')]:
        a = np.load(os.path.join(ROOT, 'experiments', path), allow_pickle=True).astype(float)
        rows.append(analyze(ep, a[:, 2], a[:, 0], {'source': path, 'cancer': 'BRCA'}))
    # BRCA PAM50 HER2축 one-vs-rest (앵커)
    csvp = os.path.join(ROOT, 'experiments/sjpark/pam50_clam_mb_uni_v1/predictions_ext_indexed.csv')
    r = list(csv.DictReader(open(csvp)))
    y = [1 if x['pam50_true'] == 'HER2' else 0 for x in r]  # PAM50 HER2-enriched 아형
    p = [float(x['proba_HER2']) for x in r]
    rows.append(analyze('brca_pam50_HER2subtype', y, p, {'source': 'pam50 one-vs-rest', 'cancer': 'BRCA'}))
    # cross-cancer
    for f in sorted(glob.glob(os.path.join(ROOT, 'experiments/crosscancer/*/full/mil_cost_results.json'))):
        cancer = f.split('/')[-3]
        d = json.load(open(f))
        for ep, v in d.get('endpoints', {}).items():
            pp, pt = v.get('patient_proba'), v.get('patient_true')
            if not (isinstance(pp, dict) and isinstance(pt, dict)):
                continue
            keys = [k for k in pp if k in pt]
            y = [int(pt[k]) for k in keys]; p = [float(pp[k]) for k in keys]
            rows.append(analyze(ep, y, p, {'source': os.path.relpath(f, ROOT), 'cancer': cancer}))
    return rows

def fmt(v, d=3):
    return '—' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.{d}f}'

def main():
    rows = load_all()
    outdir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(outdir, 'operating_point_results.json'), 'w') as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
    # markdown 표
    L = ['# BIOP02-124 #3 — 임상 operating-point 분석 결과',
         '',
         '> 이미 커밋된 예측(proba+true)만 사용, 재학습·재추론 없음. 스크립트=`operating_point.py`.',
         '> **검정력 규칙**: n_pos<25 → exploratory(지점 추정 불안정, 확증 해석 금지). ✅=powered, ⚠️=exploratory.',
         '',
         '## 표 1. 요약 (threshold=0.5 기준 + rule-in/out)',
         '',
         '| endpoint | 암종 | n | n_pos | 유병률 | 검정력 | AUROC | Sens@.5 | Spec@.5 | PPV@.5 | NPV@.5 | rule-out(Sens≥.9)→Spec | rule-in(Spec≥.9)→Sens | ECE |',
         '|---|---|--:|--:|--:|:--:|--:|--:|--:|--:|--:|--:|--:|--:|']
    for r in rows:
        a = r['at_threshold_0p5']; ro = r['rule_out_sens90']; ri = r['rule_in_spec90']
        pw = '⚠️' if r['exploratory'] else '✅'
        ro_s = f"@{ro['thr']:.2f}→{fmt(ro['specificity'])}" if ro else '없음'
        ri_s = f"@{ri['thr']:.2f}→{fmt(ri['sensitivity'])}" if ri else '없음'
        L.append(f"| {r['endpoint']} | {r['cancer']} | {r['n']} | {r['n_pos']} | {fmt(r['prevalence'])} | {pw} | "
                 f"{fmt(r['auroc'])} | {fmt(a['sensitivity'])} | {fmt(a['specificity'])} | {fmt(a['ppv'])} | {fmt(a['npv'])} | "
                 f"{ro_s} | {ri_s} | {fmt(r['calibration']['ece_10bin'])} |")
    L += ['', '## 표 2. decision-curve net benefit (pt=0.2) + 유병률 민감도', '',
          '| endpoint | 암종 | NB(model)@.2 | NB(treat-all)@.2 | 모델 우위 | PPV@½유병률 | PPV@2×유병률 |',
          '|---|---|--:|--:|:--:|--:|--:|']
    for r in rows:
        nb = next(x for x in r['decision_curve'] if x['pt'] == 0.2)
        adv = '✅' if nb['nb_model'] > max(nb['nb_treat_all'], nb['nb_treat_none']) else '—'
        pv = r['prevalence_sensitivity']
        L.append(f"| {r['endpoint']} | {r['cancer']} | {fmt(nb['nb_model'],4)} | {fmt(nb['nb_treat_all'],4)} | {adv} | "
                 f"{fmt(pv[0]['ppv'])} | {fmt(pv[1]['ppv'])} |")
    L.append('')
    with open(os.path.join(outdir, 'OPERATING_POINT_RESULTS.md'), 'w') as fh:
        fh.write('\n'.join(L))
    print('\n'.join(L))
    print(f"\n[written] {outdir}/operating_point_results.json + OPERATING_POINT_RESULTS.md  (endpoints={len(rows)})")

if __name__ == '__main__':
    main()

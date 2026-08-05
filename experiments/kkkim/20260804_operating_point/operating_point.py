#!/usr/bin/env python3
"""BIOP02-124 #3 — 임상 operating-point 분석 (게재 blocker).

각 endpoint의 예측확률(proba)+정답(true)에서 임상 의사결정 지표를 계산한다:
  - 유병률, n, n_pos, AUROC
  - threshold=0.5 및 Youden-최적점에서 sensitivity/specificity/PPV/NPV
  - rule-out(민감도>=0.90 유지 최대 임계) / rule-in(특이도>=0.90 유지 최소 임계)
  - 1000-bootstrap 95% CI (Sens/Spec/PPV/NPV @0.5) — 리포 관행(M4)
  - calibration: 10-bin ECE + Brier
  - decision curve: net benefit @ pt in {0.1,0.2,0.3} vs treat-all / treat-none
  - prevalence sensitivity: rule-in 임계 지점의 Sens/Spec로 목표 유병률에서 Bayes PPV/NPV

단위(unit) 규율(중요):
  - BRCA ER·PAM50 예측은 CPTAC-external·**slide 단위**(indexed csv에 case_id 有) → **환자(case) 단위로 집계**(case별 proba 평균).
  - BRCA PR·HER2는 npy만 있어 case_id가 없다 → slide 단위 그대로 두고 unit='slide'로 명시(환자 클러스터 미보정 caveat).
  - 교차암종은 cost JSON의 patient_proba/patient_true(이미 환자 단위).
검정력 규칙(사전등록): n_pos<25 -> exploratory(지점 추정 불안정, 확증 해석 금지).

입력: 이미 커밋된 예측만 사용(재학습·재추론 없음). model.pt/predictions.npy=N/A(재분석).
"""
import json, glob, csv, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POWER_MIN_POS = 25
N_BOOT = 1000
BOOT_SEED = 42

def auroc(y, p):
    y = np.asarray(y); p = np.asarray(p)
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float('nan')
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
    best, bj = None, -1
    for t in np.unique(p):
        c = confusion_at(y, p, t)
        if np.isnan(c['sensitivity']) or np.isnan(c['specificity']):
            continue
        j = c['sensitivity'] + c['specificity'] - 1
        if j > bj:
            bj, best = j, c
    return best

def rule_threshold(y, p, target, mode):
    cand = None
    for t in np.unique(p):
        c = confusion_at(y, p, t)
        if mode == 'ruleout' and not np.isnan(c['sensitivity']) and c['sensitivity'] >= target:
            cand = c
        if mode == 'rulein' and not np.isnan(c['specificity']) and c['specificity'] >= target:
            return c
    return cand

def boot_ci(y, p, thr, n_boot=N_BOOT, seed=BOOT_SEED):
    """환자(또는 슬라이드) 단위 리샘플로 Sens/Spec/PPV/NPV의 95% CI."""
    rng = np.random.default_rng(seed)
    n = len(y); keys = ('sensitivity', 'specificity', 'ppv', 'npv')
    acc = {k: [] for k in keys}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        c = confusion_at(y[idx], p[idx], thr)
        for k in keys:
            if not np.isnan(c[k]):
                acc[k].append(c[k])
    out = {}
    for k in keys:
        out[k] = [round(float(np.percentile(acc[k], 2.5)), 3),
                  round(float(np.percentile(acc[k], 97.5)), 3)] if acc[k] else [None, None]
    return out

def ece_brier(y, p, bins=10):
    y = np.asarray(y, float); p = np.asarray(p, float)
    edges = np.linspace(0, 1, bins + 1); ece = 0.0
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        m = (p >= lo) & (p < hi) if i < bins - 1 else (p >= lo) & (p <= hi)
        if m.sum() == 0:
            continue
        ece += (m.sum() / len(p)) * abs(p[m].mean() - y[m].mean())
    return float(ece), float(np.mean((p - y) ** 2))

def net_benefit(y, p, pt):
    n = len(y); c = confusion_at(y, p, pt)
    nb_model = c['tp'] / n - c['fp'] / n * (pt / (1 - pt))
    prev = float(np.mean(y))
    nb_all = prev - (1 - prev) * (pt / (1 - pt))
    return dict(pt=pt, nb_model=round(nb_model, 4), nb_treat_all=round(nb_all, 4), nb_treat_none=0.0)

def prevalence_shift(sens, spec, target_prev):
    if sens is None or spec is None or np.isnan(sens) or np.isnan(spec):
        return dict(target_prev=target_prev, ppv=float('nan'), npv=float('nan'))
    tp = sens * target_prev; fp = (1 - spec) * (1 - target_prev)
    tn = spec * (1 - target_prev); fn = (1 - sens) * target_prev
    ppv = tp / (tp + fp) if (tp + fp) else float('nan')
    npv = tn / (tn + fn) if (tn + fn) else float('nan')
    return dict(target_prev=target_prev, ppv=ppv, npv=npv)

def analyze(name, y, p, meta):
    y = np.asarray(y).astype(int); p = np.asarray(p).astype(float)
    n = len(y); npos = int(y.sum()); prev = npos / n if n else float('nan')
    exploratory = npos < POWER_MIN_POS
    at05 = confusion_at(y, p, 0.5)
    ri = rule_threshold(y, p, 0.90, 'rulein')
    # 유병률 민감도는 rule-in 지점 Sens/Spec로(0.5는 희귀축에서 Sens=0 → NaN 유발)
    base_s = ri['sensitivity'] if ri else at05['sensitivity']
    base_sp = ri['specificity'] if ri else at05['specificity']
    pv = [prevalence_shift(base_s, base_sp, tp_)
          for tp_ in (round(prev / 2, 3), round(min(prev * 2, 0.95), 3))]
    ece, brier = ece_brier(y, p)
    au = auroc(y, p)
    return dict(endpoint=name, cancer=meta['cancer'], unit=meta['unit'], cohort=meta['cohort'],
                source=meta['source'], n=n, n_pos=npos, prevalence=round(prev, 4),
                exploratory=exploratory, powered=(not exploratory),
                auroc=None if np.isnan(au) else round(au, 4),
                at_threshold_0p5=at05, at_threshold_0p5_ci=boot_ci(y, p, 0.5),
                youden_optimal=youden(y, p),
                rule_out_sens90=rule_threshold(y, p, 0.90, 'ruleout'), rule_in_spec90=ri,
                calibration=dict(ece_10bin=round(ece, 4), brier=round(brier, 4)),
                decision_curve=[net_benefit(y, p, pt) for pt in (0.1, 0.2, 0.3)],
                prevalence_sensitivity=dict(evaluated_at=('rule_in' if ri else 'thr0.5'),
                                            sens=base_s, spec=base_sp, shifts=pv))

def aggregate_by_case(rows, proba_key, label_fn):
    """slide 행 -> case별 proba 평균, label은 case 내 최빈(동률시 max)."""
    from collections import defaultdict
    d = defaultdict(lambda: {'p': [], 'y': []})
    for x in rows:
        d[x['case_id']]['p'].append(float(x[proba_key]))
        d[x['case_id']]['y'].append(label_fn(x))
    y = []; p = []
    for cid, v in d.items():
        p.append(float(np.mean(v['p'])))
        y.append(int(round(np.mean(v['y']))))  # 같은 환자 라벨은 동일; 평균 반올림은 안전장치
    return y, p, len(d)

def load_all():
    rows = []
    # BRCA ER: CPTAC-ext, slide->case 집계
    er = list(csv.DictReader(open(os.path.join(ROOT, 'experiments/sjpark/er_status_clam_uni_v2/predictions_ext_indexed.csv'))))
    y, p, nc = aggregate_by_case(er, 'er_pred_prob', lambda x: int(float(x['er_true_label'])))
    rows.append(analyze('brca_er', y, p, dict(cancer='BRCA', unit='patient(집계)', cohort='CPTAC-ext',
                                              source='er_status_clam_uni_v2 (slide→case 집계, %d cases)' % nc)))
    # BRCA PAM50 HER2 아형: CPTAC-ext, slide->case 집계
    pm = list(csv.DictReader(open(os.path.join(ROOT, 'experiments/sjpark/pam50_clam_mb_uni_v1/predictions_ext_indexed.csv'))))
    y, p, nc = aggregate_by_case(pm, 'proba_HER2', lambda x: 1 if x['pam50_true'] == 'HER2' else 0)
    rows.append(analyze('brca_pam50_HER2subtype', y, p, dict(cancer='BRCA', unit='patient(집계)', cohort='CPTAC-ext',
                                                             source='pam50 one-vs-rest (slide→case 집계, %d cases)' % nc)))
    # BRCA PR·HER2: npy만(case_id 없음) → slide 단위 명시
    for ep, path in [('brca_pr', 'sjpark/pr_status_clam_uni_v2/predictions_ext.npy'),
                     ('brca_her2', 'sjpark/her2_status_clam_uni_v2/predictions_ext.npy')]:
        a = np.load(os.path.join(ROOT, 'experiments', path), allow_pickle=True).astype(float)
        rows.append(analyze(ep, a[:, 2], a[:, 0], dict(cancer='BRCA', unit='slide(미집계)', cohort='CPTAC-ext',
                                                       source=path + ' (case_id 없음 → slide 단위)')))
    # cross-cancer: patient 단위
    for f in sorted(glob.glob(os.path.join(ROOT, 'experiments/crosscancer/*/full/mil_cost_results.json'))):
        cancer = f.split('/')[-3]; d = json.load(open(f))
        for ep, v in d.get('endpoints', {}).items():
            pp, pt = v.get('patient_proba'), v.get('patient_true')
            if not (isinstance(pp, dict) and isinstance(pt, dict)):
                continue
            keys = [k for k in pp if k in pt]
            rows.append(analyze(ep, [int(pt[k]) for k in keys], [float(pp[k]) for k in keys],
                                dict(cancer=cancer, unit='patient', cohort='TCGA-holdout',
                                     source=os.path.relpath(f, ROOT))))
    return rows

def fmt(v, d=3):
    return '—' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{v:.{d}f}'

def ci(c):
    return '' if c[0] is None else f' [{c[0]:.2f}–{c[1]:.2f}]'

def main():
    rows = load_all()
    outdir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(outdir, 'operating_point_results.json'), 'w') as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
    L = ['# BIOP02-124 #3 — 임상 operating-point 분석 결과', '',
         '> 이미 커밋된 예측(proba+true)만 사용, 재학습·재추론 없음. 스크립트=`operating_point.py`(seed 42, 1000-bootstrap).',
         '> **단위**: BRCA ER/PAM50=환자 집계(CPTAC-ext), PR/HER2=slide 단위(case_id 없음), 교차암종=환자(TCGA-holdout).',
         '> **검정력**: n_pos<25 → ⚠️exploratory(지점 추정 불안정, 확증 해석·본문 승격 금지). ✅=powered.', '',
         '## 표 1. Sens/Spec/PPV/NPV @0.5 (95% CI, 1000-bootstrap) + rule-in/out',
         '',
         '| endpoint | 암종 | 단위 | n | n_pos | 유병률 | 검정력 | AUROC | Sens@.5 | Spec@.5 | PPV@.5 | NPV@.5 | rule-out(Sens≥.9)→Spec | rule-in(Spec≥.9)→Sens | ECE |',
         '|---|---|---|--:|--:|--:|:--:|--:|--|--|--|--|--:|--:|--:|']
    for r in rows:
        a = r['at_threshold_0p5']; c = r['at_threshold_0p5_ci']; ro = r['rule_out_sens90']; ri = r['rule_in_spec90']
        pw = '⚠️' if r['exploratory'] else '✅'
        ro_s = f"@{ro['thr']:.2f}→{fmt(ro['specificity'])}" if ro else '없음'
        ri_s = f"@{ri['thr']:.2f}→{fmt(ri['sensitivity'])}" if ri else '없음'
        L.append(f"| {r['endpoint']} | {r['cancer']} | {r['unit']} | {r['n']} | {r['n_pos']} | {fmt(r['prevalence'])} | {pw} | "
                 f"{fmt(r['auroc'])} | {fmt(a['sensitivity'])}{ci(c['sensitivity'])} | {fmt(a['specificity'])}{ci(c['specificity'])} | "
                 f"{fmt(a['ppv'])}{ci(c['ppv'])} | {fmt(a['npv'])}{ci(c['npv'])} | {ro_s} | {ri_s} | {fmt(r['calibration']['ece_10bin'])} |")
    L += ['', '## 표 2. decision-curve net benefit (pt=0.2) + 유병률 민감도 (rule-in 지점)', '',
          '> ⚠️ exploratory 행은 저유병률에서 treat-all이 강한 음수라 거의 모든 모델이 "우위"로 보인다(유병률 인공물). 확증 아님.', '',
          '| endpoint | 암종 | 검정력 | NB(model)@.2 | NB(treat-all)@.2 | 모델 우위 | PPV@½유병률 | PPV@2×유병률 |',
          '|---|---|:--:|--:|--:|:--:|--:|--:|']
    for r in rows:
        nb = next(x for x in r['decision_curve'] if x['pt'] == 0.2)
        pw = '⚠️' if r['exploratory'] else '✅'
        # 검정력 없는 행엔 ✅ 표시 억제(유병률 인공물 방지)
        adv = ('✅' if nb['nb_model'] > max(nb['nb_treat_all'], nb['nb_treat_none']) else '—') if not r['exploratory'] else '(exploratory)'
        pv = r['prevalence_sensitivity']['shifts']
        L.append(f"| {r['endpoint']} | {r['cancer']} | {pw} | {fmt(nb['nb_model'],4)} | {fmt(nb['nb_treat_all'],4)} | {adv} | "
                 f"{fmt(pv[0]['ppv'])} | {fmt(pv[1]['ppv'])} |")
    L.append('')
    with open(os.path.join(outdir, 'OPERATING_POINT_RESULTS.md'), 'w') as fh:
        fh.write('\n'.join(L))
    print('\n'.join(L))
    print(f"\n[written] operating_point_results.json + OPERATING_POINT_RESULTS.md  (endpoints={len(rows)})")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""BIOP02-121 MUST #2 — site/batch confounding 감사 (게재 blocker, 122 전제조건).

질문: H&E 모델이 생물학이 아니라 기관(TSS)·스캐너·염색 batch를 학습했는가?
위 Lauren 사례(분할=기관구성 반영)가 이미 이 위험을 보였다. 이 감사 없이는
HPV/BRAF/조직형 신호도 site artifact 의심을 받는다(npj 외부검증 blocker 122의 전제).

기존 예측(재학습 없음)으로 가능한 3종:
  (A) label-site imbalance — endpoint별 site간 라벨 유병률 편중(단일 site가 양성/음성 독점?)
  (B) within-site AUROC — site를 상수로 고정한 부분집합에서도 신호가 남는가.
      pooled AUROC가 within-site에서 유지되면 site 교란이 아님(핵심 검정).
  (C) score↔site 연관(음성 한정) — 참-음성만 모아 예측확률이 site로 갈리는가.
      갈리면 라벨과 무관한 batch 신호를 점수가 실어나른다(누출 지표). eta²로 계량.

⚠️ 재학습 필요라 여기서 안 하는 것(별도 후속): site-예측 모델(임베딩→TSS),
   전면 LOSO 재학습, site-stratified permutation 재학습. 단, 예측이 이미
   site-disjoint holdout이라 (B) within-site + per-site AUROC가 LOSO 신호의 상당부를 준다.

입력: experiments/crosscancer/*/full/mil_cost_results.json (patient key=TCGA 바코드, TSS=2번째 필드).
"""
import json, os, glob, sys
import numpy as np
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '20260804_operating_point'))
from operating_point import auroc

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POWER_MIN_POS = 25

def tss(bc):
    return bc.split('-')[1] if bc.startswith('TCGA-') and len(bc.split('-')) > 1 else 'NA'

def eta_squared(values, groups):
    """일원분산분석 eta²: 그룹(site)이 설명하는 분산 비율."""
    values = np.asarray(values, float); groups = np.asarray(groups)
    grand = values.mean(); ss_tot = ((values - grand) ** 2).sum()
    if ss_tot == 0:
        return 0.0
    ss_between = 0.0
    for g in np.unique(groups):
        m = groups == g
        ss_between += m.sum() * (values[m].mean() - grand) ** 2
    return float(ss_between / ss_tot)

def analyze(cancer, ep, pt, pp):
    keys = [k for k in pp if k in pt]
    y = np.array([int(pt[k]) for k in keys]); p = np.array([float(pp[k]) for k in keys])
    site = np.array([tss(k) for k in keys])
    n = len(y); npos = int(y.sum()); powered = npos >= POWER_MIN_POS
    au_pool = auroc(y, p)
    # (A) label-site imbalance
    by = defaultdict(lambda: [0, 0])
    for yi, si in zip(y, site):
        by[si][int(yi)] += 1
    site_prev = {s: (v[1] / (v[0] + v[1])) for s, v in by.items()}
    pos_by_site = {s: v[1] for s, v in by.items()}
    max_site_pos_share = max(pos_by_site.values()) / npos if npos else float('nan')
    n_site_all_one_class = sum(1 for s, v in by.items() if (v[0] + v[1]) >= 3 and (v[0] == 0 or v[1] == 0))
    # (B) within-site AUROC (양·음성 모두 있는 site만), 표본가중 평균
    ws = []
    for s, v in by.items():
        if v[0] >= 1 and v[1] >= 1 and (v[0] + v[1]) >= 5:
            m = site == s
            a = auroc(y[m], p[m])
            if a == a:
                ws.append((s, a, int(m.sum()), int(y[m].sum())))
    if ws:
        wsum = sum(w[2] for w in ws)
        within_auroc = sum(w[1] * w[2] for w in ws) / wsum
        within_cov = wsum / n
    else:
        within_auroc, within_cov = float('nan'), 0.0
    # (C) score↔site (참-음성 한정 eta²; 라벨 효과 분리)
    neg = y == 0
    eta_neg = eta_squared(p[neg], site[neg]) if neg.sum() > 2 else float('nan')
    eta_all = eta_squared(p, site)
    return dict(cancer=cancer, endpoint=ep, n=n, n_pos=npos, powered=powered, n_site=len(by),
                pooled_auroc=round(float(au_pool), 4) if au_pool == au_pool else None,
                A_label_site=dict(max_single_site_pos_share=round(float(max_site_pos_share), 3) if npos else None,
                                  n_sites_all_one_class=n_site_all_one_class,
                                  site_prevalence_spread=round(float(np.std(list(site_prev.values()))), 3)),
                B_within_site=dict(within_site_auroc=round(float(within_auroc), 4) if within_auroc == within_auroc else None,
                                   coverage=round(float(within_cov), 3), n_sites_used=len(ws),
                                   drop_vs_pooled=round(float(au_pool - within_auroc), 4) if (within_auroc == within_auroc and au_pool == au_pool) else None),
                C_score_site=dict(eta2_negatives_only=round(float(eta_neg), 4) if eta_neg == eta_neg else None,
                                  eta2_all=round(float(eta_all), 4)))

def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'experiments/crosscancer/*/full/mil_cost_results.json'))):
        cancer = f.split('/')[-3]; d = json.load(open(f))
        for ep, v in d.get('endpoints', {}).items():
            pp, pt = v.get('patient_proba'), v.get('patient_true')
            if isinstance(pp, dict) and isinstance(pt, dict):
                rows.append(analyze(cancer, ep, pt, pp))
    outdir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)
    json.dump(rows, open(os.path.join(outdir, 'site_audit_results.json'), 'w'), indent=2, ensure_ascii=False)

    def f(v, d=3):
        return '—' if v is None else f'{v:.{d}f}'
    L = ['# BIOP02-121 MUST #2 — site/batch confounding 감사', '',
         '> 기존 site-disjoint holdout 예측만 사용(재학습 없음). TSS=TCGA 바코드 2번째 필드.',
         '> **판독 규칙**: within-site AUROC가 pooled와 비슷하면(작은 drop) site 교란 아님. '
         'eta²(참-음성)이 크면 점수가 라벨과 무관한 site 신호를 실어나름(누출). ✅powered / ⚠️exploratory.', '',
         '## 표. endpoint별 site 감사',
         '',
         '| endpoint | 암종 | 검정력 | n_site | pooled AUROC | within-site AUROC (drop) | 단일site 양성독점 | 단일클래스 site수 | eta²(음성) | eta²(전체) |',
         '|---|---|:--:|--:|--:|--|--:|--:|--:|--:|']
    for r in rows:
        pw = '✅' if r['powered'] else '⚠️'
        b = r['B_within_site']; a = r['A_label_site']; c = r['C_score_site']
        wdrop = f"{f(b['within_site_auroc'])} ({'+' if (b['drop_vs_pooled'] or 0) >= 0 else ''}{f(b['drop_vs_pooled'],3)})" if b['within_site_auroc'] is not None else '—'
        L.append(f"| {r['endpoint']} | {r['cancer']} | {pw} | {r['n_site']} | {f(r['pooled_auroc'])} | {wdrop} | "
                 f"{f(a['max_single_site_pos_share'])} | {a['n_sites_all_one_class']} | {f(c['eta2_negatives_only'],3)} | {f(c['eta2_all'],3)} |")
    L += ['',
          '## 판독 (실측)',
          '',
          '- **두경부 HPV — site 인공물 아님(가장 중요).** pooled 0.959 → within-site 0.966(drop −0.006, 사실상 무), eta²(음성) 0.108, 단일site 양성독점 0.192로 낮다. site를 상수로 고정해도 신호가 그대로 유지되므로, HPV 확증은 기관·스캐너 batch가 아니라 형태(바이러스축)에서 온다. **122 외부검증 면제 협상의 정량 근거.**',
          '- **폐 LUSC 조직형(양성대조) — site 구성 편중은 예상된 것.** 37개 site 중 27개가 단일 조직형(eta²_all 0.705). LUSC/LUAD가 기관별로 몰려 있어 within-site(양·음성 공존 site) 계산이 불가(—). 조직형은 검출돼야 하는 양성대조라 이 편중 자체는 문제 아니나, 조직형이 강한 site 상관물임을 보여 #7(조직형 교란)과 정합.',
          '- **위 Lauren — 음성의 정체가 site 일반화 실패임을 계량 확인.** pooled 0.536인데 within-site 0.783(drop −0.247). 즉 **형태 신호가 site 안에는 있으나 site간 라벨편중으로 일반화가 무너진다**(eta² 음성 0.284, 단일클래스 site 존재). A3 진단(Lauren 특이 site-교란)의 정량 확증 — "형태에 전혀 안 보임"이 아니라 "site를 넘어 일반화 안 됨"으로 음성을 정밀화.',
          '- **두경부 grade_high — 깨끗.** within 0.850 vs pooled 0.815(drop −0.035 유지), eta²(음성) 0.093 낮음.',
          '- **폐 KRAS — site+조직형 이중 교란(exploratory).** pooled 0.681 → within-site 0.406(붕괴), eta²(음성) 0.468(매우 높음=점수가 라벨 무관 site 신호를 실어나름). #7의 조직형 인공물 판정과 겹쳐 KRAS는 형태 상관물 축 승격 불가가 이중으로 확정. EGFR도 eta²(음성) 0.468로 site 신호가 크나 within-site 0.789로 잔존.',
          '',
          '> ⚠️ **within-site AUROC 안정성 주의**: 암종당 site가 많아 site별 표본이 작다(특히 exploratory·Lauren n=58). within-site 값은 소수 site에 좌우될 수 있어 방향 지표로 읽고, 확정은 재학습 LOSO(후속)로 한다.',
          '',
          '## 122(외부검증 면제) 연결',
          '',
          '- 이건규 122 판정: "(B) — #2 site 감사 결과에 조건부. 면제 협상 = LOSO 성능저하 작음 + label-site confounding 없음 + held-out site calibration 유지".',
          '- 본 감사의 within-site AUROC 유지(=LOSO 근사) + 앵커 eta²(음성) 작음 + 앵커 label-site 편중 작음이 **면제 협상의 정량 근거**가 된다. 반대로 편중이 크면 그 endpoint는 외부검증 없이 승격 불가.',
          '',
          '## 재학습 필요 후속 (여기서 안 함, 명시)',
          '',
          '- 임베딩→TSS site-예측 모델(batch 학습 여부 직접 검정), 전면 LOSO 재학습, site-stratified label permutation 재학습. GPU 재학습 자원 필요 → braveji와 큐 협의.',
          '',
          '> claim_level: hypothesis_only · 리뷰: braveji. 재학습 후속은 별도.']
    open(os.path.join(outdir, 'SITE_AUDIT_RESULTS.md'), 'w').write('\n'.join(L))
    print('\n'.join(L))
    print(f"\n[written] site_audit_results.json + SITE_AUDIT_RESULTS.md (endpoints={len(rows)})")

if __name__ == '__main__':
    main()

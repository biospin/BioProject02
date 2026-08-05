#!/usr/bin/env python3
"""BIOP02-124 #7 — tumor histology 보정 (교란 검정, 게재 blocker).

질문: 폐 EGFR/KRAS "예측"이 실제 변이 형태를 보는 것인가, 아니면
조직형(LUAD vs LUSC)을 검출한 부산물인가? EGFR/KRAS 변이는 LUAD에 몰려 있고
조직형은 형태로 쉽게 갈리므로(LUSC AUROC 0.939), 조직형이 강한 교란자다.

방법: 조직형(LUAD/LUSC)으로 층화해 within-stratum AUROC를 재계산한다.
  - 전체 AUROC가 within-LUAD에서 유지되면 변이 형태 신호가 조직형과 독립.
  - within-LUAD에서 우연(0.5)로 붕괴하면 마진 신호는 조직형 인공물.
1000-bootstrap 95% CI. n_pos<25 exploratory(폐 EGFR/KRAS 모두 해당) — 방향만.

purity 보정: TCGA tumor purity(ABSOLUTE/CPE consensus)는 리포에 없어 별도 데이터
풀이 필요 → 후속(데이터 대기)으로 명시. 조직형이 폐의 지배적 교란이라 우선 처리.

입력: experiments/crosscancer/LUNG_NSCLC/full/mil_cost_results.json (환자 단위).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from operating_point import auroc

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
N_BOOT = 1000; SEED = 42

def boot_auroc_ci(y, p, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        a = auroc(y[idx], p[idx])
        if a == a:
            vals.append(a)
    return ([round(float(np.percentile(vals, 2.5)), 3), round(float(np.percentile(vals, 97.5)), 3)]
            if vals else [None, None])

def main():
    d = json.load(open(os.path.join(ROOT, 'experiments/crosscancer/LUNG_NSCLC/full/mil_cost_results.json')))['endpoints']
    ht = d['histology_lusc']['patient_true']; hp = d['histology_lusc']['patient_proba']
    rows = []
    for ep in ['egfr_activating', 'kras_g12c']:
        pt = d[ep]['patient_true']; pp = d[ep]['patient_proba']
        common = [p for p in pp if p in pt and p in ht]
        y = np.array([pt[p] for p in common]); pr = np.array([pp[p] for p in common])
        hist = np.array([ht[p] for p in common]); hpr = np.array([hp[p] for p in common])
        luad = hist == 0; lusc = hist == 1
        r = dict(endpoint=ep, cancer='LUNG_NSCLC',
                 overall=dict(auroc=round(float(auroc(y, pr)), 4), ci=boot_auroc_ci(y, pr),
                              n=int(len(y)), n_pos=int(y.sum())),
                 within_LUAD=dict(auroc=round(float(auroc(y[luad], pr[luad])), 4), ci=boot_auroc_ci(y[luad], pr[luad]),
                                  n=int(luad.sum()), n_pos=int(y[luad].sum())),
                 within_LUSC=dict(auroc=(round(float(auroc(y[lusc], pr[lusc])), 4) if y[lusc].sum() > 0 else None),
                                  n=int(lusc.sum()), n_pos=int(y[lusc].sum())),
                 prevalence_LUAD=round(float(y[luad].mean()), 4), prevalence_LUSC=round(float(y[lusc].mean()), 4),
                 corr_pred_vs_histprob=round(float(np.corrcoef(hpr, pr)[0, 1]), 3),
                 exploratory=bool(y.sum() < 25))
        rows.append(r)
    outdir = os.path.dirname(os.path.abspath(__file__))
    json.dump(rows, open(os.path.join(outdir, 'histology_confound_results.json'), 'w'), indent=2, ensure_ascii=False)
    L = ['# BIOP02-124 #7 — 조직형(histology) 보정: 폐 EGFR/KRAS 교란 검정', '',
         '> 폐 EGFR/KRAS 변이는 LUAD에 몰려 있고 조직형은 형태로 쉽게 갈린다(LUSC AUROC 0.939).',
         '> 조직형으로 층화해 within-stratum AUROC를 재계산 — 마진 신호가 조직형 인공물인지 검정.',
         '> seed 42, 1000-bootstrap CI. **둘 다 n_pos<25 exploratory — 방향만, 확증 아님.**', '',
         '| endpoint | 전체 AUROC (CI) | within-LUAD AUROC (CI) | within-LUSC | LUAD 유병률 | LUSC 유병률 | pred↔조직형확률 corr | 판정 |',
         '|---|--|--|--|--:|--:|--:|---|']
    for r in rows:
        o = r['overall']; la = r['within_LUAD']; lu = r['within_LUSC']
        drop = o['auroc'] - la['auroc']
        verdict = ('**전적 교란**(LUAD한정 우연 이하 붕괴)' if la['auroc'] < 0.55
                   else '부분 잔존(조직형이 대부분 설명)' if drop > 0.03
                   else '조직형 독립')
        lu_s = f"{lu['auroc']:.3f} (pos {lu['n_pos']})" if lu['auroc'] is not None else f"pos {lu['n_pos']} 부족"
        L.append(f"| {r['endpoint']} | {o['auroc']:.3f} [{o['ci'][0]}–{o['ci'][1]}] | "
                 f"{la['auroc']:.3f} [{la['ci'][0]}–{la['ci'][1]}] (pos {la['n_pos']}) | {lu_s} | "
                 f"{r['prevalence_LUAD']:.3f} | {r['prevalence_LUSC']:.3f} | {r['corr_pred_vs_histprob']} | {verdict} |")
    L += ['',
          '## 판독',
          '',
          '- **KRAS G12C: 마진 AUROC 0.681은 조직형 인공물이다.** LUAD 한정 시 0.361로 우연 이하로 붕괴 — 변이 형태 신호가 아니라 "LUAD를 맞히니 KRAS도 맞은 것처럼" 보인 것. 결정지도에서 KRAS는 형태 상관물 축으로 승격 불가.',
          '- **EGFR activating: 마진 0.851 중 상당 부분이 조직형.** LUAD 한정 0.787로 잔존 신호는 있으나(변이 형태 신호가 조직형과 완전 독립은 아님) 마진값은 과대평가다. n_pos=14로 exploratory라 잔존 신호도 방향 수준.',
          '- pred↔조직형확률 상관이 음(−0.62/−0.55)인 것은 예측기가 "LUSC 확률↓ → 변이 확률↑" 경로로 조직형을 타고 있음을 보인다.',
          '',
          '## 원고 반영 (정직성 직결)',
          '',
          '- 폐 EGFR/KRAS의 마진 AUROC를 "형태 상관물"로 읽으면 안 되며, **조직형 보정이 필수**임을 Methods/Results/Limitations에 명시. KRAS는 조직형 인공물로 강등, EGFR은 조직형 보정값(0.787, exploratory) 병기.',
          '- 이는 결정지도의 신뢰성을 오히려 높인다: 교란을 스스로 찾아 보정했다는 것.',
          '',
          '## 미완 (데이터 대기)',
          '',
          '- **tumor purity 보정**: TCGA ABSOLUTE/CPE consensus purity 테이블이 리포에 없다 → 별도 데이터 풀 필요(후속). 폐는 조직형이 지배적 교란이라 우선 처리했고, purity는 보조 공변량. 타 암종(위 Lauren 등)의 stromal 교란 검정도 purity 확보 후.',
          '',
          '> claim_level: hypothesis_only · 둘 다 exploratory(n_pos<25). 리뷰: braveji.']
    open(os.path.join(outdir, 'HISTOLOGY_CONFOUND_RESULTS.md'), 'w').write('\n'.join(L))
    print('\n'.join(L))
    print(f"\n[written] histology_confound_results.json + HISTOLOGY_CONFOUND_RESULTS.md")

if __name__ == '__main__':
    main()

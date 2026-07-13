#!/usr/bin/env python3
"""Build lung transcriptomic-subtype labels (LUAD TRU/PP/PI, LUSC 4-class)
from authoritative public TCGA calls, joined to the NSCLC embedding cohort.

Sources (authoritative, web-verified 2026-07-12):
  LUAD: UCSC Xena TCGA.LUAD.sampleMap/LUAD_clinicalMatrix, column `Expression_Subtype`
        values Bronchioid/Squamoid/Magnoid, renamed per TCGA 2014 (Nature 511:543):
        Bronchioid->TRU, Squamoid->PI, Magnoid->PP.
  LUSC: UCSC Xena pancanatlas TCGASubtype.20170308, column `Subtype_mRNA`
        values classical/basal/secretory/primitive (Wilkerson 2010 / TCGA LUSC 2012).

cBioPortal SUBTYPE field is histology only (== 'LUAD'/'LUSC'), no expression subtype -> unusable.
Labels are made independently of any H&E result (prereg law honesty).
"""
import csv, gzip, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(HERE, os.pardir, 'full')
FULL = os.path.abspath(FULL)

def pat(s):
    return '-'.join(s.split('-')[:3])

# --- cohort + existing mutation/histology labels ---
cohort = {}
mut = {}
for x in csv.DictReader(open(os.path.join(FULL, 'patient_labels.csv'))):
    cohort[x['case_id']] = x['cohort']
    mut[x['case_id']] = x

# --- embeddings present (informational snapshot only; NOT a filter) ---
emb = set()
embdir = os.path.join(FULL, 'embeddings')
for f in os.listdir(embdir):
    if f.endswith('_uni_embeddings.npy'):
        emb.add('-'.join(f.split('-')[:3]))

# --- LUAD authoritative (Xena Expression_Subtype) ---
HAYES2RENAMED = {'Bronchioid': 'TRU', 'Squamoid': 'PI', 'Magnoid': 'PP'}
luad = {}       # case_id -> renamed subtype
luad_orig = {}  # case_id -> Hayes original name
r = list(csv.reader(open(os.path.join(HERE, 'xena_LUAD_clinicalMatrix.tsv')), delimiter='\t'))
di = {c: i for i, c in enumerate(r[0])}
for row in r[1:]:
    v = row[di['Expression_Subtype']]
    if v in HAYES2RENAMED:
        p = pat(row[di['sampleID']])
        luad[p] = HAYES2RENAMED[v]
        luad_orig[p] = v

# --- LUSC authoritative (pancan Subtype_mRNA) ---
LUSC_CLASSES = {'classical', 'basal', 'secretory', 'primitive'}
lusc = {}
for row in csv.DictReader(gzip.open(os.path.join(HERE, 'xena_pancan_TCGASubtype.20170308.tsv.gz'), 'rt'), delimiter='\t'):
    if row['Subtype_mRNA'] in LUSC_CLASSES:
        lusc[pat(row['sampleID'])] = row['Subtype_mRNA']

# --- build joined rows keyed to FULL labeled cohort (all labeled patients) ---
out = os.path.join(FULL, 'subtype_labels.csv')
rows = []
for cid in sorted(cohort):
    coh = cohort[cid]
    ls = luad.get(cid, '') if coh == 'LUAD' else ''
    us = lusc.get(cid, '') if coh == 'LUSC' else ''
    if not ls and not us:
        continue  # no authoritative subtype -> omit (recorded as unlabeled)
    rows.append({
        'case_id': cid,
        'cohort': coh,
        'luad_subtype': ls,
        'lusc_subtype': us,
        'luad_subtype_orig_hayes': luad_orig.get(cid, '') if coh == 'LUAD' else '',
        'source': 'authoritative',
        'source_dataset': 'xena_LUAD_clinicalMatrix.Expression_Subtype' if coh == 'LUAD'
                          else 'xena_pancan_TCGASubtype.Subtype_mRNA',
        'has_embedding': int(cid in emb),
    })

with open(out, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# --- stdout summary ---
nL = sum(1 for c in cohort.values() if c == 'LUAD')
nU = sum(1 for c in cohort.values() if c == 'LUSC')
emb_coh = len(emb & set(cohort))
ld = collections.Counter(x['luad_subtype'] for x in rows if x['luad_subtype'])
ud = collections.Counter(x['lusc_subtype'] for x in rows if x['lusc_subtype'])
ld_e = collections.Counter(x['luad_subtype'] for x in rows if x['luad_subtype'] and x['has_embedding'])
ud_e = collections.Counter(x['lusc_subtype'] for x in rows if x['lusc_subtype'] and x['has_embedding'])
print('=== lung subtype labels written:', out)
print(f'cohort: {len(cohort)} patients (LUAD {nL}, LUSC {nU}); embeddings present now: {emb_coh} (still running)')
print(f'LUAD subtype-labeled: {sum(ld.values())} / {nL}  dist={dict(ld)}  (with-emb {sum(ld_e.values())} {dict(ld_e)})')
print(f'LUSC subtype-labeled: {sum(ud.values())} / {nU}  dist={dict(ud)}  (with-emb {sum(ud_e.values())} {dict(ud_e)})')
print(f'TOTAL subtype-labeled rows: {len(rows)}  (with-emb {sum(1 for x in rows if x["has_embedding"])})')
print('source: authoritative (published TCGA calls); computed SSP concordance: NOT run (recorded)')

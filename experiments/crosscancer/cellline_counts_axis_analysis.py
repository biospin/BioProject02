#!/usr/bin/env python3
# PROVENANCE / INPUT-REGEN: this script reads data/_driver_mutations_subset.csv, which is a
# gene-filtered slice of DepMap 24Q4 OmicsSomaticMutations.csv. Regenerate it first with:
#   cols=['ModelID','HugoSymbol','ProteinChange','DNAChange','VariantInfo','Hotspot','HessDriver','MolecularConsequence']
#   genes={'EGFR','KRAS','BRAF','ALK','NRAS'}
#   pd.concat([c[c.HugoSymbol.isin(genes)] for c in pd.read_csv('OmicsSomaticMutations.csv',usecols=cols,chunksize=200000,low_memory=False)]).to_csv('_driver_mutations_subset.csv',index=False)
# NOTE: KRAS "any-mut" axis = G/Q-anchored missense + indel (hotspot codons 12/13/61); A146 not captured. G12C is exact-string (unaffected).
"""Cross-cancer Phase-1 cell-line feasibility gate: Lung NSCLC + Colorectal.
Mirrors BRCA methodology (experiments/kkkim/20260710_cellline_counts/).
DepMap 24Q4 x GDSC2 (27Oct23). Molecular data primary; literature fills gaps only.
"""
import pandas as pd, json, re, os

DATA='/home/kkkim/project/BioProject02/experiments/kkkim/20260710_cellline_counts/data'
OUT_L='/home/kkkim/project/BioProject02/experiments/crosscancer/LUNG_NSCLC/cellline_counts'
OUT_C='/home/kkkim/project/BioProject02/experiments/crosscancer/COLORECTAL/cellline_counts'
os.makedirs(OUT_L,exist_ok=True); os.makedirs(OUT_C,exist_ok=True)

m=pd.read_csv(f'{DATA}/Model.csv',low_memory=False)
gdsc=pd.read_excel(f'{DATA}/GDSC2_fitted_dose_response_27Oct23.xlsx')
mut=pd.read_csv(f'{DATA}/_driver_mutations_subset.csv',low_memory=False)
fus=pd.read_csv(f'{DATA}/OmicsFusionFiltered.csv')
sig=pd.read_csv(f'{DATA}/OmicsSignatures.csv',index_col=0)  # index=ModelID, MSIScore

gcells=gdsc.drop_duplicates('SANGER_MODEL_ID')[['SANGER_MODEL_ID','CELL_LINE_NAME','TCGA_DESC']]

def zscore_tail(cohort_ids, drug, sanger_map):
    """Return per-line Z_SCORE for a drug across cohort; lower LN_IC50/Z = more sensitive."""
    sub=gdsc[(gdsc['DRUG_NAME']==drug) & (gdsc['SANGER_MODEL_ID'].isin(cohort_ids))]
    sub=sub.drop_duplicates('SANGER_MODEL_ID')
    return sub[['SANGER_MODEL_ID','CELL_LINE_NAME','LN_IC50','Z_SCORE']]

# ============ helper: mutation classifiers ============
def egfr_activating(pchanges):
    """L858R, exon19 dels (E746_A750del family / p.E746..del), G719X, L861Q, exon20 ins (rare)."""
    hits=[]
    for p in pchanges:
        if not isinstance(p,str): continue
        s=p.replace('p.','')
        if re.match(r'^L858R$',s): hits.append(p)
        elif re.match(r'^L861[A-Z]',s): hits.append(p)
        elif re.match(r'^G719[A-Z]',s): hits.append(p)
        # exon19 in-frame deletion: E746_ or L747_ style deletions
        elif ('del' in s and re.match(r'^[EL]74[0-9]',s)): hits.append(p)
        # exon20 insertion
        elif ('ins' in s and re.match(r'^[A-Z]7[67][0-9]',s)): hits.append(p)
    return hits

def kras_variant(pchanges):
    g12c=[]; anymut=[]
    for p in pchanges:
        if not isinstance(p,str): continue
        s=p.replace('p.','')
        if re.match(r'^[GQ]\d+[A-Z]',s) or 'del' in s or 'ins' in s:  # missense at hotspot codons
            anymut.append(p)
        if s=='G12C': g12c.append(p)
    return g12c, anymut

def braf_v600e(pchanges):
    return [p for p in pchanges if isinstance(p,str) and p.replace('p.','').startswith('V600')]

# =====================================================================
# LUNG NSCLC
# =====================================================================
NSCLC_SUB={'Lung Adenocarcinoma','Lung Squamous Cell Carcinoma','Non-Small Cell Lung Cancer',
 'Large Cell Lung Carcinoma','Lung Adenosquamous Carcinoma','Poorly Differentiated Non-Small Cell Lung Cancer'}
lung=m[(m['OncotreeLineage']=='Lung') & (m['OncotreeSubtype'].isin(NSCLC_SUB))].copy()
lung_ids=set(lung['ModelID'])
# GDSC intersection on SangerModelID
lung=lung.merge(gcells,left_on='SangerModelID',right_on='SANGER_MODEL_ID',how='inner')
lung_cohort_ids=set(lung['ModelID'])
lung_sanger=set(lung['SangerModelID'])
print('=== LUNG NSCLC ===')
print('DepMap NSCLC (subtype-based):',len(lung_ids),'| ∩ GDSC2-screened:',len(lung_cohort_ids))
print('TCGA_DESC of cohort:',lung['TCGA_DESC'].value_counts().to_dict())

lmut=mut[mut['ModelID'].isin(lung_cohort_ids)]
def genepc(df,gene,mid):
    return list(df[(df['ModelID']==mid)&(df['HugoSymbol']==gene)]['ProteinChange'])

rows=[]
def _gtok(x):
    return str(x).split(' (')[0].strip()
fus['_L']=fus['LeftGene'].map(_gtok); fus['_R']=fus['RightGene'].map(_gtok)
alk_lung=fus[(fus['ModelID'].isin(lung_cohort_ids)) & ((fus['_L']=='ALK')|(fus['_R']=='ALK'))]
alk_lung_models={mid:sorted(set(alk_lung[alk_lung['ModelID']==mid]['FusionName'])) for mid in alk_lung['ModelID'].unique()}

for _,r in lung.iterrows():
    mid=r['ModelID']
    egfr=egfr_activating(genepc(lmut,'EGFR',mid))
    krasg12c,kras=kras_variant(genepc(lmut,'KRAS',mid))
    braf=braf_v600e(genepc(lmut,'BRAF',mid))
    alkf=alk_lung_models.get(mid,[])
    rows.append(dict(cell_line=r['StrippedCellLineName'],ModelID=mid,SangerModelID=r['SangerModelID'],
        TCGA_DESC=r['TCGA_DESC'],
        EGFR_activating=';'.join(egfr),ALK_fusion=';'.join(alkf),
        KRAS_G12C=';'.join(krasg12c),KRAS_anymut=';'.join(kras),BRAF_V600=';'.join(braf),
        axis_antiEGFR=int(len(egfr)>0),axis_antiALK=int(len(alkf)>0),
        axis_antiKRAS_G12C=int(len(krasg12c)>0),axis_KRASmut_any=int(len(kras)>0),
        ))
lt=pd.DataFrame(rows)
# chemo axis = no actionable EGFR/ALK/KRAS-G12C driver (pan-wildtype for targeted axes)
lt['axis_chemo_noTargetDriver']=((lt['axis_antiEGFR']==0)&(lt['axis_antiALK']==0)&(lt['axis_antiKRAS_G12C']==0)&(lt['axis_KRASmut_any']==0)).astype(int)
lt.to_csv(f'{OUT_L}/cellline_axis_table.csv',index=False)

lc={
 'axis_antiEGFR_activating':int(lt['axis_antiEGFR'].sum()),
 'axis_antiALK_fusion':int(lt['axis_antiALK'].sum()),
 'axis_antiKRAS_G12C':int(lt['axis_antiKRAS_G12C'].sum()),
 'axis_KRASmut_any':int(lt['axis_KRASmut_any'].sum()),
 'axis_chemo_noTargetDriver':int(lt['axis_chemo_noTargetDriver'].sum()),
}
print('LUNG axis counts:',lc)
# overlaps (mutual exclusivity check)
dbl=lt[(lt['axis_antiEGFR']+lt['axis_antiALK']+lt['axis_KRASmut_any'])>1][['cell_line','EGFR_activating','ALK_fusion','KRAS_anymut']]
print('Lung driver co-occurrence (should be rare):',len(dbl))

# drug validation lung
lung_val={}
for drug in ['Gefitinib','Afatinib','Osimertinib','Erlotinib','Crizotinib']:
    z=zscore_tail(lung_sanger,drug,None)
    z=z.merge(lt[['SangerModelID','axis_antiEGFR','axis_antiALK']],left_on='SANGER_MODEL_ID',right_on='SangerModelID',how='left')
    lung_val[drug]=z
    z.to_csv(f'{OUT_L}/_zscore_{drug}.csv',index=False)

lung_counts=dict(
 intersection_definition="DepMap 24Q4 NSCLC (OncotreeLineage=Lung AND OncotreeSubtype in {LUAD,LUSC,NSCLC,LargeCell,Adenosquamous,PoorlyDiff-NSCLC}; SCLC/carcinoid/NUT/meso/SMARCA4-undiff/immortalized EXCLUDED) INNER JOIN GDSC2-screened on SangerModelID",
 n_depmap_nsclc_subtype=len(lung_ids),
 n_intersection_gdsc=len(lung_cohort_ids),
 tcga_desc_breakdown=lung['TCGA_DESC'].value_counts().to_dict(),
 axes={
  'antiEGFR_activating':{'n':lc['axis_antiEGFR_activating'],'threshold':5,'GO':lc['axis_antiEGFR_activating']>=5,'label_basis':'DepMap 24Q4 OmicsSomaticMutations EGFR ProteinChange: L858R/exon19del/G719X/L861Q/exon20ins (activating only; T790M-alone excluded)'},
  'antiALK_fusion':{'n':lc['axis_antiALK_fusion'],'threshold':5,'GO':lc['axis_antiALK_fusion']>=5,'label_basis':'DepMap 24Q4 OmicsFusionFiltered ALK fusions in NSCLC lines (EML4-ALK etc; NPM1-ALK/lymphoma excluded by cohort restriction)'},
  'antiKRAS_G12C':{'n':lc['axis_antiKRAS_G12C'],'threshold':5,'GO':lc['axis_antiKRAS_G12C']>=5,'label_basis':'DepMap 24Q4 KRAS p.G12C (sotorasib-druggable subset)'},
  'KRASmut_any_context':{'n':lc['axis_KRASmut_any'],'threshold':5,'GO':lc['axis_KRASmut_any']>=5,'label_basis':'DepMap 24Q4 KRAS any hotspot missense/indel (context, not a standalone targeted axis)'},
  'chemo_noTargetDriver':{'n':lc['axis_chemo_noTargetDriver'],'threshold':5,'GO':lc['axis_chemo_noTargetDriver']>=5,'label_basis':'NSCLC lines lacking EGFR-activating / ALK-fusion / KRAS mut (chemo/IO baseline candidates)'},
 },
 driver_cooccurrence_n=int(len(dbl)),
 gdsc_drugs_present={'EGFR':['Gefitinib','Afatinib','Osimertinib','Erlotinib'],'ALK':['Crizotinib'],'KRAS_G12C':'ABSENT (Sotorasib not in GDSC2 27Oct23; MEK Selumetinib available as downstream proxy)','chemo':['Cisplatin','Paclitaxel','Docetaxel']},
 sources={'depmap':'DepMap 24Q4 Public figshare 27993248: Model.csv(51065297), OmicsSomaticMutations.csv(51065732), OmicsFusionFiltered.csv(51065693)','gdsc':'GDSC2_fitted_dose_response_27Oct23.xlsx'},
 caveats=[
  'Cohort = NSCLC only (SCLC explicitly excluded: 58 SCLC GDSC-screened lines would otherwise inflate the chemo axis).',
  'EGFR/ALK/KRAS axes are DepMap-molecular-derived (mutation/fusion primary); no literature backfill needed.',
  'ALK axis counts lines with any ALK fusion call in OmicsFusionFiltered restricted to NSCLC cohort; canonical EML4-ALK NSCLC lines are H2228/H3122.',
  'KRAS-G12C is the sotorasib-druggable subset; Sotorasib is NOT in GDSC2 so direct drug validation for this axis is not possible (MEKi proxy only).',
 ],
 go_nogo=('GO' if all([lc['axis_antiEGFR_activating']>=5, lc['axis_antiALK_fusion']>=5, lc['axis_antiKRAS_G12C']>=5, lc['axis_chemo_noTargetDriver']>=5]) else 'PARTIAL'),
 go_nogo_per_axis={'antiEGFR':lc['axis_antiEGFR_activating']>=5,'antiALK':lc['axis_antiALK_fusion']>=5,'antiKRAS_G12C':lc['axis_antiKRAS_G12C']>=5,'chemo':lc['axis_chemo_noTargetDriver']>=5},
)
json.dump(lung_counts,open(f'{OUT_L}/counts.json','w'),indent=2,default=str)

# =====================================================================
# COLORECTAL
# =====================================================================
print(); print('=== COLORECTAL ===')
bowel=m[m['OncotreeLineage']=='Bowel'].copy()
bowel_ids=set(bowel['ModelID'])
bowel=bowel.merge(gcells,left_on='SangerModelID',right_on='SANGER_MODEL_ID',how='inner')
crc_ids=set(bowel['ModelID'])
crc_sanger=set(bowel['SangerModelID'])
print('DepMap Bowel:',len(bowel_ids),'| ∩ GDSC2:',len(crc_ids))
print('TCGA_DESC:',bowel['TCGA_DESC'].value_counts().to_dict())

cmut=mut[mut['ModelID'].isin(crc_ids)]
# MSI calibration
canon_msi={'HCT116','DLD1','LOVO','RKO','SW48','LS174T','HCT15','LS180','CO115','SNU175','SNUC2B'}
canon_mss={'SW480','SW620','HT29','COLO205','CACO2','SW837','COLO320'}
bowel['MSIScore']=bowel['ModelID'].map(sig['MSIScore'])
# check separation
tmp=bowel.copy(); tmp['S']=tmp['StrippedCellLineName'].str.upper()
print('canonical MSI-high scores:',tmp[tmp['S'].isin(canon_msi)][['StrippedCellLineName','MSIScore']].values.tolist())
print('canonical MSS scores:',tmp[tmp['S'].isin(canon_mss)][['StrippedCellLineName','MSIScore']].values.tolist())

rows=[]
for _,r in bowel.iterrows():
    mid=r['ModelID']
    braf=braf_v600e(genepc(cmut,'BRAF',mid))
    krasg12c,kras=kras_variant(genepc(cmut,'KRAS',mid))
    msi=r['MSIScore']
    rows.append(dict(cell_line=r['StrippedCellLineName'],ModelID=mid,SangerModelID=r['SangerModelID'],
        TCGA_DESC=r['TCGA_DESC'],MSIScore=msi,
        BRAF_V600=';'.join(braf),KRAS_anymut=';'.join(kras),
        axis_antiBRAF_V600E=int(len(braf)>0),axis_KRASmut=int(len(kras)>0),
        axis_KRAS_WT=int(len(kras)==0),
        ))
ct=pd.DataFrame(rows)
MSI_THR=None  # set after calibration below
ct.to_csv(f'{OUT_C}/cellline_axis_table.csv',index=False)  # rewritten after MSI threshold
globals()['_ct']=ct; globals()['_bowel']=bowel; globals()['_crc_sanger']=crc_sanger
globals()['_lung_val']=lung_val; globals()['_lung_counts']=lung_counts
print('CRC prelim: BRAF-V600E',ct['axis_antiBRAF_V600E'].sum(),'KRASmut',ct['axis_KRASmut'].sum(),'KRAS-WT',ct['axis_KRAS_WT'].sum())

# ============ CRC MSI axis (calibrated threshold) ============
# Clean bimodal gap: MSI-high lines >=65, MSS <=4. Threshold=20 (any value in [5,65] identical).
MSI_THR=20.0
ct['axis_MSI_high']=(ct['MSIScore']>=MSI_THR).astype(int)
# reorder cols and rewrite
ct=ct[['cell_line','ModelID','SangerModelID','TCGA_DESC','MSIScore','axis_MSI_high',
       'BRAF_V600','axis_antiBRAF_V600E','KRAS_anymut','axis_KRASmut','axis_KRAS_WT']]
ct.to_csv(f'{OUT_C}/cellline_axis_table.csv',index=False)

cc={
 'axis_antiBRAF_V600E':int(ct['axis_antiBRAF_V600E'].sum()),
 'axis_MSI_high':int(ct['axis_MSI_high'].sum()),
 'axis_KRASmut':int(ct['axis_KRASmut'].sum()),
 'axis_KRAS_WT':int(ct['axis_KRAS_WT'].sum()),
 'axis_chemo_baseline':int(len(ct)),  # whole cohort = chemo baseline
}
# co-occurrence (CRC axes are NOT mutually exclusive; report overlaps)
braf_msi=int(((ct['axis_antiBRAF_V600E']==1)&(ct['axis_MSI_high']==1)).sum())
kras_msi=int(((ct['axis_KRASmut']==1)&(ct['axis_MSI_high']==1)).sum())
braf_kras=int(((ct['axis_antiBRAF_V600E']==1)&(ct['axis_KRASmut']==1)).sum())
print('CRC axis counts:',cc)
print(f'CRC overlaps: BRAF&MSI={braf_msi} KRAS&MSI={kras_msi} BRAF&KRAS={braf_kras}')

# CRC drug validation
crc_val={}
for drug in ['Dabrafenib','Trametinib','Selumetinib','5-Fluorouracil','Oxaliplatin','Irinotecan','SN-38']:
    z=zscore_tail(crc_sanger,drug,None)
    z=z.merge(ct[['SangerModelID','axis_antiBRAF_V600E','axis_MSI_high','axis_KRASmut']],left_on='SANGER_MODEL_ID',right_on='SangerModelID',how='left')
    crc_val[drug]=z
    z.to_csv(f'{OUT_C}/_zscore_{drug}.csv',index=False)

crc_counts=dict(
 intersection_definition='DepMap 24Q4 Bowel (OncotreeLineage=Bowel; colon/rectal adenocarcinoma) INNER JOIN GDSC2-screened on SangerModelID',
 n_depmap_bowel=len(bowel_ids),
 n_intersection_gdsc=len(crc_ids),
 tcga_desc_breakdown=bowel['TCGA_DESC'].value_counts().to_dict(),
 note='CRC axes are NOT partitioned: MSI / BRAF-V600E / KRAS-mut CO-OCCUR. Each counted independently over the same cohort; overlaps reported.',
 axes={
  'antiBRAF_V600E':{'n':cc['axis_antiBRAF_V600E'],'threshold':5,'GO':cc['axis_antiBRAF_V600E']>=5,'label_basis':'DepMap 24Q4 OmicsSomaticMutations BRAF p.V600E/V600x'},
  'MSI_high':{'n':cc['axis_MSI_high'],'threshold':5,'GO':cc['axis_MSI_high']>=5,'label_basis':f'DepMap 24Q4 OmicsSignatures MSIScore>={MSI_THR} (calibrated: canonical MSI-high HCT116/DLD1/LoVo/RKO/SW48/HCT15 all >=65; MSS SW480/SW620/HT29/COLO205 <=4; clean bimodal gap 4-65)'},
  'KRASmut':{'n':cc['axis_KRASmut'],'threshold':5,'GO':cc['axis_KRASmut']>=5,'label_basis':'DepMap 24Q4 KRAS hotspot mut (anti-EGFR resistance / MEK-axis context)'},
  'KRAS_WT':{'n':cc['axis_KRAS_WT'],'threshold':5,'GO':cc['axis_KRAS_WT']>=5,'label_basis':'KRAS wild-type (anti-EGFR-eligible context; NB cetuximab is antibody, absent from GDSC2)'},
  'chemo_baseline':{'n':cc['axis_chemo_baseline'],'threshold':5,'GO':True,'label_basis':'whole CRC cohort = 5-FU/oxaliplatin/irinotecan baseline'},
 },
 overlaps={'BRAF_and_MSI':braf_msi,'KRASmut_and_MSI':kras_msi,'BRAF_and_KRASmut':braf_kras},
 msi_calibration={'threshold':MSI_THR,'canonical_MSI_high_scores':{r['cell_line']:round(r['MSIScore'],1) for _,r in ct[ct['cell_line'].str.upper().isin(['HCT116','DLD1','LOVO','RKO','SW48','HCT15','LS180','LS174T'])].iterrows()},'n_below_gap_max':float(ct[ct['MSIScore']<MSI_THR]['MSIScore'].max())},
 gdsc_drugs_present={'BRAF':['Dabrafenib','Trametinib'],'BRAF_ABSENT':['Vemurafenib','Encorafenib','Cetuximab(antibody)'],'MEK_proxy':['Selumetinib','Trametinib'],'chemo':['5-Fluorouracil','Oxaliplatin','Irinotecan','SN-38']},
 sources={'depmap':'DepMap 24Q4 Public figshare 27993248: Model.csv(51065297), OmicsSomaticMutations.csv(51065732), OmicsSignatures.csv(51065726, MSIScore)','gdsc':'GDSC2_fitted_dose_response_27Oct23.xlsx'},
 caveats=[
  'MSI/BRAF/KRAS axes co-occur (BRAF-V600E CRC is often MSI-high); independent counts, not a single-assignment table.',
  'MSIScore threshold defensible: canonical MSI-high lines score >=65, MSS <=4, no CRC line falls in the 4-65 gap.',
  'anti-EGFR (cetuximab) cannot be drug-validated in GDSC2 (antibody, absent); KRAS-WT axis is a mutation-status feasibility proxy only.',
  'BRAF-V600E axis validation uses Dabrafenib/Trametinib (Vemurafenib/Encorafenib absent from GDSC2 27Oct23).',
 ],
 go_nogo=('GO' if all([cc['axis_antiBRAF_V600E']>=5, cc['axis_MSI_high']>=5, cc['axis_KRASmut']>=5, cc['axis_KRAS_WT']>=5]) else 'PARTIAL'),
 go_nogo_per_axis={'antiBRAF_V600E':cc['axis_antiBRAF_V600E']>=5,'MSI_high':cc['axis_MSI_high']>=5,'KRASmut':cc['axis_KRASmut']>=5,'KRAS_WT':cc['axis_KRAS_WT']>=5},
)
json.dump(crc_counts,open(f'{OUT_C}/counts.json','w'),indent=2,default=str)

# ============ drug-validation summary (sensitive tail = target+ lines with low Z) ============
def val_summary(zdf, axis_col, drug):
    zz=zdf.dropna(subset=['Z_SCORE'])
    if len(zz)==0 or axis_col not in zz: return f'{drug}: no data'
    pos=zz[zz[axis_col]==1]; neg=zz[zz[axis_col]==0]
    import numpy as np
    return f'{drug}: target+ n={len(pos)} medianZ={pos["Z_SCORE"].median():.2f} | target- n={len(neg)} medianZ={neg["Z_SCORE"].median():.2f}'
print('\n--- LUNG drug validation (Z<0 = sensitive) ---')
for d in ['Gefitinib','Afatinib','Osimertinib']:
    print(' ',val_summary(lung_val[d],'axis_antiEGFR',d))
print(' ',val_summary(lung_val['Crizotinib'],'axis_antiALK','Crizotinib'))
print('--- CRC drug validation ---')
for d in ['Dabrafenib','Trametinib','Selumetinib']:
    print(' ',val_summary(crc_val[d],'axis_antiBRAF_V600E',d))

# stash for report
json.dump({'lung':lung_counts,'crc':crc_counts},open('/tmp/claude-10005/_allcounts.json','w'),default=str,indent=2)
print('\nDONE. Outputs written to LUNG_NSCLC/ and COLORECTAL/ cellline_counts/')

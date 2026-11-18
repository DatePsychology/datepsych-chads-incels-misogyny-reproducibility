#!/usr/bin/env python3
"""Reanalyse EMS item responses in Selmer or Alexander datasets.

This script does NOT contain or simulate either study's respondent data.
Use data supplied by the authors with the matching JSON config.
All outcomes normalized to a 0-1 scale for comparability.
"""
import argparse
import json
import math
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

# A qualitative sensitivity partition specified before respondent-level data access.
# NOT empirically validated factors or established ground truth.
SCALES = {
    'full_13': list(range(1,14)),
    'core_hostility_4': [4,7,8,9],
    'preferences_grievance_4': [2,5,6,12],
    'romantic_distress_5': [1,3,10,11,13],
    'hostility_plus_grievance_8': [2,4,5,6,7,8,9,12]
}
PRIMARY = ['full_13','core_hostility_4','preferences_grievance_4','romantic_distress_5']


def c_alpha(frame):
    x = frame.dropna().astype(float).to_numpy()
    if x.shape[0] < 3 or x.shape[1] < 2:
        return math.nan
    itemvar = np.var(x,axis=0,ddof=1).sum()
    totalvar = np.var(x.sum(axis=1),ddof=1)
    return (x.shape[1] / (x.shape[1]-1))*(1-itemvar/totalvar) if totalvar > 0 else math.nan


def pearson_ci(r,n):
    if not np.isfinite(r) or n <= 3 or abs(r)>=1:
        return [math.nan,math.nan]
    z = np.arctanh(r)
    spread = stats.norm.ppf(0.975)/np.sqrt(n-3)
    return list(np.tanh([z-spread,z+spread]))


def standardized_d(a,b):
    a,b = np.asarray(a,dtype=float),np.asarray(b,dtype=float)
    if len(a)<2 or len(b)<2:return math.nan
    pool = ((len(a)-1)*np.var(a,ddof=1)+(len(b)-1)*np.var(b,ddof=1))/(len(a)+len(b)-2)
    return (np.mean(a)-np.mean(b))/np.sqrt(pool) if pool>0 else math.nan


def group_test(df, score, predicate_a, predicate_b, description):
    a=df.loc[predicate_a,score].dropna().to_numpy(dtype=float)
    b=df.loc[predicate_b,score].dropna().to_numpy(dtype=float)
    if min(len(a),len(b)) < 3:return None
    t=stats.ttest_ind(a,b,equal_var=False)
    return {'test':description,'outcome':score,'n_a':len(a),'n_b':len(b),
            'mean_a_0to1':float(np.mean(a)),'mean_b_0to1':float(np.mean(b)),
            'mean_difference_0to1':float(np.mean(a)-np.mean(b)),
            'cohens_d':float(standardized_d(a,b)),'welch_t':float(t.statistic),
            'p_two_sided':float(t.pvalue)}


def corr_test(df,x,y,description):
    d=df[[x,y]].dropna()
    if len(d)<5 or d[x].nunique()<2 or d[y].nunique()<2:return None
    rp,pp=stats.pearsonr(d[x],d[y]);rs,ps=stats.spearmanr(d[x],d[y])
    lo,hi=pearson_ci(rp,len(d))
    return {'test':description,'predictor':x,'outcome':y,'n':len(d),
            'pearson_r':float(rp),'pearson_p':float(pp),'pearson_ci_low':float(lo),
            'pearson_ci_high':float(hi),'spearman_rho':float(rs),'spearman_p':float(ps)}


def add_holm(table, field='p_two_sided'):
    table=table.copy()
    if table.empty or field not in table.columns:return table
    table['p_holm_descriptive_family']=np.nan
    for name, idx in table.groupby('test').groups.items():
        v=table.loc[idx,field]
        mask=v.notna()
        if mask.sum():
            table.loc[v[mask].index,'p_holm_descriptive_family']=multipletests(v[mask],method='holm')[1]
    return table


def bool_value(x):
    if pd.isna(x):return np.nan
    if isinstance(x,(int,float,np.integer,np.floating)):
        if x == 1:return True
        if x == 0:return False
    s=str(x).strip().lower()
    if s in {'yes','y','true','1','t'}:return True
    if s in {'no','n','false','0','f'}:return False
    return np.nan


def validate_and_score(df, cfg):
    ems=cfg['ems_items']
    assert len(ems)==13 and len(set(ems))==13, 'Exactly 13 distinct EMS columns required in item order'
    need=list(ems)
    if cfg['study']=='selmer':need += [cfg['soi_have'],cfg['soi_want']]+cfg.get('covariates',[])
    elif cfg['study']=='alexander':need += [cfg['incel_self'],cfg['incel_operational']]+cfg.get('chad_items',[])
    else:raise ValueError('study must be selmer or alexander')
    missing=[x for x in need if x not in df.columns]
    if missing:raise ValueError('Missing columns: '+', '.join(missing))
    for c in ems:
        df[c]=pd.to_numeric(df[c],errors='coerce')
        if df[c].dropna().lt(1).any() or df[c].dropna().gt(7).any():
            raise ValueError(f'{c}: EMS items expected 1..7; recode before analysis')
    for k, indices in SCALES.items():
        cols=[ems[i-1] for i in indices]
        # Complete cases for each subscale. Unobserved items never silently imputed.
        df[k]=(df[cols].mean(axis=1,skipna=False)-1)/6
    return df


def describe_psychometrics(df,cfg,out):
    rec=[]
    for name,indices in SCALES.items():
        cols=[cfg['ems_items'][i-1] for i in indices]
        x=df[cols].dropna()
        rec.append({'scale':name,'items':','.join(map(str,indices)), 'complete_n':len(x),
                    'alpha':c_alpha(df[cols]),'mean_0to1':df[name].mean(),
                    'sd_0to1':df[name].std(),'floor_0to1_n':int((df[name]==0).sum()),
                    'ceiling_0to1_n':int((df[name]==1).sum())})
    pd.DataFrame(rec).to_csv(out/'scale_diagnostics.csv',index=False)
    x=df[cfg['ems_items']].dropna()
    if len(x) >= 10:
        # Pearson PCA is a diagnostic, NOT evidence of a validated factor model.
        corr=x.corr().to_numpy()
        eig=np.linalg.eigvalsh(corr)[::-1]
        pd.DataFrame({'component':np.arange(1,14),'eigenvalue':eig,
                      'fraction_variance':eig/13}).to_csv(out/'pearson_pca_diagnostic.csv',index=False)
    df[PRIMARY].corr().to_csv(out/'subscale_correlations.csv')
    for name,indices in SCALES.items():
        # item-total corrected correlations to assess whether a grievance item is redundant or anomalous
        cols=[cfg['ems_items'][i-1] for i in indices]
        if len(cols)<3:continue
        rows=[]
        for col in cols:
            other=[z for z in cols if z!=col]
            x=df[[col]+other].dropna()
            if len(x)>=5 and x[col].nunique()>1 and x[other].sum(axis=1).nunique()>1:
                r=stats.pearsonr(x[col],x[other].sum(axis=1)).statistic
            else:r=np.nan
            rows.append({'scale':name,'item':col,'n':len(x),'corrected_item_total_r':r})
        pd.DataFrame(rows).to_csv(out/f'item_total_{name}.csv',index=False)


def analyze_selmer(df,cfg,out):
    for x in [cfg['soi_have'],cfg['soi_want']]:
        df[x]=pd.to_numeric(df[x],errors='coerce')
    records=[]
    have,want=cfg['soi_have'],cfg['soi_want']
    # Build same-outcome models; report both unadjusted/adjusted and interaction sensitivity.
    cov=cfg.get('covariates',[])
    cats=set(cfg.get('categoricals',[]))
    terms=[f'C(Q({v!r}))' if v in cats else f'Q({v!r})' for v in cov]
    base=f'Q({have!r}) + Q({want!r})'
    for y in SCALES:
        for model,rhs in [('main_effects',base),
                          ('interaction',f'Q({have!r}) * Q({want!r})'),
                          ('main_effects_adjusted',base+(' + '+' + '.join(terms) if terms else '')),
                          ('interaction_adjusted',f'Q({have!r}) * Q({want!r})'+(' + '+' + '.join(terms) if terms else ''))]:
            try:
                fit=smf.ols(f'Q({y!r}) ~ {rhs}',data=df).fit(cov_type='HC3')
                for term in fit.params.index:
                    if term=='Intercept':continue
                    ci=fit.conf_int().loc[term].tolist()
                    records.append({'outcome':y,'model':model,'term':term,'n':int(fit.nobs),
                                    'estimate':float(fit.params[term]),'se_hc3':float(fit.bse[term]),
                                    'p':float(fit.pvalues[term]),'ci_low':ci[0],'ci_high':ci[1]})
            except Exception as exc:
                warnings.warn(f'Model {model} for {y} failed: {exc}')
    pd.DataFrame(records).to_csv(out/'selmer_regressions_hc3.csv',index=False)
    corrs=[corr_test(df,have,y,'SOI-Have versus outcome') for y in PRIMARY]
    corrs += [corr_test(df,want,y,'SOI-Want versus outcome') for y in PRIMARY]
    pd.DataFrame([z for z in corrs if z]).to_csv(out/'selmer_correlations.csv',index=False)


def analyze_alexander(df,cfg,out):
    s=cfg['incel_self'];o=cfg['incel_operational']
    df['_self_id']=df[s].map(bool_value)
    df['_op_id']=df[o].map(bool_value)
    inc=df['_self_id'].eq(True)
    op_only=df['_self_id'].eq(False)&df['_op_id'].eq(True)
    neither=df['_self_id'].eq(False)&df['_op_id'].eq(False)
    groups={'self_incels':int(inc.sum()),'operational_only':int(op_only.sum()),
            'neither':int(neither.sum()),'both_yes':int((inc&df['_op_id'].eq(True)).sum()),
            'self_only':int((inc&df['_op_id'].eq(False)).sum()),
            'missing_any_flag':int((df['_self_id'].isna()|df['_op_id'].isna()).sum())}
    (out/'group_counts.json').write_text(json.dumps(groups,indent=2))
    rec=[]
    # The published comparisons use self-identifiers against everybody else,
    # and operational-only against neither (both incel categories removed).
    for y in SCALES:
        rec.extend([group_test(df,y,inc,df['_self_id'].eq(False),'self-identifying versus other men'),
                    group_test(df,y,op_only,neither,'operational-only versus neither')])
    table=pd.DataFrame([z for z in rec if z])
    add_holm(table).to_csv(out/'alexander_group_comparisons.csv',index=False)
    chad=cfg.get('chad_items')
    if chad:
        assert len(chad)==15 and len(set(chad))==15, '15 distinct Chad Scale items required'
        for col in chad:
            df[col]=pd.to_numeric(df[col],errors='coerce')
        df['_chad_raw_mean']=df[chad].mean(axis=1,skipna=False)
        c=[]
        for y in SCALES:
            c.append(corr_test(df,'_chad_raw_mean',y,'full sample'))
            tmp=df.loc[neither]
            c.append(corr_test(tmp,'_chad_raw_mean',y,'neither incel category'))
        pd.DataFrame([z for z in c if z]).to_csv(out/'alexander_chad_correlations.csv',index=False)
        # Additional sensitivity: association controlling both incel flags.
        for y in SCALES:
            sub=df.loc[df['_self_id'].notna()&df['_op_id'].notna()].copy()
            sub['_self_i']=sub['_self_id'].astype(int)
            sub['_op_i']=sub['_op_id'].astype(int)
            fit=smf.ols(f'{y} ~ _chad_raw_mean + _self_i + _op_i',data=sub).fit(cov_type='HC3')
            pd.DataFrame([{'outcome':y,'n':int(fit.nobs),'term':k,'beta':fit.params[k],
                           'p':fit.pvalues[k],'ci_low':fit.conf_int().loc[k,0],
                           'ci_high':fit.conf_int().loc[k,1]} for k in fit.params.index])\
                .to_csv(out/f'alexander_adjusted_{y}.csv',index=False)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True,help='Authorized, de-identified CSV supplied by study author')
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    cfg=json.loads(args.config.read_text(encoding='utf-8'))
    args.output.mkdir(parents=True,exist_ok=True)
    df=validate_and_score(pd.read_csv(args.input),cfg)
    describe_psychometrics(df,cfg,args.output)
    if cfg['study']=='selmer':analyze_selmer(df,cfg,args.output)
    else:analyze_alexander(df,cfg,args.output)
    summary={'study':cfg['study'],'input_rows':len(df),'source_path':str(args.input),
             'input_data_provided_by_authors':True,
             'completed_n_per_score':{k:int(df[k].notna().sum()) for k in SCALES},
             'warnings':['Analysis is exploratory sensitivity analysis unless registered before observing data.',
                         'Suggested three subscales are content-defined, not validated latent factors.',
                         'Tests do not establish causality; observational/self-reported sampling limits persist.']}
    (args.output/'run_manifest.json').write_text(json.dumps(summary,indent=2))
    print(f"Completed {cfg['study']} sensitivity analysis: {len(df)} rows. Outputs: {args.output}")

if __name__=='__main__':main()

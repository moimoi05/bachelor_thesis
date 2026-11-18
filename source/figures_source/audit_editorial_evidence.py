"""Read-only audit of clinical matching, Cox training logs and reported PCA results.
Only aggregate audit tables are exported; original inputs are never modified.
"""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, importlib.util, json
import numpy as np
import pandas as pd
S=Path(__file__).resolve().parents[1]
D=Path('/home/data/user/nguyenphuongnam/data_alzheimer')
ROOT=D.parent/'alzheimer_training'
source=D/'scripts/16_build_clinical_core_v1.py'
spec=importlib.util.spec_from_file_location('clinical_source',source)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
inputs=[source,D/'metadata/processed/training_manifest_with_raw_mri.csv',D/'clinical/clinical_longitudinal_raw.csv',S/'evidence/A6_FINAL_TRAIN_VAL_TEST_EVALUATION.json',S/'evidence/FINAL_STANDARDIZED_VALIDATION_BENCHMARK.json',S/'evidence/official_pca_manifest.json',ROOT/'phase_06_ablation/src/p06_ablation/samplers.py',ROOT/'phase_06_ablation/src/p06_ablation/trainer.py']
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
scans=read(inputs[1]);scans=[r for r in scans if int(r['visit_index'])==0]
assert len(scans)==359 and len({r['RID'] for r in scans})==359
clinical={(r['RID'],r['visit_index'],r['image_id']):r for r in read(inputs[2])}
rows=[];offsets=[];failed_detail=[]
for name,file,field,outcol,hi,done in [('MMSE','MMSE_21Jul2026.csv','MMSCORE','mmse_total_score',30,True),('CDR','CDR_21Jul2026.csv','CDGLOBAL','cdr_global',3,False)]:
 path=D/'data/raw/clinical'/file;inputs.append(path);by=defaultdict(list)
 for r in read(path):by[r['RID']].append(r)
 for scan in scans:
  target=mod.day(scan['study_date']); candidates=by[scan['RID']]
  valid=[r for r in candidates if mod.valid(r,'VISDATE',field,0,hi,require_done=done)]
  matched,off=mod.nearest(valid,target,'VISDATE')
  saved=clinical[scan['RID'],scan['visit_index'],scan['image_id']]
  assert (matched is not None)==bool(saved[outcol]),'Mismatch with frozen clinical input'
  if matched:
   assert float(matched[field])==float(saved[outcol])
   reason='observed_valid'
  else:
   dates=[mod.day(r['VISDATE']) for r in candidates if mod.day(r.get('VISDATE')) is not None]
   in_window=[r for r in candidates if mod.day(r.get('VISDATE')) is not None and abs((mod.day(r['VISDATE'])-target).days)<=90]
   reason='no_dated_record' if not dates else ('outside_90_days' if not in_window else 'within_90_but_invalid')
   if in_window:
    for r in in_window:
     failed_detail.append(dict(variable=name,qc_error=r.get('HAS_QC_ERROR')=='1',invalid_value=mod.number(r.get(field),0,hi) is None,not_done=done and r.get('DONE')=='0'))
  rows.append(dict(variable=name,split=saved['split'],reason=reason))
  valid_days=[abs((mod.day(r['VISDATE'])-target).days) for r in valid]
  offsets.append(dict(variable=name,missing=matched is None,nearest_valid_abs_days=min(valid_days) if valid_days else np.nan))
agg=pd.DataFrame(rows).groupby(['variable','split','reason']).size().rename('n').reset_index()
agg.to_csv(S/'evidence/clinical_missingness_audit.csv',index=False)
totals=pd.DataFrame(rows).groupby(['variable','reason']).size().rename('n').reset_index().to_dict('records')
interval=np.array([(mod.day(s['study_date'])-mod.day(s['baseline_date'])).days for s in scans])
summary={'clinical_counts':totals,'invalid_window_records':failed_detail,'s1_minus_baseline_days':dict(min=int(interval.min()),median=float(np.median(interval)),q1=float(np.quantile(interval,.25)),q3=float(np.quantile(interval,.75)),max=int(interval.max())),'nearest_valid_abs_days':pd.DataFrame(offsets).groupby(['variable','missing']).nearest_valid_abs_days.agg(['count','median','min','max']).reset_index().to_dict('records')}
report=json.loads(inputs[3].read_text()); training=[]
for ck in report['checkpoint_audit']:
 path=Path(ck['path']).parent.parent/'history.json';inputs.append(path);h=json.loads(path.read_text())
 assert all(r['unique_train_rids']==251 and r['duplicate_train_rids']==0 for r in h)
 training.append(dict(seed=h[0]['seed'],epochs=len(h),valid_batches=sum(r['train_valid_cox_batches'] for r in h),invalid_batches=sum(r['train_invalid_cox_batches'] for r in h),min_valid_per_epoch=min(r['train_valid_cox_batches'] for r in h),max_valid_per_epoch=max(r['train_valid_cox_batches'] for r in h)))
pd.DataFrame(training).to_csv(S/'evidence/cox_sampler_audit.csv',index=False);summary['training']=training
b=json.loads(inputs[4].read_text());p10=next(r for r in b['deep_models'] if r['model']=='P10')
summary['pca_cindex']=[]
for seed,expected in zip([20260727,20260728,20260729],[38,69,2]):
 path=ROOT/f'phase_10_paper_cnn_tlstm_reproduction/artifacts/pca/seed_{seed}/official_pca_manifest.json'
 inputs.append(path);pca=json.loads(path.read_text());assert pca['component_count']==expected
 summary['pca_cindex'].append(dict(seed=seed,pca_components=pca['component_count'],explained_variance=pca['explained_variance'],val_cindex=p10[f'seed_{seed}']))
summary['sources']=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]
(S/'evidence/editorial_audit.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in summary.items() if k!='sources'},indent=2,ensure_ascii=False))

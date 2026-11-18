"""Check the normalized weighted-pair AUC formula against the evaluation pipeline."""
from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
from sksurv.nonparametric import CensoringDistributionEstimator
from sksurv.util import Surv
S=Path(__file__).resolve().parents[1]
ROOT=Path('/home/data/user/nguyenphuongnam/alzheimer_training')
sys.path.insert(0,str(ROOT/'scripts'))
from analyze_rc_free_survival import horizon_auc

def weighted_pair_auc(train,frame,h):
    ytrain=Surv.from_arrays(train.event.astype(bool),train.time)
    censor=CensoringDistributionEstimator().fit(ytrain)
    cases=(frame.event.to_numpy()==1)&(frame.time.to_numpy()<=h)
    controls=frame.time.to_numpy()>h
    assert cases.any() and controls.any()
    # Same adjacent-score tie grouping as scikit-survival's default tied_tol.
    scores=frame.risk.to_numpy();order=np.argsort(-scores)
    block=np.r_[0,np.cumsum(np.abs(np.diff(scores[order]))>1e-8)]
    ranks=np.empty(len(frame),dtype=int);ranks[order]=block
    delta=ranks[controls][None,:]-ranks[cases][:,None]
    concordance=(delta>0).astype(float)+.5*(delta==0)
    weights=1/censor.predict_proba(frame.time.to_numpy()[cases])
    value=np.sum(weights[:,None]*concordance)/(controls.sum()*weights.sum())
    control_weight=1/censor.predict_proba([h])[0]
    expanded=np.sum(weights[:,None]*concordance*control_weight)/(controls.sum()*control_weight*weights.sum())
    assert abs(value-expanded)<1e-12
    return float(value)

def compare(train,frame,h,name):
    expected=horizon_auc(train,frame,h)
    assert expected['status']=='ok',expected
    actual=weighted_pair_auc(train,frame,h)
    assert abs(actual-expected['auc'])<1e-12,(name,actual,expected)
    return dict(case=name,horizon=h,formula_auc=actual,reference_auc=expected['auc'],absolute_error=abs(actual-expected['auc']))

report=json.loads((S/'evidence/A6_FINAL_TRAIN_VAL_TEST_EVALUATION.json').read_text())
checks=[]
for seed in [20260727,20260728,20260729]:
    pred=ROOT/'project_reports/a6_final_predictions'
    train=pd.read_csv(pred/f'seed_{seed}_train.csv')
    for split in ['val','test']:
        frame=pd.read_csv(pred/f'seed_{seed}_{split}.csv')
        for h in [2.,3.,5.]:checks.append(compare(train,frame,h,f'{seed}_{split}'))
train=pd.DataFrame({'time':[1.,2.,3.,4.,5.,6.,7.,8.,10.],'event':[1,0,1,0,1,0,1,1,0]})
frame=pd.DataFrame({'time':[1.5,2.5,3.5,5.,12.],'event':[1,1,0,1,0],'risk':[2.,2.,1.,.5,-1.]})
checks.append(compare(train,frame,4.,'exact_ties_and_followup_beyond_train'))
frame['risk']=[1.,1.+4e-9,1.+8e-9,.5,-1.]
checks.append(compare(train,frame,4.,'adjacent_tolerance_ties'))
frame['risk']=0.
r=compare(train,frame,4.,'all_scores_tied');assert abs(r['formula_auc']-.5)<1e-12;checks.append(r)
# Event exactly at h is a case, censoring exactly at h is excluded.
frame['time']=[1.5,4.,4.,5.,12.];frame['risk']=[3.,2.,1.,.5,-1.]
checks.append(compare(train,frame,4.,'event_and_censoring_at_horizon'))
(S/'evidence/ipcw_formula_checks.json').write_text(json.dumps(checks,indent=2))
print(f'{len(checks)} weighted-pair AUC checks passed; max error {max(r["absolute_error"] for r in checks):.3g}')

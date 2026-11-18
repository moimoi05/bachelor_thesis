"""Reproduce ROC and training figures from frozen predictions and original histories."""
from pathlib import Path
import sys, json, hashlib, os
os.environ.setdefault('MPLCONFIGDIR','/tmp/thesis8-mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sksurv.nonparametric import CensoringDistributionEstimator
from sksurv.util import Surv
S=Path(__file__).resolve().parents[1]
ROOT=Path('/home/data/user/nguyenphuongnam/alzheimer_training')
sys.path.insert(0,str(ROOT/'scripts'))
import analyze_rc_free_survival as original
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False})
seeds=original.SEEDS
report=json.loads((S/'evidence/A6_FINAL_TRAIN_VAL_TEST_EVALUATION.json').read_text())
frames,subjects,files=original.load_inputs()
provenance=[]
def record(p):
 p=Path(p); provenance.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
def save(fig,name):
 for ext in ['pdf','png','svg']:fig.savefig(S/'image'/f'{name}.{ext}',dpi=300,bbox_inches='tight')
 plt.close(fig)
rows=[]; metrics=[]
fig,axes=plt.subplots(2,3,figsize=(9,7.3),layout='constrained')
expected=pd.read_csv(S/'evidence/auc_summary.csv')
for ri,split in enumerate(['val','test']):
 for ci,h in enumerate([2.,3.,5.]):
  ax=axes[ri,ci]; all_tpr=[]; aucs=[]; grid=np.linspace(0,1,1001)
  color=['#1676ad','#d17a22'][ri]
  for si,seed in enumerate(seeds):
   train=frames[seed,'train']; f=frames[seed,split]
   reference=original.horizon_auc(train,f,h); assert reference['status']=='ok'
   tau=np.nextafter(h,np.inf)
   yy=Surv.from_arrays(f.event.astype(bool).to_numpy() & (f.time.to_numpy()<=tau),np.minimum(f.time.to_numpy(),tau))
   censor=CensoringDistributionEstimator().fit(Surv.from_arrays(train.event.astype(bool),train.time))
   weights=censor.predict_ipcw(yy)
   order=np.argsort(-f.risk.to_numpy(),kind='stable'); score=f.risk.to_numpy()[order]
   cases=((f.event.to_numpy()==1)&(f.time.to_numpy()<=h))[order]; controls=(f.time.to_numpy()>h)[order]
   tp=np.cumsum(cases*weights[order]); fp=np.cumsum(controls)
   # Same tied-score tolerance as cumulative_dynamic_auc; retain last of each tie block.
   keep=np.r_[np.abs(np.diff(score))>1e-8,True]
   tpr=np.r_[0,tp[keep]/tp[-1]]; fpr=np.r_[0,fp[keep]/fp[-1]]
   auc=float(np.trapezoid(tpr,fpr)); assert np.isclose(auc,reference['auc'],atol=1e-12)
   assert np.all(np.diff(tpr)>=0) and np.all(np.diff(fpr)>=0)
   aucs.append(auc)
   ax.step(fpr,tpr,where='post',color=color,alpha=.35,lw=.85,marker='o',ms=2.7)
   all_tpr.append(np.interp(grid,fpr,tpr))
   for x,y in zip(fpr,tpr): rows.append(dict(split=split,seed=seed,horizon=h,fpr=x,tpr=y))
   metrics.append(dict(split=split,seed=seed,**reference))
  mean=np.mean(all_tpr,axis=0); sd=np.std(all_tpr,axis=0,ddof=1)
  ax.plot(grid,mean,color=color,lw=1.8,label='ROC trung bình nội suy')
  ax.fill_between(grid,np.maximum(0,mean-sd),np.minimum(1,mean+sd),color=color,alpha=.13)
  ax.plot([0,1],[0,1],'--',color='.6',lw=.8)
  ex=expected[(expected.split==split)&(expected.horizon==h)].iloc[0]
  assert np.isclose(np.mean(aucs),ex.auc_mean,atol=1e-10) and np.isclose(np.std(aucs,ddof=1),ex.auc_sd,atol=1e-10)
  ax.text(.98,.06,f'AUC = {np.mean(aucs):.4f} ± {np.std(aucs,ddof=1):.4f}\n{reference["cases"]} biến cố / {reference["controls"]} đối chứng',ha='right',transform=ax.transAxes,fontsize=9)
  title='Xác thực' if split=='val' else 'Kiểm tra hậu nghiệm'
  ax.set(title=f'({chr(97+ri*3+ci)}) {title}\nMốc {int(h)} năm',xlabel='1 − Độ đặc hiệu',ylabel='Độ nhạy',xlim=(0,1),ylim=(0,1.02))
  ax.grid(alpha=.15)
save(fig,'empirical-ipcw-roc')
pd.DataFrame(rows).to_csv(S/'evidence/roc_coordinates.csv',index=False)
pd.DataFrame(metrics).to_csv(S/'evidence/roc_auc_verified.csv',index=False)
fig,axes=plt.subplots(1,2,figsize=(9,4.5),layout='constrained'); ax=axes[0]; right=ax.twinx()
colors=['#1676ad','#d17a22','#38945a']; histories=[]; summaries=[]
for i,audit in enumerate(report['checkpoint_audit']):
 run=Path(audit['path']).parent.parent; hp=run/'history.json'; sp=run/'final_summary.json'; record(hp);record(sp)
 hist=pd.DataFrame(json.loads(hp.read_text())); summary=json.loads(sp.read_text()); seed=seeds[i]
 assert hist.seed.eq(seed).all() and len(hist)==summary['completed_epochs']
 best=summary['best_epoch']; selected=hist[hist.epoch==best].iloc[0]
 assert np.isclose(selected.val_cindex,summary['best_validation_cindex'])
 col=colors[i]; label=str(seed)
 ax.plot(hist.epoch,hist.train_loss,color=col,lw=1,label=label)
 right.plot(hist.epoch,hist.val_cox_loss_full,color=col,lw=1,ls='--')
 axes[1].plot(hist.epoch,hist.val_cindex,color=col,lw=1,label=label)
 axes[1].scatter([best],[selected.val_cindex],marker='*',s=100,color=col,zorder=5)
 axes[1].scatter([hist.epoch.iloc[-1]],[hist.val_cindex.iloc[-1]],marker='s',s=22,color=col)
 summaries.append(dict(seed=seed,best_epoch=int(best),stop_epoch=int(hist.epoch.max()),best_cindex=float(selected.val_cindex),first_train=float(hist.train_loss.iloc[0]),last_train=float(hist.train_loss.iloc[-1]),first_val=float(hist.val_cox_loss_full.iloc[0]),last_val=float(hist.val_cox_loss_full.iloc[-1])))
 histories.append(hist[['seed','epoch','train_loss','val_cox_loss_full','val_cindex','best_epoch','learning_rate','early_stop_counter']])
ax.set(title='(a) Hàm mất mát Cox',xlabel='Vòng huấn luyện',ylabel='Huấn luyện: trung bình loss theo lô')
right.set_ylabel('Xác thực: loss toàn tập (nét đứt)')
axes[1].set(title='(b) C-index xác thực',xlabel='Vòng huấn luyện',ylabel='C-index',ylim=(.4,1))
for a in axes:a.grid(alpha=.15);a.legend(fontsize=9,loc='lower right')
save(fig,'empirical-training')
pd.concat(histories).to_csv(S/'evidence/training_history.csv',index=False)
(S/'evidence/training_summary.json').write_text(json.dumps(summaries,indent=2))
for p in files: record(p)
(S/'evidence/empirical_provenance.json').write_text(json.dumps(provenance,indent=2))
print(json.dumps(summaries,indent=2))

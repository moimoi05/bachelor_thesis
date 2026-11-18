"""Aggregate participant characteristics at first selected MRI; no imputation."""
from pathlib import Path
import json,tarfile,tempfile,hashlib
import numpy as np
import pandas as pd
import pyreadr
from scipy.stats import kruskal,chi2_contingency
S=Path(__file__).resolve().parents[1]; D=Path('/home/data/user/nguyenphuongnam/data_alzheimer')
paths=[D/'metadata/processed/model_ready_manifest_v1.csv',D/'metadata/processed/training_manifest_with_raw_mri.csv',D/'clinical/clinical_longitudinal_raw.csv',D/'data/raw/clinical/ADNIMERGE2.tar.gz']
m=pd.read_csv(paths[0]);raw=pd.read_csv(paths[1]);clinical=pd.read_csv(paths[2]);keys=['RID','visit_index','image_id']
f=m.merge(raw[keys+['study_date','baseline_phase','prediction_date','outcome_date']],on=keys,validate='one_to_one')
f=f.merge(clinical[keys+['mmse_total_score','cdr_global','cdr_sum_of_boxes']],on=keys,validate='one_to_one')
assert len(f)==1077 and f.RID.nunique()==359 and f.groupby('RID').split.nunique().eq(1).all()
f.study_date=pd.to_datetime(f.study_date)
first=f.sort_values(['RID','study_date']).drop_duplicates('RID').copy()
times=f.sort_values(['RID','study_date']).groupby('RID').study_date.apply(list)
first['interval12']=first.RID.map(lambda r:(times[r][1]-times[r][0]).days)
first['interval13']=first.RID.map(lambda r:(times[r][2]-times[r][0]).days)
with tarfile.open(paths[3]) as tar, tempfile.NamedTemporaryFile(suffix='.rda') as tmp:
 tmp.write(tar.extractfile('ADNIMERGE2/data/PTDEMOG.rda').read());tmp.flush();demo=next(iter(pyreadr.read_r(tmp.name).values()))
demo['VISDATE']=pd.to_datetime(demo.VISDATE); demo['row_order']=np.arange(len(demo))
for col in ['age','male','education']:first[col]=np.nan
for idx,row in first.iterrows():
 d=demo[(demo.RID==row.RID)&(demo.VISDATE<=row.study_date)].sort_values(['VISDATE','row_order'],ascending=False)
 # Use the latest available nonmissing pre-MRI record separately per field.
 for src,dest in [('PTDOB','age'),('PTGENDER','male'),('PTEDUCAT','education')]:
  v=d.dropna(subset=[src])
  if not len(v):continue
  if dest=='age':
   birth=pd.to_datetime(v.iloc[0][src],format='%m/%Y',errors='coerce')
   if pd.notna(birth):first.loc[idx,dest]=(pd.Timestamp(row.study_date).to_pydatetime()-(birth.to_pydatetime()+__import__("datetime").timedelta(days=14))).days/365.25
  elif dest=='male':
   val=str(v.iloc[0][src]); first.loc[idx,dest]=1 if val=='Male' else (0 if val=='Female' else np.nan)
  else:
   val=float(v.iloc[0][src]);first.loc[idx,dest]=val if val>=0 else np.nan
splits=['train','val','test']
assert [len(first[first.split==s]) for s in splits]==[251,54,54]
assert [int(first[first.split==s].event.sum()) for s in splits]==[74,16,16]
variables=[('age','Tuổi tại MRI đầu (năm)'),('male','Nam, n (\\%)'),('education','Học vấn (năm)'),('mmse_total_score','MMSE ban đầu'),('cdr_global','CDR-global ban đầu'),('cdr_sum_of_boxes','CDR-SB ban đầu'),('interval12',r'$s_2-s_1$ (ngày)'),('interval13',r'$s_3-s_1$ (ngày)'),('survival_time_years',r'$t_i$ (năm), TB $\pm$ SD'),('followup_median',r'$t_i$ (năm), trung vị [Q1; Q3]')]
summary=[]; rows=[]; groups=[first[(first.split==s)&(first.event==e)] for s in splits for e in [0,1]]
rows.append('Số người & '+' & '.join(str(len(g)) for g in groups)+r' & -- \\')
for col,label in variables:
 key='survival_time_years' if col=='followup_median' else col
 arrays=[first.loc[first.split==s,key].dropna().to_numpy() for s in splits]
 if col=='male':
  ct=np.array([[int((a==0).sum()),int((a==1).sum())] for a in arrays]); test=chi2_contingency(ct); assert (test.expected_freq>=5).all();p=float(test.pvalue)
 elif col=='followup_median':p=None
 elif np.ptp(np.concatenate(arrays))==0:p=1.
 else:p=float(kruskal(*arrays).pvalue)
 cells=[]
 for g in groups:
  x=g[key].dropna(); n=len(x)
  if col=='male':cell=f'{int(x.sum())} ({100*x.mean():.1f})'
  elif col=='followup_median':cell=f'{x.median():.2f} [{x.quantile(.25):.2f}; {x.quantile(.75):.2f}]'
  else:cell=f'${x.mean():.2f} \\pm {x.std(ddof=1):.2f}$'
  if n<len(g):cell+=f' ({n})'
  cells.append(cell)
  summary.append(dict(variable=col,split=g.split.iloc[0],event=int(g.event.iloc[0]),n=n,missing=len(g)-n,mean=float(x.mean()),sd=float(x.std(ddof=1)),median=float(x.median()),q1=float(x.quantile(.25)),q3=float(x.quantile(.75)),p=p))
 rows.append(label+' & '+' & '.join(cells)+' & '+('--' if p is None else ('$<0.001$' if p<.001 else f'{p:.3f}'))+r' \\')
tex=r'''\begin{landscape}
\begin{table}[p]
\centering\small
\caption[Đặc điểm người tham gia tại MRI đầu]{Đặc điểm người tham gia tại MRI đầu, chia theo tập và trạng thái kết cục.}
\label{tab:baseline-characteristics}
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
& \multicolumn{2}{c}{Huấn luyện ($N=251$)} & \multicolumn{2}{c}{Xác thực ($N=54$)} & \multicolumn{2}{c}{Kiểm tra ($N=54$)} & $p$ \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}
Đặc điểm & $\delta=0$ & $\delta=1$ & $\delta=0$ & $\delta=1$ & $\delta=0$ & $\delta=1$ & \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\par\vspace{6pt}
\begin{minipage}{0.96\linewidth}\small
$\delta=0$: kiểm duyệt; $\delta=1$: ghi nhận biến cố. Trừ các dòng ghi riêng, số liệu là trung bình $\pm$ SD mẫu. Số trong ngoặc thêm sau thống kê là số quan sát hợp lệ nếu có thiếu; tỷ lệ nam dùng mẫu số có thông tin giới tính. Tuổi ước tính từ tháng/năm sinh, quy ước ngày 15. Nhân khẩu học lấy bản ghi hợp lệ gần nhất không sau MRI đầu; điểm MMSE/CDR dùng bản ghi ghép theo cửa sổ $\pm90$ ngày của pipeline, trước điền thiếu. $p$ so sánh ba tập tổng thể bằng Kruskal--Wallis, riêng giới tính dùng chi-square; chỉ có mục đích mô tả. $s_3-s_1$ là khoảng tích lũy từ MRI đầu đến MRI cuối. $t_i$ là thời gian quan sát từ MRI cuối đến biến cố/kiểm duyệt.
\end{minipage}
\end{table}
\end{landscape}
'''
(S/'tables/baseline_characteristics.tex').write_text(tex)
pd.DataFrame(summary).to_csv(S/'evidence/baseline_characteristics.csv',index=False)
follow=[]
for s in splits:
 x=first[first.split==s].survival_time_years;follow.append(dict(split=s,mean=float(x.mean()),median=float(x.median()),q1=float(x.quantile(.25)),q3=float(x.quantile(.75)),max=float(x.max())))
(S/'evidence/baseline_followup.json').write_text(json.dumps(follow,indent=2))
(S/'evidence/baseline_provenance.json').write_text(json.dumps([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],indent=2))
print('Missing:',first[[k for k,l in variables if k!='followup_median']].isna().sum().to_dict());print('Follow-up:',follow);print('p-values:',{r['variable']:r['p'] for r in summary})

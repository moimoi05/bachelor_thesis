"""Rebuild aggregate survival tables and figures from bundled evidence."""

import argparse
import json

import numpy as np
import pandas as pd

from academic_style import S, plt, save
from matplotlib.lines import Line2D
from render_empirical import NAVY, SPLITS, grid_axis, plot_style

EVIDENCE = S / 'evidence'
T = S / 'tables'
RISK_YEARS = (0, 2, 3, 5)
RISK_STYLES = (
    ('Low risk', 'Nguy cơ thấp', '#17638E', '#DCE7F0', '-'),
    ('High risk', 'Nguy cơ cao', '#9E520A', '#F3E4D5', '--'),
)


def num(x,d=4):
    return f'{x:.{d}f}'


def mean_sd(a,b,d=4):
    return '$'+num(a,d)+r'\pm'+num(b,d)+'$'


def table(name,caption,label,headers,rows,spec):
    caption={
        'tab:standard-bench':'C-index xác thực, trung bình $\\pm$ SD qua ba lần khởi tạo; M là triệu tham số.',
        'tab:survival-metrics':'C-index và AUC, trung bình $\\pm$ SD qua ba lần khởi tạo; mỗi tập có 54 người (16 biến cố).',
        'tab:horizon-support':'Số người có biến cố / theo dõi quá mốc / kiểm duyệt trước hoặc tại mốc; $\\widehat G(h)$ ước lượng từ tập huấn luyện.',
        'tab:km-statistics':'Log-rank, HR cao/thấp và kiểm tra nguy cơ tỷ lệ (PH).'
    }[label]
    t=r'\begin{table}[H]'+'\n'+r'\centering\small'+'\n'+r'\caption['+{'tab:standard-bench':'So sánh C-index và độ phức tạp mô hình','tab:survival-metrics':'C-index và AUC của RC-Free','tab:horizon-support':'Số người theo trạng thái và xác suất chưa kiểm duyệt tại từng mốc','tab:km-statistics':'Log-rank và HR theo nhóm nguy cơ'}[label]+']{'+caption+'}\n'+r'\label{'+label+'}\n'
    t+=r'\begin{tabularx}{\linewidth}{'+spec+'}\n'+r'\toprule'+'\n'
    t+=' & '.join(r'\textbf{'+h+'}' for h in headers)+r' \\'+'\n'+r'\midrule'+'\n'
    t+='\n'.join(' & '.join(row)+r' \\' for row in rows)+'\n'+r'\bottomrule'+'\n'+r'\end{tabularx}'+'\n'+r'\end{table}'+'\n'
    (T/name).write_text(t, encoding='utf-8')


def build_tables(auc, km):
    T.mkdir(exist_ok=True)
    benchmark = json.loads((EVIDENCE / 'FINAL_STANDARDIZED_VALIDATION_BENCHMARK.json').read_text(encoding='utf-8'))
    final = json.loads((EVIDENCE / 'A6_FINAL_TRAIN_VAL_TEST_EVALUATION.json').read_text(encoding='utf-8'))
    names={'P10':'CNN--PCA--T-LSTM (thích nghi)','P05B':'Full Outer-Product (loạt chính)',
           'P05-CP':'Full CP Pairwise','A6':'RC-Free Pairwise'}
    rows=[]
    for r in benchmark['deep_models']:
        if r['model'] not in names:
            continue
        params=r['parameters_by_seed']
        par=num(params[0]/1e6,2) if len(set(params))==1 else num(min(params)/1e6,2)+r'\text{--}'+num(max(params)/1e6,2)
        pairs={'P10':'0 / 0','P05B':'3 / 6','P05-CP':'3 / 6','A6':'2 / 4'}[r['model']]
        rows.append([names[r['model']],mean_sd(r['mean'],r['sample_sd'],4),'$'+par+'$',pairs])
    table('benchmark.tex','C-index validation qua ba seed, mean $\\pm$ SD. Số tham số toàn mạng làm tròn theo triệu (M); cặp/nhánh đếm tương tác tường minh.',
          'tab:standard-bench',['Mô hình','C-index $\\uparrow$','Tham số (M)','Cặp/nhánh'],rows,'@{}Y r r c@{}')

    vals=[]
    for split in ['val','test']:
        r=final['summary']['cindex'][split]
        vals.append(mean_sd(r['mean'],r['sample_sd']))
    rows=[['C-index',*vals]]
    for h in [2,3,5]:
        vals=[]
        for split in ['val','test']:
            r=auc[auc.split.eq(split)&auc.horizon.eq(h)].iloc[0]
            assert r.status=='ok' and r.valid_seeds==3
            vals.append(mean_sd(r.auc_mean,r.auc_sd))
        rows.append([f'AUC {h} năm',*vals])
    table('survival_metrics.tex','RC-Free: mean $\\pm$ SD của ba seed. Mỗi tập có 54 người và 16 biến cố; test là đánh giá hậu nghiệm.',
          'tab:survival-metrics',['Chỉ số','Xác thực (chính)','Kiểm tra hậu nghiệm'],rows,'@{}Y r r@{}')
    rows=[]
    for h in [2,3,5]:
        rr=[auc[auc.split.eq(s)&auc.horizon.eq(h)].iloc[0] for s in ['val','test']]
        rows.append([str(h)]+[f'{int(r.cases)} / {int(r.controls)} / {int(r.censored_by_h)}' for r in rr]+['$'+num(rr[0].censoring_survival,3)+'$'])
    table('horizon_support.tex','Số cases / controls / kiểm duyệt trước hoặc tại mốc. $\\widehat G(h)$ là xác suất còn chưa bị kiểm duyệt ước lượng từ train, dùng chung giữa các seed.',
          'tab:horizon-support',['Năm','Xác thực','Kiểm tra hậu nghiệm',r'$\widehat G(h)$'],rows,'@{}c Y Y r@{}')
    rows=[]
    for _,r in km.iterrows():
        rows.append(['Xác thực' if r.split=='val' else 'Kiểm tra hậu nghiệm', '$'+num(r.logrank_p,6)+'$',
                     '$'+num(r.hr,2)+'$','$'+num(r.hr_ci_lower,2)+'$--$'+num(r.hr_ci_upper,2)+'$',
                     '$'+num(r.ph_p,3)+'$'])
    table('km_statistics.tex','Log-rank, HR cao/thấp và kiểm tra nguy cơ tỷ lệ (PH).',
          'tab:km-statistics',['Tập','Log-rank p','HR','CI 95\\%','p (PH)'],rows,'@{}Y r r r r@{}')


def build_auc_summary(auc):
    """Preserve the optional validation-only AUC chart outside the thesis."""
    with plot_style():
        f = auc.loc[auc.split.eq('val')].sort_values('horizon')
        fig, ax = plt.subplots(figsize=(6.3, 2.65))
        ax.errorbar(f.horizon, f.auc_mean, yerr=f.auc_sd, color=RISK_STYLES[0][2],
                    lw=1.8, marker='o', markersize=6, capsize=5, capthick=1.3)
        ax.axhline(.5, color='#A7B4BA', ls=(0, (3, 3)), lw=.9)
        ax.set(xlabel='Năm từ ngày MRI cuối', ylabel='AUC', xticks=[2, 3, 5],
               yticks=[.5, .6, .7, .8, .9, 1.], ylim=(.48, 1.035), xlim=(1.7, 5.3))
        grid_axis(ax)
        fig.tight_layout(pad=.7)
    return fig


def build_km(evidence=EVIDENCE):
    metrics = pd.read_csv(evidence / 'km_statistics.csv').set_index('split')
    curves = pd.read_csv(evidence / 'km_curves.csv').set_index(['split', 'group']).sort_index()
    risk = pd.read_csv(evidence / 'number_at_risk.csv').set_index(['split', 'group']).sort_index()
    counts = pd.read_csv(evidence / 'km_event_counts.csv').set_index(['split', 'group']).sort_index()
    with plot_style():
        fig = plt.figure(figsize=(6.30, 3.64))
        layout = fig.add_gridspec(2, 2, height_ratios=[3.1, 1.05],
                                 left=.13, right=.97, bottom=.13, top=.92,
                                 wspace=.34, hspace=.52)
        reference = None
        for col, (split, split_label) in enumerate(SPLITS):
            ax = fig.add_subplot(layout[0, col], sharey=reference)
            reference = ax
            risk_ax = fig.add_subplot(layout[1, col], sharex=ax)
            ax.set(xlabel='Năm từ ngày MRI cuối', xlim=(0, 5), ylim=(0, 1.04),
                   xticks=(0, 1, 2, 3, 4, 5), yticks=(0, .25, .50, .75, 1.0))
            ax.set_title(f'({chr(97 + col)}) {split_label}', loc='left',
                         fontsize=10, weight='bold', color=NAVY, pad=8)
            if col:
                ax.tick_params(labelleft=False)
            else:
                ax.set_ylabel('Xác suất chưa có biến cố')
            grid_axis(ax)
            prepare_risk_table(risk_ax)
            split_metrics = metrics.loc[split]
            assert (split_metrics.n, split_metrics.events) == (54, 16)
            for group_number, style in enumerate(RISK_STYLES):
                group = style[0]
                plot_km_group(ax, curves.loc[split, group], counts.loc[split, group],
                              split_metrics, group_number, style)
                plot_risk_row(risk_ax, risk.loc[split, group], split_metrics, group_number, style)

        fig.legend(handles=km_legend(), loc='lower center', bbox_to_anchor=(.54, .009),
                   frameon=False, ncol=3, handlelength=2.5, columnspacing=1.5)
    return fig


def prepare_risk_table(ax):
    ax.set_ylim(0, 3.2)
    ax.set_axis_off()
    ax.text(0, 3.04, 'Số người còn nguy cơ', va='center', fontsize=9, weight='bold', color=NAVY)
    for year in RISK_YEARS:
        ax.text(year, 2.17, str(year), fontsize=8.5, ha='center', va='center')
    ax.axhline(1.84, color='#B7C0CA', lw=.6)


def plot_km_group(ax, curve, counts, metrics, group_number, style):
    _, label, color, fill, line_style = style
    assert counts['count'].sum() == metrics[f'n_{group_number}']
    assert counts.events.sum() == metrics[f'events_{group_number}']
    observed = curve.loc[curve.time.le(5)].sort_values('time')
    survival = observed.survival.to_numpy()
    assert (observed.time.iloc[0], survival[0]) == (0, 1)
    assert np.all(np.diff(survival) <= 1e-10)
    assert observed.ci_lower.le(observed.survival).all()
    assert observed.ci_upper.ge(observed.survival).all()
    censored = counts.loc[counts.censored.gt(0) & counts.time.le(5), 'time']
    marker_y = observed.set_index('time').survival.reindex(censored).to_numpy()
    assert np.isfinite(marker_y).all()
    if observed.time.iloc[-1] < 5:
        # Show the observed final step through the right edge of the display window.
        observed = pd.concat([observed, observed.iloc[[-1]].assign(time=5.)], ignore_index=True)
    ax.fill_between(observed.time, observed.ci_lower, observed.ci_upper, step='post',
                    facecolor=fill, alpha=.8, linewidth=0)
    ax.step(observed.time, observed.survival, where='post', color=color,
            linestyle=line_style, linewidth=1.45, label=label)
    ax.plot(censored, marker_y, linestyle='none', marker='|', color=color,
            markersize=5.7, markeredgewidth=.85, zorder=4)


def plot_risk_row(ax, row, metrics, group_number, style):
    _, _, color, _, _ = style
    row = row.sort_values('year')
    assert tuple(row.year) == RISK_YEARS
    assert row.at_risk.iloc[0] == metrics[f'n_{group_number}']
    y = (1.25, .45)[group_number]
    ax.annotate(('Thấp', 'Cao')[group_number], (0, y), xytext=(-10, 0),
                textcoords='offset points', ha='right', va='center',
                fontsize=8.5, color=color, annotation_clip=False)
    for year, count in zip(row.year, row.at_risk, strict=True):
        ax.text(year, y, str(count), ha='center', va='center', fontsize=8.5)


def km_legend():
    items = [Line2D([0], [0], label=label, color=color, ls=line_style, lw=1.45)
             for _, label, color, _, line_style in RISK_STYLES]
    items.append(Line2D([0], [0], label='Kiểm duyệt', color=NAVY,
                        linestyle='none', marker='|', markersize=5.7))
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--km-only', action='store_true',
                        help='render the Kaplan–Meier figure while leaving tables and other figures intact')
    args = parser.parse_args()
    if not args.km_only:
        auc = pd.read_csv(EVIDENCE / 'auc_summary.csv')
        km = pd.read_csv(EVIDENCE / 'km_statistics.csv')
        build_tables(auc, km)
        save(build_auc_summary(auc), 'survival-auc')
    save(build_km(), 'survival-km')
    print('Rendered two-panel Kaplan–Meier figure from verified evidence.')


if __name__ == '__main__':
    main()

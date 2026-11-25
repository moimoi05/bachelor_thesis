"""Render Chapter 4 training and ROC plots from the frozen aggregate evidence."""

import json

import numpy as np
import pandas as pd

from academic_style import S, plt
import matplotlib as mpl


EVIDENCE = S / 'evidence'
TEXT = '#28313C'
NAVY = '#172C46'
GRID = '#E9ECEF'
SEED_STYLE = {
    20260727: ('#17638E', '-', 'o'),
    20260728: ('#9E520A', '--', 's'),
    20260729: ('#23715B', (0, (3, 1, 1, 1)), '^'),
}
HORIZONS = (2, 3, 5)
SPLITS = (('val', 'Xác thực'), ('test', 'Kiểm tra (hậu nghiệm)'))


def plot_style():
    return plt.rc_context({
        'font.family': ['Arial', 'DejaVu Sans'],
        'font.size': 9, 'text.color': TEXT,
        'axes.labelcolor': TEXT, 'axes.edgecolor': NAVY, 'axes.linewidth': 0.7,
        'axes.spines.top': False, 'axes.spines.right': False,
        'xtick.color': TEXT, 'ytick.color': TEXT,
        'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5,
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'xtick.major.size': 3, 'ytick.major.size': 3,
        'xtick.major.width': 0.65, 'ytick.major.width': 0.65,
        'legend.fontsize': 8.5, 'mathtext.fontset': 'dejavusans',
        'pdf.fonttype': 42, 'svg.fonttype': 'none',
    })


def grid_axis(ax):
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=GRID, linewidth=0.65)


def validate_roc_panel(curves, verified, summary):
    """Check each ordered threshold series against the recorded IPCW AUC."""
    assert summary.status == 'ok' and summary.valid_seeds == len(SEED_STYLE)
    assert len(verified) == len(SEED_STYLE) and verified.status.eq('ok').all()
    assert set(curves.seed) == set(verified.index) == set(SEED_STYLE)
    assert verified.cases.eq(summary.cases).all()
    assert verified.controls.eq(summary.controls).all()
    aucs = []
    for seed in SEED_STYLE:
        coordinates = curves.loc[curves.seed.eq(seed), ['fpr', 'tpr']].to_numpy()
        assert np.isfinite(coordinates).all() and np.all(np.diff(coordinates, axis=0) >= 0)
        np.testing.assert_allclose(coordinates[[0, -1]], [[0, 0], [1, 1]], atol=1e-12, rtol=0)
        fpr, tpr = coordinates.T
        auc = np.trapezoid(tpr, fpr)
        np.testing.assert_allclose(auc, verified.loc[seed, 'auc'], atol=1e-12, rtol=0)
        aucs.append(auc)
    np.testing.assert_allclose(
        [np.mean(aucs), np.std(aucs, ddof=1)],
        [summary.auc_mean, summary.auc_sd], atol=1e-12, rtol=0,
    )


def original_style():
    return plt.rc_context({
        **mpl.rcParamsDefault,
        'font.family': 'DejaVu Sans', 'font.size': 11, 'pdf.fonttype': 42,
        'svg.fonttype': 'none', 'axes.spines.top': False,
    })


def build_roc(evidence=EVIDENCE):
    curves = pd.read_csv(evidence / 'roc_coordinates.csv')
    verified = pd.read_csv(evidence / 'roc_auc_verified.csv').set_index(['split', 'horizon', 'seed']).sort_index()
    summary = pd.read_csv(evidence / 'auc_summary.csv').set_index(['split', 'horizon'])
    grid = np.linspace(0, 1, 1001)
    with original_style():
        fig, axes = plt.subplots(2, 3, figsize=(9, 7.3), layout='constrained')
        for row, (split, title) in enumerate(SPLITS):
            color = ('#1676ad', '#d17a22')[row]
            for col, horizon in enumerate(HORIZONS):
                ax = axes[row, col]
                panel = curves.loc[curves.split.eq(split) & curves.horizon.eq(horizon)]
                stat = summary.loc[split, horizon]
                validate_roc_panel(panel, verified.loc[split, horizon], stat)
                interpolated = []
                for _, curve in panel.groupby('seed', sort=True):
                    ax.step(curve.fpr, curve.tpr, where='post', color=color, alpha=.35,
                            lw=.85, marker='o', ms=2.7)
                    interpolated.append(np.interp(grid, curve.fpr, curve.tpr))
                mean = np.mean(interpolated, axis=0)
                sd = np.std(interpolated, axis=0, ddof=1)
                ax.plot(grid, mean, color=color, lw=1.8, label='ROC trung bình nội suy')
                ax.fill_between(grid, np.maximum(0, mean-sd), np.minimum(1, mean+sd),
                                color=color, alpha=.13)
                ax.plot([0, 1], [0, 1], '--', color='.6', lw=.8)
                ax.text(.98, .06, f'AUC = {stat.auc_mean:.4f} ± {stat.auc_sd:.4f}\n'
                        f'{stat.cases} biến cố / {stat.controls} đối chứng',
                        ha='right', transform=ax.transAxes, fontsize=9)
                ax.set(title=f'({chr(97+row*3+col)}) {title}\nMốc {horizon} năm',
                       xlabel='1 − Độ đặc hiệu', ylabel='Độ nhạy', xlim=(0, 1), ylim=(0, 1.02))
                ax.grid(alpha=.15)
    return fig


def validate_training(history, summary):
    assert history.epoch.tolist() == list(range(1, summary['stop_epoch'] + 1))
    chosen = history.loc[history.epoch.eq(summary['best_epoch']), 'val_cindex'].item()
    np.testing.assert_allclose(chosen, summary['best_cindex'], rtol=0, atol=1e-12)
    fields = ['train_loss', 'val_cox_loss_full']
    np.testing.assert_allclose(
        history.loc[:, fields].iloc[[0, -1]].to_numpy(),
        [[summary['first_train'], summary['first_val']],
         [summary['last_train'], summary['last_val']]], rtol=0, atol=1e-12,
    )


def build_training(evidence=EVIDENCE):
    history = pd.read_csv(evidence / 'training_history.csv')
    summaries = json.loads((evidence / 'training_summary.json').read_text(encoding='utf-8'))
    assert set(history.seed) == {row['seed'] for row in summaries} == set(SEED_STYLE)
    with original_style():
        fig, (loss, ranking) = plt.subplots(1, 2, figsize=(9, 4.8), layout='constrained')
        valid_loss = loss.twinx()
        for summary, color in zip(summaries, ('#1676ad', '#d17a22', '#38945a'), strict=True):
            seed = summary['seed']
            trajectory = history.loc[history.seed.eq(seed)]
            validate_training(trajectory, summary)
            loss.plot(trajectory.epoch, trajectory.train_loss, color=color, lw=1, label=str(seed))
            valid_loss.plot(trajectory.epoch, trajectory.val_cox_loss_full, color=color, lw=1, ls='--')
            ranking.plot(trajectory.epoch, trajectory.val_cindex, color=color, lw=1)
            ranking.scatter(summary['best_epoch'], summary['best_cindex'], marker='*', s=100,
                            color=color, zorder=5)
            ranking.scatter(summary['stop_epoch'], trajectory.val_cindex.iloc[-1], marker='s',
                            s=22, color=color)
        loss.set(title='(a) Hàm mất mát Cox', xlabel='Vòng huấn luyện',
                 ylabel='Mất mát huấn luyện trung bình theo lô')
        valid_loss.set_ylabel('Mất mát trên toàn tập xác thực (nét đứt)')
        ranking.set(title='(b) C-index xác thực', xlabel='Vòng huấn luyện', ylabel='C-index', ylim=(.4, 1))
        for ax in (loss, ranking):
            ax.grid(alpha=.15)
        fig.legend(*loss.get_legend_handles_labels(), loc='outside lower center',
                   ncols=3, frameon=False, fontsize=11)
    return fig


if __name__ == '__main__':
    for name, build in [('empirical-training', build_training), ('empirical-ipcw-roc', build_roc)]:
        fig = build()
        with original_style():
            for ext in ('pdf', 'png', 'svg'):
                fig.savefig(S / 'image' / f'{name}.{ext}', dpi=300, bbox_inches='tight')
        plt.close(fig)

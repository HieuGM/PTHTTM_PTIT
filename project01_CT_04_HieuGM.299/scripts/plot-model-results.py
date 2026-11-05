"""Publication-ready figures from recorded held-out scores; never invent metrics."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, precision_recall_curve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/figures'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for dataset, title in [('cdc', 'CDC BRFSS: survey label'),
                           ('hospital', 'Hospital: readmission <30 days')]:
        record = json.loads((ROOT / f'results/{dataset}-training.json').read_text(encoding='utf-8'))
        scores = np.load(ROOT / f'results/{dataset}-test-predictions.npz')
        y = scores['y_true']
        fig, axes = plt.subplots(2, 2, figsize=(10, 7.4))
        fig.suptitle(title + ' | held-out test', fontsize=14, fontweight='bold')
        for name, key, color in [('MLP', 'mlp', '#136f9c'), ('Logistic', 'logistic', '#bf6f27')]:
            score = scores[f'{key}_score']
            m = record['test'][key]
            fpr, tpr, _ = roc_curve(y, score)
            precision, recall, _ = precision_recall_curve(y, score)
            axes[0, 0].plot(fpr, tpr, color=color, label=f"{name} AUC={m['roc_auc']:.3f}")
            axes[0, 1].plot(recall, precision, color=color,
                            label=f"{name} AP={m['average_precision']:.3f}")
            frac, mean = calibration_curve(y, score, n_bins=10, strategy='quantile')
            axes[1, 0].plot(mean, frac, 'o-', color=color,
                            label=f"{name} Brier={m['brier']:.3f}")
            rows.append(dict(dataset=dataset, model=key, **{k: v for k, v in m.items()
                        if k not in {'confusion_matrix', 'confusion_order'}}))
        axes[0, 0].plot([0, 1], [0, 1], '--', color='gray', lw=1)
        axes[0, 1].axhline(y.mean(), ls='--', color='gray', label=f'Prevalence={y.mean():.3f}')
        axes[1, 0].plot([0, 1], [0, 1], '--', color='gray', lw=1)
        history = record['history']
        axes[1, 1].plot([h['epoch'] for h in history], [h['val_roc_auc'] for h in history],
                        color='#136f9c', label='Validation ROC-AUC')
        axes[1, 1].axvline(record['best_epoch'], ls='--', color='gray', label='Selected epoch')
        labels = [('False-positive rate', 'Sensitivity', 'ROC'),
                  ('Recall', 'Precision', 'Precision–Recall'),
                  ('Mean sigmoid score (quantile bins)', 'Observed fraction', 'Calibration diagnostic'),
                  ('Epoch', 'Validation ROC-AUC', 'Checkpoint selection')]
        for ax, (xlab, ylab, subtitle) in zip(axes.flat, labels):
            ax.set(xlabel=xlab, ylabel=ylab, title=subtitle)
            ax.legend(fontsize=8, loc='best')
            ax.grid(alpha=0.18)
        fig.tight_layout(rect=(0, 0, 1, 0.96))
        fig.savefig(OUT / f'{dataset}-evaluation.png', dpi=180, bbox_inches='tight')
        plt.close(fig)
    with (ROOT / 'results/model-comparison.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    manifest = json.loads((ROOT / 'results/data-manifest.json').read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, (dataset, info) in zip(axes, manifest.items()):
        items = info['split']
        neg = [s['n']-s['positive'] for s in items.values()]
        pos = [s['positive'] for s in items.values()]
        ax.bar(list(items), neg, color='#b9d9e8', label='Label 0')
        ax.bar(list(items), pos, bottom=neg, color='#136f9c', label='Label 1')
        ax.set(title=dataset.upper()+' | disjoint splits', ylabel='Rows')
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / 'dataset-splits.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    print('Saved 3 figures and model-comparison.csv')


if __name__ == '__main__':
    main()

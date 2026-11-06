"""Benchmark figures built solely from recorded held-out predictions and run summaries."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve
from .training import MODEL_IDS

SHORT_NAMES = ['Logistic', 'RF', 'HistGB', 'MLP2', 'MLP3', 'ResMLP']
COLORS = ['#607d8b', '#d18b26', '#7b5aa6', '#238c9c', '#225bb1', '#c84e57']


def plot_benchmark(root, mode='full'):
    root = Path(root)
    output = root / 'results/benchmark' / mode
    figures = output / 'figures'
    figures.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(output / 'summary.csv')
    record = json.loads((output / 'benchmark-results.json').read_text(encoding='utf-8'))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False})
    files = []
    for dataset in summary.dataset.unique():
        rows = summary.loc[summary.dataset == dataset].set_index('model_id').loc[MODEL_IDS]
        fig, axes = plt.subplots(2, 2, figsize=(9, 7))
        fig.suptitle(dataset.upper() + ' | fixed split, three model seeds | ' + mode,
                     fontweight='bold', fontsize=12)
        for axis, metric, title in [(axes[0, 0], 'roc_auc', 'ROC-AUC mean +/- sample SD'),
                                    (axes[0, 1], 'average_precision', 'Average precision mean +/- sample SD')]:
            axis.bar(SHORT_NAMES, rows[metric + '_mean'], yerr=rows[metric + '_std'],
                     color=COLORS, capsize=3)
            axis.set(title=title, ylim=(0, 1.05), ylabel=metric)
            axis.tick_params(axis='x', rotation=30)
            axis.grid(axis='y', alpha=.15)
        # Plot a predeclared seed (42), not the seed/model chosen by test performance.
        first_seed = record['environment']['model_seeds'][0]
        for model_id, name, color in zip(MODEL_IDS, SHORT_NAMES, COLORS):
            scores = np.load(output / dataset / f'{model_id}-seed{first_seed}-predictions.npz')
            y, score = scores['y_test'], scores['test_score']
            fpr, tpr, _ = roc_curve(y, score)
            precision, recall, _ = precision_recall_curve(y, score)
            axes[1, 0].plot(fpr, tpr, color=color, label=name, lw=1.4)
            axes[1, 1].plot(recall, precision, color=color, label=name, lw=1.4)
        axes[1, 0].plot([0, 1], [0, 1], '--', color='gray', lw=.7)
        axes[1, 0].set(title=f'ROC | seed {first_seed}', xlabel='False-positive rate', ylabel='Sensitivity')
        axes[1, 1].axhline(y.mean(), color='gray', ls='--', lw=.7, label='Prevalence')
        axes[1, 1].set(title=f'Precision-recall | seed {first_seed}', xlabel='Recall', ylabel='Precision')
        for axis in axes[1]:
            axis.legend(fontsize=7, loc='best')
            axis.grid(alpha=.15)
        fig.tight_layout(rect=(0, 0, 1, .96))
        path = figures / (dataset + '-benchmark.png')
        fig.savefig(path, dpi=170, bbox_inches='tight')
        plt.close(fig)
        files.append(path)
    return files

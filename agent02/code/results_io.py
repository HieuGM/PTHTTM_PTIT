"""Deterministic result serialization and figures from measured training data."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def training_stats(rows):
    a = np.array([r['rl_mean_reward_per_step'] for r in rows])
    b = np.array([r['rule_mean_reward_per_step'] for r in rows])
    return {'rl_total_reward': sum(r['rl_episode_reward'] for r in rows),
            'rule_total_reward': sum(r['rule_episode_reward'] for r in rows),
            'rl_mean_reward': float(a.mean()), 'rule_mean_reward': float(b.mean()),
            'rl_first100': float(a[:100].mean()), 'rl_last100': float(a[-100:].mean()),
            'rl_last1000_std': float(a[-1000:].std(ddof=1)),
            'rule_first100': float(b[:100].mean()), 'rule_last100': float(b[-100:].mean()),
            'rl_action_counts': [sum(r['rl_no_discount'] for r in rows), sum(r['rl_discount'] for r in rows)],
            'rule_action_counts': [sum(r['rule_no_discount'] for r in rows), sum(r['rule_discount'] for r in rows)]}


def aggregate(runs):
    rows = []
    for name in sorted(set(r['name'] for r in runs)):
        selected = [r for r in runs if r['name'] == name and r['train_seed'] != 42]
        for strategy in ['rl', 'rule']:
            values = [r[strategy+'_evaluation']['mean_rewards'][0] for r in selected]
            rates = [r[strategy+'_evaluation']['discount_rates'][0] for r in selected]
            rows.append({'configuration': name, 'strategy': strategy, 'n': len(values),
                         'mean_reward': float(np.mean(values)), 'sample_sd': float(np.std(values, ddof=1)),
                         'mean_discount_rate': float(np.mean(rates))})
    return rows


def plot_curves(out, runs):
    groups = {'baseline': ['baseline'], 'learning-rate': ['alpha-0.01', 'baseline', 'alpha-0.50'],
              'exploration': ['baseline', 'epsilon-0.05', 'epsilon-0.30'],
              'robustness': ['baseline', 'discount-0.05']}
    for filename, names in groups.items():
        fig, ax = plt.subplots(figsize=(9, 4.6))
        for name in names:
            chosen = [r for r in runs if r['name'] == name and r['train_seed'] != 42]
            data = []
            for r in chosen:
                a = np.array([x['rl_mean_reward_per_step'] for x in r['training_rows']])
                data.append(a.reshape(-1, 100).mean(axis=1))
            a = np.array(data)
            x = np.arange(100, a.shape[1]*100+1, 100)
            y, sd = a.mean(axis=0), a.std(axis=0, ddof=1)
            ax.plot(x, y, label=name)
            ax.fill_between(x, y-sd, y+sd, alpha=.13)
        ax.set(xlabel='Training episode (non-overlapping windows of 100)',
               ylabel='Mean profit per step', title='Five training seeds; shading = sample SD')
        ax.legend(); ax.grid(alpha=.25); fig.tight_layout()
        fig.savefig(out/(filename+'.png'), dpi=170); plt.close(fig)
    baseline = next(r for r in runs if r['name']=='baseline' and r['train_seed']==42)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for key, label in [('rl_episode_reward','RL'),('rule_episode_reward','Rule opponent')]:
        ax.plot(np.cumsum([r[key] for r in baseline['training_rows']]), label=label)
    ax.set(xlabel='Training episode', ylabel='Cumulative profit', title='Baseline seed 42 cumulative training reward')
    ax.legend(); ax.grid(alpha=.25); fig.tight_layout()
    fig.savefig(out/'baseline-cumulative.png', dpi=170); plt.close(fig)

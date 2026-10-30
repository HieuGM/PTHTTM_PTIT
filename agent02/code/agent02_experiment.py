"""Full assignment benchmark. Run from any directory with Python + NumPy/Matplotlib."""
from dataclasses import asdict, replace
from pathlib import Path
import platform
import sys
import time
import numpy as np
from reference_core import Config, RuleBasedAgent, train_rl_against_rule
from evaluation import evaluate
from results_io import write_json, write_csv, training_stats, aggregate, plot_curves

OUT = Path(__file__).resolve().parents[1]/'results'
SEEDS = [11, 22, 33, 44, 55]
SETTINGS = {'baseline': {}, 'alpha-0.01': {'alpha': .01}, 'alpha-0.50': {'alpha': .50},
            'epsilon-0.05': {'epsilon_start': .05, 'epsilon_min': .05, 'epsilon_decay': 1.},
            'epsilon-0.30': {'epsilon_start': .30, 'epsilon_min': .30, 'epsilon_decay': 1.},
            'discount-0.05': {'discount_rate': .05}}


def one_run(name, seed):
    config = replace(Config(), **SETTINGS[name])
    agent, training = train_rl_against_rule(config, seed)
    eval_seed = seed+500_000
    rl = evaluate(config, agent, eval_seed)
    rule = evaluate(config, RuleBasedAgent(), eval_seed)
    data = {'name': name, 'train_seed': seed, 'agent_seed': seed+10_000,
            'config': asdict(config), 'q_table': agent.q.tolist(),
            'policy': {str(k): v for k,v in agent.greedy_policy().items()},
            'training_stats': training_stats(training), 'training_rows': training,
            'rl_evaluation': rl, 'rule_evaluation': rule}
    if name == 'baseline':
        shifted = replace(config, discount_rate=.05)
        data['transfer_evaluation'] = evaluate(shifted, agent, eval_seed)
        data['transfer_rule_evaluation'] = evaluate(shifted, RuleBasedAgent(), eval_seed)
    write_json(OUT/f'{name}-seed-{seed}.json', data)
    write_csv(OUT/f'{name}-seed-{seed}-training.csv', training)
    write_csv(OUT/f'{name}-seed-{seed}-evaluation.csv', rl['episodes'])
    print(f'{name} seed={seed} train={data["training_stats"]["rl_mean_reward"]:.4f} '
          f'eval={rl["mean_rewards"][0]:.4f} rule_separate={rule["mean_rewards"][0]:.4f} '
          f'policy={data["policy"]}', flush=True)
    return data


def main():
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    runs = []
    for name, seeds in [('baseline', [42]+SEEDS)]+[(n,SEEDS) for n in SETTINGS if n!='baseline']:
        for seed in seeds:
            runs.append(one_run(name, seed))
    rows = aggregate(runs)
    write_csv(OUT/'comparison-summary.csv', rows)
    transfers = []
    for r in runs:
        if r['name']=='baseline' and r['train_seed']!=42:
            transfers.append({'seed': r['train_seed'], 'transfer_reward':r['transfer_evaluation']['mean_rewards'][0],
                              'rule_reward':r['transfer_rule_evaluation']['mean_rewards'][0],
                              'transfer_discount_rate':r['transfer_evaluation']['discount_rates'][0]})
    write_csv(OUT/'robustness-transfer.csv', transfers)
    summary = {'environment': {'python':sys.version, 'numpy': np.__version__, 'platform':platform.platform()},
               'training_seeds':SEEDS, 'baseline_seed':42, 'aggregate':rows,
               'robustness_transfer':transfers, 'elapsed_seconds':time.time()-started,
               'protocol': 'Reference training RNG and random ties. Evaluation: separate focal-policy-vs-rule matches, common demand and per-customer uniform tapes, greedy deterministic ties, frozen Q, seed=train_seed+500000.'}
    write_json(OUT/'summary.json', summary)
    plot_curves(OUT, runs)
    print('Completed', summary['elapsed_seconds'], 'seconds', flush=True)


if __name__ == '__main__':
    main()

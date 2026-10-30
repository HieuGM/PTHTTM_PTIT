"""Independent numerical checks; run directly with Python (no pytest required)."""
from dataclasses import replace
from pathlib import Path
import json
import sys
import types
import numpy as np
from reference_core import Config, ECommerceEnvironment, QLearningAgent, RuleBasedAgent
from reference_core import train_rl_against_rule
from evaluation import evaluate, make_tape

ROOT = Path(__file__).resolve().parents[1]
checks = []


def check(name, test):
    test()
    checks.append(name)
    print('PASS', name)


def q_update():
    a = QLearningAgent(alpha=.1, gamma=.9)
    a.q[0, 0, 0] = 4
    a.q[1, 0] = [5, 2]
    a.learn((0, 0), 0, 6, (1, 0))
    assert np.isclose(a.q[0, 0, 0], 4.65)
    a.q[0, 0, 0] = 4
    a.learn((0, 0), 0, 6, (1, 0), terminal=True)
    assert np.isclose(a.q[0, 0, 0], 4.2)


def rule_and_transitions():
    rule = RuleBasedAgent()
    assert [rule.act(s) for s in [(0, 0), (0, 1), (1, 0), (1, 1)]] == [0, 0, 0, 1]
    env = ECommerceEnvironment(Config(), seed=123)
    assert env.reset()[0][1] == env.reset()[1][1] == 0
    env.demand = 1
    states, rewards, info = env.step([1, 0])
    assert states[0][1] == 0 and states[1][1] == 1
    assert np.allclose(info['conversion'], [.7, .45])
    assert info['customers'] == 20
    assert rewards == [info['sales'][0] * 3, info['sales'][1] * 5]
    for invalid in [[], [0], [0, 1, 0], [2, 0], [0, -1]]:
        try:
            env.step(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f'accepted invalid actions {invalid}')


def binomial_profit():
    env = ECommerceEnvironment(Config(), seed=712)
    sales = []
    for _ in range(10000):
        env.demand = 0
        _, rewards, info = env.step([1, 0])
        assert 0 <= info['sales'][0] <= 10
        assert rewards[0] == info['sales'][0] * 3
        sales.append(info['sales'][0])
    # Binomial(10,.45), mean 4.5 and variance 2.475; generous fixed-seed bounds.
    assert abs(np.mean(sales) - 4.5) < .08
    assert abs(np.var(sales, ddof=1) - 2.475) < .15


def evaluation_oracle():
    cfg = replace(Config(), evaluation_episodes=25, steps_per_episode=7)
    demand, uniforms = make_tape(cfg, 271)
    d2, u2 = make_tape(cfg, 271)
    assert np.array_equal(demand, d2) and np.array_equal(uniforms, u2)
    a = QLearningAgent(epsilon=1)
    a.q[:, :, 0] = 100  # Greedy policy must ignore epsilon=1 during evaluation.
    before = a.q.copy()
    rl = evaluate(cfg, a, 271)
    rule = evaluate(cfg, RuleBasedAgent(), 271)
    assert rl == evaluate(cfg, a, 271)
    assert rl['total_rewards'] == rule['total_rewards']
    assert np.array_equal(before, a.q)
    # Independent constant-policy oracle: rule-vs-rule never initiates discounts.
    expected = [0., 0.]
    for episode in range(25):
        for t in range(7):
            d = int(demand[episode, t])
            n, probability = (20, .55) if d else (10, .30)
            for i in range(2):
                expected[i] += sum(float(x) < probability for x in uniforms[episode, t, i, :n]) * 5
    assert rl['total_rewards'] == expected
    assert rl['action_counts'] == [[175, 0], [175, 0]]
    assert rl['mean_rewards'] == [v / 175 for v in expected]
    assert [sum(r[k] for r in rl['episodes']) for k in ['focal_reward', 'opponent_reward']] == expected
    a.q[:, :, 1] = 200  # A second independent oracle exercises actual discounting.
    discounted = evaluate(cfg, a, 271)
    expected = [0., 0.]
    opponent_discounts = 0
    for episode in range(25):
        for t in range(7):
            d = int(demand[episode, t])
            n = 20 if d else 10
            opponent_action = d if t > 0 else 0
            opponent_discounts += opponent_action
            probabilities = [.45 + .25*d - .10*opponent_action,
                             .20 + .25*d + .15*opponent_action]
            for i, margin in enumerate([3, 3 if opponent_action else 5]):
                expected[i] += sum(float(x) < probabilities[i]
                                   for x in uniforms[episode, t, i, :n]) * margin
    assert discounted['total_rewards'] == expected
    assert discounted['action_counts'] == [[0, 175], [175-opponent_discounts, opponent_discounts]]


def reference_parity():
    source = ROOT.parent / 'ASIGNMENT-AGENT_02/agent02_code.tex'
    if not source.exists():
        source = ROOT / 'reference/agent02_code.tex'
    assert source.exists(), 'Original reference source required for parity validation'
    ref = types.ModuleType('agent02_reference_for_test')
    sys.modules[ref.__name__] = ref
    exec(compile(source.read_text(encoding='utf-8'), str(source), 'exec'), ref.__dict__)
    cfg = replace(Config(), episodes=100)
    ours, rows = train_rl_against_rule(cfg, 42)
    theirs, original_rows = ref.train_rl_against_rule(cfg, 42)
    assert np.array_equal(ours.q, theirs.q)
    for observed, original in zip(rows, original_rows):
        assert all(observed[k] == v for k, v in original.items())
        assert observed['rl_discount'] + observed['rl_no_discount'] == 20
        assert observed['rule_discount'] + observed['rule_no_discount'] == 20


def persisted_results():
    files = list((ROOT / 'results').glob('*-seed-*.json'))
    for file in files:
        r = json.loads(file.read_text(encoding='utf-8'))
        assert len(r['training_rows']) == 5000
        assert np.asarray(r['q_table']).shape == (2, 2, 2)
        for prefix in ['rl', 'rule']:
            reward = sum(x[prefix + '_episode_reward'] for x in r['training_rows'])
            assert r['training_stats'][prefix + '_total_reward'] == reward
            assert np.isclose(r['training_stats'][prefix + '_mean_reward'], reward / 100000)
            assert sum(r['training_stats'][prefix + '_action_counts']) == 100000
        keys = ['rl_evaluation', 'rule_evaluation']
        if 'transfer_evaluation' in r:
            keys += ['transfer_evaluation', 'transfer_rule_evaluation']
        for key in keys:
            ev = r[key]
            assert ev['steps'] == 10000 and len(ev['episodes']) == 500
            assert all(sum(c) == 10000 for c in ev['action_counts'])
            totals = [sum(x[k] for x in ev['episodes']) for k in ['focal_reward', 'opponent_reward']]
            assert ev['total_rewards'] == totals
            assert np.allclose(ev['mean_rewards'], np.array(totals) / 10000)
        assert r['rl_evaluation']['q_unchanged'] is True
    summary = ROOT / 'results/summary.json'
    if summary.exists():
        s = json.loads(summary.read_text(encoding='utf-8'))
        assert len(files) == 31
        for row in s['aggregate']:
            selected = [json.loads(f.read_text(encoding='utf-8')) for f in files
                        if f.name.startswith(row['configuration'] + '-seed-') and not f.name.endswith('-42.json')]
            values = [r[row['strategy'] + '_evaluation']['mean_rewards'][0] for r in selected]
            assert row['n'] == len(values) == 5
            assert np.isclose(row['mean_reward'], np.mean(values))
            assert np.isclose(row['sample_sd'], np.std(values, ddof=1))
    print('Validated persisted result files:', len(files), 'summary complete:', summary.exists())


if __name__ == '__main__':
    for name, test in [('Q and terminal target', q_update), ('Rule and simultaneous transitions', rule_and_transitions),
                       ('Binomial sales and profit', binomial_profit), ('Frozen paired evaluation oracle', evaluation_oracle),
                       ('Exact reference training parity', reference_parity), ('Persisted result integrity', persisted_results)]:
        check(name, test)
    out = ROOT / 'results/test-results.json'
    out.write_text(json.dumps({'passed': len(checks), 'checks': checks}, indent=2), encoding='utf-8')
    print(len(checks), 'check groups passed')

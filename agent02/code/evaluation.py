"""Held-out evaluation with common demand and per-customer sales uniforms."""
import numpy as np
from reference_core import RuleBasedAgent


def make_tape(config, seed):
    shape = (config.evaluation_episodes, config.steps_per_episode)
    demand = np.random.default_rng(seed).integers(0, 2, size=shape)
    sales = np.random.default_rng(seed + 1_000_000).random(
        (*shape, 2, max(config.low_demand_customers, config.high_demand_customers)))
    return demand, sales


def evaluate(config, focal, seed):
    """Focal agent versus rule; caller repeats with same seed for rule versus rule.

    Evaluation resolves Q ties with argmax (lowest index), unlike random training
    tie-breaking. Per-customer Bernoulli sums have the specified binomial law.
    """
    demands, uniforms = make_tape(config, seed)
    q_before = focal.q.copy() if hasattr(focal, 'q') else None
    opponent = RuleBasedAgent()
    totals = np.zeros(2)
    counts = np.zeros((2, 2), dtype=int)
    episodes = []
    for episode in range(config.evaluation_episodes):
        previous = [0, 0]
        reward_sum = np.zeros(2)
        for step in range(config.steps_per_episode):
            d = int(demands[episode, step])
            states = [(d, previous[1]), (d, previous[0])]
            a0 = int(np.argmax(focal.q[states[0]])) if q_before is not None else focal.act(states[0])
            actions = [a0, opponent.act(states[1])]
            n = config.high_demand_customers if d else config.low_demand_customers
            for i in range(2):
                p = float(np.clip(.30 + .25*d + .15*actions[i] - .10*actions[1-i], .05, .95))
                sales = int(np.sum(uniforms[episode, step, i, :n] < p))
                margin = config.price*(1-config.discount_rate*actions[i])-config.unit_cost
                reward_sum[i] += sales*margin
                counts[i, actions[i]] += 1
            previous = actions
        totals += reward_sum
        episodes.append({'episode': episode+1, 'focal_reward': float(reward_sum[0]),
                         'opponent_reward': float(reward_sum[1])})
    if q_before is not None:
        assert np.array_equal(q_before, focal.q), 'Evaluation modified Q'
    steps = config.evaluation_episodes*config.steps_per_episode
    return {'seed': seed, 'steps': steps, 'total_rewards': totals.tolist(),
            'mean_rewards': (totals/steps).tolist(), 'action_counts': counts.tolist(),
            'discount_rates': (counts[:, 1]/steps).tolist(), 'episodes': episodes,
            'q_unchanged': True if q_before is not None else None}

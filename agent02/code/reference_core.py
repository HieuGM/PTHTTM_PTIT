"""Provided agent02_code.tex logic, compacted with Python AST unparse.

Training RNG, tie handling, terminal target and numerical operations are retained.
Only per-episode action-count instrumentation is added to the reference loop.
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class Config:
    episodes: int = 5000
    steps_per_episode: int = 20
    alpha: float = 0.1
    gamma: float = 0.9
    epsilon_start: float = 0.2
    epsilon_min: float = 0.02
    epsilon_decay: float = 0.995
    price: float = 10.0
    unit_cost: float = 5.0
    discount_rate: float = 0.2
    low_demand_customers: int = 10
    high_demand_customers: int = 20
    seed: int = 42
    evaluation_episodes: int = 500
    output_dir: str = 'agent02_results'

class ECommerceEnvironment:

    def __init__(self, config, seed=None):
        self.config = config
        actual_seed = config.seed if seed is None else seed
        self.rng = np.random.default_rng(actual_seed)
        self.demand = 0
        self.previous_actions = [0, 0]

    def reset(self):
        self.demand = int(self.rng.integers(0, 2))
        self.previous_actions = [0, 0]
        return self.get_states()

    def get_states(self):
        return [(self.demand, self.previous_actions[1]),
                (self.demand, self.previous_actions[0])]

    def step(self, actions):
        if len(actions) != 2:
            raise ValueError('Exactly two actions are required.')
        if any((action not in (0, 1) for action in actions)):
            raise ValueError('Actions must be 0 or 1.')
        rewards = []
        sales_list = []
        conversion_list = []
        if self.demand == 0:
            customers = self.config.low_demand_customers
        else:
            customers = self.config.high_demand_customers
        for i in range(2):
            own_action = actions[i]
            competitor_action = actions[1 - i]
            conversion = (0.3 + 0.25 * self.demand + 0.15 * own_action
                          - 0.1 * competitor_action)
            conversion = float(np.clip(conversion, 0.05, 0.95))
            sales = int(self.rng.binomial(customers, conversion))
            effective_price = self.config.price * (
                1.0 - self.config.discount_rate * own_action)
            profit_per_sale = effective_price - self.config.unit_cost
            profit = sales * profit_per_sale
            rewards.append(float(profit))
            sales_list.append(sales)
            conversion_list.append(conversion)
        self.previous_actions = list(actions)
        self.demand = int(self.rng.integers(0, 2))
        next_states = self.get_states()
        info = {'sales': sales_list, 'conversion': conversion_list,
                'customers': customers}
        return (next_states, rewards, info)

class QLearningAgent:

    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2, seed=123):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = np.random.default_rng(seed)
        self.q = np.zeros((2, 2, 2), dtype=float)

    def act(self, state, explore=True):
        demand, competitor_previous_action = state
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(0, 2))
        values = self.q[demand, competitor_previous_action]
        best_actions = np.flatnonzero(np.isclose(values, np.max(values)))
        return int(self.rng.choice(best_actions))

    def learn(self, state, action, reward, next_state, terminal=False):
        demand, competitor_previous_action = state
        next_demand, next_competitor_action = next_state
        old_value = self.q[demand, competitor_previous_action, action]
        if terminal:
            target = reward
        else:
            best_future_value = np.max(self.q[next_demand, next_competitor_action])
            target = reward + self.gamma * best_future_value
        self.q[demand, competitor_previous_action, action] = (
            old_value + self.alpha * (target - old_value))

    def greedy_policy(self):
        policy = {}
        for demand in range(2):
            for competitor_action in range(2):
                state = (demand, competitor_action)
                policy[state] = int(np.argmax(self.q[demand, competitor_action]))
        return policy

class RuleBasedAgent:

    def act(self, state):
        demand, competitor_previous_action = state
        if demand == 0:
            return 0
        elif demand == 1 and competitor_previous_action == 1:
            return 1
        else:
            return 0

def train_rl_against_rule(config, seed, alpha=None, epsilon_start=None,
                          epsilon_min=None, epsilon_decay=None):
    alpha = config.alpha if alpha is None else alpha
    epsilon_start = config.epsilon_start if epsilon_start is None else epsilon_start
    epsilon_min = config.epsilon_min if epsilon_min is None else epsilon_min
    epsilon_decay = config.epsilon_decay if epsilon_decay is None else epsilon_decay
    env = ECommerceEnvironment(config, seed=seed)
    rl_agent = QLearningAgent(alpha=alpha, gamma=config.gamma,
                             epsilon=epsilon_start, seed=seed + 10000)
    rule_agent = RuleBasedAgent()
    episode_results = []
    for episode in range(config.episodes):
        rl_agent.epsilon = max(epsilon_min, epsilon_start * epsilon_decay ** episode)
        states = env.reset()
        episode_rewards = [0.0, 0.0]
        action_counts = np.zeros((2, 2), dtype=int)
        for step in range(config.steps_per_episode):
            rl_action = rl_agent.act(states[0], explore=True)
            rule_action = rule_agent.act(states[1])
            actions = [rl_action, rule_action]
            action_counts[0, rl_action] += 1
            action_counts[1, rule_action] += 1
            next_states, rewards, info = env.step(actions)
            terminal = step == config.steps_per_episode - 1
            rl_agent.learn(state=states[0], action=rl_action, reward=rewards[0],
                           next_state=next_states[0], terminal=terminal)
            episode_rewards[0] += rewards[0]
            episode_rewards[1] += rewards[1]
            states = next_states
        episode_results.append({
            'episode': episode + 1,
            'rl_episode_reward': episode_rewards[0],
            'rule_episode_reward': episode_rewards[1],
            'rl_mean_reward_per_step': episode_rewards[0] / config.steps_per_episode,
            'rule_mean_reward_per_step': episode_rewards[1] / config.steps_per_episode,
            'epsilon': rl_agent.epsilon, 'alpha': alpha,
            'rl_no_discount': int(action_counts[0, 0]),
            'rl_discount': int(action_counts[0, 1]),
            'rule_no_discount': int(action_counts[1, 0]),
            'rule_discount': int(action_counts[1, 1])})
    return (rl_agent, episode_results)

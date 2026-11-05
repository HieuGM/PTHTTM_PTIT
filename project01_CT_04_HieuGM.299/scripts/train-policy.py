"""Train a reproducible one-step bandit; reward is presentation rubric, not health."""
from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parents[1]
rng = random.Random(299)
q = [[0.0] * 3 for _ in range(4)]
counts = [[0] * 3 for _ in range(4)]
rewards = []
# States: evidence absent/present × concise/detailed request.
# Actions: abstain, short grounded response, longer grounded response.
targets = [0, 0, 1, 2]
for episode in range(4000):
    s = rng.randrange(4)
    epsilon = max(.08, 1 - episode / 3000)
    a = rng.randrange(3) if rng.random() < epsilon else max(range(3), key=lambda i: q[s][i])
    reward = 1.0 if a == targets[s] else -1.0
    if s < 2 and a != 0:
        reward = -3.0
    q[s][a] += .15 * (reward - q[s][a])
    counts[s][a] += 1
    rewards.append(reward)
greedy = [max(range(3), key=lambda i: row[i]) for row in q]
result = {"algorithm": "Q-learning, one-step contextual bandit (gamma=0)",
          "seed": 299, "episodes": 4000, "q_values": q,
          "visits": counts, "greedy_actions": greedy, "rubric_targets": targets,
          "correct_states": sum(a == b for a, b in zip(greedy, targets)),
          "state_count": 4, "last_500_mean_reward": sum(rewards[-500:])/500,
          "scope": "Toy presentation rubric; no patient outcomes or treatment learning."}
(ROOT / "models").mkdir(exist_ok=True)
(ROOT / "models/presentation-policy.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/policy-training.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"correct_states": result["correct_states"], "state_count": 4}))

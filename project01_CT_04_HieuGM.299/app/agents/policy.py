"""One-step Q-learning presentation policy, separated from medical decisions."""
import json
from pathlib import Path
from app.agents.rules import normalize

ACTIONS = ["abstain", "brief", "detail"]


def state(question, has_evidence):
    detailed = any(x in normalize(question) for x in ["chi tiet", "giai thich", "tai sao", "cu the"])
    return int(has_evidence) * 2 + int(detailed)


class PresentationPolicy:
    def __init__(self, root):
        path = Path(root) / "models/presentation-policy.json"
        if not path.exists():
            raise FileNotFoundError("Cần chạy scripts/train-policy.py trước khi khởi động.")
        self.values = json.loads(path.read_text(encoding="utf-8"))["q_values"]

    def choose(self, question, has_evidence):
        s = state(question, has_evidence)
        index = max(range(len(ACTIONS)), key=lambda i: self.values[s][i])
        return ACTIONS[index]

"""Serializable agent messages and per-request state."""
from dataclasses import dataclass, field, asdict
import time


@dataclass
class Message:
    sender: str
    receiver: str
    kind: str
    detail: str
    elapsed_ms: float


@dataclass
class Context:
    question: str
    glucose: float | None = None
    unit: str = "mg/dL"
    trace: list = field(default_factory=list)
    started: float = field(default_factory=time.perf_counter)
    max_steps: int = 8

    def send(self, sender, receiver, kind, detail):
        if len(self.trace) >= self.max_steps:
            raise RuntimeError("Đã đạt giới hạn điều phối Agent.")
        self.trace.append(asdict(Message(sender, receiver, kind, detail,
                                        round((time.perf_counter()-self.started)*1000, 2))))

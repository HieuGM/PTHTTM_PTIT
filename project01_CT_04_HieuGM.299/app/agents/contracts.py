"""Serializable agent messages and per-request state."""
from dataclasses import dataclass, field, asdict
import time
import uuid


@dataclass
class Message:
    sender: str
    receiver: str
    kind: str
    detail: str
    elapsed_ms: float


@dataclass
class AgentResult:
    request_id: str
    agent: str
    status: str
    payload: dict
    evidence: list
    model_version: str
    elapsed_ms: float
    duration_ms: float = 0.0
    decision: dict = field(default_factory=dict)


@dataclass
class Context:
    question: str
    glucose: float | None = None
    unit: str = "mg/dL"
    trace: list = field(default_factory=list)
    started: float = field(default_factory=time.perf_counter)
    max_steps: int = 8
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list = field(default_factory=list)

    def send(self, sender, receiver, kind, detail):
        if len(self.trace) >= self.max_steps:
            raise RuntimeError("Đã đạt giới hạn điều phối Agent.")
        self.trace.append(asdict(Message(sender, receiver, kind, detail,
                                        round((time.perf_counter()-self.started)*1000, 2))))

    def emit(self, agent, status, payload, evidence=None, version="2.1",
             duration_ms=0.0, decision=None):
        if len(self.messages) >= 12:
            raise RuntimeError("Đã đạt giới hạn thông điệp Agent.")
        result = asdict(AgentResult(self.request_id, agent, status, payload, evidence or [],
            version, round((time.perf_counter()-self.started)*1000, 2),
            round(max(0.0, duration_ms), 3), decision or {}))
        self.messages.append(result)
        return result

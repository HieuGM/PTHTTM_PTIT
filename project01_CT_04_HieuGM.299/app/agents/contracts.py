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

    def emit(self, agent, status, payload, evidence=None, version="2.0"):
        if len(self.messages) >= 12:
            raise RuntimeError("Đã đạt giới hạn thông điệp Agent.")
        result = asdict(AgentResult(self.request_id, agent, status, payload, evidence or [],
                                   version, round((time.perf_counter()-self.started)*1000, 2)))
        self.messages.append(result)
        return result

"""Bounded seven-agent orchestration following the supplied architecture PDF."""
from app.agents.contracts import Context
import pickle
from app.agents.roles import (PatientDataAgent, DLPredictionAgent, RuleBasedAgent,
                              KnowledgeAgent, MonitoringAgent)
from app.agents.reporting import ExplanationAgent, structured_report


class ReportWorkflow:
    version = "hybrid-mas-2.0"

    def __init__(self, root, kb, generator):
        self.data = PatientDataAgent()
        self.dl = DLPredictionAgent(root)
        self.rules = RuleBasedAgent()
        self.knowledge = KnowledgeAgent(kb)
        self.explanation = ExplanationAgent(generator)
        self.monitor = MonitoringAgent()

    def _finish(self, context, status, report=None, error=None):
        audit = self.monitor.run(context, status)
        monitor_status = "degraded" if audit.get("write_status") == "failed" else "ok"
        if monitor_status == "degraded" and status == "completed":
            status = "degraded"
            audit["status"] = status
        context.emit(self.monitor.name, monitor_status, audit, version=self.monitor.version)
        trace = [{"sender": m["agent"], "receiver": "CoordinatorAgent", "kind": m["status"],
                  "detail": f'{m["agent"]}: {m["status"]}', "elapsed_ms": m["elapsed_ms"]}
                 for m in context.messages]
        return {"request_id": context.request_id, "status": status, "report": report,
                "error": error, "messages": context.messages, "trace": trace,
                "audit": audit, "system_version": self.version}

    def run(self, dataset, features, question="", glucose=None, unit="mg/dL"):
        context = Context(question or "")
        context.emit("CoordinatorAgent", "started", {"workflow": "data-dl-rule-kg-explanation-audit"},
                     version=self.version)
        try:
            if not isinstance(question, str) or len(question) > 2000:
                raise ValueError("Câu hỏi cần là chuỗi tối đa 2.000 ký tự.")
            validated = self.data.run(dataset, features, glucose, unit)
        except (ValueError, TypeError, KeyError) as error:
            context.emit(self.data.name, "invalid", {"error": str(error)}, version=self.data.version)
            return self._finish(context, "validation_error", error={"code": "invalid_patient_data",
                                "message": str(error), "agent": self.data.name})
        context.emit(self.data.name, "ok", validated, version=self.data.version)
        try:
            prediction = self.dl.run(dataset, features)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError, EOFError, pickle.UnpicklingError):
            context.emit(self.dl.name, "error", {"error_code": "model_unavailable"})
            return self._finish(context, "dependency_error", error={"code": "model_unavailable",
                "message": "Không nạp hoặc chạy được mô hình. Hãy kiểm tra artifact và phiên bản.",
                "agent": self.dl.name})
        context.emit(self.dl.name, "ok", prediction, version=prediction["model_version"])
        query = question.strip() or "Bệnh đái tháo đường cần theo dõi những gì?"
        rules = self.rules.run(query, prediction, glucose, unit)
        context.emit(self.rules.name, "flagged" if rules["flags"] else "ok", rules,
                     version=self.rules.version)
        evidence, knowledge_status = [], "ok"
        if rules["safety"]:
            knowledge_status = "skipped_safety"
            context.emit(self.knowledge.name, "skipped", {"reason": "safety_override"},
                         version=self.knowledge.version)
        else:
            try:
                knowledge = self.knowledge.run(query)
                evidence = knowledge["evidence"]
                known = getattr(self.knowledge.kb, "source_index", {c["id"]: c for c in self.knowledge.kb.cards})
                if any(hit["id"] not in known or hit["url"] != known[hit["id"]]["url"]
                       or not hit["url"].startswith("https://") for hit in evidence):
                    raise ValueError("Invalid evidence provenance")
                if knowledge["inventory"].get("graph_backend") != "neo4j":
                    knowledge_status = "degraded"
                context.emit(self.knowledge.name, knowledge_status,
                    {"evidence_count": len(evidence), "inventory": knowledge["inventory"]},
                    evidence=evidence, version=self.knowledge.version)
            except (OSError, RuntimeError, ValueError, KeyError, TypeError):
                evidence, knowledge_status = [], "error"
                context.emit(self.knowledge.name, "error", {"error_code": "knowledge_unavailable"},
                             version=self.knowledge.version)
        context.emit("CoordinatorAgent", "aggregated", {"prediction_available": True,
            "rule_flags": len(rules["flags"]), "evidence_count": len(evidence),
            "knowledge_status": knowledge_status, "safety_priority": bool(rules["safety"])},
            version=self.version)
        try:
            explanation = self.explanation.run(query, prediction, rules, evidence)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError):
            explanation = {"answer": "Chưa tạo được giải thích. Hãy xem riêng dự đoán, luật và bằng chứng.",
                           "generation": "template", "status": "explanation_error", "citations": []}
        context.emit(self.explanation.name, explanation["status"],
            {"generation": explanation["generation"], "citations": explanation.get("citations", [])},
            version=explanation.get("model") or self.explanation.version)
        report = structured_report(prediction, rules, evidence, explanation, knowledge_status)
        degraded = knowledge_status in {"degraded", "error"} or explanation["status"] in {
            "explanation_error", "llm_unavailable", "insufficient_evidence"}
        status = rules["safety"]["level"] if rules["safety"] else ("degraded" if degraded else "completed")
        return self._finish(context, status, report=report)

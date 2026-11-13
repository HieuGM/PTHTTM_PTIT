"""Seven core agents with bounded internal retrieval/review decisions and timings."""
import pickle
import time
from app.agents.contracts import Context
from app.agents.roles import (PatientDataAgent, DLPredictionAgent, RuleBasedAgent,
                              KnowledgeAgent, MonitoringAgent)
from app.agents.reporting import ExplanationAgent, structured_report
from app.capabilities import VERSION, usage


def duration(start):
    return (time.perf_counter()-start)*1000


class ReportWorkflow:
    version = VERSION

    def __init__(self, root, kb, generator):
        self.data = PatientDataAgent()
        self.dl = DLPredictionAgent(root)
        self.rules = RuleBasedAgent()
        self.knowledge = KnowledgeAgent(kb)
        self.explanation = ExplanationAgent(generator)
        self.monitor = MonitoringAgent()

    def _finish(self, context, status, report=None, error=None):
        started = time.perf_counter()
        audit = self.monitor.run(context, status)
        monitor_status = "degraded" if audit.get("write_status") == "failed" else "ok"
        if monitor_status == "degraded" and status == "completed":
            status = "degraded"
            audit["status"] = status
        context.emit(self.monitor.name, monitor_status, audit, version=self.monitor.version,
            duration_ms=duration(started), decision={"action": "metadata_audit",
            "reason": audit.get("write_status", "disabled")})
        trace = [{"sender": m["agent"], "receiver": "CoordinatorAgent", "kind": m["status"],
                  "detail": f'{m["agent"]}: {m["status"]}', "elapsed_ms": m["elapsed_ms"],
                  "duration_ms": m["duration_ms"]} for m in context.messages]
        decisions = [{"stage": m["agent"], "status": m["status"], **m["decision"]}
                     for m in context.messages]
        return {"request_id": context.request_id, "status": status, "report": report,
                "error": error, "messages": context.messages, "trace": trace,
                "decision_trace": decisions, "feature_usage": usage(context.messages, report),
                "audit": audit, "system_version": self.version}

    def run(self, dataset, features, question="", glucose=None, unit="mg/dL"):
        context = Context(question or "")
        context.emit("CoordinatorAgent", "started", {"workflow": "bounded-adaptive-report"},
            version=self.version, decision={"action": "start", "reason": "seven_role_contract"})
        started = time.perf_counter()
        try:
            if not isinstance(question, str) or len(question) > 2000:
                raise ValueError("Câu hỏi cần là chuỗi tối đa 2.000 ký tự.")
            validated = self.data.run(dataset, features, glucose, unit)
        except (ValueError, TypeError, KeyError) as error:
            context.emit(self.data.name, "invalid", {"error": str(error)}, version=self.data.version,
                duration_ms=duration(started), decision={"action": "stop", "reason": "invalid_input"})
            return self._finish(context, "validation_error", error={"code": "invalid_patient_data",
                                "message": str(error), "agent": self.data.name})
        context.emit(self.data.name, "ok", validated, version=self.data.version,
            duration_ms=duration(started), decision={"action": "allow_prediction", "reason": "schema_valid"})
        started = time.perf_counter()
        try:
            prediction = self.dl.run(dataset, features)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError, EOFError, pickle.UnpicklingError):
            context.emit(self.dl.name, "error", {"error_code": "model_unavailable"},
                duration_ms=duration(started), decision={"action": "stop", "reason": "model_unavailable"})
            return self._finish(context, "dependency_error", error={"code": "model_unavailable",
                "message": "Không nạp hoặc chạy được mô hình. Hãy kiểm tra artifact và phiên bản.",
                "agent": self.dl.name})
        context.emit(self.dl.name, "ok", prediction, version=prediction["model_version"],
            duration_ms=duration(started), decision={"action": "inference", "reason": "frozen_serving_artifact"})
        query = question.strip() or "Bệnh đái tháo đường cần theo dõi những gì?"
        started = time.perf_counter()
        rules = self.rules.run(query, prediction, glucose, unit)
        context.emit(self.rules.name, "flagged" if rules["flags"] else "ok", rules,
            version=self.rules.version, duration_ms=duration(started),
            decision={"action": "safety_override" if rules["safety"] else "allow_retrieval",
                      "reason": rules["safety"]["level"] if rules["safety"] else "no_safety_override"})
        evidence, knowledge_status = [], "ok"
        retrieval = {"attempts": [], "sufficient": False, "reason": "skipped_safety"}
        if rules["safety"]:
            knowledge_status = "skipped_safety"
            context.emit(self.knowledge.name, "skipped", {"reason": "safety_override"},
                version=self.knowledge.version, decision={"action": "skip", "reason": "safety_override"})
        else:
            started = time.perf_counter()
            try:
                knowledge = self.knowledge.run(query)
                evidence = knowledge["evidence"]
                retrieval = knowledge.get("retrieval", retrieval)
                known = self.knowledge.kb.source_index
                if any(hit["id"] not in known or hit["url"] != known[hit["id"]]["url"]
                       or not hit["url"].startswith("https://") for hit in evidence):
                    raise ValueError("Invalid evidence provenance")
                if knowledge["inventory"].get("graph_backend") != "neo4j":
                    knowledge_status = "degraded"
                context.emit(self.knowledge.name, knowledge_status,
                    {"evidence_count": len(evidence), "inventory": knowledge["inventory"], "retrieval": retrieval},
                    evidence=evidence, version=self.knowledge.version, duration_ms=duration(started),
                    decision={"action": "accept_evidence" if retrieval.get("sufficient") else "abstain",
                              "reason": retrieval.get("reason", "not_assessed"),
                              "attempt_count": len(retrieval.get("attempts", []))})
            except (OSError, RuntimeError, ValueError, KeyError, TypeError):
                evidence, knowledge_status = [], "error"
                retrieval = {"attempts": [], "sufficient": False, "reason": "knowledge_unavailable"}
                context.emit(self.knowledge.name, "error", {"error_code": "knowledge_unavailable"},
                    version=self.knowledge.version, duration_ms=duration(started),
                    decision={"action": "abstain", "reason": "knowledge_unavailable"})
        started = time.perf_counter()
        aggregate = {"prediction_available": True, "rule_flags": len(rules["flags"]),
            "evidence_count": len(evidence), "knowledge_status": knowledge_status,
            "safety_priority": bool(rules["safety"])}
        context.emit("CoordinatorAgent", "aggregated", aggregate, version=self.version,
            duration_ms=duration(started), decision={"action": "aggregate", "reason": "preserve_information_types"})
        started = time.perf_counter()
        try:
            explanation = self.explanation.run(query, prediction, rules, evidence)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError):
            explanation = {"answer": "Chưa tạo được giải thích. Hãy xem riêng dự đoán, luật và bằng chứng.",
                "generation": "template", "status": "explanation_error", "citations": [],
                "review": {"passed": False, "status": "error", "revision_count": 0}}
        quality = explanation.get("review", {})
        context.emit(self.explanation.name, explanation["status"],
            {"generation": explanation["generation"], "citations": explanation.get("citations", []),
             "review": quality}, version=explanation.get("model") or self.explanation.version,
            duration_ms=duration(started), decision={"action": quality.get("status", "not_assessed"),
                "reason": "safety_override" if rules["safety"] else "post_generation_review",
                "revision_count": quality.get("revision_count", 0)})
        report = structured_report(prediction, rules, evidence, explanation, knowledge_status)
        report.update(retrieval=retrieval, quality=quality)
        if quality.get("revision_count", 0) or quality.get("passed") is False:
            report["review_flags"].append({"rule_id": "output_review", "severity": "review",
                "reason": "Cần xem kết quả kiểm duyệt và lịch sử sửa câu trả lời."})
            report["requires_human_review"] = True
        degraded = knowledge_status in {"degraded", "error"} or explanation["status"] in {
            "explanation_error", "llm_unavailable", "insufficient_evidence", "revised_extractive"}
        status = rules["safety"]["level"] if rules["safety"] else ("degraded" if degraded else "completed")
        return self._finish(context, status, report=report)

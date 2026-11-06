"""Explicit input/output contracts for the PDF's independent specialist agents."""
import json
import math
import os
import time
from pathlib import Path
from app.agents.rules import check
from app.ml.predict import Predictor, validate_features
from app.ml.schema import SCHEMAS


class PatientDataAgent:
    name = "PatientDataAgent"
    version = "schema-2.0"

    def run(self, dataset, features, glucose=None, unit="mg/dL"):
        if unit not in {"mg/dL", "mmol/L"}:
            raise ValueError("Đơn vị đường huyết không hợp lệ.")
        if glucose is not None:
            upper = 83.3 if unit == "mmol/L" else 1500
            if isinstance(glucose, bool) or not isinstance(glucose, (int, float)):
                raise ValueError("Đường huyết cần là số hữu hạn.")
            if not 0 < glucose <= upper or not math.isfinite(glucose):
                raise ValueError("Đường huyết ngoài miền nhập cho phép.")
        values = validate_features(dataset, features)
        return {"validated": True, "dataset": dataset, "feature_count": len(values),
                "feature_order": [s["name"] for s in SCHEMAS[dataset]]}


class DLPredictionAgent:
    name = "DLPredictionAgent"

    def __init__(self, root):
        self.predictor = Predictor(root)

    def run(self, dataset, features):
        result = self.predictor.predict(dataset, features)
        metadata = self.predictor.metadata(dataset)
        result["model_version"] = metadata.get("model_version", "legacy-1.0")
        result["artifact_reused"] = dataset in {"cdc", "hospital"}
        return result


class RuleBasedAgent:
    name = "RuleBasedAgent"
    version = "educational-rules-2.0"

    def run(self, question, prediction, glucose=None, unit="mg/dL"):
        safety = check(question, glucose, unit)
        flags = []
        if safety:
            flags.append({"rule_id": "safety_override", "severity": safety["level"],
                          "reason": safety["reason"], "source": safety["url"]})
        margin = abs(prediction["risk_score"] - prediction["threshold"])
        if margin <= .05:
            flags.append({"rule_id": "near_model_threshold", "severity": "review",
                "reason": "Điểm cách ngưỡng phân loại không quá 0,05; nên xem xét độ ổn định của mô hình.",
                "source": "operational model-review rule; not a clinical threshold"})
        if prediction["predicted_class"] == 1:
            flags.append({"rule_id": "positive_research_label", "severity": "review",
                "reason": "Mô hình phân loại nhãn nghiên cứu dương; cần diễn giải cùng nhiệm vụ và giới hạn.",
                "source": "model metadata"})
        return {"safety": safety, "flags": flags, "clinical_use": False,
                "decision_priority": "Safety rules override the presentation of all model scores."}


class KnowledgeAgent:
    name = "KGRAGAgent"
    version = "hybrid-graph-retrieval-2.0"

    def __init__(self, kb):
        self.kb = kb

    def run(self, question):
        hits = self.kb.retrieve(question, k=4)
        return {"evidence": hits, "inventory": self.kb.inventory(), "evidence_count": len(hits)}


class MonitoringAgent:
    name = "MonitoringAgent"
    version = "metadata-audit-2.0"

    def run(self, context, status):
        audit = {"request_id": context.request_id, "status": status,
            "duration_ms": round((time.perf_counter()-context.started)*1000, 2),
            "agents": [{k: m[k] for k in ("agent", "status", "model_version", "elapsed_ms")}
                       for m in context.messages],
            "records_patient_features": False, "records_question": False,
            "records_api_keys": False}
        # Opt-in metadata only; no patient payload or question is persisted.
        if os.getenv("AUDIT_LOG_PATH"):
            path = Path(os.environ["AUDIT_LOG_PATH"])
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(audit, ensure_ascii=False)+"\n")
                audit["write_status"] = "written"
            except OSError as error:
                audit["write_status"] = "failed"
                audit["error_code"] = type(error).__name__
        else:
            audit["write_status"] = "disabled"
        return audit

"""Grounded structured reports keep model, symbolic rules and evidence separate."""


class ExplanationAgent:
    name = "ExplanationAgent"
    version = "grounded-report-2.0"

    def __init__(self, generator):
        self.generator = generator

    def run(self, question, prediction, rules, evidence):
        safety = rules.get("safety")
        if safety:
            return {"answer": safety["answer"], "generation": "safety_rule",
                    "status": safety["level"], "citations": [], "model": None}
        return self.generator.generate(question, evidence, model_output=prediction, rules=rules)


def structured_report(prediction, rules, evidence, explanation, knowledge_status):
    review_flags = list(rules.get("flags", []))
    if not evidence:
        review_flags.append({"rule_id": "missing_relevant_evidence", "severity": "review",
                             "reason": "Chưa truy xuất được bằng chứng phù hợp cho câu hỏi."})
    if knowledge_status not in {"ok", "skipped_safety"}:
        review_flags.append({"rule_id": "knowledge_dependency_degraded", "severity": "review",
                             "reason": "Thành phần tri thức đang dùng chế độ dự phòng hoặc gặp lỗi."})
    limitations = list(prediction.get("limitations", []))
    limitations.extend(["Dự đoán mô hình, kết quả luật và tài liệu truy xuất là các loại thông tin riêng.",
                        "Nguồn trích dẫn hợp lệ không tự chứng minh từng câu giải thích được tài liệu hỗ trợ."])
    sources = [{k: hit[k] for k in ("id", "title", "url", "document_id", "page") if k in hit}
               for hit in evidence]
    uncertainty = {"score_calibrated": False, "external_validation_vietnam": False,
        "near_model_threshold": any(f.get("rule_id") == "near_model_threshold" for f in review_flags),
        "evidence_available": bool(evidence), "knowledge_status": knowledge_status,
        "interpretation": "Điểm mô hình chưa hiệu chuẩn; chưa định lượng bất định cho từng cá nhân."}
    conflicts = {"status": "requires_review" if rules.get("safety") else "not_assessed",
        "items": ([{"type": "safety_override", "resolution": "Ưu tiên cảnh báo quy tắc; không dùng score để bỏ qua cảnh báo."}]
                  if rules.get("safety") else []),
        "limitation": "Không có bộ kiểm chứng mâu thuẫn ngữ nghĩa tự động giữa dự đoán và tài liệu."}
    return {"prediction": prediction, "rule_results": rules, "retrieved_evidence": evidence,
            "explanation": explanation, "sources": sources, "review_flags": review_flags,
            "uncertainty": uncertainty, "conflicts": conflicts,
            "limitations": list(dict.fromkeys(limitations)), "clinical_use": False,
            "requires_human_review": bool(review_flags)}

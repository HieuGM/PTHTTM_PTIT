"""Five communicating roles with safety and citation gates."""
from app.agents.contracts import Context
from app.agents.rules import check, normalize
from app.agents.policy import PresentationPolicy
from app.knowledge.retrieval import KnowledgeBase


class Coordinator:
    def __init__(self, root):
        self.kb = KnowledgeBase(root)
        self.policy = PresentationPolicy(root)

    def answer(self, question, glucose=None, unit="mg/dL"):
        ctx = Context(question, glucose, unit)
        ctx.send("Coordinator", "SafetyAgent", "request", "Kiểm tra dấu hiệu nguy hiểm và phạm vi tư vấn.")
        safety = check(question, glucose, unit)
        if safety:
            ctx.send("SafetyAgent", "Coordinator", "override", safety["reason"])
            return {"answer": safety["answer"], "status": safety["level"],
                    "sources": [{"id": "rule", "title": "Nguồn quy tắc an toàn", "url": safety["url"]}],
                    "trace": ctx.trace, "policy_action": "safety_override", "generation": "rule"}
        ctx.send("SafetyAgent", "RetrievalAgent", "allow", "Trong phạm vi giáo dục; truy xuất tri thức.")
        hits = self.kb.retrieve(question)
        # Topic guard supplements lexical similarity; no evidence => explicit abstention.
        q = normalize(question)
        diabetes_terms = ["tieu duong", "dai thao duong", "duong huyet", "glucose", "hba1c", "insulin",
                          "metformin", "ha duong", "ceton", "bien chung", "ban chan", "an uong",
                          "van dong", "dinh duong", "tien dai", "thai ky", "tiep can du lieu",
                          "tip 1", "tip 2", "thuoc dieu tri", "albumin", "cdc", "nguy co", "cgm"]
        evidence = bool(hits) and any(t in q for t in diabetes_terms)
        action = self.policy.choose(question, evidence)
        ctx.send("RetrievalAgent", "PolicyAgent", "evidence", f"{len(hits)} đoạn phù hợp; nguồn được giữ theo ID.")
        ctx.send("PolicyAgent", "EducationAgent", "presentation", f"Q-learning chọn cách trình bày: {action}.")
        if not evidence or action == "abstain":
            answer = "Kho tri thức hiện chưa có đủ bằng chứng phù hợp để trả lời câu hỏi này. Bạn có thể hỏi về kiến thức, theo dõi và phòng biến chứng đái tháo đường; với tình huống cá nhân, hãy trao đổi với nhân viên y tế."
            sources, status = [], "insufficient_evidence"
        else:
            selected = hits[:2] if action == "detail" else hits[:1]
            answer = "\n\n".join(f"{h['text']} [{h['id']}]" for h in selected)
            sources = [{k: h[k] for k in ["id", "title", "url"]} for h in selected]
            status = "grounded"
        ctx.send("EducationAgent", "CriticAgent", "draft", "Ghép nội dung trích xuất với dẫn nguồn của từng đoạn.")
        known = {card["id"] for card in self.kb.cards}
        if any(s["id"] not in known or not s["url"].startswith("https://") for s in sources):
            raise RuntimeError("Nguồn dẫn không hợp lệ.")
        ctx.send("CriticAgent", "Coordinator", "verified", "Kiểm tra ID nguồn và định dạng; không xác thực chẩn đoán.")
        return {"answer": answer, "status": status, "sources": sources, "trace": ctx.trace,
                "policy_action": action, "generation": "extractive", "retrieved_ids": [h["id"] for h in hits]}

    def analyze(self, dataset, features):
        from app.ml.predict import predict
        ctx = Context("model_analysis")
        ctx.send("Coordinator", "DataAgent", "validate", f"Kiểm tra đầy đủ trường của dataset {dataset}.")
        result = predict(dataset, features)
        ctx.send("DataAgent", "PredictionAgent", "validated", "Đã kiểm tra schema, kiểu và miền giá trị.")
        ctx.send("PredictionAgent", "CriticAgent", "prediction", "Suy luận MLP từ trọng số đã huấn luyện.")
        ctx.send("CriticAgent", "Coordinator", "verified", "Điểm mô hình nghiên cứu; không phải chẩn đoán hoặc xác suất đã hiệu chuẩn lâm sàng.")
        return {**result, "trace": ctx.trace}

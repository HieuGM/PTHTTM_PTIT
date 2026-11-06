# CHƯƠNG 2. KIẾN TRÚC HYBRID MULTIAGENT SYSTEM

## 2.1. Sáu lớp hệ thống

Sáu lớp gồm giao diện; API và xử lý dữ liệu; điều phối; agent chuyên biệt; model và knowledge; đánh giá/audit. Các agent chạy trong một tiến trình Python, giao tiếp qua object có cấu trúc. Cách triển khai này hỗ trợ kiểm thử và theo dõi; chưa là agent phân tán độc lập qua message broker.

![Kiến trúc bảy agent và hai kho dữ liệu](figures/architecture.png)

SQLite huấn luyện chứa raw/prepared và split, chỉ dùng cục bộ. SQLite cache tri thức chứa tài liệu/chunk/quan hệ công khai. Neo4j lưu graph; trọng số DL nạp từ artifact. Không huấn luyện lại tại request.

## 2.2. Bảy agent và ánh xạ mã nguồn

| Agent | Thành phần | Trách nhiệm |
|---|---|---|
| Patient Data | PatientDataAgent, roles.py | Kiểm schema, kiểu, thứ tự, miền, thiếu giá trị |
| DL Prediction | DLPredictionAgent, predict.py | Nạp model/scaler/ngưỡng; score, nhãn, metadata |
| Rule-Based | RuleBasedAgent, rules.py | Luật có lý do, cảnh báo và review flags |
| KG/RAG | KnowledgeAgent, retrieval.py | Thực thể, graph, chunk, ranking và nguồn |
| Coordinator | ReportWorkflow, workflow.py | Điều phối, dừng sớm, tổng hợp và xử lý lỗi |
| Explanation | ExplanationAgent, generation.py | Giải thích bằng FPT hoặc template có nhãn |
| Monitoring | MonitoringAgent, roles.py | Metadata, trạng thái, version và độ trễ |

Coordinator không thay thuật toán của agent khác. Prediction suy luận; KG tìm tài liệu; Explanation dùng kết quả đã có. Có thể thay retriever hoặc LLM mà không đổi schema dự đoán. Số lần message không phải số loại agent, vì Coordinator có thể phát nhiều sự kiện trong một request.

## 2.3. Hợp đồng giao tiếp

Message có request_id, agent, status, payload, evidence, model_version và elapsed_ms. Phiên bản nhận diện model hoặc agent; request_id liên kết toàn bộ cùng yêu cầu. Payload tùy chức năng, không phải chuỗi log không cấu trúc.

```json
{"request_id":"ma-tu-sinh", "agent":"DLPredictionAgent",
 "status":"ok", "payload":{"dataset":"cdc"},
 "evidence":[], "model_version":"legacy-1.0", "elapsed_ms":12.5}
```

Ví dụ minh họa cấu trúc, không phải đo độ trễ. Monitoring mặc định chỉ ghi metadata, không vector sức khỏe, câu hỏi hoặc khóa API.

## 2.4. Luồng chính và dừng sớm

API nhận cohort và feature. Coordinator tạo request_id, gọi Data. Nếu schema/giá trị sai, trả validation_error trước DL, Rule và KG. Nếu hợp lệ: DL suy luận; Rule đánh giá; KG lấy evidence; Coordinator tổng hợp; Explanation tạo báo cáo; Monitoring ghi metadata.

Luồng hữu hạn có trace. Cảnh báo nguy cấp và yêu cầu vượt phạm vi được luật ưu tiên để LLM không trì hoãn hoặc ghi đè thông báo an toàn. Điểm dự đoán nghiên cứu không phủ quyết cảnh báo luật; tài liệu giáo dục không là quan sát của cá nhân.

## 2.5. Lỗi và dự phòng

DL lỗi thì trả dependency_error, không tạo score giả. Thiếu Neo4j/kết nối lỗi thì dùng cache và nêu backend. Thiếu FPT, lỗi API hoặc citation không hợp lệ thì dùng template có nhãn. Không gọi template là output đã sinh bằng LLM.

Fallback giúp demo cục bộ, không là bằng chứng Neo4j production. Health/catalog công bố model, inventory, graph và LLM configuration; bằng chứng gọi API thật được ghi riêng với metadata an toàn.

## 2.6. Ranh giới dữ liệu và bảo mật

API không nhận SQL/Cypher tùy ý. Query graph dùng tham số. Corpus ingest trước, không tải URL tùy ý từ request. Nội dung nguồn là dữ liệu hỗ trợ, không được thực thi như chỉ thị.

FPT key và Neo4j password chỉ ở môi trường/.env bị ignore. Raw/database chứa patient_nbr phục vụ split không vào Git/image/ZIP. Artifact state_dict nạp weights_only=True; không pickle toàn bộ object mô hình. Audit ra file chỉ bật khi cấu hình rõ đường dẫn.

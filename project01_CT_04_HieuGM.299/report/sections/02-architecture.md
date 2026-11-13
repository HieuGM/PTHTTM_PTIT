# CHƯƠNG 2. KIẾN TRÚC HYBRID MULTIAGENT SYSTEM

## 2.1. Agent và hệ đa agent trong phạm vi đề tài

Agent phần mềm nhận thông tin từ môi trường, xử lý theo mục tiêu và tạo hành động hoặc kết quả. Wooldridge và Jennings mô tả các đặc tính thường dùng để nhận diện agent: tự chủ, tương tác với agent khác, phản ứng với môi trường và hành vi hướng mục tiêu. Đặc tính này là cơ sở phân tích thiết kế, không có nghĩa mọi hàm xử lý hoặc mọi lớp Python đều tự động trở thành agent có năng lực suy luận độc lập. Nguồn: [Wooldridge và Jennings, Intelligent Agents: Theory and Practice](https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/ker95/subsubsectionstar3_1_1_1.html).

Trong DiaCare, môi trường quan sát gồm request API, trạng thái model, kết quả truy xuất và trạng thái phụ thuộc. Hành động của agent là trả dữ liệu đã kiểm tra, chạy suy luận, phát cảnh báo, lấy evidence hoặc tạo giải thích. Mục tiêu chung là tạo báo cáo có thể truy vết; mỗi vai trò chỉ nhận phần thông tin cần cho nhiệm vụ. Ví dụ, Prediction không sửa luật, còn Explanation không huấn luyện lại mạng hoặc đổi ngưỡng phân lớp.

Mức tự chủ của nguyên mẫu còn giới hạn. Coordinator quyết định thứ tự gọi theo một quy trình hữu hạn; các agent chuyên biệt thực hiện thuật toán đã định nghĩa khi được gọi. Hệ thống chưa có agent tự đặt mục tiêu dài hạn, thương lượng, lập kế hoạch mở hoặc chạy liên tục trong tiến trình riêng. Vì vậy, cách gọi chính xác là kiến trúc đa agent theo vai trò, được điều phối tập trung theo đặc tả của môn học. Đóng góp nằm ở phân trách nhiệm, hợp đồng giao tiếp, phối hợp nhiều phương pháp AI và khả năng kiểm tra từng bước.

Các phương pháp có vai trò khác nhau: Deep Learning học hàm dự đoán từ dữ liệu; luật biểu diễn điều kiện minh bạch; KG/RAG tìm tri thức có nguồn; LLM diễn đạt kết quả đã tổng hợp. Agent không đồng nghĩa với LLM: Data, Rule và Monitoring dùng xử lý xác định; chỉ Explanation có thể gọi dịch vụ sinh ngôn ngữ. RL là mô phỏng tùy chọn, không điều khiển bảy vai trò cốt lõi.

## 2.2. Sáu lớp hệ thống

Sáu lớp gồm giao diện; API và xử lý dữ liệu; điều phối; agent chuyên biệt; model và knowledge; đánh giá/audit. Các agent chạy trong một tiến trình Python, giao tiếp qua object có cấu trúc. Cách triển khai này hỗ trợ kiểm thử và theo dõi; chưa là agent phân tán độc lập qua message broker.

![Kiến trúc bảy agent và hai kho dữ liệu](figures/architecture.png)

SQLite huấn luyện chứa raw/prepared và split, chỉ dùng cục bộ. SQLite cache tri thức chứa tài liệu/chunk/quan hệ công khai. Neo4j lưu graph; trọng số DL nạp từ artifact. Không huấn luyện lại tại request.

## 2.3. Mô hình trừu tượng và trạng thái hệ thống

Đặc tả kiến trúc, mục 4 ở trang PDF 5-6, biểu diễn hệ đa agent bằng M = (A, S, O, C, F). Các thành phần được ánh xạ vào nguyên mẫu như sau:

| Ký hiệu | Ý nghĩa trong DiaCare | Hiện thực |
|---|---|---|
| A | Tập bảy vai trò cốt lõi | Data, DL, Rule, KG/RAG, Coordinator, Explanation, Monitoring |
| S | Trạng thái của một yêu cầu và kết quả trung gian | Context, prediction, rules, evidence, explanation |
| O | Quan sát cấp cho từng vai trò | Feature/schema, câu hỏi, output model, inventory phụ thuộc |
| C | Cơ chế trao đổi kết quả có cấu trúc | AgentResult, Context.emit, danh sách messages |
| F | Quy tắc điều phối, tổng hợp và kết thúc | ReportWorkflow.run, structured_report, _finish |

S không phải một cơ sở dữ liệu bệnh án dùng chung. Context tạo mới cho từng request, giữ request_id, thời điểm bắt đầu và message; các biến kết quả nằm trong lượt thực thi workflow. Model và corpus có thể được nạp lại để tái sử dụng giữa các request, nhưng hệ thống không học từ feature người dùng gửi lên. Cách tách này giúp phân biệt trạng thái thực thi tạm thời với artifact mô hình và kho tài liệu đã chuẩn bị.

Mỗi agent được mô tả bằng ánh xạ Ai: Xi → Yi. Chẳng hạn, DL ánh xạ feature hợp lệ sang score, nhãn và metadata; KG ánh xạ câu hỏi sang danh sách evidence; Monitoring ánh xạ metadata thực thi sang bản ghi audit. F kết hợp các output nhưng giữ prediction, rule_results và retrieved_evidence ở các trường riêng. Đây là tổng hợp thông tin theo hợp đồng, không cộng score truy xuất với score DL thành một xác suất bệnh mới.

Mô hình trừu tượng giải thích ranh giới thay thế thành phần. Khi đổi thuật toán retrieval, đầu ra evidence vẫn phải giữ ID, văn bản và nguồn; khi đổi dịch vụ LLM, prediction và rule_results vẫn có nghĩa như trước. Khả năng thay thế phụ thuộc việc giữ contract và kiểm thử tương ứng, không chỉ giữ tên class.

## 2.4. Bảy agent và hợp đồng đầu vào, đầu ra

| Agent và mã nguồn | Đầu vào | Đầu ra chính |
|---|---|---|
| Patient Data: PatientDataAgent, roles.py | Dataset, feature, glucose và unit tùy chọn | Xác nhận hợp lệ, số/thứ tự feature; hoặc lỗi schema, kiểu, miền, thiếu giá trị |
| DL Prediction: DLPredictionAgent, predict.py | Dataset và feature đã qua kiểm tra | Score, nhãn, threshold, task, metadata/version; nạp model và scaler tương ứng |
| Rule-Based: RuleBasedAgent, rules.py | Câu hỏi, prediction, glucose/unit | Safety, rule_id, lý do, nguồn và review flags |
| KG/RAG: KnowledgeAgent, adaptive.py | Câu hỏi | Evidence có nguồn, inventory và retrieval gồm attempts, lý do, lượt chọn hoặc từ chối |
| Coordinator: ReportWorkflow, workflow.py | Yêu cầu tổng hợp | Status, report hoặc error, request_id, messages và audit |
| Explanation: ExplanationAgent, reporting.py | Câu hỏi, prediction, rules, evidence | Answer, generation, citations và quality; kiểm duyệt/sửa có giới hạn |
| Monitoring: MonitoringAgent, roles.py | Context và trạng thái workflow | Metadata audit, version, mốc thời gian; write_status khi bật ghi file |

Coordinator không thay thuật toán của agent khác. Prediction suy luận; KG tìm tài liệu; Explanation dùng kết quả đã có. Có thể thay retriever hoặc LLM mà không đổi schema dự đoán. Số lần message không phải số loại agent, vì Coordinator có thể phát nhiều sự kiện trong một request.

Trạng thái của vai trò và trạng thái toàn workflow có ý nghĩa khác nhau. Data phát ok hoặc invalid; DL phát ok hoặc error; Rule phát flagged khi có cờ; KG có thể ok, degraded, error hoặc skipped. Explanation công bố trạng thái sinh thực tế; Monitoring có thể degraded khi ghi audit thất bại. Coordinator dùng started và aggregated để đánh dấu hai mốc điều phối. Workflow trả completed, degraded, validation_error, dependency_error hoặc mức safety tương ứng. Không diễn giải mọi message khác ok là một yêu cầu đã thất bại hoàn toàn.

Đường dẫn trong bảng rút gọn theo thư mục: agent ở app/agents, model ở app/ml, retrieval/generation ở app/knowledge. Contract được kiểm ở tests/test_workflow.py; các tình huống model, audit và dependency lỗi được kiểm ở tests/test_failure_paths.py. Tên lớp triển khai KnowledgeAgent phát tên vai trò KGRAGAgent trong message; đây là cùng một vai trò truy xuất, không phải hai agent khác nhau.

## 2.5. Hợp đồng giao tiếp và cách đọc thời gian

Message có request_id, agent, status, payload, evidence, model_version, elapsed_ms, duration_ms và decision. Phiên bản nhận diện model hoặc agent; request_id liên kết toàn bộ cùng yêu cầu. Payload tùy chức năng; decision ghi hành động và lý do điều phối.

```json
{"request_id":"ma-tu-sinh", "agent":"DLPredictionAgent",
 "status":"ok", "payload":{"dataset":"cdc"},
 "evidence":[], "model_version":"legacy-1.0", "elapsed_ms":12.5,
 "duration_ms":10.2, "decision":{"action":"inference"}}
```

Ví dụ minh họa cấu trúc, không phải đo độ trễ. Monitoring mặc định chỉ ghi metadata, không vector sức khỏe, câu hỏi hoặc khóa API.

Trường elapsed_ms trong Context.emit là thời gian tích lũy từ lúc tạo Context đến lúc phát message. Bản 2.1 bổ sung duration_ms của message, đo bằng perf_counter ngay trước/sau call trong ReportWorkflow. Nó bao gồm công việc nội bộ của call, chẳng hạn các lượt retrieval hoặc review; không phải hiệu hai mốc elapsed_ms. Bước skipped có duration_ms bằng 0. duration_ms ở cấp audit vẫn là tổng thời gian tới lúc tạo audit. Không cộng các mốc tích lũy để tính latency; một lượt minh họa cũng chưa là benchmark tải hoặc SLA.

Luồng thường có tám message: Coordinator bắt đầu, Data, DL, Rule, KG, Coordinator tổng hợp, Explanation và Monitoring. Như vậy có bảy loại agent. Context.emit giới hạn tối đa 12 message để chặn luồng vượt ngân sách; giới hạn max_steps=8 trong Context.send thuộc trace của các API cũ. Hai cơ chế cùng có request context nhưng không nên dùng số bước của luồng chat để suy ra số agent hoặc số message của report.

## 2.6. Luồng chính, nhánh lỗi và dừng sớm

API nhận cohort và feature. Coordinator tạo request_id, gọi Data. Nếu schema/giá trị sai, trả validation_error trước DL, Rule và KG. Nếu hợp lệ: DL suy luận; Rule đánh giá; KG lấy evidence; Coordinator tổng hợp; Explanation tạo báo cáo; Monitoring ghi metadata.

Luồng hữu hạn có trace. Cảnh báo nguy cấp và yêu cầu vượt phạm vi được luật ưu tiên để LLM không trì hoãn hoặc ghi đè thông báo an toàn. Điểm dự đoán nghiên cứu không phủ quyết cảnh báo luật; tài liệu giáo dục không là quan sát của cá nhân.

![Luồng tuần tự và các nhánh xử lý của báo cáo tổng hợp](figures/workflow-sequence.png)

Mã giả dưới đây tóm tắt ReportWorkflow.run và _finish; chi tiết điều kiện hợp lệ nằm trong schema và validator của từng cohort.

```text
Tạo Context; phát Coordinator: started
Kiểm câu hỏi, feature, glucose và unit
Nếu sai: phát Data: invalid; audit; trả validation_error
Phát Data: ok
Chạy DL bằng artifact đã lưu
Nếu lỗi: phát DL: error; audit; trả dependency_error
Phát DL: ok; chạy Rule; phát kết quả và flags
Nếu Rule có safety:
    Evidence rỗng; phát KG: skipped
Ngược lại:
    Truy xuất thích ứng tối đa ba lượt; kiểm provenance
    Thiếu Neo4j: dùng cache, đánh dấu degraded
    Lỗi truy xuất: evidence rỗng, đánh dấu error
Phát Coordinator: aggregated
Explanation nhận prediction, rules và evidence
    Có safety: trả nội dung safety_rule
    Không safety: generator, review, sửa extractive tối đa một lần
Tạo structured_report, uncertainty và conflicts
Chọn trạng thái workflow theo safety và phụ thuộc
Monitoring tạo audit; trả report, messages và status
```

Nhánh safety vẫn chạy sau DL theo thứ tự của đặc tả. Khi đã có safety, KG bị bỏ qua và Explanation trả thông điệp của luật, không gọi LLM. Với đầu vào sai, DL không chạy; với model không nạp được, không sinh score thay thế. Nếu lỗi chỉ ảnh hưởng tri thức hoặc giải thích, các kết quả đã có vẫn được giữ để người đọc xem riêng và nhận biết phần suy giảm.

## 2.7. Lỗi và dự phòng

DL lỗi thì trả dependency_error, không tạo score giả. Thiếu Neo4j/kết nối lỗi thì dùng cache và nêu backend. Thiếu FPT, lỗi API hoặc citation không hợp lệ thì dùng template có nhãn. Không gọi template là output đã sinh bằng LLM.

Fallback giúp demo cục bộ, không là bằng chứng Neo4j production. Health/catalog công bố model, inventory, graph và LLM configuration; bằng chứng gọi API thật được ghi riêng với metadata an toàn.

API ánh xạ validation_error sang HTTP 422 và dependency_error sang HTTP 503. Report hoàn tất hoặc degraded vẫn có thể trả HTTP 200, vì client cần đọc trạng thái nghiệp vụ trong JSON. Do đó, chỉ thấy HTTP 200 chưa đủ kết luận mọi dịch vụ ngoài hoạt động. Nếu AUDIT_LOG_PATH không ghi được, report đã tạo không bị loại; message Monitoring nêu lỗi và workflow completed được chuyển thành degraded.

## 2.8. Phạm vi của các endpoint

Endpoint /api/report là lối vào quy trình bảy agent được mô tả trong chương này. Nó yêu cầu chọn cohort và feature đúng schema, có thể thêm câu hỏi hoặc glucose. Kết quả thể hiện đầy đủ prediction, luật, evidence, explanation và metadata. Đây là endpoint cần dùng để minh họa tích hợp theo tài liệu kiến trúc.

Endpoint /api/chat giữ luồng hỏi đáp tri thức của phiên bản trước. Trace có các vai trò Safety, Retrieval, Policy, Education và Critic; policy mô phỏng chọn cách trình bày. Chat không yêu cầu vector feature và không chạy DL dự đoán trong mỗi câu hỏi. Endpoint /api/predict chỉ phục vụ suy luận model và trace rút gọn; nó không tạo báo cáo KG/RAG tổng hợp. Ba endpoint dùng chung một số tài nguyên nhưng không có cùng hợp đồng đầu ra hoặc cùng số bước. Mã ánh xạ nằm trong app/main.py và app/agents/coordinator.py.

GET /api/capabilities đọc registry tại app/capabilities.py: phương pháp, vai trò, source symbol, endpoint, demo và giới hạn. implemented cho biết có mã; configured cho biết cấu hình phụ thuộc; feature_usage của từng report mới cho biết phần đã thực sự chạy. Vì vậy, registry không biến cấu hình FPT hoặc Neo4j thành bằng chứng gọi thành công.

## 2.9. Ranh giới dữ liệu và bảo mật

API không nhận SQL/Cypher tùy ý. Query graph dùng tham số. Corpus ingest trước, không tải URL tùy ý từ request. Nội dung nguồn là dữ liệu hỗ trợ, không được thực thi như chỉ thị.

FPT key và Neo4j password chỉ ở môi trường/.env bị ignore. Raw/database chứa patient_nbr phục vụ split không vào Git/image/ZIP. Artifact state_dict nạp weights_only=True; không pickle toàn bộ object mô hình. Audit ra file chỉ bật khi cấu hình rõ đường dẫn.

## 2.10. Quyền ghi trạng thái và điều khiển nội bộ bản 2.1

Outer workflow giữ bảy vai trò và tám message thông thường. Hai controller mới nằm trong KG/RAG và Explanation, không làm tăng số agent core. Quyền đọc/ghi dưới đây được công bố trong AGENTS của registry; đây là phân trách nhiệm trong mã, chưa là cơ chế phân quyền hệ điều hành.

| Vai trò | Đọc | Ghi / quyết định | Công cụ chính |
|---|---|---|---|
| Data | Dataset, feature, glucose/unit | Validated, thứ tự feature; cho phép hoặc dừng | validate_features |
| DL | Feature hợp lệ, serving artifact | Prediction hoặc dependency_error | Predictor.predict |
| Rule | Câu hỏi, prediction, glucose/unit | Rules; cho truy xuất hoặc safety_override | check |
| KG/RAG | Câu hỏi, corpus, ontology | Evidence/retrieval; nhận, thử tiếp hoặc từ chối | AdaptiveRetrieval.run |
| Coordinator | Request và output trung gian | Request_id, status, messages, report | ReportWorkflow.run |
| Explanation | Question, prediction, rules, evidence | Explanation/quality; đạt, sửa hoặc từ chối | generate, review_and_revise |
| Monitoring | Metadata thực thi | Audit; không ghi feature/câu hỏi/key | MonitoringAgent.run |

![Hai controller nội bộ hữu hạn: truy xuất và kiểm duyệt câu trả lời](figures/agent-controls.png)

Ngân sách là tối đa ba lần gọi retrieve và tối đa một lần sửa extractive, không phải số lượt bắt buộc. Nếu lượt đầu đủ điều kiện thì dừng. Review không gọi LLM lần hai. decision_trace giữ hành động/lý do của các vai trò; retrieval.attempts và quality.attempts giải thích các quyết định bên trong. Quyết định nội bộ được tự động hóa trong phạm vi rõ, chưa là lập kế hoạch mở hoặc tác tử phân tán tự chủ.

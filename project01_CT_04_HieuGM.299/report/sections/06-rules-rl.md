# CHƯƠNG 6. LUẬT, BÁO CÁO CÓ CẤU TRÚC VÀ RL MÔ PHỎNG

## 6.1. Vai trò của Rule-Based Agent

Rule Agent áp dụng điều kiện minh bạch và trả rule_id, severity, reason, source. Nó tách cảnh báo an toàn khỏi score DL và khỏi nội dung RAG. Điều kiện nhập glucose kiểm kiểu, số hữu hạn, đơn vị và miền. Chuỗi số, boolean, NaN/Infinity hoặc giá trị ngoài miền không được im lặng ép thành input hợp lệ.

Luật cảnh báo xử lý tín hiệu nguy cấp và ranh giới thuốc/liều. Nội dung này phục vụ minh họa nghiên cứu, cần người có chuyên môn duyệt trước dùng thật. Người xem phải đọc lý do và nguồn của luật; không xem luật là chẩn đoán đã xác nhận.

## 6.2. Review flags vận hành

Nếu score cách threshold mô hình không quá 0,05, hệ thống gắn near_model_threshold để lưu ý độ ổn định phân lớp. Đây là quy tắc vận hành, không là ngưỡng y khoa. Nó không tương đương uncertainty Bayesian hoặc khoảng tin cậy.

Nếu model trả nhãn nghiên cứu dương, hệ thống gắn positive_research_label và nhắc đọc nhiệm vụ/giới hạn. Nhãn dương Hospital chỉ liên quan tái nhập viện, không thể diễn giải là phát hiện bệnh mới. Nếu thiếu evidence hoặc knowledge dependency degraded, report bổ sung review flag tương ứng.

## 6.3. Báo cáo và bất định

Báo cáo có prediction, rule_results, retrieved_evidence, explanation, sources, review_flags, limitations và clinical_use=False. Thiết kế giữ riêng các luồng thông tin để không trộn một đoạn giáo dục với nhận định về cá nhân.

Bất định gồm độ nhạy gần threshold, giới hạn quần thể, dữ liệu nhỏ, sigmoid chưa hiệu chuẩn và dependency dự phòng. Ba seed benchmark đo biến thiên khởi tạo trên cùng split, không cung cấp interval cho score của một người. Báo cáo không tạo con số confidence khi chưa có phép ước lượng tương ứng.

Kết quả model và rule có thể khác mục đích: một score thấp không bác bỏ cảnh báo triệu chứng, tài liệu tổng quát không xác nhận feature bệnh nhân. Xung đột hoặc thiếu bằng chứng cần người có chuyên môn xem lại; không lấy biểu quyết giữa ba nguồn để kết luận bệnh. Cảnh báo có ưu tiên trình bày trước giải thích thông thường.

## 6.4. Explanation Agent và việc xem nguồn

Explanation nhận output đã tổng hợp, không tự sửa model hoặc threshold. FPT được dùng khi cấu hình hợp lệ và phản hồi qua kiểm citation; template được dùng khi thiếu cấu hình hoặc lỗi. Trạng thái generation cho biết đường đi thực tế.

Người dùng có thể xem source title, URL và page của PDF để kiểm chứng. Thẻ biên soạn mang source_type khác tài liệu tải thật. Đường graph cho biết concept và evidence, không tự tạo một chuỗi suy luận lâm sàng đáng tin cậy cho mọi người.

## 6.5. Monitoring và audit

Metadata audit gồm request_id, status, duration_ms, danh sách agent/status/model_version/elapsed_ms. Mặc định không ghi file; AUDIT_LOG_PATH bật ghi JSONL metadata. Audit không ghi patient feature, câu hỏi hoặc API key. Trace trong phản hồi vẫn giúp xem agent nào chạy, bị bỏ qua hoặc degraded.

Không công bố log có ID bệnh nhân. Cấu hình logger của hạ tầng là phạm vi riêng cần rà trước khi mở cho sử dụng thật. Bài hiện chưa có hệ phân quyền bệnh viện, quản trị hồ sơ hoặc lưu trữ dữ liệu khám chữa bệnh.

## 6.6. RL là phần mở rộng tùy chọn

Đặc tả cho phép bỏ RL trong bản đầu. Project giữ mô-đun Q-learning mô phỏng từ phiên bản trước để minh họa chọn kiểu trình bày. Đây là one-step contextual bandit với gamma=0, bốn trạng thái và ba hành động; không có bệnh nhân thật hay phần thưởng sức khỏe.

Thực nghiệm lịch sử dùng seed 299, 4.000 episode. Greedy policy khớp rubric ở 4/4 state; reward trung bình 500 episode cuối 0,844. Những số này chỉ phản ánh rubric synthetic đã thiết kế. Không gọi là hiệu quả điều trị, cá nhân hóa thuốc hoặc giảm biến chứng.

Core bảy agent không phụ thuộc RL để dự đoán hoặc truy xuất. Nếu mở rộng RL sau này, cần mô phỏng riêng và đánh giá chính sách có ràng buộc trước mọi ứng dụng thực; không cho policy tự kê đơn, đổi liều hoặc điều khiển chăm sóc người thật.

Ánh xạ phần mở rộng vào MDP của đặc tả: trạng thái s là tổ hợp có/không evidence và yêu cầu ngắn/chi tiết, tạo bốn trạng thái 0-3. Action là abstain, brief hoặc detail. Mỗi episode lấy một trạng thái rồi kết thúc sau một action; vì gamma=0, bài hiện tại là bandit theo ngữ cảnh, chưa học chiến lược chăm sóc nhiều bước. Reward bằng +1 khi khớp rubric, -1 khi không khớp, và -3 nếu trả lời khi không có evidence. Các giá trị này do tác giả đặt để minh họa.

$$Q(s,a)\leftarrow Q(s,a)+\alpha\,[r-Q(s,a)]$$

scripts/train-policy.py dùng alpha=0,15 và epsilon=max(0,08; 1-episode/3000). Target greedy cho bốn state là abstain, abstain, brief, detail. app/agents/policy.py chỉ đọc bảng Q khi chọn cách trình bày cho chat. Luồng /api/report không gọi policy này. Chuyển trạng thái kết thúc một bước và reward nhân tạo giải thích vì sao kết quả 4/4 không thể được diễn giải thành chính sách tối ưu cho một bài toán y tế thật.

## 6.7. Kiểm chứng toàn luồng bằng request chạy thật

<!-- API_CASES_START -->

Lượt chạy cục bộ ghi tại 2026-11-13T11:04:29.232131+07:00; 10/10 ca đạt kỳ vọng chức năng. Dữ liệu là giá trị mặc định minh họa theo schema, không là hồ sơ bệnh nhân. Mô hình dùng trọng số thật; tri thức dùng SQLite cache và giải thích bằng template. Lượt này không gọi FPT hoặc Neo4j ngoài, không đo SLA.

| Ca | HTTP | Trạng thái | Message | Generation |
|---|---:|---|---:|---|
| cdc-normal | 200 | degraded | 8 | template |
| hospital-normal | 200 | degraded | 8 | template |
| pima-normal | 200 | degraded | 8 | template |
| early-normal | 200 | degraded | 8 | template |
| missing-feature | 422 | validation_error | 3 | không tạo report |
| emergency | 200 | emergency | 8 | safety_rule |
| medication-boundary | 200 | boundary | 8 | safety_rule |
| low-glucose | 200 | urgent | 8 | safety_rule |
| adaptive-rewrite | 200 | degraded | 8 | template |
| unrelated-query | 200 | degraded | 8 | template |

### 6.7.1. Một request Pima xuyên suốt

Request sau gửi đến POST /api/report. Các tên trường giữ nguyên để có thể chạy lại:

```json
{
  "dataset": "pima",
  "features": {
    "Pregnancies": 1,
    "Glucose": 120,
    "BloodPressure": 72,
    "SkinThickness": 20,
    "Insulin": 80,
    "BMI": 28,
    "DiabetesPedigreeFunction": 0.5,
    "Age": 35
  },
  "question": "HbA1c phản ánh điều gì?"
}
```

Request_id của lần ghi: `a15ba8f9-3106-4e50-82a3-4b9be3ff751f`. Score thực là 0,3034, ngưỡng validation 0,3691, nhãn nghiên cứu 0; phiên bản 2.0-db-benchmark. Đây là output của vector minh họa, không là xác suất bệnh cá nhân.

| Thứ tự / agent | Status | Mốc elapsed_ms | duration_ms riêng |
|---|---|---:|---:|
| 1. CoordinatorAgent | started | 0.02 | 0.0 |
| 2. PatientDataAgent | ok | 0.08 | 0.024 |
| 3. DLPredictionAgent | ok | 2.44 | 2.321 |
| 4. RuleBasedAgent | ok | 3.01 | 0.497 |
| 5. KGRAGAgent | degraded | 14.27 | 11.223 |
| 6. CoordinatorAgent | aggregated | 14.6 | 0.001 |
| 7. ExplanationAgent | llm_not_configured | 16.94 | 2.304 |
| 8. MonitoringAgent | ok | 17.08 | 0.015 |

### 6.7.2. Evidence, giải thích và cờ review

Một số evidence được trả trong đúng request trên:

| ID | Document / page | Nguồn |
|---|---|---|
| KB08 | WEB05 / - | [Ý nghĩa HbA1c](https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis) |
| KB07 | WEB05 / - | [Xét nghiệm chẩn đoán](https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis) |
| PDF01-P019-C001 | PDF01 / 19 | [Bộ Y tế — Hướng dẫn chẩn đoán và điều trị đái tháo đường típ 2 (2020), bản do Sở Y tế Đồng Nai đăng tải](https://syt.dongnai.gov.vn/vi/van-ban/detail/V-v-trien-khai-thuc-hien-Quyet-dinh-so-5481-QD-BYT-ngay-30-12-2020-cua-Bo-truong-Bo-Y-te-4905/?download=1&id=0) |

Các cờ review: knowledge_dependency_degraded. Trạng thái degraded phản ánh backend cache, không phải suy luận DL thất bại. conflicts.status=not_assessed cho biết chưa thực hiện kiểm mâu thuẫn ngữ nghĩa tổng quát. clinical_use=False và uncertainty.score_calibrated=False được giữ trong report.

File results/agent-upgrade-cases.json lưu toàn bộ input minh họa, response, trace, nguồn, hash bốn trọng số và môi trường chạy. Request_id/thời gian ở lần tái chạy sẽ khác; cần so sánh hành vi và schema thay vì yêu cầu UUID giống nhau.

### 6.7.3. Hai đường rẽ quan trọng

Ca missing-feature trả HTTP 422, chỉ có Coordinator → Patient Data → Monitoring. Không có message DL và report=null: luồng không tạo dự đoán khi vector chưa hợp lệ.

Các ca emergency, medication-boundary và low-glucose dùng safety_rule; KG có status skipped. DL đã chạy trước Rule theo thứ tự hiện tại, nhưng score không ghi đè cảnh báo. Explanation dùng thông điệp luật mà không gọi LLM. Các ca này minh họa điều phối; không là đánh giá độ nhạy/đặc hiệu lâm sàng của bộ luật.

<!-- API_CASES_END -->

## 6.8. Kiểm duyệt sau sinh và sửa hữu hạn

Bản 2.1 thêm app/knowledge/review.py. ExplanationAgent.run gọi generator một lần, sau đó review_and_revise kiểm output. Các phép kiểm gồm: cấu trúc; citation inline khớp danh sách; metadata nguồn khớp evidence; không có URL mới; một số mẫu khẳng định chẩn đoán cá nhân hoặc chỉ dẫn liều thuốc; disclaimer; và mức giao token với văn bản nguồn. Nội dung disclaimer chung được dùng cả trong prompt và template.

Lexical_support_ratio là tỷ lệ token nội dung còn lại xuất hiện trong evidence sau chuẩn hóa/lọc từ dừng; ngưỡng hiện tại là 0,35. Nó chỉ phát hiện một số nội dung ít liên hệ từ vựng, không hiểu đầy đủ ngữ nghĩa, tính đúng của con số, mâu thuẫn hoặc suy luận y khoa. Regex chẩn đoán/liều có xử lý phủ định/điều kiện cục bộ nhưng vẫn có thể bỏ sót hoặc bắt nhầm. Kết quả passed chỉ nghĩa đạt các phép kiểm đã định nghĩa.

Nếu bản nháp không đạt, controller sửa tối đa một lần: lấy tối đa hai đoạn trích từ evidence, bỏ các đoạn bị mẫu luật chặn hoặc chứa tham chiếu không phù hợp, thêm citation/disclaimer rồi kiểm lại. Nếu không có đoạn phù hợp hoặc bản sửa vẫn không đạt, trả refusal thay vì xuất bản sửa lỗi. Không gọi LLM thêm để sửa. Safety override của Rule đi đường safety_rule với nhãn review riêng; không yêu cầu evidence hoặc gọi LLM trong nhánh này.

| Trường quan sát | Ý nghĩa |
|---|---|
| quality.initial_passed / final_passed | Phân biệt bản nháp và bản cuối |
| quality.attempts / initial_issue_codes | Lịch sử verdict/lý do; không lưu nguyên văn draft bị loại |
| revision_count / max_revisions | Số lần sửa thực tế và trần một lần |
| original_generation / provider_attempted | Giữ đường đi gốc dù kết quả cuối đã chuyển template |
| feature_usage.fpt_called / final_generation | Phân biệt đã gọi FPT với cách tạo output cuối |

Các ca cố tình đưa draft sai citation, khẳng định bệnh hoặc nêu liều trong tests/test_output_review.py là đầu vào kiểm thử có nhãn, không được gán là câu trả lời FPT thật. Chúng kiểm cơ chế chặn/sửa và giới hạn số lượt. Reviewer thuộc Explanation, không phải agent LLM Critic thứ tám hoặc bộ xác thực lâm sàng.

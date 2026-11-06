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

# CHƯƠNG 2. HỆ ĐA AGENT VÀ KIẾN TRÚC

## 2.1. Agent và hệ đa Agent

Agent là một thành phần nhận quan sát, duy trì trạng thái liên quan và chọn hành động để thực hiện một mục tiêu trong môi trường. Trong project, môi trường là request hỏi đáp hoặc phân tích dữ liệu; hành động là kiểm tra luật, truy xuất thẻ, chọn cách trình bày, chạy mô hình hoặc xác minh cấu trúc dẫn nguồn. Tính tự chủ của các vai trò được giới hạn bằng nhiệm vụ và điều kiện chuyển tiếp rõ ràng.

Hệ đa Agent tổ chức nhiều vai trò chuyên trách cùng giải quyết một nhiệm vụ chung. Cách tổ chức này giúp phân tách mục tiêu: SafetyAgent ưu tiên cảnh báo, RetrievalAgent ưu tiên bằng chứng liên quan, PredictionAgent ưu tiên suy luận đúng mô hình, còn CriticAgent kiểm tra cấu trúc và phạm vi đầu ra. Coordinator quyết định luồng chuyển thông điệp và dừng khi đã có kết quả.

Hiện thực của project là điều phối xác định trong một tiến trình Python, không phải mạng Agent độc lập phân tán hoặc LLM tự lập kế hoạch. Các vai trò được biểu diễn qua các hàm công cụ và thông điệp trong context. Việc tách vai trò có lợi cho truy vết và kiểm thử, nhưng bản thân số lượng tên Agent không chứng minh cải thiện chất lượng so với một pipeline tương đương. Đánh giá lợi ích nhân quả của MAS cần ablation với cùng công cụ, dữ liệu và ngân sách.

## 2.2. Vai trò và giao thức phối hợp

| Vai trò | Đầu vào | Hành động và đầu ra |
|---|---|---|
| SafetyAgent | Câu hỏi, glucose tùy chọn, đơn vị | Phát hiện cảnh báo/ngoài phạm vi; có thể dừng luồng |
| DataAgent | Tên dataset, dictionary đặc trưng | Kiểm tra đủ trường, kiểu số, miền và mã hóa |
| PredictionAgent | Vector đã xác thực | Chuẩn hóa theo train và suy luận MLP |
| RetrievalAgent | Câu hỏi tiếng Việt | Trả top-k thẻ, điểm và nguồn |
| PolicyAgent | Có/không bằng chứng, yêu cầu độ chi tiết | Chọn abstain/brief/detail từ Q-table |
| EducationAgent | Thẻ đã chọn, kiểu trình bày | Ghép văn bản của một hoặc hai thẻ, giữ ID |
| CriticAgent | Dự thảo hoặc điểm mô hình | Kiểm tra ID/URL hoặc nhắc đúng ý nghĩa điểm |
| Coordinator | Request và kết quả các vai trò | Điều phối, giới hạn bước và trả trace |

Thông điệp có các trường sender, receiver, kind, detail và elapsed_ms. Context được tạo mới cho từng request, chứa câu hỏi trong bộ nhớ và danh sách trace; mỗi trace có tối đa tám thông điệp. Không có vòng lặp Agent không giới hạn. Nếu vượt ngân sách, hệ thống phát sinh lỗi thay vì tiếp tục gọi công cụ.

<!-- pagebreak -->

## 2.3. Kiến trúc tổng quan

![Kiến trúc DiaCare: nhánh mô hình và nhánh tri thức cùng đi qua điều phối và kiểm tra](figures/architecture.png)

Lớp giao diện dùng HTML, CSS và JavaScript, trao đổi JSON với FastAPI. API khởi tạo KB, policy và metadata mô hình khi ứng dụng bắt đầu. Dữ liệu huấn luyện không nằm trong image triển khai; suy luận chỉ cần hai state_dict, thống kê scaler và metadata. Cơ sở tri thức được đóng gói từ JSON có kiểm soát phiên bản rồi ghi vào SQLite ở thư mục runtime.

Nhánh hỏi đáp đi qua SafetyAgent trước. Nếu có cảnh báo khẩn hoặc yêu cầu kê đơn, Coordinator trả lời theo quy tắc và dẫn nguồn. Nếu được phép, RetrievalAgent tạo vector câu hỏi, tìm bằng chứng và chuyển cho PolicyAgent. EducationAgent ghép nội dung trích xuất; CriticAgent chỉ chấp nhận các mã thẻ đã có và liên kết HTTPS. Nhánh này không gọi LLM và không phát sinh kiến thức mới ngoài thẻ đã chọn.

Nhánh phân tích dùng DataAgent xác thực schema rồi gọi PredictionAgent. Vector được chuẩn hóa bằng mean/std fit trên train, qua mạng và sigmoid để thu điểm. Ngưỡng phân loại đã được chọn bằng validation trong quá trình huấn luyện. CriticAgent gắn lại ý nghĩa nhiệm vụ và giới hạn sử dụng. Điểm của nhánh CDC và Hospital không được gộp thành một điểm nguy cơ chung.

## 2.4. Thiết kế cơ sở dữ liệu và tài nguyên

Bảng SQLite cards gồm id làm khóa chính, title, content và url. Mỗi lần khởi động, nội dung được đồng bộ lại từ cards.json; kết nối được đóng sau khi ghi hoặc đọc để tránh giữ khóa file trên Windows. Vector TF-IDF được xây dựng trong RAM từ cùng danh sách thẻ, nên ID truy xuất và bản ghi DB có thể đối chiếu được.

Tài nguyên mô hình được cache trong tiến trình. Đối tượng Predictor tải state_dict với weights_only=True, đặt model.eval và chạy trong inference_mode. Thống kê scaler nằm trong metadata JSON, tránh pickle đối tượng tiền xử lý. Predictor kiểm tra toàn bộ đặc trưng; không âm thầm bổ sung các trường người dùng chưa nhập. Các giá trị mặc định trên giao diện là dữ liệu minh họa thao tác và có thông báo rõ.

## 2.5. Thiết kế lỗi và quyền riêng tư

API từ chối dataset không hợp lệ, trường thừa/thiếu, số ngoài khoảng, mã phân loại không nguyên, kiểu boolean/string và giá trị NaN/Infinity. Phản hồi lỗi validation chỉ nêu vị trí và loại lỗi, không phản chiếu nguyên văn dữ liệu sức khỏe. JavaScript hiển thị đầu ra bằng textContent, tránh diễn dịch câu hỏi thành HTML.

Ứng dụng không có chức năng quản lý hồ sơ bệnh nhân, đăng nhập, điều trị hoặc ghi đơn. Khi triển khai công khai, cần đặt sau HTTPS của nhà cung cấp, bổ sung giới hạn lưu lượng và theo dõi tải nếu mở rộng sử dụng. Đó là yêu cầu vận hành tiếp theo, không phải tính năng đã kiểm chứng trong demo cục bộ.

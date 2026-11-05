# CHƯƠNG 7. KIỂM THỬ, DEMO VÀ TRIỂN KHAI

## 7.1. Kiểm thử phần mềm

Bộ pytest gồm 55 trường hợp và chạy với hai mô hình đã huấn luyện thật. Các nhóm kiểm tra gồm truy xuất, thông điệp Agent, giới hạn bước, nguồn trích dẫn, schema mô hình, nạp trọng số mới, tính ổn định score, điều kiện cảnh báo và các phản hồi HTTP lỗi. Không dùng mock mô hình hoặc thay mạng bằng hàm điểm cố định để làm test đạt.

Trong quá trình kiểm thử, ba lỗi kỹ thuật đã được phát hiện và sửa. Kết nối SQLite không tự đóng khi chỉ dùng context manager của sqlite3 gây khóa file trên Windows; bản sửa dùng closing và commit rõ ràng. Pydantic có thể ép boolean hoặc chuỗi số sang float trước khi Predictor nhận dữ liệu; bản sửa dùng strict numeric types. Phản hồi lỗi chứa NaN/Infinity có thể lỗi serialize JSON; handler mới chỉ trả vị trí, loại và thông điệp lỗi, không phản chiếu input.

Lượt kiểm tra cuối đạt 55/55, còn một cảnh báo deprecation của thư viện TestClient không làm test thất bại. Kiểm thử mô hình riêng đối chiếu score từ state_dict với dự đoán test đã lưu, kiểm tra scaler dùng đúng train và xác nhận tập nhóm không giao nhau. Thành công các test là bằng chứng triển khai đúng hợp đồng phần mềm ở những trường hợp đã xét, không bảo đảm mọi cách diễn đạt hoặc tình huống y tế đều được xử lý đúng.

## 7.2. Kịch bản demo

Kịch bản thứ nhất mở trang Trợ lý kiến thức và hỏi “HbA1c là gì?”. Người xem kiểm tra phần trả lời, ID nguồn, URL NIDDK và trace qua các vai trò. Tiếp theo thử câu hỏi ngoài chủ đề để quan sát insufficient_evidence, rồi yêu cầu kê đơn để thấy boundary và lý do dừng.

Kịch bản thứ hai nhập glucose theo mg/dL hoặc mmol/L cùng câu hỏi giáo dục, quan sát quy tắc cảnh báo nếu dưới ngưỡng. Có thể dùng tình huống thử nghiệm có mô tả dấu hiệu nguy hiểm để thấy safety_override chạy trước policy. Đây là dữ liệu kiểm thử giao diện, không phải thông tin của một người bệnh thật.

Kịch bản thứ ba vào Phân tích dữ liệu, chọn CDC, kiểm tra 21 trường và cách mã hóa rồi chạy MLP. Đầu ra gồm risk_score, threshold, predicted_class, label_semantics và trace. Đổi sang Hospital để quan sát schema 10 biến và nhãn tái nhập viện; không diễn giải score Hospital thành mức độ tiểu đường. Cuối cùng xóa một trường hoặc nhập giá trị ngoài miền qua API để xác nhận HTTP422.

## 7.3. Giao diện và API

Giao diện có ba khu vực: Trợ lý kiến thức, Phân tích dữ liệu và Kho tri thức. Menu bên cạnh thể hiện thông tin sinh viên. Các thẻ nguồn giữ liên kết gốc; khối trace mô tả từng bước thay vì chỉ hiện tên Agent. CSS có bố cục thay đổi theo chiều rộng, form từ ba cột xuống một cột khi màn hình nhỏ.

| Endpoint | Phương thức | Mục đích |
|---|---|---|
| / | GET | Giao diện demo |
| /health | GET | Tình trạng sẵn sàng, mô hình và kiểm kê KB |
| /api/catalog | GET | Metadata, schema và thông tin bộ bài |
| /api/knowledge | GET | Các thẻ tri thức và nguồn |
| /api/chat | POST | Hỏi đáp, glucose tùy chọn, đơn vị |
| /api/predict | POST | Phân loại theo dataset và vector đầu vào |
| /api/results | GET | Một số kết quả tổng hợp được phép công bố |
| /docs | GET | Tài liệu tương tác OpenAPI |

Các endpoint và frontend được phục vụ cùng origin; JavaScript không nhúng secret, không gửi thông tin sang dịch vụ LLM. App không yêu cầu mở dữ liệu cá nhân để chạy demo. Bản giao diện desktop được xem trực tiếp trong Edge, còn kiểm thử chức năng hệ thống được thực hiện bằng API. Chưa có đánh giá người dùng hoặc kiểm thử giao diện tự động trên mọi trình duyệt/thiết bị.

## 7.4. Đóng gói Docker

Dockerfile dựa trên Python3.12 slim và cài dependency có khóa phiên bản. Image chỉ sao chép app, models và results, không sao chép raw dataset hoặc các split dùng huấn luyện. Ứng dụng chạy bằng user không phải root, một worker Uvicorn, đọc cổng từ PORT và đặt SQLite ở thư mục runtime có quyền ghi. Không cần GPU, khóa API hoặc train lại lúc khởi động.

Từ thư mục project, chạy các lệnh:

```powershell
docker build -t diacare-hieugm299:1.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 diacare-hieugm299:1.0
python scripts/verify-deployment.py --url http://127.0.0.1:8000
```

Một worker giúp giảm việc nhân đôi model/index. Số thread CPU được giới hạn trong container. SQLite được dựng lại từ JSON nguồn nên không cần persistent disk để giữ KB. Cách này phù hợp demo có nội dung tĩnh; không phải thiết kế lưu hồ sơ người bệnh hoặc đồng bộ chỉnh sửa KB giữa nhiều replica.

## 7.5. Triển khai cloud và giới hạn bằng chứng

Gói có render.yaml với runtime Docker, healthCheckPath /health và biến APP_DATA_DIR. Cấu hình dành cho một repository riêng chứa nội dung project ở root. Với monorepo cần đặt Root Directory tương ứng. Quy trình tạo service, kiểm tra tài nguyên và lệnh xác minh endpoint được ghi trong DEPLOY.md, dựa trên tài liệu Blueprint chính thức của Render.

Bản Docker đã được build từ đúng Dockerfile và chạy trên Docker Engine 29.9.2 trong môi trường Linux WSL2 riêng. Cả 13 kiểm tra HTTP đạt, gồm frontend/tài nguyên tĩnh, kiểm kê KB, suy luận hai mô hình, từ chối input thiếu, trả lời có nguồn, ưu tiên cảnh báo và xử lý NaN. Container báo healthy; một quan sát lúc nhàn rỗi sau kiểm tra ghi khoảng 254,9 MiB RAM, không phải benchmark tải. docker-verification.json giữ thời điểm, image ID và từng kết quả.

Cloud là bước triển khai riêng: cần tài khoản/kết nối repository và phải kiểm tra endpoint sau deploy. Project chưa có URLcloud công khai được tạo trong phiên làm việc này; không dùng một URL dự kiến làm bằng chứng hệ thống đã phục vụ Internet.

## 7.6. Kết luận và hướng phát triển

Project hiện thực đầy đủ luồng dữ liệu lớn đến mô hình đã huấn luyện, suy luận có schema, KB có nguồn, trả lời trích xuất, điều phối đa vai trò, Rule và minh họa RL. Các kết quả cho thấy MLP có thể học tín hiệu trong hai nhiệm vụ, nhưng mức phân biệt tái nhập viện còn hạn chế; pipeline hỏi đáp vẫn có thể chọn nguồn chưa cụ thể nhất.

Hướng tiếp theo là đánh giá nhiều seed, khoảng tin cậy theo người, calibration và fairness; mở rộng đặc trưng Hospital có kiểm soát thời điểm quan sát; xin quyền dùng và kiểm định trên dữ liệu Việt Nam. Với KB cần rà soát chuyên môn, mở rộng bộ câu hỏi độc lập và kiểm tra phủ định, đa bệnh, mức độ cụ thể. Tích hợp LLM chỉ nên thực hiện sau khi có giao thức kiểm tra claim–citation và đo riêng chất lượng sinh, không suy từ kết quả trích xuất hiện tại.

Ứng dụng được bàn giao ở mức demo học tập có thể chạy lại, không tự nhận là thiết bị y tế, công cụ kê đơn hoặc hệ thống quản lý điều trị đã được xác thực. Mọi mở rộng ứng dụng thực tế cần quy trình đánh giá phù hợp với dữ liệu, người dùng và mục đích triển khai.

# CHƯƠNG 1. GIỚI THIỆU ĐỀ TÀI

## 1.1. Bối cảnh và bài toán

Thông tin về đái tháo đường nằm ở nhiều nguồn: hồ sơ khám chữa bệnh, khảo sát sức khỏe, hướng dẫn chuyên môn và tài liệu giáo dục người bệnh. Một hệ thống chỉ đưa ra điểm dự đoán sẽ khó giải thích điểm đó có ý nghĩa gì. Một chatbot chỉ trả lời bằng văn bản cũng không tự bảo đảm đã dùng đúng nguồn hoặc nhận biết trường hợp ngoài phạm vi. Đề tài kết hợp mô hình học sâu, cơ sở tri thức và các vai trò Agent để mỗi thành phần thực hiện một nhiệm vụ có thể kiểm tra.

Project xây dựng DiaCare MAS, ứng dụng học tập tiếng Việt với hai chức năng chính. Chức năng hỏi đáp truy xuất thông tin từ kho tri thức có nguồn. Chức năng phân tích tiếp nhận bộ biến đầu vào theo đúng schema của một trong hai dataset, chạy MLP đã huấn luyện và hiển thị ý nghĩa nhãn, điểm mô hình, ngưỡng cùng dấu vết xử lý. Các cảnh báo từ quy tắc được xử lý trước nhánh hỏi đáp thông thường.

Hai nguồn dữ liệu lớn được sử dụng là CDC Diabetes Health Indicators với 253.680 bản ghi khảo sát và Diabetes 130-US Hospitals với 101.766 lượt điều trị nội trú. Chúng không phải dữ liệu Việt Nam và không cùng nhãn. Bộ thứ nhất phân loại trạng thái tiền đái tháo đường/đái tháo đường được ghi nhận trong khảo sát; bộ thứ hai phân loại tái nhập viện trong 30 ngày ở các lượt điều trị của người bệnh tiểu đường. Do vậy, thực nghiệm so sánh MLP với baseline trong từng dataset, không coi hai tập là kiểm định ngoại viện của nhau.

## 1.2. Mục tiêu

Mục tiêu kỹ thuật thứ nhất là hình thành quy trình dữ liệu có nguồn, chống rò rỉ, huấn luyện thật và lưu trọng số để suy luận. Mục tiêu thứ hai là tổ chức KB tiếng Việt với mã thẻ và liên kết gốc, kết hợp truy xuất với tạo câu trả lời trích xuất. Mục tiêu thứ ba là hiện thực điều phối đa vai trò có thông điệp, quy tắc ưu tiên và giới hạn bước. Mục tiêu thứ tư là đóng gói API và giao diện thành một ứng dụng có thể chạy độc lập bằng Docker.

Mục tiêu đánh giá gồm đo phân loại trên tập kiểm tra giữ riêng; kiểm tra truy xuất và khả năng từ chối bằng bộ câu hỏi có nhãn; kiểm thử dữ liệu nhập, dẫn nguồn, cảnh báo và suy luận từ trọng số thật. Thành công về kỹ thuật không đồng nghĩa hiệu quả lâm sàng. Dữ liệu lịch sử của Hoa Kỳ và bộ câu hỏi tự biên soạn chỉ hỗ trợ đánh giá trong phạm vi nghiên cứu của project.

## 1.3. Sản phẩm và phạm vi

| Sản phẩm | Nội dung thực hiện |
|---|---|
| Dữ liệu | Hai dataset công khai, nguồn và hash, báo cáo làm sạch/chia tập |
| Deep Learning | Hai MLP ba lớp ẩn, trọng số đã huấn luyện, Logistic và majority baseline |
| Cơ sở tri thức | 24 thẻ tiếng Việt, 19 URL nguồn, SQLite |
| Truy xuất và trả lời | TF-IDF, top-k, trả lời trích xuất có ID nguồn |
| Multi-Agent | Bảy vai trò chuyên trách cùng Coordinator, trace có giới hạn |
| Rule và RL | Cảnh báo/giới hạn theo luật; Q-learning một bước cho cách trình bày |
| Demo | FastAPI, giao diện web responsive, Dockerfile, cấu hình Render |
| Bằng chứng | JSON/NPZ kết quả, biểu đồ, kiểm thử và hướng dẫn tái lập |

Hệ thống không thu thập họ tên người bệnh, mã hồ sơ, địa chỉ hoặc số điện thoại. Các câu hỏi và giá trị nhập chỉ đi qua bộ nhớ của request. SQLite dùng để tổ chức thẻ tri thức, không lưu nội dung hỏi đáp hay hồ sơ sức khỏe. Mã nguồn không chứa khóa API và không cần dịch vụ LLM trả phí để hoạt động mặc định.

## 1.4. Cấu trúc báo cáo

Báo cáo đi từ cơ sở Agent và kiến trúc, tới thiết kế dữ liệu, Deep Learning, KB/truy xuất, điều phối và Rule/RL. Phần thực nghiệm trình bày số đo và lỗi còn tồn tại. Phần triển khai ghi lệnh chạy cùng ranh giới giữa bản Docker đã kiểm tra và cấu hình cloud cần tài khoản thực. Phụ lục cung cấp schema, API và kịch bản demo.

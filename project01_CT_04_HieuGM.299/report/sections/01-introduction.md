# CHƯƠNG 1. BÀI TOÁN VÀ PHẠM VI THỰC HIỆN

## 1.1. Mục tiêu của Project01

DiaCare là nguyên mẫu học thuật về hệ đa agent hỗ trợ tìm hiểu bệnh đái tháo đường. Đề tài kết hợp hai nhánh: Knowledge Base từ Web/PDF, Knowledge Graph và RAG; dữ liệu Diabetes trong cơ sở dữ liệu để huấn luyện, so sánh Deep Learning. Báo cáo trình bày kết quả thực nghiệm và cách các thành phần phối hợp thành ứng dụng.

Tài liệu project_architecture_multiagent_diabet_v1.pdf do giảng viên cung cấp định nghĩa bảy agent cốt lõi, giao tiếp có cấu trúc và quy trình tạo báo cáo. Đây là đặc tả kiến trúc; không quy định số bộ dữ liệu hoặc mô hình. Ma trận bốn cohort, sáu loại mô hình, ba seed là phần mở rộng thực nghiệm để có so sánh rõ ràng.

Đầu vào gồm cohort, đầy đủ đặc trưng đúng schema và câu hỏi tùy chọn. Đầu ra gồm dự đoán, kết quả luật, bằng chứng truy xuất, giải thích, nguồn và giới hạn. Các thành phần được giữ riêng để người xem biết thông tin đến từ mô hình, luật hay tài liệu.

## 1.2. Kết quả chính và cách đếm

| Thành phần | Kết quả và ý nghĩa |
|---|---|
| Dữ liệu học có giám sát | 4 cohort độc lập: CDC, Hospital, Pima, Early Stage |
| Loại mô hình | 6: Logistic Regression, Random Forest, Histogram Gradient Boosting, MLP hai tầng, MLP ba tầng, Residual MLP |
| Deep Learning | 3 kiến trúc nhiều tầng ẩn; seed là lần khởi tạo, không là loại kiến trúc mới |
| Ma trận | 4 × 6 = 24 tổ hợp dataset-model; mỗi tổ hợp 3 seed, tổng 72 lượt thật |
| Tái sử dụng | Giữ nguyên artifact CDC/Hospital đã triển khai; benchmark mới lưu riêng |
| Tri thức | Web, PDF tiếng Việt và thẻ có nguồn; KG được xây dựng mới và xuất Cypher |
| Điều phối | 7 agent cốt lõi, request_id xuyên suốt, trạng thái và phiên bản |
| Nâng cấp mã 2.1 | Retrieval tối đa 3 lượt, review/sửa tối đa 1 lần, timing từng call và registry công nghệ |
| Sản phẩm | Notebook độc lập, FastAPI, Docker, báo cáo, hướng dẫn bảo vệ |

Hai cohort nhỏ bổ sung giúp quan sát độ nhạy khởi tạo và tác động của dữ liệu ít. Chúng không làm tăng bằng chứng kiểm định của cùng một mô hình vì nhiệm vụ, feature và quần thể khác nhau. Không cộng mọi hàng thành một tập huấn luyện chung.

## 1.3. Điều chỉnh so với giả định của kiến trúc mẫu

Kiến trúc mẫu giả định đã có DL và Neo4j KG. Hai mô hình CDC/Hospital đã tồn tại; người học xác nhận chưa có Neo4j hoặc DB_diabet.cypher. Bài thực hiện tái sử dụng DL hiện có và xây KG từ đầu. Cypher bàn giao là kết quả mới của project, không là kho tri thức có sẵn của giảng viên.

Vinmec là nguồn bài viết sức khỏe cho KB/RAG. Bài viết công khai cung cấp văn bản, không cung cấp ma trận bệnh nhân có nhãn để thay cho bốn cohort. Không gọi bài viết là dữ liệu bệnh nhân Vinmec để train DL. PDF kiến trúc 11 trang không nêu bắt buộc dùng Vinmec; nguồn này được bổ sung theo trao đổi với người học.

## 1.4. Giới hạn sử dụng

Đây là nguyên mẫu giáo dục và nghiên cứu. Điểm sigmoid chưa được hiệu chuẩn thành xác suất bệnh cá nhân tại Việt Nam. Hospital dự đoán tái nhập viện dưới 30 ngày ở người có đái tháo đường; đây không phải phát hiện bệnh mới. CDC dùng nhãn gộp tiền đái tháo đường/đái tháo đường theo nguồn binary.

Hệ thống không chẩn đoán xác nhận, kê thuốc hoặc tự điều chỉnh liều. Luật minh họa cần chuyên gia thẩm định trước khi dùng thật. RL chỉ mô phỏng cách trình bày. Citation đúng ID hoặc URL chứng minh truy vết, chưa chứng minh mọi phát biểu được nguồn hỗ trợ đầy đủ.

## 1.5. Cách kiểm chứng

Các số liệu Chương 3-4 lấy từ artifact thực. 72 lượt nằm tại results/benchmark/full; manifest nguồn, SQL và split tại results/benchmark/database-manifest.json; hash bảo toàn mô hình cũ tại results/benchmark/legacy-preservation.json. Chương 5 mô tả corpus/graph/RAG; Chương 6 mô tả luật và báo cáo; Chương 7 hướng dẫn notebook, kiểm thử và triển khai.

Bằng chứng ngày 05/11/2026 là lịch sử phiên bản cũ. Kết quả kiểm tra của phiên bản nào chỉ áp dụng cho phiên bản đó. Trạng thái bản nâng cấp phải đối chiếu verification mới nhất, không suy ra từ việc URL cũ vẫn truy cập được.

Bản 2.1 thay đổi hành vi agent và mã giao diện, đồng thời đồng bộ notebook. Phần mới được kiểm qua agent-upgrade-cases.json, agent-upgrade-evaluation.json, agent-upgrade-pytest.json và notebook-agent-upgrade-verification.json. Registry /api/capabilities nối từng phương pháp với source symbol, endpoint và demo; feature_usage của request cho biết phần đã thực sự chạy.

## 1.6. Câu hỏi nghiên cứu và tiêu chí hoàn thành

Đề tài đặt ba câu hỏi. Thứ nhất, các mô hình Deep Learning có đem lại lợi ích so với baseline đơn giản trên cùng dữ liệu bảng hay không? Câu trả lời dựa trên bảng so sánh từng cohort ở Chương 4, bao gồm cả trường hợp baseline cạnh tranh hoặc tốt hơn. Thứ hai, có thể kết hợp dự đoán, luật và tài liệu mà vẫn truy vết được nguồn của từng kết quả không? Câu trả lời được thể hiện bằng hợp đồng agent, report có cấu trúc và một request chạy thật. Thứ ba, hệ thống phản ứng thế nào khi dữ liệu sai hoặc dịch vụ ngoài không khả dụng? Cần quan sát luồng dừng sớm, trạng thái degraded và đường fallback cụ thể.

| Mã | Yêu cầu thực hiện | Tiêu chí kiểm chứng |
|---|---|---|
| YC01 | DB cung cấp dữ liệu cho DL | Có bảng SQLite, SQL, split và nguồn/hash trong manifest |
| YC02 | So sánh mô hình có kiểm soát | Cùng cohort/split, fit tiền xử lý trên train, chọn bằng validation |
| YC03 | KB/KG và RAG có provenance | Chunk truy được URL/page; relation có evidence; phân biệt cache và Neo4j |
| YC04 | Phối hợp bảy agent | Một request_id, message có trạng thái, report tách các loại thông tin |
| YC05 | Xử lý lỗi có thể quan sát | Input sai dừng trước DL; dependency lỗi không tạo score giả |
| YC06 | Có sản phẩm chạy lại được | Notebook, API, Docker, hướng dẫn và hồ sơ kiểm chứng theo phiên bản |

Đây là tiêu chí kỹ thuật của nguyên mẫu. Một bộ kiểm chức năng đạt không trả lời được câu hỏi về hiệu quả điều trị, tính công bằng hoặc độ an toàn khi triển khai lâm sàng. Phần kết luận vì vậy tách đóng góp kỹ thuật khỏi các bằng chứng còn thiếu.

## 1.7. Người sử dụng và tình huống sử dụng

Người học có thể chọn một cohort, nhập vector minh họa và quan sát các agent tạo báo cáo. Người xem đánh giá cách kết nối các thành phần qua trace, không dùng các giá trị điền sẵn như hồ sơ của bản thân. Người kiểm tra kỹ thuật có thể mở nguồn, xem phiên bản model, chạy notebook hoặc đối chiếu API để tái lập kết quả.

Ba tình huống chính gồm: tạo báo cáo kết hợp model và câu hỏi; tra cứu tri thức có nguồn; xem bảng benchmark và graph. Luồng tạo báo cáo là điểm tích hợp chính của kiến trúc bảy agent. Luồng chat giữ cơ chế hỏi đáp của phiên bản trước; nó không thay thế bằng chứng cho luồng báo cáo. Không có đăng nhập bệnh viện, nhập hồ sơ định danh hoặc tích hợp bệnh án trong phạm vi bài.

## 1.8. Phương pháp và cách tổ chức báo cáo

Bài thực hiện theo thứ tự: xác định nhiệm vụ/nhãn; kiểm kê và làm sạch nguồn; lưu DB và cố định split; huấn luyện baseline cùng DL; xây corpus và graph; tích hợp agent qua hợp đồng; đánh giá từng thành phần và kiểm tra toàn luồng. Kết quả ML là thực nghiệm đã lưu ngày 06/11/2026. Các ví dụ bổ sung cho bản nộp lại ghi ngày chạy riêng, không đổi ngày hoặc trình bày các lượt cũ như thực nghiệm mới.

Chương 2 giải thích Agent/MAS và ánh xạ sang mã nguồn. Chương 3 mô tả dữ liệu, SQL và ngăn rò rỉ. Chương 4 trình bày mô hình, chỉ số và sai số. Chương 5 giải thích tri thức, graph, retrieval và generation. Chương 6 theo dõi báo cáo/luật/RL qua ví dụ cụ thể. Chương 7 tập hợp tái lập, kiểm chứng, giao diện, triển khai và kết luận. Phụ lục cung cấp bảng đối chiếu và điểm vào mã nguồn để người đọc kiểm tra độc lập.

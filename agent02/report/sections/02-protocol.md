## Thiết lập và quy trình thực nghiệm

### Phạm vi triển khai

Mã bắt đầu từ agent02_code.tex do đề cung cấp. Dù có đuôi .tex, nội dung file là Python. Thực nghiệm giữ nguyên môi trường, cập nhật Q, xử lý terminal và chuỗi RNG huấn luyện của mã này, tách thành các module nhỏ và bổ sung đo lường. Chỉ **một RL học với một đối thủ luật cố định**, không phải hai RL cùng học. Không dùng LLM hay GPU.

| Tham số | Giá trị |
|---|---|
| Huấn luyện mỗi lượt | 5.000 episode × 20 bước = 100.000 bước |
| Đánh giá mỗi policy | 500 episode × 20 bước = 10.000 bước |
| Alpha và gamma chuẩn | 0,10 và 0,90 |
| Exploration chuẩn | max(0,02; 0,20 × 0,995^episode), episode bắt đầu 0 |
| Giá gốc và chi phí | P = 10; C = 5; giảm giá chuẩn 20% |
| Seed baseline | Môi trường 42; RL 10042; đánh giá 500042 |
| Seed lặp độc lập | 11, 22, 33, 44, 55; seed RL = seed + 10000 |

### Các phép so sánh A đến E

A/B chạy baseline, lưu reward từng episode, tổng reward tích lũy, Q-table và đếm hành động. C so sánh alpha 0,01; 0,10; 0,50. D so sánh lịch chuẩn với epsilon cố định 0,05 và 0,30. C/D giữ các tham số còn lại và bộ seed như nhau. Mỗi cấu hình đều chạy đủ ngân sách, không chọn seed tốt nhất.

E đánh giá policy RL đã đóng băng trong trận RL-vs-rule; sau đó đánh giá policy luật trong trận rule-vs-rule riêng. Hai trận dùng cùng demand và cùng uniforms theo từng khách hàng. Lấy tổng các Bernoulli độc lập tạo đúng phân phối Binomial(N,p), đồng thời tránh việc nhánh lấy mẫu khác nhau làm lệch chuỗi demand giữa policy. Seed đánh giá bằng seed huấn luyện + 500000, RNG doanh số bằng seed đánh giá + 1000000.

Không cập nhật Q, không exploration trong đánh giá; tie chọn argmax chỉ số nhỏ nhất. Huấn luyện vẫn dùng random tie như mã gốc. Đây là thay đổi quy trình đánh giá có chủ đích; không kỳ vọng tái tạo số của hàm evaluate_pair nguyên bản. SD trong bảng tổng hợp là SD mẫu giữa **5 seed**, ddof=1. Vùng tô trên đồ thị cũng là SD giữa seed, không phải khoảng tin cậy.

Q9 đổi mức giảm giá thành 5%, giữ phần khác. Đo riêng policy baseline chuyển sang môi trường mới và policy huấn luyện lại ở môi trường mới, cùng so với luật. Tổng cộng **31 lượt huấn luyện đầy đủ**: baseline seed 42 và 6 cấu hình × 5 seed.

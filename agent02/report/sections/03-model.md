## Mô hình và hai cách ra quyết định

### Câu 1 Agent và môi trường

Hai người bán là hai agent, cùng tương tác trong một thị trường. Tại bước t, agent i quan sát s_i(t) = (d_t, c_i(t)), với d thuộc {0,1} là nhu cầu thấp/cao và c là hành động của đối thủ ở bước trước. Có bốn quan sát cục bộ và hai hành động: a = 0 không giảm giá, a = 1 giảm giá. Hai agent chọn đồng thời, không được nhìn hành động hiện tại của bên kia trước khi chọn.

Mỗi bên có xác suất chuyển đổi p_i = clip(0,30 + 0,25d + 0,15a_i − 0,10a_j; 0,05; 0,95). Khi d = 0 có N = 10 khách tiềm năng; d = 1 có N = 20. Doanh số S_i được lấy mẫu Binomial(N,p_i). Reward là lợi nhuận r_i = S_i × [10(1 − δa_i) − 5]. Sau bước, hành động hiện tại trở thành lịch sử; nhu cầu mới được lấy độc lập, hai giá trị có xác suất bằng nhau. Mỗi episode đặt lịch sử hai bên về 0.

Đây là hệ đa agent vì reward của một bên phụ thuộc hành động của bên kia, và hành động hôm nay thay đổi quan sát ngày sau của đối thủ. Nhu cầu chung không làm hai tác nhân trở thành một: mỗi bên có policy và lợi nhuận riêng. Mô hình mô tả cạnh tranh qua môi trường, không có giao thức trao đổi thông điệp hay phối hợp LLM.

### Câu 2 Học từ kinh nghiệm và theo luật

| Khía cạnh | Q-learning | Agent theo luật |
|---|---|---|
| Quyết định | Epsilon-greedy theo Q(s,a) | If-else từ d và c |
| Kinh nghiệm | Cập nhật Q từ reward và trạng thái kế | Không cập nhật tham số |
| Thích nghi | Có thể học lại nếu tiếp tục tương tác | Cần người sửa luật |
| Tính toán | Lưu 8 Q-value; cần ngân sách tương tác | Vài phép kiểm tra điều kiện |
| Giải thích | Xem Q và policy; phụ thuộc dữ liệu học | Dễ kiểm tra từng nhánh |

Luật chuẩn: nhu cầu thấp thì không giảm; nhu cầu cao chỉ giảm nếu đối thủ đã giảm ở bước trước. Nó không tối ưu hóa trực tiếp reward. Q-learning thử hành động rồi ước lượng return; huấn luyện có chi phí dù suy luận với bảng nhỏ rất rẻ.

Luật phù hợp khi chương trình khuyến mãi phải tuân thủ điều kiện cố định, ít dữ liệu và cần quyết định dễ kiểm tra. RL phù hợp hơn khi có simulator đáng tin cậy, nhiều tương tác và cần điều chỉnh trước thay đổi nhu cầu, với ràng buộc giá và rủi ro rõ ràng. Đây là tình huống thiết kế, không phải kết luận hiệu quả kinh doanh từ mô phỏng nhỏ này.

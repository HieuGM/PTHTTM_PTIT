## Đề xuất agent và phép kiểm chứng tốt hơn

### Câu 10 Thiết kế cải tiến

Đề xuất trước hết sửa biểu diễn trạng thái thay vì thay ngay bằng mạng sâu. Trạng thái gồm nhu cầu hiện tại, hành động trước của đối thủ, hành động trước của mình, số bước còn lại, mức giảm giá áp dụng và trạng thái tồn kho nếu mô hình có tồn kho. Khi chỉ bổ sung hai hành động trước và thời gian, có thể vẫn dùng bảng nhỏ. Nếu quan sát đối thủ nhiễu hoặc bị trễ, bổ sung belief hoặc lịch sử ngắn được định nghĩa rõ.

Hành động ban đầu vẫn là {không giảm, giảm theo mức cho phép}; có thể mở rộng thành các mức 0%, 5%, 10%, 20% sau khi kiểm tra mô hình giá. Reward là lợi nhuận sau giá vốn, trừ chi phí thay đổi giá và chi phí tồn kho, với giới hạn giá bán không dưới giá vốn. Tránh thưởng doanh số đơn thuần nếu mục tiêu là lợi nhuận.

Phương pháp cơ sở là Q-learning theo horizon với trạng thái đầy đủ hơn, learning rate giảm theo số lần thăm và exploration theo lịch được chọn trên validation. Có thể thử Double Q-learning để giảm thiên lệch max; so sánh riêng từng thay đổi để biết thành phần nào đóng góp. Cần giữ một policy an toàn theo luật để giới hạn hành động khi thiếu dữ liệu.

### Kế hoạch đánh giá độ bền vững

Giữ ngân sách tương tác ngang nhau cho agent đề xuất, Q-learning tham chiếu và luật. Chia seed điều chỉnh tham số với seed kiểm tra cuối; không chọn policy chỉ vì nó tốt trên seed kiểm tra. Đánh giá cả reset [0,0] lẫn lịch sử khởi đầu 00, 01, 10, 11 và báo kết quả theo từng nhóm, tránh che khuất các trạng thái không được thăm.

Thử các mức giảm giá, demand độc lập và demand có tính bền, các đối thủ luật, luôn giảm, luôn không giảm và RL checkpoint đã đóng băng. Dùng ít nhất 20 seed kiểm tra mới, báo reward/bước, regret so với oracle phù hợp mô hình, tỷ lệ giảm giá, phân vị lợi nhuận thấp, vi phạm ràng buộc và ngân sách tính toán. Dùng cùng demand và sales uniforms để so sánh ghép cặp; tính chênh lệch theo seed và khoảng tin cậy của chênh lệch.

Gọi agent cải tiến bền vững hơn chỉ khi lợi ích giữ được trên nhiều nhóm dịch chuyển, không chỉ một trung bình gộp, và không làm tăng vi phạm hay rủi ro vượt mức đã xác định. Cần ablation lần lượt bỏ lịch sử của mình, bỏ biến thời gian và bỏ cơ chế an toàn để xác định tác dụng từng thành phần.

**Phân biệt phạm vi:** agent cải tiến và thử hai RL cùng học là đề xuất thiết kế. Phần đã triển khai, chạy và lưu kết quả trong bài là agent tham chiếu, đánh giá riêng, các cấu hình alpha/epsilon và kiểm tra mức giảm giá 5%.

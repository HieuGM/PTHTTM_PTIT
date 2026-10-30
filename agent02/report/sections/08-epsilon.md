## Exploration và exploitation

### Câu 4 Vai trò của epsilon greedy

Trong huấn luyện, với xác suất epsilon agent chọn hành động ngẫu nhiên; còn lại chọn hành động có Q cao nhất. Khi có hai hành động, nhánh random vẫn có thể chọn hành động greedy nên tỷ lệ hành động không greedy không nhất thiết bằng epsilon. Khi Q bằng nhau, mã huấn luyện phá hòa ngẫu nhiên; đánh giá dùng argmax xác định và không khám phá.

![So sánh lịch epsilon chuẩn với epsilon cố định 0,05 và 0,30](../results/exploration.png)

{{EPSILON_TABLE}}

{{EPSILON_DISCUSSION}}

Lịch chuẩn epsilon_k = max(0,02; 0,20 × 0,995^k) chạm sàn khoảng episode k = 460. Hai cấu hình cố định giữ đúng 0,05 và 0,30 suốt 5.000 episode. Các tham số alpha, gamma, giá, nhu cầu, seed và ngân sách giữ như nhau. Khi đánh giá, cả ba đều tắt exploration để so policy đã học thay vì trộn thêm chi phí khám phá.

Khám phá quá nhiều có thể làm mất lợi nhuận tức thời do thường xuyên thử giảm giá không phù hợp, đồng thời kích hoạt phản ứng của đối thủ. Ngừng quá sớm có thể khiến một hành động kém được thử bị đánh giá thấp, khiến agent mắc kẹt với Q nhiễu. Mức epsilon tối ưu còn phụ thuộc alpha, số bước và độ quan sát của trạng thái; bảng này chỉ kiểm tra ba cấu hình cụ thể.

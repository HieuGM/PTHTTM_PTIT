## Giới hạn và kiểm tra độ nhạy

### Câu 9 Hạn chế của mô phỏng

Thứ nhất, công thức chuyển đổi là giả định minh họa, không được fit từ thị trường. Hai bên lấy doanh số riêng nên tổng số đơn có thể lớn hơn N; N không phải một kho khách độc quyền được chia giữa người bán. Mô hình không xét hàng tồn, ngân sách, nhiều mức giá hay khách mua lặp lại.

Thứ hai, demand độc lập và đồng xác suất sau mỗi bước nên không có mùa vụ, quán tính hay tác động quảng cáo. Reset lịch sử về [0,0] làm một số trạng thái không xuất hiện khi đánh giá policy nhất định. Kết quả tốt trên phân phối khởi đầu này chưa đảm bảo xử lý được mọi lịch sử cạnh tranh.

Thứ ba, quan sát bốn trạng thái bỏ thiếu lịch sử hành động của mình và horizon; đối thủ cố định chỉ là một kiểu hành vi. Ngân sách 5.000 episode và 5 seed còn nhỏ, alpha cố định nên không có bảo đảm hội tụ từ thực nghiệm. Không sử dụng các giới hạn này để suy đoán lợi nhuận triển khai thực tế.

### Thay đổi đã triển khai Giảm giá 5 phần trăm

Trong config discount-0.05, δ từ 0,20 xuống 0,05; giá khi giảm = 9,5 và biên lợi nhuận = 4,5. Khi đối thủ không giảm: nhu cầu thấp cho E[r giảm] = 10 × 0,45 × 4,5 = 20,25 so với 15; nhu cầu cao cho 20 × 0,70 × 4,5 = 63 so với 55. Lợi ích tức thời của giảm giá thay đổi rõ rệt; phản ứng đối thủ vẫn cần được tính đến.

{{ROBUSTNESS_TABLE}}

{{ROBUSTNESS_DISCUSSION}}

Transfer dùng policy đã học ở mức 20% rồi đánh giá đóng băng tại mức 5%, không cập nhật. Retrain dùng đủ 5.000 × 20 bước ở mức 5%, sau đó đánh giá riêng cùng seed. Luật không được sửa theo reward mới. Tất cả số trong bảng là reward/bước và mean ± SD mẫu của cùng 5 seed; mức giảm giá của mô hình khác tỷ lệ hành động giảm giá của agent.

Đường học hai mức giảm giá được lưu trong results/robustness.png và hiển thị trong notebook. Các cấu hình dùng cùng năm seed; dữ liệu reward từng episode đi kèm cho phép kiểm tra khác biệt giữa quá trình học và policy đóng băng cuối cùng.

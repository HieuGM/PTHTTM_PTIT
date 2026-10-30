## Learning rate và độ ổn định

### Câu 7 So sánh ba learning rate

![Đường học của alpha 0,01 và 0,10 và 0,50 trên năm seed](../results/learning-rate.png)

{{ALPHA_TABLE}}

Bảng dùng cùng 5 seed huấn luyện và cùng protocol đánh giá 10.000 bước mỗi seed. Train là reward/bước trên toàn bộ 5.000 episode, lấy trung bình giữa seed. Cột dao động là trung bình SD episode/bước trong 1.000 episode cuối của từng seed. Eval là mean ± SD mẫu giữa seed. Tỷ lệ giảm giá lấy từ đánh giá greedy.

{{ALPHA_DISCUSSION}}

Về cơ chế, alpha = 0,01 điều chỉnh 1% hiệu TD mỗi bước nên làm mượt nhiễu nhưng cập nhật chậm. Alpha = 0,50 thay nửa khoảng cách đến target ở mỗi lần quan sát nên nhạy với reward ngẫu nhiên và target bootstrap. Alpha = 0,10 nằm giữa hai mức. Khi dùng alpha cố định và epsilon còn sàn, Q vẫn có thể dao động; không giả định hội tụ chỉ từ số episode lớn.

Sự khác nhau giữa reward trên đường học và đánh giá cuối cho thấy không nên chỉ nhìn một điểm cuối để chọn learning rate. SD reward cũng chịu ảnh hưởng nhu cầu và doanh số ngẫu nhiên, không phải thước đo thuần túy của độ dao động Q. Để kết luận về ổn định Q cần ghi thêm Q theo thời gian và độ thay đổi policy, ngoài dữ liệu đang có.

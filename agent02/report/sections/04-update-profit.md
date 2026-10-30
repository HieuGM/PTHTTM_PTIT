## Cập nhật Q và mục tiêu lợi nhuận

### Câu 3 Ý nghĩa và phép tính Q learning

Q(s,a) ước lượng tổng reward chiết khấu khi chọn a tại s rồi tiếp tục theo policy. Với bước chưa kết thúc, TD target = r + gamma × max Q(s′,a′). Hiệu TD = target − Q(s,a). Cập nhật Q mới = Q cũ + alpha × hiệu TD. Alpha quyết định mức tiếp nhận bằng chứng mới, gamma quyết định trọng số tương lai.

Với Q cũ = 4; alpha = 0,1; r = 6; gamma = 0,9; max Q kế = 5:

**Bước 1** Target = 6 + 0,9 × 5 = 10,5.

**Bước 2** Hiệu TD = 10,5 − 4 = 6,5.

**Bước 3** Q mới = 4 + 0,1 × 6,5 = **4,65**.

Giá trị tăng 0,65 vì mục tiêu mới cao hơn ước lượng cũ. Đây là ví dụ số giả định của đề để minh họa phép cập nhật; kết quả thực nghiệm được báo riêng. Ở bước terminal, target = r, không bootstrap. Bảng không có biến thời gian còn lại nên đang dùng cùng Q cho các vị trí khác nhau trong episode hữu hạn; không xem đây là lời giải tối ưu chính xác theo horizon.

### Câu 5 Giảm giá và hàm reward

Không giảm giá: biên lợi nhuận mỗi đơn = 10 − 5 = **5**. Giảm 20%: giá bán = 10 × 0,8 = 8; biên lợi nhuận = 8 − 5 = **3**. Giảm giá tăng xác suất mua 0,15 nhưng giảm 40% biên lợi nhuận mỗi đơn. Tăng doanh số chưa đảm bảo tăng tổng lợi nhuận.

| Nhu cầu d | Hành động đối thủ hiện tại b | E[r không giảm] | E[r giảm 20%] |
|---|---|---|---|
| 0 | 0 | 10 × 0,30 × 5 = 15 | 10 × 0,45 × 3 = 13,5 |
| 0 | 1 | 10 × 0,20 × 5 = 10 | 10 × 0,35 × 3 = 10,5 |
| 1 | 0 | 20 × 0,55 × 5 = 55 | 20 × 0,70 × 3 = 42 |
| 1 | 1 | 20 × 0,45 × 5 = 45 | 20 × 0,60 × 3 = 36 |

Đáng chú ý, ở nhu cầu thấp khi đối thủ giảm giá, giảm giá cũng có lợi tức thời cao hơn 0,5. Vì vậy không được nói không giảm giá luôn trội ở mọi trạng thái. Hành động còn ảnh hưởng phản ứng của đối thủ ở bước sau; bảng trên chưa tính return dài hạn.

Nếu reward đổi thành số đơn bán, agent sẽ có động lực giảm giá thường xuyên hơn vì bỏ qua biên lợi nhuận. Có thể bổ sung chi phí đổi giá, giới hạn tồn kho hoặc chi phí thu hút khách; mỗi thay đổi phải nêu đơn vị và đánh giá lại. Tối ưu một reward sai mục tiêu có thể tạo hành vi không có lợi cho doanh nghiệp.

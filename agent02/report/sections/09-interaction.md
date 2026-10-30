## Tương tác đa agent và tính không dừng

### Câu 8 Đối thủ thay đổi bài toán học như thế nào

Hành động hiện tại của đối thủ xuất hiện trực tiếp trong xác suất mua: nếu đối thủ chuyển từ 0 sang 1 trong cùng điều kiện, p của mình giảm 0,10. Ví dụ mình không giảm giá và nhu cầu cao: p từ 0,55 còn 0,45, lợi nhuận kỳ vọng từ 55 còn 45. Sau bước, hành động đó trở thành c trong quan sát tiếp theo. Agent không thấy trước hành động hiện tại mà chỉ thấy lịch sử.

Hành động của mình hôm nay cũng thay đổi quyết định đối thủ ngày sau. Theo luật chuẩn, nếu nhu cầu kế tiếp cao, đối thủ giảm giá khi mình vừa giảm giá. Vì vậy tối ưu reward không chỉ xét lợi nhuận tức thời. Khi reset hai bên về 0, policy luật đấu luật sẽ duy trì toàn 0: không có bên nào khởi phát phản ứng dây chuyền.

### Vì sao independent Q learning có thể khó

Nếu cả hai RL cùng cập nhật policy, phân phối reward và trạng thái kế mà mỗi bên gặp sẽ đổi theo quá trình học của bên kia. Một Q-value học từ dữ liệu cũ có thể không còn phản ánh đối thủ hiện tại. Trong trường hợp này giả định môi trường dừng của phân tích Q-learning thông thường khó áp dụng; còn có thể xảy ra dao động chiến lược và đuổi theo policy lẫn nhau.

Thực nghiệm ở đây giữ đối thủ luật cố định nên không đo trực tiếp độ không dừng do hai learner. Không được dùng đường học trong bài làm bằng chứng rằng huấn luyện đồng thời hai RL đã ổn định. Các biến động đang quan sát còn có thể đến từ nhu cầu ngẫu nhiên, doanh số và exploration.

### Một thay đổi thực nghiệm để khảo sát

Chạy hai nhánh với cùng seed, ngân sách và cấu hình: nhánh A một RL học với luật cố định; nhánh B hai RL cùng học. Lưu checkpoint mỗi 250 episode và đánh giá đóng băng với bộ đối thủ chuẩn gồm luật, luôn giảm và luôn không giảm. Đo reward, tần suất đổi policy và reward khi đối đầu các checkpoint cũ của đối thủ. Dùng các seed chưa tham gia điều chỉnh tham số. Đây là thiết kế đề xuất, chưa chạy trong bộ số liệu hiện tại.

### Giới hạn trạng thái cục bộ

Quan sát (d, hành động trước của đối thủ) không chứa hành động trước của chính agent, trong khi biến này ảnh hưởng luật của đối thủ hiện tại. Các lịch sử khác nhau có thể trùng một quan sát nhưng dẫn đến reward khác nhau. Do đó không bảo đảm quan sát bốn trạng thái có tính Markov. Bổ sung lịch sử của mình và thời gian còn lại là cải tiến hợp lý trước khi tăng độ phức tạp thuật toán.

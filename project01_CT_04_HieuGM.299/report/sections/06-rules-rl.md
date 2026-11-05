# CHƯƠNG 6. ĐIỀU PHỐI, RULE VÀ REINFORCEMENT LEARNING

## 6.1. Điều phối có giới hạn

Coordinator có hai luồng rõ ràng. Luồng hỏi đáp gọi các vai trò Safety, Retrieval, Policy, Education và Critic theo thứ tự. Luồng phân tích gọi Data, Prediction và Critic. Mỗi lần chuyển đều ghi sender, receiver, kind, mô tả ngắn và thời gian đã trôi qua. Tám thông điệp là giới hạn cứng; không có Agent tự gọi lại không kiểm soát.

Các vai trò không trao đổi hồ sơ giữa những request khác nhau. Context mới được tạo cho từng lượt; không có bộ nhớ hội thoại dài hạn hoặc suy diễn từ những câu trước. Người dùng cần nhập đầy đủ đặc trưng mỗi lần phân tích. Thiết kế này làm demo dễ tái lập và giảm dữ liệu lưu trữ nhưng chưa hỗ trợ quản lý điều trị liên tục.

## 6.2. Hệ quy tắc

Quy tắc xử lý cảnh báo dựa trên triệu chứng được mô tả và glucose nhập tùy chọn, tách biệt hoàn toàn với score MLP. Hệ thống quy đổi mmol/L sang mg/dL bằng hệ số 18,0182. Đường huyết dưới 70 mg/dL kích hoạt cảnh báo hạ đường huyết; giá trị từ 300 mg/dL kích hoạt cảnh báo cần chú ý khẩn, đặc biệt khi kéo dài hoặc kèm dấu hiệu nặng. Đây là hướng dẫn giáo dục dựa trên tài liệu, không phải các ngưỡng duy nhất để chẩn đoán hoặc loại trừ cấp cứu.

Các cụm như bất tỉnh, co giật, khó thở, hôn mê hoặc không nuốt được có thể dừng hỏi đáp thông thường. Logic có kiểm tra một số từ phủ định ngay trước triệu chứng và phân biệt câu hỏi kiến thức với mô tả cá nhân hiện tại. Đây vẫn là xử lý ngôn ngữ bằng luật; không bao phủ hết cách nói tiếng Việt, không thể bảo đảm độ nhạy/specificity lâm sàng và không thay hệ thống phân loại cấp cứu chuyên môn.

| Nhóm quy tắc | Hành vi |
|---|---|
| Dấu hiệu nguy hiểm | Khuyên tìm trợ giúp cấp cứu, không cho đồ ăn/nước khi không nuốt an toàn |
| Glucose thấp | Nhắc xử trí theo kế hoạch đã được nhân viên y tế hướng dẫn và tìm hỗ trợ nếu nặng |
| Glucose cao | Nhắc liên hệ y tế, chú ý DKA và không bỏ qua triệu chứng |
| Kê đơn/điều chỉnh thuốc | Từ chối tính liều hoặc thay đổi thuốc cá nhân |
| Bịa nguồn hoặc bỏ qua bằng chứng | Không thực hiện yêu cầu tạo thông tin giả |
| Vị trí/lịch mở cửa trực tiếp | Nêu chưa có công cụ và dữ liệu tương ứng |
| Dinh dưỡng định lượng cá nhân | Không tự tính gram/kcal khi thiếu đánh giá lâm sàng |

Các quy tắc cảnh báo được áp dụng trước policy học. Q-table không có quyền bỏ qua hoặc giảm mức cảnh báo; MLP cũng không tham gia quyết định có cần cảnh báo hay không. Thiết kế này tránh dùng một mô hình khảo sát cắt ngang làm công cụ đánh giá tình huống cấp tính mà dữ liệu huấn luyện không bao phủ.

## 6.3. Thiết kế Q-learning

RL trong project là một contextual bandit một bước, được huấn luyện bằng cập nhật Q-learning với gamma bằng 0. Môi trường có bốn trạng thái, tạo từ hai biến nhị phân: đã có bằng chứng phù hợp hay chưa, và người dùng có yêu cầu giải thích chi tiết hay không. Ba hành động là abstain, brief và detail.

Reward là rubric kỹ thuật tự thiết kế: hành động đúng kiểu trình bày nhận +1; sai nhận -1; trả lời khi không có bằng chứng bị phạt -3. Với trạng thái không có bằng chứng, mục tiêu là abstain. Với bằng chứng có sẵn, câu hỏi ngắn chọn brief và câu yêu cầu giải thích chọn detail. Reward không dùng kết cục sức khỏe, tuân thủ điều trị hoặc sự hài lòng người bệnh thật.

Huấn luyện dùng seed 299, 4.000 episode, learning rate 0,15 và epsilon giảm từ 1 xuống tối thiểu 0,08. Công thức cập nhật là Q(s,a) ← Q(s,a) + α[r − Q(s,a)] vì bài toán kết thúc sau một hành động. Script train-policy.py ghi Q-table, số lần thăm từng state–action và reward trung bình 500 episode cuối.

## 6.4. Kết quả và cách diễn giải RL

Sau huấn luyện, greedy policy chọn đúng hành động theo rubric ở 4/4 trạng thái. Kết quả này chỉ chứng minh thuật toán học được bảng thưởng đơn giản trong môi trường mô phỏng. Nó không cho biết việc thêm RL tốt hơn điều kiện if/else tương đương, không chứng minh cải thiện hiểu biết và không phải học tăng cường điều trị.

Với môi trường nhỏ, triển khai điều kiện trực tiếp có thể đơn giản hơn. RL được đưa vào để minh họa mối liên hệ state–action–reward và cách tích hợp policy đã học dưới các ràng buộc cố định. Mở rộng hợp lý trong tương lai là thu phản hồi đồng thuận về cách trình bày/chủ đề giáo dục, đánh giá offline và bảo vệ quyền riêng tư; không mở rộng sang tối ưu liều thuốc bằng dữ liệu mô phỏng của demo.

## 6.5. Kiểm thử phối hợp

Kiểm thử riêng bao gồm 11 tình huống cảnh báo, chuyển đổi đơn vị, phủ định triệu chứng, câu hỏi giáo dục, yêu cầu điều chỉnh thuốc và thứ tự ưu tiên luật. Các trường hợp đều đạt sau sửa lỗi được phát hiện trong quá trình phát triển. Bộ test kiểm tra cả trace không vượt tám bước và chỉ dẫn nguồn tồn tại trong KB.

Các test đạt là bằng chứng về hợp đồng phần mềm trong những trường hợp đã viết. Chưa có đánh giá độc lập đủ lớn để ước lượng xác suất bỏ sót nguy hiểm. Cần tiếp tục ghi nhận lỗi thật và mở rộng kiểm thử theo cách diễn đạt mới, thay vì coi một danh sách test ngắn là bảo đảm an toàn.

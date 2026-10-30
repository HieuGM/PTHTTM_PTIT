## Kết luận và tài liệu tham khảo

### Kết luận

Thực nghiệm đã triển khai hai kiểu quyết định, chạy baseline, kiểm tra đường học, ba learning rate, ba exploration và phép so sánh policy đóng băng trong các trận riêng. Tất cả cấu hình chạy trên cùng bộ 5 seed; baseline chuẩn có thêm seed 42. Câu 9 bổ sung thay đổi mức giảm giá từ 20% sang 5%, tách rõ transfer với retrain.

{{CONCLUSION}}

Kết quả phản ánh sự tương tác giữa reward, biểu diễn trạng thái, đối thủ và quy trình đánh giá. Trong mô hình nhỏ, luật phù hợp có thể cạnh tranh tốt với RL. Q-learning có cơ chế học từ phản hồi nhưng không tự bảo đảm policy tối ưu hay thích nghi nếu không tiếp tục cập nhật. Đánh giá đóng băng cho biết chất lượng policy cuối ở phân phối đã chọn; training còn exploration trả lời một câu hỏi khác.

### Tái lập và kiểm tra

Dữ liệu gồm JSON cho từng seed, CSV reward theo episode, bảng tổng hợp và hình dựng từ các kết quả đó. Kiểm thử kiểm tra phép cập nhật Q, terminal, luật, chuyển trạng thái đồng thời, reward, phân phối doanh số, kết quả đánh giá so với oracle độc lập, bất biến Q và tính tái lập. Có đối chiếu chính xác với mã gốc ở 100 episode. Không thay kết quả nhiễu bằng kết quả lý thuyết để làm đẹp báo cáo.

Tên PDF nộp bài là **agent02_CT_04_hieugm.pdf**, theo mẫu agent01 và quy ước tên của đề. Gói hỗ trợ chứa notebook đã thực thi, HTML, mã Python, dữ liệu kết quả và Markdown báo cáo chỉnh sửa được.

### Tài liệu tham khảo

[1] Intelligent System Development. Laboratory Experiment 02 Reinforcement-Learning-Based Agents versus Rule-Based Agents. Năm học 2026–2027. File đề assignment_Agent02_due_29.10.pdf trong bộ ASIGNMENT-AGENT_02. Nguồn yêu cầu, công thức và cấu hình thực nghiệm; mục 7–10.

[2] Mã giảng viên cung cấp. agent02_code.tex và agent02_complementary_code.pdf trong cùng bộ đề. Nguồn môi trường, Q-learning và luật. Bài làm bổ sung đánh giá riêng, common random numbers, nhiều seed cho mọi cấu hình và kiểm tra độ nhạy.

[3] Naeem M., Rizvi S. T. H., Coronato A. A Gentle Introduction to Reinforcement Learning and Its Application in Different Fields. IEEE Access, 2020. DOI 10.1109/ACCESS.2020.3038605. Bản PDF kèm đề. Tham khảo nền tảng reward, policy và exploration.

[4] Developing Multiagent Systems A Practical Tutorial with Python and PyTorch. Tài liệu môn học slide_multiAgent_system_20.10.2026.pdf. Tham khảo mô hình nhiều agent tương tác qua môi trường. Các số liệu và kết luận thực nghiệm trong báo cáo được tính từ mã của bài làm.

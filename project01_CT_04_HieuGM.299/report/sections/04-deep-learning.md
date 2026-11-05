# CHƯƠNG 4. MÔ HÌNH DEEP LEARNING

## 4.1. Kiến trúc và hàm học

Mỗi dataset sử dụng một mạng MLP gồm ba lớp ẩn 64, 32 và 16 nút, ReLU giữa các lớp và một đầu ra logit. Đầu vào có 21 chiều với CDC và 10 chiều với Hospital. Mạng được hiện thực bằng PyTorch; các tham số đã học được lưu thành state_dict độc lập với dữ liệu huấn luyện. Đầu ra sigmoid nằm trong khoảng 0–1 nhưng không tự bảo đảm là xác suất được hiệu chuẩn trong quần thể người dùng mới.

Biểu diễn mạng là hợp các phép biến đổi tuyến tính và phi tuyến: vector chuẩn hóa đi qua Linear–ReLU, Linear–ReLU, Linear–ReLU rồi Linear. Số tham số của CDC là 4.033, Hospital là 3.329. Mạng nhiều lớp đáp ứng thành phần Deep Learning của project; không thay mạng bằng một hàm điểm tự đặt hoặc kết quả dự đoán giả.

Loss là binary cross-entropy trên logits. Adam sử dụng learning rate 0,001, weight decay 0,00001 và batch size 2.048. Ngân sách tối đa 25 epoch, patience 5 theo ROC-AUC validation, seed 42. Lượt chạy hiện tại cả hai mô hình thực hiện 25 epoch; checkpoint tốt nhất được khôi phục trước khi đo test. Môi trường huấn luyện được lưu trong environment.json, gồm Python 3.14.6, PyTorch CPU 2.14.0, NumPy 2.4.6 và scikit-learn 1.9.0 trên Windows.

## 4.2. Tiền xử lý và lựa chọn ngưỡng

Mỗi đặc trưng được chuẩn hóa z-score bằng mean và standard deviation của train. Với biến mã phân loại có thứ tự, đây là một lựa chọn đơn giản cho demo; coi khoảng cách giữa các mã là tương đương có thể tạo giả định mạnh. Một hướng cải thiện là dùng one-hot hoặc embedding cho biến không thứ tự, giữ nguyên split để so sánh.

Mặc định ngưỡng 0,5 có thể không tối ưu F1 khi nhãn mất cân bằng. Quy trình chọn ngưỡng bằng validation riêng, sau đó lưu trong metadata. Ngưỡng MLP CDC là khoảng 0,233954; Hospital khoảng 0,134504. Các ngưỡng này không phải mốc y khoa hoặc ngưỡng triển khai đã được bệnh viện chấp nhận. Tối ưu F1 cũng không đại diện mọi chi phí âm tính giả/dương tính giả.

Logistic Regression là baseline tuyến tính trên cùng dữ liệu chuẩn hóa. Baseline always-negative minh họa rằng accuracy cao chưa đủ để nhận diện lớp dương. Không có tìm kiếm siêu tham số quy mô lớn hoặc nhiều seed cho hai MLP này, nên không kết luận kiến trúc đã tối ưu.

<!-- pagebreak -->

## 4.3. Kết quả CDC

![CDC: đường ROC, precision–recall và tiến trình huấn luyện theo kết quả thật](../results/figures/cdc-evaluation.png)

| Mô hình | ROC-AUC | AP | F1 | Sensitivity | Specificity | Brier |
|---|---|---|---|---|---|---|
| MLP | 0,8274 | 0,4393 | 0,4782 | 0,6368 | 0,8215 | 0,1017 |
| Logistic | 0,8206 | 0,4156 | 0,4685 | 0,6551 | 0,8015 | 0,1038 |
| Luôn âm | 0,5000 | 0,1482 | 0,0000 | 0,0000 | 1,0000 | 0,1482 |

Test CDC có 33.952 mẫu, gồm 5.030 mẫu dương. MLP có 23.758 true negative, 5.164 false positive, 1.827 false negative và 3.203 true positive. Sensitivity khoảng 63,68% cho thấy mô hình vẫn bỏ sót nhiều nhãn dương. Precision khoảng 38,28% phản ánh phần đáng kể dự đoán dương không khớp nhãn nguồn.

MLP cải thiện ROC-AUC và AP so với Logistic trong lượt đo này, trong khi sensitivity ở ngưỡng F1 đã chọn thấp hơn Logistic. Do đó không thể tóm tắt rằng MLP tốt hơn ở mọi tiêu chí. Chênh lệch AUC khoảng 0,0068 chưa được đánh giá khoảng tin cậy hoặc kiểm định cặp. Baseline luôn âm đạt accuracy 85,18%, cao hơn accuracy MLP 79,41%, nhưng sensitivity bằng 0; đây là lý do phải đọc nhiều chỉ số cùng nhau.

<!-- pagebreak -->

## 4.4. Kết quả Hospital

![Hospital: kết quả phân loại tái nhập viện dưới 30 ngày và tiến trình huấn luyện](../results/figures/hospital-evaluation.png)

| Mô hình | ROC-AUC | AP | F1 | Sensitivity | Specificity | Brier |
|---|---|---|---|---|---|---|
| MLP | 0,6334 | 0,1869 | 0,2505 | 0,4090 | 0,7688 | 0,0958 |
| Logistic | 0,6285 | 0,1849 | 0,2396 | 0,4734 | 0,6914 | 0,0961 |
| Luôn âm | 0,5000 | 0,1107 | 0,0000 | 0,0000 | 1,0000 | 0,1107 |

Test Hospital gồm 15.125 lượt điều trị của 10.728 người. ROC-AUC MLP khoảng 0,6334 và AP khoảng 0,1869 thể hiện năng lực phân biệt còn khiêm tốn. MLP vượt baseline Logistic một khoảng nhỏ ở các chỉ số chính được chọn nhưng chưa đủ căn cứ nói có lợi ích lâm sàng, giảm tái nhập viện hoặc dùng được cho quyết định phân bổ chăm sóc.

Các đặc trưng thu gọn, dữ liệu cũ, phân bố bệnh viện và nhiều yếu tố chưa quan sát có thể ảnh hưởng kết quả. Cần thêm nghiên cứu có kiểm soát trước khi kết luận nguyên nhân. Đặc biệt, mô hình này dự báo readmission của một lượt ra viện chứ không phát hiện một người có tiểu đường hay không. Giao diện giữ hai nhánh riêng và luôn trình bày label_semantics.

## 4.5. Suy luận, tái lập và giới hạn

Predictor kiểm tra tên dataset, tập trường, miền giá trị và mã nguyên, tạo vector theo thứ tự metadata, chuẩn hóa rồi gọi mạng. Test parity đối chiếu 30 dòng mỗi dataset giữa kết quả tính lúc đánh giá và trọng số được nạp mới; score phải khớp trong sai số số học cho phép. Các ví dụ trong example-predictions.json lấy từ tập test thật, đã loại ID, dùng để minh họa kỹ thuật chứ không là hồ sơ người dùng.

Các file NPZ dự đoán test lưu y_true và score để dựng lại metric; JSON ghi cấu hình, thời gian, checkpoint và protocol. Không cần huấn luyện lại mỗi lần chạy web. Việc tái huấn luyện trên máy khác có thể làm thay đổi số học/thời gian; khi thay kết quả phải dựng lại bảng/hình thay vì sửa con số trong báo cáo bằng tay.

Chưa có calibration hậu nghiệm, kiểm định theo nhóm tuổi/giới, khảo sát độ lệch phân phối hoặc dữ liệu bệnh nhân Việt Nam. MLP không được dùng để loại trừ cấp cứu, thay xét nghiệm, tính liều thuốc hoặc xác nhận chẩn đoán. Các giới hạn này gắn trực tiếp với ý nghĩa nhãn và phạm vi bằng chứng của dữ liệu, không chỉ là chú thích ở cuối trang.

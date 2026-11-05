# CHƯƠNG 3. DỮ LIỆU VÀ GIAO THỨC THỰC NGHIỆM

## 3.1. Lựa chọn dữ liệu

Ưu tiên của đề là dataset đủ lớn và có thể là dữ liệu Việt Nam. Khảo sát nguồn WHO cho thấy STEPS Việt Nam 2021 có 4.435 bản ghi và có điều kiện truy cập/sử dụng riêng. Project chưa tải hoặc huấn luyện bộ này. Một cổng dữ liệu đặt ở Việt Nam không tự khiến dữ liệu BRFSS thành dữ liệu người Việt. Hai tập chính vì thế được chọn theo khả năng tiếp cận công khai, quy mô và quyền tái sử dụng rõ ràng.

| Thuộc tính | CDC BRFSS | Diabetes 130-US Hospitals |
|---|---|---|
| Nguồn | UCI 891; bản gốc Alex Teboul/BRFSS 2015 | UCI 296; dữ liệu bệnh viện 1999–2008 |
| Quy mô gốc | 253.680 bản ghi, 21 biến đầu vào | 101.766 lượt nội trú, metadata nguồn 47 biến |
| Biến chọn | Toàn bộ 21 biến khảo sát | 10 biến dễ nhập, có ở thời điểm ra viện |
| Nhãn dương | Tiền đái tháo đường hoặc đái tháo đường gộp | readmitted bằng <30 |
| Giấy phép | CC0 theo metadata tác giả Kaggle | CC BY 4.0 theo UCI |
| Đơn vị chia tập | Vector đặc trưng duy nhất sau xử lý | Nhóm patient_nbr |

Tệp CDC có sẵn trong bài trước được đối chiếu với CSV UCI sau khi bỏ ID và quy đổi kiểu số; kết quả nội dung tương ứng. Hash tệp đầu vào, cấu hình và kích thước thực sau xử lý được ghi trong results/data-manifest.json. Script fetch-data.py có thể tải lại từ hai URL chính thức mà không cần khóa API. Dữ liệu gốc Hospital có định danh giả của encounter và patient, chỉ dùng patient_nbr để chia nhóm; chúng không là đầu vào mô hình hoặc nội dung image triển khai.

## 3.2. Đặc trưng CDC

Các biến gồm tăng huyết áp, cholesterol, kiểm tra cholesterol, BMI, hút thuốc, đột quỵ, bệnh tim, vận động, ăn trái cây/rau, uống nhiều rượu, tiếp cận chăm sóc, rào cản chi phí, sức khỏe tổng quát/tinh thần/thể chất, khó đi lại, giới tính, nhóm tuổi, học vấn và thu nhập. Phần lớn biến là mã phân loại, không phải phép đo liên tục. Age là mã nhóm 1–13; không được nhập tuổi thật 65 vào trường này. GenHlth là thang 1–5, MentHlth/PhysHlth là số ngày 0–30.

Diabetes_binary bằng 1 gộp cả tiền đái tháo đường và đái tháo đường của biến thể CDC nhị phân đang dùng. Vì nhãn phản ánh khảo sát cắt ngang, không được diễn giải đầu ra là xác suất một người hiện chưa mắc sẽ phát bệnh trong tương lai. Mô hình cũng không dùng glucose hay HbA1c xét nghiệm để xác nhận chẩn đoán.

## 3.3. Đặc trưng Hospital

Mười đặc trưng được chọn gồm time_in_hospital, num_lab_procedures, num_procedures, num_medications, number_outpatient, number_emergency, number_inpatient, number_diagnoses, AgeGroup và Gender. AgeGroup là nhóm tuổi 1–10 từ [0–10) đến [90–100); Gender được mã hóa 0 nữ, 1 nam theo hai giá trị có đủ mẫu trong nguồn. Ba dòng có gender không hợp lệ cho schema này bị loại, làm tập còn 101.763 lượt.

Các biến như số ngày nằm viện và số thuốc trong lượt điều trị chỉ có đầy đủ khi ra viện. Vì vậy thời điểm dự đoán được xác định là lúc ra viện; mô hình không đại diện sàng lọc khi mới nhập viện. Thu gọn đặc trưng làm biểu mẫu dễ sử dụng nhưng bỏ qua nhiều thông tin bệnh học; đây là một nguyên nhân cần khảo sát khi hiệu năng còn hạn chế, không phải kết luận nhân quả từ một thí nghiệm.

## 3.4. Làm sạch và chống rò rỉ

CDC có 24.206 dòng trùng hoàn toàn. Ngoài ra có 5.218 dòng thuộc các nhóm cùng đặc trưng nhưng nhãn xung đột. Quy trình loại nhóm xung đột và giữ một vector đặc trưng duy nhất ở các nhóm còn lại, thu 226.342 mẫu. Hai số trên có phần giao nhau, không được cộng rồi trừ trực tiếp từ quy mô gốc. Cách làm thay đổi phân phối so với dữ liệu nguồn; hiệu năng chỉ áp dụng cho tập đã xử lý như mô tả.

CDC được chia phân tầng 70/15/15 với seed 42 sau xử lý trùng. Hospital dùng chia nhóm theo patient_nbr, bảo đảm một người không xuất hiện đồng thời ở train, validation và test. Các ID không nằm trong vector X. Scaler chỉ fit trên train; cả validation và test dùng lại mean/std đó. Các biến đã chọn không có dữ liệu thiếu sau kiểm tra, nên không cần imputation.

![Quy mô train, validation và test của hai bài toán sau làm sạch](../results/figures/dataset-splits.png)

| Dataset | Train | Validation | Test | Giao nhóm giữa tập |
|---|---|---|---|---|
| CDC | 158.439 | 33.951 | 33.952 | 0 vector đặc trưng trùng |
| Hospital | 71.583 | 15.055 | 15.125 | 0 patient trùng |

Hospital có 50.060 người trong train, 10.727 trong validation và 10.728 trong test sau lọc. Đánh giá test trên lượt nội trú không tương đương đánh giá mỗi người một phiếu; người có nhiều lượt trong cùng tập vẫn có thể tạo phụ thuộc. Chưa tính khoảng tin cậy có bootstrap theo người, nên không tuyên bố khác biệt nhỏ giữa mô hình là có ý nghĩa thống kê.

## 3.5. Thiết kế so sánh

Trong mỗi dataset, MLP và Logistic Regression được huấn luyện trên cùng train, dùng cùng validation/test. Baseline luôn dự đoán âm được bổ sung để chỉ ra ảnh hưởng mất cân bằng. Checkpoint MLP được chọn theo ROC-AUC validation, ngưỡng nhị phân theo F1 validation và được cố định trước khi đo test. Không chọn mô hình, ngưỡng hoặc epoch bằng kết quả test.

Các chỉ số chính là ROC-AUC, Average Precision (AP), F1, sensitivity, specificity, precision, Brier và ma trận nhầm lẫn. AP trong báo cáo là average_precision_score, không tự đổi tên thành diện tích PR nội suy hình thang. Accuracy được giữ để tham khảo nhưng không làm tiêu chí chính: dự đoán toàn âm vẫn có accuracy cao khi nhãn dương hiếm.

# Dữ liệu thực và quyền sử dụng

Hai bài toán độc lập; không gộp nhãn hoặc suy ra mô hình này tốt hơn mô hình kia từ AUC khác quần thể.

| Bộ | Nguồn | Kích thước gốc | Nhãn | Giấy phép |
|---|---|---:|---|---|
| CDC BRFSS 2015 | [UCI 891](https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators), bản [Kaggle của Alex Teboul](https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset) | 253.680 × 22 | `Diabetes_binary`: gộp diabetes/prediabetes | Bản Kaggle khai báo CC0 Public Domain |
| Diabetes 130-US Hospitals 1999–2008 | [UCI 296](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008), DOI [10.24432/C5230J](https://doi.org/10.24432/C5230J) | 101.766 lượt nội trú, 71.518 bệnh nhân | `readmitted == '<30'` | CC BY 4.0 |

Tác giả bộ hospital: John Clore, Krzysztof Cios, Jon DeShazo, Beata Strack. Nguồn nghiên cứu: Strack et al. (2014), *Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records*, BioMed Research International, DOI [10.1155/2014/781670](https://doi.org/10.1155/2014/781670).

`scripts/fetch-data.py` lấy CSV từ UCI. Nếu workspace có CDC của bài 01 thì tái sử dụng để tiết kiệm tải; lượt kiểm tra 05/11/2026 xác nhận toàn bộ giá trị của 253.680 hàng bằng bản UCI sau bỏ cột `ID` và chuẩn hóa dtype. Không đưa `ID` vào đặc trưng.

`raw/` là cache cục bộ bị ignore; hospital giữ mã `patient_nbr` chỉ trong bước tạo split để đảm bảo các lượt của cùng bệnh nhân không lọt giữa train/validation/test. Không đóng gói CSV raw hoặc mã bệnh nhân. `splits/` là cache ma trận số không có ID, tái tạo bằng `prepare-data.py` và cũng bị ignore. Artifacts triển khai trong `models/` không cần hai thư mục này.

CDC loại toàn bộ nhóm vector đặc trưng có nhãn mâu thuẫn rồi giữ một bản mỗi vector còn lại. Do các nhóm mâu thuẫn cũng chứa bản sao, không cộng trực tiếp số bản sao ban đầu và số hàng mâu thuẫn để suy ra số hàng sạch. Lượt chạy có 226.342 hàng sạch. Hospital loại ba giới tính `Unknown/Invalid`, giữ 101.763 hàng; không lọc theo outcome để làm đẹp kết quả. Đặc trưng tổng kết đợt điều trị chỉ dùng tại thời điểm ra viện.

Tiền xử lý mean/std được fit bằng train. Checkpoint chọn theo validation AUC, ngưỡng chọn theo validation F1. Test chỉ dùng báo cáo cuối, không tham gia lựa chọn. Số lượng và SHA256 nằm trong `results/data-manifest.json`; mã nguồn và cấu hình seed được lưu để tái tạo. Chia nhóm ngăn rò rỉ cùng bệnh nhân, chưa phải kiểm chứng theo bệnh viện hoặc theo thời gian.

Dữ liệu Mỹ lịch sử, không có tập xác thực lâm sàng Việt Nam; bài học thuật không chứng minh tính phù hợp cho bệnh nhân Việt Nam. Nhãn CDC là tự khai báo; nhãn bệnh viện là tái nhập viện, không phải phát hiện bệnh lần đầu.

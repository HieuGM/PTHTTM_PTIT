# Dữ liệu thực, SQLite và benchmark bốn cohort

## Bản nâng cấp 06/11/2026

Benchmark mới dùng **bốn bộ dữ liệu độc lập**, sáu loại mô hình, ba seed mô hình:
24 tổ hợp dataset–model, 72 lượt thực nghiệm trên split cố định. Mỗi cohort có nhãn,
quần thể và thứ tự feature riêng; so sánh sáu mô hình trong từng cohort.

| Bộ | Dòng gốc → sạch | Feature | Nhiệm vụ và nguồn |
|---|---:|---:|---|
| CDC BRFSS |253.680 →226.342|21|Binary gộp tiền đái tháo đường/đái tháo đường; UCI891/Kaggle Alex Teboul|
| Hospital |101.766 →101.763|10 được chọn|Tái nhập viện<30 ngày, quan sát khi ra viện; UCI296, CC BY4.0|
| Pima |768 →768|8|Nhãn tested_positive/negative trong cohort phụ nữ Pima≥21 tuổi; OpenML37 phân phối bản gốc UCI/NIDDK|
| Early Stage |520 →251|16|Nhãn Positive/Negative tại Sylhet Diabetes Hospital, Bangladesh; UCI529, CC BY4.0|

Early Stage có269 dòng trùng hoàn toàn, không có nhóm feature mâu thuẫn nhãn;
bỏ trùng trước chia để cùng vector không lọt giữa train/validation/test. Số520
là dòng nguồn, số251 là vector độc nhất dùng thực nghiệm. Tuổi thực tế16–90,
khác khoảng tuổi trong phần mô tả tóm tắt UCI. Pima có0 duplicate/conflict;
zero ở Glucose, BloodPressure, SkinThickness, Insulin, BMI được coi là missing,
điền bằng median chỉ fit train. Pregnancies0 vẫn hợp lệ.

### Nguồn bổ sung và giấy phép

- Pima: [OpenML37](https://www.openml.org/d/37),
  [API metadata](https://api.openml.org/api/v1/json/data/37),
  [ARFF gốc được phân phối](https://openml.org/data/v1/download/37/diabetes.arff).
  Metadata OpenML ghi licence=`Public`, original owner NIDDK, donor Vincent Sigillito,
  nguồn UCI cũ. Endpoint Pima UCI cũ hiện không tải được; UCI34 là AIM94 time-series
  khác nên không thay thế bằng dataset34. Toàn bộ768×8feature, nhãn và thứ tự ARFF
  được đối chiếu bằng bản CSV của bài trước. ARFF MD5 khớp metadata OpenML:
  `3cbaa3e54586aa88cf6aacb4033e4470`. Không tự đổi nhãn giấy phép thành CC0.
- Early Stage: [UCI529](https://archive.ics.uci.edu/dataset/529/early+stage+diabetes+risk+prediction+dataset),
  DOI [10.24432/C5VG8H](https://doi.org/10.24432/C5VG8H),
  [ZIP chính thức](https://archive.ics.uci.edu/static/public/529/early+stage+diabetes+risk+prediction+dataset.zip).
  CSV SHA256: `7889d9d0beb7dd1ccc58da99f72763f16afb259b5dbbaa086f8195366ff66137`.

### SQL được dùng thật trong luồng huấn luyện

`app/ml/database.py` tải/kiểm kê CSV rồi ghi `raw_cdc`, `raw_hospital`, `raw_pima`,
`raw_early` cùng bảng provenance vào `data/database/diabetes.sqlite3`.
`datasets.prepare_database()` đọc lại bảng raw bằng SELECT để làm sạch/chia,
fit median/mean/std chỉ train và lưu bảng `prepared_<dataset>` cùng thống kê.
`datasets.load_prepared()` SELECT từng split theo `split_order`; các mảng nhận
từ query này trực tiếp cấp vào tất cả các vòng fit, không lấy cache NPZ cũ.

```sql
SELECT Glucose, BMI, Age, target
FROM prepared_pima WHERE split='train' ORDER BY split_order LIMIT 5;
SELECT split, COUNT(*) AS rows, SUM(target) AS positives
FROM prepared_early GROUP BY split;
```

Split train/val/test: CDC158439/33951/33952; Hospital71583/15055/15125;
Pima537/115/116; Early175/38/38. Hospital giữ phân nhóm patient_nbr của giao thức
cũ; các số patient không vào X hoặc bảng prepared. Bảng raw và DB chỉ ở máy
cục bộ để chia nhóm, bị loại khỏi Git/image/ZIP; không cung cấp query tùy ý qua API.

`results/benchmark/database-manifest.json` lưu số dòng, source hash, bảng, SQL,
split và thống kê chuẩn hóa. `results/benchmark/full/` chứa từng run, dự đoán
validation/test, CSV summary và hình; `models/benchmark/full/` giữ state_dict DL
và hệ số logistic nhỏ. Không đưa cây RF/HGB lớn vào image; giữ config/seed và
score để refit kiểm chứng. `models/cdc/`, `models/hospital/` và kết quả cũ được
tái sử dụng nguyên vẹn; Pima/Early mới chọn DL phục vụ bằng validation AUC,
không dùng test chọn mô hình. Không huấn luyện tại request hoặc startup.

Ba seed trên một split đo độ nhạy khởi tạo của mô hình, không là khoảng tin cậy
quần thể. Hai cohort nhỏ có test116/38 dòng; cần nêu giới hạn này khi bảo vệ.
Không coi dữ liệu Mỹ/Bangladesh là xác thực trên người Việt hoặc score đã hiệu chuẩn.

## Hồ sơ hai bộ dữ liệu ban đầu

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

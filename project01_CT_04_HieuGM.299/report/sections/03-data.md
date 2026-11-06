# CHƯƠNG 3. BỐN COHORT VÀ CƠ SỞ DỮ LIỆU HUẤN LUYỆN

## 3.1. Nguồn và nhiệm vụ

| Cohort | Dòng nguồn / sạch | Feature | Nhãn |
|---|---:|---:|---|
| CDC BRFSS 2015 | 253.680 / 226.342 | 21 | Binary gộp tiền đái tháo đường/đái tháo đường |
| Hospital 130-US | 101.766 / 101.763 | 10 | Tái nhập viện dưới 30 ngày |
| Pima | 768 / 768 | 8 | Tested positive/negative, phụ nữ Pima từ 21 tuổi |
| Early Stage | 520 / 251 | 16 | Positive/Negative, Sylhet Hospital Bangladesh |

CDC lấy từ UCI891, bản binary của Alex Teboul khai báo CC0. Hospital UCI296 và Early Stage UCI529 có CC BY 4.0. Pima lấy từ ARFF OpenML37, metadata ghi licence Public, original owner NIDDK. Không tự đổi giấy phép Pima thành CC0.

Endpoint Pima UCI cũ không tải được. UCI34 là AIM94 time-series khác, không dùng thay thế. ARFF OpenML được đối chiếu toàn bộ 768 hàng, tám feature, nhãn và thứ tự với CSV đã có; MD5 khớp metadata. URL/hash ở data/README.md và manifest.

## 3.2. CDC và Hospital

CDC loại nhóm vector có nhãn mâu thuẫn rồi giữ một bản/vector còn lại. Làm sạch trước split ngăn cùng vector qua train và test. Nhóm mâu thuẫn có thể chứa bản sao nên không cộng số duplicate và số mâu thuẫn để suy ra kích thước sạch.

Hospital loại ba dòng gender Unknown/Invalid. Split theo patient_nbr ngăn các lượt của cùng người giao train/validation/test. ID chỉ tạo nhóm, không trong X, trọng số hoặc API. Mười feature được chọn mang thông tin khi ra viện; không diễn giải là dự báo ngay lúc nhập viện. Chia nhóm chưa kiểm chứng bệnh viện mới hoặc dữ liệu tương lai.

## 3.3. Pima: zero-coded missing

Glucose, BloodPressure, SkinThickness, Insulin, BMI bằng 0 được coi là missing theo giao thức bài. Median tính chỉ trên train rồi dùng nguyên vẹn cho validation/test/inference. Pregnancies bằng 0 vẫn hợp lệ. Không xóa mọi hàng có số 0 và không lấy median toàn tập vì sẽ thay quần thể hoặc rò rỉ test.

Pima có 768 dòng, không phát hiện duplicate/conflict trong kiểm kê. Cohort chỉ gồm một nhóm phụ nữ lịch sử nên không suy rộng mặc nhiên cho nam giới, người trẻ hoặc dân số Việt.

## 3.4. Early Stage: vì sao 520 còn 251?

Nguồn 520 dòng có 269 dòng trùng hoàn toàn; sau dedup còn 251 vector, gồm 173 dương và 78 âm. Không có feature-group mâu thuẫn nhãn. Giữ 520 rồi split ngẫu nhiên dễ làm cùng vector lọt test và tăng điểm thiếu tin cậy.

Tuổi thật trong CSV 16-90, khác mô tả ngắn 20-65 trên trang nguồn. Schema dựa kiểm kê thật và ghi khác biệt. Test chỉ 38 dòng; một vài dự đoán đổi làm metric thay đáng kể, không xem AUC cao là bằng chứng mạnh về tổng quát hóa.

## 3.5. SQLite dùng thật trong huấn luyện

database.py đọc/tải CSV và lưu raw_cdc, raw_hospital, raw_pima, raw_early cùng provenance. datasets.py SELECT bảng raw để làm sạch/chia, fit median/mean/std train, rồi ghi prepared_<dataset> với split_order. load_prepared() SELECT từng split; mảng nhận từ query trực tiếp cấp mọi vòng fit.

```sql
SELECT split, COUNT(*) AS rows, SUM(target) AS positives
FROM prepared_early GROUP BY split;
SELECT Glucose, BMI, Age, target FROM prepared_pima
WHERE split='train' ORDER BY split_order LIMIT 5;
```

Benchmark không đọc NPZ cũ để giả lập database. NPZ đầu ra giữ nhãn/score hoặc hệ số nhỏ để kiểm metric. CSV dễ mở Excel; NPZ giữ nhiều mảng đúng dtype và nén. Định dạng không quyết định thuật toán.

## 3.6. Chia tập và tiền xử lý

| Cohort | Train | Validation | Test | Giao thức |
|---|---:|---:|---:|---|
| CDC | 158.439 | 33.951 | 33.952 | Vector sạch, split cố định |
| Hospital | 71.583 | 15.055 | 15.125 | Không giao nhóm bệnh nhân |
| Pima | 537 | 115 | 116 | Stratified, median train |
| Early Stage | 175 | 38 | 38 | Dedup trước stratified split |

Split seed 42; model seed 42/43/44. Đổi model seed không tạo ba test mới. Mean/std fit train và áp cùng thứ tự feature. Checkpoint chọn validation ROC-AUC; ngưỡng chọn validation F 1; đóng băng trước đo test. Không lựa mô hình phục vụ bằng test.

## 3.7. Provenance và giới hạn

Manifest lưu URL, hash, số dòng, SQL, split và thống kê. Raw/database chỉ ở máy cục bộ, bị loại khỏi phát hành. Bốn cohort khác nguồn/nhãn/quần thể, không gộp thành một nhiệm vụ và không là bốn tập external validation của một model.

Bài viết Vinmec và PDF Việt giúp truy xuất tài liệu Việt, không thay tập bệnh nhân Việt có nhãn. Trước dùng thực cần quyền dữ liệu, kiểm định ngoài miền, hiệu chuẩn, đánh giá theo nhóm và chuyên gia y tế.

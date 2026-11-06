# Mô hình, SQLite và benchmark 72 lượt

**4 cohort × 6 loại model × 3 seed = 72 lượt**, không phải 72 kiến trúc. Có ba kiến trúc DL: MLP 64-32, MLP 64-32-16, Residual MLP; ba baseline: Logistic, RF, HGB. Cách chạy chính là [notebook độc lập](notebook/project01-diacare.ipynb); script phục vụ bảo trì.

## Dữ liệu và chống rò rỉ

| Cohort | Dòng sạch | Feature | Train / validation / test |
|---|---:|---:|---|
| CDC | 226.342 | 21 | 158439 / 33951 / 33952 |
| Hospital | 101.763 | 10 | 71583 / 15055 / 15125 |
| Pima | 768 | 8 | 537 / 115 / 116 |
| Early Stage | 251 | 16 | 175 / 38 / 38 |

CDC bỏ nhóm mâu thuẫn và trùng vector trước split. Hospital chia theo bệnh nhân, không giao nhóm; feature dùng tại thời điểm ra viện. Pima coi zero ở năm cột sinh lý là missing, lấy median chỉ từ train; Pregnancies 0 hợp lệ. Early bỏ 269 duplicate từ 520 dòng trước split, không có nhóm feature mâu thuẫn; tuổi thật 16-90.

CSV raw → bảng raw SQLite → SELECT làm sạch → bảng prepared/split → SELECT cấp X/y trực tiếp cho fit. Không lấy NPZ cache cũ giả làm DB. Median/mean/std chỉ fit train. Split seed 42 cố định, model seed 42/43/44. Xem [nguồn và giấy phép](data/README.md); Pima OpenML ghi Public, không tự gán CC0.

## Cấu hình full chốt trước

| Model | Cấu hình |
|---|---|
| Logistic | C=1, max_iter=1000 |
| RF | 100 cây, depth 12, min_samples_leaf 5, n_jobs 2 |
| HGB | 100 iteration, depth 6, early_stopping=False |
| MLP2 | 64 ReLU Dropout.15 → 32 ReLU Dropout.10 → 1 logit |
| MLP3 | 64 ReLU Dropout.15 → 32 ReLU Dropout.10 → 16 ReLU → 1 logit |
| ResMLP | Projection 32, hai residual block, mỗi block hai linear 32, output 1 |

Neural: Adam lr.001, weight_decay1e-5; batch 2048/max 25 epoch cho cohort lớn, batch 32/max 100 epoch cho cohort nhỏ. Patience 10, checkpoint maximum validation AUC với delta>1e-5. BCEWithLogitsLoss khi học, sigmoid khi inference. Threshold maximum F 1 validation, sau đó đóng băng để đo test. Smoke dùng hai epoch, 10 cây/iteration; không thay kết quả full.

## Kết quả thực

`results/benchmark/full/summary.csv` có mean/sample SD ba seed cho ROC-AUC, AP, F 1, precision, sensitivity, specificity, accuracy, Brier và runtime. Từng run có confusion/prevalence/config/threshold/predictions/hash. Hình nằm tại `results/benchmark/full/figures/`.

| Cohort | Quan sát test trong cùng cohort |
|---|---|
| CDC | MLP3 AUC 0,8277±0,0004; HGB 0,8270; chênh lệch nhỏ, không kết luận độ sâu luôn tốt |
| Hospital | MLP3 AUC 0,6348±0,0012, AP 0,1866; khả năng còn hạn chế |
| Pima | MLP3 AUC 0,8653±0,0049; Logistic 0,8624; baseline đơn giản vẫn cạnh tranh |
| Early | RF AUC 0,9615; MLP3 SD 0,0837; test chỉ 38 dòng nên rất hạn chế |

AP là Average Precision, không gán nhãn trapezoidal PR-AUC. SD 0 của thuật toán xác định trên cùng split không chứng minh hết bất định. Không tính trung bình AUC bốn cohort để chọn winner hoặc gọi chúng là external validation của cùng model. SD seed không là CI quần thể; score chưa calibration Việt.

72 run full hoàn thành trên CPU; tổng fit+evaluate 145,588 giây, không gồm mọi bước tải/build/test. Pha đầu 54 run rồi copy 2 gặp lỗi timestamp trên Windows bind-mount. Sửa copyfile, kiểm hash 54 record rồi chạy 18 run còn lại. elapsed 23,449 giây của resume không là tổng 72 run. Xem execution-history.json và environment.json trong thư mục full.

## Serving và tái sử dụng DL

- `models/cdc/` và `models/hospital/` giữ nguyên model/scaler/ngưỡng cũ, version legacy-1.0. Có 11 artifact được so SHA256 trong `results/benchmark/legacy-preservation.json`.
- `models/pima/`: MLP2 seed 42, validation AUC 0,8387. `models/early/`: ResMLP seed 42, validation AUC 0,9744. Cả hai dùng version 2.0-db-benchmark.
- Cohort mới chọn DL bằng validation AUC giữa chín run neural, không dùng test. Benchmark mới lưu riêng để so sánh, serving cũ đáp ứng yêu cầu reuse.
- Neural weights là state_dict, nạp weights_only=True. Metadata JSON giữ schema/feature order/preprocessing/threshold/task/label/version/limitations. Logistic lưu coefficient NPZ. RF/HGB không ship weights; giữ config/seed/test scores để refit.

API từ chối missing/extra/bool/string/NaN/Infinity/fractional category/out-of-range. risk_score là sigmoid nghiên cứu; predicted_class dùng ngưỡng validation, không là chẩn đoán. Hospital dự đoán readmission, không phải phát hiện bệnh mới.

## Tái chạy khi bảo trì

```powershell
python scripts/prepare-database.py
python scripts/run-benchmark.py --mode full --seeds 42 43 44 --reuse-prepared-db
python -m compileall -q app scripts tests
python -m pytest tests -q
```

DB và raw Hospital chỉ ở máy cục bộ, bị ignore khỏi Git/image/ZIP. Không gửi ID bệnh nhân vào API/FPT. Notebook ghi output riêng. Kiểm metric từ score không thay external validation hoặc thẩm định y tế.

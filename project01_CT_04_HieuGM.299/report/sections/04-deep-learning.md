# CHƯƠNG 4. DEEP LEARNING VÀ BENCHMARK SO SÁNH

## 4.1. Sáu cấu hình chốt trước

Ba mô hình cổ điển cung cấp baseline tuyến tính và phi tuyến. Ba mạng neural khảo sát độ sâu và kết nối residual trên cùng feature/split. Không thay hyperparameter theo điểm test. Seed mô hình 42,43,44 được áp cho mọi loại; bộ chia dữ liệu giữ cố định seed 42.

| ID | Kiến trúc / cấu hình full |
|---|---|
| logistic | Logistic Regression, C=1, max_iter=1000 |
| random_forest | 100 cây, max_depth=12, min_samples_leaf=5, n_jobs=2 |
| hist_gradient_boosting | 100 iteration, max_depth=6, early_stopping=False |
| mlp 2 | Input → 64 ReLU Dropout 0.15 → 32 ReLU Dropout 0.10 → 1 logit |
| mlp 3 | Input → 64 ReLU Dropout 0.15 → 32 ReLU Dropout 0.10 → 16 ReLU → 1 logit |
| resmlp | Input projection 32, hai residual block gồm hai linear 32 mỗi block, output 1 |

Mạng trả logit khi học, dùng BCEWithLogitsLoss; suy luận áp sigmoid. Residual block có shortcut cộng đầu vào với phép biến đổi rồi ReLU. Cả ba là mạng nhiều tầng ẩn; không dùng ba seed để tuyên bố có chín kiến trúc DL.

## 4.2. Ngân sách huấn luyện và lựa chọn

Adam learning_rate 0.001, weight_decay1e-5. CDC/Hospital tối đa 25 epoch, batch 2048; Pima/Early tối đa 100 epoch, batch 32. Patience 10 theo validation ROC-AUC, chỉ cập nhật checkpoint khi AUC tăng hơn1e-5. Sau nạp checkpoint tốt nhất, chọn threshold đạt F 1 cao nhất trên validation rồi mới tính score/test metric.

Ba mạng được học từ đầu trong benchmark riêng. Hai model phục vụ CDC/Hospital đã có từ phiên bản trước vẫn được tái sử dụng, không bị thay bằng model mới có test đẹp hơn. Pima/Early là cohort mới nên chọn DL phục vụ theo validation AUC trong chín run neural/cohort; không dùng test chọn.

## 4.3. Chỉ số và cách diễn giải

ROC-AUC đo thứ hạng score. AP là Average Precision theo scikit-learn, không phải diện tích hình thang PR-AUC. F1, sensitivity, specificity và accuracy được tính tại ngưỡng validation; confusion matrix theo nhãn[0,1]. Luôn đọc prevalence và always-negative baseline khi lệch lớp.

Brier là trung bình squared error score-label, chưa chứng minh hiệu chuẩn lâm sàng Việt. Mean ± SD dùng sample SD ba seed trên một split, không là khoảng tin cậy quần thể. SD0 có thể do thuật toán xác định, không chứng minh hết bất định.

<!-- BENCHMARK_START -->

<!-- pagebreak -->

## 4.4. Kết quả CDC BRFSS

Các giá trị là test mean ± SD ba seed; ngưỡng từng run chọn trên validation.

| Model | ROC-AUC | AP | F1 | Brier |
|---|---:|---:|---:|---:|
| HGB | 0,8270 ± 0,0000 | 0,4386 ± 0,0000 | 0,4767 ± 0,0000 | 0,1018 ± 0,0000 |
| Logistic | 0,8206 ± 0,0000 | 0,4156 ± 0,0000 | 0,4685 ± 0,0000 | 0,1038 ± 0,0000 |
| MLP2 | 0,8277 ± 0,0003 | 0,4382 ± 0,0011 | 0,4778 ± 0,0011 | 0,1016 ± 0,0001 |
| MLP3 | 0,8277 ± 0,0004 | 0,4385 ± 0,0006 | 0,4783 ± 0,0001 | 0,1016 ± 0,0000 |
| Random Forest | 0,8247 ± 0,0001 | 0,4352 ± 0,0004 | 0,4771 ± 0,0023 | 0,1022 ± 0,0000 |
| ResMLP | 0,8271 ± 0,0001 | 0,4358 ± 0,0013 | 0,4783 ± 0,0002 | 0,1018 ± 0,0000 |

![So sánh metric trong cohort CDC BRFSS, error bar là SD ba seed](../results/benchmark/full/figures/cdc-benchmark.png)

<!-- pagebreak -->

## 4.5. Kết quả Hospital

Các giá trị là test mean ± SD ba seed; ngưỡng từng run chọn trên validation.

| Model | ROC-AUC | AP | F1 | Brier |
|---|---:|---:|---:|---:|
| HGB | 0,6296 ± 0,0000 | 0,1820 ± 0,0000 | 0,2441 ± 0,0000 | 0,0961 ± 0,0000 |
| Logistic | 0,6285 ± 0,0000 | 0,1849 ± 0,0000 | 0,2396 ± 0,0000 | 0,0961 ± 0,0000 |
| MLP2 | 0,6341 ± 0,0007 | 0,1858 ± 0,0009 | 0,2470 ± 0,0015 | 0,0959 ± 0,0000 |
| MLP3 | 0,6348 ± 0,0012 | 0,1866 ± 0,0004 | 0,2498 ± 0,0020 | 0,0958 ± 0,0000 |
| Random Forest | 0,6249 ± 0,0011 | 0,1781 ± 0,0017 | 0,2446 ± 0,0028 | 0,0963 ± 0,0001 |
| ResMLP | 0,6330 ± 0,0024 | 0,1856 ± 0,0005 | 0,2466 ± 0,0021 | 0,0959 ± 0,0000 |

![So sánh metric trong cohort Hospital, error bar là SD ba seed](../results/benchmark/full/figures/hospital-benchmark.png)

<!-- pagebreak -->

## 4.6. Kết quả Pima

Các giá trị là test mean ± SD ba seed; ngưỡng từng run chọn trên validation.

| Model | ROC-AUC | AP | F1 | Brier |
|---|---:|---:|---:|---:|
| HGB | 0,8104 ± 0,0000 | 0,7280 ± 0,0000 | 0,6458 ± 0,0000 | 0,1921 ± 0,0000 |
| Logistic | 0,8624 ± 0,0000 | 0,7832 ± 0,0000 | 0,7292 ± 0,0000 | 0,1493 ± 0,0000 |
| MLP2 | 0,8550 ± 0,0229 | 0,7675 ± 0,0357 | 0,6934 ± 0,0114 | 0,1629 ± 0,0231 |
| MLP3 | 0,8653 ± 0,0049 | 0,7866 ± 0,0048 | 0,7189 ± 0,0213 | 0,1521 ± 0,0022 |
| Random Forest | 0,8357 ± 0,0026 | 0,7660 ± 0,0043 | 0,6826 ± 0,0196 | 0,1585 ± 0,0018 |
| ResMLP | 0,8608 ± 0,0117 | 0,7848 ± 0,0148 | 0,7145 ± 0,0116 | 0,1524 ± 0,0060 |

![So sánh metric trong cohort Pima, error bar là SD ba seed](../results/benchmark/full/figures/pima-benchmark.png)

<!-- pagebreak -->

## 4.7. Kết quả Early Stage

Các giá trị là test mean ± SD ba seed; ngưỡng từng run chọn trên validation.

| Model | ROC-AUC | AP | F1 | Brier |
|---|---:|---:|---:|---:|
| HGB | 0,9519 ± 0,0000 | 0,9801 ± 0,0000 | 0,9091 ± 0,0000 | 0,0908 ± 0,0000 |
| Logistic | 0,9487 ± 0,0000 | 0,9781 ± 0,0000 | 0,9020 ± 0,0000 | 0,1036 ± 0,0000 |
| MLP2 | 0,9241 ± 0,0385 | 0,9660 ± 0,0224 | 0,8770 ± 0,0526 | 0,1679 ± 0,0682 |
| MLP3 | 0,9081 ± 0,0837 | 0,9589 ± 0,0397 | 0,8782 ± 0,0750 | 0,1632 ± 0,0683 |
| Random Forest | 0,9615 ± 0,0000 | 0,9841 ± 0,0003 | 0,9140 ± 0,0104 | 0,0921 ± 0,0011 |
| ResMLP | 0,9391 ± 0,0400 | 0,9733 ± 0,0212 | 0,9020 ± 0,0151 | 0,0855 ± 0,0307 |

![So sánh metric trong cohort Early Stage, error bar là SD ba seed](../results/benchmark/full/figures/early-benchmark.png)

<!-- BENCHMARK_END -->

## 4.8. Tổng hợp quan sát

CDC: ba mạng và HGB cho ROC-AUC gần nhau quanh 0,827; chênh lệch giữa MLP2/MLP3 rất nhỏ. Không có cơ sở kết luận độ sâu hơn luôn tốt hơn từ ba seed một split. AP quanh 0,44 cho thấy bài toán khó hơn con số accuracy riêng lẻ có thể gợi ý.

Hospital: ROC-AUC mọi mô hình chỉ quanh 0,625-0,635 và AP quanh 0,178-0,187. Mạng không giải quyết hoàn toàn bài toán tái nhập viện với mười feature hiện tại. Cần bổ sung thông tin, thiết kế thời điểm dự báo rõ và kiểm định theo thời gian/bệnh viện; không giấu kết quả thấp.

Pima: logistic có ROC-AUC 0,8624; MLP3 trung bình 0,8653±0,0049, MLP2 dao động lớn hơn. Đây là ví dụ baseline đơn giản vẫn cạnh tranh trên dữ liệu bảng nhỏ. Không chọn architecture vì test cao nhất rồi trình bày như lựa chọn có trước.

Early: Random Forest có ROC-AUC trung bình 0,9615, nhưng test chỉ 38 dòng. Các mạng dao động đáng kể giữa seed, MLP3 SD khoảng 0,0837. AUC cao ở một cohort nhỏ không chứng minh tốt hơn CDC/Hospital, vì nhãn/quần thể/test khác nhau.

## 4.9. Tái sử dụng artifact và chi phí

11 artifact mô hình/kết quả cũ của CDC/Hospital được đối chiếu SHA256 và giữ nguyên. serving CDC/Hospital dùng model_version legacy-1.0; Pima/Early dùng 2.0-db-benchmark. Pima chọn MLP2 seed 42 theo validation AUC 0,8387; Early chọn ResMLP seed 42 theo validation AUC 0,9744. Đây là lựa chọn validation, khác bảng test mean/SD.

72 run được thực thi thật trên CPU Linux với Python 3.12.16, torch 2.15.0+cpu, NumPy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1. Tổng các thời gian fit+evaluate ghi theo run là 145,588 giây. Đây không gồm mọi thời gian tải nguồn, build container và kiểm thử.

Lượt đầu đã hoàn thành 54 run nhưng bước copy artifact Pima gặp lỗi cập nhật timestamp trên Windows bind-mount. Sửa copy 2 thành copyfile chỉ sao nội dung, xác minh hash/nhãn 54 run, rồi chạy tiếp 18 run Early. Giá trị 23,449 giây của invocation resume không phải thời gian train 72 run. execution-history.json lưu rõ hai pha.

## 4.10. Artifact và khả năng tái lập

Mỗi run giữ config, seed, checkpoint/history khi phù hợp, SQL source/hash, threshold, metric và score validation/test. Neural weights lưu state_dict; logistic giữ coefficient/intercept trong NPZ. Cây RF/HGB không đóng gói để tránh artifact lớn; cần refit bằng cùng config/seed/data để tái tạo model, còn score test đã lưu để tính lại metric.

Các hình so sánh biểu diễn metric theo cohort. Báo cáo không tạo leaderboard gộp AUC của bốn nhiệm vụ. Đánh giá thêm bootstrap, calibration, temporal/external validation và kiểm định khác biệt là hướng phát triển, chưa được tuyên bố đã làm.

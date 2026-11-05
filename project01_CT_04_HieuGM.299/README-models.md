# Dữ liệu và mô hình Deep Learning

Hai MLP PyTorch được huấn luyện riêng: CDC BRFSS dự đoán nhãn gộp diabetes/prediabetes khảo sát; Hospital dự đoán tái nhập viện dưới 30 ngày trong hồ sơ người bệnh có đái tháo đường. Mỗi mô hình: số đặc trưng → 64 ReLU Dropout0.15 → 32 ReLU Dropout0.10 → 16 ReLU → 1 sigmoid. Logistic regression là baseline trên cùng split/scaler.

Từ thư mục `project01_CT_04_HieuGM.299`:

```powershell
python scripts/fetch-data.py
python scripts/prepare-data.py
python scripts/train-models.py --epochs 25
python scripts/plot-model-results.py
python scripts/test-models.py
```

Cần NumPy, pandas, scikit-learn, torch CPU và matplotlib. Phiên bản đã chạy lưu trong `results/environment.json`; chạy lại có thể khác thời gian và sai số số học theo máy. Seed42, Adam lr0.001, weight decay1e-5, batch2048, tối đa25epoch, patience5; không quét test hoặc thay ngưỡng theo test. Một seed chưa đo được độ bất định giữa lần khởi tạo.

`models/{cdc,hospital}/model.pt` chỉ chứa state_dict, không pickle toàn bộ object; `metadata.json` chứa schema, mean/std, ngưỡng cố định, ý nghĩa nhãn và giới hạn. Baseline lưu NumPy coefficient/intercept. Không cần dữ liệu train, Internet hoặc API key để suy luận.

```python
from app.ml.predict import get_metadata, predict, Predictor
meta = get_metadata('cdc')
features = {s['name']: s['default'] for s in meta['feature_specs']}
result = predict('cdc', features)
```

API nhận đủ trường đúng schema, từ chối thiếu/thừa, chuỗi, boolean, NaN, infinity, mã phân loại không nguyên và số ngoài khoảng. Metadata dùng chính thứ tự đặc trưng huấn luyện. `risk_score` là sigmoid của mô hình, không phải xác suất bệnh đã được hiệu chỉnh cho người Việt. `predicted_class` là phân loại nhãn bộ dữ liệu theo ngưỡng validation; cần đọc `task`, `label_semantics` và `limitations` kèm kết quả.

Kết quả thực: `results/{dataset}-training.json`, test scores `*-test-predictions.npz`, bảng `model-comparison.csv`, hình `results/figures/`. Chỉ số gồm ROC-AUC, average precision (AP), F1, precision, sensitivity, specificity, accuracy, Brier và confusion matrix. AP baseline phụ thuộc prevalence; Brier/calibration plot không tự chứng minh đã hiệu chỉnh lâm sàng. Baseline luôn đoán0 giúp nhận ra accuracy gây hiểu nhầm khi lệch lớp.

Không so trực tiếp các AUC CDC và hospital vì nhiệm vụ/đặc trưng/quần thể khác nhau. Hospital chỉ dùng đặc trưng tổng kết khi ra viện; split bệnh nhân ngăn trùng người, chưa mô phỏng bệnh viện mới hoặc triển khai tương lai. Xem nguồn/giấy phép và lọc dữ liệu tại `data/README.md`. Cache `data/raw/`, `data/splits/` không phân phối; mô hình/kết quả không chứa mã bệnh nhân.

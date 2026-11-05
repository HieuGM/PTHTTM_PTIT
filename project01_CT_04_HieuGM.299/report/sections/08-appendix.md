# PHỤ LỤC. TÁI LẬP VÀ HỢP ĐỒNG DỮ LIỆU

## A.1. Chạy trực tiếp

Các lệnh sau chạy từ chính thư mục project. requirements-lock.txt ghi môi trường Linux của image; môi trường huấn luyện Windows được lưu riêng để đối chiếu.

```powershell
python -m pip install -r requirements.txt -c requirements-lock.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m pytest tests -q
python tests/evaluate-system.py
```

Không cần raw dataset để suy luận. Muốn huấn luyện lại, dùng fetch-data.py, prepare-data.py và train-models.py theo README-models.md. Sau huấn luyện cần chạy plot-model-results.py, kiểm thử và dựng lại báo cáo. Không chỉnh kết quả bằng tay để giữ nguyên một con số cũ.

## A.2. Ví dụ JSON hỏi đáp

```json
{
  "question": "HbA1c là gì?",
  "glucose": null,
  "unit": "mg/dL"
}
```

Phản hồi có answer, status, sources, trace, policy_action và generation. Với trả lời có nguồn, generation bằng extractive. Với luật ưu tiên, generation bằng rule. Trường sources chứa ID/title/url; elapsed_ms là thời gian từ đầu request tới thông điệp, không phải thời gian riêng của toàn bộ model hoặc benchmark latency.

## A.3. Ví dụ JSON phân tích

```json
{
  "dataset": "hospital",
  "features": {
    "time_in_hospital": 4,
    "num_lab_procedures": 40,
    "num_procedures": 1,
    "num_medications": 15,
    "number_outpatient": 0,
    "number_emergency": 0,
    "number_inpatient": 1,
    "number_diagnoses": 8,
    "AgeGroup": 7,
    "Gender": 1
  }
}
```

Đây là input minh họa kỹ thuật tự nhập, không phải hồ sơ bệnh nhân. Nên lấy schema đầy đủ từ /api/catalog thay vì tự suy ý nghĩa biến. Trường CDC Age hoặc Hospital AgeGroup phải nhập mã nhóm đúng phạm vi, không phải số tuổi trực tiếp. Kết quả luôn có clinical_use bằng false và score_semantics giải thích điểm sigmoid.

## A.4. Danh sách tài nguyên

| Nhóm tệp | Vai trò |
|---|---|
| models/cdc và models/hospital | State_dict, metadata, baseline tham chiếu |
| models/presentation-policy.json | Q-table và cấu hình bandit |
| results/data-manifest.json | Quy mô, hash và giao thức chia tập |
| results/*-training.json | Cấu hình, lịch sử loss, validation, test |
| results/*-test-predictions.npz | Nhãn và dự đoán để tính lại metric |
| results/system-evaluation.json | Từng câu hỏi, hạng nguồn và quyết định |
| results/model-tests.json | Kiểm chứng score, scaler và đầu vào |
| results/docker-verification.json | Kiểm tra HTTP của container đã chạy |
| report/sections và builders | Nguồn báo cáo có thể chỉnh và dựng lại |

Tệp raw Hospital không được đưa vào gói nộp hoặc image vì không cần cho demo và chứa định danh giả dùng chia nhóm. Có script tải từ nguồn chính thức để tái lập. Manifest gói nộp ghi SHA256 cho các tệp đã đóng gói, tự loại chính manifest để tránh tự tham chiếu.

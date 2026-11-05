# Project01 — DiaCare MAS

**Giáp Minh Hiếu · B23DCCN299 · Nhóm 04**

Hệ đa vai trò hỗ trợ tìm hiểu bệnh đái tháo đường: hai MLP đã huấn luyện trên dữ liệu thật, KB24thẻ có19URLnguồn, truy xuất/trả lời trích xuất có nguồn, luật cảnh báo, Q-learning minh họa cách trình bày, FastAPI và web demo.

## Mở bài làm

- [Báo cáo PDF](report/project01_CT_04_HieuGM.299.pdf)
- [Nguồn báo cáo Markdown](report/project01_CT_04_HieuGM.299.md)
- [Chi tiết mô hình, kết quả và tái huấn luyện](README-models.md)
- [Dữ liệu, giấy phép và tải lại](data/README.md)
- [Hướng dẫn deploy](DEPLOY.md)

## Chạy nhanh bằng Docker

Chạy các lệnh trong chính thư mục `project01_CT_04_HieuGM.299`:

```powershell
docker build -t diacare-hieugm299:1.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 diacare-hieugm299:1.0
```

Mở http://localhost:8000; API tài liệu tại `/docs`, kiểm tra sẵn sàng tại `/health`.
Image kèm trọng số và KB; không cần tải dữ liệu gốc, huấn luyện lại hoặc nhập khóa API khi chạy demo. `requirements-lock.txt` ghi phiên bản của image Linux đã kiểm thử; môi trường huấn luyện Windows được ghi riêng trong `results/environment.json`.

## Chạy trực tiếp bằng Python

```powershell
python -m pip install -r requirements.txt -c requirements-lock.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Khuyến nghị Python3.12 cho bản triển khai Linux; huấn luyện đã chạy bằng Python3.14 trên máy này. Trọng số `.pt` là state_dict nạp với `weights_only=True`, thống kê chuẩn hóa nằm trong JSON.

## Kiểm thử và tái lập

```powershell
python -m compileall -q app scripts tests report
python -m pytest tests -q
python tests/evaluate-system.py
python scripts/train-policy.py
```

`55/55` pytest đạt trên máy phát triển, sau giải nén gói độc lập và trong container Linux. Docker cũng đạt 13/13 kiểm tra HTTP, healthcheck healthy. `results/system-evaluation.json` giữ từng trường hợp của30câu phát triển, gồm lỗi Q22 chọn thẻ tổng quát đầu tiên; đây không phải benchmark độc lập hoặc kiểm định y khoa. `results/docker-verification.json` ghi kiểm tra thực trong container và ngày chạy.

Kiểm chứng lại scaler và dự đoán từng dòng bằng `python scripts/test-models.py` cần cache `data/splits/`. Cache này không nằm trong ZIP. Trước tiên chạy tải và chuẩn bị dữ liệu theo README-models.md; các test API ở trên chỉ cần trọng số có sẵn.

## Dữ liệu và cách đọc kết quả

- CDC:253.680dòng gốc, sau xử lý226.342vector độc nhất; MLP testAUC0,8274/AP0,4393. Nhãn dương gộp tiền đái tháo đường và đái tháo đường theo bộ binary.
- Hospital:101.766lượt gốc,101.763sau loại3dòng gender không phù hợp; chia theo người bệnh không giao nhóm. MLP testAUC0,6334/AP0,1869 cho nhãn tái nhập viện dưới30ngày. Kết quả còn hạn chế.
- Hai bài toán khác nhau; không so trực tiếp score/AUC để kết luận bên nào tốt hơn hoặc coi hai tập là externalvalidation.
- Các nguồn đều là dữ liệu Mỹ; chưa xác thực trên bệnh nhân Việt Nam. Điểm sigmoid chưa hiệu chuẩn cho quyết định lâm sàng.

## Cấu trúc

```text
app/agents/       Context, luật, policy, điều phối
app/knowledge/    KB, câu hỏi đánh giá, TF-IDF và SQLite
app/ml/           Schema, mạng, pipeline dữ liệu và suy luận
app/static/       Giao diện HTML/CSS/JavaScript
models/           Hai MLP, metadata, baseline, Q-table
scripts/          Tải dữ liệu, train, vẽ hình và kiểm thử mô hình
tests/            API, MAS, dữ liệu nhập và đánh giá KB
results/          Metric, dự đoán, cấu hình, nguồn/hash và biểu đồ
report/           Báo cáo và mã dựng PDF
```

Không lưu câu hỏi/chỉ số sức khỏe của request. SQLite chỉ chứa thẻ tri thức. Không có LLM sinh tự do trong bản mặc định; câu trả lời được ghép trích xuất có nguồn. Q-learning là bandit mô phỏng một bước cho cách trình bày, không tối ưu điều trị. Dữ liệu `data/raw/` và `data/splits/` không nằm trong ZIP hoặc image.

Triển khai cloud chưa được thực hiện vì chưa có tài khoản/credential hosting trong phiên làm việc. Gói Docker và `render.yaml` đã chuẩn bị để triển khai từ kho mã riêng; xem DEPLOY.md.

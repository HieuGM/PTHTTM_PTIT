# Project01 — DiaCare MAS

**Giáp Minh Hiếu · B23DCCN299 · Nhóm 04**

Hệ đa vai trò hỗ trợ tìm hiểu bệnh đái tháo đường: hai MLP đã huấn luyện trên dữ liệu thật, KB 24 thẻ có 19 URL nguồn, truy xuất và trả lời trích xuất có nguồn, luật cảnh báo, Q-learning minh họa cách trình bày, FastAPI và web demo.

**Demo công khai:** [DiaCare trên Render](https://diacare-mas-hieugm299.onrender.com) · [API](https://diacare-mas-hieugm299.onrender.com/docs) · [Kiểm tra sẵn sàng](https://diacare-mas-hieugm299.onrender.com/health).

Dịch vụ Docker gói Free tại Singapore đã chuyển sang `live` lúc **17:16 ngày 05/11/2026**. Kiểm tra HTTP trên URL công khai đạt **13/13**; bằng chứng nằm trong `results/render-http-verification.json` và `results/render-deployment.json`. Gói Free có thể ngủ khi không có truy cập nên lần mở lại có thể chậm.

## Mở bài làm

- **[Notebook chứa toàn bộ mã](notebook/project01-diacare.ipynb)** — mở Jupyter/VS Code/Colab và chọn **Run All**; không cần chạy từng file `.py`.
- [Báo cáo PDF](report/project01_CT_04_HieuGM.299.pdf)
- [Nguồn báo cáo Markdown](report/project01_CT_04_HieuGM.299.md)
- [Chi tiết mô hình, kết quả và tái huấn luyện](README-models.md)
- [Dữ liệu, giấy phép và tải lại](data/README.md)
- [Hướng dẫn deploy](DEPLOY.md)

## Chạy bằng notebook — cách dùng chính

Chỉ cần tệp `notebook/project01-diacare.ipynb`, Python 3.12 và Internet lần đầu. Notebook tự cài thư viện còn thiếu, tải hai CSV thật từ UCI, làm sạch/chia dữ liệu, huấn luyện MLP và baseline, vẽ biểu đồ, dựng KB/luật/Q-learning/MAS và chạy demo. Schema, KB, bộ câu hỏi, API cùng HTML/CSS/JavaScript đều có mã trực tiếp trong các ô; không import module `.py` của bài.

Ô cấu hình mặc định `RUN_MODE="full"`: tối đa 25 epoch/mô hình, patience 5. Chọn `"smoke"` để kiểm tra luồng với 2 epoch trên cùng toàn bộ dữ liệu và split. Kết quả mới ghi vào `diacare-notebook-output/` cạnh thư mục làm việc của kernel, tách khỏi kết quả đã nộp và dịch vụ Render. Số đo có thể khác nhẹ theo phiên bản thư viện; smoke không thay số liệu báo cáo.

Sau huấn luyện có ô hỏi đáp, biểu mẫu nhập đặc trưng và bảng trace ngay trong notebook. Ô cuối kiểm tra API với model thật; tùy chọn `START_WEB=True` để mở giao diện tại `http://127.0.0.1:8000` trên máy cá nhân. Đầu ra raw CSV chỉ giữ cục bộ, không chia sẻ ID bệnh viện.

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

Khuyến nghị Python 3.12 cho bản triển khai Linux; huấn luyện đã chạy bằng Python 3.14 trên máy này. Trọng số `.pt` là state_dict nạp với `weights_only=True`, thống kê chuẩn hóa nằm trong JSON.

## Kiểm thử và tái lập

```powershell
python -m compileall -q app scripts tests report
python -m pytest tests -q
python tests/evaluate-system.py
python scripts/train-policy.py
```

`55/55` pytest đạt trên máy phát triển, sau giải nén gói độc lập và trong container Linux. Docker cũng đạt 13/13 kiểm tra HTTP, healthcheck healthy. `results/system-evaluation.json` giữ từng trường hợp của 30 câu phát triển, gồm lỗi Q22 chọn thẻ tổng quát đầu tiên; đây không phải benchmark độc lập hoặc kiểm định y khoa. `results/docker-verification.json` ghi kiểm tra thực trong container và ngày chạy.

Kiểm chứng lại scaler và dự đoán từng dòng bằng `python scripts/test-models.py` cần cache `data/splits/`. Cache này không nằm trong ZIP. Trước tiên chạy tải và chuẩn bị dữ liệu theo README-models.md; các test API ở trên chỉ cần trọng số có sẵn.

## Dữ liệu và cách đọc kết quả

- CDC: 253.680 dòng gốc, sau xử lý còn 226.342 vector độc nhất; MLP test AUC 0,8274, AP 0,4393. Nhãn dương gộp tiền đái tháo đường và đái tháo đường theo bộ binary.
- Hospital: 101.766 lượt gốc, 101.763 sau loại 3 dòng gender không phù hợp; chia theo người bệnh không giao nhóm. MLP test AUC 0,6334, AP 0,1869 cho nhãn tái nhập viện dưới 30 ngày. Kết quả còn hạn chế.
- Hai bài toán khác nhau; không so trực tiếp score/AUC để kết luận bên nào tốt hơn hoặc coi hai tập là kiểm định ngoài miền cho nhau.
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

Mã nguồn đã push lên [HieuGM/PTHTTM_PTIT](https://github.com/HieuGM/PTHTTM_PTIT). Dịch vụ Render hiện chạy từ commit `6eb79dc0468bc76347b10c2ef0ab1a360974686a`, nhánh `main`, Dockerfile và build context trong thư mục `project01_CT_04_HieuGM.299`. Dịch vụ được tạo trực tiếp qua MCP; Blueprint `render.yaml` ở gốc repo là cấu hình tái triển khai. Xem [DEPLOY.md](DEPLOY.md) để biết cấu hình thực tế và cách kiểm tra lại.

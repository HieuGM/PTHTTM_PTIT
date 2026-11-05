# Kiểm thử Project01 — 05/11/2026

## Kết quả cuối

`python -m compileall -q tests` đạt.

`python -m pytest tests -q`: **50 passed, 1 warning**, 19,71 giây, chạy trên Python Anaconda có PyTorch `2.14.0+cpu`, pytest `9.0.3`. Dùng cả trọng số MLP CDC và Hospital thực tại `models/`; không mock dữ liệu, không thay mô hình. Cảnh báo duy nhất từ Starlette TestClient về httpx/httpx2; không có kiểm thử thất bại.

Mã kiểm thử: `project01_CT_04_HieuGM.299/tests/conftest.py`, `test_system.py`, `test_api_models.py`, `evaluate-system.py`.

## Phạm vi đã kiểm tra

- API trang chủ, health, catalog hai dataset, KB 24 thẻ, dự đoán và trace qua DataAgent/PredictionAgent/CriticAgent.
- Predictor hai dataset: thiếu trường, trường thừa, ngoài khoảng, số không hữu hạn, số phân số ở trường mã nguyên, bool và chuỗi số đều bị từ chối. Điểm dự đoán là float hữu hạn trong [0,1], bằng nhau khi nạp mới trọng số.
- HTTP: dữ liệu chat rỗng/trắng/quá dài, glucose 0/âm, mmol/L quá khoảng, đơn vị sai, trường thừa; NaN và ±Infinity được trả 422, không gây 500. HTTP feature bool/chuỗi không bị âm thầm ép thành số.
- Quy tắc cấp cứu: dấu hiệu chủ động, câu phủ định và câu hỏi giáo dục; đổi mmol/L bằng hệ số 18,0182 cho kết quả cùng mức cảnh báo. Yêu cầu liều thuốc/kê đơn bị từ chối.
- MAS: trace tối đa 8 bước, vượt giới hạn phát sinh RuntimeError; câu trả lời trích xuất chứa ID nguồn thật, URL khớp corpus; câu ngoài phạm vi không dẫn nguồn giả.
- Quyền riêng tư ở tầng ứng dụng: SQLite chỉ có bảng cards, số dòng bằng corpus; marker câu hỏi kiểm thử không được lưu vào bản ghi hay byte của DB. Chưa kiểm tra cấu hình logging của nhà cung cấp cloud bên ngoài.

## Đánh giá truy xuất và answerability

Lệnh: `python tests/evaluate-system.py`. Kết quả từng ca được giữ tại `project01_CT_04_HieuGM.299/results/system-evaluation.json`.

| Chỉ số | Kết quả |
|---|---:|
| Thẻ / URL nguồn chính thức | 24 / 19 |
| Câu hỏi được tác giả soạn | 30 |
| Có bằng chứng / cần từ chối | 22 / 8 |
| Recall@1, trên 22 câu có bằng chứng | 21/22 = 95,45% |
| Recall@3 | 22/22 = 100% |
| MRR@3 | 0,97727 |
| Answerability đúng | 30/30 |
| Câu có bằng chứng được trả lời | 22/22 |
| Câu âm được từ chối | 8/8 |
| Câu có trích đúng ít nhất một ID mong đợi | 21/22 |
| Bộ quy tắc riêng, ngoài 30 câu | 11/11 |

**Thất bại còn giữ nguyên:** Q22 “Tiền đái tháo đường là gì?” có KB24 đúng ở hạng 2; chính sách trả lời ngắn chọn KB01 hạng 1. Hệ thống vẫn trả lời có nguồn nhưng quá tổng quát và không trích thẻ kỳ vọng. Không chỉnh corpus, nhãn đánh giá hoặc số liệu để làm mất ca này.

30 câu và 11 ca quy tắc là **bộ phát triển nhỏ, do người triển khai soạn**, một số lỗi được sửa sau khi quan sát. Không là benchmark độc lập, không là xác thực lâm sàng, không chứng minh độ an toàn y khoa hay hiệu quả cho người Việt Nam. Citation validity chỉ xác thực ID/URL khớp corpus; không tự chứng minh từng diễn giải đủ bằng chứng.

## Lỗi phát hiện và vòng sửa

1. Câu giáo dục ngắn “hạ đường huyết gây co giật?” bị coi cấp cứu; tác giả sửa phân biệt giáo dục/phủ định. Kiểm thử tương ứng hiện đạt.
2. SQLite context manager chỉ commit, chưa đóng kết nối, làm thư mục đánh giá tạm bị khóa trên Windows. Tác giả sửa đóng kết nối rõ ràng và commit; evaluator hiện hoàn thành và dọn thư mục tạm được.
3. Lượt pytest ban đầu: 45 đạt, 5 lỗi. Ba lỗi là NaN/±Infinity nằm trong chi tiết validation làm JSONResponse phát sinh lỗi serialize; hai lỗi do Pydantic ép bool/chuỗi số thành float trước Predictor. Tác giả thêm handler validation không trả raw input và dùng kiểu số strict. Lượt cuối 50/50 đạt.

## Phần chưa xác nhận

- Docker Linux, URL public và cấu hình vận hành cloud do agent chính kiểm tra riêng, không nằm trong kết luận pytest này.
- Báo cáo tiểu luận/PDF chưa xuất hiện trong nhiệm vụ kiểm thử này; cần kiểm tra layout/nội dung sau khi dựng.
- Kiểm thử không chứng minh khả năng xử lý đầy đủ mọi biến thể ngôn ngữ phủ định, dấu hiệu cấp cứu, câu hỏi ngoài KB hoặc dữ liệu dịch chuyển phân phối.


## Kiểm chứng bàn giao bổ sung 05/11/2026

Reviewer bổ sung năm regression sau lượt kiểm thử ban đầu: tổng 55/55 đạt. Gói ZIP đã giải nén độc lập trên ổ D và chạy 55/55 đạt, không có raw/split cache. Bản Docker Linux chạy cùng mã nguồn (18 tệp app khớp SHA256) đạt 55/55 pytest và 13/13 kiểm tra HTTP, healthcheck healthy. Bằng chứng: results/package-verification.json và results/docker-verification.json. Không có URL Render public được tạo.

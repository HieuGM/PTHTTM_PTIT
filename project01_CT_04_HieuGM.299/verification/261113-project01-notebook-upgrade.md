# Project01 notebook 2.1 — full verification, 13/11/2026

## Kết quả

Đã đồng bộ notebook theo mã cuối và chạy đủ **72 lượt fit**, **80 kiểm tra ML**, **99 kiểm tra API** và **37 kiểm tra nâng cấp**. Thời gian toàn lượt: **157,817 giây**. Kernel mới, thư mục riêng chỉ có notebook cùng sáu tệp cache nguồn thật đã đối chiếu SHA256; không có tệp `.py` ứng dụng đi kèm.

Bản giao là chính notebook đã chạy thành công: **67 ô, 56 ô mã, 28 mô-đun inline, 6 tài nguyên giao diện**. Tất cả execution_count liên tiếp, không có error output. Source cell khớp tệp hiện tại và manifest; bốn bộ trọng số nhúng khớp bốn serving artifact của project. Không chép trọng số hoặc số liệu benchmark sinh lại trong sandbox sang project triển khai.

## Thay đổi

- Hai helper `notebook-upgrade.py` và `notebook-api-checks.py` dùng ca retry thật **“Mờ mắt là gì?”**: lần đầu chưa đủ anchor; alias rewrite lấy evidence ở lượt 2. HbA1c thường đủ sau một lượt, câu bóng đá từ chối không truy xuất.
- Notebook hiển thị bản đồ công nghệ → mã nguồn → endpoint, trạng thái đã triển khai/cấu hình/đã chạy, duration riêng từng call, decision trace, kết quả kiểm duyệt/sửa có giới hạn.
- Các bản nháp không an toàn trong ô kiểm thử có nhãn `test_candidate`; không gán chúng cho phản hồi FPT thật.

## Bằng chứng và đường dẫn

- Notebook: `project01_CT_04_HieuGM.299/notebook/project01-diacare.ipynb`.
- Kiểm chứng: `project01_CT_04_HieuGM.299/results/notebook-agent-upgrade-verification.json`.
- SHA256 notebook: `99bedbc3974185faf45d268f3fce12eda173f140be9648e34df00f1c78b253e3`.
- Thư mục chạy: `D:/CodexTaskCache/diacare-hieugm299-261105/upgrade-261113/notebook-full-v21-final/`.
- Môi trường: Python 3.11.15, Torch 2.11.0+cpu, NumPy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0; thông tin đầy đủ trong JSON.

## Phạm vi

Lượt thử đầu tại `notebook-full-v21` đã bị dừng theo yêu cầu root khi review phát hiện P1 ở runtime; giữ `interrupted-run.json`, không sử dụng làm bằng chứng đạt và không chép notebook thử đó về bản giao. Sau sửa P1 và chốt mã, đã rebuild và chạy lượt full cuối nêu trên. Chỉ một lượt full cuối hoàn tất cho source cuối.

Không gọi FPT hoặc Neo4j ngoài, không deploy, không thay số liệu lịch sử 72 run trong báo cáo. Pima/Early được lựa lại theo validation trong thư mục sandbox của notebook; các serving artifact project vẫn giữ nguyên. Có một cảnh báo môi trường Windows/ZMQ về selector thread, không có lỗi thực thi notebook.

Câu hỏi chưa giải quyết: Không có.

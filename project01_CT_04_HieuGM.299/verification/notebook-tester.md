# Project01 notebook — kiểm thử độc lập

**Kết quả: đạt.** Notebook chứa 34 ô, 25 ô mã Python; tất cả chạy thực từ đầu đến cuối.

- Full ban đầu: thư mục sạch chỉ có notebook; tải hai CSV UCI, huấn luyện hai MLP đủ 25 epoch và hai logistic baseline. 25/25 ô mã đạt trong 111,47 giây.
- Smoke: thư mục sạch mới, kernel mới, tải lại hai CSV UCI; cùng toàn bộ dữ liệu/split, mỗi MLP 2 epoch. 25/25 ô mã đạt trong 178,68 giây; thời gian gồm tải mạng.
- Sau sửa ô cài Torch sang CPU index: chạy lại toàn bộ bằng kernel mới, dùng cache raw thật đã tải. 25/25 ô mã đạt trong 59,24 giây.
- Sau reviewer yêu cầu kiểm tra phiên bản thư viện (đặc biệt Pydantic2): chạy lại toàn bộ bản cuối với kernel mới/cache raw thật. 25/25 ô mã đạt trong 46,14 giây; bản giao giữ output full của lần cuối này.
- Cả hai chế độ đạt 55 assertion trong notebook: API thật với mô hình vừa train, schema strict, giá trị không hữu hạn, nạp trọng số mới, mean/std chỉ train, chuyển đổi test, trace và giới hạn Agent, 4 trạng thái policy, 11 ca luật. Đây là 55 kiểm tra notebook, tách với bộ 55 pytest production trước đó.
- Thêm 21 kiểm tra độc lập: hash raw, toàn bộ forward MLP test bằng NumPy từ state_dict, logistic forward từ hệ số, nhãn test giữ nguyên, ROC-AUC/AP từ score đã lưu, checkpoint/ngưỡng validation, vector CDC không giao và patient Hospital không giao; các dòng Hospital khớp phép chia theo nhóm tái dựng độc lập.
- Compile từng ô, chuẩn nbformat, không có import `app.*`, `code.*`, `__file__`, lệnh chạy `.py` hoặc `exec` chuỗi source. Thư mục test không chứa source module, KB/model/JSON có sẵn.

Môi trường: Linux Python3.12, Torch CPU, bộ thư viện cụ thể trong `results/notebook-verification.json`. Không có mock hoặc số liệu giả. Kiểm tra forward NumPy dùng dung sai float32; metric thứ hạng được tái tính từ score đã ghi để giữ đúng các điểm hòa.

Kết quả full mới gần kết quả PDF: CDC AUC khoảng0,82743, Hospital khoảng0,63340. Sai khác nhỏ do môi trường được giữ nguyên trong đầu ra mới; không sửa metric/PDF, trọng số production hoặc Render.

Tệp giao: `project01_CT_04_HieuGM.299/notebook/project01-diacare.ipynb`. Bằng chứng gọn: `project01_CT_04_HieuGM.299/results/notebook-verification.json`; các output/raw đầy đủ chỉ lưu trong thư mục QA ở ổ D, không đưa ID/raw CSV vào gói nộp.

Giới hạn: nhánh tự cài thư viện khi kernel thiếu gói chưa được chạy trong kiểm thử này vì runtime kiểm tra đã cài các gói cần thiết. Kiểm thử đã chạy đầy đủ mọi ô tính toán và API. Full/smoke Project01 không chứng minh toàn bộ budget Final; Final có báo cáo kiểm thử riêng khi hoàn tất.

Câu hỏi chưa giải quyết: không.

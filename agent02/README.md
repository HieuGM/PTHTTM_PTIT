# Agent 02 Q learning và agent theo luật

Sinh viên **Giáp Minh Hiếu — B23DCCN299**. Tên bài **agent02_CT_04_hieugm**, tương tự bài agent01. Ngày thực hiện **29/10/2026**.

## File nộp và file hỗ trợ

- [Báo cáo PDF](report/agent02_CT_04_hieugm.pdf): file nộp theo đề, 14 trang, tiếng Việt, đủ 10 câu hỏi, bảng kết quả, hình và mã thiết yếu.
- [Báo cáo Markdown](report/agent02_CT_04_hieugm.md): nội dung chỉnh sửa được; các phần nguồn ở `report/sections/`.
- [Notebook đã chạy](notebook/agent02_CT_04_hieugm.ipynb) và [bản HTML](notebook/agent02_CT_04_hieugm.html): chứa toàn bộ mã làm bài trong 17 ô code, tự chạy đủ 31 lượt huấn luyện/đánh giá từ kernel mới trong thư mục trống; không cần file .py, JSON hay PNG đi kèm.
- [Mã chạy toàn bộ thí nghiệm](code/agent02_experiment.py), [kiểm thử](code/test-experiment.py), [bảng tổng hợp](results/comparison-summary.csv), [kết quả máy đọc](results/summary.json).
- `reference/` giữ bản đề và Python giảng viên cung cấp (file `.tex` thực chất chứa Python), để đối chiếu và kiểm tra parity khi giải nén độc lập.

## Phạm vi và quy trình

Một RL học với một đối thủ luật cố định. Mỗi lượt huấn luyện 5.000 episode × 20 bước. Baseline có seed42; mọi cấu hình so sánh chạy seeds11/22/33/44/55, agent RNG=seed+10000. Sáu cấu hình: baseline, alpha0.01, alpha0.50, epsilon cố định0.05, epsilon cố định0.30, giảm giá5%; tổng31 lượt huấn luyện đầy đủ.

Đánh giá đóng băng Q, không exploration, 500×20 bước, seed=training seed+500000. Hai trận riêng RL-vs-rule và rule-vs-rule dùng cùng demand và cùng uniforms theo khách hàng. Đây là Bernoulli sum có đúng phân phối Binomial; training giữ thuật toán và chuỗi RNG gốc. Đánh giá tie chọn argmax đầu tiên, training tie ngẫu nhiên như nguồn. Đối chiếu chính xác Q và các trường episode gốc trên100 episode.

SD trong bảng là SD mẫu giữa5 seed (`ddof=1`), không phải SD episode. Đồ thị dùng cửa sổ100 episode không chồng lấp; vùng tô là ±1 SD giữa seed. Dữ liệu raw từng episode, Q-table, policy, tổng reward và đếm hành động nằm trong `results/*-seed-*.json` và CSV. Không giả lập số đo để đạt kết quả kỳ vọng.

Baseline42 training RL33.45548, đối thủ32.83930 reward/bước; đánh giá focal RL=luật34.9185, cả hai không khởi phát giảm giá. Baseline5seed RL=luật35.0728±0.1456. Đây là kết quả mô phỏng, không là kết luận RL hay luật luôn tốt hơn. Báo cáo giải thích trạng thái chưa được thăm và giả định chuyển đổi. Thí nghiệm giảm giá5% phân biệt policy chuyển từ20% với huấn luyện lại, không gọi policy đóng băng là tự thích nghi.

## Chạy lại

Python đã dùng3.14.6 trên Windows; phiên bản package chính xác được lưu trong `results/environment.json` và `requirements.txt`. Thuật toán chỉ cần NumPy, tạo hình cần Matplotlib; phần notebook và PDF cần các gói còn lại. Từ thư mục `agent02`:

```powershell
python -m pip install -r requirements.txt
python code/agent02_experiment.py
python code/test-experiment.py
python notebook/build-notebook.py
python report/assemble-report.py
python report/render-report.py
python report/check-report.py
```

Notebook chứa toàn bộ định nghĩa môi trường, agent, huấn luyện, đánh giá, ghi dữ liệu, thống kê và biểu đồ. Chỉ cần mở file IPYNB, chọn **Restart Kernel and Run All**; notebook tự tạo thư mục `agent02_results` trong thư mục làm việc và chạy đủ31 lượt. Thời gian tham khảo khoảng12 phút; không cần giữ cấu trúc thư mục gốc. Trong workspace hiện tại, interpreter kiểm chứng là `C:/Users/Laptop/anaconda3/python.exe`.

Bìa dùng đúng trang mẫu từ A01_06_linhpm.488.pdf, thay thành Assignment 02 và tên Giáp Minh Hiếu, B23DCCN299; khung và logo PTIT được giữ nguyên. Các trang 2–14 không đổi. Nguồn mẫu một trang lưu ở reference/cover-template.pdf.

PDF dùng ReportLab và PyMuPDF, font Times New Roman Bold cho bìa, Arial và Consolas từ `C:/Windows/Fonts`, PyMuPDF render để kiểm tra. Trên máy khác cần sửa đường dẫn font trong `report/render-report.py` hoặc cài font tương ứng. Không cần Word, API key hoặc GPU. Có thể đọc PDF/HTML đã tạo mà không cài môi trường dựng.

Sau dựng PDF, xem toàn bộ PNG trong `report/preview/`. `check-report.py` kiểm tra nội dung, số trang và biên văn bản, không tự thay thế kiểm tra trực quan. Sau khi xác nhận đủ14 trang, ghi trạng thái visual review trong audit rồi chạy `python package-delivery.py`. ZIP có manifest SHA256; ảnh preview không được đóng gói, chỉ audit được giữ.

## Cấu trúc

`code/reference_core.py`: môi trường, hai agent, training; `code/evaluation.py`: evaluation độc lập; `code/results_io.py`: xuất dữ liệu và hình; `code/agent02_experiment.py`: điều phối6 cấu hình; `code/test-experiment.py`: sáu nhóm kiểm chứng. `report/assemble-report.py` đưa số từ JSON vào bảng, tránh sửa tay số liệu. `report/render-report.py` dựng PDF từ Markdown.

Hạn chế: mô hình chuyển đổi minh họa, không có khách độc quyền hay tồn kho, demand độc lập; quan sát thiếu hành động trước của mình và thời gian còn lại. Hai RL cùng học và agent cải tiến ở câu10 chỉ là đề xuất, chưa được chạy trong bộ kết quả này.

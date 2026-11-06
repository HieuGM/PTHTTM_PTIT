# Quy ước mã và số liệu tiểu luận 03

- Thay đổi trong `tieuluan03/`; giữ dữ liệu, mã và báo cáo bài 01/02 để đối chiếu. Ưu tiên module nhỏ dưới 200 dòng khi hợp lý, tên mới rõ chức năng; không đổi tên mã kế thừa chỉ để đồng nhất hình thức.
- Phân biệt dữ liệu/kết quả kế thừa, kiểm chứng mới và smoke. Không dùng smoke để thay benchmark đầy đủ; không suy ra ưu thế framework khi khác optimizer, khởi tạo hoặc ngân sách.
- JSON kết quả phải ghi cấu hình, môi trường, nguồn dữ liệu/hash khi có, metric và lỗi thực tế. Không sửa số để khớp kỳ vọng; dựng lại nội dung/hình khi thay kết quả. Keras phải ghi backend thực tế.
- Chuỗi thời gian chia theo thời gian, scaler chỉ fit dữ liệu train được dùng; ghi ngày nhãn và baseline naive. Không diễn giải R² trên giá thành lợi nhuận hoặc khả năng dự báo hướng.
- Gradient check cần báo toàn bộ nhóm kiểm tra, dtype, epsilon và lỗi; so sánh autograd theo cùng tham số/quy ước trục. Không dùng median để che các tọa độ sai.
- Agent có trạng thái/thông điệp rõ, giới hạn bước và lý do từ chối. Critic xác thực nguồn không được mô tả là đã chứng minh answerability. Ca chèn lỗi phải ghi rõ là kiểm thử.
- Sau sửa mã: compile, chạy kiểm tra phù hợp, sửa lỗi trước báo cáo. Không lặp huấn luyện dài nếu thay đổi chỉ ảnh hưởng tài liệu. Sau sửa nội dung: dựng lại MD/DOCX/PDF, chạy `report/check-report.py`, mở contact sheets và trang nghi vấn.
- Không chạy đồng thời hai tiến trình Word export. Trạng thái audit cuối và review cuối phải phản ánh đúng việc đã hoàn thành trong `plans/261023-tieuluan03/plan.md`.

# Bổ sung cho Tiểu luận Final và Project01 — 05/11/2026

- Giữ riêng `tieuluan_final_CT_04_HieuGM.299/` và `project01_CT_04_HieuGM.299/`; không sửa dữ liệu/kết quả cũ chỉ để khớp báo cáo mới. Bìa mới dùng metadata người học đã xác nhận.
- GCN/MLP: ghi rõ hai đồ thị, ba seed, split, metric và mean/SD; không suy rộng kết quả đồ thị nhỏ thành benchmark GNN quy mô lớn.
- Dataset y tế: ghi nguồn/giấy phép/hash, thời điểm quan sát, nhãn và đơn vị split. CDC phải tránh vector trùng giữa tập; Hospital chia theo patient_nbr và loại ID khỏi X. Tiền xử lý chỉ fit train, chọn checkpoint/ngưỡng bằng validation.
- Số sigmoid chỉ là score nghiên cứu khi chưa hiệu chuẩn; báo riêng hai nhiệm vụ, AP đúng định nghĩa, baseline cùng split và hạn chế dịch chuyển sang Việt Nam. Không diễn giải điểm thành chẩn đoán cá nhân.
- API số dùng kiểu strict, từ chối thiếu/thừa/ngoài miền/nonfinite; không echo raw dữ liệu sức khỏe trong validation. SQLite cần commit và đóng kết nối rõ ràng, không lưu request mặc định.
- Dẫn nguồn phải khớp ID/URL corpus; đánh giá retrieval và answerability riêng, giữ từng ca lỗi. Bộ 30 câu phát triển và 11 ca luật không thay kiểm định độc lập. Không đổi nhãn hoặc xóa thất bại để làm đẹp metric.
- Rule được ưu tiên hơn policy/mô hình; RL chỉ học kiểu trình bày bằng reward mô phỏng đã công bố, không gán là học điều trị. Trace giới hạn tám bước; không kê đơn/tính liều bằng demo.
- Khóa dependency và lưu môi trường train/deploy riêng. Chỉ ghi Docker chạy được sau build và HTTP thật; chỉ ghi Render online sau xác minh URL. Build thành công không thay kiểm chứng container startup hoặc API.
- Sau thay mã chạy compile và test phù hợp; sau sửa báo cáo dựng lại và kiểm tra toàn bộ trang. 55 test ở mốc tích hợp hiện tại không tự chứng minh chức năng mới thêm sau đó.

## Notebook là lối chạy chính — 05/11/2026

- Theo lựa chọn của người dùng, các project sau ưu tiên một notebook độc lập, mở rồi Run All. Phạm vi bổ sung hiện tại chỉ gồm Final và Project01, mỗi bài một `.ipynb`.
- Mã thuật toán, tải dữ liệu, tiền xử lý, huấn luyện, đánh giá và demo nằm trực tiếp trong ô; không dùng `%run`, `exec` tệp nguồn hoặc import module `.py` cục bộ để bọc bài làm. Script dựng notebook có thể tồn tại để bảo trì, nhưng không là phụ thuộc khi chạy notebook.
- Dữ liệu nhỏ, KB/schema và bộ câu hỏi được nhúng; dữ liệu lớn tải từ nguồn thật khi thiếu cache. Ghi nguồn/hash, phiên bản, seed, cấu hình và chế độ chạy. Kiểm thử độc lập bằng kernel mới trong thư mục chỉ chứa notebook.
- Phân biệt `smoke` với `full`; ngân sách nhỏ vẫn chạy thuật toán thật nhưng không thay benchmark trong PDF. Assert notebook, pytest ứng dụng và kiểm tra HTTP là các bộ kiểm chứng khác nhau, phải ghi riêng.
- Đầu ra mới chỉ ghi dưới `notebook-output/` hoặc `diacare-notebook-output/`, không ghi đè `results/`, trọng số hay báo cáo đã nộp. Loại cache, CSV y tế gốc, ID bệnh viện, checkpoint tạm và thư mục đầu ra sinh lại khỏi Git, Docker image và ZIP bàn giao; giữ notebook cùng output nhúng phù hợp và bằng chứng kiểm thử cần thiết.
- Notebook dài theo yêu cầu được chia thành ô ngắn, tiêu đề và giải thích tiếng Việt; không ép giới hạn 200 dòng bằng cách tạo wrapper phụ thuộc tệp ngoài.

## Project01 Hybrid MAS - 06/11/2026

Contract mỗi agent phải giữ request_id, status, payload, evidence, version và latency; không giấu lỗi dependency bằng score giả. Data validation phải dừng trước DL khi sai. Report phân biệt prediction/rules/evidence/explanation và giới hạn; fallback có nhãn backend/generation thực.

Dữ liệu train phải được cấp từ SELECT trên prepared SQLite; imputer/scaler fit train, checkpoint/threshold chọn validation, không test chọn serving. Hash bảo toàn artifact legacy. Mọi công bố seed/model/dataset phải phân biệt loại architecture, run và serving artifact. Không gộp AUC khác nhiệm vụ.

Corpus phân biệt downloaded và reference-only, MENTIONS và quan hệ chuyên môn có nguồn. Citation validation không là medical truth validation; read session không thay RBAC. Secret chỉ ở environment/.env ignore, raw database có ID không vào Git/image/ZIP. Notebook độc lập chứa mã trực tiếp, output riêng và không persist key.

# Dựng lại báo cáo

Builder dành cho Windows có font Times New Roman/Consolas trong `C:/Windows/Fonts`.
Cài thêm `reportlab`, `pymupdf`, `matplotlib`, `Pillow` cho môi trường tác giả; các gói dựng PDF không cần trong image web.

```powershell
python report/prepare-report.py
python report/build-pdf.py
python report/check-report.py --render-dir report/preview/pages
```

`assets/original-cover.pdf` lưu trang bìa gốc. Builder giữ nguyên trang này cho lần nộp lại; audit so pixel render với bản gốc. `cover-info.json` vẫn chứa metadata bìa đã xác nhận.

`sections/` là nội dung chỉnh sửa được; `prepare-report.py` tạo hình kiến trúc, danh sách nguồn và Markdown hoàn chỉnh. Các biểu đồ mô hình đọc từ kết quả thực trong `results/`.
Khi thay nội dung/kết quả phải xuất lại PDF, render ảnh mọi trang và kiểm tra bố cục trước khi nộp.

`prepare-analysis.py` đọc artifact model và `results/agent-upgrade-cases.json` để sinh bảng serving, confusion matrix, ví dụ API/trace và sơ đồ workflow; không huấn luyện lại. Khi cần thu ví dụ mới, chạy `python scripts/capture-report-cases.py` trước hai lệnh dựng báo cáo. Script này dùng input minh họa, trọng số thật và chủ động tắt FPT/Neo4j để kiểm đường template/cache. Không sửa JSON kết quả bằng tay.


## Nguồn dựng bản mã 2.1

`prepare-upgrade.py` đọc phép đo retrieval, 156-test proof, notebook execution và provider check để sinh bảng đúng artifact; đồng thời vẽ controller hữu hạn. `prepare-analysis.py` sinh ví dụ từ 10 response thật của API cục bộ. `assets/original-cover.pdf` luôn được chèn lại; không đổi bìa.

Các JSON verification được đóng gói để dựng lại báo cáo không cần gọi FPT hoặc huấn luyện lại. Khi muốn chạy lại hành vi, dùng `scripts/capture-report-cases.py`, `scripts/evaluate-agent-upgrade.py` và notebook. Lượt FPT thật là kiểm riêng có thể dùng cấu hình riêng của người chạy; không đặt key trong notebook hoặc báo cáo.

# Dựng lại báo cáo

Builder dành cho Windows có font Times New Roman/Consolas trong `C:/Windows/Fonts`.
Cài thêm `reportlab`, `pymupdf`, `matplotlib`, `Pillow` cho môi trường tác giả; các gói dựng PDF không cần trong image web.

```powershell
python report/prepare-report.py
python report/build-pdf.py
```

`cover-info.json` chứa metadata bìa đã được người dùng xác nhận: PGS. TS. Trần Đình Quế, CT01, nhóm04; Giáp Minh Hiếu/B23DCCN299. Bìa dựng mới bằng chữ, khung và logo PTIT, không chỉnh đè trang bìa người khác.

`sections/` là nội dung chỉnh sửa được; `prepare-report.py` tạo hình kiến trúc, danh sách nguồn và Markdown hoàn chỉnh. Các biểu đồ mô hình đọc từ kết quả thực trong `results/`.
Khi thay nội dung/kết quả phải xuất lại PDF, render ảnh mọi trang và kiểm tra bố cục trước khi nộp.

# Visual QA Project01 — 05/11/2026

**Kết luận: đạt, 25 trang.** Đã mở và kiểm tra riêng toàn bộ ảnh trang 001–025 ở tỷ lệ render 1,3×. Không dùng trang 026 cũ còn trong thư mục ảnh làm bằng chứng.

- PDF: `project01_CT_04_HieuGM.299/report/project01_CT_04_HieuGM.299.pdf`.
- Ảnh QA: `D:/CodexTaskCache/diacare-hieugm299-261105/project-preview/`.
- Bìa đúng Giáp Minh Hiếu, B23DCCN299; PGS. TS. Trần Đình Quế, CT01, nhóm 04; bìa dựng mới.
- Mục lục hai trang khớp bảy chương, phụ lục và tài liệu tham khảo; số trang nội dung bắt đầu sau bìa.
- Không thấy chữ thiếu dấu, ô vuông, nội dung tràn/cắt, hình chồng chữ hoặc bảng cắt hàng. Bảng API tiếp tục trang sau với hàng tiêu đề lặp.
- Mục 2.3 và sơ đồ cùng trang 7; nhãn ngắn gọn, mũi tên rõ và không cắt hộp. Tiêu đề 4.3/4.4 ở cùng trang với hình CDC/Hospital tương ứng (trang PDF 13/14), không còn tiêu đề cô lập.
- Trục, chú giải ROC/PR/calibration/checkpoint đọc được; số liệu và bảng có khoảng cách rõ. Caption 2.1, 3.1, 4.1, 4.2 nhất quán.
- Trang PDF 21 thể hiện Docker Engine Linux WSL2, 13/13 HTTP, healthy, quan sát RAM; trang 22 nêu cloud chưa có URL công khai. Phân biệt bằng chứng local/cloud rõ.
- Tài liệu tham khảo 28 mục nằm trọn trang PDF 25; không còn một mục lẻ ở trang sau.
- Phụ lục JSON phân tích tiếp tục hai dấu đóng ngoặc đầu trang PDF 24; nội dung không mất, không chồng/cắt; chấp nhận cho mã minh họa có thể ngắt trang.

Không sửa PDF/nội dung trong lượt QA. Audit tự động riêng đạt 15/15; kiểm tra ảnh này bổ sung xác minh bố cục trực quan.

Câu hỏi chưa giải quyết: không có thuộc phạm vi visual QA. URL Render công khai vẫn cần tài khoản triển khai, theo báo cáo.


## Cập nhật sau deploy Render — 05/11/2026

Báo cáo vẫn25trang sau khi bổ sung URLpublic, commit, thời điểm live và bằng chứng13/13HTTP. Đã render lại toàn bộ trang và xem lại các trang thay đổi: PDF3(mục lục),21–22(7.5và kết luận),23(phụ lục tiếp nối); không tràn/chồng/chữ lỗi, linkURL rõ. Nội dung các chương khác không đổi. Audit15/15đạt.

### Xác minh độc lập bản sau deploy

Đã mở riêng ảnh mới của cả bốn trang PDF 3, 21, 22, 23 ở tỷ lệ 1,3×. **Đạt; không phát hiện lỗi bố cục mới.** Mục lục khớp; đoạn Render live, commit và 13/13 kiểm tra HTTP đọc được; URL `diacare-mas-hieugm299.onrender.com` không bị tràn/cắt. Phụ lục vẫn bắt đầu đúng trang, không có tiêu đề cô lập do thay đổi phần deploy.

SHA256 PDF cuối: `98e03949e22c5d8883721888c40296414d652155c0e66d4e6cd128773bf9517d`.

Ghi nhận “cloud chưa có URL công khai” ở lượt QA trước là trạng thái lịch sử, đã được thay bằng bằng chứng Render công khai trong bản PDF này. Không có câu hỏi còn lại thuộc phạm vi visual QA. Không sửa PDF trong lượt xác minh.

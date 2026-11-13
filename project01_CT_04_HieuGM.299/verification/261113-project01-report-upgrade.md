# Project01 report update 2.1 — 13/11/2026

Đã đọc README và đối chiếu capabilities, workflow/contracts/roles/reporting, adaptive/review/generation, dữ liệu ca API và hai bản evaluation. Chỉ sửa report/sections/*.md; không sửa builder/PDF/cover/app/README.

## Thay đổi

- Ch1: nêu cải tiến mã và đường kiểm chứng ngay trong kết quả chính.
- Ch2: duration_ms đo call, elapsed_ms tích lũy; decision; bảng quyền đọc/ghi, controller nội bộ và capabilities; giữ 7 core/8 outer messages.
- Ch5: chính sách 2.1.1 có alias/anchor/provenance/budget, genuine retry, bảng before/after giữ Q21/hồi quy, ghi hậu kiểm phát triển và bản v1 bảo toàn.
- Ch6: reviewer xác định, lexical ratio0.35, tối đa1extractive revision/không thêm LLM call, refusal nếu không thể xuất bản sửa đạt; scope không là semantic/clinical truth. Không chỉnh block API sinh tự động.
- Ch7: tách phase1 tài liệu12/11 khỏi code2.1; bộ kiểm/notebook proof mới; public2.0 lịch sử; demo source-to-usage; ảnh controls/technology; kết luận vẫn cuối7.10.
- Phụ lục: ánh xạ module/endpoint mới, duration/decision trong contract, đường tái lập mới.

## Điểm root cần hoàn tất

- Markers ADAPTIVE_EVAL_START/END tại5.11 và UPGRADE_EVIDENCE_START/END tại7.8 đã có đúng một cặp mỗi loại, để builder lấy số JSON cuối. Không hardcode153 hoặc số ô notebook vào báo cáo.
- Root tạo figures/agent-controls.png, ui-controls.png, ui-technology.png rồi render/QA.
- Block6.7 do root đổi nguồn sang agent-upgrade-cases.json10ca; source ví dụ/phần generated vẫn giữ nguyên đến builder.
- Suite/notebook/live proof sau P1fix cần root điền từ artifact cuối; đoạn6.8 mô tả terminalrefusal.
- Render section7.5 chỉ công bố bằng chứng2.0 lịch sử; nếu phát hành2.1 thì root thêm metadata mới, không đổi ngày proof cũ.

Khoảng1.550từ trắng tăng thêm so nguồn42trang, cộng ba hình mới; không tăng chương. Không có TODO trong nội dung. Hạn chế kiểm lexical/regex và hồi quyretrieval được giữ rõ.

Câu hỏi chưa giải quyết: không có; finalverification/QA do root đang thực hiện.

# Project01 resubmission: content and helper review

Ngày: 12/11/2026. Phạm vi: 9 section báo cáo; đặc tả kiến trúc 11 trang; code paths/contracts; helper mới và công cụ dựng PDF. Chỉ đọc, không sửa project, không chạy lại pytest/benchmark/notebook/deploy.

## Kết luận

Không có blocker hoặc lỗi thay đổi thuật toán/model. Bản nộp lại bổ sung đúng các phần trước còn giải thích thiếu theo đặc tả: cơ sở Agent/MAS, mô hình hình thức, I/O, trạng thái, workflow, feature/order, ví dụ tổng hợp, phân tích sai số và giao diện thật. Tách rõ kết quả lịch sử ngày 05-06/11 với phép kiểm bổ sung ngày 12/11. Có ba chỉnh nhẹ về độ chính xác cần xử lý trước khóa bản.

## Findings

### P3 - Audit đang kiểm sai danh tính báo cáo mẫu

- File: `project01_CT_04_HieuGM.299/report/check-report.py`, khóa `no_sample_student`.
- Hiện kiểm `Vũ Thị Mai Linh` và `B23DCCN490`, trong khi trang 1 của `project_01_CT_04_linhvtm_v2.pdf` là `Văn Thị Mai Linh`, `B23DCCN489`.
- Nội dung PDF hiện không có danh tính mẫu; đây là lỗi tiêu chí audit, không phải phát hiện chép danh tính.
- Sửa assertion theo danh tính thật, có thể giữ thêm hai giá trị cũ nếu muốn.

### P3 - Phụ lục A.1 ghi rộng một trang cho mục Safety

- File: `report/sections/08-appendix.md`, hàng cuối A.1: `10 / tr.10-11`.
- Section 10 Safety and Research Limitations nằm trên trang vật lý 10. Trang 11 tiếp section 11 Conclusion.
- Sửa thành `10 / tr.10`; các hàng đặc tả khác được đối chiếu, không thấy sai số trang hoặc tên mục.

### P3 - Câu mô tả trường nguyên cần chính xác hơn

- File: `report/sections/03-data.md`, đoạn cuối 3.8: “dùng số thực cho trường nguyên sẽ bị từ chối”.
- `validate_features` chấp nhận giá trị số thực có giá trị nguyên như `1.0` vì điều kiện từ chối là `int(value) != value`.
- Sửa thành “giá trị không nguyên cho trường nguyên”.
- Mô tả thứ tự có thể nói rõ values được lấy theo `SCHEMAS` trong `validate_features`; metadata có cùng thứ tự. `Predictor.predict` không tự sort object JSON theo metadata, dù hành vi đầu ra hiện đúng.

## Những điểm đã kiểm

- Tên hàm/class ở A.6 đều tồn tại: ReportRequest, report, ReportWorkflow.run/_finish, Predictor.predict, ExplanationAgent.run, KnowledgeBase.retrieve/graph_evidence, EvidenceGenerator.generate và validate_generated.
- SCHEMAS có đúng 21/10/8/16 feature. Tên/thứ tự ở mã khớp hoàn toàn `feature_specs` trong metadata phục vụ của bốn cohort. Danh sách báo cáo giữ đúng case và dấu cách.
- `elapsed_ms` thực là mốc tích lũy từ lúc tạo Context; chương 2/6 và công cụ ghi ví dụ giải thích đúng. Tám message của bảy agent, hai message Coordinator, không bị trình bày thành tám agent.
- `/api/report` là workflow bảy vai trò; `/api/chat` và `/api/predict` là đường cũ. RL chỉ được policy chọn trình bày ở chat, không điều khiển report.
- Tám ca ghi trong `resubmission-cases.json` có 8/8 passed, HTTP/status/số message phù hợp bảng Chương 6; mốc elapsed tăng không giảm trong mỗi request. Synthetic input được ghi rõ là mặc định minh họa; inference dùng weights thật.
- Nội dung mới không suy thành FPT/Neo4j production: script xóa cấu hình gọi ngoài trước import app, dotenv dùng override=False; APP_DATA_DIR riêng; audit file bị tắt. Kết quả normal là cache/template/degraded.
- Bảng serving lấy legacy CDC/Hospital và đúng pima/mlp2-seed42, early/resmlp-seed42. Số đếm và phép tính Pima precision/recall/specificity/F1/accuracy đúng, tách với mean/SD ba seed.
- RAG coefficients, graph/card boosts, điều kiện word/char và cutoff 0,09 trong mục 5.9 khớp retrieval.py. Không gọi LSA là neural embedding hoặc citation gate là kiểm chứng ngữ nghĩa.
- Công thức bandit, target actions, seed, episode, alpha/epsilon ở chương 6 khớp train-policy.py/policy.py. Giữ nhãn reward synthetic và gamma=0.
- Bằng chứng pytest/metric/hash/notebook ngày 12/11 khớp JSON đã đọc. Review không chạy lại các bộ kiểm đã đạt.

## Công cụ dựng và giữ bìa

- AST parse thành công với năm helper: capture-report-cases.py, prepare-analysis.py, prepare-report.py, build-pdf.py, check-report.py. Không cần compile tạo cache hoặc chạy lại suite để kiểm thay đổi nội dung này.
- prepare-analysis đọc số liệu thực, không fit lại. Các block thay thế có marker bắt buộc; prepare-report gọi helper rồi dựng toàn bộ Markdown cùng thứ tự section.
- build-pdf thay đúng trang 0 sau multiBuild và khôi phục outline. Bìa gốc nằm trong report/assets/original-cover.pdf, đi kèm nguồn dựng.
- So độc lập ba bản render scale 1,3: trang bìa trước sửa tại tmp/pdfs/project01-review/original-cover.pdf, asset giữ bìa, trang đầu PDF mới. Pixel giống hoàn toàn cả hai phép so.
- PDF đọc tại thời điểm review có 42 trang, đủ 7 chương. Layout/ảnh toàn trang do root QA; review này không thay kiểm trực quan đó.

## Rủi ro còn lại / điều kiện khóa bản

Sửa ba finding P3 và dựng lại báo cáo/audit để assertion khớp bản cuối. Duyệt PNG cuối, sau đó đồng bộ ZIP/manifest. Không có lý do từ review để thay weights, train lại, triển khai cloud hoặc sửa runtime app.

## Câu hỏi chưa giải quyết

Không có câu hỏi chặn.


## Kết quả xử lý và khóa bản của root

Đã sửa đủ ba finding: danh tính mẫu audit về Văn Thị Mai Linh/B23DCCN489; Safety tại trang10; trường integer mô tả giá trị không nguyên và SCHEMAS chính xác. PDF cuối42trang đạt33/33audit, bìa pixel giống gốc, đã duyệt đủ42trang. ZIP/manifest kiểmCRC/SHA256. Không còn finding chặn.

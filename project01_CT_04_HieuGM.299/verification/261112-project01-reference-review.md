# Project01 — tham khảo và đề xuất cải thiện, 12/11/2026

## Kết luận

Bản hiện có mạnh hơn bài tham khảo về thí nghiệm bốn cohort/72 run, kiểm rò rỉ, provenance, kiểm thử và triển khai. Cần cải thiện cách giải thích hệ đa agent, minh họa vận hành thật và kết nối yêu cầu → mã → bằng chứng. Không cần thay kiến trúc thành LangGraph hay tăng số model. Giữ nguyên trang bìa PDF.

Đã đọc README Project01, toàn bộ văn bản hai PDF tham khảo, các chương 2–7/phụ lục hiện có và mã workflow/contracts/roles/reporting/generation/API; xem trực quan PDF bài mẫu tr.12 và bản hiện tại tr.5. Số trang dưới là thứ tự trang PDF, không phải số in chân trang.

## Điểm nên học từ bài tham khảo

| Ưu tiên | Bài tham khảo | Khoảng trống hiện tại | Bổ sung đề nghị, dùng bằng chứng của Hiếu |
|---|---|---|---|
| P1 | Tr.8–14: khái niệm agent, vòng đời, state/memory/tool, cơ chế phối hợp, tự trị | Chương 2 đi thẳng vào sáu lớp, chưa giải thích vì sao từng thành phần là agent và mức tự chủ thực tế | Thêm cơ sở lý thuyết gọn: agent=(vai trò, đầu vào quan sát, công cụ, chính sách, đầu ra); MAS tập trung, chu trình perception→decision→action→result. Ánh xạ về bảy lớp/thành phần thật. Nêu chỉ Explanation gọi LLM; các agent còn lại dùng pipeline/luật/công cụ xác định. |
| P1 | Tr.12–13: bảng agent/state đọc-ghi/tool/quyết định | Bảng hiện tại chỉ có tên, file, trách nhiệm | Thêm bảng đầu vào → đầu ra → công cụ → điều kiện dừng/lỗi. Dùng tên phương thức thật trong `app/agents/roles.py`, `reporting.py`, `workflow.py`. |
| P1 | Tr.34–35: request PowerShell và phản hồi API; tr.36–40: ảnh UI trace/risk/graph/evidence | Chương 7 mới hướng dẫn demo bằng lời, không có hồ sơ hoàn chỉnh hay ảnh giao diện | Thêm một walkthrough Pima đủ 8 feature hoặc CDC đủ 21 feature; câu hỏi công khai; request JSON; score/threshold/model_version; nguồn/citation; 8 message chuẩn. Chạy thật và lưu JSON an toàn. Có case invalid (422, không DL), thiếu Neo4j/FPT có nhãn, safety override. |
| P1 | Tr.36–40: ảnh giao diện với chú thích giải thích kết quả | PDF hiện tại chỉ có architecture + 4 benchmark plots | Chụp UI thực của chính project: Report có score/flags, trace, evidence; Benchmark; Graph/Knowledge. Caption ghi backend/generation tại lúc chụp. Không lấy ảnh bài mẫu và không dựng ảnh mô phỏng. |
| P2 | Tr.19–21: state/checkpoint, endpoint table, quyết định thiết kế | Mô tả contract đã có nhưng state ownership, API và rationale rải rác | Thêm bảng `/health`, `/api/catalog`, `/api/predict`, `/api/report`, `/api/chat`, `/api/graph`, `/api/benchmark`, `/api/knowledge`: input/output/error. Nêu tại sao chọn workflow tuần tự hữu hạn, reuse model, fallback và phân biệt DB train/KG/cache. |
| P2 | Tr.25–30: đóng gói model, truy vấn graph và prompt/code có diễn giải | Mã đầy đủ nằm trong notebook nhưng báo cáo chưa chứng minh cầu nối model→agent bằng đoạn lõi | Trích 10–25 dòng thật của `DLPredictionAgent.run`, `Context.emit` hoặc nhánh validation/fallback Coordinator; mô tả đủ để người đọc theo dõi, không in nguyên file dài. Trích Cypher query tham số từ `neo4j_backend.py` nếu cần. |
| P2 | Tr.51: kết luận tổng hợp đóng góp và hạn chế | Chương 7 kết thúc bằng hướng phát triển, thiếu kết luận riêng cô đọng | Thêm kết luận: đã xây gì, kết quả nào nổi bật/yếu, phần nào triển khai thật, giới hạn nào còn lại. Giảm lặp các disclaimer và lịch sử nội bộ, gom lịch sử kiểm chứng vào phụ lục. |

## Bám sát kiến trúc giảng viên

`project_architecture_multiagent_diabet_v1.pdf` tr.3–4 yêu cầu sáu lớp, reuse DL/KG, tr.5–8 yêu cầu agent độc lập/interface/message và điều phối tuần tự, tr.9–10 yêu cầu provenance, RL tùy chọn, human review. Project hiện tại phù hợp hơn bài tham khảo sáu agent:

- `app/agents/workflow.py:11` — `ReportWorkflow` chính là Coordinator; không có LLM supervisor/route tự do.
- `app/agents/contracts.py:18` — `AgentResult` đủ request_id, agent, status, payload, evidence, model_version, elapsed_ms; `Context.emit` tạo message. elapsed_ms hiện là thời gian kể từ khởi tạo request, cần mô tả rõ cumulative, không gọi là thời gian riêng của từng agent nếu chưa sửa.
- `app/agents/roles.py` — PatientDataAgent kiểm schema/đơn vị/finite; DL dùng Predictor; Rule có safety/near-threshold/positive-label; Knowledge retrieve k=4; Monitoring không lưu câu hỏi/features/key theo mặc định.
- `app/agents/reporting.py` — Explanation chọn safety_rule hoặc generator; structured_report giữ riêng prediction/rules/evidence/explanation/uncertainty/conflicts.
- `app/knowledge/generation.py:23` — validator kiểm JSON, ID trong evidence, inline/list khớp, cấm URL mới; chưa kiểm semantic groundedness hoặc mọi câu khẳng định chẩn đoán/liều trong output.
- `app/main.py:106` — `/api/report` ánh xạ validation_error→HTTP422 và dependency_error→HTTP503; status degraded vẫn HTTP200.

## Những điều không được chép thành năng lực hiện có

Bài mẫu dùng LangGraph, InMemorySaver/thread_id/resume, SSE, bge-m3 embedding1024, Neo4j vector index, Supervisor LLM route, Critic và vòng sửa. Project Hiếu chưa có các cơ chế này. Có thể ghi là so sánh thiết kế/hướng phát triển, không mô tả đã thực hiện. Không nhập ngưỡng nguy cơ 40/65, số liệu Pima 5-feature, ảnh Long Châu, lớp/MSV/tên tác giả của bài mẫu.

Bài mẫu tr.50 cũng tự nêu chưa có unit test tự động; không giảm hệ kiểm 102 test hiện có để giống mẫu. Bài mẫu có mâu thuẫn nhỏ: tr.51 hướng phát triển còn nhắc streaming dù tr.20/tr.31 đã mô tả SSE; chỉ tham khảo cách trình bày, không sao nội dung bất nhất.

## Rủi ro và việc nên sửa nếu đụng mã

1. Các message elapsed_ms là cumulative; UI/báo cáo có thể gây hiểu nhầm “latency từng bước”. Có thể đổi tên/diễn giải hoặc thêm duration_ms riêng; kiểm regression nếu sửa.
2. Output validator hiện chưa kiểm trực tiếp no-diagnosis/no-dosage; chỉ prompt hạn chế. Có thể bổ sung deterministic guard hẹp với ca kiểm thử thật, nhưng không tuyên bố semantic medical safety verifier. Giữ nguyên bảy agent, đưa guard vào Explanation thay vì thêm Critic chỉ để giống mẫu.
3. Việc giới thiệu agent phải trung thực: đây là modular agent workflow tập trung trong cùng tiến trình, không là các tác tử tự lập kế hoạch/phân tán. Giảng viên cho phép deterministic Data và template Explanation.

## Phạm vi tài liệu đề nghị

Bổ sung khoảng 6–10 trang có giá trị: 2 trang cơ sở MAS + contract; 1 trang sequence/decisions; 2–3 trang walkthrough/API; 2 trang ảnh UI; 1 trang kết luận. Không cố đạt 53 trang bằng code listing hoặc thêm model. Ưu tiên giữ số liệu thật và cải thiện khả năng đọc/kiểm chứng.

Câu hỏi chưa giải quyết: Không có phản hồi chấm bài cụ thể của giảng viên trong thư mục được đọc; không nên bịa nguyên nhân phải nộp lại.

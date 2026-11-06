# CHƯƠNG 7. TÁI LẬP, NOTEBOOK, KIỂM THỬ VÀ TRIỂN KHAI

## 7.1. Notebook là lối chạy chính

Notebook chứa mã trực tiếp trong ô, chạy từ trên xuống trong kernel mới, không import module Python cục bộ của project. Script builder chỉ dùng bảo trì. Luồng gồm môi trường, schema/nguồn, CSV→SQLite→SELECT, benchmark/biểu đồ, serving model tái sử dụng, KB/graph/RAG, bảy agent, demo/API.

Full chạy ngân sách đầy đủ; smoke giảm seed/epoch/cây để kiểm luồng, không thay số đo full. Output ở thư mục riêng, không ghi đè serving model hoặc báo cáo. Dữ liệu tải thật/cache phải có provenance; model nhúng để reuse không thay việc fit benchmark trên nguồn thật.

## 7.2. Tái chạy bằng module khi bảo trì

Các lệnh dưới tương đương thao tác trong notebook, dùng khi phát triển ứng dụng. Chạy từ thư mục Project01; không bắt buộc người học chạy chúng để xem notebook.

```powershell
python scripts/prepare-database.py
python scripts/run-benchmark.py --mode full --seeds 42 43 44 --reuse-prepared-db
python scripts/ingest-knowledge.py --help
python scripts/load-neo4j.py --help
python -m compileall -q app scripts tests report
python -m pytest tests -q
```

Ingestion/Neo4j dùng thông tin kết nối môi trường; không đặt key/password trực tiếp trong câu lệnh được đưa lên Git. Refit cây cần cùng dữ liệu, preprocessing, seed và config. Phiên bản thư viện hoặc nền tảng khác có thể làm sai số số học và thời gian thay đổi.

## 7.3. Các lớp bằng chứng

Kiểm mô hình cần tính lại metric từ y/score, kiểm hash weights, threshold validation, scaler train-only, split/nhóm không giao và bảo toàn serving model cũ. Kiểm MAS cần request_id, thứ tự agent, dừng sớm, lỗi dependency, báo cáo và không ghi dữ liệu nhạy cảm. Kiểm KG cần import/query Neo4j thật, counts, idempotence, provenance và cache parity.

Kiểm notebook cần chạy kernel mới trong thư mục không có source app; không chỉ kiểm JSON hoặc syntax. Kiểm Docker cần build đúng source cuối, gọi API/model/KB và kiểm health. Kiểm public cần chờ deploy live rồi gọi HTTPS, đối chiếu version/commit; việc localhost đạt không thay bằng chứng public.

55/55 pytest và 13/13 HTTP ghi ngày 05/11/2026 là bằng chứng lịch sử phiên bản đầu. Bộ 30 câu phát triển và 11 ca an toàn lịch sử không phải bộ clinical validation. Bản nâng cấp thay schema, retrieval, API và UI nên cần kết quả kiểm tra mới; đối chiếu file verification mới nhất khi nộp.

Bản nâng cấp đạt 102 pytest ở lượt kiểm cuối. Kiểm độc lập tính lại 72 run/144 bộ metric, 36 checkpoint, 24 summary và 11 hash legacy. Bằng chứng nằm tại results/pytest-verification-v2.json và báo cáo tester.

Bản nâng cấp đã kiểm giao diện desktop/mobile thực với 24 kiểm tra: bốn form model, tám message luồng thường, sáu hàng benchmark/cohort, 34 node/19 relation, 26 document metadata, 24 thẻ, chat và năm tab không tràn ngang/lỗi JavaScript. Footprint ứng dụng đo khoảng 302 MiB trong môi trường kiểm; không là bảo đảm mọi tải. Notebook bàn giao có 61 ô/51 ô mã, gồm 25 ô mô-đun inline. Bản cuối chạy full trong kernel mới với nguồn cache thật đã kiểm hash: 72 lượt fit, 80 kiểm tra ML và 68 kiểm tra API đạt, 211,575 giây, không có source app cục bộ đi kèm. Một lượt full trước đó tải nguồn thật đạt trong 339,18 giây. Hai thời gian toàn luồng này không thay tổng fit từng run 145,588 giây của benchmark báo cáo; cache và phiên bản execution được ghi rõ trong notebook-verification.json.

## 7.4. Docker và cấu hình FPT

Image chứa model/corpus và không train tại startup. Một worker Uvicorn hạn chế nhân bản bộ nhớ; OMP_NUM_THREADS=2 giới hạn CPU thread. SQLite cache dựng lại dưới APP_DATA_DIR=/tmp/diacare. Raw/database và notebook-output không trong image.

FPT_API_KEY, FPT_MODEL và FPT_API_URL cấu hình bằng biến môi trường. Gateway AI Marketplace đã kiểm endpoint HTTPS https://mkp-api.fptcloud.com/chat/completions. FPT_BASE_URL là lựa chọn thay thế; full URL được ưu tiên. Key thật không xuất hiện trong notebook/PDF/repository. HTTP 200 xác nhận kết nối chưa đủ để chứng minh câu trả lời grounded; cần thêm kiểm citation/evidence của output thật.

## 7.5. Render và trạng thái phiên bản

Demo tại https://diacare-mas-hieugm299.onrender.com, API docs tại /docs và readiness tại /health. Dịch vụ hiện có dùng Docker Free Singapore, repo HieuGM/PTHTTM_PTIT nhánh main, service `srv-dbm5dfgu01pc738ercq0`. Root Directory trống; Dockerfile và build context trỏ thư mục `project01_CT_04_HieuGM.299`.

Bản nâng cấp chuyển live lúc 14:40:42 ngày 06/11/2026 theo giờ Việt Nam, commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0`. Kiểm public HTTPS cuối đạt 30/30, gồm suy luận bốn model, corpus/graph/benchmark và sinh câu trả lời FPT thật. Lượt trước đạt 29/30 vì một câu FPT dùng template fallback; giữ nguyên tại results/render-http-attempts.json. Chạy lại cùng câu hỏi/bộ kiểm đạt 30/30, không xóa lỗi ban đầu. Đây là kiểm chức năng theo lượt, không bảo đảm LLM luôn thành công. Kết quả cuối ở results/render-http-verification.json, metadata ở results/render-deployment.json.

Dịch vụ dùng public Git URL nên cần manual deploy theo commit mới sau push; deploy do đổi environment ở commit cũ không được tính là bản nâng cấp. FPT Environment đã cấu hình riêng trên Render, không ship .env. Free có thể ngủ; lần mở đầu chậm không tự chứng minh lỗi model.

Neo4j Docker cục bộ không truy cập từ Render bằng localhost. Muốn live graph production cần URI accessible và credential riêng; khi thiếu dùng sqlite_cache/degraded có nhãn. Không tạo thêm tài nguyên trả phí. Live của ứng dụng không chứng minh đã có Neo4j production hoặc kiểm định lâm sàng.

## 7.6. Kịch bản demo bảo vệ

Mở bảng benchmark, chọn lần lượt bốn cohort và giải thích khác nhiệm vụ. Trên report, chọn CDC và feature mặc định minh họa; đọc task, score, threshold, version. Nhập câu hỏi về chế độ ăn hoặc xét nghiệm, mở evidence Vinmec/PDF và trace để chỉ ra KG/RAG/Explanation.

Thử thiếu feature hoặc nhập ngoài miền: Data từ chối trước DL. Thử yêu cầu kê liều: luật giới hạn phản hồi. Tắt FPT hoặc Neo4j có chủ đích trong môi trường cục bộ để xem nhãn fallback; không giả định fallback chính là dịch vụ ngoài đang chạy. Khi demo LLM thật, dùng câu hỏi công khai và không cung cấp hồ sơ nhận dạng.

## 7.7. Hướng phát triển

Ưu tiên bộ câu hỏi độc lập có thẩm định chuyên môn, đánh giá claim-level support, nguồn mới và prompt injection; so sánh retriever với neural embedding phù hợp tiếng Việt. Với ML, thêm external/temporal validation, calibration và phân tích nhóm. Với hệ thống, đo tải/RAM/latency/cost, rate limit và hạ tầng log có chính sách rõ.

Không mở rộng số model chỉ để tăng số lượng khi chưa có giả thuyết so sánh. Ma trận hiện tại hữu hạn, có baseline và ba neural architecture, cho thấy cả kết quả tốt và yếu. Giá trị của bài là pipeline tái lập, không rò rỉ, provenance và ranh giới nghiên cứu được thể hiện trong sản phẩm.

# Project01 2.1 — kiểm thử và review độc lập, 13/11/2026

## Kết quả

**156 pytest đạt, 0 lỗi, 1 cảnh báo deprecation; 11,80 giây, exit 0.** App source SHA256 không đổi trong lượt chạy cuối. Kết quả/env/stdout/hash tại `project01_CT_04_HieuGM.299/results/agent-upgrade-pytest.json`.

Lượt đầu trước sửa lỗi review đạt 153 test/15,80 giây được giữ nguyên tại `results/agent-upgrade-pytest-before-review-fix.json`. Không thay bằng chứng cũ thành kiểm chứng bản cuối.

Đã đọc README project trước khi thực hiện. Môi trường QA dùng Python3.11.15/Torch2.11CPU, các phiên bản dependency cụ thể có trong JSON. Không đọc trực tiếp `.env`, không gọi FPT hoặc Neo4j production, không train và không chạy lại notebook. Conftest tắt hai backend ngoài; các test lỗi dùng sự cố chủ động và mẫu đối kháng được ghi rõ.

## Finding P1 đã phát hiện và sửa

`review_and_revise` trước sửa trả lại candidate `revised_extractive` kể cả khi lần kiểm cuối báo `final_passed=False`. Với văn bản bằng chứng chia dòng `Bạn\nbị tiểu đường.`, bộ lọc từng đoạn không thấy câu khẳng định hoàn chỉnh; ghép đoạn tạo lại câu bị cấm. Review phát hiện lỗi nhưng vẫn trả nội dung đó ra ngoài.

Root đã giao quyền sửa trong phạm vi nâng cấp. Đã sửa `app/knowledge/review.py`:

- `_extractive` kiểm lại đoạn **sau khi ghép**, trước khi dùng làm evidence excerpt.
- `_publish_checked` tại dòng134 chặn candidate không đạt ở ranh giới trả kết quả. Đầu ra thay bằng `REFUSAL`, citations rỗng, `status=insufficient_evidence`, `generation=template`, model rỗng.
- `review_and_revise` gọi gate tại dòng156. Giữ lịch sử candidate đã hỏng trong `attempts`; verdict công bố mô tả đầu ra thực sự sau gate. `terminal_action`/`terminal_verdict` phân biệt fallback hằng tin cậy với thêm một lần sửa. Không giữ raw rejected draft.
- Ngân sách vẫn tối đa một lần sửa extractive, tối đa hai bản ghi candidate; không có lượt LLM bổ sung.

Ba regression mới dùng input thực của hàm: chia dòng câu khẳng định cá nhân; chia dòng tên thuốc/liều; citation không hợp lệ tại publication gate. 30 test review riêng đạt trước lượt full156 cuối.

## Các phần đã đối chiếu

| Thành phần | Kết luận |
|---|---|
| Adaptive retrieval2.1.1 | Tối đa3 lượt; không ép rewrite nếu lượt đầu đã đủ; `Mờ mắt là gì?` là demo retry thật; thiếu anchor/provenance trả evidence rỗng |
| Provenance | Adapter so URL/text/document/page với `source_index`; không dùng score hybrid và lexical như cùng thang xác suất |
| Output review | Check cấu trúc/citation/URL, pattern chẩn đoán/liều hẹp, disclaimer, overlap lexical; có revision/refusal và publication gate |
| Provider metadata | Draft bị thay không làm mất `provider_attempted`, generation/model gốc và usage; không giữ nội dung bị từ chối |
| Safety | Rule override bỏ KG và generator; giữ bảy agent core và tám message thông thường |
| Timing | `duration_ms` đo quanh từng call; `elapsed_ms` tích lũy. Không lấy hiệu timeline rồi gán thành thời gian agent |
| Audit | File opt-in chỉ metadata/status/version/timing; không question/features/key hoặc decision payload |
| Inventory | `/api/capabilities` phân biệt implemented/configured/executed; source path/symbol được AST test đối chiếu; neural embedding/LangGraph/SSE công bố chưa có |
| Feature order | Predictor từ chối metadata có thứ tự feature khác SCHEMAS trước inference |
| UI source | `upgrade.js` parse bằng node thành công; text server được đưa vào DOM bằng textContent helper, không innerHTML |

## Giới hạn còn lại

Retrieval sufficiency và 35% lexical overlap là heuristic, không xác minh ngữ nghĩa hoặc an toàn y khoa toàn diện. Evaluation là bộ phát triển có điều chỉnh sau quan sát; Q21 còn bị bỏ sót và phải giữ trong báo cáo. Không diễn giải nâng cấp thành mọi chỉ số đều tăng.

Timing là call timing/timeline trong workflow, chưa là latency HTTP toàn tuyến hoặc benchmark tải. Backend ngoài, Docker/public deployment, ảnh trình duyệt, notebook độc lập và bố cục PDF cuối cần bằng chứng riêng do root tích hợp; pytest không thay các kiểm đó.

Không còn blocker trong phần runtime đã review sau sửa. Không có câu hỏi chặn.

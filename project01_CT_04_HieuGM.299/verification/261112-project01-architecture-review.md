# Project01: đối chiếu đặc tả Hybrid MAS

Ngày: 12/11/2026. Chỉ đọc và lập kế hoạch; không chạy lại benchmark. Nguồn: `project_architecture_multiagent_diabet_v1.pdf` (11 trang), README project, các section báo cáo và mã hiện có. Số trang dưới đây là thứ tự trang PDF, gồm trang đầu.

## Kết luận

Core đã thực hiện phần lớn đặc tả. Cải thiện có giá trị nhất là giải thích vì sao thiết kế là MAS, công bố contract đầy đủ và đưa một ca tích hợp kiểm chứng được. Chưa thấy nhu cầu thay 7 agent, tăng model/dataset hoặc huấn luyện lại. Báo cáo hiện tại mạnh về tính trung thực số liệu nhưng còn giống hồ sơ kiểm tra hơn một báo cáo giải thích thiết kế.

## Ma trận yêu cầu - hiện thực

| Đặc tả, trang | Bằng chứng hiện có | Đánh giá / cải thiện báo cáo |
|---|---|---|
| 6 lớp, tr.3-4 | `report/sections/02-architecture.md`, sơ đồ architecture.png; `app/main.py`, workflow, models, KB | Đủ; thêm bảng mỗi lớp - mã - dữ liệu quản lý để người đọc đối chiếu |
| 7 agent core, RL tùy chọn, tr.5-6 | `app/agents/roles.py`, `workflow.py`, `reporting.py`; `/api/catalog` công bố 7 tên | Đủ; phân biệt vai trò logic trong cùng tiến trình với agent tự chủ/phân tán |
| Đơn nhiệm, modularity, interface, evidence, failure, tr.5 | Các class `run`, structured_report; kiểm `tests/test_workflow.py` và `test_failure_paths.py` | Đủ; bảng hiện tại chỉ nêu trách nhiệm, thiếu I/O và trạng thái từng agent |
| M=(A,S,O,C,F), Ai:Xi→Yi, tr.5-6 | `Context` là trạng thái request; AgentResult là message; ReportWorkflow là hàm điều phối; observations là input từng vai trò | Chưa giải thích trong báo cáo; thêm mô hình trừu tượng gắn vào lớp/hàm thật, không chép công thức rỗng |
| Validate → DL → Rule → KG → tổng hợp → Explanation → Audit, tr.6-7 | `ReportWorkflow.run`, `_finish`; kiểm thứ tự 8 message trong `test_workflow.py` | Đủ; thêm sequence diagram và pseudocode gắn nhánh invalid/dependency/safety/cache/LLM |
| Message có id/agent/status/payload/evidence/version, tr.7-8 | `AgentResult`, `Context.emit`; request_id xuyên suốt | Đủ; ví dụ JSON hiện chỉ payload dataset nên chưa minh họa score/version/evidence thực |
| Tái dùng DL, schema, preprocessing, version, metric, tr.8-9 | models cdc/hospital legacy; Predictor; chương 3-4; SHA256 legacy | Đủ; giữ lựa chọn serving bằng validation/reuse, không đổi theo test |
| Query interpretation → entities → graph → chunks → ranking → sources, tr.9 | `app/knowledge/retrieval.py`, `neo4j_backend.py`; chương 5 | Đủ; nên thêm một chuỗi query→concept→chunk có ID thật, kèm backend thực |
| Structured report tách prediction/rules/evidence, tr.6 | `structured_report` còn có uncertainty/conflicts/limitations/human review | Đủ; thiếu ví dụ report thực được đọc và giải thích theo từng trường |
| Audit và đánh giá từng agent/toàn MAS, tr.3,5,10 | tests/workflow/failure, verification JSON; audit metadata | Có bằng chứng; thiếu bảng ca kiểm với điều kiện - hành vi mong đợi - file test/kết quả |
| RL trong mô phỏng, tr.9-11 | `policy.py`, policy-training.json; chương 6 ghi contextual bandit gamma=0 | Đủ, giữ nhãn tùy chọn; không cần đưa RL vào core report |
| Human review, uncertain/conflicting, sources, tr.10 | uncertainty/conflicts/review_flags; safety override; template khi thiếu dependency | Đủ theo phạm vi; báo cáo phải ghi conflicts là `not_assessed` nếu chưa có bộ kiểm mâu thuẫn ngữ nghĩa |

## Những điểm cần viết chính xác

1. **`elapsed_ms` là thời gian tích lũy**, không phải thời lượng riêng agent. `Context.emit` tính `(perf_counter()-context.started)*1000`. `MonitoringAgent.duration_ms` là tổng thời gian tới lúc audit. Có thể trình bày timeline hoặc hiệu hai mốc với giải thích; không gọi trường hiện tại là latency từng agent.
2. **8 message không phải 8 agent.** Workflow thường emit Coordinator hai lần, Data, DL, Rule, KG, Explanation, Monitoring. Tối đa 12 message trong `emit`; `max_steps=8` thuộc trace API cũ dùng `send`.
3. **Có hai luồng API.** `/api/report` là core 7 agent. `/api/chat` giữ vai trò lịch sử Safety/Retrieval/Policy/Education/Critic và policy trình bày. Không dùng trace chat để minh họa core 7 agent; `Coordinator` docstring "Five communicating roles" là mô tả cũ của chat, không đại diện toàn hệ.
4. **Không phải mỗi agent là LLM.** Data/Rule/Monitor xác định; DL neural inference; KG retrieval/graph; Explanation dùng LLM hoặc template; Coordinator quy trình hữu hạn. Đây là phân rã theo trách nhiệm, không phải hội thoại tự phát của 7 LLM.
5. **Safety nhánh report xảy ra sau DL** theo đặc tả. Nếu có safety, KG bị skipped và Explanation trả safety_rule, không gọi LLM. Nói "luật ưu tiên cách trình bày" chính xác hơn nói "luật chạy trước mọi agent".
6. **Chế độ suy giảm là kết quả hợp lệ có nhãn.** Neo4j cache → degraded; FPT thiếu/lỗi → template; model không nạp được → dependency_error/HTTP503; validation → HTTP422; audit ghi lỗi vẫn giữ report nhưng degraded.
7. **Monitoring bền vững chỉ có metadata** khi bật `AUDIT_LOG_PATH`; phản hồi message có payload prediction/evidence và không đồng nghĩa file log. Không tuyên bố toàn bộ trace được lưu bền vững mặc định.

## Bổ sung ưu tiên

### P1 - Lập luận MAS và contracts (chương 1-2)

Thêm định nghĩa Agent theo input→trạng thái/xử lý→output, đặc tính quan sát/hành động của nguyên mẫu; xác định mức tự chủ giới hạn. Định nghĩa M=(A,S,O,C,F) với A là 7 vai trò; S là Context + kết quả trung gian; O là dữ liệu được cấp cho từng vai trò; C là AgentResult/messages; F là ReportWorkflow.run. Bảng I/O cần: Data(raw schema)→validated/error; DL(valid features)→score/label/task/threshold/version; Rule(question/prediction/glucose)→flags/safety; KG(query)→evidence/inventory; Explanation(query/prediction/rules/evidence)→answer/generation/citations; Monitoring(context/status)→audit; Coordinator(request)→status/report/error/messages.

### P1 - Ca tích hợp thực (chương 6-7)

Dùng feature mặc định đã công bố là dữ liệu minh họa, câu hỏi công khai HbA1c. Lưu kết quả chạy local có ngày/phạm vi; nếu tắt FPT/Neo4j thì giữ rõ generation=template và backend=cache. Từ kết quả trích bảng ngắn score/task/threshold/version, rule IDs, evidence ID/URL/page, generation/citation, uncertainty/conflicts và thứ tự message. Không cần đưa toàn bộ JSON nhiều trang. Không gọi số đo local là kiểm public hay lâm sàng.

### P2 - Sơ đồ và ma trận kiểm thử

Sequence diagram cần các nhánh: invalid→Monitor→422; model unavailable→Monitor→503; safety→skip KG→safety explanation; bình thường→KG→aggregate→Explanation; dependency fallback có nhãn. Bảng ca kiểm trỏ `tests/test_workflow.py`, `test_failure_paths.py`, `results/failure-injection-verification.json`, `knowledge-fallback-verification.json` và kết quả pytest hiện có theo đúng ngày.

## Kiểm hoàn tất

- Bìa PDF cũ giữ nguyên, so ảnh/hash trước/sau.
- Nội dung mới có đường dẫn và ví dụ thật; kết quả lịch sử không đổi ngày.
- Không sửa trọng số hoặc benchmark để làm đẹp.
- Kiểm build/audit PDF và render trực quan; ZIP/manifest đồng bộ với PDF mới.
- Thay đổi code nếu có phải compile + test thích hợp; sửa báo cáo thuần không cần train lại.

## Câu hỏi chưa giải quyết

Không có câu hỏi chặn. Chưa có rubric/nhận xét chấm cụ thể; hướng cải thiện dựa trên yêu cầu gốc và khoảng cách giải thích của báo cáo hiện có.

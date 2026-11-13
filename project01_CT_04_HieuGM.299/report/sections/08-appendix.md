# PHỤ LỤC. HỒ SƠ KIỂM CHỨNG VÀ ĐỐI CHIẾU YÊU CẦU

## A.1. Ánh xạ đặc tả sang sản phẩm

Số trang dưới là trang vật lý của project_architecture_multiagent_diabet_v1.pdf (11 trang). “Đã có” mô tả chức năng kỹ thuật theo bằng chứng, không là chứng nhận lâm sàng. Các giả định khác đặc tả được nêu trực tiếp.

| Mục đặc tả / trang | Yêu cầu và hiện trạng | Nơi kiểm tra trong bài |
|---|---|---|
| 1.2 / tr.3 | Tái sử dụng DL: giữ hai serving model CDC/Hospital; benchmark mở rộng ở kho riêng | 1.3, 4.9; legacy-preservation.json |
| 1.2, 7.2 / tr.3,9 | KG giả định có sẵn: thực tế phải xây mới; Neo4j đã kiểm local, public dùng cache | 1.3, 5.3-5.4; DB_diabet.cypher, neo4j-verification.json |
| 2.1 / tr.3-4 | Sáu lớp: UI, API, điều phối, agent, model/knowledge, đánh giá | 2.2; app/main.py và app/static |
| 3.1-3.2 / tr.5 | Bảy vai trò, I/O và quyền ghi trạng thái, quyết định nội bộ hữu hạn | 2.1, 2.4, 2.10; roles.py, workflow.py, capabilities.py |
| 4 / tr.5-6 | M=(A,S,O,C,F), ánh xạ input/output của agent | 2.3; Context, AgentResult, ReportWorkflow |
| 5 / tr.6-7 | Workflow tuần tự; input sai phải dừng trước DL | 2.6, 6.7; test_workflow.py và request missing-feature |
| 6 / tr.7-8 | Message có request_id, agent, status, payload, evidence, model_version | 2.5; contracts.py; trace thật tại 6.7 |
| 7.1 / tr.8-9 | Kiến trúc DL, dữ liệu, tên/thứ tự feature, preprocessing, output/version, metric | Chương 3-4; metadata.json, predict.py |
| 7.2 / tr.9 | Diễn giải query, thực thể, graph, ranking, dẫn nguồn; thêm controller hữu hạn | 5.5, 5.9-5.11; retrieval.py, adaptive.py |
| 5-6 / tr.6-8 | Báo cáo tách các loại thông tin; thêm kiểm duyệt/sửa sau sinh | 6.3, 6.7-6.8; structured_report, review.py, /api/report |
| 3.1, 9 / tr.5,10 | Monitoring, kiểm thử từng thành phần và toàn hệ | 6.5, 7.3, 7.8; audit và verification |
| 8 / tr.9-10 | RL tùy chọn trong mô phỏng; không điều khiển điều trị | 6.6; policy.py, train-policy.py; tách core |
| 9 / tr.10 | Giao diện và báo cáo thực nghiệm | 7.9; notebook, API, ảnh UI và bảng benchmark |
| 10 / tr.10 | Nguồn có thể xem lại, giới hạn chẩn đoán/thuốc, nêu bất định | 1.4, 6.1-6.4, A.5; rules.py, uncertainty/conflicts |

Phần bổ sung tài liệu làm rõ lý thuyết, contract, sequence/lỗi, feature và ví dụ thực. Code 2.1 bổ sung quyết định retrieval/review, timing và registry có thể kiểm trực tiếp. Các cải tiến nội bộ vẫn theo khung bảy vai trò. Chưa có bằng chứng hoàn tất kiểm chứng ngữ nghĩa tổng quát, hệ phân tán tự chủ hoặc Neo4j production.

## A.2. Cấu trúc bàn giao

```text
notebook/project01-diacare.ipynb    Mã độc lập chạy từ trên xuống
app/ml/                           Database, dataset, training, inference
app/knowledge/                    Corpus, ontology, retrieval, generation
app/agents/                       Bảy agent, contracts, rules, workflow
app/static/                       Report, Chat, Benchmark, Graph, Knowledge, Technology
models/                           Serving weights và benchmark neural
results/benchmark/full/            72run, summary, scores, figures
results/*verification.json         Bằng chứng theo phạm vi/phiên bản
DB_diabet.cypher                  Seed graph mới có provenance
report/                           PDF, Markdown, sections, builder
bao-ve-project01.md                Câu hỏi bảo vệ và demo
.env.example                      Tên biến, không có key/password
```

## A.3. Năm câu cần trả lời ngay khi bảo vệ

Dùng mấy bộ dữ liệu? Bốn cohort độc lập cho học có giám sát; corpus Web/PDF là nguồn tri thức riêng. Không gọi 12 tài liệu là 12 dataset train DL.

Dùng mấy mô hình? Sáu loại: ba cổ điển, ba Deep Learning. Có 24 tổ hợp dataset-model,72 lượt do ba seed. Bốn serving model là bốn artifact đang được API nạp, không là bốn kiến trúc khác nhau.

Vì sao không chọn test cao nhất để deploy? Làm vậy dùng test tham gia lựa chọn và làm kết quả lạc quan. Pima/Early chọn validation; CDC/Hospital giữ artifact cũ để đúng yêu cầu tái sử dụng.

Có dùng Neo4j/LLM thật không? Neo4j local đã import/query thật và có verification; FPT gọi HTTPS thật có evidence/citation check. Render có backend nào phải đọc health/verification thực tế, không suy từ kết quả local.

Kết quả có chẩn đoán được không? Chưa. Quần thể nước ngoài, test nhỏ ở hai cohort, sigmoid chưa calibration Việt. Reviewer mới là bộ kiểm cấu trúc/nguồn/mẫu luật và lexical support, chưa chứng minh đúng y khoa. Core là nguyên mẫu học thuật có human review.

## A.4. Bảng kiểm trước khi nộp

Mở notebook và kiểm kernel mới; chọn full khi cần tái lập benchmark. Đọc kết quả full ở results, không thay bằng smoke. Kiểm PDF cover đúng tên/MSV/CT01/04, không còn tên người mẫu. Mở link demo, đối chiếu model_count/system_version; kiểm graph_backend và generation thực.

Loại .env thật, key/password, raw/database, runtime log và patient ID khỏi ZIP/Git/image. Kiểm manifest/CRC sau gói. Báo cáo kiểm thử ngày nào và phiên bản nào phải được ghi rõ; không đổi ngày của bằng chứng cũ để làm như đã chạy lại.

## A.5. Những việc chưa được chứng minh

Chưa có xác thực lâm sàng Việt Nam; chưa có external/temporal validation hay calibration production; chưa có nghiên cứu tác động chăm sóc. Chưa có benchmark tải/SLA. Chưa có đánh giá claim-level support lớn được chuyên gia chấm. SD ba seed không là uncertainty đầy đủ. Chế độ cache không là Neo4j production, citation hợp lệ không là sự thật y khoa.

## A.6. Điểm vào mã nguồn cho người kiểm tra

Contract sau trích từ app/agents/contracts.py, bỏ decorator/import để tập trung các trường. payload và evidence là object/danh sách JSON; client cần đọc status trước khi diễn giải nội dung.

```python
class AgentResult:
    request_id: str
    agent: str
    status: str
    payload: dict
    evidence: list
    model_version: str
    elapsed_ms: float
    duration_ms: float = 0.0
    decision: dict = field(default_factory=dict)
```

| Muốn kiểm tra | Điểm vào |
|---|---|
| Nhận request và mã HTTP | app/main.py: report; app/api_models.py: ReportRequest |
| Toàn bộ thứ tự điều phối | app/agents/workflow.py: ReportWorkflow.run và _finish |
| Nguồn của score, thứ tự feature | app/ml/predict.py: Predictor.predict; models/<cohort>/metadata.json |
| Luật và ưu tiên phản hồi | app/agents/rules.py: check; reporting.py: ExplanationAgent.run |
| Ranking và graph fallback | app/knowledge/retrieval.py: KnowledgeBase.retrieve, graph_evidence |
| Chính sách accept/retry/abstain | app/knowledge/adaptive.py: AdaptiveRetrieval.run |
| Prompt, HTTPS và citation gate | app/knowledge/generation.py: EvidenceGenerator.generate, validate_generated |
| Kiểm duyệt và sửa hữu hạn | app/knowledge/review.py: review_output, review_and_revise |
| Có dùng công nghệ nào, dùng ở đâu? | app/capabilities.py: FEATURES, AGENTS, inventory, usage; GET /api/capabilities |
| Tái tạo ví dụ Chương 6 | scripts/capture-report-cases.py; results/agent-upgrade-cases.json |
| Đánh giá thay đổi retrieval | scripts/evaluate-agent-upgrade.py; agent-upgrade-evaluation.json và bản v1 |
| Tái tạo bảng/sơ đồ/báo cáo | report/prepare-analysis.py, prepare-report.py, build-pdf.py |

Nguồn báo cáo và công cụ dựng được đóng gói cùng bài để có thể sửa tiếp. assets/original-cover.pdf là trang bìa gốc được giữ lại; builder thay trang đầu bằng trang này sau khi dựng nội dung. Kiểm render pixel trước/sau được dùng để xác nhận yêu cầu giữ nguyên bìa, thay vì chỉ so tên và mã sinh viên.

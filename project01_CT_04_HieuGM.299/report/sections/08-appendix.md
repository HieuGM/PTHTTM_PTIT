# PHỤ LỤC. HỒ SƠ KIỂM CHỨNG VÀ ĐỐI CHIẾU YÊU CẦU

## A.1. Ánh xạ đặc tả sang sản phẩm

| Yêu cầu từ kiến trúc | Sản phẩm |
|---|---|
| Tái sử dụng DL | models/cdc, models/hospital; legacy-preservation.json |
| Patient validation, dừng sớm | PatientDataAgent, ReportWorkflow, /api/report |
| KG Neo4j và RAG | corpus/ontology, DB_diabet.cypher, neo4j_backend.py |
| Contract có trạng thái/version | AgentResult, Context.emit, messages và request_id |
| Báo cáo prediction/rule/evidence riêng | structured_report và ExplanationAgent |
| Monitoring | Metadata audit; mặc định không ghi file/patient data |
| Đánh giá thành phần và hệ | 72 run, retrieval checks, Neo4j proof, pytest, notebook/API |
| RL tùy chọn | One-step contextual bandit mô phỏng, tách core |

## A.2. Cấu trúc bàn giao

```text
notebook/project01-diacare.ipynb    Mã độc lập chạy từ trên xuống
app/ml/                           Database, dataset, training, inference
app/knowledge/                    Corpus, ontology, retrieval, generation
app/agents/                       Bảy agent, contracts, rules, workflow
app/static/                       Report, Chat, Benchmark, Graph, Knowledge
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

Kết quả có chẩn đoán được không? Chưa. Quần thể nước ngoài, test nhỏ ở hai cohort, sigmoid chưa calibration Việt, RAG chỉ có kiểm citation cơ bản. Core là nguyên mẫu học thuật có human review.

## A.4. Bảng kiểm trước khi nộp

Mở notebook và kiểm kernel mới; chọn full khi cần tái lập benchmark. Đọc kết quả full ở results, không thay bằng smoke. Kiểm PDF cover đúng tên/MSV/CT01/04, không còn tên người mẫu. Mở link demo, đối chiếu model_count/system_version; kiểm graph_backend và generation thực.

Loại .env thật, key/password, raw/database, runtime log và patient ID khỏi ZIP/Git/image. Kiểm manifest/CRC sau gói. Báo cáo kiểm thử ngày nào và phiên bản nào phải được ghi rõ; không đổi ngày của bằng chứng cũ để làm như đã chạy lại.

## A.5. Những việc chưa được chứng minh

Chưa có xác thực lâm sàng Việt Nam; chưa có external/temporal validation hay calibration production; chưa có nghiên cứu tác động chăm sóc. Chưa có benchmark tải/SLA. Chưa có đánh giá claim-level support lớn được chuyên gia chấm. SD ba seed không là uncertainty đầy đủ. Chế độ cache không là Neo4j production, citation hợp lệ không là sự thật y khoa.

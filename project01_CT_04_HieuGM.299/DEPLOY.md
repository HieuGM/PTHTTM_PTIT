# Docker, Render, FPT Cloud và Neo4j

## Dịch vụ Render hiện có

[Demo](https://diacare-mas-hieugm299.onrender.com) · [API](https://diacare-mas-hieugm299.onrender.com/docs) · [Health](https://diacare-mas-hieugm299.onrender.com/health) · [Dashboard](https://dashboard.render.com/web/srv-dbm5dfgu01pc738ercq0)

| Cấu hình | Giá trị |
|---|---|
| Service | diacare-mas-hieugm299, srv-dbm5dfgu01pc738ercq0 |
| Workspace | Giáp Minh Hiếu's workspace, đã xác nhận |
| Runtime / plan / region | Docker / Free / Singapore |
| Repo / branch | HieuGM/PTHTTM_PTIT / main |
| Root Directory | Trống, gốc repo |
| Dockerfile | project01_CT_04_HieuGM.299/Dockerfile |
| Build context | project01_CT_04_HieuGM.299 |
| Env | APP_DATA_DIR=/tmp/diacare, OMP_NUM_THREADS=2, PORT=8000 |
| Process | Một worker Uvicorn, bind 0.0.0.0:8000 |

**Bản nâng cấp đã live lúc 14:40:42 ngày 06/11/2026 (giờ Việt Nam)**, commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0`. FPT Environment đã cấu hình riêng. HTTPS cuối đạt **30/30**, có sinh câu trả lời FPT thật. Lượt đầu 29/30 do một câu dùng template fallback được giữ trong `results/render-http-attempts.json`; chạy lại cùng bộ kiểm/câu hỏi đạt 30/30. Không xem đây là tỷ lệ thành công lâu dài của provider. Metadata và kiểm HTTPS nằm tại `results/render-deployment.json`, `render-http-verification.json`. Bản đầu commit 6eb79dc ngày 05/11 và 13 HTTP là bằng chứng lịch sử, không được dùng thay kiểm bản mới.

Dịch vụ được tạo trực tiếp qua MCP; Blueprint render.yaml ở gốc repo là cấu hình tái triển khai, chưa mặc nhiên là nguồn quản lý service hiện có. Dịch vụ dùng public Git repository URL nên cần trigger manual deploy theo commit sau khi push. Không coi deploy do cập nhật environment ở commit cũ là bản ứng dụng mới. Theo dõi đúng commit/deploy, chờ live rồi gọi HTTPS/health/report/catalog. Không tạo thêm service trùng tên. Free có thể ngủ, request đầu chậm; chưa có SLA/load benchmark.

## FPT AI Marketplace

Key/model đã điền private .env tại máy người học. Endpoint đã xác minh bằng tài liệu chính thức và HTTPS thật:

```dotenv
FPT_API_URL=https://mkp-api.fptcloud.com/chat/completions
FPT_BASE_URL=https://mkp-api.fptcloud.com
FPT_MODEL=<model ID trong tài khoản của bạn>
FPT_API_KEY=<chỉ đặt trong Environment hoặc private .env>
FPT_MAX_TOKENS=1200
FPT_TIMEOUT_SECONDS=45
```

Full URL ưu tiên; nếu chỉ có BASE thì app thêm /chat/completions. Gateway AI Marketplace này không tự thêm /v 1. Model ID lấy đúng catalog tài khoản được cấp phép. Không chép key vào notebook/report/chat/Git. Trên Render, thêm các biến tại Environment rồi save/redeploy; .env cục bộ không tự được deploy vì bị ignore.

FPT thực đã trả HTTP 200 và câu trả lời có citation. Metadata an toàn nằm trong `results/fpt-api-verification.json`. Đây là test provider/output, không chứng minh clinical correctness. Thiếu cấu hình/lỗi/citation sai thì dùng template có nhãn; không có evidence thì insufficient_evidence. API giới hạn token/timeout, không theo redirect.

Nguồn triển khai: [Render Deploys](https://render.com/docs/deploys).

Nguồn FPT: [FPT AI Marketplace API integration](https://ai-docs.fptcloud.com/api-reference/ai-marketplace/api-reference/api-integration-multimodal-model-text-md).

## Docker cục bộ

Chạy tại thư mục Project01:

```powershell
docker build -t diacare-hieugm299:2.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 --env-file .env diacare-hieugm299:2.0
```

Bỏ env-file để dùng template/cache. Image kèm weights/corpus, không train/tải raw tại startup, không cần GPU. .env không nằm trong image. APP_DATA_DIR chứa cache công khai sinh lại; bản demo không cần persistent disk.

Trong container, localhost là container đó. Dùng Docker network và tên container graph, hoặc host.docker.internal nếu hỗ trợ. Không dùng URI localhost cục bộ trên Render.

## Neo4j và seed mới

Neo4j Community 5.26 local Docker đã import/query thật từ DB_diabet.cypher:400 node,2545 edge; kiểm idempotence/cache parity đạt. KG được xây mới vì người học chưa có Neo4j/Cypher.

Cấu hình private .env hoặc Environment:

```dotenv
NEO4J_URI=bolt://<host có thể truy cập>:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<private>
NEO4J_DATABASE=neo4j
```

Dùng Neo4j Browser/cypher-shell import DB_diabet.cypher, hoặc `python scripts/load-neo4j.py --help` để xem tùy chọn của công cụ bảo trì. Query phục vụ dùng tham số và read session; read session không tự tạo ràng buộc RBAC của server. Production nên dùng credential quyền đọc phù hợp sau khi load seed bằng tài khoản quản trị.

Để Render dùng live graph, cần Neo4j/Aura có URI truy cập được từ Render và đã cấp phép. Không tạo mới tài nguyên trả phí trong luồng này. Thiếu kết nối thì app dùng sqlite_cache/degraded có nhãn. Graph UI vẽ snapshot corpus đóng gói, không gọi là direct live graph visualization.

## Kiểm tra và bảo mật

Kiểm compile/pytest, build image, gọi HTTP sau thay đổi. Chờ Render live rồi mở health/catalog kiểm bốn model, corpus version, graph backend và FPT configured. Gọi report để xem generation thực; configured không có nghĩa mọi request đều dùng LLM.

Không ship raw/database, patient ID, private .env, log hoặc notebook output có secret. Audit mặc định không ghi file; AUDIT_LOG_PATH chỉ ghi metadata. Một worker và OMP 2 hạn chế RAM/thread. Chưa đo tải nên không cam kết phục vụ nhiều người đồng thời.

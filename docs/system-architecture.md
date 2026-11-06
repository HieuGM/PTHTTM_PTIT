# Kiến trúc Agent02

`agent02/` là bài thực nghiệm cục bộ, đầu ra chính theo tên `agent02_CT_04_hieugm`. Không thay đổi bài Agent01 hoặc các tiểu luận.

| Thành phần | Vai trò và luồng dữ liệu |
|---|---|
| `code/reference_core.py` | `Config` → môi trường hai người bán → chọn đồng thời hành động → lợi nhuận nhị thức → Q-learning cập nhật; đối thủ luật không học. Giữ phép toán và RNG của mã mẫu, thêm đếm hành động. |
| `code/evaluation.py` | Q đã học → chính sách greedy đóng băng → trận RL-vs-rule riêng và trận rule-vs-rule riêng. Hai trận dùng chung mảng nhu cầu và uniform từng khách hàng để ghép cặp công bằng. |
| `code/agent02_experiment.py` | Điều phối baseline42 và sáu cấu hình×năm seed; đo chuyển chính sách baseline sang giảm giá5% và huấn luyện lại riêng. |
| `code/results_io.py` | Dữ liệu đo → JSON/CSV từng episode → mean/SD mẫu giữa các seed → hình cửa sổ100 episodes và lợi nhuận tích lũy. |
| `results/` | Giữ cấu hình, seed thực, Q/policy, tổng lợi nhuận, số hành động, train/evaluation, kết quả chuyển chính sách và hình. |
| `reference/`, `report/`, `notebook/` | Mã/đề tham khảo và sản phẩm giải thích; báo cáo/notebook đang tích hợp, chưa xác nhận QA tài liệu cuối. |

Seed môi trường train được truyền trực tiếp (`train_seed`), RNG agent = seed+10000; `config.seed=42` là giá trị mẫu được giữ lại. Đánh giá dùng demand seed=train seed+500000, sales seed=demand seed+1000000. Sampling số bán bằng tổng Bernoulli có cùng phân phối Binomial như mẫu. Đánh giá dùng deterministic argmax khi hòa; huấn luyện giữ random tie. Trạng thái cục bộ bốn giá trị thiếu hành động trước của chính mình và thời gian còn lại; đây là giới hạn mô hình, không phải bảo đảm Markov/hội tụ.

# Kiến trúc tiểu luận 03

`tieuluan03/` là gói báo cáo và thực nghiệm cục bộ, không phải dịch vụ web triển khai. Bài 01/02 cung cấp dữ liệu và kết quả kế thừa; không bị ghi đè.

| Thành phần | Vai trò và luồng dữ liệu |
|---|---|
| `code/cnn/` | Loader ảnh → CNN NumPy/Keras/PyTorch → kiểm chứng/smoke. CIFAR mới tách train/test theo tên batch; kết quả lịch sử có split cũ vẫn được ghi rõ. |
| `code/rnn/` | Elman/SimpleRNN kế thừa ba cách, đọc CSV bài 01; kết quả chính không huấn luyện lại. |
| `code/lstm/` | CSV → chia thời gian 70/15/15 → scaler train → cửa sổ 30 → NumPy/Keras-torch/PyTorch → dự đoán/metric so với naive. Cùng khởi tạo, SGD, 5 epoch; 329 tham số hiệu dụng. |
| `code/agents/` | Coordinator → truy hồi một miền → EvidenceCritic → ExtractiveResponder. Một tiến trình, luật xác định, tối đa bốn thông điệp; từ chối miền mơ hồ, lỗi công cụ hoặc hết ngân sách. |
| `results/` | JSON đo thật và kế thừa, checks, dự đoán, weights; hash nguồn hình ở `figure-provenance.json`. |
| `report/` | Section Markdown + JSON → hình/nội dung hợp nhất → Node `docx` → Microsoft Word xuất PDF → audit/contact sheets. |

Demo Agent sao chép kho/retriever nhỏ của bài 02 để tự chứa dữ liệu. Critic kiểm tra hợp đồng và nguồn, không xác minh đủ nghĩa; Q33/Q34 vẫn chấp nhận thẻ không trả lời đúng yêu cầu. Không có LLM, hàng đợi phân tán hoặc truy cập URL nguồn lúc trả lời.

CNN/RNN mặc định dùng dữ liệu dưới `tieuluan01/`; có biến `CNN_DATA_DIR`/`RNN_DATA_DIR` cho vị trí khác. LSTM đọc ba CSV bài 01. Tái dựng báo cáo kế thừa cần giữ cả `tieuluan01/` và `tieuluan02/`. Hướng dẫn và phụ thuộc đầy đủ: `tieuluan03/README.md`, `tieuluan03/requirements.txt`.

# Kiến trúc Tiểu luận Final và DiaCare MAS — 05/11/2026

`tieuluan_final_CT_04_HieuGM.299/` hợp nhất nội dung có hiệu đính thành bảy chương, bổ sung Deep Graph với GCN/MLP trên hai đồ thị, ba seed. `results/graph-results.json` và provenance giữ kết quả mới; kết quả ML/CNN/RNN/LSTM kế thừa vẫn có nhãn giới hạn. Báo cáo 104 trang được dựng mới, giữ bài mẫu và các bài trước.

`project01_CT_04_HieuGM.299/` là ứng dụng FastAPI phục vụ HTML/CSS/JavaScript cùng origin. Hai nhánh sử dụng artifact đã train; không tải dataset hoặc huấn luyện ở startup.

| Thành phần | Luồng và ranh giới |
|---|---|
| `scripts/`, `data/` | Tải/kiểm kê hai CSV → làm sạch → split CDC theo vector, Hospital theo bệnh nhân → scaler train → MLP và baseline → JSON/NPZ/hash |
| `app/ml/`, `models/` | Xác thực schema đầy đủ → chuẩn hóa từ metadata → MLP state_dict → score và ý nghĩa nhãn. Hai dataset có model/ngưỡng riêng, không gộp điểm |
| `app/knowledge/` | 24 thẻ có ID/nguồn/ngày kiểm tra → SQLite cards và TF-IDF trong RAM → top-k, điểm tương đồng |
| `app/agents/` | Coordinator → SafetyAgent; nhánh tri thức: RetrievalAgent → PolicyAgent → EducationAgent → CriticAgent; nhánh model: DataAgent → PredictionAgent → CriticAgent. Vai trò xác định trong một tiến trình, trace tối đa tám thông điệp |
| Rule/Policy | Quy tắc cảnh báo/từ chối chạy trước policy. Q-learning gamma=0 chọn abstain/brief/detail theo rubric mô phỏng; không điều khiển điều trị |
| `tests/`, `results/` | Kiểm thử thật với model/KB, 30 câu phát triển và các ca quy tắc; giữ sai sót truy xuất, không mô tả là xác thực lâm sàng |
| Docker/Render | Image chứa app, trọng số và kết quả, không raw/split dữ liệu; user không root, Uvicorn một worker, SQLite runtime. Docker Linux đạt 55/55 pytest và HTTP 13/13. Render Docker Free/Singapore đã live, URL công khai đạt HTTP 13/13 |

SQLite chỉ giữ tri thức, không giữ câu hỏi hoặc hồ sơ sức khỏe. Context và trace theo request ở RAM; lỗi validation chỉ trả vị trí/loại/thông điệp. Trả lời mặc định là trích xuất có nguồn, không gọi LLM. Critic kiểm tra ID/URL/hợp đồng, không chứng minh từng claim đầy đủ hoặc quyết định lâm sàng đúng.


## Cấu hình Render đã kiểm tra

Dịch vụ `srv-dbm5dfgu01pc738ercq0` phục vụ https://diacare-mas-hieugm299.onrender.com từ commit `6eb79dc0468bc76347b10c2ef0ab1a360974686a` của nhánh `main` trong `HieuGM/PTHTTM_PTIT`. Deploy được tạo trực tiếp qua MCP, dùng Root Directory trống và chỉ định Dockerfile/build context ở thư mục `project01_CT_04_HieuGM.299`.

Ứng dụng nhận `PORT=8000`, bind `0.0.0.0`, dùng `APP_DATA_DIR=/tmp/diacare` và `OMP_NUM_THREADS=2`. Render hiện kiểm tra TCP mặc định; endpoint `/health` được kiểm tra riêng trên HTTPS. KB SQLite được dựng lại từ JSON, không phụ thuộc đĩa bền vững và không lưu câu hỏi người dùng. Blueprint ở gốc repo mô tả lựa chọn cấu hình tương đương theo Root Directory, chưa được áp dụng để quản lý dịch vụ hiện tại.

Trạng thái live lúc 17:16 ngày 05/11/2026 và HTTP 13/13 được lưu tại `project01_CT_04_HieuGM.299/results/render-deployment.json` và `render-http-verification.json`. Chưa thực hiện benchmark tải hoặc xác thực lâm sàng qua triển khai này.

## Lối chạy notebook độc lập — 05/11/2026

Notebook là lối chạy chính cho bài thực nghiệm theo lựa chọn mới của người dùng; Docker/Render tiếp tục phục vụ ứng dụng DiaCare bằng artifact đã kiểm chứng. Mỗi notebook chứa mã trực tiếp trong ô, không cần source tree hoặc module `.py` của bài. Các script dựng notebook là công cụ bảo trì, không tham gia luồng Run All.

| Notebook | Luồng và trạng thái |
|---|---|
| `project01_CT_04_HieuGM.299/notebook/project01-diacare.ipynb` | Cài dependency thiếu → tải hai CSV UCI thật → kiểm kê/làm sạch/split → scaler train → hai MLP và baseline → metric/biểu đồ → KB/schema/câu hỏi nhúng → luật/policy/MAS → demo/API và assert. Full mặc định tối đa 25 epoch, smoke 2 epoch trên cùng toàn bộ dữ liệu/split. Đã chạy độc lập full, 55 assert notebook đạt |
| `tieuluan_final_CT_04_HieuGM.299/notebook/tieuluan-final.ipynb` | ML cơ bản/toán/gradient → CNN/RNN/LSTM NumPy–PyTorch–Keras → GCN/MLP hai đồ thị → retrieval/đa agent. Sáu CSV có nguồn/hash được nhúng; ảnh và Cora tải nguồn thật khi thiếu cache. Smoke mặc định, full có cấu hình riêng. Đã chạy đủ 45 ô mã smoke CPU, 43 lượt mô hình, 34 câu Agent và 5 ca tích hợp; không thay kết quả benchmark full/PDF |

Project01 ghi dữ liệu tải về, model và kết quả mới dưới `diacare-notebook-output/`; Final dùng `notebook-output/final-<mode>/`. Hai luồng không ghi đè kết quả `results/`, trọng số triển khai hoặc PDF cũ. Thư mục đầu ra sinh lại, cache, CSV y tế gốc và ID bệnh viện bị loại khỏi Git/image/ZIP bàn giao; notebook có thể giữ output nhúng và bằng chứng kiểm thử phù hợp. `.dockerignore` của Project01 loại cả `notebook/` để việc bổ sung notebook không đổi nội dung image ứng dụng.

Kiểm chứng notebook dùng kernel mới, không có source module/model/KB ngoài `.ipynb`; cache dữ liệu thật nếu tái sử dụng phải ghi rõ nguồn/hash. Project01 đã chạy full và smoke từ thư mục chỉ có notebook, tải UCI trực tiếp. Final bắt đầu từ notebook riêng, tải MNIST/Fashion thật; sau khi ngắt tải CIFAR chậm, lượt hoàn tất dùng cache ảnh xác minh checksum. 55 assert notebook Project01, 55 pytest ứng dụng và 13 kiểm tra HTTP là ba phạm vi khác nhau. Bộ 30 câu phát triển/11 ca an toàn vẫn có giới hạn cũ; chạy lại notebook không tạo bằng chứng lâm sàng hoặc thay số liệu PDF.

## 06/11/2026 - Kiến trúc Project01 theo PDF Hybrid MAS

Phần này thay mô tả Project01 ngày05/11 ở trên; Final và các bài khác giữ nguyên.

Bảy agent cốt lõi: Patient Data, DL Prediction, Rule-Based, KG/RAG, Coordinator, Explanation, Monitoring. `ReportWorkflow` điều phối request features+question, Data sai dừng trước DL; hợp đồng có request_id/agent/status/payload/evidence/model_version/latency. Report tách dự đoán, luật, evidence, giải thích, bất định/xung đột/giới hạn. Audit mặc định không ghi file và không lưu feature/câu hỏi/key.

ML: CSV thật→rawSQLite→SELECT làm sạch/chia→preparedSQLite→SELECT cung cấp mọi fit. Bốn cohort CDC/Hospital/Pima/Early; sáu loại model, ba seed,72 run. Split cố định, median/scaler chỉ train; checkpoint/ngưỡng bằng validation.11 artifact CDC/Hospital bảo toàn; serving cũ tái sử dụng, benchmark mới lưu riêng. Pima/Early mới chọn DL bằng validation AUC. Nhãn/cohort khác nhau, không gộp AUC để xếp hạng chung.

Knowledge:12 document tải thật(7 WHO/NIDDK+4Vinmec+1 PDF Việt77 trang),14reference-onlyrecord,340 chunk đã gồm24 thẻ,34 concept,2160 MENTIONS,19 relation chuyên môn. Neo4j local import/query thật400 node/2545 edge, kiểm idempotence/cache parity. Query read session không thay RBAC server. Graph UI là snapshot corpus; retriever dùng live Neo4j khi có kết nối, fallback sqlite_cache có nhãn.

Retriever dùng word/characterTF-IDF, LSA32 và graph boost; LSA không là neural embedding. Trên22câu phát triển goldthẻ, lexicalR@1=.9545/MRR=.9773, hybridR@1=.9091/MRR=.9470; R@3=1 cả hai. Không tuyên bố graph tốt hơn baseline. Tám câu nguồn Vinmec mới có lexicalR@3=.875/hybrid=.5, gold hẹp theo tên document; không là clinical validation.

FPT AI Marketplace full endpoint `https://mkp-api.fptcloud.com/chat/completions`, cấu hình environment. Đã gọi HTTPS thật có output/citation, metadata an toàn trong results/fpt-api-verification.json. Validator kiểm ID/inline, không chứng minh claim-level support. Thiếu/lỗi FPT→template; thiếu Neo4j→cache/degraded. Neo4j local không đồng nghĩa production trên Render.

Notebook mới tiếp tục là lối chạy chính, native inline cells và output riêng; kiểm fresh kernel theo artifact cuối. Trạng thái public Render đọc verification mới nhất sau deploy; bằng chứng13 HTTP/55 pytest ngày05/11 thuộc phiên bản cũ. RL contextual bandit vẫn chỉ là mở rộng mô phỏng, không thuộc bảy agent core và không điều trị.

### Artifact và vận hành bản nâng cấp - 06/11/2026

Notebook 61 ô/51 ô mã/25 mô-đun source inline thực thi 72 lượt fit, 80 kiểm tra ML và 68 API trong kernel mới, dùng cache nguồn thật có hash; 211,575 giây, không import file app cục bộ. Lượt full tải nguồn 339,18 giây được tách riêng.

Render live 14:40:42 ngày 06/11 giờ Việt Nam từ commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0`. Dịch vụ public Git URL dùng manual deploy; deploy commit cũ do đổi env không là mã mới. FPT Environment cấu hình riêng. Neo4j production không được suy từ bằng chứng local. Metadata và từng lượt kiểm HTTPS trong results là nguồn trạng thái; LLM có thể fallback dù một lượt grounded đã thành công.

Public HTTPS cuối 30/30 đạt, có FPT sinh thật; lượt đầu 29/30 với một template fallback được giữ trong render-http-attempts.json. Chạy lại cùng câu hỏi/bộ kiểm đạt 30/30; không suy thành SLA hoặc provider luôn thành công.

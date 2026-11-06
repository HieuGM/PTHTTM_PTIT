# Nhật ký thay đổi

## 29/10/2026 — Agent02

- Thêm `agent02/code/` từ mã tham khảo đề Agent02: môi trường thương mại điện tử, Q-learning và agent luật; giữ RNG/đồng thời hành động/cập nhật terminal của mẫu. Bổ sung thống kê hành động, dữ liệu từng episode, đánh giá tách khỏi huấn luyện và đầu ra JSON/CSV/PNG.
- Chạy đủ 31 lượt: baseline seed42, sáu cấu hình trên seed11/22/33/44/55; mỗi lượt 5.000 episodes×20 bước, đánh giá 500×20. Ba learning rate .01/.10/.50; epsilon giảm theo mẫu và cố định .05/.30; độ bền giảm giá từ 20% xuống 5% với huấn luyện lại và chuyển nguyên chính sách baseline.
- Đánh giá RL-vs-rule và rule-vs-rule trong các trận riêng với cùng nhu cầu và cùng số ngẫu nhiên khách hàng; Q đóng băng, không khám phá, tie dùng argmax. Huấn luyện vẫn giữ random tie của mẫu. Cấu hình JSON giữ `config.seed=42` theo mẫu; seed thực tế ghi riêng tại `train_seed`, `agent_seed` và seed đánh giá.
- Lợi nhuận/bước trung bình±SD mẫu năm seed: baseline35.0728±0.1456, alpha.50 33.7930±1.8390, epsilon.30 28.8672±3.8254; giảm giá5% học lại36.9318±0.4339, chuyển baseline35.0728±0.1456. Đây là mô phỏng theo giả thiết đề; không kết luận RL tốt hơn trong mọi thị trường.
- Đã compile và đối chiếu 100 episodes seed42 với mã nguyên gốc, Q và mọi trường kết quả gốc bằng nhau; báo cáo/notebook và kiểm tra tài liệu cuối đang do root tích hợp.

## 23/10/2026 — Agent01

- Tạo bài `agent01/` theo `agent01.md`, tên đầu ra `agent01_CT_04_hieugm`: MD/DOCX/PDF, PDF 6 trang; ảnh mã và đầu ra notebook được chèn vào báo cáo.
- Notebook `agent01/notebook/agent01_CT_04_hieugm.ipynb` đã chạy đủ 8 ô mã, minh họa 5 loại Agent theo phân loại IBM. Mã tự viết để minh họa, không phải mã nguyên văn IBM; không dùng LLM hoặc cloud.
- Kết quả `agent01/results/agents-results.json` ghi 9 nhóm assert đạt. Q-learning chạy 1.000 episodes, seed 42; trên đồ thị nhỏ trong bài, chi phí đường đi giảm từ 10 xuống 6. Kết quả này chỉ áp dụng cho môi trường minh họa.
- Hoàn tất kiểm thử độc lập từ kernel mới, review mã/tài liệu và kiểm tra trực quan 6 trang. Cả 15 kiểm tra tài liệu đạt tại `agent01/report/preview/audit.json`; báo cáo tester/reviewer ở `plans/reports/*-20261023-agent01.md`. Gói nộp `agent01_CT_04_hieugm.zip` chứa PDF, Word, notebook có output, ảnh và nguồn dựng lại.

## 23/10/2026 — Tiểu luận 03

- Tạo `tieuluan03/` để hợp nhất bài 01 và 02 thành sáu chương; giữ nguyên hai bài trước. Nguồn báo cáo: `tieuluan03/report/sections/` và `tieuluan03/report/tieuluan03_CT_hieugm_299.md`.
- Bổ sung CNN ba cách triển khai, kiểm chứng gradient/autograd, sửa loader CIFAR đọc batch theo tên và smoke MNIST thật. Bảng benchmark chính vẫn là kết quả kế thừa, có nhãn giới hạn split/ngân sách.
- Bổ sung LSTM NumPy BPTT, PyTorch và Keras backend torch; gradient check, parity, huấn luyện thật trên VNINDEX/AMZN/vàng với cùng cấu hình. Kết quả, trọng số và dự đoán ở `tieuluan03/results/lstm-*`. LSTM không vượt naive theo RMSE trong lượt chạy này.
- Bổ sung hệ nhiều vai trò xác định có trace và giới hạn bước; không dùng LLM. Trên 34 câu kế thừa: Recall@3=1 trên 28 câu có đáp án; từ chối đúng 4/6 câu không đáp án; giữ hai lỗi Q33/Q34. Xem `tieuluan03/results/agents-results.json`.
- Tạo hình từ JSON, ghi nguồn/hash trong `tieuluan03/results/figure-provenance.json`; thêm bảng hàm I/O, hướng dẫn chạy và tái tạo tại `tieuluan03/README.md`.
- Hoàn tất MD/DOCX/PDF cùng tên gốc `tieuluan03_CT_hieugm_299`, PDF 93 trang. Tester/reviewer đã hoàn tất; sửa nhận định quá mức ở chương 2 và định nghĩa Recall đa ID ở chương 5. Cả 12 kiểm tra PDF đạt, đã xem các trang bảng/mã/công thức và hệ đa Agent.

Không triển khai cloud/Docker, không đánh giá sinh LLM, không huấn luyện lại benchmark RNN/CNN đầy đủ của bài 01.

## 29/10/2026 — Hoàn tất giao nộp Agent02

- Báo cáo PDF 14 trang đủ 10 câu; Markdown chỉnh sửa được, notebook 6 ô mã đã chạy và HTML.
- Cả 6 nhóm kiểm thử số và 14 kiểm tra tài liệu đạt; reviewer không còn vấn đề cần sửa; đã xem đủ 14 trang.
- Gói agent02_CT_04_hieugm.zip có mã, kết quả 31 lượt chạy, đề và nguồn mẫu, manifest SHA256; kiểm tra ZIP và chạy thử độc lập sau giải nén đều đạt.

## 29/10/2026 — Sửa bìa Agent02 theo mẫu

- Bìa theo A01_06_linhpm.488.pdf, giữ nguyên khung, logo PTIT và bố cục; Assignment 02, Giáp Minh Hiếu, B23DCCN299.
- Đã xem bìa mới, kiểm tra 13 trang nội dung phía sau giống hệt ảnh render cũ; 17 kiểm tra tài liệu đạt. Cập nhật ZIP và manifest SHA256.

## 30/10/2026 — Gộp toàn bộ code Agent02 vào notebook

- Thay notebook phụ thuộc module cục bộ bằng một file độc lập chứa toàn bộ môi trường, agent, training, evaluation, thống kê, biểu đồ và điều phối31lượt.
- Chạy từ kernel mới trong thư mục trống,17ô thành công,31lượt đầy đủ mất476.54giây;5ảnh PNG nhúng, bảng thống kê và Q-table có output thật.
- Giữ nguyên thuật toán/số liệu; cập nhật HTML, mô tả notebook trong README/PDF và góiZIP.

## 05/11/2026 — Tiểu luận Final và Project01

- Hoàn thành `tieuluan_final_CT_04_HieuGM.299`: báo cáo 104 trang, bảy chương, bổ sung Deep Graph. Thực nghiệm GCN/MLP trên hai đồ thị với ba seed; giữ phân biệt số đo mới và kết quả kế thừa trong nguồn/hash.
- Tạo `project01_CT_04_HieuGM.299` cho DiaCare MAS. Hai nguồn CDC 253.680 bản ghi và Hospital 101.766 lượt; sau làm sạch còn 226.342 và 101.763. CDC tách vector đặc trưng, Hospital tách patient_nbr; scaler chỉ fit train. Hai nhiệm vụ khác nhãn, không dùng như external validation của nhau.
- Huấn luyện hai MLP 64–32–16 cùng Logistic/majority baseline, lưu state_dict, metadata và dự đoán test. Test ROC-AUC MLP CDC 0,82743, Hospital 0,63340; không diễn giải thành chẩn đoán hoặc hiệu quả lâm sàng.
- Bổ sung KB 24 thẻ tiếng Việt/19 nguồn chính thức, SQLite và TF-IDF; điều phối bảy vai trò cùng Coordinator, trace tối đa tám bước, luật ưu tiên và giới hạn thuốc. RL một bước chỉ chọn kiểu trình bày theo rubric mô phỏng, không học từ bệnh nhân.
- Kiểm tra 30 câu phát triển: Recall@1 21/22, Recall@3 22/22, MRR@3 0,97727; 8/8 câu âm được từ chối. Giữ ca Q22: thẻ đúng ở hạng 2 nhưng câu ngắn trích nguồn hạng 1 chưa cụ thể nhất. Bộ quy tắc riêng đạt 11/11; không coi là kiểm định độc lập.
- Sửa kết nối SQLite chưa đóng, ép kiểu bool/chuỗi số và lỗi serialize validation với NaN/Infinity; phản hồi validation không echo dữ liệu nhập. Bộ tích hợp hiện có 55 test, gồm năm regression mới sau lượt 50/50 ban đầu.
- Thêm Dockerfile, dependency lock, cấu hình Render và tài liệu triển khai theo yêu cầu Docker+Render. Image đầu tiên đã build; build cập nhật gặp đầy ổ C. Kiểm tra HTTP container cuối, PDF Project01, README và gói nộp đang do root hoàn thiện; chưa xác nhận deploy public Render.
- Thông tin bìa đã xác nhận: Giáp Minh Hiếu/B23DCCN299, PGS. TS. Trần Đình Quế, CT01, nhóm 04. Dựng bìa mới; không ghi đè bài mẫu Nguyễn Tự Kiên hoặc bài trước.


### Bằng chứng Docker cuối — 05/11/2026

Build đúng Dockerfile trên Docker Engine29.9.2 trong WSL2 riêng lưu ở D. Container healthy, 55/55pytest và 13/13HTTP;18tệp app khớp hash nguồn. Gói độc lập sau giải nén chạy55/55test. DockerDesktopgốc không sửa VHD sau lỗi IO lúc C đầy; engine riêng dùng cho kiểm chứng. Render chưa phát hành public. Báo cáo Project25trang,15/15audit tự động; rà ảnh cuối trước đóng ZIP.


### Hoàn tất bộ nộp — 05/11/2026

Project01: PDF25trang đã duyệt toàn bộ ảnh trang,15/15audit; ZIP94tệp,CRC/SHA256đạt. Final: PDF104trang,ZIP159tệp,CRC/SHA256đạt. DockerDesktopgốc đã khởi động lại thành công sau khi C có dung lượng (Engine29.6.1), không sửa/xóaVHD. Demo kiểm chứng riêng vẫn chạy tại localhost:8012; publicRender chưa tạo do chưa có tài khoản kết nối.


### Triển khai DiaCare công khai — 05/11/2026

- Tạo dịch vụ `diacare-mas-hieugm299` bằng MCP tại workspace đã được người dùng xác nhận; runtime Docker, gói Free, vùng Singapore. Không thay đổi các dịch vụ cũ khác; người dùng tự xóa một dịch vụ để giải phóng hạn mức.
- Deploy `dep-dbm5dgou01pc738erfu0` từ commit `6eb79dc0468bc76347b10c2ef0ab1a360974686a` đã `live` lúc 17:16 giờ Việt Nam. URL: https://diacare-mas-hieugm299.onrender.com.
- Kiểm tra URL công khai đạt 13/13: frontend/tài nguyên tĩnh, KB, hai mô hình, nguồn trích dẫn, cảnh báo, input thiếu và NaN, từ chối ngoài chủ đề. Bằng chứng: `project01_CT_04_HieuGM.299/results/render-http-verification.json` và `render-deployment.json`.
- Dịch vụ hiện dùng Root Directory trống, Dockerfile Path `project01_CT_04_HieuGM.299/Dockerfile`, Docker Build Context `project01_CT_04_HieuGM.299`, `PORT=8000`. Render dùng TCP readiness mặc định; `/health` được kiểm tra riêng qua HTTPS. Blueprint trong repo là cấu hình tái triển khai, không phải nguồn cấu hình đã áp dụng của dịch vụ MCP này.
- Cập nhật README, DEPLOY, roadmap, kiến trúc và kế hoạch theo bằng chứng live. Báo cáo Project01 vẫn 25 trang sau bổ sung URL, đạt 15/15 audit và kiểm tra ảnh các trang thay đổi; root phụ trách dựng lại ZIP và push tài liệu với `[skip render]`.

## 05/11/2026 — Bổ sung hai notebook độc lập

- Người dùng xác nhận chỉ bổ sung Final và Project01, mỗi bài một notebook; ưu tiên notebook là lối chạy chính cho các project sau. Mã nằm trực tiếp trong ô, không gọi wrapper `.py` của bài. Script dựng notebook chỉ phục vụ bảo trì.
- Project01 có `notebook/project01-diacare.ipynb`, 34 ô gồm 25 ô mã: tải hai CSV UCI thật, làm sạch/chia dữ liệu, hai MLP và baseline, biểu đồ, KB/luật/policy/MAS, demo và API. Đã chạy full trong thư mục sạch chỉ có notebook, tối đa 25 epoch/mô hình, 111,47 giây; 55 assert notebook đạt. Đánh giá gồm 30 câu phát triển và 11 ca an toàn, không phải kiểm định độc lập. Bộ 55 pytest ứng dụng là bằng chứng riêng trước đó.
- Hoàn thành notebook Final 77 ô/45 ô mã: ML cơ bản, gradient, CNN/RNN/LSTM ba cách triển khai, hai đồ thị, retrieval và đa agent. Sáu CSV thật được nhúng có SHA256; ảnh/Cora lấy nguồn thật. Smoke CPU cuối chạy đủ 43 lượt mô hình trong 87,94 giây, 34 câu Agent và 5 ca tích hợp. Tái sử dụng ảnh có checksum sau khi ngắt lượt tải CIFAR chậm; không ghi nhận đó là lỗi thuật toán hoặc lượt benchmark full.
- Project01 chạy lại bản cuối sau sửa kiểm tra phiên bản Pydantic/FastAPI và Torch CPU: 25 ô mã đạt trong 46,14 giây, 55 assert notebook và 21 kiểm tra độc lập đều đạt. Notebook đã push trong commit `7838b76` với `[skip render]`; có liên kết Colab trong README repo.
- Đầu ra notebook được tách sang `notebook-output/` hoặc `diacare-notebook-output/`; cache/CSV y tế/ID và artifact sinh lại không đưa vào image hoặc gói nộp. Project01 đã loại notebook và đầu ra notebook khỏi Docker build context.
- Đợt bổ sung này giữ nguyên PDF Final 104 trang, PDF Project01 25 trang, kết quả đã nộp và dịch vụ Render đang chạy. Tester/reviewer hoàn tất; Final có thêm 73 kiểm tra artifact độc lập. Bản định dạng cuối giữ chính xác AST và toàn bộ output của 45 ô đã chạy. Hai ZIP và manifest được dựng lại, kiểm CRC/SHA256; số tệp ZIP ở các mốc trước là lịch sử trước khi thêm notebook.

## 06/11/2026 — CSV để đọc dữ liệu

Xuất riêng `csv-xem-du-lieu/cdc.csv` (226.342 dòng, 23 cột) và `hospital.csv` (101.763 dòng, 12 cột) từ các mảng raw của Project01. Giữ đủ đặc trưng trước chuẩn hóa, nhãn và split train/validation/test; UTF-8 BOM để mở Excel. Đã kiểm tra roundtrip toàn bộ giá trị/nhãn/split. NPZ, notebook, mô hình, gói nộp và Render giữ nguyên; không đưa các bản CSV này lên Git.

## 06/11/2026 - Nâng Project01 theo kiến trúc Hybrid MAS

- Bốn cohort học có giám sát, SQLite thật cung cấp SELECT cho fit; CDC/Hospital/Pima/Early, làm sạch và chống rò rỉ trước split. Vinmec là văn bản KB/RAG, không gọi là patient dataset để train.
- Sáu loại model×ba seed,24dataset-model,72 run full thật. Mean/sampleSD trong từng cohort; không xếp hạng AUC khác task. Tổng fit+evaluate145,588 giây, elapsed23,449 giây là invocation resume riêng. Khắc phục copy2timestamp trên bind-mount bằng copyfile, không đổi thuật toán;54 record được hash verify trước18 run tiếp.
- Giữ nguyên11 artifact legacy CDC/Hospital; benchmark mới riêng. Pima/Early chọn DL bằng validation AUC. Ghi config/score/hash/env; không ship câyRF/HGB lớn, giữ phương án refit.
- Bổ sung bảy agent cốt lõi, structured messages/request_id/status/version, dừng sớm và report. FPT AI Marketplace endpoint đã xác minh, kiểm API thật có citation và không lưu khóa; template/cache fallback có nhãn.
- Corpus12tài liệu tải thật gồm4 Vinmec Web và1 PDF Việt lịch sử77 trang, cùng7 WHO/NIDDK;340 chunk gồm24 thẻ,34 concept,2160 MENTIONS,19 relation chuyên môn.14URLrecord chỉ tham chiếu được đếm riêng.
- Neo4j local400 node/2545 edge import/query/idempotence/cacheparity thật; GraphUI là snapshot, retrieval live khi kết nối. Readsession không là RBAC. Kiểm retrieval giữ cả lexical tốt hơn hybrid ở bộ cũ và lỗi của tám câu Vinmec mới.
- Viết lại báo cáo/README/deploy/modeldocs và38Q&A bảo vệ. Notebook độc lập và finalDocker/Render verification theo artifact cuối được cập nhật riêng. Không đổi tiểu luậnFinal.

### Bằng chứng cuối Project01 - 06/11/2026

- Notebook 61 ô/51 ô mã/25 mô-đun inline chạy full 72 lượt fit, 80 kiểm tra ML và 68 API, 211,575 giây. Kernel mới không có source app, có raw cache thật/hash; lượt full tải nguồn trước đó 339,18 giây được ghi riêng.
- 102 pytest, kiểm độc lập 72 run/144 bộ metric/36 checkpoint/24 summary/11 hash legacy; 24 kiểm tra trình duyệt desktop/mobile.
- Render commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0`, live 14:40:42 ngày 06/11 giờ Việt Nam. FPT vars được chuyển riêng qua Environment, không có key trong Git. Public Git URL service cần manual deploy theo commit; push không tự chứng minh deploy.
- Báo cáo 26 trang/bảy chương, 24 hàng mean/SD và bốn hình benchmark, 38 Q&A. Nguồn Web/PDF/Vinmec và giới hạn được ghi rõ; PDF audit/PNG review và metadata HTTPS/ZIP theo artifact cuối. Giữ cả lần gọi public LLM fallback để phản ánh độ ổn định thực tế.

Public HTTPS cuối 30/30 đạt, có FPT sinh thật; lượt đầu 29/30 với một template fallback được giữ trong render-http-attempts.json. Chạy lại cùng câu hỏi/bộ kiểm đạt 30/30; không suy thành SLA hoặc provider luôn thành công.

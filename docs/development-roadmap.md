# Tiến độ Agent02

Cập nhật 29/10/2026. Kế hoạch: `plans/261029-agent02/plan.md`.

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Môi trường và hai loại agent | Xong; giữ thuật toán/RNG huấn luyện mẫu, bổ sung đếm hành động | `agent02/code/reference_core.py` |
| Thực nghiệm A–E và kiểm tra độ bền | Xong 31 lượt đầy đủ, mỗi lượt 5.000×20 bước train, 500×20 bước đánh giá | `agent02/results/*-seed-*.json`, `run.log` |
| So sánh nhiều seed, biểu đồ và dữ liệu gốc | Xong; sáu cấu hình, năm seed; baseline riêng seed42 | `agent02/results/summary.json`, `comparison-summary.csv`, PNG và CSV |
| Đối chiếu mã tham khảo | Đạt Q và toàn bộ trường output gốc bằng nhau trên 100 episodes seed42 sau định dạng | `agent02/code/reference_core.py`, `agent02/reference/` |
| Báo cáo, notebook và kiểm tra giao nộp | Xong PDF 14 trang, notebook độc lập 17 ô đã chạy đủ31lượt; 14 kiểm tra tài liệu đạt, đã xem đủ trang; ZIP có hash và kiểm thử sau giải nén | `agent02/report/`, `agent02/notebook/`, kế hoạch |

# Tiến độ Agent01

Cập nhật 23/10/2026. Đề bài: `agent01.md`.

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Tổng hợp tài liệu, nội dung AI Agent | Đã dựng bản bài | `agent01/report/agent01_CT_04_hieugm.md` |
| Notebook minh họa 5 loại Agent theo IBM | Đã chạy 8 ô mã; mã tự viết, không chép nguyên văn IBM; không LLM/cloud | `agent01/notebook/agent01_CT_04_hieugm.ipynb` |
| Kiểm chứng thực nghiệm | 9 nhóm assert đạt; Q-learning 1.000 episodes, seed 42; chi phí 10 → 6 trên đồ thị nhỏ | `agent01/results/agents-results.json`, notebook |
| MD/DOCX/PDF và ảnh notebook | Đã dựng, PDF 6 trang | `agent01/report/agent01_CT_04_hieugm.{md,docx,pdf}`, `agent01/results/screenshot-manifest.json` |
| Kiểm tra tài liệu tự động | Các kiểm tra hiện có đạt | `agent01/report/preview/audit.json` |
| Kiểm thử độc lập, review và visual audit | Hoàn tất; fresh kernel 8 ô mã, 9 nhóm assert; 15/15 kiểm tra tài liệu đạt; đã xem 6 trang | `plans/reports/tester-20261023-agent01.md`, `plans/reports/reviewer-20261023-agent01.md`, `agent01/report/preview/` |

# Tiến độ tiểu luận 03

Cập nhật 23/10/2026. Kế hoạch chi tiết: `plans/261023-tieuluan03/plan.md`.

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Kiểm kê và kế thừa bài 01/02 | Xong | `tieuluan03/results/legacy-*-results.json` |
| Mã CNN/RNN ba cách; LSTM mới | Xong | `tieuluan03/code/{cnn,rnn,lstm}/` |
| Chạy LSTM và kiểm chứng | Xong | `lstm-results.json`, `lstm-checks.json`, weights/predictions trong `tieuluan03/results/` |
| Demo đa vai trò, kiểm thử nhánh lỗi | Xong | `tieuluan03/code/agents/`, `agents-results.json` |
| Nội dung sáu chương, hình, tài liệu tham khảo, README | Đã hợp nhất | `tieuluan03/report/sections/`, `figure-provenance.json`, `tieuluan03/README.md` |
| Dựng ba định dạng đầu ra | Xong, PDF 93 trang | `tieuluan03/report/tieuluan03_CT_hieugm_299.{md,docx,pdf}` |
| Tester, code-reviewer và kiểm tra PDF cuối | Xong | Báo cáo trong `plans/reports/`; 12 kiểm tra tài liệu đều đạt tại `report/preview/audit.json`; đã xem contact sheets |

Phạm vi giữ nguyên sáu chương theo đề. Keras mới chạy trên backend torch; các phép so sánh cũ khác cấu hình được gắn giới hạn. Không có mốc triển khai dịch vụ hoặc hạn nộp suy đoán từ ngày 23/10.

## 30/10/2026 — Notebook Agent02 độc lập

Đã gộp toàn bộ mã vào agent02_CT_04_hieugm.ipynb;17ô mã thực thi tuần tự trong thư mục trống,31lượt full,5biểu đồ nhúng. Không cần filePython hay kết quả tính trước đi kèm.

# 05/11/2026 — Tiểu luận Final và Project01

Kế hoạch: `plans/261105-final-and-diabetes/plan.md`. Sinh viên Giáp Minh Hiếu, B23DCCN299; thông tin đã xác nhận: giảng viên PGS. TS. Trần Đình Quế, lớp CT01, nhóm 04. Bìa dựng mới theo mẫu, giữ nguyên bài mẫu và các bài cũ.

| Hạng mục | Trạng thái và bằng chứng |
|---|---|
| Tiểu luận Final | Hoàn thành báo cáo 104 trang, bảy chương; `tieuluan_final_CT_04_HieuGM.299/report/` |
| Deep Graph bổ sung | GCN và MLP trên hai đồ thị, ba seed; kết quả thật ở `tieuluan_final_CT_04_HieuGM.299/results/graph-results.json` |
| Dữ liệu và MLP Project01 | Xong hai nguồn lớn, chia chống rò rỉ, hai MLP cùng baseline; `project01_CT_04_HieuGM.299/results/data-manifest.json`, `model-comparison.csv` |
| KB, MAS, Rule/RL | Xong 24 thẻ/19 nguồn, trả lời trích xuất, trace tối đa tám bước, policy trình bày Q-learning mô phỏng; `app/`, `models/`, `results/system-evaluation.json` |
| Kiểm thử | 55 trường hợp theo lượt tích hợp mới nhất, gồm năm regression bổ sung sau bộ 50 ban đầu; báo cáo tester/reviewer trong `plans/reports/` |
| Docker và Render | Hoàn thành Docker Linux: 55/55 pytest, HTTP 13/13. [Render Free tại Singapore](https://diacare-mas-hieugm299.onrender.com) đã live lúc 17:16 ngày 05/11/2026; URL công khai đạt 13/13 HTTP. Bằng chứng: `project01_CT_04_HieuGM.299/results/render-deployment.json`, `render-http-verification.json` |
| Báo cáo Project01 và bàn giao | Hoàn thành PDF25trang,15/15audit và rà trực quan toàn bộ; ZIP94tệp CRC/SHA256đạt |

Các metric hỏi đáp từ bộ phát triển tự soạn; giữ lỗi Q22 chọn nguồn chưa cụ thể nhất. Không coi dữ liệu Mỹ là kiểm định trên người Việt, không xem policy mô phỏng là học điều trị.

## Bổ sung notebook — 05/11/2026

Kế hoạch: `plans/261105-notebook-deliverables/plan.md`. Chỉ Final và Project01, mỗi bài một notebook tự đủ mã. Các project sau ưu tiên notebook là lối chạy chính theo lựa chọn của người dùng.

| Hạng mục | Trạng thái và bằng chứng |
|---|---|
| Notebook Project01 | Đã có `project01_CT_04_HieuGM.299/notebook/project01-diacare.ipynb`, 34 ô/25 ô mã; full chạy trong thư mục sạch chỉ có notebook, tối đa 25 epoch mỗi MLP, 111,47 giây, 55 assert notebook đạt. 30 câu phát triển và 11 ca an toàn được đánh giá riêng; 55 pytest ứng dụng không được tính là assert notebook |
| Notebook Final | Hoàn thành `tieuluan_final_CT_04_HieuGM.299/notebook/tieuluan-final.ipynb`, 77 ô/45 ô mã; smoke CPU chạy toàn bộ trong 87,94 giây với dữ liệu ảnh thật đã xác minh checksum. 43 lượt mô hình và 34 câu Agent; chưa chạy toàn bộ ngân sách full trong đợt chuyển notebook |
| Quy ước và kiến trúc notebook | Đã ghi mã trực tiếp trong ô, tải/nhúng dữ liệu có nguồn, chế độ smoke/full và đầu ra tách riêng trong `docs/code-standards.md`, `docs/system-architecture.md` |
| Kiểm thử, gói nộp mới và đồng bộ Git | Hoàn tất tester/reviewer: Project01 55 assert + 21 kiểm tra độc lập; Final 73 kiểm tra độc lập, 45 ô mã đạt. Hai ZIP mới xác minh CRC/SHA256; Project01 notebook đã push `7838b76`, có liên kết Colab. Các số tệp ZIP ở mốc trước là bằng chứng lịch sử |

PDF và kết quả báo cáo cũ, Docker cùng dịch vụ Render được giữ nguyên trong đợt bổ sung notebook. `smoke` kiểm tra chức năng, không thay benchmark PDF.

## 06/11/2026 - Project01 theo đặc tả Hybrid MAS

Kế hoạch: plans/261106-project01-kg-rag-benchmark/plan.md. Phạm vi chỉ Project01, không đổi Final.

| Hạng mục | Trạng thái / bằng chứng |
|---|---|
| Bốn cohort + SQLite | Hoàn thành dữ liệu thật, raw/prepared/SELECT, split/scaler; results/benchmark/database-manifest.json |
| Ma trận6 model×3 seed |72 run full hoàn thành,24dataset-model; results/benchmark/full; tổng fit+evaluate145,588 giây |
| Bảo toàn DL cũ |11 artifact CDC/Hospital SHA256 không đổi; Pima/Early chọn bằng validation |
| Neo4j/Web/PDF/Vinmec |12downloaded,340 chunk,34 concept,19 relation; Neo4j400 node/2545 edge thật và cache parity |
| Bảy agent/API/FPT | Luồng typedcontract/report và fallback; FPT thực groundedanswer có citation; pytest102 ở lượt tích hợp |
| Báo cáo và hướng dẫn bảo vệ | Đang hoàn thiện theo kết quả mới; bao-ve-project01.md có38Q&A và demo |
| Notebook, kiểm cuối, Docker/Render | Kiểm theo artifact cuối; không dùng bằng chứng phiên bản05/11 để xác nhận bản mới |

Chưa có clinical validation Việt Nam, external/temporal validation, calibration production hoặc load/SLA. RAG có lỗi được giữ; graph không thắng lexical trong bộ phát triển cũ. Neo4j production cần endpoint reachable nếu muốn live graph trên Render; fallback phải có nhãn.

### Hoàn tất bản nâng cấp Project01 - 06/11/2026

Notebook bàn giao có 61 ô/51 ô mã/25 mô-đun inline. Full kernel mới đạt 72 lượt fit, 80 kiểm tra ML và 68 API trong 211,575 giây với cache nguồn thật có hash. Lượt full tải nguồn trước đó 339,18 giây được ghi riêng. Báo cáo mới 26 trang và 38 Q&A bảo vệ đã dựng; audit PDF và rà PNG thực hiện theo bản cuối.

Ứng dụng đạt 102 pytest; kiểm độc lập 72 run/144 bộ metric/36 checkpoint/24 summary/11 hash legacy và 24 kiểm tra trình duyệt. Render nâng cấp commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0` đã live lúc 14:40:42 ngày 06/11/2026 giờ Việt Nam. FPT Environment cấu hình riêng; kết quả HTTPS từng lượt được giữ, gồm cả fallback khi LLM không qua kiểm. Dịch vụ public Git URL cần manual deploy theo commit. Neo4j public dùng cache/degraded nếu thiếu URI production; Neo4j local đã kiểm thật. Chưa có clinical validation hoặc SLA.

Public HTTPS cuối 30/30 đạt, có FPT sinh thật; lượt đầu 29/30 với một template fallback được giữ trong render-http-attempts.json. Chạy lại cùng câu hỏi/bộ kiểm đạt 30/30; không suy thành SLA hoặc provider luôn thành công.

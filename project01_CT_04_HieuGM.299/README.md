# Project01 - DiaCare Hybrid MAS

**Giáp Minh Hiếu · B23DCCN299 · CT01 · Nhóm 04**  
Giảng viên: **PGS. TS. Trần Đình Quế**.

Project kết hợp **Deep Learning từ SQLite**, **Knowledge Graph Neo4j + RAG từ Web/PDF** và **7 agent** theo kiến trúc giảng viên cung cấp. Đây là nguyên mẫu học thuật, chưa xác thực lâm sàng, không chẩn đoán hoặc kê đơn.

- [Notebook chứa mã trực tiếp trong các ô](notebook/project01-diacare.ipynb) - cách chạy chính, Run All.
- [Báo cáo PDF](report/project01_CT_04_HieuGM.299.pdf) và [Markdown](report/project01_CT_04_HieuGM.299.md).
- [Hướng dẫn bảo vệ, số lượng dữ liệu/model và demo](bao-ve-project01.md).
- [Mô hình và số liệu](README-models.md), [nguồn/giấy phép](data/README.md), [Docker + Render + FPT/Neo4j](DEPLOY.md).
- [Demo Render](https://diacare-mas-hieugm299.onrender.com) · [API docs](https://diacare-mas-hieugm299.onrender.com/docs) · [Health](https://diacare-mas-hieugm299.onrender.com/health).

## Bốn bộ dữ liệu, sáu loại mô hình, 72 lượt

| Cohort | Dòng nguồn → sạch | Feature | Nhiệm vụ |
|---|---:|---:|---|
| CDC BRFSS | 253.680 → 226.342 | 21 | Nhãn khảo sát gộp tiền đái tháo đường/đái tháo đường |
| Hospital | 101.766 → 101.763 | 10 | Tái nhập viện dưới 30 ngày |
| Pima | 768 → 768 | 8 | Tested positive/negative, cohort phụ nữ Pima |
| Early Stage | 520 → 251 | 16 | Positive/Negative, Sylhet Bangladesh; dedup trước split |

**6 loại**: Logistic Regression, Random Forest, Histogram Gradient Boosting, MLP 64-32, MLP 64-32-16, Residual MLP. Có **24 tổ hợp dataset-model × 3 seed 42/43/44 = 72 run thật**. Seed không là loại model mới. Split cố định; train-only median/scaler; validation chọn checkpoint/ngưỡng. So sánh trong từng cohort, không xếp hạng AUC khác nhiệm vụ.

72 run và hình: `results/benchmark/full/`; nguồn/SQL/split: `results/benchmark/database-manifest.json`. Tổng thời gian fit+evaluate của các run 145,588 giây;23,449 giây là invocation resume riêng, không là toàn bộ 72 run. 11 artifact cũ CDC/Hospital được bảo toàn; serving hai cohort này tái sử dụng trọng số cũ. Pima/Early chọn DL phục vụ bằng validation AUC.

## Tri thức và bảy agent

Corpus **12 tài liệu tải thật**:7 WebWHO/NIDDK,4 Web Vinmec,1 PDF Việt 77 trang. Có 14 reference-onlyURLrecords và 24 thẻ; **340 chunk đã gồm thẻ**,34 concept,2160 MENTIONS,19 quan hệ chuyên môn có evidence. Vinmec là **nguồn văn bản RAG**, không phải dữ liệu bệnh nhân có nhãn dùng train.

Neo4j local được import/query thật:400 node,2545 edge, có kiểm idempotence/cache parity. `DB_diabet.cypher` được xây mới vì người học chưa có KG. PDF 2020 là nguồn lịch sử, không tuyên bố hướng dẫn mới nhất. Xem `results/knowledge-ingestion.json`, `neo4j-verification.json`, `knowledge-verification.json`.

Luồng `/api/report`: **Coordinator → Data → DL → Rule → KG/RAG → tổng hợp → Explanation → Monitoring**. Có request_id, status, payload, evidence, model_version và latency. Sai dữ liệu dừng trước DL. Report tách prediction/rules/evidence/explanation/uncertainty/conflicts/limitations. Audit mặc định không ghi file, không lưu feature/câu hỏi/key.

FPT Cloud sinh câu trả lời có citation khi cấu hình hợp lệ; thiếu/lỗi API dùng template có nhãn. Neo4j không khả dụng dùng `sqlite_cache/degraded`. Không xem fallback là kết nối ngoài thành công. RL là contextual bandit mô phỏng cách trình bày, tách bảy agent core.

Retrieval: word/characterTF-IDF, LSA32 và graph boost; **LSA không phải neural embedding**. Mọi variant có prior cố định cho thẻ. Trên 22 câu phát triển có gold, lexicalR@1=0,9545, hybrid=0,9091; R@3 cả hai=1. Graph không thắng baseline trong phép đo này. Tám câu kiểm nguồn Vinmec mới có hạn chế gold tài liệu cụ thể; không là clinical benchmark.

## Chạy notebook

Mở notebook bằng Jupyter/VSCode/Colab, dùng Python 3.12 và Internet lần đầu, rồi Run All. Mã pipeline, agent và giao diện có trực tiếp trong ô, không cần source module `.py` của bài. Model/corpus nhúng là dữ liệu để tái sử dụng; benchmark vẫn fit trên dữ liệu thật qua SQL.

Bản bàn giao có **61 ô/51 ô mã**, 25 ô mô-đun inline; full đã chạy **72 lượt fit + 80 kiểm tra ML + 68 kiểm tra API** trong kernel mới dùng cache nguồn thật có hash, 211,575 giây. Lượt full tải nguồn trước đó hoàn thành trong 339,18 giây; xem `results/notebook-verification.json`.

`RUN_MODE="full"` chạy ngân sách đầy đủ; `"smoke"` kiểm luồng với ngân sách nhỏ. Kết quả ở `diacare-notebook-output/`, không ghi đè artifact triển khai. Chỉ bật gọi FPT thật khi đã cấu hình môi trường; không nhập key vào ô được chia sẻ hoặc commit output có key. Kết quả smoke không thay số liệu full trong báo cáo.

## Chạy ứng dụng bằng Docker

Tại thư mục Project01:

```powershell
docker build -t diacare-hieugm299:2.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 --env-file .env diacare-hieugm299:2.0
```

Bỏ `--env-file .env` nếu chỉ xem template/cache offline. Mở http://localhost:8000. Image có serving weights/corpus, không tải dữ liệu train lúc startup. Một worker, không cần GPU. `.env` thật không trong Git/image/ZIP.

## Tái lập và kiểm thử khi bảo trì

```powershell
python scripts/prepare-database.py
python scripts/run-benchmark.py --mode full --seeds 42 43 44 --reuse-prepared-db
python -m compileall -q app scripts tests report
python -m pytest tests -q
```

Bản nâng cấp đã đạt **102 pytest** ở lượt tích hợp 06/11/2026; kiểm cuối sau đóng gói/deploy được ghi riêng. 55 pytest và 13 HTTP ngày 05/11 là bằng chứng phiên bản đầu. FPT thực đã gọi thành công có citation/usage trong `results/fpt-api-verification.json`; không chứa khóa. Notebook, Docker và Render phải được kiểm theo artifact cuối, không suy từ pytest.

## Triển khai và giới hạn

Bản nâng cấp **đã live lúc 14:40:42 ngày 06/11/2026**, commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0` trên dịch vụ hiện có Docker Free Singapore. FPT đã cấu hình bằng Render Environment. Kiểm public cuối **30/30** đạt, có FPT sinh thật. Lượt trước 29/30 vì một template fallback được giữ tại `results/render-http-attempts.json`; cùng bộ kiểm/câu hỏi chạy lại đạt 30/30. Không bảo đảm LLM luôn thành công. Metadata và kiểm public nằm tại `results/render-deployment.json`, `render-http-verification.json`. Dịch vụ dùng public Git URL nên cập nhật bằng manual deploy theo commit. Neo4j local không truy cập từ Render bằng localhost; bản public dùng cache có nhãn cho đến khi có instance production accessible.

Các cohort Mỹ/Bangladesh không chứng minh phù hợp bệnh nhân Việt. Hai cohort nhỏ test 116/38 dòng; SD 3 seed không bao gồm sampling/domain uncertainty. Sigmoid chưa calibration lâm sàng; IDcitation hợp lệ không chứng minh mọi claim. Chưa có SLA, load benchmark hay kiểm định y tế. Đọc task/label/version/limitations trước giải thích score.

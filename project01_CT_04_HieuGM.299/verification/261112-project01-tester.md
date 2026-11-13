# Project01 — kiểm chứng artifact nộp lại, 12/11/2026

Kết quả: **PASS** trong phạm vi kiểm artifact đã lưu. Không huấn luyện lại, không gọi mạng/LLM, không đọc `.env`, không thay code/notebook/model. JSON chi tiết: `project01_CT_04_HieuGM.299/results/resubmission-artifact-verification.json`.

## Môi trường và phương pháp

Python3.12.9, NumPy2.3.4, scikit-learn1.7.2 trên Windows. Đọc score và nhãn thật từ NPZ với `allow_pickle=False`; tính độc lập ROC-AUC, AP, precision, sensitivity, specificity, F1, accuracy, Brier, prevalence và confusion matrix. Không import hàm metric của project. Tolerance1e-7 cho metric,1e-10 cho mean/sampleSD.

Đã xem `tests/audit-benchmark.py`; không chạy nguyên script vì nó còn yêu cầu Torch inference, SQL raw local và ZIP backup đường dẫn Linux `/work/...` không phù hợp phạm vi hiện tại. Phép kiểm được thực hiện trực tiếp trên artifact score/hash/metadata.

## Các kiểm tra đạt

- 72 tổ hợp dataset/model/seed duy nhất:4 cohort ×6 loại ×3 seed42/43/44.
- 72 JSON riêng khớp aggregate `benchmark-results.json` và72 NPZ khớp SHA256.
- 144 bộ metric validation/test tính lại khớp; mọi score hữu hạn, trong[0,1], nhãn thuộc{0,1}.
- 72 ngưỡng chọn lại bằng maximum validationF1 khớp ngưỡng test; không dùng test chọn lại.
- 36 neural weight hash và36 history best_epoch khớp quy tắc validationAUC/delta1e-5.
- 24 nhóm mean/sampleSD, mỗi nhóm3seed, đủ9 đại lượng, khớp `summary.csv`.
- Tổng fit+evaluate từ72run=145.588240721giây.
- Pima chọnMLP2seed42, Early chọnResMLPseed42 theo validationAUC cao nhất trong9neuralrun/cohort; serving weights/threshold/best_epoch khớp run đã chọn.
- 11 tệp legacy khớp hash preservation; CDC/Hospital serving metadata threshold và test score khớp `*-training.json/test/mlp`.

## Confusion matrix phục vụ bảng mới

Hàng=true0/1, cột=predicted0/1. Đây là bốn artifact serving cụ thể, không phải mean ba seed.

| Cohort | TN | FP | FN | TP | Precision | Sensitivity | Specificity | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cdc | 23758 | 5164 | 1827 | 3203 | 0.382813 | 0.636779 | 0.821451 | 0.478167 |
| hospital | 10340 | 3110 | 990 | 685 | 0.180501 | 0.408955 | 0.768773 | 0.250457 |
| pima | 58 | 17 | 11 | 30 | 0.638298 | 0.731707 | 0.773333 | 0.681818 |
| early | 8 | 4 | 1 | 25 | 0.862069 | 0.961538 | 0.666667 | 0.909091 |

Pima:75nhãn âm,41nhãn dương,116dòng. Precision=30/47=.6382978723; sensitivity=30/41=.7317073171; specificity=58/75=.7733333333; F1=60/88=.6818181818; accuracy=88/116=.7586206897; always-negative accuracy=75/116=.6465517241. Các con số báo cáo làm tròn4chữ số đều đúng.

Đã đọc công thức mới chương4: affine/ReLU, sigmoid, nhãn score>=threshold, BCE, precision/sensitivity/specificity/F1 đúng. Đã báo root sửa đường dẫn `app/ml/networks.py` thành `app/ml/network.py`, và checkpoint thực ở `app/ml/training.py`.

## Notebook

JSON hợp lệ;61ô,51ô mã,25ô module inline. AST parse51ô sau bỏ header cell magic hợp lệ; execution_count liên tiếp1–51; không có output lỗi;4PNGoutput. SHA256`dcace0e4b14563c53da92f1368616a538c5f2f4875c2a650c22cbeb53d9cca64` khớp final-delivery06/11. Không sửa hoặc chạy lại notebook trong lượt kiểm này.

## Giới hạn

Không forward model bằng Torch; không refit cây; không kiểm lại rawSQL/split/group; không đối chiếu lại ZIP trước nâng cấp vì backup gốc không có tại đường dẫn của script; chỉ đối chiếu11hash đã ghi. Notebook fresh-kernel vẫn là bằng chứng ngày06/11. Không chạy pytest vì root đang chuẩn bị môi trường và nguồn báo cáo. Phép kiểm score/hash không xác nhận lâm sàng hay grounding mọi claim.

Câu hỏi chưa giải quyết: Không có.


## Kiểm pytest và compile sau khi môi trường sẵn sàng

Ngày12/11/2026, chạy đủ `python -m pytest tests -q` bằng `tmp/project01-qa-env/Scripts/python.exe` từ thư mục Project01: **102passed,0failed,1warning,15.98s**, exit0. Môi trườngPython3.11.15/Torch2.11.0+cpu/FastAPI0.162.5/Neo4j6.4.1/pytest9.0.3/NumPy2.4.4. Warning duy nhất là deprecationStarletteTestClient/httpx, không làm fail kiểm thử.

`tests/conftest.py` xóa FPT_API_KEY và NEO4J_URI trước khi tạoCoordinator; kiểm này không gọi provider trả phí hoặc xác nhậnNeo4jproduction. API/model/corpus/template/cache và các nhánh lỗi được suite hiện có kiểm bằng artifact thực. Không train/notebookrerun.

Compile đạt cho `scripts/capture-report-cases.py`, `report/prepare-analysis.py`, `report/prepare-report.py`, `report/build-pdf.py`. Không chạy lại capturecases do root đã có8/8. Bằng chứng JSON riêng: `results/resubmission-pytest.json`.

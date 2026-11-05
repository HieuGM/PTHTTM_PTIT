# Project01 — dữ liệu/mô hình

Ngày 05/11/2026. Phạm vi: `project01_CT_04_HieuGM.299/app/ml`, scripts dữ liệu/mô hình, `models/{cdc,hospital}`, dữ liệu/kết quả liên quan. Không sửa UI/MAS/báo cáo do root phụ trách.

## Đã hoàn thành

- Hai MLP PyTorch 64→32→16→1, Dropout, BCE/Adam; mỗi bộ train25epoch, một seed42; logistic regression và always-negative baseline cùng test.
- CDC253.680 hàng,24.206 bản sao toàn hàng;5.218 hàng thuộc nhóm cùng features khác nhãn bị loại, rồi dedupe vector còn lại →226.342 hàng. Split phân tầng158.439/33.951/33.952. Số bản sao và số hàng mâu thuẫn chồng nhau, không cộng để suy ra clean.
- Hospital101.766 lượt/71.518 bệnh nhân →101.763 lượt sau bỏ3gender invalid. GroupShuffle theo patient_nbr:71.583/15.055/15.125 lượt,50.060/10.727/10.728 bệnh nhân. Không trùng người giữa split.
- Scaler chỉ fit train. Checkpoint max validation AUC; threshold max validationF1. Test không dùng chọn epoch/ngưỡng.
- CDC local bằng toàn bộ giá trị của UCI891 CSV sau bỏID và castdtype; cả hai hash được lưu. Hospital tải trực tiếp UCI296 data.csv; linkZIP đề xuất404.
- Metadata đủ feature_specs/name/label/min/max/default/integer/coding, preprocessing, threshold, label semantics, task và giới hạn. Predictor strict missing/extra/type/bool/nonfinite/range/integer.
- Modelweights state_dict, logistic coefficientNPZ; không có raw identifier trong artifacts/kết quả. Raw hospital cache dưới data/raw bị ignore, không đóng gói.
- Ba PNG đã mở kiểm tra: CDC/hospital ROC–PR–calibration–validation curves và split label distributions; bố cục sạch.

## Kết quả test

| Bộ | Mô hình | AUC | AP | F1 | Sensitivity | Specificity | Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| CDC | MLP | .827426 | .439342 | .478167 | .636779 | .821451 | .101660 |
| CDC | Logistic | .820640 | .415583 | .468472 | .655070 | .801466 | .103810 |
| Hospital | MLP | .633403 | .186922 | .250457 | .408955 | .768773 | .095820 |
| Hospital | Logistic | .628458 | .184881 | .239649 | .473433 | .691450 | .096132 |

CDCthresholdMLP .2339537889; hospital .1345039457. Nhãn/task khác nhau nên không so trực tiếp AUC hai bộ. Hospital còn990false negatives/1.675positive, không phù hợp quyết định lâm sàng. Chênh lệch MLP/logistic ở một seed chưa là bằng chứng ưu thế có ý nghĩa thống kê.

## Kiểm tra đã chạy

- Compileall app/ml và scripts: đạt.
- `scripts/prepare-data.py`: assert finite, hai lớp, group overlap0; nguồn/splitSHA.
- `scripts/test-models.py`: đạt hai bộ; scaler đúng train;30test rows/bộ suy luận API bằng score đã lưu;10invalid input cases/bộ bị từ chối; metadata copy không biến đổi cache; confusion totals khớp n; không export ID.
- `results/model-tests.json` giữ kết quả; parent cần giao tester/reviewer độc lập theo workflow repo.

## Điểm bàn giao

- API: `from app.ml.predict import Predictor,predict,get_metadata`; dataset IDs `cdc`,`hospital`. Dùng metadata để dựng form, không tự thay order field.
- Kết quả trả `risk_score`,`predicted_class`,`threshold`,`task`,`label_semantics`,`clinical_use=False`,`limitations`. Sigmoid chưa được xác thực thành xác suất cá nhân tại Việt Nam.
- `README-models.md`, `data/README.md`: tái lập, nguồn, giấy phépCC0/CCBY4, phạm vi/giới hạn.
- `results/model-comparison.csv`, `*-training.json`, `*-test-predictions.npz`, `example-predictions.json` (3mẫu test thật/bộ khôngID), `model-artifact-manifest.json`, `data-manifest.json`, `environment.json`.
- `data/raw/` và `data/splits/` là cache tái tạo, không đưa vào gói deploy/ZIP. Deployment chỉ cần modelweights, metadata và Python modules.

Không còn câu hỏi thuộc phạm vi ML. Root xử lý frontend/MAS, báo cáo, deployment và kiểm thử toàn hệ thống.

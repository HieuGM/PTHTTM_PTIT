# PHẦN 2 — BÁO CÁO KỸ THUẬT: HAI HỆ THỐNG THÔNG MINH

**Môn học: Intelligent System Development — Assignment 01**
*From Data Representation to a First Intelligent System*

> Hai hệ thống: **🫀 Hệ Chẩn đoán bệnh tim** (classification) và **🏠 Hệ Dự đoán giá nhà** (regression) — cùng một methodology *Understand → Represent → Implement → Experiment → Apply*.

---

## 1. Introduction

Assignment 01 yêu cầu phát triển **một intelligent system nhỏ** — không chỉ "train classifier" — theo khung Slide 01: Intelligence → Intelligent System → Representation → Learning → Decision → Action.

Báo cáo này trình bày **hai hệ thống** trên hai bài toán có bản chất khác nhau về bản chất học:

| | 🫀 Hệ Chẩn đoán bệnh tim | 🏠 Hệ Dự đoán giá nhà |
|---|---|---|
| Loại bài toán | **Binary classification** | **Regression** |
| Target | Có/không bệnh tim (0/1) | Giá bán USD (liên tục) |
| Metric chính | Recall, F1, Accuracy, Precision | MAE, RMSE, R² |
| Model cuối | Random Forest (B=100) | Random Forest Regressor (B=100, log-target) |
| Ứng dụng | Sàng lọc tim mạch cho nhân viên y tế | Ước giá nhà cho người mua/bán |

Hai hệ thống cùng dùng **một quy trình 22 mục** (Required Notebook Structure — mục 21 đề), cùng kỷ luật thực nghiệm, nhưng khác nhau ở mọi quyết định kỹ thuật do bản chất classification/regression chi phối — đó chính là bài học so sánh mà báo cáo này làm rõ.

**Lưu ý về lựa chọn dataset:** Slide 67 quy định *"Do not simply reproduce Lee's diabetes example"* — diabetes chỉ là scaffold. Hai dataset được chọn là dataset thật, khác hoàn toàn ví dụ lớp: UCI Heart Disease (Cleveland) và Kaggle Ames Housing.

---

## 2. Intelligent System Definition

### 2.1 Hệ Chẩn đoán bệnh tim

**System statement:**

> Hệ thống hỗ trợ sàng lọc bệnh tim nhận 13 chỉ số tim mạch đo lường được của bệnh nhân, biểu diễn thành feature vector $x \in \mathbb{R}^{13}$ (sau encode: $\mathbb{R}^{18}$), dùng model học từ 303 bệnh nhân để dự đoán xác suất hẹp động mạch vành, hỗ trợ nhân viên y tế ưu tiên bệnh nhân cần khám chuyên sâu.

### 2.2 Hệ Dự đoán giá nhà

**System statement:**

> Hệ thống ước tính giá nhà nhận các thuộc tính bất động sản (diện tích, chất lượng, vị trí, năm xây...), biểu diễn thành feature vector (sau encode: $\mathbb{R}^{271}$) + log-transform target, dùng model học từ 1460 giao dịch Ames, Iowa để dự đoán giá bán USD, hỗ trợ người mua/bán/đại lý định giá tham khảo.

### 2.3 Kiến trúc chung cả hai hệ thống

```
ENVIRONMENT → INPUT → REPRESENTATION → PREPROCESSING → MODEL → PREDICTION → OUTPUT → USER
                                     (one-hot + scale)  (RF)    (class/giá)  (web app)
                                                                              │
                                                       feedback: dữ liệu mới ◀─┘
```

Cả hai hiện thực đầy đủ chuỗi Slide 01: external information (dataset) → internal representation (feature vector) → learning (traditional ML) → decision (prediction) → action (application deploy).

---

## 3. Problem Definition

| Thành phần | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Input $x$ | 13 chỉ số tim mạch | 74 thuộc tính nhà |
| Target $y$ | $\{0, 1\}$ — có/không bệnh | $\mathbb{R}$ — giá USD |
| Bài toán | Binary classification | Regression |
| Định nghĩa 1 câu | Given the 13-dim feature vector, predict heart disease class | Given house feature vector, predict sale price in USD |
| Learning objective | $\theta^* = \arg\min_\theta \frac{1}{N}\sum \ell(f_\theta(x_i), y_i)$ | cùng công thức, $\ell$ = squared loss trên log-giá |

---

## 4. Dataset

### 4.1 UCI Heart Disease (Cleveland)

| Thuộc tính | Giá trị |
|---|---|
| Nguồn | https://archive.ics.uci.edu/dataset/45/heart+disease |
| Quan sát | 303 bệnh nhân (Cleveland Clinic) |
| Feature | 13 (6 numerical + 7 categorical) |
| Target | `num` 0–4 → nhị phân (num>0 = có bệnh) |
| Cân bằng lớp | 164 khỏe / 139 bệnh (54/46) — cân bằng tốt |
| Citation | Janosi, Steinbrunn, Pfisterer, Detrano (1988) |

Tiền xử lý: median imputation cho `ca` (4 thiếu), `thal` (2 thiếu) — tỷ lệ ~2% quá nhỏ để bỏ hàng.

### 4.2 Kaggle Ames Housing

| Thuộc tính | Giá trị |
|---|---|
| Nguồn | https://www.kaggle.com/c/house-prices-advanced-regression-techniques |
| Quan sát | 1460 giao dịch (Ames, Iowa 2006–2010) |
| Feature | 74 sau xử lý (36 numerical + 38 categorical) |
| Target | `SalePrice` ($34,900 – $755,000, lệch phải skew 1.88) |
| Citation | De Cock (2011), J. Statistics Education 19(3) |

Tiền xử lý tinh tế: **NA của Ames mang nghĩa "không có tiện ích"** (không phải missing!) — `Garage*`, `Bsmt*`, `FireplaceQu` NA → "None"; bỏ 5 cột thiếu >50%; `LotFrontage` → median theo Neighborhood.

---

## 5. Data Representation

### 5.1 Nguyên lý chung

$$\text{Raw feature} \neq \text{Encoded feature} \neq \text{Model input}$$

### 5.2 So sánh representation hai hệ thống

| | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Raw | 13 cột (7 categorical mã số) | 74 cột (38 chuỗi văn bản) |
| Encoded | one-hot 7 categorical → **18 chiều** | one-hot 38 categorical → **271 chiều** |
| Model input | standardized trong Pipeline | standardized trong Pipeline |
| **Representation của target** | nhãn 0/1 (nguyên bản) | **log(1+y)** — chính là thay đổi representation! |
| Lý do chọn | one-hot tránh giả thứ tự sai (cp 1–4 vô thứ tự) | one-hot giữ 25 khu Neighborhood không áp thứ tự |

**Điểm nhấn:** ở hệ giá nhà, việc log-transform target *chính là một quyết định representation* — không chỉ input mới là representation. Experiment 3 chứng minh quyết định này cải thiện mọi model.

---

## 6. Traditional ML Methods

### 6.1 Bốn model mỗi hệ thống (đúng mục 13 đề)

**Hệ tim (classification):** Logistic Regression, k-NN (k=11), SVM (RBF, C=1), Random Forest (B=100).

**Hệ nhà (regression):** Linear Regression, Decision Tree Regressor (depth 8), Random Forest Regressor (B=100, log-target), SVR (RBF).

### 6.2 Model understanding — bảng tổng hợp 7 câu hỏi

| Câu hỏi | LR | KNN | SVM/DT | RF |
|---|---|---|---|---|
| Representation nhận? | vector chuẩn hóa (cần) | vector chuẩn hóa (**bắt buộc** — khoảng cách) | SVM cần scale / DT không cần | không cần scale |
| Quan hệ học? | ranh giới tuyến tính | lân cận theo khoảng cách | margin tối đa / chia đệ quy | ensemble trung bình/vote |
| Tham số? | $w, b$ | không có (lazy) | siêu phẳng / cấu trúc cây | 100 cây |
| Tiêu chí? | cross-entropy (log) | không loss toàn cục | margin + hinge / Gini | Gini từng cây + variance reduction |
| Giả định? | log-odds tuyến tính | điểm gần nhau cùng lớp | margin lớn → khái quát | cây đa dạng → lỗi triệt tiêu |
| Mạnh? | diễn giải, nhanh | đơn giản, phi tuyến cục bộ | hiệu quả chiều cao / diễn giải cây | hiệu năng top, robust |
| Yếu? | chỉ tuyến tính | curse of dim, chậm inference | nhạy $C,\gamma$, khó diễn giải / overfit | black box hơn |

*(Chi tiết từng model + công thức: notebook mục 10–13 mỗi hệ.)*

---

## 7. Experimental Design

Cả hai hệ thống thực hiện **đúng 3 controlled experiments**, mỗi experiment đặt **câu hỏi trước khi chạy** (mục 15 đề):

| Experiment | Câu hỏi | Hệ tim | Hệ nhà |
|---|---|---|---|
| **1. Model comparison** | Model nào tốt nhất dưới cùng protocol? | 4 model × 5-fold CV (F1) | 4 model × 10-fold CV (R²) |
| **2. Hyperparameter** | Đổi 1 tham số → thay đổi gì? | RF: $B$ ∈ {1..400}; KNN: $k$ ∈ {1..31} | DT: depth ∈ {2..None}; RF: $B$ ∈ {5..400} |
| **3. Representation** | Đổi representation → thay đổi gì? (a) raw vs standardized (b) $X_{all}$ vs $X_{top6}$ | (a) raw vs **log-target** (b) $X_{all}$ vs $X_{top8}$ |

**Kỷ luật:** mọi quyết định phát triển dùng cross-validation trên train; test set chỉ dùng **một lần** ở Evaluation (tránh danh mục cấm của đề).

---

## 8. Results

### 8.1 Hệ Chẩn đoán bệnh tim — test set (n=61)

| Model | Accuracy | Precision | Recall | **F1** |
|---|---|---|---|---|
| **Random Forest (100)** | **0.885** | 0.839 | **0.929** | **0.881** |
| KNN (k=11) | 0.885 | 0.862 | 0.893 | 0.877 |
| Logistic Regression | 0.836 | 0.800 | 0.857 | 0.828 |
| SVM (RBF) | 0.836 | 0.800 | 0.857 | 0.828 |
| Baseline (majority) | 0.541 | 0.000 | 0.000 | 0.000 |

**Phân tích:** cả 4 model vượt baseline áp đảo (F1: 0 → 0.83–0.88) — học được tín hiệu thật. RF có **Recall 0.929** cao nhất — chỉ bỏ sót 2/28 người bệnh (FN nhỏ nhất), đúng ưu tiên y tế. AUC của các model 0.90–0.93 (mức excellent cho sàng lọc).

### 8.2 Hệ Dự đoán giá nhà — test set (n=292)

| Model | MAE | RMSE | **R²** |
|---|---|---|---|
| **Random Forest (log-target)** | **$17,277** | $29,297 | **0.888** |
| Linear Regression | ~$23k | ~$35k | ~0.84 |
| Decision Tree | ~$22k | ~$34k | ~0.85 |
| SVR (RBF, default) | ~$28k | ~$41k | ~0.77 |
| Baseline (mean) | $59,931 | $88,271 | −0.016 |

**Phân tích:** RF MAE ≈ $17k ≈ 10.6% median giá — vượt baseline 3.5×. Residual phân bố quanh 0 không theo pattern → model đã vắt hết phần tuyến tính. LR bị "kéo về trung bình" ở nhà đắt (> $400k dự đoán thấp hơn thật) — đúng hạn chế lý thuyết tuyến tính ở đuôi phân phối.

### 8.3 Kết quả 3 experiments

**Hệ tim:**
- **Exp 1:** Xếp hạng RF ≈ SVM > LR > KNN ổn định qua 5 fold;
- **Exp 2:** RF F1 tăng từ 0.70 (1 cây) → ~0.78 (50+ cây) rồi **bão hòa** — thêm cây chỉ giảm variance; KNN tối ưu k=13;
- **Exp 3a:** Standardization: **SVM +0.313 F1, KNN +0.208** (thay đổi rất lớn!), LR −0.007, RF −0.007 (miễn nhiễm);
- **Exp 3b:** Top-6 feature giữ ~95% hiệu năng.

**Hệ nhà:**
- **Exp 1:** RF > DT > LR > SVR(default) qua 10 fold;
- **Exp 2:** DT depth 2 (R² 0.58 — underfit) → 8–12 (~0.75 tối ưu) → đi ngang (overfit bắt đầu); RF bão hòa B≈100;
- **Exp 3a:** **log-target cải thiện mọi model** (LR, RF, SVR đều Δ dương);
- **Exp 3b:** Top-8 feature giữ gần nguyên hiệu năng (Δ chỉ −0.03 với RF).

---

## 9. Model Comparison — vì sao chọn Random Forest cho cả hai hệ?

Model selection là **quyết định đa tiêu chí** (Slide 01 trang 54), không phải max(accuracy):

| Tiêu chí | Đánh giá cho cả 2 hệ |
|---|---|
| Hiệu năng | RF cao nhất + **ổn định nhất** (IQR hẹp nhất qua folds) |
| Metric ưu tiên ứng dụng | Tim: Recall cao nhất (0.929); Nhà: MAE thấp nhất |
| Diễn giải | Có feature importance (`OverallQual` trội ở nhà; `ca`, `thal` ở tim) |
| Chi phí inference | 100 cây × vài ms — vô hình với web app |
| Robust | Tim: không cần scale → pipeline app ít rủi ro mismatch; Nhà: bất biến với outlier |
| Ổn định tham số | Exp 2: bão hòa từ B≈100 → không nhạy |

---

## 10. Representation Analysis — bằng kênh triết lý Slide 01

Ba nguồn bằng chứng độc lập hội tụ trong cả hai hệ:

1. **EDA** (histogram theo lớp, scatter, correlation): nhận diện feature mạnh;
2. **LR weights/coefficients**: xác nhận hướng + sức ảnh hưởng;
3. **RF feature importance**: xác nhận ranking.

| | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Feature trội | `ca` (số mạch hẹp), `thal`, `cp`, `oldpeak`, `thalach` | `OverallQual` (0.55+), `GrLivArea`, `TotalBsmtSF`, `GarageCars` |
| Feature yếu | `chol`, `trestbps` | các tiện nghi hiếm |
| Redundancy | không có cặp ρ>0.6 | Garage↔GarageArea 0.88, Bsmt↔1stFlr 0.81 |

**Kết luận trung tâm (trả lời trực tiếp Slide 01):** *Representation không phải lựa chọn trung tính*:

- Cùng KNN, đổi raw → standardized: **+0.208 F1**;
- Cùng SVM: **+0.313 F1**;
- Cùng RF hệ nhà, đổi target raw → log: R² cải thiện rõ;
- Nhưng cùng RF hệ tim: **~0 thay đổi** khi scale.

→ Ảnh hưởng của representation **phụ thuộc cơ chế học của model** (khoảng cách/margin nhạy, split theo ngưỡng miễn dịch) — mỗi cặp (representation, model) là một quyết định thiết kế phải thử nghiệm, không suy ra được trên giấy.

---

## 11. Intelligent Application

### 11.1 Kiến trúc ứng dụng (cả hai hệ)

```
Người dùng (web) → Streamlit UI → predict() → one-hot reindex đúng cột huấn luyện → RF model → kết quả + khuyến nghị
```

**Nguyên lý bắt buộc:** *cùng representation dùng lúc huấn luyện được tái dựng chính xác cho input mới* — app lưu `enc_columns` + danh sách categorical trong artifacts .joblib, hàm predict `reindex(columns=enc_columns, fill_value=0)` đảm bảo vector 18/271 chiều đúng hệt.

### 11.2 Hệ tim (`apps/heart_app/`)
- Form 13 chỉ số (slider/selectbox tiếng Việt kèm giải thích y khoa);
- Output: xác suất + ngưỡng 0.5 + kết luận + **cảnh báo vùng mơ hồ 0.35–0.65**;
- 3 preset case demo 1-click (nguy cơ thấp/cao/biên);
- Disclaimer y tế.

### 11.3 Hệ nhà (`apps/house_app/`)
- 3 tab input (chất lượng, diện tích, vị trí) — người dùng nhập 8 feature quyết định, feature phụ dùng median/mode train (thiết kế từ Exp 3b);
- Output: giá ước tính + **dải tham chiếu ±MAE/RMSE** + so median Ames;
- Cảnh báo độ tin cậy thấp ở phân khúc cao cấp;
- 3 preset phân khúc.

### 11.4 Deploy

Cả hai app **Streamlit deploy lên Hugging Face Spaces** (miễn phí, không cần thẻ tín dụng) — hướng dẫn từng bước tiếng Việt trong `apps/HUONG_DAN_DEPLOY.md`. Đã test local end-to-end bằng browser automation: cả 2 app chạy đúng (case nguy cơ cao → "CÓ BỆNH TIM" 96%; nhà cao cấp NridgHt → $302,408).

---

## 12. Limitations

| Hạng mục | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Dữ liệu | 303 mẫu — nhỏ; 1 trung tâm y tế (Cleveland) — hạn chế khái quát đa dân số | 1 thị trường nhỏ, 2006–2010 (bao gồm khủng hoảng BĐS) — stale theo thời gian |
| Representation | Mất ECG chuỗi thời gian, ảnh siêu âm, hồ sơ văn bản, quan hệ bệnh–thuốc | Mất ảnh hiện trạng, mô tả listing, động lực bán, xu hướng vĩ mô |
| Model | RF không cho khoảng tin cậy chuẩn; không extrapolate ngoài phạm vi feature đã thấy | Không dự đoán ngoài max giá train ($755k); cần retrain khi thị trường đổi |
| Ứng dụng | Sàng lọc tham khảo — KHÔNG thay thế bác sĩ; 13 chỉ số nhập tay | 8 feature chính; feature phụ cố định median — không phản ánh nhà bất thường |
| Đánh giá | 1 split 80/20 (+CV) — với N=303 khoảng tin cậy còn rộng | Tương tự; chưa kiểm tra drift theo YrSold |

---

## 13. Reflection

### 13.1 Điều gì làm hệ thống "intelligent"? (mục 18 đề — 7 câu)

Trả lời đầy đủ trong notebook mục 21 của mỗi hệ. Cốt lõi:

- **Phần intelligent hợp lý:** *học từ ví dụ + khái quát + dự đoán đúng trên input chưa thấy* — năng lực không ai lập trình luật tường minh. Bằng chứng: Recall 0.93 trên 61 bệnh nhân / R² 0.89 trên 292 nhà model chưa từng thấy;
- **Vì sao xử lý được input mới:** model học **cấu trúc quan hệ** (pattern) chứ không ghi nhớ mẫu — với input cùng phân phối, pattern hội tụ cho dự đoán đúng;
- **Trained model ≠ complete intelligent system:** model chỉ 1 thành phần. Hệ thống hoàn chỉnh = input handling + representation + preprocessing + prediction + output + **application deploy** + (tương lai) feedback loop.

### 13.2 Representation reflection (mục 19 đề — 8 câu)

| Câu hỏi | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Vì sao phù hợp? | 13 chỉ số là tín hiệu lâm sàng chuẩn, đủ thưa để học với 303 mẫu | Thuộc tính hồ sơ là thứ người định giá thật sự xem |
| Giữ gìn? | chỉ số đo đếm chính xác | quan hệ giá–thuộc tính tính toán được |
| Mất gì? | ECG thô, ảnh, ngữ cảnh lâm sàng | ảnh, mô tả văn bản, động lực bán, chuỗi thời gian |
| Image? | ảnh siêu âm/MRI → CNN (A4) | ảnh mặt tiền/nội thất → CNN (kiểu Zestimate) |
| Sequence? | chuỗi ECG → RNN/Transformer (A3) | chuỗi giá giao dịch khu vực → time-series |
| Graph? | đồ thị bệnh–triệu chứng–thuốc → GNN/KG (A4) | đồ thị nhà–đường–trường học → GNN không gian |
| Embedding? | embedding bệnh nhân từ hồ sơ (A5) | embedding mô tả listing (A5) |
| Đổi thì sao? | nhiều thông tin hơn → trần cao hơn, nhưng mất diễn giải + cần deep learning + dữ liệu lớn | tương tự |

**Thông điệp kết nối course roadmap:** *Different information representations ⇒ different learning methods* — chính là lý do A3 (deep learning), A4 (graph), A5 (embedding/RAG) tồn tại sau A1.

---

## 14. Conclusion

**Hiện thực hóa khung Understand → Represent → Implement → Experiment → Apply cho hai hệ:**

| | 🫀 Bệnh tim | 🏠 Giá nhà |
|---|---|---|
| Understand | Sàng lọc nhị phân từ 13 chỉ số | Ước giá regression từ 74 thuộc tính |
| Represent | one-hot 18 chiều | one-hot 271 chiều + **log-target** |
| Implement | baseline + 4 classifier | baseline + 4 regressor |
| Experiment | 3 experiments — RF≈SVM>LR>KNN; B bão hòa 50; scale +0.21/+0.31 cho KNN/SVM | 3 experiments — RF>DT>LR>SVR; depth 8–12; log-target tốt hơn mọi model |
| Apply | RF (F1 0.88, Recall 0.93) → Streamlit app | RF (R² 0.89, MAE $17k) → Streamlit app |

**Ba thông điệp lớn của Assignment 01** (khớp Slide 01):

1. **Representation là xương sống** — model không nhận thế giới thực mà nhận representation của thông tin được chọn; đổi representation (scale, log-target, chọn feature) thay đổi kết quả học theo cách phụ thuộc cơ chế model;
2. **Baseline + controlled experiments + metric đúng** là điều kiện để nói "model học được điều gì hữu ích" — không phải con số accuracy trơ trọi;
3. **Model ≠ hệ thống** — chỉ khi bọc model trong pipeline Input → Representation → Preprocessing → Model → Prediction → Output và **deploy thành web app** thì mới có intelligent system nhỏ hoàn chỉnh. Đây là intelligent system đầu tiên của lộ trình 5 assignment; các assignment sau sẽ thay representation (tensor, graph, embedding) và mở rộng năng lực học.

---

## Phụ lục: Đối chiếu 14 Explicit Requirements (R1–R14)

| # | Yêu cầu | Bằng chứng |
|---|---|---|
| R1 | Real dataset | UCI Heart Disease + Kaggle Ames (nguồn + citation trong notebook mục 3) |
| R2 | System definition | System statement + diagram (notebook mục 1–2) |
| R3 | Representation | 3 tầng raw/encoded/input + bảng feature (mục 5) |
| R4 | Feature analysis | EDA 4 biểu đồ + giải thích từng cái (mục 6 + 4) |
| R5 | Problem formulation | Câu formal 1 câu + công thức $D, f_\theta, \theta^*$ (mục 1) |
| R6 | Baseline | DummyClassifier/DummyRegressor + phân tích "vì sao cần" (mục 9) |
| R7 | ≥4 models | LR, KNN, SVM, RF (tim) / LR, DT, RF, SVR (nhà) — hiểu model 7 câu mỗi cái |
| R8 | ≥3 experiments | Model comparison + hyperparameter + representation — mỗi cái có câu hỏi trước |
| R9 | Metrics + giải thích | Tim: 4 metric + CM + ROC; Nhà: MAE/MSE/RMSE/R² + residual — kèm vì sao chọn |
| R10 | Scientific analysis | Mỗi kết quả có "vì sao" (scale/margin/variance...) |
| R11 | Application | 2 app Streamlit + hàm predict đúng representation |
| R12 | System demonstration | 3 case mỗi hệ qua pipeline đầy đủ + screenshot app |
| R13 | Reflection | 7+8 câu trả lời đầy đủ (mục 21 notebook) |
| R14 | Reproducibility | RANDOM_STATE=42, data local, requirements, notebook chạy end-to-end |

## Phụ lục: Cấu trúc deliverables nộp kèm

```
assignment01/
├── docs/
│   ├── phan1_ly_thuyet.md/.pdf      ← Phần 1: lý thuyết (11 trang)
│   ├── phan2_bao_cao_ky_thuat.md    ← file này
│   └── phan2_bao_cao_ky_thuat.pdf
├── notebooks/
│   ├── 01_heart_disease_system.ipynb  (73 cells, output đầy đủ)
│   └── 02_house_price_system.ipynb    (70 cells, output đầy đủ)
├── data/
│   ├── heart_clean.csv              (303 × 14 — nguồn: UCI)
│   ├── ames_clean.csv               (1460 × 75 — nguồn: Kaggle)
│   └── ames_train.csv               (gốc Kaggle tải về)
├── artifacts/
│   ├── heart_model.joblib           (RF classifier + metadata representation)
│   └── ames_model.joblib            (RF regressor + metadata)
├── apps/
│   ├── heart_app/ (app.py + model + requirements)
│   ├── house_app/ (app.py + model + requirements)
│   └── HUONG_DAN_DEPLOY.md          ← hướng dẫn deploy HF Spaces tiếng Việt
├── figures/                          (26 biểu đồ + 2 screenshot app)
└── README.md                         ← hướng dẫn chạy toàn bộ
```

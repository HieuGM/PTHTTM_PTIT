# ASSIGNMENT 01 — INTELLIGENT SYSTEM DEVELOPMENT

**From Data Representation to a First Intelligent System**

> 🫀 **Hệ Chẩn đoán Bệnh tim** (classification) &nbsp;|&nbsp; 🏠 **Hệ Dự đoán Giá nhà** (regression)
>
> Hai intelligent system nhỏ: từ dữ liệu thật → representation → traditional ML → experiment → **web app deploy**.

| | Hệ Chẩn đoán bệnh tim | Hệ Dự đoán giá nhà |
|---|---|---|
| Dataset | UCI Heart Disease (Cleveland) — 303 bệnh nhân | Kaggle Ames Housing — 1460 nhà |
| Bài toán | Binary classification | Regression |
| Model cuối | Random Forest (B=100) | Random Forest Regressor (log-target) |
| Kết quả test | **F1 = 0.88, Recall = 0.93** | **R² = 0.89, MAE ≈ $17k** |
| App | `apps/heart_app/` | `apps/house_app/` |

---

## 📁 Cấu trúc dự án

```
assignment01/
├── docs/
│   ├── phan1_ly_thuyet.pdf .md     ← PHẦN 1: Lý thuyết (Slide 01 ↔ Assignment)
│   ├── phan2_bao_cao_ky_thuat.pdf .md ← PHẦN 2: Báo cáo kỹ thuật 2 hệ thống
├── notebooks/
│   ├── 01_heart_disease_system.ipynb   ← 22 mục, output chạy thật, 13 biểu đồ
│   └── 02_house_price_system.ipynb     ← 22 mục, output chạy thật, 13 biểu đồ
├── data/
│   ├── heart_clean.csv             ← dữ liệu sạch (nguồn: UCI, tải 26/08)
│   ├── ames_clean.csv              ← dữ liệu sạch (nguồn: Kaggle Ames)
│   └── ames_train.csv              ← bản gốc Kaggle
├── artifacts/
│   ├── heart_model.joblib          ← model + metadata representation (dùng cho app)
│   └── ames_model.joblib
├── apps/
│   ├── heart_app/  (app.py + model.joblib + requirements.txt)
│   ├── house_app/  (app.py + model.joblib + requirements.txt)
│   └── HUONG_DAN_DEPLOY.md         ← 🚀 deploy lên Hugging Face Spaces (tiếng Việt)
├── figures/                        ← 26 biểu đồ notebook + 2 screenshot app
└── README.md                       ← file này
```

---

## ⚡ CHẠY NHANH (5 phút)

### Yêu cầu môi trường
Python 3.10+, các package: `scikit-learn pandas numpy matplotlib seaborn jupyter joblib streamlit`

```bash
pip install -r apps/heart_app/requirements.txt jupyter matplotlib seaborn
```

### 1. Mở 2 notebook (đã chạy sẵn output — mở xem được ngay)

```bash
cd assignment01/notebooks
jupyter notebook 01_heart_disease_system.ipynb    # hệ bệnh tim
jupyter notebook 02_house_price_system.ipynb      # hệ giá nhà
```

> Notebook đọc dữ liệu từ `../data/` — chạy end-to-end từ đầu (Run All) tái lập toàn bộ
> kết quả + 2 file model .joblib. `RANDOM_STATE = 42` cố định mọi nơi.

### 2. Chạy 2 web app local

```bash
# App bệnh tim
cd apps/heart_app
streamlit run app.py        # → http://localhost:8501

# App giá nhà (terminal khác)
cd apps/house_app
streamlit run app.py        # → http://localhost:8502
```

### 3. Deploy lên web công khai (nộp link cho thầy)

Xem **`apps/HUONG_DAN_DEPLOY.md`** — hướng dẫn từng bước deploy Hugging Face Spaces
(miễn phí, không cần thẻ tín dụng, ~10 phút cho cả 2 app).

---

## 📓 Nội dung 2 notebook (đúng 22 mục Required Notebook Structure)

| # | Mục | Hệ tim | Hệ nhà |
|---|---|---|---|
| 1–2 | System + Problem Definition, Diagram | sàng lọc tim mạch | ước giá nhà |
| 3–4 | Dataset Source + Description | UCI, 10 câu hỏi | Kaggle Ames, 10 câu hỏi |
| 5 | Data Representation | 13→18 chiều one-hot | 74→271 chiều + log-target |
| 6–7 | Feature Analysis + EDA | 4 biểu đồ + giải thích | 4 biểu đồ + giải thích |
| 8 | Train/Test Split | 80/20 stratify + 5-fold CV | 80/20 + 10-fold CV |
| 9 | Baseline | DummyClassifier (F1=0) | DummyRegressor (MAE $60k) |
| 10–13 | 4 Models + hiểu model | LR, KNN, SVM, RF | LR, DT, RF, SVR |
| 14 | Evaluation | 4 metric + CM + ROC | MAE/MSE/RMSE/R² + residual |
| 15 | Exp 1: Model Comparison | RF ≈ SVM > LR > KNN | RF > DT > LR > SVR |
| 16 | Exp 2: Hyperparameter | RF bão hòa B≈50–100; KNN k=13 | DT tối ưu depth 8–12 |
| 17 | Exp 3: Representation | scale: SVM +0.31, KNN +0.21 | log-target tốt hơn mọi model |
| 18 | Final Model | RF (F1 0.88, Recall 0.93) | RF (R² 0.89, MAE $17k) |
| 19–20 | Application + Demonstration | 3 case demo | 3 case demo |
| 21–22 | Reflection + Conclusion | 7+8 câu reflection | 7+8 câu reflection |

**Mọi biểu đồ đều có markdown "📊 Giải thích" ngay sau** — phân tích đọc được gì từ biểu đồ, vì sao kết quả như vậy.

---

## 🔑 Những con số chính (test set)

### Hệ bệnh tim (n=61)

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| **Random Forest** | **0.885** | 0.839 | **0.929** | **0.881** |
| KNN (k=11) | 0.885 | 0.862 | 0.893 | 0.877 |
| Logistic Regression | 0.836 | 0.800 | 0.857 | 0.828 |
| SVM (RBF) | 0.836 | 0.800 | 0.857 | 0.828 |
| Baseline | 0.541 | 0 | 0 | 0 |

### Hệ giá nhà (n=292)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| **Random Forest (log)** | **$17,277** | $29,297 | **0.888** |
| Linear Regression | ~$23k | ~$35k | ~0.84 |
| Decision Tree | ~$22k | ~$34k | ~0.85 |
| SVR (default) | ~$28k | ~$41k | ~0.77 |
| Baseline (mean) | $59,931 | $88,271 | −0.016 |

---

## 🔬 Phát hiện thú vị từ 3 controlled experiments

1. **Scaling chỉ quan trọng với model dựa khoảng cách** — SVM +0.31 F1, KNN +0.21 khi chuẩn hóa; Random Forest **không đổi** (cây split theo ngưỡng, bất biến với biến đổi đơn điệu). → Representation và cơ chế học gắn với nhau;
2. **Random Forest bão hòa nhanh** — 50–100 cây là đủ, 400 cây như 100 cây (thêm cây chỉ giảm variance, không tăng bias);
3. **log-transform target cải thiện mọi model** trong regression giá nhà — vì giá nhà lệch phải mạnh (skew 1.88), squared-error trên log = sai số tương đối công bằng cho nhà rẻ lẫn đắt;
4. **Top-6/8 feature giữ ~95% hiệu năng** — tín hiệu tập trung trong ít feature then chốt (`ca, thal, cp` cho tim; `OverallQual, GrLivArea` cho nhà).

---

## 📚 Nguồn dữ liệu (citations)

1. Janosi A., Steinbrunn W., Pfisterer M., Detrano R. (1988). *Heart Disease Data Set*. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/45/heart+disease
2. De Cock D. (2011). *Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project*. Journal of Statistics Education, 19(3).
3. Tran D. Q. (2026). *Intelligent System Development — Lecture 01 & Assignment 01*. PTIT.
4. Lee W.-M. (2019). *Python Machine Learning*, Wiley — Chương 12 (scaffold tham khảo workflow).
5. Pedregosa et al. (2011). *Scikit-learn: Machine Learning in Python*. JMLR 12.

---

## ✅ Đối chiếu 8 deliverables bắt buộc (mục 24 đề)

| Deliverable | File |
|---|---|
| 1. Jupyter Notebook | `notebooks/01_*.ipynb`, `notebooks/02_*.ipynb` |
| 2. Dataset info + source | notebook mục 3 + `data/` + README này |
| 3. Technical report | `docs/phan2_bao_cao_ky_thuat.pdf` |
| 4. System diagram | notebook mục 2 (ASCII diagram) + report |
| 5. Experimental comparison table | notebook mục 14–15 + report mục 8 |
| 6. Figures | `figures/` (26 file) |
| 7. Application source | `apps/heart_app/`, `apps/house_app/` |
| 8. README | file này |

---

*Sinh viên thực hiện: ……………………… — lớp ……… — ngày ……… (điền trước khi nộp)*

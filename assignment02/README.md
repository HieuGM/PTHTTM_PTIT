# ASSIGNMENT 02 — INTELLIGENT SYSTEM DEVELOPMENT

**From Data Representation to a Deployable Intelligent System**

> 🩸 **Dự đoán Tiểu đường** (classification) | 🏠 **Định giá Nhà** (regression) | 🛒 **Phát hiện Sở thích Khách hàng** (classification + text embeddings)
>
> Ba intelligent system: `Raw Data → Understand → Clean → Represent → Learn → Evaluate → Persist → Deploy (API + Web + Mobile)`

| | App 1 — Diabetes | App 2 — House Price | App 3 — Customer Behavior |
|---|---|---|---|
| Dataset (Kaggle) | Pima Indians Diabetes — 768 | KC House Sales — 21,613 | Online Retail — 55,263 dòng |
| Bài toán | Binary classification | Regression | Multi-class (9 lớp) + text |
| Representation | $X \in \mathbb{R}^{768 \times 8}$ (impute + scale) | $X \in \mathbb{R}^{21536 \times 87}$ (17 num + 70 one-hot zip) | RFM 5D ⊕ TF-IDF 4000D (sparse) |
| Model cuối | Random Forest (200) | Gradient Boosting (log-target) | Linear SVM (text-linear) |
| Test | Acc 0.74, AUC 0.81 | R² 0.90, MAE $68k | macro-F1 0.37, acc 0.70 |
| So sánh model | 5 model + baseline | 5 model + baseline | 6 model + baseline + repr ablation |
| API | FastAPI `/predict` | FastAPI `/predict` | FastAPI `/predict` |
| Web + Mobile | Streamlit + mobile HTML | Streamlit + mobile HTML | Streamlit + mobile HTML |

---

## 📁 Cấu trúc dự án (theo Appendix A đề bài)

```
assignment02/
├── diabetes/
│   ├── data/pima_diabetes.csv          ← dataset (Kaggle mirror tải local)
│   ├── notebook/01_diabetes_system.ipynb  ← 23 mục, output chạy thật, 9 figures
│   │   └── diabetes_nb_source.py + _build.py  (build lại notebook từ source)
│   ├── model/diabetes_pipeline.joblib  ← imputer + scaler + RF + metadata
│   ├── api/main.py                     ← FastAPI POST /predict (+ CORS)
│   ├── web/app.py                      ← Streamlit client
│   └── mobile/index.html               ← mobile client (gọi API)
├── house_price/                        ← cấu trúc tương tự (KC House)
├── customer_behavior/                  ← cấu trúc tương tự (Online Retail + TF-IDF)
├── deploy/                             ← gói deploy HF Spaces + deploy-all.py
├── figures/                            ← 25 figures notebook + 10 screenshots web/mobile
├── report/                             ← báo cáo DOCX/PDF
├── DEPLOY_HUONG_DAN.md                 ← 🚀 hướng dẫn deploy 6 HF Spaces
└── README.md                           ← file này
```

---

## ⚡ CHẠY NHANH

### Môi trường
Python 3.10+, packages: `scikit-learn pandas numpy matplotlib seaborn jupyter joblib fastapi uvicorn streamlit sentence-transformers`

### 1. Xem 3 notebook (đã chạy sẵn output)

```bash
cd assignment02
jupyter notebook diabetes/notebook/01_diabetes_system.ipynb
jupyter notebook house_price/notebook/02_house_price_system.ipynb
jupyter notebook customer_behavior/notebook/03_customer_behavior_system.ipynb
```

> Notebook đọc dữ liệu từ `../data/`, chạy end-to-end (Run All) tái lập toàn bộ kết quả
> + 3 file model `.joblib`. `RANDOM_SEED = 42` cố định mọi nơi.
> Build lại notebook từ source: `python notebook/_build.py notebook/<tên>_nb_source.py`

### 2. Chạy 3 REST API local

```bash
# Terminal 1
cd diabetes/api && uvicorn main:app --port 8001 --reload
# Terminal 2
cd house_price/api && uvicorn main:app --port 8002 --reload
# Terminal 3
cd customer_behavior/api && uvicorn main:app --port 8003 --reload
```

Swagger UI: `http://localhost:8001/docs` (tương tự 8002, 8003)

```bash
curl -X POST http://localhost:8001/predict -H "Content-Type: application/json" \
  -d '{"Pregnancies":6,"Glucose":183,"BloodPressure":88,"SkinThickness":35,"Insulin":230,"BMI":36.5,"DiabetesPedigreeFunction":0.72,"Age":45}'
# → {"prediction":"diabetic","confidence":0.87,...}
```

### 3. Chạy 3 web + 3 mobile local

```bash
cd diabetes/web && streamlit run app.py          # :8501 (tự gọi API 8001)
# mobile: mở diabetes/mobile/index.html bằng browser (tự gọi API 8001)
```

### 4. Deploy công khai (nộp link)

Xem **`DEPLOY_HUONG_DAN.md`** — script `deploy/deploy-all.py` tạo 6 HF Spaces
(3 API Docker + 3 web Streamlit), tự cài URL chéo, ~10 phút.

---

## 📓 Nội dung 3 notebook (đúng 23 mục Appendix B)

| # | Mục | 1 Diabetes | 2 House | 3 Customer |
|---|---|---|---|---|
| 1 | Problem Definition | sàng lọc tiểu đường | định giá nhà | interest discovery |
| 2–3 | Source + Loading | Kaggle PIMA | Kaggle KC | Kaggle Online Retail |
| 4–9 | Inspection → Outlier | zero-trá hình→NaN | trùng id, bedrooms=33 | hủy đơn, giá ≤0, B2B outlier |
| 10 | EDA | 4+ biểu đồ O/I/ML | 5 biểu đồ | RFM + category + text |
| 11–13 | Types + Representation + FE | 8D numeric | 87D (one-hot zip) | RFM ⊕ TF-IDF + leakage demo |
| 14–15 | Split + Pipeline | 70/15/15 stratify | 70/15/15 | 70/15/15 stratify 9 lớp |
| 16–18 | Baseline → 5-6 model → Compare | LR/DT/RF/SVM/KNN | LR/Ridge/DT/RF/GB | LR/DT/RF/SVM/LinearSVM/KNN |
| 19–20 | Test eval + Error analysis | CM+ROC+AUC | residual+phân khúc | CM 9 lớp + cặp nhầm |
| 21–23 | Selection → Persistence → Inference | RF | GB | Linear SVM |

Đặc biệt App 3 có **mục 18.5**: so sánh tabular-only vs tabular+text (yêu cầu đề) —
text nâng macro-F1 RF 0.163→0.291; **mục 18.6**: demo MiniLM embedding $B \times T \times d=384$.

## 🔑 Representation Summary (bảng bắt buộc của đề)

| Application | Raw form | Numerical representation | Model input |
|---|---|---|---|
| Diabetes | CSV / table | Feature matrix (median-impute + standardized) | $B \times 8$ float64 |
| House price | CSV / table | Encoded matrix (17 scaled + 70 one-hot zipcode, log-target) | $B \times 87$ float64 |
| E-commerce | CSV + descriptions | Tabular RFM ⊕ text TF-IDF (Comment→Tokens→IDs→Embedding) | sparse $B \times 4005$; demo $B \times T \times 384$ |

## 🔬 Reproducibility

- Python 3.12 (Anaconda, Windows 11); sklearn 1.9.0; pandas 2.x; numpy 1.26+
- `RANDOM_SEED = 42` mọi nơi; split cố định `random_state`
- Dataset tải local trong `<app>/data/` (không cần mạng khi chạy)
- Notebook build từ `<tên>_nb_source.py` qua `_build.py` — tái lập cell-by-cell
- Deploy pin `scikit-learn==1.9.0` (khớp môi trường train — tránh lệch model serialization)

## 📚 Nguồn dữ liệu (citations)

1. Smith, J.W. et al. (1988). *Pima Indians Diabetes Database*. UCI/Kaggle. https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
2. Harlfoxem. *House Sales in King County, USA*. Kaggle. https://www.kaggle.com/datasets/harlfoxem/housesalesprediction
3. Daqing Chen et al. *Online Retail*. UCI ML Repository / Kaggle. https://www.kaggle.com/datasets/carrie1/ecommerce-data
4. Tran D. Q. (2026). *Intelligent System Development — Lecture 02 & Assignment 02*. PTIT.
5. Pedregosa et al. (2011). *Scikit-learn: Machine Learning in Python*. JMLR 12.

---

## ✅ Đối chiếu deliverables đề yêu cầu

| Deliverable | File |
|---|---|
| 3 Jupyter notebooks | `<app>/notebook/0[1-3]_*.ipynb` |
| 3 trained + persisted pipelines | `<app>/model/*.joblib` (preprocess + model + metadata) |
| 3 web prediction services | `<app>/web/app.py` + deploy HF Spaces |
| 3 mobile demonstrations | `<app>/mobile/index.html` + host tại `<api>/mobile` |
| Báo cáo (~10 trang) | `report/` |
| Source code | repo này |
| Dataset references | README mục Nguồn dữ liệu |
| README | file này |

## 🔗 Link demo (điền sau khi deploy)

| Hệ thống | Web | API (Swagger) | Mobile |
|---|---|---|---|
| Diabetes | … | … | …/mobile |
| House Price | … | … | …/mobile |
| Customer | … | … | …/mobile |

---

*Sinh viên thực hiện: ……………………… — MSSV: ……… — lớp: ……… (điền trước khi nộp)*

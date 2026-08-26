# PHẦN 1 — LÝ THUYẾT: TỪ INTELLIGENCE ĐẾN INTELLIGENT SYSTEM

**Môn học: Intelligent System Development — Assignment 01**
*From Data Representation to a First Intelligent System*

> "Understand the system, represent the information, learn from data, and turn the model into an application."

---

## 1. Intelligence là gì? — Quan điểm chức năng (functional view)

Không có một định nghĩa kỹ thuật duy nhất được chấp nhận rộng rãi cho *intelligence*. Môn học này tiếp cận theo **quan điểm chức năng**: một hệ thống được coi là "có trí tuệ" khi nó *thực hiện được* các năng lực sau (Slide 01, trang 6):

| Năng lực | Câu hỏi cốt lõi | Cơ chế điển hình |
|---|---|---|
| **Perception** (tri giác) | Hệ thống nhận thông tin gì từ môi trường? | Sensor, dữ liệu, API |
| **Representation** (biểu diễn) | Thông tin được biểu diễn bên trong như thế nào? | Feature vector, tensor, graph, embedding |
| **Learning** (học) | Hệ thống học từ đâu? | Machine learning, deep learning |
| **Reasoning** (suy luận) | Hệ thống suy luận ra sao dưới bất định? | Logic, search, xác suất |
| **Decision** (quyết định) | Hệ thống chọn hành động nào? | Ngưỡng quyết định, policy, tối ưu hóa |
| **Action** (hành động) | Hệ thống tác động lên môi trường ra sao? | Dự đoán, cảnh báo, giao diện người dùng |
| **Adaptation** (thích nghi) | Hệ thống cải thiện từ phản hồi không? | Feedback, continual learning |

**Điểm mấu chốt:** Intelligence không phải là một thuật toán duy nhất. Trí tuệ *nổi lên* (emerges) từ sự **phối hợp các năng lực** (Slide 01, trang 7).

### 1.1 Khái niệm "intelligence" trong Assignment 01

Assignment 01 cố tình xử lý intelligence theo nghĩa **hẹp và có thể vận hành được** (limited and operational sense). Hệ thống thể hiện một *hình thức* trí tuệ khi nó có thể:

1. **Nhận thông tin** (receive information);
2. **Biểu diễn thông tin liên quan một cách tính toán** (represent relevant information computationally);
3. **Học một quan hệ từ các ví dụ** (learn a relationship from examples);
4. **Tạo ra dự đoán cho một trường hợp mới** (produce a prediction for a new case);
5. **Hỗ trợ một quyết định hoặc ứng dụng** (support a decision or application).

Từ đó, working notion of intelligence cho Assignment 01 là:

$$\boxed{\;\text{Learning from examples} \;+\; \text{Generalization} \;+\; \text{Prediction}\;}$$

Đây không phải định nghĩa hoàn chỉnh về trí tuệ. Các assignment sau sẽ mở rộng qua deep learning (A3), kiến thức + đồ thị (A4), embedding/RAG/tương tác/triển khai (A5).

---

## 2. Intelligent System là gì? — Abstraction kỹ thuật

Slide 01 (trang 8) đưa ra một abstraction kỹ thuật hữu ích:

$$\text{IntelSyst} = (\text{Environment}, \text{State}, \text{Representation}, \text{Knowledge}, \text{Learning}, \text{Decision}, \text{Action})$$

```
Environment ──observe──▶ Internal State ──reason──▶ Decision ──act──▶ Environment
                update ▲                                              │
                └──────────────── feedback ◀─────────────────────────┘
```

**Phân biệt quan trọng nhất:** *external state* (thế giới thực) ≠ *internal/cognitive state* (biểu diễn bên trong hệ thống).

> Hệ thống **không sở hữu trực tiếp** toàn bộ thế giới thực. Nó vận hành thông qua **quan sát (observations)** và **biểu diễn (representations)**.

### 2.1 Sự khác nhau: Model ≠ Application ≠ Intelligent System

| Khái niệm | Bản chất | Thành phần |
|---|---|---|
| **Model** | Hàm học được $f_\theta(x)$ | Learned mapping |
| **Application** | Model làm ra **usable** | model + interface + data processing |
| **Intelligent System** | Application vận hành **trong môi trường** | application + state + interaction + feedback |

Từ đó rút ra nguyên lý xuyên suốt môn học:

$$\text{ML model} \neq \text{complete intelligent system}$$

Assignment 01 hiện thực hóa nguyên lý này bằng cách **bắt buộc** biến model thành application (mục 17 trong đề): model một mình chưa phải là hệ thống hoàn chỉnh.

---

## 3. Representation — Ý tưởng trung tâm của toàn bộ môn học

### 3.1 Nguyên lý nền tảng (Foundation / Key principle)

> **Model không nhận "thế giới thực". Model nhận một biểu diễn (representation) của thông tin được lựa chọn. Do đó: Representation quyết định thông tin nào có sẵn cho học.**

Slide 01 (trang 24) nhấn mạnh: **Representation không phải lựa chọn trung tính** (Representation is not a neutral choice). Cùng một đối tượng thực có thể được biểu diễn nhiều cách:

```
Real-world Object ──▶ Feature Vector   (giữ thông tin đo đếm, mất cấu trúc)
                 ──▶ Graph             (giữ quan hệ, mất chi tiết liên tục)
                 ──▶ Embedding         (giữ ngữ nghĩa học được, mất tính diễn giải)
```

Mỗi representation **giữ lại một phần thông tin và loại bỏ/su biến đổi phần khác**:

$$\text{Representation} \Rightarrow \text{available information} \Rightarrow \text{possible learning}$$

### 3.2 Feature vector — Representation của dữ liệu có cấu trúc

Với dữ liệu có cấu trúc (structured data), một quan sát được biểu diễn bằng **feature vector**:

$$x_i = [x_{i1}, x_{i2}, \dots, x_{id}] \in \mathbb{R}^d$$

Một dataset có giám sát (supervised dataset):

$$D = \{(x_i, y_i)\}_{i=1}^{N}$$

trong đó:
- $x_i$: input representation (biểu diễn đầu vào);
- $d$: số đặc trưng (features);
- $y_i$: target (giá trị mục tiêu);
- $N$: số quan sát (observations).

Ma trận đặc trưng hoàn chỉnh:

$$X \in \mathbb{R}^{N \times d}$$

### 3.3 Ba tầng representation phải phân biệt (mục 8 đề bài)

$$\text{Raw feature} \neq \text{Encoded feature} \neq \text{Model input}$$

Ví dụ trong hệ Chẩn đoán bệnh tim:
- **Raw feature**: `cp` (loại đau ngực) nhận giá trị 1–4 — biến phân loại theo thang đo định danh;
- **Encoded feature**: sau one-hot encoding thành 4 cột nhị phân `cp_1..cp_4`;
- **Model input**: sau chuẩn hóa (standardization) các đặc trưng số — giá trị $z = \frac{x - \mu}{\sigma}$.

Sự thay đổi representation ở tầng preprocessing **thay đổi hẳn** không gian mà thuật toán học "nhìn thấy".

### 3.4 Tiến hóa của representation trong lịch sử AI (Slide 01, trang 22–23)

$$\text{Symbols} \rightarrow \text{Features} \rightarrow \text{Vectors} \rightarrow \text{Tensors} \rightarrow \text{Graphs} \rightarrow \text{Embeddings} \rightarrow \text{Multimodal}$$

| Cấu trúc thông tin | Representation tự nhiên | Model điển hình | Giai đoạn môn học |
|---|---|---|---|
| Bản ghi có cấu trúc | Feature vector $x \in \mathbb{R}^d$ | LR, KNN, SVM, Trees | **A1–A2** |
| Hình ảnh | Tensor | CNN, ViT | Deep Learning |
| Chuỗi (sequence) | Vector sequence | RNN, LSTM, Transformer | Deep Learning |
| Quan hệ | Nodes + edges | GNN | Knowledge/Graph |
| Tri thức | Entities + relations | KG reasoning | Knowledge Graph |
| Văn bản | Embeddings | Similarity search | RAG |
| Đa phương thức | Nhiều representation | Multimodal AI | Final Project |

**Lịch sử của AI cũng là lịch sử của representations** — đây là câu chủ đạo nối Assignment 01 với toàn bộ lộ trình môn học.

---

## 4. Traditional Machine Learning — Vị trí trong lịch sử AI

### 4.1 Timeline khái niệm (Slide 01, trang 10–12)

| Giai đoạn | Paradigm | Ý tưởng chính | Representation điển hình |
|---|---|---|---|
| 1950s–60s | Symbolic AI | Logic, search, problem solving | Symbols / rules |
| 1970s–80s | Expert Systems | Mã hóa tri thức chuyên gia | Rules / knowledge base |
| **1980s–2000s** | **Statistical ML** | **Học pattern từ ví dụ** | **Feature vectors** |
| 2000s–2010s | Deep Learning | Học representation phân tầng | Tensors |
| 2010s | Large-scale DL | Data + compute + learned repr. | High-dim tensors |
| Late 2010s–2020s | Transformers | Attention, sequence modeling | Embeddings / tokens |
| 2020s | Foundation/Gen AI | Reusable learned capabilities | Multimodal embeddings |
| Hiện tại | Interactive/Agentic | Perceive, reason, use tools, act | State + memory + tools |

### 4.2 Era 3: Statistical ML — sự dịch chuyển cốt lõi

$$\underbrace{\text{Program the rules}}_{\text{Symbolic AI}} \longrightarrow \underbrace{\text{Learn patterns from examples}}_{\text{Statistical ML}}$$

Thay vì con người viết luật `IF fever AND cough THEN possible_infection`, hệ thống **tự suy ra** quan hệ input → output từ dữ liệu:

$$\hat{y} = f_\theta(x)$$

Các phương pháp điển hình: **Logistic Regression, k-Nearest Neighbors, Support Vector Machines, Decision Trees, Random Forests** — đúng 5 nhóm model Assignment 01 yêu cầu.

**Hệ quả quan trọng:** khi học từ dữ liệu thay vì viết luật, **representation trở thành bài toán kỹ thuật trung tâm** (Representation becomes a central engineering problem).

### 4.3 Traditional ML vs Deep Learning — phân biệt bắt buộc phải nắm

| Tiêu chí | Traditional ML | Deep Learning |
|---|---|---|
| Representation | **Human-designed features** | **Learned representations** |
| Pipeline | Data → Human features → ML Model → Prediction | Data → Learned repr. → Prediction |
| Dạng dữ liệu | Vector cố định chiều | Vectors, tensors, sequences |
| Model học gì | Quan hệ dự đoán | Representation + quan hệ dự đoán |
| Hiệu quả | Dữ liệu có cấu trúc | Dữ liệu phi cấu trúc phức tạp |
| Kích thước model | Nhỏ | Lớn |
| Sở hữu trong môn học | **Assignment 01: feature engineering** | A3+: representation learning |

$$\text{Traditional ML}: \underbrace{\text{human-designed feature representation}}_{\text{con người thiết kế}} + \underbrace{\text{learned prediction model}}_{\text{máy học}}$$
$$\text{Deep Learning}: \underbrace{\text{learned representation}}_{\text{máy học}} + \underbrace{\text{learned prediction model}}_{\text{máy học}}$$

### 4.4 Vì sao Traditional ML phù hợp Assignment 01?

1. **Formulation toán minh bạch** — sinh viên kiểm chứng được từng thành phần;
2. **Representation kiểm tra trực tiếp được** — feature vector con người đọc hiểu;
3. **Nhiều thuật toán cổ điển so sánh được** trong cùng một protocol;
4. **Experiment kiểm soát và giải thích được**;
5. **Deployment tạo ra góc nhìn hệ thống** (system perspective).

> *We start simple so that the development principles are visible.* (Slide 01, trang 33)

---

## 5. Formulating the Learning Problem — Toán học của việc học

### 5.1 Bài toán học có giám sát

Cho dataset:

$$D = \{(x_i, y_i)\}_{i=1}^{N}$$

hệ thống tìm hàm dự đoán:

$$\hat{y} = f_\theta(x)$$

Quá trình học là **tìm tham số tối ưu** theo tiêu chí tối thiểu hóa mất mát trung bình:

$$\theta^* = \arg\min_\theta \frac{1}{N}\sum_{i=1}^{N} \ell\big(f_\theta(x_i), y_i\big)$$

**Giải thích từng ký hiệu** (đề bài yêu cầu sinh viên giải thích mọi ký hiệu):

| Ký hiệu | Ý nghĩa | Ví dụ trong hệ bệnh tim |
|---|---|---|
| $x_i \in \mathbb{R}^d$ | Input representation của quan sát thứ $i$ | Vector 13 chỉ số tim mạch |
| $y_i$ | Target (label) của quan sát thứ $i$ | 0 = khỏe, 1 = mắc bệnh tim |
| $f_\theta$ | Họ hàm dự đoán tham số hóa bởi $\theta$ | Logistic Regression, RF, ... |
| $\theta$ | Tham số model (weights, biases, cấu trúc cây) | $w, b$ của LR |
| $\hat{y}$ | Dự đoán cho input mới | Xác suất/bán quyết bệnh tim |
| $\ell(\cdot, \cdot)$ | Loss function đo sai khác dự đoán–thực tế | Cross-entropy / Gini impurity |
| $\theta^*$ | Tham số tối ưu tìm được | Kết quả `model.fit()` |

### 5.2 Classification vs Regression

**Classification** — dự đoán lớp:

$$x \rightarrow \hat{y} \in \{1, \dots, K\}$$

Ví dụ: disease/healthy, spam/not spam. *Hệ Chẩn đoán bệnh tim của em thuộc loại này (nhị phân, $K=2$).*

**Regression** — dự đoán lượng số:

$$x \rightarrow \hat{y} \in \mathbb{R}$$

Ví dụ: house price, temperature. *Hệ Dự đoán giá nhà của em thuộc loại này.*

### 5.3 Training ≠ Testing — vì sao phải tách

$$D = D_{train} \cup D_{test}$$

- **Training set**: nguồn để thuật toán *học* quan hệ (tìm $\theta^*$);
- **Test set**: mô phỏng *dữ liệu chưa từng thấy* để **ước lượng khả năng khái quát (generalization)**.

**Vì sao test set không được dùng làm nguồn huấn luyện?** Nếu model "nhìn thấy" test set trong quá trình phát triển (chọn model, chỉnh hyperparameter dựa trên test score), kết quả đánh giá sẽ bị **lạm phát** — model thuộc nhớ dữ liệu (overfitting/memorization) thay vì khái quát. Đề bài liệt kê *"Using the test set repeatedly during model development"* vào danh mục điều CẤM. Đánh giá trung thực đòi hỏi test set được dùng **đúng một lần** ở bước cuối.

---

## 6. Baseline — Điểm tham chiếu đầu tiên

Trước khi xây model phức tạp, phải có **baseline** — chiến lược ngây thơ nhất:

- Classification: `DummyClassifier(strategy="most_frequent")` — luôn đoán lớp đa số;
- Regression: `DummyRegressor(strategy="mean")` — luôn đoán giá trị trung bình.

**Vì sao baseline cần thiết?** Câu hỏi đúng không phải *"Model của tôi có chính xác không?"* mà là:

> **Model của tôi có học được điều gì hữu ích vượt trội một chiến lược đơn giản không?**

Ví dụ: hệ bệnh tim có 54.1% mẫu lớp 0 → baseline accuracy = 54.1%. Một model đạt 60% "nghe khá", nhưng chỉ **hơn baseline 6 điểm** — bằng chứng học được khá yếu; ngược lại model đạt 85% là hơn hẳn 31 điểm. Không có baseline, mọi con số accuracy đều **không có ngữ cảnh** để diễn giải.

---

## 7. Bốn model truyền thống — Nguyên lý học của từng model

### 7.1 Logistic Regression (Classification)

$$z = w^Tx + b, \qquad \sigma(z) = \frac{1}{1 + e^{-z}}$$

$$x \rightarrow w^Tx + b \rightarrow \sigma(\cdot) \rightarrow P(y=1|x)$$

- **Representation nhận vào**: feature vector (cần chuẩn hóa để weight so sánh được);
- **Quan hệ học**: ranh giới quyết định **tuyến tính** trong không gian đặc trưng;
- **Tham số học**: $w \in \mathbb{R}^d$, $b \in \mathbb{R}$;
- **Tiêu chí học**: tối thiểu hóa cross-entropy loss (có thể + regularization);
- **Giả định**: quan hệ log-odds tuyến tính theo đặc trưng;
- **Mạnh**: diễn giải được (weight = đóng góp của feature), nhanh, baseline tốt;
- **Yếu**: bắt không được quan hệ phi tuyến/phương thức tương tác phức tạp.
- *Weight $w_j$ dương lớn → tăng $x_j$ làm tăng xác suất lớp 1; âm lớn → giảm.*

### 7.2 k-Nearest Neighbors (Classification/Regression)

$$d(x, x_i) = \sqrt{\sum_{j=1}^{d}(x_j - x_{ij})^2} \quad \text{(khoảng cách Euclid)}$$

- **Representation nhận vào**: feature vector **+ toàn bộ training set** (lazy learner);
- **Quan hệ học**: không học hàm tường minh — phân loại theo **lân cận** của điểm mới;
- "Tham số": $k$ (hyperparameter, không học từ dữ liệu);
- **Tiêu chí**: không có hàm loss tối thiểu hóa toàn cục;
- **Giả định**: các điểm gần nhau theo metric khoảng cách có nhãn tương tự;
- **Mạnh**: đơn giản, không giả định dạng hàm, bắt được ranh giới phi tuyến;
- **Yếu**: **feature scale chi phối khoảng cách** (Glucose ~100, Age ~40 → Glucose áp đảo); chậm lúc inference; degrade ở chiều cao.

> **Hệ quả quan trọng liên kết representation ↔ model:** Với KNN, *representation và preprocessing kết nối với nhau* — chuẩn hóa đặc trưng **thay đổi trực tiếp** hình học không gian và kết quả phân lớp. Đây là lý do Experiment 3 (representation) có ý nghĩa.

### 7.3 Support Vector Machine (Classification)

- **Representation nhận vào**: feature vector (chuẩn hóa gần như bắt buộc);
- **Quan hệ học**: ranh giới phân cách với **biên (margin) lớn nhất**;
- **Tham số**: vector hỗ trợ + hệ số siêu phẳng $w, b$; kernel trick cho phi tuyến (RBF);
- **Tiêu chí học**: $\min \frac{1}{2}\|w\|^2 + C\sum\xi_i$ — tối đa margin, phạt vi phạm;
- **Giả định**: margin lớn → khái quát tốt;
- **Mạnh**: hiệu quả chiều cao, kernel linh hoạt;
- **Yếu**: nhạy với scale, chi phí $O(n^2)$–$O(n^3)$, khó diễn giải.

> *Good separation is not enough; **the margin matters**.* — nhiều ranh giới phân đúng training data, SVM chọn ranh giới **cách xa nhất** cả hai lớp để khái quát.

### 7.4 Decision Tree & Random Forest

**Decision Tree:**

- **Representation nhận vào**: feature vector (không cần scale — chia theo ngưỡng);
- **Quan hệ học**: chia đệ quy không gian đặc trưng theo tiêu chí tách;
- **Cấu trúc học**: cây các node điều kiện `(feature, ngưỡng)`;
- **Tiêu chí học**: Gini impurity / entropy — mỗi lần chia tối đa độ tinh khiết;
- **Mạnh**: diễn giải cực tốt (vẽ cây ra đọc được), bắt phi tuyến + tương tác;
- **Yếu**: **overfit mạnh** nếu không giới hạn độ sâu; bất ổn (nhỏ dữ liệu → cây khác hẳn).

**Random Forest = Bagging + Random Feature Selection + Ensemble Prediction:**

$$\hat{y} = \text{Vote}\big(T_1(x), \dots, T_B(x)\big) \qquad \text{(classification)}$$
$$\hat{y} = \frac{1}{B}\sum_{b=1}^{B} T_b(x) \qquad \text{(regression)}$$

Mỗi cây: (1) nhìn **bootstrap sample** của dữ liệu; (2) mỗi split chỉ xét **subset ngẫu nhiên** các feature. Nhiều cây đa dạng → dự đoán **robust hơn** (giảm variance).

Với regression (hệ giá nhà), assignment dùng thêm:

### 7.5 Linear Regression (Regression)

$$\hat{y} = w^Tx + b$$

- **Tiêu chí học**: tối thiểu hóa MSE $\sum_i (f_\theta(x_i) - y_i)^2$ (OLS có nghiệm đóng);
- **Giả định**: quan hệ tuyến tính, sai số iid Gaussian, không đa cộng tuyến mạnh;
- **Mạnh**: đơn giản, diễn giải được (hệ số = marginal effect);
- **Yếu**: bắt không được phi tuyến nếu không thêm biến đổi đặc trưng.

### 7.6 Support Vector Regression (Regression)

SVR tìm hàm $f(x)$ lệch khỏi $y$ thực tế tối đa $\varepsilon$, đồng thời phẳng nhất có thể — phiên bản "margin" của regression: chỉ các điểm ngoài **$\varepsilon$-tube** mới đóng góp loss.

**Điểm chung quan trọng** (Slide 01, trang 44): các thuật toán nhận **cùng một representation** (feature vector) nhưng áp đặt **giả định và cơ chế học khác nhau** — đó là lý do so sánh chúng trong cùng protocol là một experiment có ý nghĩa khoa học.

---

## 8. Controlled Experiments — Từ "chạy model" đến thực nghiệm

Slide 01 (trang 52) phân biệt:

- **Experiment yếu**: *"I trained KNN, SVM, and Logistic Regression. KNN was best."*
- **Experiment mạnh**: hỏi thêm **"WHY?"** — và thiết kế kiểm soát để trả lời.

### 8.1 Ba experiment bắt buộc

**Experiment 1 — Model Comparison:** ≥4 model, cùng protocol đánh giá, cùng train/test split → bảng Accuracy/Precision/Recall/F1 (hoặc MAE/MSE/RMSE/$R^2$).

**Experiment 2 — Hyperparameter Investigation:** thay đổi **một** hyperparameter có ý nghĩa (k của KNN, độ sâu cây, số cây RF, $C$ của SVM, regularization của LR...). *Phải nêu câu hỏi thực nghiệm TRƯỚC khi chạy.*

**Experiment 3 — Representation/Feature Investigation:** so sánh $X_{all}$ vs $X_{selected}$, hoặc unscaled vs standardized. Trả lời: *representation thay đổi kết quả không, và **vì sao**?* — experiment này **trả lời trực tiếp triết lý Slide 01**.

### 8.2 Nguyên tắc đổi một biến

Một experiment có kiểm soát chỉ đổi **một yếu tố** và giữ nguyên phần còn lại. Đề bài cảnh cáo: *"Changing many parameters without an experimental question"* là không đủ chuẩn — mỗi lần đổi tham số phải **trả lời một câu hỏi**.

---

## 9. Evaluation — Accuracy là chưa đủ

### 9.1 Classification

Confusion matrix:

|  | Dự đoán + | Dự đoán − |
|---|---|---|
| **Thực tế +** | TP | FN |
| **Thực tế −** | FP | TN |

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}, \quad \text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = \frac{2PR}{P + R}$$

**Chọn metric nào tùy bài toán ứng dụng** (yêu cầu bắt buộc của đề):

- **Hệ bệnh tim**: bỏ sót người bệnh (FN) nghiêm trọng hơn báo giả (FP) → **Recall là metric ưu tiên**, theo dõi Precision/F1 để bảo đảm không tăng báo giả quá cao. Accuracy đơn thuần gây hiểu lầm khi lớp mất cân bằng.
- Công thức $F_1$ là **trung bình điều hòa** của Precision và Recall — phạt nặng khi một trong hai thấp.

### 9.2 Regression

$$MAE = \frac{1}{N}\sum_i |\hat{y}_i - y_i|, \quad MSE = \frac{1}{N}\sum_i (\hat{y}_i - y_i)^2, \quad RMSE = \sqrt{MSE}$$

$$R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}$$

- **MAE**: sai số trung bình cùng đơn vị giá nhà ($) — dễ diễn giải cho người dùng;
- **RMSE**: phạt lỗi lớn nặng hơn — quan trọng vì dự đoán lệch $100k nghiêm trọng hơn nhiều so với $10k;
- **$R^2$**: phần phương sai mục tiêu model giải thích được (1.0 hoàn hảo, 0 = bằng baseline mean);
- **Hệ giá nhà**: $R^2$ là chỉ số tổng quát, RMSE nhấn sai số lớn, MAE để diễn giải cho người dùng cuối — báo cáo đủ cả bốn.

### 9.3 Model Selection là một **quyết định**

Câu hỏi không phải $\max(\text{Accuracy})$ mà là: model nào **khái quát tốt**? metric nào quan trọng với ứng dụng? model có **diễn giải được** không (y tế cần)? chi phí tính toán? có **deploy được đáng tin cậy** không?

---

## 10. Từ Model đến Intelligent Application

### 10.1 Model một mình chưa phải hệ thống

Pipeline ứng dụng phải hiện thực hóa đầy đủ:

$$\text{Input} \rightarrow \text{Representation} \rightarrow \text{Preprocessing} \rightarrow \text{Model} \rightarrow \text{Prediction} \rightarrow \text{Output}$$

**Ràng buộc nền tảng:** *Representation dùng cho input mới phải GIỐNG HỆT representation dùng lúc huấn luyện* — cùng encoder, cùng scaler, cùng thứ tự cột. Đây chính là ý nghĩa câu Slide 01 (trang 56): *"New input must be represented and preprocessed in the same way as the training data."*

### 10.2 Model Persistence + Deployment

```python
# Lưu model sau huấn luyện
import joblib
joblib.dump(model, "model.joblib")

# Tải lại cho inference
model = joblib.load("model.joblib")
prediction = model.predict(X_new)
```

Kiến trúc deployment dạng **Prediction Service** (Slide 01, trang 57):

```
User/Client ──request features──▶ REST API / Web App ──▶ Saved ML Model (inference)
           ◀──prediction response──┘
```

> *Application does not need to know how the model learns. It needs a well-defined prediction interface.*

Trong Assignment 01, em hiện thực hóa bằng **web app Streamlit** deploy lên **Hugging Face Spaces**: người dùng nhập chỉ số → app chuyển sang đúng representation huấn luyện → model trả dự đoán + xác suất → hiển thị kèm khuyến nghị. Đây là bước **Deploy** trong vòng phát triển Understand → Represent → Implement → Experiment → Evaluate → Deploy → Iterate.

### 10.3 Demonstration bắt buộc

Đề yêu cầu demo đường đi đầy đủ:

$$\text{User/Environment} \rightarrow \text{Input} \rightarrow \text{Feature Representation} \rightarrow \text{ML Model} \rightarrow \text{Prediction}$$

với **ít nhất 3 input case** — một case lành, một case mắc bệnh (với hệ tim); một nhà rẻ, một nhà trung bình, một nhà đắt (với hệ giá nhà) — chứng minh cùng một pipeline xử lý mọi case.

---

## 11. Reflection — Điều gì làm hệ thống này "intelligent"?

### 11.1 Bảy câu hỏi reflection bắt buộc (mục 18 đề)

1. **Hệ thống nhận thông tin gì?** Chỉ số measument của bệnh nhân / đặc điểm nhà;
2. **Representation nội bộ là gì?** Feature vector $x \in \mathbb{R}^d$ sau encode + scale;
3. **Model học gì từ ví dụ?** Quan hệ ánh xạ feature → target $f_\theta: x \mapsto \hat{y}$;
4. **Dự đoán/quyết định gì?** Xác suất bệnh tim (ngưỡng 0.5) / mức giá ước tính ($);
5. **Vì sao xử lý được input chưa thấy?** **Khái quát hóa**: học quan hệ có cấu trúc (pattern) chứ không ghi nhớ từng mẫu — miễn input mới cùng phân phối với training data;
6. **Phần nào gọi là "intelligent" hợp lý?** Khả năng **học từ ví dụ + khái quát + dự đoán đúng** — năng lực không ai lập trình luật tường minh;
7. **Hạn chế gì ngăn trở việc thông minh hơn?** (mục 11.2).

### 11.2 Hạn chế của representation feature vector (mục 19 đề)

- **Lưu giữ**: các thuộc tính đo đếm/chốt được chọn — tín hiệu dự báo chính;
- **Mất**: quan hệ giữa các thực thể, dữ liệu ảnh/Y tế gốc (ECG thô, ảnh chụp), chuỗi thời gian, ngữ cảnh lâm sàng, tri thức y khoa chuyên gia;
- **Image?** Có thể — ảnh siêu âm tim / ảnh chụp nhà → tensor → CNN (A4 của môn học);
- **Sequence?** Có thể — chuỗi ECG theo thời gian, lịch sử giao dịch nhà;
- **Graph?** Có thể — đồ thị bệnh–triệu chứng, mạng lưới vị trí nhà–trường học–trung tâm;
- **Learned embeddings?** Có thể — embedding mã hóa bệnh nhân/nhà tương tự nhau gần nhau;
- **Đổi representation thì đổi gì?** Đổi *thông tin có sẵn* → đổi *họ hàm học được* → đổi *trần khả năng dự đoán* (nhưng thường đổi cả chi phí dữ liệu + mất diễn giải).

$$\text{trained model} \neq \text{complete intelligent system}$$

Hệ thống hoàn chỉnh cần thêm: input handling, representation, preprocessing, prediction, output, và **tích hợp vào application**.

---

## 12. Vị trí của Assignment 01 trong lộ trình môn học

$$\underbrace{\text{Structured Data}}_{\text{input}} \rightarrow \underbrace{\text{Feature Engineering}}_{\text{representation}} \rightarrow \underbrace{\text{Traditional ML}}_{\text{learning}} \rightarrow \underbrace{\text{Prediction}}_{\text{decision}}$$

Trong dòng chảy lịch sử:

$$\text{Symbolic AI} \rightarrow \text{Expert Systems} \rightarrow \boxed{\text{Statistical ML}} \rightarrow \text{Deep Learning} \rightarrow \text{Foundation/Gen AI} \rightarrow \text{Interactive/Agentic}$$

Assignment 01 chiếm giai đoạn **Statistical ML** — giai đoạn mà con người thiết kế representation (feature vector) và máy học quan hệ dự đoán.

Lộ trình 5 assignment:

| Giai đoạn | Representation chính | Năng lực chính |
|---|---|---|
| **A1** | Feature vectors | **Traditional ML + deployment** ← *vị trí hiện tại* |
| A2 | Data / improved representations | Preprocessing + evaluation |
| A3 | Learned representations | Neural networks + deep learning |
| A4 | Tensors + graphs | CNN + relational knowledge |
| A5 | Embeddings + context | RAG + conversational systems |
| Project | Integrated representations | Complete intelligent system |

Tiến trình dài hạn: Data → Representation → Learning → Knowledge → Retrieval → Generation → Interaction → **Intelligent System**.

---

## 13. Kết luận lý thuyết

Assignment 01 là **bước hiện thực hóa đầu tiên** của khung khái niệm Slide 01:

$$\text{Understand} \rightarrow \text{Represent} \rightarrow \text{Implement} \rightarrow \text{Experiment} \rightarrow \text{Evaluate} \rightarrow \text{Apply}$$

Ba luận điểm trung tâm được Parts 2 (thực hành) chứng minh:

1. **Representation là xương sống**: model không nhận thế giới thực mà nhận representation — representation quyết định thông tin sẵn có cho học. Hai hệ thống thực nghiệm (bệnh tim, giá nhà) sẽ cho thấy đổi representation (scale, chọn feature, log-transform) **thay đổi kết quả học**.

2. **Learning = học từ ví dụ + khái quát + dự đoán**: baseline cho khung tham chiếu, ≥4 model cùng representation so sánh theo protocol thống nhất, 3 controlled experiment trả lời câu hỏi đặt trước.

3. **Model ≠ hệ thống**: chỉ khi model được bọc trong pipeline Input → Representation → Preprocessing → Model → Prediction → Output và **deploy thành application** (web app) thì mới có một *intelligent system nhỏ* hoàn chỉnh — intelligent system **đầu tiên** em phát triển trong môn học này.

---

## Tài liệu tham khảo

1. Tran, D. Q., *Intelligent System Development — Lecture 01: From Intelligence to Intelligent Systems*, PTIT.
2. Tran, D. Q., *Intelligent System Development — Assignment 01: From Data Representation to a First Intelligent System*, PTIT.
3. Lee, W.-M., *Python® Machine Learning*, First Edition, Wiley, 2019 — Chương 12: Deploying Machine Learning Models.
4. Scikit-learn documentation: machine learning algorithms and model evaluation.
5. Russell, S. and Norvig, P., *Artificial Intelligence: A Modern Approach*.
6. Goodfellow, I., Bengio, Y., and Courville, A., *Deep Learning*.
7. Vaswani, A. et al., "Attention Is All You Need," 2017.

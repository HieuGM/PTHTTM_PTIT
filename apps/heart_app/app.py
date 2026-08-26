# -*- coding: utf-8 -*-
"""
HEART DISEASE SCREENING — Intelligent System App (Assignment 01)
Môn học: Intelligent System Development

Pipeline: Input → Representation → Preprocessing → Model → Prediction → Output
Model: Random Forest (B=100) — huấn luyện trong notebook 01_heart_disease_system.ipynb
Representation: 13 chỉ số thô → one-hot 18 chiều → (model đã nhúng scaler)
"""
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# ==== Trang trí ====
st.set_page_config(page_title="Chẩn đoán bệnh tim — ISD Assignment 01",
                   page_icon="🫀", layout="wide")

# ==== Tải model + metadata representation (CÙNG representation như training) ====
ARTIFACTS = "heart_model.joblib"  # đặt cạnh app.py khi deploy


@st.cache_resource
def load_artifacts():
    return joblib.load(ARTIFACTS)


try:
    art = load_artifacts()
except FileNotFoundError:
    st.error("⚠️ Không tìm thấy `heart_model.joblib`. Hãy đặt file model cạnh `app.py`.")
    st.stop()


def predict_patient(measurements: dict):
    """Input (13 chỉ số thô) → one-hot encode đúng thứ tự → model → (lớp, xác suất)."""
    x = pd.DataFrame([measurements])
    x_enc = pd.get_dummies(x, columns=art["categorical"], prefix=art["categorical"])
    x_enc = x_enc.reindex(columns=art["enc_columns"], fill_value=0)
    pred = int(art["model"].predict(x_enc)[0])
    proba = float(art["model"].predict_proba(x_enc)[0][1])
    return pred, proba


# ==== GIAO DIỆN ====
st.title("🫀 Hệ Chẩn đoán Bệnh tim — Intelligent System")
st.caption(
    "Assignment 01 — Intelligent System Development | Random Forest | "
    "Dataset: UCI Heart Disease (Cleveland, 303 bệnh nhân) | "
    "Test: F1 = 0.88, Recall = 0.93"
)

with st.expander("ℹ️ Hệ thống hoạt động thế nào? (kiến trúc)"):
    st.markdown(
        """
```
Người dùng nhập 13 chỉ số ──▶ One-hot encode (18 chiều) ──▶ Random Forest ──▶ Xác suất bệnh tim
        (INPUT)                    (REPRESENTATION)              (MODEL)          (PREDICTION)
                                                                              │
_ngưỡng 0.5_ ──▶ KHỎE / CÓ BỆNH + khuyến nghị ──▶ (OUTPUT hiển thị cho nhân viên y tế)
```
Model học từ 303 bệnh nhân tại Cleveland Clinic (UCI). **Cùng một representation**
dùng lúc huấn luyện được tái dựng chính xác cho input mới — đây là nguyên lý cốt lõi.
    """
    )

st.subheader("Nhập chỉ số tim mạch của bệnh nhân")

left, right = st.columns(2)

with left:
    st.markdown("**Thông tin chung**")
    age = st.slider("Tuổi (năm)", 20, 90, 55)
    sex = st.radio("Giới tính", ["Nữ (0)", "Nam (1)"], horizontal=True)
    trestbps = st.number_input("Huyết áp tâm thu lúc nghỉ — trestbps (mm Hg)", 80, 220, 130)
    chol = st.number_input("Cholesterol huyết thanh — chol (mg/dl)", 100, 650, 240)
    fbs = st.radio(
        "Đường huyết lúc đói > 120 mg/dl — fbs",
        ["Không (0)", "Có (1)"], horizontal=True)
    thalach = st.number_input("Nhịp tim tối đa — thalach (bpm)", 60, 220, 150)

with right:
    st.markdown("**Chỉ số chuyên sâu**")
    cp = st.selectbox("Loại đau ngực — cp", [
        "1 — Typical angina (đau thắt điển hình)",
        "2 — Atypical angina",
        "3 — Non-anginal pain (không do tim)",
        "4 — Asymptomatic (không triệu chứng)",
    ])
    restecg = st.selectbox("Điện tâm đồ nghỉ — restecg", [
        "0 — Bình thường",
        "1 — Bất thường ST-T",
        "2 — Phì đại thất trái (Estes)",
    ])
    exang = st.radio("Đau thắt ngực khi gắng sức — exang", ["Không (0)", "Có (1)"], horizontal=True)
    oldpeak = st.number_input("Oldpeak — giảm đoạn ST khi tập (mV)", 0.0, 6.5, 1.0, 0.1)
    slope = st.selectbox("Độ dốc ST lúc tập tối đa — slope", ["0 — Lên", "1 — Phẳng", "2 — Xuống"])
    ca = st.selectbox("Số mạch vành chính hẹp — ca (fluoroscopy)", ["0", "1", "2", "3"])
    thal = st.selectbox("Thalassemia — thal", [
        "3 — Bình thường",
        "6 — Fixed defect (kết cố định)",
        "7 — Reversible defect (kết đảo ngược)",
    ])

measurements = {
    "age": float(age),
    "sex": 0 if sex.startswith("Nữ") else 1,
    "cp": float(cp[0]),
    "trestbps": float(trestbps),
    "chol": float(chol),
    "fbs": 0 if fbs.startswith("Không") else 1,
    "restecg": float(restecg[0]),
    "thalach": float(thalach),
    "exang": 0 if exang.startswith("Không") else 1,
    "oldpeak": float(oldpeak),
    "slope": float(slope[0]),
    "ca": float(ca),
    "thal": float(thal[0]),
}

st.divider()

# ==== DỰ ĐOÁN ====
if st.button("🩺 Dự đoán", type="primary", use_container_width=True):
    pred, proba = predict_patient(measurements)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Xác suất bệnh tim", f"{proba:.1%}")
    with col2:
        st.metric("Ngưỡng quyết định", "0.50")
    with col3:
        st.metric("Kết luận", "CÓ BỆNH TIM" if pred == 1 else "KHỎE")

    # thanh xác suất
    st.progress(min(proba, 1.0))

    if pred == 1:
        st.error(
            f"⚠️ **Mức độ rủi ro CAO** — model dự đoán bệnh nhân **có khả năng mắc bệnh tim** "
            f"(xác suất {proba:.1%}). Khuyến nghị: ưu tiên khám chuyên sâu tim mạch."
        )
    else:
        st.success(
            f"✅ **Mức độ rủi ro THẤP** — model dự đoán bệnh nhân **không có dấu hiệu bệnh tim** "
            f"(xác suất bệnh chỉ {proba:.1%})."
        )

    if 0.35 <= proba <= 0.65:
        st.warning(
            "⚖️ Xác suất nằm trong **vùng mơ hồ** (0.35–0.65): model không đủ tự tin. "
            "Khuyến nghị khám chuyên sâu để xác định chính xác."
        )

    st.caption(
        "⚠️ Công cụ hỗ trợ sàng lọc nghiên cứu — KHÔNG thay thế chẩn đoán của bác sĩ. "
        "Model học từ 303 bệnh nhân (UCI Cleveland); hiệu năng ước tính: Recall 0.93, F1 0.88."
    )

# ==== Preset cases cho demo nhanh (3 case như notebook) ====
st.divider()
st.subheader("🎬 Demo nhanh — 3 case mẫu từ notebook")
preset_cols = st.columns(3)
presets = {
    "Case 1 — Nguy cơ thấp": {
        "age": 42, "sex": 0, "cp": 3, "trestbps": 115, "chol": 180, "fbs": 0,
        "restecg": 0, "thalach": 172, "exang": 0, "oldpeak": 0.2, "slope": 2,
        "ca": 0, "thal": 3},
    "Case 2 — Nguy cơ cao": {
        "age": 68, "sex": 1, "cp": 4, "trestbps": 150, "chol": 310, "fbs": 1,
        "restecg": 2, "thalach": 110, "exang": 1, "oldpeak": 3.2, "slope": 0,
        "ca": 2, "thal": 7},
    "Case 3 — Case biên": {
        "age": 57, "sex": 1, "cp": 2, "trestbps": 132, "chol": 250, "fbs": 0,
        "restecg": 1, "thalach": 142, "exang": 0, "oldpeak": 1.2, "slope": 1,
        "ca": 1, "thal": 6},
}
for col, (name, meas) in zip(preset_cols, presets.items()):
    with col:
        if st.button(name, key=name):
            pred, proba = predict_patient(meas)
            if pred == 1:
                st.error(f"**CÓ BỆNH TIM** — xác suất {proba:.1%}")
            else:
                st.success(f"**KHỎE** — xác suất bệnh {proba:.1%}")
            st.progress(min(proba, 1.0))

st.divider()
st.markdown(
    "<sub>Assignment 01 — Intelligent System Development | Hệ Chẩn đoán bệnh tim | "
    "Random Forest (scikit-learn) | Deploy: Hugging Face Spaces (Streamlit)</sub>",
    unsafe_allow_html=True,
)
